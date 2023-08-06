from looqbox.objects.container.positional.abstract_positional_container import AbstractPositionalContainer
from looqbox.objects.component_utility.css_option import CssOption as css
from looqbox.objects.container.positional.looq_column import ObjColumn
from looqbox.objects.container.positional.looq_row import ObjRow
from looqbox.objects.container.looq_tooltip import ObjTooltip
from looqbox.objects.container.looq_switch import ObjSwitch
from looqbox.objects.visual.shape.looq_line import ObjLine
from looqbox.objects.visual.looq_text import ObjText
from looqbox.render.abstract_render import BaseRender


class ObjContainer(AbstractPositionalContainer):

    def __init__(self, *content, **properties):
        """
        :param sample_info:
        :param kwargs: all component variables and optional pre-sets for the container

            height: Height of the container, defaults to 50px
            line: If it should have the side line, defaults to True
            line_thickness: Thickness of the side line, defaults to 5px
            tooltip: Tooltip text, displayed if not empty, defaults to empty string
            title: Title of the container
            subtitle: Subtitle of the container
            line_color: Side line color, defaults to "#40db62"
            tooltip_spacing: Tooltip margin against container
            tooltip_size: Size ofg the tooltip, defaults to 15px
            css_options: Options to apply to the container
        """
        super().__init__()

        self.content = content
        self.properties = properties

        self.obj_container_args = [
            "height",
            "line",
            "line_thickness",
            "tooltip",
            "title",
            "subtitle",
            "line_color",
            "title_spacing",
            "tooltip_spacing",
            "tooltip_size"
        ]
        self.abs_container_args = [
            "value",
            "render_condition",
            "tab_label",
            "obj_class"
        ]

        self._default_style = [
            css.TextAlign("left"),
            css.Height("100%"),
            css.Width("100%")
        ]
        self._children_style = [
            css.JustifyContent("flex-start"),
            css.Padding("15px"),
            css.TextAlign("left"),
            css.Height("100%"),
            css.Width("100%")
        ]
        self._container_style = [
            css.Overflow("hidden"),
            css.Position("relative"),
            css.Width("100%"),
            css.Height("100%"),
            css.FlexWrap("nowrap")
        ]
        self._line_style = [
            css.Margin(0),
            css.Position("absolute"),
            css.Height("100%"),
        ]
        self._tooltip_style = [
            css.Position("absolute"),
            css.Right(self.properties.get("tooltip-spacing", "5px")),
            css.Width(self.properties.get("tooltip-size", "15px")),
            css.Height(self.properties.get("tooltip-size", "15px"))
        ]

    def _get_container(self) -> ObjRow:
        content = self._get_content()
        extra_properties = {looq_object_property: property_value for looq_object_property, property_value in
                            vars(self).items() if looq_object_property in self.abs_container_args}
        return ObjRow(content, css_options=[css.Padding("5px")], **extra_properties)

    def _get_content(self) -> ObjRow:

        _header = self._get_header()
        _is_single_container = self.is_single_switch(self.content)

        if _is_single_container and _header:
            self._insert_header_on_switch(_header)

        children_container = ObjColumn(self.content, **self._get_positional_args()).set_main_alignment_center
        children_container = self._add_default_style(children_container, self._default_style)

        _current = ObjColumn(
            (_header if not _is_single_container and _header else []) + [children_container],
            css_options=self._children_style,
        )

        _line = self._get_line()
        _tooltip = self._get_container_tooltip()

        return ObjRow(
            _line,
            _current,
            _tooltip,
            css_options=self._container_style,
        ).add_border.set_cross_alignment_center

    def _insert_header_on_switch(self, _header):
        for idx in range(len(tmp_container := self.content[0].children)):
            tmp_container[idx] = ObjColumn(_header, tmp_container[idx], tab_label=tmp_container[idx].tab_label)

    def _get_header(self):
        _header = [
            self._get_title(),
            self._get_subtitle()
        ]
        _header = [header_text_content for header_text_content in _header if header_text_content.text is not None]
        return _header

    @staticmethod
    def is_single_switch(content):
        return len(content) == 1 and isinstance(content[0], ObjSwitch)

    @staticmethod
    def _add_default_style(container, default_style):
        for current_content in default_style:
            container.css_options = (css.add(container.css_options, current_content))
        return container

    def _get_line(self) -> ObjLine:
        line_obj = ObjLine(
            css_options=self._line_style,
            render_condition=self.properties.get("line", False)
        ) \
            .set_thickness(self.properties.get("line_thickness", "3px")) \
            .set_size("100%") \
            .set_color(self.properties.get("line_color", "#40db62")) \
            .set_alignment_center

        return line_obj

    def _get_title(self) -> ObjText:
        return title if isinstance(title := self.properties.get("title"), ObjText) else \
            ObjText(
                title,
                css_options=[css.Color("#333"), css.FontSize("16px")],
                render_condition=self.properties.get("title")
            )

    def _get_subtitle(self) -> ObjText:
        return subtitle if isinstance(subtitle := self.properties.get("subtitle"), ObjText) else \
            ObjText(
                subtitle,
                css_options=[css.Color("#b0b0b0"), css.FontSize("14px"), css.FontWeight("500")],
                render_condition=self.properties.get("subtitle")
            )

    def _get_positional_args(self) -> dict:
        return {
            properties: value for properties, value in self.properties.items()
            if properties not in self.obj_container_args
        }

    def _get_container_tooltip(self) -> ObjTooltip:
        container_tooltip = ObjTooltip(
            text=self.properties.get("tooltip", ""),
            render_condition=self.properties.get("tooltip"),
            css_options=self._tooltip_style
        )

        return container_tooltip

    def to_json_structure(self, visitor: BaseRender):
        content = self._get_container().to_json_structure(visitor)
        return content
