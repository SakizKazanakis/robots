"""Parametric CAD geometry regression, not structural verification."""
import unittest, math, tempfile
from pathlib import Path
from dataclasses import replace
from cad.legs.exoframe_v04 import Design, cheek, spacer, places, components, export, basic_load_sweep, load_canonical

class EXOFRAMEGeometricTests(unittest.TestCase):
    def setUp(self):self.p=Design()
    def test_lengths(self):
        a,b,c,d=places(self.p)
        for actual,expected in ((math.dist(a,b),self.p.coxa),(math.dist(b,c),self.p.femur),
                                (math.dist(c,d),self.p.tibia)):
            self.assertAlmostEqual(actual,expected,places=5)
    def test_canonical_source(self):
        root=Path(__file__).resolve().parents[1]
        p=load_canonical(root/"cad/parameters.json")
        self.assertEqual((p.coxa,p.femur,p.tibia),(90,135,160))
    def test_solids(self):
        for material in ("plywood","aluminum"):
            for L in (self.p.femur,self.p.tibia):
                sh=cheek(L,self.p,material)
                self.assertTrue(sh.isValid())
                self.assertEqual(len(sh.Solids()),1)
    def test_windows_remove_material(self):
        self.assertLess(cheek(135,self.p).Volume(),cheek(135,self.p,cutouts=False).Volume())
    def test_thickness_parameter(self):
        self.assertGreater(cheek(135,replace(self.p,ply_t=9)).Volume(),cheek(135,self.p).Volume())
    def test_material_keeps_geometry(self):
        self.assertEqual(places(self.p),places(replace(self.p,aluminum_t=5)))
    def test_spacer_is_hollow(self):
        s=spacer(self.p)
        self.assertTrue(s.isValid())
        self.assertLess(s.Volume(),math.pi*(self.p.spacer_od/2)**2*self.p.cavity_width)
    def test_unique_components(self):
        for kind in ("plywood","aluminum"):
            cs=components(self.p,kind)
            self.assertEqual(len(cs),38)
            self.assertEqual(len(set(x[0] for x in cs)),len(cs))
            self.assertEqual(sum("MOTOR_ENVELOPE" in n for n,_,_ in cs),3)
            self.assertEqual(sum("DIAGONAL_SPATIAL_BRACE" in n for n,_,_ in cs),4)
    def test_overload_not_misreported(self):
        k=basic_load_sweep(self.p)
        self.assertGreater(k["knee_Nm_max_vertical_only"],2.5)
        self.assertGreater(k["knee_Nm_max_with_hypothetical_2p5_multiplier"],7)
    def test_invalid_rejected(self):
        with self.assertRaises(ValueError):replace(self.p,cavity_width=50).validate()
    def test_step_exports_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            audit=export(self.p,Path(d))
            self.assertEqual(len(audit["parts"]),8)
            self.assertEqual(audit["parts"]["plywood_assembly"]["component_count"],38)
            self.assertEqual(len(list(Path(d).glob("*.step"))),8)

if __name__=="__main__":unittest.main()
