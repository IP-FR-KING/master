# Premier essai du master Windows 11 sur VM locale

Version candidate : vérifiée statiquement dans le cloud, à valider sur Windows.
Base retenue en attendant confirmation : Windows 11 Pro x64 français, AZERTY,
Firefox, 7-Zip, Notepad++, mises à jour et fond d'écran Windows par défaut.

## 1. Préparer la VM

Utiliser une VM de test dédiée : UEFI, TPM 2.0, Secure Boot, 2 processeurs,
8 Go de RAM conseillés et disque virtuel neuf de 80 Go minimum.
Ne pas attacher de disque physique ni de SSD contenant des données.
Installer Windows 11 Pro avec une ISO officielle et conserver Defender actif.
Pour ce premier essai, faire l'installation manuellement : le modèle historique
`autounattend.xml.j2` efface le disque 0 et configure le réseau du lab
192.168.100.0/24 ; ne pas l'attacher à une VM sur un autre réseau.

Créer un compte administrateur local dédié à Ansible. Dans la VM de lab, avec
PowerShell administrateur, vérifier que le réseau de test est de profil Privé,
puis configurer WinRM (remplacer l'adresse demandée par celle du PC contrôleur) :

```powershell
$Controller = Read-Host 'Adresse IP du contrôleur Ansible local'
Enable-PSRemoting -Force
Set-NetFirewallRule -Name 'WINRM-HTTP-In-TCP*' -RemoteAddress $Controller
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $false
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $false
New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name LocalAccountTokenFilterPolicy -PropertyType DWord -Value 1 -Force
```

L'inventaire utilise NTLM sur HTTP avec chiffrement des messages ; conserver
`AllowUnencrypted=false`. L'accès administrateur distant par compte local est
réservé à cette VM de test et le pare-feu limite l'accès au contrôleur.
Ne pas exposer le port 5985 sur Internet. Pour la capture destinée à un usage
hors lab, retirer l'accès de préparation et son compte sur une copie avant la
généralisation finale, après validation du premier essai.
Prendre un snapshot `installation-propre` avant les personnalisations.

## 2. Préparer le contrôleur local

Depuis la copie du dépôt sur le PC Linux :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-cloud.txt ansible pywinrm
.venv/bin/ansible-galaxy collection install -r collections/requirements.yml
.venv/bin/python scripts/check_project.py
.venv/bin/python -m unittest discover -s tests -v
mkdir -p inventory/local
cp -n inventory/group_vars/all/vault.yml.example inventory/group_vars/all/vault.yml
```

Renseigner localement `vault_winrm_user`, `vault_winrm_password` et
`vault_win_local_password`, puis chiffrer le fichier :

```bash
.venv/bin/ansible-vault encrypt inventory/group_vars/all/vault.yml
```

Le mot de passe du compte post-Sysprep doit avoir au moins 12 caractères et
respecter la stratégie de Windows. Ne pas laisser `CHANGE_ME`.
Créer `inventory/local/vars.yml` (ignoré par Git) avec l'IP réelle de la VM :

```yaml
win_reference_ip: 192.168.100.50 # à remplacer par l'IP de votre VM
win_local_admin: MasterAdmin
win_custom_wallpaper_enabled: false
```

`MasterAdmin` est un compte dédié créé après Sysprep, différent du compte intégré
Administrateur. Ne pas mettre de secret dans ce fichier de variables.

## 3. Personnaliser et vérifier

Les commandes suivantes s'exécutent uniquement sur le PC et ciblent `win11-ref`.

```bash
.venv/bin/ansible win11-ref -i inventory/hosts.yml -m ansible.windows.win_ping -e @inventory/local/vars.yml --ask-vault-pass
.venv/bin/ansible-playbook -i inventory/hosts.yml playbooks/customize-win11-reference.yml --limit win11-ref -e @inventory/local/vars.yml -e master_prepare_confirm=true --ask-vault-pass
```

Vérifier dans la VM : Windows Update sans redémarrage en attente, lancement des
trois applications, raccourcis sur le bureau public et Defender actif.
Relancer la personnalisation si d'autres mises à jour restent nécessaires.
Noter la version avec `winver`. Prendre un snapshot `avant-sysprep`.

## 4. Généraliser puis tester une copie

```bash
.venv/bin/ansible-playbook -i inventory/hosts.yml playbooks/sysprep-win11.yml --limit win11-ref -e @inventory/local/vars.yml -e sysprep_confirm=true --ask-vault-pass
```

Le playbook conserve les DLL, les ActionFiles et les journaux Windows d'origine.
Il s'arrête avant Sysprep si un redémarrage ou un échec antérieur est détecté.
La transmission de la commande asynchrone ne prouve pas le succès : constater
l'arrêt de la VM. Si elle reste allumée ou échoue, conserver et examiner
`C:\Windows\System32\Sysprep\Panther\setupact.log` et `setuperr.log`.
Ne pas effacer les journaux ni appliquer les contournements historiques.

Après l'arrêt, garder la référence éteinte. Faire un clone à froid avec disque,
MAC et état UEFI/TPM propres via l'hyperviseur, puis démarrer uniquement ce clone.
Le premier test est l'OOBE sur cette copie ; FOG et PXE viennent ensuite.
Vérifier le nouveau nom de machine, le compte `MasterAdmin`, français/AZERTY,
les trois applications et un redémarrage normal. Vérifier que le compte Ansible
hérité est supprimé ou désactivé avant tout usage hors lab ; cette candidate
ne réalise pas automatiquement cette suppression.

## 5. Retour de test

Fournir : commit testé, hyperviseur, édition/build Windows, étape, résultat
attendu/observé et extrait d'erreur expurgé. Les fichiers de réponses Windows
contiennent les mots de passe en clair : ils restent locaux et doivent être
retirés des supports de test après usage. Aucun journal brut ni image dans Git.
