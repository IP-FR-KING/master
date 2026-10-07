# Contexte partagé — Master Windows 11

## Décisions confirmées le 7 octobre 2026

- OS cible : Windows 11.
- Travailler sur les scripts et procédures depuis ChatGPT sur iPhone, PC éteint.
- Conserver le projet dans GitHub et l'utiliser avec Codex Cloud.
- L'utilisateur effectue les tests Windows, FOG, VM et SSD sur son ordinateur.
- Source cloud : `https://github.com/IP-FR-KING/master`.
- Copie de travail PC préparée dans `/home/waladi/master-win11`.
- Les sources locales historiques de `srv-fog` sont conservées séparément.

## Sources importées

- Automatisations Ansible de `srv-fog`, avec les modifications locales présentes
  au moment de l'import, sans reprendre son historique Git.
- Modèles `autounattend.xml.j2` pour l'installation et `unattend.xml.j2` pour OOBE.
- Références historiques de préparation du master et de réparation du démarrage.
- Inventaire de lab sans poste physique interne ; secrets remplacés par un exemple.
- Fond d'écran interne exclu et personnalisation du wallpaper optionnelle.

## État matériel

Non vérifié lors de cet import. Les documents précédents décrivent un lab FOG,
des essais Sysprep et un problème de configuration/démarrage sur SSD externe.
Ce sont des observations historiques, pas une preuve de l'état actuel.

## Prochain travail

1. Configurer et publier l'environnement Codex Cloud avec ce dépôt.
2. Reprendre la préparation du master selon la priorité donnée par l'utilisateur.
3. Avant un essai, relire la procédure concernée et les éventuels journaux récents.
4. Reporter les résultats PC dans ce fichier ou dans une note de test dédiée.

## Validation de cet import

Vérifications statiques uniquement : parsing YAML, templates Jinja2 rendus avec
des valeurs fictives et parsing XML. Aucun playbook ni test Windows exécuté.
