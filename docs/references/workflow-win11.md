> Référence historique importée ; état du matériel non vérifié le 7 octobre 2026. Les identifiants ont été remplacés.

# Workflow : Déploiement Windows 11 via FOG PXE

## Nommage uniforme

| VM | IP | Rôle |
|----|-----|------|
| `srv-fog` | 192.168.100.10 (statique) | Serveur FOG |
| `win11-ref` | 192.168.100.50 (statique, hors DHCP) | Image source Windows 11 |
| `win11-pxe` | DHCP 100-200 | Client test déploiement |

---

## Statut

| Phase | Description | Statut |
|-------|-------------|--------|
| 0 | Reset lab VMs (`reset-lab-vms.yml`) | À faire |
| 1 | Installation Windows auto sur win11-ref (autounattend.xml) | À faire |
| 2 | Personnalisation image (`customize-win11-reference.yml`) | À faire |
| 3 | Sysprep + unattend.xml (`sysprep-win11.yml`) | À faire |
| 4 | Capture FOG | À faire |
| 5 | Déploiement win11-pxe + validation OOBE automatique | À faire |

---

## Prérequis vault.yml

Avant tout, vérifier que ces variables existent dans vault.yml :

```bash
ansible-vault edit inventory/group_vars/all/vault.yml --ask-vault-pass
```

```yaml
# Doit contenir au minimum :
vault_fog_user: "CHANGE_ME"
vault_fog_password: "CHANGE_ME"
vault_fog_mysql_password: "CHANGE_ME"
vault_winrm_user: "CHANGE_ME"
vault_winrm_password: "CHANGE_ME"
vault_win_local_password: "CHANGE_ME"
```

---

## Phase 0 — Reset et recréation des VMs lab

> ⚠️ Supprime `win11`, `win11-client`, `client-pxe`. Anciens disques conservés en `.qcow2.old`.

```bash
# reset-lab-vms.yml tourne sur localhost — pas de --check disponible (actions destructives)
ansible-playbook playbooks/reset-lab-vms.yml
```

Ce playbook :
- Arrête et supprime les VMs : `win11`, `win11-client`, `client-pxe`
- Archive les disques existants (`*.qcow2` → `*.qcow2.old`)
- Crée des disques vierges (60 Go) pour `win11-ref` et `win11-pxe`
- Génère l'ISO `win11-autounattend.iso` depuis le template Jinja2
- Définit `win11-ref` (boot cdrom → Windows ISO + autounattend)
- Définit `win11-pxe` (boot network → PXE FOG)

---

## Phase 1 — Installation Windows automatique sur win11-ref

```bash
# Démarrer la VM — Windows s'installe automatiquement (~20-30 min)
virsh start win11-ref
virt-viewer win11-ref   # surveiller l'installation
```

L'autounattend.xml gère :
- Bypass TPM / Secure Boot (lab VM sans TPM)
- Partitionnement UEFI (EFI 300 Mo + MSR 128 Mo + Windows)
- Installation Windows 11 Pro (clé générique KMS lab)
- Locale française, AZERTY, fuseau horaire Romance Standard Time
- Compte `vault_winrm_user` / `vault_winrm_password` créé automatiquement
- IP statique `192.168.100.50` configurée au premier démarrage
- WinRM HTTP activé sur port 5985

La VM redémarre plusieurs fois pendant l'installation. Elle est prête quand le bureau Windows apparaît sans aucune interaction.

### Vérifier la connectivité WinRM

```bash
# Depuis la machine locale, après l'installation complète
ansible win11-ref -i inventory/hosts.yml -m ansible.windows.win_ping --ask-vault-pass
```

Réponse attendue : `"ping": "pong"`

---

## Phase 2 — Personnalisation (Ansible via WinRM)

```bash
# Toujours --check avant d'appliquer
ansible-playbook -i inventory/hosts.yml playbooks/customize-win11-reference.yml \
  --ask-vault-pass --check

ansible-playbook -i inventory/hosts.yml playbooks/customize-win11-reference.yml \
  --ask-vault-pass
```

Résultat :
- Mises à jour Windows installées (relancer si `found_update_count > 0`)
- Firefox, 7-Zip, Notepad++ installés via Chocolatey
- Fond d'écran `C:\Windows\Web\Wallpaper\Custom\wallpaper-entreprise.jpg`
- Raccourcis sur le bureau public (`C:\Users\Public\Desktop\`)
- Teams Chat widget, Widgets désactivés (registre)
- Xbox, Clipchamp supprimés (provisioned apps)
- Fichiers temporaires et corbeille vidés

---

## Phase 3 — Sysprep avec unattend.xml (bypass OOBE automatique)

> ⚠️ Point de non-retour. La VM s'éteint après Sysprep. Ne pas la redémarrer sous Windows.

```bash
# Pas de --check (Sysprep est fire-and-forget via WinRM async)
ansible-playbook -i inventory/hosts.yml playbooks/sysprep-win11.yml --ask-vault-pass
```

Le playbook :
1. Applique le fix `spopk.dll` si nécessaire (takeown + icacls + suppression)
2. Copie `unattend.xml` (rendu depuis template) dans `C:\Windows\Panther\`
3. Lance `sysprep.exe /generalize /oobe /shutdown /unattend:...`

Surveiller l'arrêt :
```bash
watch -n5 "virsh domstate win11-ref"
# Attendre : shut off
```

Si Sysprep échoue, consulter les logs :
```bash
ansible win11-ref -i inventory/hosts.yml -m ansible.windows.win_shell \
  -a "Get-Content C:\Windows\Panther\setuperr.log -Tail 30" --ask-vault-pass
```

---

## Phase 4 — Capture FOG

### 1. Basculer win11-ref sur boot PXE

```bash
virsh edit win11-ref
```

Dans la section `<os>`, mettre `network` avant `hd` :
```xml
<boot dev='network'/>
<boot dev='hd'/>
```

### 2. Programmer la capture dans FOG

1. Ouvrir http://192.168.100.10/fog/management/
2. **Host Management** → `win11-ref` (enregistrée au 1er boot PXE si pas encore fait)
3. Associer l'image `Windows11-Base` au host
4. **Basic Tasks** → **Capture** → confirmer

### 3. Démarrer la VM et capturer

```bash
virsh start win11-ref
# Boot PXE → capture automatique (15-30 min selon la taille)
```

Surveiller :
```bash
ssh fogadmin@192.168.100.10 "watch -n15 'ls -lh /images/Windows11-Base/'"
```

---

## Phase 5 — Déploiement et validation

### 1. Déployer sur win11-pxe

1. FOG web → **Host Management** → `win11-pxe`
2. Associer l'image `Windows11-Base`
3. **Basic Tasks** → **Deploy** → confirmer

```bash
virsh start win11-pxe
virt-viewer win11-pxe
```

### 2. Critères de validation

- [ ] Windows 11 démarre directement sur le bureau (0 interaction OOBE)
- [ ] Connexion automatique en tant que `Administrateur` (ou bureau direct)
- [ ] Fond d'écran personnalisé visible
- [ ] Raccourcis Firefox, 7-Zip, Notepad++ présents sur le bureau
- [ ] Heure et locale françaises correctes
- [ ] Compte `Administrateur` fonctionnel avec mot de passe `vault_win_local_password`

---

## Passage en production

1. Mettre à jour `inventory/group_vars/all/vars.yml` :
   - `fog_server_ip: FOG_SERVER_IP`
   - `win_reference_ip: <IP du poste physique de référence>`
2. Rejouer `install-fog.yml` + `configure-fog.yml` + `configure-fog-win11.yml`
3. Recapturer depuis un poste physique de référence

---

## Référence rapide

```bash
# État des VMs
virsh list --all

# Démarrer / arrêter
virsh start win11-ref
virsh start win11-pxe
virsh shutdown win11-ref        # arrêt propre
virsh destroy win11-ref         # ⚠️ arrêt forcé

# Console graphique
virt-viewer win11-ref
virt-viewer win11-pxe

# Vérifier boot order
virsh dumpxml win11-ref | grep -A5 '<boot'

# Test WinRM Ansible
ansible win11-ref -i inventory/hosts.yml -m ansible.windows.win_ping --ask-vault-pass

# Nettoyage anciens disques (si plus nécessaires)
sudo rm /var/lib/libvirt/images/*.qcow2.old
```
