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

## Candidate pour le premier essai VM

Préparation demandée pour un test local ultérieur. Base provisoire : Windows 11
Pro x64 français/AZERTY, mises à jour, Firefox, 7-Zip et Notepad++.
Hyperviseur et build Windows à confirmer par l'utilisateur.

- Procédure : `docs/PREMIER-ESSAI-VM.md`, installation manuelle puis
  personnalisation, snapshot, Sysprep et test OOBE sur un clone à froid.
- Contournements historiques retirés du playbook Sysprep : aucune suppression de
  spopk.dll, aucun remplacement d'ActionFiles, aucun effacement des journaux ou
  du marqueur d'échec Sysprep.
- Confirmation explicite requise pour personnalisation et généralisation ;
  Sysprep vérifie les redémarrages en attente et les échecs antérieurs.
- Compte post-Sysprep dédié : MasterAdmin ; secrets définis seulement sur le PC.
- Rendu XML des identifiants échappé ; chemin Chocolatey corrigé.
- Inventaire WinRM passé à NTLM avec chiffrement des messages ; procédure
  locale de préparation et limitation du pare-feu au contrôleur.
- Validation cloud : 20 fichiers YAML/Jinja2/XML et 2 tests de régression réussis.
  Aucun playbook exécuté, aucun test Windows/FOG effectué, aucune image créée.

Prochaine étape : exécuter le premier essai sur une VM dédiée et rapporter le
commit, l'hyperviseur, le build Windows et les résultats. Le modèle d'installation
automatique reste historique (réseau de lab, effacement disque 0) et n'est pas
le chemin recommandé pour ce premier essai.
