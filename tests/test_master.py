"""Régressions statiques ; aucun accès Windows ou réseau."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
NS = {'u': 'urn:schemas-microsoft-com:unattend'}


class MasterTests(unittest.TestCase):
    def test_credentials_survive_xml_rendering(self):
        context = yaml.safe_load((ROOT / 'inventory/group_vars/all/vars.yml').read_text())
        password = 'Test<&>"\'Password42'
        context.update(vault_winrm_user='LabAdmin', vault_winrm_password=password,
                       vault_win_local_password=password)
        env = Environment(undefined=StrictUndefined)
        for name in ('autounattend.xml.j2', 'unattend.xml.j2'):
            for wallpaper in (False, True):
                with self.subTest(template=name, wallpaper=wallpaper):
                    text = env.from_string((ROOT / 'playbooks/templates' / name).read_text()).render(
                        **context, win_custom_wallpaper_enabled=wallpaper)
                    xml = ET.fromstring(text)
                    values = xml.findall('.//u:Password/u:Value', NS)
                    self.assertEqual(len(values), 2)
                    self.assertTrue(all(v.text == password for v in values))

    def test_requested_apps_are_installed_and_checked(self):
        variables = yaml.safe_load((ROOT / 'inventory/group_vars/all/vars.yml').read_text())
        apps = variables['win_master_apps']
        self.assertEqual({a['package'] for a in apps},
                         {'firefox', 'brave', 'googlechrome', 'libreoffice-fresh',
                          'pdfgear', 'anydesk', '7zip', 'thunderbird'})
        self.assertEqual(len(apps), 8)
        libreoffice = next(a for a in apps if a['name'] == 'LibreOffice')
        self.assertEqual(libreoffice['install_args'], 'UI_LANGS=fr')
        tasks = yaml.safe_load((ROOT / 'playbooks/customize-win11-reference.yml').read_text())[0]['tasks']
        install = next(t for t in tasks if t.get('chocolatey.chocolatey.win_chocolatey', {}).get('name') == '{{ item.package }}')
        self.assertEqual(install['loop'], '{{ win_master_apps }}')
        self.assertNotIn('ignore_errors', install)
        checks = next(t for t in tasks if t.get('register') == 'master_app_files')
        self.assertEqual(checks['loop'], '{{ win_master_apps }}')
        assertion = next(t for t in tasks if t.get('loop') == '{{ master_app_files.results }}')
        self.assertIn('item.stat.exists', assertion['ansible.builtin.assert']['that'])
        collections = yaml.safe_load((ROOT / 'collections/requirements.yml').read_text())
        self.assertIn({'name': 'chocolatey.chocolatey'}, collections['collections'])

    def test_sysprep_preserves_windows_components_and_logs(self):
        play = yaml.safe_load((ROOT / 'playbooks/sysprep-win11.yml').read_text())[0]
        tasks = play['tasks']
        self.assertIn('ansible.builtin.assert', tasks[0])
        self.assertIn('sysprep_confirm', str(tasks[0]))
        self.assertFalse(any(t.get('ansible.windows.win_file', {}).get('state') == 'absent'
                             for t in tasks))
        text = str(tasks)
        self.assertNotIn('takeown', text)
        self.assertNotIn('icacls', text)
        self.assertNotIn('sysprep_Cleanup.xml', text)
        self.assertIn('RebootPending', text)
        templates = [t for t in tasks if 'ansible.windows.win_template' in t]
        self.assertEqual(len(templates), 1)
        self.assertTrue(templates[0]['no_log'])


if __name__ == '__main__':
    unittest.main()
