# Optimisation des générations BC-250

Référence validée : Qwen-Image-2.1-Uncensored Q8_0, 512×512, 4 étapes, 1 image, environ 33 secondes côté API Unsloth, seed `2395674787`. Les images avec seulement 4 étapes restent très bruitées.

## Protocole

Conserver modèle, prompt et seed identiques. Tester **un seul paramètre à la fois** :
1. 512×512, 4 étapes : référence ;
2. 512×512, 8 étapes ;
3. 512×512, 12 étapes ;
4. 512×512, 20 étapes si stable ;
5. 768×768, 4 étapes seulement après validation mémoire.

Conserver Guidance=1 au début, batch=1, runs=1 et preview désactivé. Ne pas supposer que 1536×1536 fonctionnera. Augmenter le nombre de pas augmente le temps et ne garantit pas une meilleure qualité avec tous les schedulers.

Exemple de prompt constant : `A small red house in a green meadow, daylight`.

## Surveillance

```bash
watch -n 2 'free -h; cat /sys/class/drm/card0/device/mem_info_vram_used'
sudo journalctl -k --since '10 minutes ago' --no-pager | grep -Ei 'out of memory|oom|killed process'
pgrep -af '/sd-server'
```

Si OOM, revenir au dernier profil stable. Le paramètre `--max-vram 6` limite le placement géré sur le GPU et **n'est pas une limite de RAM système**. Éviter les exécutions simultanées de plusieurs modèles.

Comparer la netteté, le bruit, la conformité au prompt, la durée et les pics mémoire. Une quantification plus petite ou des stratégies de placement sur disque peuvent être étudiées séparément mais n'ont pas été validées dans cette configuration.
