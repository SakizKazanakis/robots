import unittest,tempfile,math
from dataclasses import replace
from cad.joints.cartridge_v05 import Joint,components,export,OEM_CYLINDER_AXES
class CartridgeTests(unittest.TestCase):
 def setUp(self):self.p=Joint()
 def test_components_valid(self):
  for name,part in components(self.p).items():
   self.assertTrue(part.isValid(),name)
   self.assertGreater(part.Volume(),0)
 def test_oem_cylinder_axes(self):
  for x,y,z in OEM_CYLINDER_AXES["housing_r1p4_y27p2"]:
   self.assertAlmostEqual(math.hypot(x,z),23.5,places=3)
 def test_bearing_counterbore(self):
  self.assertGreater(len(components(self.p)["opposite_bearing_housing_ASSUMED"].Faces()),5)
 def test_parameter_sensitive(self):
  self.assertGreater(components(replace(self.p,adapter_od=78))["output_adapter_ASSUMED"].Volume(),components(self.p)["output_adapter_ASSUMED"].Volume())
 def test_illogical_dimensions_rejected(self):
  with self.assertRaises(ValueError):replace(self.p,adapter_od=60).validate()
 def test_step_export(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(len(export(self.p,d)["parts"]),7)
if __name__=="__main__":unittest.main()
