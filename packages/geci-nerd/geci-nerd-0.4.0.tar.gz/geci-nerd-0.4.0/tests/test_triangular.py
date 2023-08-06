import numpy as np
from unittest import TestCase
from nerd.density_functions import triangular


class TestTriangular(TestCase):
    def setUp(self) -> None:
        self.w = 60
        self.p = 2

    def test_triangular_scalar_inside(self):
        self.assertAlmostEqual(triangular(0, self.w, self.p), self.p)

    def test_triangular_scalar_outside(self):
        self.assertAlmostEqual(triangular(self.w / 2 + 1, self.w, self.p), 0)

    def test_triangular_vector(self):
        density = triangular(np.array([-self.w, 0, self.w / 3, self.w / 2, self.w]), self.w, self.p)
        expected = np.array([0, self.p, self.p / 3, 0, 0])
        self.assertTrue(np.allclose(density, expected, rtol=1e-10))
