import unittest
from serializers import SerializersFactory, SerializerType

from test_constants import PRIMITIVES
from test_constants import rec_func
from test_constants import gen
from test_constants import decorated_func
from test_constants import T


class SerializationTestCase(unittest.TestCase):

    def setUp(self):
        self.xml = SerializersFactory.create_serializer(SerializerType.XML)

    def test_primitives(self):
        """Test primitive types serialization"""

        primitives = self.xml.dumps(PRIMITIVES)
        primitives = self.xml.loads(primitives)

        self.assertEqual(PRIMITIVES, primitives)

    def test_func(self):
        """Test func serialization"""

        func = self.xml.dumps(rec_func)
        func = self.xml.loads(func)

        before = [rec_func(i) for i in range(100)]
        after = [func(i) for i in range(100)]

        self.assertEqual(before, after)

    def test_gen(self):
        """Test gen serialization"""

        s_gen = self.xml.dumps(gen)
        s_gen = self.xml.loads(s_gen)

        before = [*gen()]
        after = [*s_gen()]

        self.assertEqual(before, after)

    def test_decorator(self):
        """Test decorator serialization"""

        df = self.xml.dumps(decorated_func)
        df = self.xml.loads(df)

        before = [decorated_func(i) for i in range(100)]
        after = [df(i) for i in range(100)]

        self.assertEqual(before, after)

    def test_class(self):
        """Test class serialization"""

        sT = self.xml.dumps(T)
        sT = self.xml.loads(sT)

        before = [T.A, T.B, T.C, T._X, T.tst4(), T.lol()]
        after = [sT.A, sT.B, sT.C, sT._X, sT.tst4(), sT.lol()]

        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
