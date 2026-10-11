# BC250-Unsloth-Vulkan

Correctif reproductible pour **Unsloth Studio sur AMD BC-250 / SkillFishOS** utilisant stable-diffusion.cpp accéléré avec Vulkan/RADV.

## Configuration validée

- SkillFishOS 26.06.5, kernel 7.2.5-skillfishos, RADV GFX1013, VRAM déclarée 8 Gio.
- Unsloth Studio Python 3.13 installé dans `/home/bc/.unsloth/studio/unsloth_studio`.
- `sd-cli` et `sd-server` Vulkan compilés dans `/home/bc/ai-build/stable-diffusion.cpp/build-vulkan/bin`.
- Qwen-Image-2.1-Uncensored-GGUF Q8_0, encodeur Qwen3-VL-8B GGUF, VAE Qwen-Image-2.1.
- Génération web vérifiée : 512×512, 4 étapes, 1 image, HTTP 200, ~33 secondes.

## Installation

Depuis la BC-250 avec l'utilisateur `bc` :

```bash
git clone https://github.com/pigeonfou/BC250-Unsloth-Vulkan.git
cd BC250-Unsloth-Vulkan
bash scripts/install.sh
```

Les exécutables Vulkan doivent déjà avoir été compilés ; voir `docs/INSTALLATION.md`. L'installateur applique deux modifications Python contrôlées, sauvegarde les originaux et configure un *drop-in* systemd. Un timer vérifie toutes les 15 minutes si une mise à jour d'Unsloth a remplacé les correctifs.

**Sécurité :** une version modifiée d'Unsloth qui ne correspond pas aux motifs reconnus n'est jamais patchée automatiquement. Le timer ne met pas à jour Unsloth lui-même et ne peut pas garantir la compatibilité avec une mise à jour majeure. Il n'interrompt pas volontairement un modèle résident.

## Vérification

```bash
systemctl is-active skillfish-unsloth.service
systemctl status bc250-unsloth-watch.timer --no-pager
pgrep -af '/sd-server'
journalctl -u skillfish-unsloth.service -n 70 --no-pager
```

Rechercher `device=vulkan mode=server` et `--auto-fit on --max-vram 6`. Le budget GPU n'est pas une limite de RAM générale. Ne pas dépasser les réglages testés sans contrôle mémoire.

## Documentation

- [Installation](docs/INSTALLATION.md)
- [Optimisation progressive](docs/TUNING.md)
- [Retour arrière](docs/ROLLBACK.md)

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Les tests vérifient les transformations de texte et les refus sûrs ; ils ne remplacent pas un test matériel.

**Ne pas publier** les modèles, secrets, sauvegardes locales ni journaux privés dans ce dépôt.
