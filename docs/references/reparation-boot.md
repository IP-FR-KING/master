> Référence historique : commandes conservées pour analyse, à vérifier avant exécution. Aucun nouveau test matériel réalisé lors de cet import.

# Guide de réparation du boot Windows 11 (master sur SSD externe)

**Date** : 2026-08-31
**Disque** : SSD externe USB ; identifier le disque et ses volumes sur le poste de test.
**Problème** : après `sysprep /generalize`, le SSD ne boote plus — « Windows n'a pas pu terminer la configuration du système ».

---

## Diagnostic (root cause)

Le BCD a été patché à la main mais il reste **incohérent** :
- **sda1 (EFI SYSTEM)** : l'élément `11000001` (device) de l'OS loader `{d578d243-...}` est resté **abstrait** (`08`) au lieu de pointer vers le GUID disque+partition GPT. Le Boot Manager a un `24000001` corrompu (valeur chaîne ⇒ GUID vide) au lieu d'un `default`/`displayorder` valides.
- **sda5 (SR_AED)** : le Boot Manager pointe vers « Windows Setup », pas vers l'OS.

Le `osdevice` (`12000002`) est correct (`\windows\system32\winload.efi`) ; l'unattend.xml est valide ; Winre.wim présente.

**Méthode recommandée** : `bcdboot` (outil officiel Microsoft) reconstruit un BCD propre et cohérent, sans patching manuel.

---

## Prérequis

- Insérer une **clé USB d'installation Windows 11** (ou la partition WinRE du SSD).
- Booter dessus, choisir la langue puis **« Réparer l'ordinateur »** → Dépannage → **Invite de commandes** (⚠ pas « Réinitialiser »).

## Procédure

### 1. Identifier les volumes
```cmd
diskpart
list volume
```
Repérer dans la sortie :
- Le volume **EFI SYSTEM** (260 M, FAT32) → noter son numéro
- Le volume **Windows** (443 G, NTFS) → noter son numéro

### 2. Assigner des lettres
```cmd
select volume 3
assign letter=C
select volume 1
assign letter=S
exit
```
> ⚠ Adapte les numéros (`3` et `1` exemple). `C:` = Windows, `S:` = EFI.

### 3. Reconstruire le BCD (la commande clé)
```cmd
bcdboot C:\Windows /s S: /f ALL
```
Cette commande régénère **automatiquement** sur `S:` :
- `bootmgfw.efi` + `EFI\Microsoft\Boot\BCD`
- l'entrée OS loader **avec les bons GUID GPT** (`11000001` correct)
- le Boot Manager avec `default` + `displayorder` valides
- `bootx64.efi` (firmware)

### 4. Vérifier
```cmd
bcdedit /store S:\EFI\Microsoft\Boot\BCD /enum
```
Tu dois voir un loader `Windows 11` avec un `device`/`osdevice` non vides et l'entrée par défaut correcte. Pour tester le specialize (ne pas refaire OOBE) :
```cmd
bcdedit /store S:\EFI\Microsoft\Boot\BCD /set {default} nosafeboot on
```

### 5. Redémarrer
- Fermer, retirer la clé, booter sur le **SSD externe USB** (menu boot UEFI, ex. F9 sur HP).
- Windows doit passer le specialize/OOBE (auto-login admin 5 fois via l'unattend.xml).

---

## Si le boot « ne le voit pas » / NVRAM

- L'export NVRAM EFI avait échoué (`BiUpdateEfiEntry c000000d`, enregistrement impossible).
- **F9 au boot** puis sélectionner le SSD à la main, ou activer « Boot from USB » dans le BIOS.
- Une fois démarré, réenregistrer le boot : (dans Windows) `bcdedit /set {bootmgr} path \EFI\Microsoft\Boot\bootmgfw.efi` puis `bcdboot C:\Windows /d`.

---

## GUID GPT de référence (SSD `/dev/sda`)

| Partition | GUID GPT (PARTUUID) |
|-----------|---------------------|
| sda1 EFI SYSTEM | 169f198c-18e8-4c29-b8b4-fe3d193fe4d3 |
| sda3 Windows | 2a90e52e-fa66-4644-9f34-0d705a2513e9 |
| sda5 SR_AED | 3c856c31-9bcf-4ec5-a501-b57e3823ca6f |

> Ces GUID sont utiles si une correction manuelle du BCD s'avère nécessaire en dernier recours (via hivex), mais `bcdboot` rend ce cas inutile dans le flux normal.

---

## Utilisé aussi pour le déploiement FOG
Une fois le master bootable, il pourra être **capturé via FOG** (image `Raw`/DD) puis déployé sur les postes cibles. Voir `plan-deploiement-fog.md` / `preparation_master.txt`.
