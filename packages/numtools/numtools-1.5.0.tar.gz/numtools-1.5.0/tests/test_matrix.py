"""vg>2.0 does not provide vg.matrix.transform"""
import numpy as np
from numtools.vgextended import matrix_transform


def test_matrix_1():
    vertices = np.array([[0.73, -0.45, 1.2], [1.0, 2.0, 3.0], [-4.0, 5.0, 6.3]])
    matrix = np.array(
        [
            [-0.20963784, 0.95414465, 0.21368192, -6.33760075],
            [0.5698353, 0.29681044, -0.76628408, -3.19552193],
            [-0.79456888, -0.03887864, -0.605928, 1.10286822],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    expected = np.array(
        [
            [-6.66358316, -3.83264776, -0.18678528],
            [-3.99790354, -4.330918, -1.58724195],
            [0.61786995, -8.81840064, 0.26940413],
        ]
    )
    results = matrix_transform(vertices, matrix)
    np.testing.assert_array_almost_equal(results, expected, decimal=7)


def test_matrix_2():
    vertices = np.array([0.73, -0.45, 1.2])
    matrix = np.array(
        [
            [-0.20963784, 0.95414465, 0.21368192, -6.33760075],
            [0.5698353, 0.29681044, -0.76628408, -3.19552193],
            [-0.79456888, -0.03887864, -0.605928, 1.10286822],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    expected = np.array([-6.66358316, -3.83264776, -0.18678528])
    results = matrix_transform(vertices, matrix)
    np.testing.assert_array_almost_equal(results, expected, decimal=7)
    # ensure vertices didn't get modified
    np.testing.assert_array_almost_equal(vertices, np.array([0.73, -0.45, 1.2]))
