"""Contrôles statiques sans accès au lab et sans exécution des playbooks."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import yaml
from jinja2 import Environment, StrictUndefined


def main():
    root = Path(__file__).resolve().parents[1]
    errors = []
    checked = 0
    yaml_paths = list((root / "playbooks").glob("*.yml"))
    yaml_paths += [root / "inventory/hosts.yml",
                   root / "inventory/group_vars/all/vars.yml",
                   root / "inventory/group_vars/all/vault.yml.example",
                   root / "collections/requirements.yml"]
    for path in yaml_paths:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            checked += 1
        except (yaml.YAMLError, OSError) as exc:
            errors.append(f"{path.relative_to(root)} : {exc}")

    context = yaml.safe_load((root / "inventory/group_vars/all/vars.yml").read_text())
    context.update({
        "vault_winrm_user": "example_user",
        "vault_winrm_password": "EXAMPLE_ONLY",
        "vault_win_local_password": "EXAMPLE_ONLY",
        "fog_mysql_password": "EXAMPLE_ONLY",
        "ansible_managed": "Static validation with fictitious values",
    })
    environment = Environment(undefined=StrictUndefined)
    for path in (root / "playbooks/templates").glob("*.j2"):
        try:
            template = environment.from_string(path.read_text())
            for wallpaper in (False, True):
                rendered = template.render(**context, win_custom_wallpaper_enabled=wallpaper)
                if path.name.endswith(".xml.j2"):
                    ET.fromstring(rendered)
            checked += 1
        except Exception as exc:
            errors.append(f"{path.relative_to(root)} : {exc}")
    for path in (root / "playbooks/files").glob("*.xml"):
        try:
            ET.parse(path)
            checked += 1
        except (ET.ParseError, OSError) as exc:
            errors.append(f"{path.relative_to(root)} : {exc}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK : {checked} fichiers YAML/Jinja2/XML vérifiés ; aucun test matériel exécuté.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
