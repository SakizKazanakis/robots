import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cad.legs.hybrid import plate,pair
from cad.legs.engineering import chassis,payload,export

class TestHybrid(unittest.TestCase):
    def test_window_reduces_volume(self): self.assertLess(plate(window=True).Volume(),plate(window=False).Volume())
    def test_thickness_changes_volume(self): self.assertGreater(plate(thickness=9).Volume(),plate(thickness=6.5).Volume())
    def test_pair(self): self.assertEqual(len(pair(95)),2)
    def test_chassis(self): self.assertTrue(chassis().isValid())
    def test_payload(self): self.assertTrue(payload().isValid())
    def test_export_and_reimport(self):
        with tempfile.TemporaryDirectory() as d: self.assertEqual(len(export(d)),6)

if __name__=="__main__": unittest.main()
