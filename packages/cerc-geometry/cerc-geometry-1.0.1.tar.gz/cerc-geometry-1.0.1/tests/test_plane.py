from geometry import Plane
from geometry import Point
from unittest import TestCase
import numpy as np


class TestPlane(TestCase):
  
  def setUp(self) -> None:
    self.plane = Plane(Point(np.array([10, 5, 6])), [2, 3, 5])
    
  def test_opposite_normal(self):
    self.assertEqual(self.plane.opposite_normal[0], -2)
    self.assertEqual(self.plane.opposite_normal[2], -5)
    self.assertEqual(self.plane.origin.coordinates[1], 5)
    self.assertNotEqual(self.plane.opposite_normal[1], 3)
  
  def test_equation(self):
    self.assertTupleEqual(self.plane.equation, tuple([2, 3, 5, -65]))
  
  def test_equation_with_wrong_coordinates(self):
    plane = Plane(Point(np.array([5, 6])), [2, 3, 5])
    self.assertIsNone(plane.equation)