# Master Windows 11

Préparation d'un master Windows 11 : installation automatisée, personnalisation,
Sysprep, capture et déploiement avec FOG.

Ce dépôt permet de continuer les scripts et la documentation depuis Codex Cloud
sur iPhone, même quand le PC est éteint. Les essais Windows, les VM, le SSD et FOG
restent sur le PC et sont testés par l'utilisateur.

- [Contexte et prochaines étapes](docs/CONTEXTE.md)
- [Configurer Codex Cloud et travailler sur iPhone](docs/IPHONE-CLOUD.md)
- [Récupérer les changements et tester sur PC](docs/TESTS-PC.md)
- [Références historiques](docs/references/)

## Vérifications disponibles sans matériel

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-cloud.txt
.venv/bin/python scripts/check_project.py
```

Ces vérifications analysent les fichiers YAML, les templates Jinja2 et les XML.
Elles ne lancent aucun playbook et ne valident pas le fonctionnement sous Windows.

## Organisation

`playbooks/` contient les automatisations Ansible et `playbooks/templates/` les
modèles de réponses Windows. `inventory/` contient un exemple de lab et un modèle
de secrets vide. Les références sont importées des travaux antérieurs ; leurs
statuts et leurs commandes doivent être vérifiés avant un nouvel essai.

Les mots de passe, les images système, les journaux bruts, les inventaires internes
et le fond d'écran d'entreprise restent locaux. Pour activer ce dernier sur le PC,
placer `wallpaper-entreprise.jpg` dans `playbooks/files/` et définir
`win_custom_wallpaper_enabled: true` dans les variables locales.
