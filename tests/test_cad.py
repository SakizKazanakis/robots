"""Analytical geometry tests; no claims about physical behavior."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"cad"))
from spider_cad import Parameters, joints, mounting_points, estimate_load, validate

class ConceptTests(unittest.TestCase):
    def setUp(self):
        self.p=Parameters()

    def test_architectures(self):
        self.assertEqual(len(list(mounting_points(self.p,6))),6)
        self.assertEqual(len(list(mounting_points(self.p,4))),4)

    def test_joint_link_lengths(self):
        a,b,c,d=joints(self.p)
        for segment,expected in [(a.sub(b),self.p.coxa),(b.sub(c),self.p.femur),(c.sub(d),self.p.tibia)]:
            self.assertAlmostEqual(segment.Length,expected,places=6)

    def test_vertical_jacobian(self):
        p=self.p
        a,b=math.radians(p.hip_pitch_deg),math.radians(p.knee_pitch_deg)
        h=1e-4
        def z(q1,q2):
            return -(p.femur*math.sin(q1)+p.tibia*math.sin(q1+q2))/1000
        f=p.assumed_total_mass_kg*p.gravity_m_s2/p.contact_legs_loadcase
        values=estimate_load(p)
        self.assertAlmostEqual(abs((z(a+h,b)-z(a-h,b))/(2*h)*f),
                               values["hip_static_vertical_only_Nm"],delta=1e-4)
        self.assertAlmostEqual(abs((z(a,b+h)-z(a,b-h))/(2*h)*f),
                               values["knee_static_vertical_only_Nm"],delta=1e-4)

    def test_reject_bad_leg_count(self):
        with self.assertRaises(AssertionError):
            validate(self.p,5)

    def test_initial_nominal_clearance(self):
        p=self.p
        ground=joints(p)[3].z-p.foot_radius
        clearance=p.body_center_z-p.body_thickness/2-ground
        self.assertGreater(clearance,60)
        self.assertLess(clearance,110)

if __name__=="__main__":
    unittest.main()
