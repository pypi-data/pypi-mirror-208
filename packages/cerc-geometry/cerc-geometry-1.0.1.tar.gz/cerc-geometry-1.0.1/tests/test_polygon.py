from unittest import TestCase
from geometry import Point
from geometry import Polygon
import numpy as np


class TestPolygon(TestCase):
  
  def setUp(self) -> None:
    self._coordinates = [[-1.3125511246773556, 7.224814483190954], [-1.3131144073658163, 7.225133803311778],
                         [-1.3137179245338189, 7.225313420780125], [-1.3144622623732403, 7.2245550354264765],
                         [-1.314663434762565, 7.222938472924113], [-1.3138989796833869, 7.221202158613096],
                         [-1.3116860834049078, 7.219745246059503], [-1.3085477941360182, 7.220523597186585],
                         [-1.3072401736067434, 7.223716818554365], [-1.3125511246773556, 7.224814483190954]]
    self._vertices = [[0, 0, 1000], [1000, 0, 1000], [1000, 1000, 1000], [0, 1000, 1000], [0, 0, 0], [1000, 0, 0],
                      [1000, 1000, 0], [0, 1000, 0]]
    self.polygon = Polygon(np.array(self._coordinates))
    self.polygon_2 = Polygon(np.array(self._vertices))
  
  def test_polygon_properties(self):
    self.assertIsInstance(self.polygon.points[0], Point)
    self.assertIsNone(self.polygon.points_list)
    self.assertEqual(self.polygon.normal, [0, 0, 0])
    self.assertEqual(self.polygon.points[0].coordinates[0], -1.3125511246773556)
    self.assertEqual(self.polygon.inverse[0][0], -1.3125511246773556)
    self.assertIsNone(self.polygon_2.triangles)  # issue with trimesh module import
    self.assertEqual(self.polygon_2.vertices.size, 0)  # issue with trimesh module import
