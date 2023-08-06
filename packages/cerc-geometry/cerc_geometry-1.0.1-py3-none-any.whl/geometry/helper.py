"""
Geometry class contains different geometry functions for manipulating
2D and 3D geometry objects
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2023 Concordia CERC group
"""
import numpy as np
from typing import List
import sys
import math


class Helper(object):

    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def to_points_matrix(cls, points: np.ndarray) -> np.ndarray:
        """
        Transform a point vector into a point matrix
        :param points: [x, y, z, x, y, z ...]
        :return: [[x,y,z],[x,y,z]...]
        """
        try:
            rows = points.size // 3
            points = points.reshape(rows, 3)
            return points
        except TypeError:
            sys.stderr.write('Expect point to be a numpy array')
        except Exception as error:
            sys.stderr.write(f'An error occurred while transforming point vector to matrix: {error}')

    @classmethod
    def points_from_string(cls, coordinates: str) -> np.ndarray:
        """
        Converts a string of coordinates go a point matrix
        :param coordinates: "x y z..."
        :return: [[x,y,z],[x,y,z]...]
        """
        try:
            points = np.fromstring(coordinates, dtype=float, sep=' ')
            points = cls.to_points_matrix(points)
            return points
        except TypeError:
            sys.stderr.write('Expect coordinates to be a string of floats separated by spaces')
        except Exception as error:
            sys.stderr.write(f'An error occurred: {error}')
        
    @classmethod
    def remove_last_point_from_string(cls, points: str) -> str:
        """
        Ignore last point in a string of points
        :param points:
        :return:
        """
        try:
            array = points.split(' ')
            res = " "
            return res.join(array[0:len(array) - 3])
        except TypeError:
            sys.stderr.write('Expects point to be a string of point values separated by spaces')
        except Exception as error:
            sys.stderr.write(f'An error occurred: {error}')

    @classmethod
    def invert_points(cls, points: List) -> List:
        """
        Reverses a list of point values
        :param points: [x,y,z...]
        :return: [...,z,y,x]
        """
        try:
            res = []
            for point in points:
                res.insert(0, point)
            return res
        except TypeError:
            sys.stderr.write('Expects point to be a list')
        except Exception as error:
            sys.stderr.write(f'An error occurred: {error}')
        
    @classmethod
    def ground_area(cls, points: List) -> float:
        """
        Get ground surface area in square meters
        :return: float
        """
        # New method to calculate area
        try:
            if len(points) < 3:
                sys.stderr.write('Warning: the area of a line or point cannot be calculated 1. Area = 0\n')
                sys.exit(1)
            alpha = 0
            vec_1 = points[1] - points[0]
            for i in range(2, len(points)):
                vec_2 = points[i] - points[0]
                alpha += cls.angle_between_vectors(vec_1, vec_2)
            if alpha == 0:
                sys.stderr.write('Warning: the area of a line or point cannot be calculated 2. Area = 0\n')
                sys.exit(1)
            #
            horizontal_points = points
            area = 0
            for i in range(0, len(horizontal_points) - 1):
                point = horizontal_points[i]
                next_point = horizontal_points[i + 1]
                area += (next_point[1] + point[1]) / 2 * (next_point[0] - point[0])
            next_point = horizontal_points[0]
            point = horizontal_points[len(horizontal_points) - 1]
            area += (next_point[1] + point[1]) / 2 * (next_point[0] - point[0])
            _area = abs(area)
            return _area
        except TypeError as error:
            sys.stderr.write(f'A type error occurred: {error}')
        except IndexError as error:
            sys.stderr.write(f'A list index error occurred: {error}')
        except Exception as error:
            sys.stderr.write(f'An error occurred: {error}')
            
    @classmethod
    def angle_between_vectors(cls, vec_1: List, vec_2: List):
        """
        angle between vectors in radians
        :param vec_1: vector
        :param vec_2: vector
        :return: float
        """
        try:
            if np.linalg.norm(vec_1) == 0 or np.linalg.norm(vec_2) == 0:
                sys.stderr.write("Warning: impossible to calculate angle between planes' normal. Return 0\n")
                sys.exit(1)
            cosine = np.dot(vec_1, vec_2) / np.linalg.norm(vec_1) / np.linalg.norm(vec_2)
            if cosine > 1 and cosine - 1 < 1e-5:
                cosine = 1
            elif cosine < -1 and cosine + 1 > -1e-5:
                cosine = -1
            alpha = math.acos(cosine)
            return alpha
        except TypeError as error:
            sys.stderr.write(f'A type error occurred: {error}')
        except Exception as error:
            sys.stderr.write(f'An error occurred: {error}')

