# Instructions du projet Master Windows 11

Répondre en français, de manière directe et concise.

## Objectif et mode de travail

L'utilisateur veut développer le master depuis l'application ChatGPT sur iPhone,
y compris lorsque son PC est éteint. Le dépôt est la mémoire partagée du projet.
Lire `docs/CONTEXTE.md` au début d'une tâche et les références pertinentes ensuite.

Le cloud sert à lire et modifier les scripts, modèles et procédures. L'utilisateur
réalise les essais sur son PC. Ne pas tenter de contacter le lab, FOG ou un poste
Windows depuis le cloud. Ne pas exécuter les playbooks de déploiement, Sysprep ou
de réinitialisation des VM dans le cloud, même avec `--check`.

## Vérification et suivi

- Vérifier les changements techniques avec `python3 scripts/check_project.py`
  après installation de `requirements-cloud.txt` si nécessaire.
- Distinguer vérifications statiques et essais Windows réellement effectués.
- Fournir une procédure de test PC adaptée au changement.
- Mettre à jour `docs/CONTEXTE.md` après une évolution significative ou un retour
  de test de l'utilisateur. Ne jamais déduire un succès matériel d'un contrôle YAML.
- Enregistrer les changements dans Git et préciser le commit ou la branche à
  récupérer. Ne pas prétendre qu'une modification non publiée est synchronisée.
- Préserver les changements existants et éviter `reset --hard` et les pushes forcés.

## Données locales et références

Aucun secret, coffre-fort réel, fichier de réponse Windows rendu avec de vrais
identifiants, journal brut, image disque ou inventaire interne dans Git.
Les valeurs de lab sont des exemples. Le dépôt peut être public.

Les documents de `docs/references/` sont historiques. Ils peuvent contenir des
contournements Sysprep ou des commandes risquées non validés. Ne pas les appliquer
automatiquement. Vérifier leur pertinence avec la version Windows et les journaux
fournis avant de proposer une modification système. Ne pas lancer de remise à
zéro de VM ou de partitionnement comme simple test.

Les essais Windows, FOG, libvirt et SSD sont à réaliser par l'utilisateur sur PC.
