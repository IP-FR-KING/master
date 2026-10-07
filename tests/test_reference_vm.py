import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/create_reference_vm.py'
spec = importlib.util.spec_from_file_location('create_reference_vm', SCRIPT)
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)


class ReferenceVMTests(unittest.TestCase):
    def test_supported_hardware_and_no_install_answer_file(self):
        cmd = vm.command(Path('/tmp/Windows 11.iso'), Path('/tmp/new.qcow2'), 'test', 'default')
        self.assertIn('8192', cmd)
        self.assertIn('backend.type=emulator,backend.version=2.0,model=tpm-crb', cmd)
        self.assertIn('path=/tmp/new.qcow2,size=80,format=qcow2,bus=sata', cmd)
        self.assertIn('firmware.feature0.enabled=yes', cmd[cmd.index('--boot') + 1])
        self.assertNotIn('--unattended', cmd)

    def test_preview_does_not_create_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            iso, disk = Path(directory) / 'test.iso', Path(directory) / 'test.qcow2'
            iso.touch()
            result = subprocess.run([sys.executable, str(SCRIPT), '--iso', str(iso), '--disk', str(disk)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(disk.exists())
            self.assertIn('Aperçu uniquement', result.stdout)

    def test_existing_disk_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            iso, disk = Path(directory) / 'test.iso', Path(directory) / 'test.qcow2'
            iso.touch()
            disk.write_text('existing')
            result = subprocess.run([sys.executable, str(SCRIPT), '--iso', str(iso), '--disk', str(disk), '--create'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(disk.read_text(), 'existing')


if __name__ == '__main__':
    unittest.main()
