from unittest import TestCase
from geometry import Polyhedron
from geometry import Polygon
import numpy as np


class TestPolyhedron(TestCase):
  
  def setUp(self) -> None:
    self._coordinates = [[-1.3125511246773556, 7.224814483190954], [-1.3131144073658163, 7.225133803311778],
                         [-1.3137179245338189, 7.225313420780125], [-1.3144622623732403, 7.2245550354264765],
                         [-1.314663434762565, 7.222938472924113], [-1.3138989796833869, 7.221202158613096],
                         [-1.3116860834049078, 7.219745246059503], [-1.3085477941360182, 7.220523597186585],
                         [-1.3072401736067434, 7.223716818554365], [-1.3125511246773556, 7.224814483190954]]
    
    self._vertices = [[0, 0, 1000], [1000, 0, 1000], [1000, 1000, 1000], [0, 1000, 1000], [0, 0, 0], [1000, 0, 0],
                      [1000, 1000, 0], [0, 1000, 0]]
    polygon_2 = Polygon(np.array(self._vertices))
    self.polyhedron = Polyhedron(polygon_2)
  
  def test_polyhedron_properties(self):
    # TODO: implement test assertions
    pass
