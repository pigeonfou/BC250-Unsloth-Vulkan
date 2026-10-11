# Installation et maintenance sur BC-250

## Prérequis

Configuration de référence : AMD BC-250 (RADV GFX1013), SkillFishOS 26.06.5, Unsloth Studio Python 3.13, utilisateur Linux `bc`. Installer les dépendances seulement si les exécutables Vulkan ne sont pas déjà compilés.

```bash
sudo apt update
sudo apt install -y git cmake ninja-build build-essential libvulkan-dev glslc spirv-headers
mkdir -p ~/ai-build
cd ~/ai-build
git clone --recursive https://github.com/leejet/stable-diffusion.cpp.git
cd stable-diffusion.cpp
cmake -S . -B build-vulkan -G Ninja -DCMAKE_BUILD_TYPE=Release -DSD_VULKAN=ON -DSD_WEBP=OFF -DSD_WEBM=OFF
cmake --build build-vulkan -j 2
./build-vulkan/bin/sd-cli --list-devices
./build-vulkan/bin/sd-server --list-devices
```

Les deux commandes doivent afficher `Vulkan0 AMD BC-250`.

## Déployer les correctifs

```bash
cd ~
git clone https://github.com/pigeonfou/BC250-Unsloth-Vulkan.git
cd BC250-Unsloth-Vulkan
python3 -m unittest discover -s tests -v
bash scripts/install.sh
```

L'installateur vérifie les exécutables, reconnaît les anciens correctifs manuels, sauvegarde les fichiers Python avant modification et configure `SD_CLI_PATH`, `SD_SERVER_PATH` et `UNSLOTH_BC250_VULKAN=1`. Il ajoute `--auto-fit on --max-vram 6` à `sd-server` uniquement sur cette configuration.

## Contrôle après installation

```bash
systemctl status skillfish-unsloth.service --no-pager
systemctl status bc250-unsloth-watch.timer --no-pager
journalctl -u skillfish-unsloth.service -n 80 --no-pager
```

Recharger le modèle dans Unsloth puis vérifier :

```bash
pgrep -af '/sd-server'
```

Chercher `device=vulkan mode=server` dans les journaux et `--auto-fit on --max-vram 6` dans le processus. Premier test : 512×512, 4 étapes, 1 image, live preview désactivé.

## Mises à jour

Le timer effectue une vérification toutes les 15 minutes. Il ne télécharge aucune mise à jour. Il reporte l'opération si un modèle est résident, et refuse les versions dont la structure diffère. Après mise à jour majeure, examiner le journal :

```bash
journalctl -u bc250-unsloth-watch.service -n 80 --no-pager
```

Une réparation à distance n'est pas garantie tant qu'elle n'a pas été exécutée sur la machine.
