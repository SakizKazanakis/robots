"""Regression tests for long-reach reference CAD, NOT proof of mechanical fitness."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
import ezdxf
from cad.legs.long_reach import (
    LegDesign, plate, spacer, cheek_pair, leg_points, make_module,
    export, mass_estimate, moment_sweep, from_canonical_parameters
)

class LongReachTests(unittest.TestCase):
    def setUp(self):self.p=LegDesign()

    def test_femur_span(self):
        a,b,c,d=leg_points(self.p)
        self.assertAlmostEqual(math.dist(b,c),self.p.femur)
        self.assertAlmostEqual(math.dist(c,d),self.p.tibia)
        self.assertAlmostEqual(math.dist(a,b),self.p.coxa)

    def test_canonical_parameter_source(self):
        root=Path(__file__).resolve().parents[1]
        p=from_canonical_parameters(root/"cad/parameters.json")
        self.assertEqual((p.coxa,p.femur,p.tibia),(90,135,160))
        self.assertEqual((p.hip_deg,p.knee_deg),(35,90))

    def test_plate_validity_and_single_solid(self):
        for material in ("plywood","aluminum"):
            for length in (self.p.femur,self.p.tibia):
                shape=plate(length,self.p,material)
                self.assertTrue(shape.isValid())
                self.assertEqual(len(shape.Solids()),1)
                self.assertGreater(shape.Volume(),0)

    def test_windows_reduce_volume(self):
        self.assertLess(plate(135,self.p).Volume(),plate(135,self.p,windows=False).Volume())

    def test_thickness_changes_volume(self):
        p=replace(self.p,plate_thickness=9)
        self.assertGreater(plate(135,p).Volume(),plate(135,self.p).Volume())

    def test_two_cheeks_separated_by_gap(self):
        a,b=cheek_pair(135,self.p)
        self.assertAlmostEqual(a.BoundingBox().zmin-b.BoundingBox().zmax,self.p.plate_gap)

    def test_tube_has_bore(self):
        s=spacer(self.p)
        self.assertTrue(s.isValid())
        self.assertGreater(s.Volume(),0)
        self.assertLess(s.Volume(),math.pi*(self.p.spacer_outer_diameter/2)**2*self.p.plate_gap)

    def test_invalid_dimensions_rejected(self):
        with self.assertRaises(ValueError):replace(self.p,plate_gap=40).validate()
        with self.assertRaises(ValueError):replace(self.p,window_width=35).validate()

    def test_reference_reach(self):
        p=self.p
        clearance=-leg_points(p)[3][2]+p.foot_radius+p.body_underside_z
        self.assertGreater(clearance,150)

    def test_weight_assumptions_are_distinct(self):
        m=mass_estimate(self.p)
        self.assertGreater(m["aluminum"]["sum_link_plates_g"],m["plywood"]["sum_link_plates_g"])

    def test_detects_drive_overload_case(self):
        s=moment_sweep(self.p)
        self.assertGreater(s["3"]["maximum_knee_Nm"],2.5)
        self.assertGreater(s["3"]["maximum_factor_2p5_knee_Nm"],7)

    def test_three_motor_envelopes(self):
        a=make_module(self.p)
        self.assertEqual(len([x for x in a.children if "MOTOR_ENVELOPE" in x.name]),3)

    def test_step_and_dxf_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            result=export(self.p,d)
            self.assertEqual(len(result["parts"]),8)
            for part in result["parts"].values():
                self.assertTrue(Path(d,part["step"]).exists())
                if "dxf" in part:
                    doc=ezdxf.readfile(Path(d,part["dxf"]))
                    self.assertFalse(doc.audit().has_errors)
                    self.assertGreater(len(doc.modelspace()),10)

if __name__=="__main__":unittest.main()
