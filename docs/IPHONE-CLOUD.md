# Continuer depuis l'iPhone, même PC éteint

## Configuration initiale

Créer l'environnement depuis ChatGPT sur le web ou l'application de bureau :

1. Choisir **Work in > Cloud > Select environment > Create environment**,
   ou **Settings > Codex Cloud > Environments > Create environment**.
2. Choisir le dépôt GitHub **IP-FR-KING/master**.
3. Demander la configuration suivante :

   > Prépare un environnement nommé Master Win11 pour ce dépôt. Lis AGENTS.md.
   > Installe Python 3, PyYAML et Jinja2 avec requirements-cloud.txt, puis lance
   > python3 scripts/check_project.py. Je réalise les tests Windows et FOG sur mon
   > PC : aucun déploiement, aucune connexion au lab, aucun secret nécessaire.

4. Vérifier le rapport puis sélectionner **Publish**.
5. Attendre la confirmation **Environment published**.

La configuration n'est pas créée automatiquement par le dépôt. Sa disponibilité
dépend du compte et des paramètres de l'espace ChatGPT.

## Sur l'iPhone

Dans l'application ChatGPT, ouvrir **Codex**, choisir **Cloud** puis l'environnement
**Master Win11**. Rouvrir la même tâche pour poursuivre un travail existant.

Exemple de première demande :

> Reprends le projet Master Win11. Lis AGENTS.md et docs/CONTEXTE.md.
> Prépare les changements demandés et une procédure de test sur PC.
> Je ferai les essais matériels moi-même. Enregistre les modifications dans GitHub.

Le mode Cloud continue sans le PC. Une connexion Remote dépend d'un ordinateur
allumé. Cette conversation locale ne devient pas automatiquement une tâche cloud :
le contexte nécessaire se trouve dans les fichiers du dépôt.

## Garder le travail d'un appareil à l'autre

Enregistrer les changements dans un commit et les publier sur GitHub avant de
changer d'environnement. Une nouvelle tâche cloud possède son propre espace.
Récupérer la branche ou le commit sur le PC avec la procédure `TESTS-PC.md`.

[Documentation officielle des environnements cloud](https://learn.chatgpt.com/docs/environments/cloud-environments)
