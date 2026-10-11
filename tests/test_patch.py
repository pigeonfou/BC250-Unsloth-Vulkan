import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from patch import patch_content, MARK_GPU, MARK_MEM, ACCEL_OLD, DEVICE_OLD, MEM_OLD

class GuardedPatchTests(unittest.TestCase):
    def test_backend_idempotent(self):
        src = "def f():\n" + ACCEL_OLD + "foo\n" + DEVICE_OLD + "\n"
        result, changed = patch_content(Path("sd_cpp_backend.py"), src)
        self.assertTrue(changed)
        self.assertEqual(result.count(MARK_GPU), 2)
        result2, changed2 = patch_content(Path("sd_cpp_backend.py"), result)
        self.assertFalse(changed2)
        self.assertEqual(result, result2)

    def test_server_idempotent(self):
        src = "def f():\n" + MEM_OLD + "\n"
        result, changed = patch_content(Path("sd_cpp_server.py"), src)
        self.assertTrue(changed)
        self.assertEqual(result.count(MARK_MEM), 1)
        result2, changed2 = patch_content(Path("sd_cpp_server.py"), result)
        self.assertFalse(changed2)
        self.assertEqual(result, result2)

    def test_unknown_version_refused(self):
        with self.assertRaises(RuntimeError):
            patch_content(Path("sd_cpp_backend.py"), "changed upstream")

if __name__ == "__main__":
    unittest.main()
