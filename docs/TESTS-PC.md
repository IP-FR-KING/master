# Récupérer et tester sur PC

## Récupérer les changements publiés

La copie préparée pour ce dépôt est `/home/waladi/master-win11`. Le dossier
historique `/home/waladi/srv-fog` reste indépendant : ne pas le remplacer.

```bash
cd /home/waladi/master-win11
git status --short
```

Si des modifications locales apparaissent, les enregistrer avant la récupération.
Lorsque le dossier est propre :

```bash
git pull --ff-only origin main
```

Pour tester une branche publiée depuis le téléphone :

```bash
git fetch origin
git switch NOM_DE_BRANCHE
```

Si la branche existe uniquement sur GitHub, `git switch` peut créer son suivi
automatiquement. En cas de conflit, conserver les changements et résoudre le
conflit ; ne pas utiliser `reset --hard`.

Sur un autre PC, cloner dans un nouveau dossier :

```bash
git clone https://github.com/IP-FR-KING/master.git master-win11
cd master-win11
```

## Préparer les outils et les secrets locaux

Installer Ansible et les collections si les essais les utilisent :

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

Copier le modèle de coffre-fort uniquement s'il n'existe pas déjà :

```bash
cp -n inventory/group_vars/all/vault.yml.example inventory/group_vars/all/vault.yml
```

Renseigner les valeurs avec un éditeur local, puis chiffrer :

```bash
ansible-vault encrypt inventory/group_vars/all/vault.yml
```

Le coffre-fort, les fichiers XML rendus et les inventaires internes sont exclus
de Git. Pour un poste physique, utiliser un inventaire dans `inventory/local/`
avec ses variables locales ; ne pas remplacer l'inventaire de lab par les données
internes dans un commit.

## Tester le changement précis

Commencer par les vérifications statiques décrites dans le README. Pour un
playbook, `--syntax-check` vérifie sa structure sans exécuter les tâches :

```bash
ansible-playbook -i inventory/hosts.yml playbooks/sysprep-win11.yml --syntax-check --ask-vault-pass
```

Effectuer ensuite uniquement l'essai correspondant au changement proposé, sur
une VM ou un poste de test identifié et sauvegardé. `--check` n'est pas une garantie
d'absence d'effet pour tous les playbooks historiques. Ne pas lancer
`reset-lab-vms.yml` ou Sysprep pour une simple vérification.

Après Sysprep avec arrêt, capturer avant tout nouveau démarrage sous Windows.
Les références importées ne remplacent pas une procédure adaptée à l'état actuel.

## Renvoyer le résultat depuis l'iPhone

Dans la tâche cloud, fournir : commit testé, version Windows, VM ou modèle du poste,
étape réalisée, résultat attendu, résultat observé et extrait d'erreur expurgé.
Demander la mise à jour de `docs/CONTEXTE.md` avec ces observations.
