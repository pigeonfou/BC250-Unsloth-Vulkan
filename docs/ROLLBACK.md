# Retour arrière contrôlé

Arrêter toute génération et décharger le modèle. Désactiver d'abord la surveillance pour éviter la réapplication du correctif :

```bash
sudo systemctl disable --now bc250-unsloth-watch.timer
sudo systemctl stop bc250-unsloth-watch.service 2>/dev/null || true
```

Afficher les sauvegardes avant de choisir celle correspondant à la version d'Unsloth à restaurer :

```bash
PKG="$HOME/.unsloth/studio/unsloth_studio/lib/python3.13/site-packages/studio/backend/core/inference"
ls -l "$PKG"/sd_cpp_backend.py* "$PKG"/sd_cpp_server.py*
```

Restaurer les deux fichiers Python à partir des sauvegardes `*.before-bc250-...` ou `*.avant-bc250-...` que vous avez vérifiées :

```bash
# Remplacer les deux chemins par les sauvegardes réellement choisies :
# cp -a "CHEMIN_SAUVEGARDE_BACKEND" "$PKG/sd_cpp_backend.py"
# cp -a "CHEMIN_SAUVEGARDE_SERVER" "$PKG/sd_cpp_server.py"
```

Retirer le drop-in ajouté par ce dépôt, puis redémarrer :

```bash
sudo rm -f /etc/systemd/system/skillfish-unsloth.service.d/bc250-vulkan.conf
sudo systemctl daemon-reload
sudo systemctl restart skillfish-unsloth.service
```

Ne pas effacer les modèles ou le cache Hugging Face. Le rollback ne remet pas automatiquement les premiers binaires CPU remplacés manuellement dans `~/.unsloth/stable-diffusion.cpp` : conserver leurs copies `backup-...`.
