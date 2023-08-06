from geometry import Helper
from unittest import TestCase
import numpy as np


class TestHelper(TestCase):
  
  def setUp(self) -> None:
    self.helper = Helper.instance()
    
  def test_helper_singleton(self):
    try:
      Helper()
    except RuntimeError as err:
      self.assertEqual(err.__str__(), 'Call instance() instead')
  
  def test_to_point_matrix(self):
    points = [0, 0, 1000, 1000, 0, 1000, 1000, 1000, 1000, 0, 1000, 1000, 0, 0, 0, 1000, 0, 0,
              1000, 1000, 0, 0, 1000, 0]
    self.assertIsNone(self.helper.to_points_matrix(points))
    self.assertEqual(self.helper.to_points_matrix(np.array(points))[0][2], 1000)

  def test_points_from_string(self):
    # test with comma separator
    point_string = "0,0,1000,1000,0,1000,1000,1000,1000,0,1000,1000,0,0,0,1000,0,0,1000,1000,0,0,1000,0"
    self.assertIsNone(self.helper.points_from_string(point_string))
    # Test with space separator
    point_string = "0 0 1000 1000 0 1000 1000 1000 1000 0 1000 1000 0 0 0 1000 0 0 1000 1000 0 0 1000 0"
    points = self.helper.points_from_string(point_string)
    self.assertEqual(points.size, 24)
    self.assertEqual(points[7][1], 1000.0)
  
  def test_remove_last_point_from_string(self):
    point_string = "0 0 1000 1000 0 1000 1000 1000 1000 0 1000 1000 0 0 0 1000 0 0 1000 1000 0 0 1000 0"
    trimmed_string = "0 0 1000 1000 0 1000 1000 1000 1000 0 1000 1000 0 0 0 1000 0 0 1000 1000 0"
    new_point_string = self.helper.remove_last_point_from_string(point_string)
    self.assertNotEqual(point_string, new_point_string)
    self.assertEqual(trimmed_string, new_point_string)
    
  def test_invert_points(self):
    points = [0, 0, 1000, 1000, 0, 1000, 1000, 1000, 1000, 0, 1000, 1000, 0, 0, 0, 1000, 0, 0,
              1000, 1000, 0, 0, 1000, 0]
    inverted_points = self.helper.invert_points(points)
    self.assertNotEqual(inverted_points, points)
    self.assertEqual(inverted_points[1], points[len(points) - 2])
    

