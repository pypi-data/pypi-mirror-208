
import unittest
from ..my_lib.dog import Dog

class TestDog(unittest.TestCase):
    def setUp(self):
        self.dog = Dog('Fido')

    def test_bark(self):
        self.assertEqual(self.dog.bark(), 'Fido is barking')
