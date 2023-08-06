import unittest
from looqbox import ObjText


class TestLooqObject(unittest.TestCase):
    """
    Test looq object using ObjText since it is a child of LooqObject and not abstract
    """

    def test_equals(self):
        looq_object = ObjText("teste")
        looq_object2 = ObjText("teste")

        self.assertEqual(looq_object, looq_object2)

    def test_not_equals(self):
        looq_object = ObjText("teste")
        looq_object2 = ObjText("teste2")

        self.assertNotEqual(looq_object, looq_object2)

    def test_hash_equals(self):
        looq_object = ObjText("teste")

        looq_object2 = ObjText("teste")
        random_looq_objs = [ObjText("teste2") for _ in range(10)]
        random_looq_objs.insert(5, looq_object2)

        self.assertIn(looq_object, random_looq_objs)

    def test_hash_not_equals(self):
        looq_object = ObjText("teste")

        looq_object2 = ObjText("teste2")
        random_looq_objs = [ObjText("teste2") for _ in range(10)]
        random_looq_objs.insert(5, looq_object2)

        self.assertNotIn(looq_object, random_looq_objs)


if __name__ == '__main__':
    unittest.main()
