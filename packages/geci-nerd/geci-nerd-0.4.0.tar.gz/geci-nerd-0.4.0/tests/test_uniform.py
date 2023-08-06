import numpy as np
from unittest import TestCase
from nerd.density_functions import uniform


class TestUniform(TestCase):
    def setUp(self) -> None:
        self.w = 60
        self.p = 2

    def test_uniform_scalar_inside(self):
        self.assertAlmostEqual(uniform(0, self.w, self.p), self.p)

    def test_uniform_scalar_outside(self):
        self.assertAlmostEqual(uniform(self.w / 2 + 1, self.w, self.p), 0)

    def test_uniform_vector(self):
        density = uniform(np.array([-self.w, 0, self.w / 3, self.w / 2, self.w]), self.w, self.p)
        expected = np.array([0, self.p, self.p, 0, 0])
        self.assertTrue(np.all(density == expected))
