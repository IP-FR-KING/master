"""Préparer une VM libvirt locale ; aucune exécution sans --create."""
import argparse
from pathlib import Path
import shlex
import shutil
import subprocess


def command(iso, disk, name, network):
    return [
        'virt-install', '--connect', 'qemu:///system', '--name', name,
        '--memory', '8192', '--vcpus', '2', '--os-variant', 'win11',
        '--boot', 'uefi,firmware.feature0.name=secure-boot,firmware.feature0.enabled=yes,firmware.feature1.name=enrolled-keys,firmware.feature1.enabled=yes',
        '--tpm', 'backend.type=emulator,backend.version=2.0,model=tpm-crb',
        '--disk', f'path={disk},size=80,format=qcow2,bus=sata',
        '--network', f'network={network},model=e1000e',
        '--cdrom', str(iso), '--graphics', 'spice', '--noautoconsole',
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', required=True, type=Path)
    parser.add_argument('--name', default='win11-ref')
    parser.add_argument('--disk', type=Path, default=Path('/var/lib/libvirt/images/win11-ref.qcow2'))
    parser.add_argument('--network', default='default')
    parser.add_argument('--create', action='store_true', help='Créer et démarrer la VM sur le PC local')
    args = parser.parse_args()
    iso = args.iso.expanduser().resolve()
    disk = args.disk.expanduser().resolve()
    if not iso.is_file():
        parser.error('ISO absente : fournir le chemin local de l’ISO officielle Windows 11 x64.')
    if disk.exists():
        parser.error('Le disque existe déjà : aucun disque existant ne sera réutilisé ou écrasé.')
    if ',' in str(disk) or ',' in args.network:
        parser.error('Le chemin disque et le nom réseau ne doivent pas contenir de virgule.')
    cmd = command(iso, disk, args.name, args.network)
    print(shlex.join(cmd), flush=True)
    if not args.create:
        print('Aperçu uniquement. Sur le PC local, ajouter --create pour lancer l’installation.')
        return 0
    if not all(shutil.which(tool) for tool in ('virsh', 'virt-install')):
        parser.error('Installer libvirt, virt-install, OVMF et swtpm sur le PC local.')
    names = subprocess.run(['virsh', '-c', 'qemu:///system', 'list', '--all', '--name'],
                           check=True, capture_output=True, text=True).stdout.splitlines()
    if args.name in names:
        parser.error('Une VM porte déjà ce nom : choisir un autre nom et un nouveau disque.')
    subprocess.run(['virsh', '-c', 'qemu:///system', 'net-info', args.network], check=True)
    if not disk.parent.is_dir():
        parser.error('Le répertoire du disque doit exister et être accessible à libvirt.')
    # virt-install contrôle le réseau actif et les capacités UEFI/TPM de l’hôte.
    # Une erreur reste visible ; aucune remise à zéro ou suppression automatique.
    return subprocess.run(cmd, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
