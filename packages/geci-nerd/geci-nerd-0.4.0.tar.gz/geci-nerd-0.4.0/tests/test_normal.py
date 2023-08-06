import numpy as np
from unittest import TestCase
from nerd.density_functions import normal


class TestNormal(TestCase):
    def setUp(self) -> None:
        self.w = 60
        self.p = 1
        self.altura_campana = self.p / np.sqrt(2 * np.pi * (self.w / 4) ** 2)

    def test_normal_scalar_inside(self):
        self.assertAlmostEqual(normal(0, self.w, self.p), self.altura_campana)

    def test_normal_scalar_outside(self):
        self.assertAlmostEqual(normal(self.w / 2 + 1, self.w, self.p), 0, places=2)

    def test_normal_vector(self):
        density = normal(np.array([-self.w, 0, self.w]), self.w, self.p)
        expected = np.array([0, self.altura_campana, 0])
        self.assertTrue(np.allclose(density, expected, atol=1e-05))
