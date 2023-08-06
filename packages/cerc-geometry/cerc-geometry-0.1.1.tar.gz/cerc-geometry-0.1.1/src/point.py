"""
Point module
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Pilar Monsalvete Alvarez de Uribarri pilar.monsalvete@concordia.ca
"""

import math
import numpy as np
import sys


class Point:
  """
  Point class
  """

  def __init__(self, coordinates: np.ndarray):
    self._coordinates = coordinates

  @property
  def coordinates(self):
    """
    Get point coordinates
    :return: [ndarray]
    """
    return self._coordinates

  def distance_to_point(self, other_point):
    """
    Calculates distance between points in an n-D Euclidean space
    :param other_point: point or vertex
    :return: float
    """
    try:
      power = 0
      for dimension in range(0, len(self.coordinates)):
        power += math.pow(other_point.coordinates[dimension]-self.coordinates[dimension], 2)
      distance = math.sqrt(power)
      return distance
    except Exception as error:
      sys.stderr.write(f'An error occurred: {error}')
    
   
