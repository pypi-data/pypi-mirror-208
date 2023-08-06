import os
from urllib.parse import quote
from multimethod import multimethod
from looqbox.global_calling import GlobalCalling
from looqbox.integration.looqbox_global import random_hash
from looqbox.render.abstract_render import BaseRender
from looqbox.utils.utils import format as looq_format


def _hex_to_rgb(color: str) -> tuple:
    color = color.lstrip('#')
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def _color_name_to_rgb(color: str) -> tuple:
    color_map = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
    }
    return color_map.get(color, color)


@multimethod
def _get_rgb_color(color: str) -> tuple:
    if color.startswith("#"):
        return _hex_to_rgb(color)
    elif color.startswith("rgb"):
        return tuple(int(x) for x in color[4:-1].split(","))
    else:
        return _color_name_to_rgb(color)


@multimethod
def _get_rgb_color(color: tuple) -> tuple:
    return color


class BasePDFRender(BaseRender):

    def __init__(self):
        from looqbox.render.pdf.pdf_builder import PDFBuilder

        try:
            question_link = GlobalCalling.looq.domains[0].get("domain", None)
        except KeyError:
            question_link = None
        if question_link is not None:
            url_safe_question = quote(GlobalCalling.looq.question)
            question_link = f"{question_link}/#/q?question={url_safe_question}"

        self.pdf = PDFBuilder(
            user_name=GlobalCalling.looq.user.login,
            user_id=GlobalCalling.looq.user.id,
            logo_path=os.path.join(os.path.dirname(__file__), "logo.png"),
            question_link=question_link,
            add_question_link=GlobalCalling.looq.feature_flags.get("looqbot", {}).get("linkOnAnswer", False),
            add_watermark=GlobalCalling.looq.feature_flags.get("looqbot", {}).get("watermark", False),
        )

        self.pdf_width, self.pdf_height = self.pdf.w, self.pdf.h
        self.left_margin = None
        self.margin = 10

        self.add_watermark = True
        self.add_template_on_first_page = False

        self.rendered_objs = list()

    def _render_container(self, container):
        spacing = 0
        if container.css_options:
            if len([css for css in container.css_options if "border" in css.property]) > 1:
                spacing = 6
        try:
            self.pdf.cell(0, spacing, "", 0, 1, 'C')
        except Exception or RuntimeError:
            pass
        for looq_obj in container.children:
            if looq_obj.render_condition:
                looq_obj.to_json_structure(self)

    def _render_frame(self, container):
        for looq_obj in container.content:
            if looq_obj.render_condition:
                looq_obj.to_json_structure(self)

    def should_render(self):
        len_rendered_objs = len(self.rendered_objs)
        if len_rendered_objs == 0:
            return False
        elif len_rendered_objs == 1:
            only_text = "ObjMessage" in self.rendered_objs or "ObjText" in self.rendered_objs
            return not only_text
        else:
            return True

    def response_board_render(self, board):
        self._render_frame(board)
        if not self.should_render():
            return None
        try:
            self.pdf.output(self.pdf.name)
        except KeyError:
            return None
        if self.add_watermark:
            self.pdf.add_watermark()
        if self.add_template_on_first_page:
            self.pdf.merge_page_before(os.path.join(os.path.dirname(__file__), "template.pdf"))

    def response_frame_render(self, frame):
        self._render_frame(frame)

    def table_render(self, obj_table):
        cell_height = 6
        border = False

        data_with_total = self._add_total(obj_table).copy()
        formatted_data = self._format_table(data_with_total, obj_table.col_format)
        table_data = formatted_data

        font_size, table_width, cell_height = self._change_font_size_by_width(
            table_data, self.pdf_width - self.margin, cell_height)

        if font_size < 3:
            return None

        self.pdf.add_page()
        self.left_margin = (self.pdf_width - table_width) / 2

        self._add_table_title(obj_table.title, obj_table.tab_label, cell_height, border, title_font_size=font_size)
        self._add_table_body(obj_table, table_data, cell_height, border, table_font_size=font_size)
        self.rendered_objs.append("ObjTable")

    def _change_font_size_by_width(self, table_data, width, cell_height):
        font_size = 10
        self.pdf.set_font_size(font_size)
        table_width = self._table_width(table_data)
        iteration = 0
        while table_width > width:
            font_size -= 0.5
            self.pdf.set_font_size(font_size)
            table_width = self._table_width(table_data)
            iteration += 1
            if iteration % 3 == 0:
                cell_height -= 1
        return font_size, table_width, cell_height

    def _table_width(self, table_data):
        self.cell_width_map = {
            col: max(
                [
                    table_data[col].astype(str).apply(lambda x: self.pdf.get_string_width(x)).max(),
                    self.pdf.get_string_width(col)
                ]
            ) + 2 for col in table_data.columns
        }
        return sum(self.cell_width_map.values())

    def _add_total(self, obj_table):
        self.has_total = False
        table_data = obj_table.data
        if obj_table.total:

            total = {}
            for col in table_data.columns:
                if col in obj_table.total:
                    total[col] = obj_table.total[col]
                else:
                    total[col] = obj_table.null_as

            table_data = table_data.append(total, ignore_index=True)
            self.has_total = True

        return table_data

    def _format_table(self, table_data, col_format):
        for col in table_data.columns:
            if col in col_format:
                table_data[col] = table_data[col].apply(lambda x: self._format(x, col_format[col]))
            table_data[col] = table_data[col].astype(str)
        return table_data

    def _format(self, x, format):
        try:
            return looq_format(x, format)
        except ValueError:
            return x

    def _add_table_title(self, title, tab_label, cell_height=6, border=False, title_font_size=10):
        if not title:
            return None

        title_font_color = (153, 153, 153)
        title_font = self.pdf.font

        if isinstance(title, str):
            title = [tab_label, title]
        else:
            title = [tab_label] + title

        self.pdf.set_font(title_font, '', title_font_size)
        self.pdf.set_text_color(*title_font_color)
        for line in title:
            if not line:
                continue
            # Since the pdf has 10 margin on the left and right, we need to add 20 to the width to center it
            self.pdf.cell(self.pdf_width, cell_height, line, border, 2, 'C')
        self.pdf.ln(cell_height)

    def _add_table_body(self, obj_table, table_data, cell_height, border, table_font_size=10):

        header_background_color = (241, 241, 241)
        header_font_color = (95, 95, 95)

        body_font_color = (37, 33, 59)
        body_backgroud_color1 = (249, 249, 249)
        body_backgroud_color2 = (255, 255, 255)

        table_font = self.pdf.font
        header_cell_height = cell_height * 1.5

        # dataframe

        self.pdf.set_font(table_font, 'B', table_font_size)
        self.pdf.set_text_color(*header_font_color)
        self.pdf.set_fill_color(*header_background_color)
        self.pdf.cell(self.left_margin)

        column_name_list = list(table_data.columns)
        for header in column_name_list[:-1]:
            cell_width = self.cell_width_map[header]

            self.pdf.cell(cell_width, header_cell_height, header, border, 0, 'C', fill=True)

        cell_width = self.cell_width_map[column_name_list[-1]]
        self.pdf.cell(cell_width, header_cell_height, column_name_list[-1], border, 1, 'C', fill=True)

        self.pdf.set_font(table_font, '', table_font_size)
        self.pdf.set_text_color(*body_font_color)

        # Iterate over lines
        iterration_range = range(0, len(table_data) - 1) if self.has_total else range(0, len(table_data))

        for i in iterration_range:
            self.pdf.cell(self.left_margin)
            bg_color = body_backgroud_color1 if i % 2 == 0 else body_backgroud_color2
            self.pdf.set_fill_color(*bg_color)

            # Iterate over cells in line
            self._add_table_line(i, table_data, cell_width, cell_height, obj_table.col_format, border)

        if self.has_total:
            self.pdf.set_fill_color(*header_background_color)
            self.pdf.cell(self.left_margin, border=border)
            self._add_table_line(i + 1, table_data, cell_width, cell_height, obj_table.col_format, border)

    def _add_table_line(self, line_idx, table_data, cell_width, cell_height, table_format, border):
        for idx, col in enumerate(table_data.columns):
            cell_width = self.cell_width_map[col]
            cell_value = table_data[col][line_idx]
            self.pdf.cell(
                cell_width, cell_height,
                cell_value,
                border, (idx + 1) // len(table_data.columns), 'C',
                fill=True
            )

    def plotly_render(self, obj_plotly):
        figure = obj_plotly.data
        temp_file = GlobalCalling.looq.temp_file(random_hash() + "plotly.png")
        figure.write_image(temp_file)

        self.pdf.add_image(temp_file, 10, 30, 190, 100)
        os.remove(temp_file)
        self.rendered_objs.append("ObjPlotly")

    def file_upload_render(self, obj_file_upload):
        pass

    def html_render(self, obj_html):
        pass

    def pdf_render(self, obj_pdf):
        pass

    def simple_render(self, obj_simple):
        pass

    def image_render(self, obj_image):
        pass

    def list_render(self, obj_list):
        pass

    def message_render(self, obj_message):
        message = obj_message.text
        try:
            self.pdf.cell(0, message, "", 0, 1, 'C')
        except Exception:
            self.pdf.add_page()
            self.pdf.cell(0, 0, message, 0, 1, 'C')
        self.rendered_objs.append("ObjMessage")

    def query_render(self, obj_query):
        pass

    def web_frame(self, obj_web):
        pass

    def text_render(self, obj_text):
        message = obj_text.text
        border = False

        if obj_text.css_options:
            font_size = [str(css.value) for css in obj_text.css_options if css.property == "fontSize"] or ["10"]
            font_color = [css.value for css in obj_text.css_options if css.property == "color"] or [(0, 0, 0)]
            font_weight = [700 if css.value == "bold" else int(css.value) for css in obj_text.css_options if css.property == "fontWeight"] or [400]
            font_weight = "B" if font_weight[0] >= 700 else ""
            font_size = int(font_size[0].replace("px", ""))
            font_size = font_size * 0.6 if font_size > 14 else font_size
            font_color = font_color[0]
        else:
            font_weight = ""
            font_size = 10
            font_color = (0, 0, 0)

        self.pdf.set_font(self.pdf.font, font_weight, font_size)
        self.pdf.set_text_color(*_get_rgb_color(font_color))

        cell_width = self.pdf.get_string_width(message)
        cell_height = font_size/2
        try:
            self.pdf.cell(h=cell_height, w=self.pdf_width, txt=message, border=border, ln=2, align='C')
        except Exception:
            self.pdf.add_page()
            # self.pdf.set_x(self.pdf_width/2)
            self.pdf.cell(h=cell_height, w=self.pdf_width, txt=message, border=border, ln=2, align='C')
        self.rendered_objs.append("ObjText")

    def audio_render(self, obj_audio):
        pass

    def video_render(self, obj_video):
        pass

    def switch_render(self, obj_switch):
        self._render_container(obj_switch)

    def tooltip_render(self, obj_tooltip):
        self._render_container(obj_tooltip)

    def link_render(self, obj_link):
        self._render_container(obj_link)

    def row_render(self, obj_row):
        self._render_container(obj_row)

    def column_render(self, obj_column):
        self._render_container(obj_column)

    def gauge_render(self, obj_gauge):
        pass

    def line_render(self, obj_shape):
        pass

    def embed_render(self, obj_embed):
        pass

    def obj_form_render(self, obj_form):
        pass

    def form_html_render(self, obj_form_html):
        pass

    def image_capture_render(self, obj_image_capture):
        pass

    def simple_table_render(self, obj_simple_table):
        pass
