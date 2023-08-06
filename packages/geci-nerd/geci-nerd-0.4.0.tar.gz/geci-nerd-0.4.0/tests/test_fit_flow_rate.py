from unittest import TestCase

from nerd.calibration import fit_flow_rate


class TestFit_flow_rate(TestCase):
    def test_fit_flow_rate(self):
        f1 = fit_flow_rate([0, 1, 2], [0, 2, 4])
        self.assertAlmostEqual(f1(6), 12)
        f2 = fit_flow_rate([1, 2, 3], [2, 9, 22])
        self.assertAlmostEqual(f2(4), 41)
