# PurpleMulti

Version personnelle d'[Evanovar RAM](https://github.com/evanovar/RobloxAccountManager)
d'evanovar (branche `perso`). La licence GPL-3 et le copyright d'origine sont conservés.

## Lancer

Double-clic sur `Lancer PurpleMulti.cmd`. Les données sont dans
`%LOCALAPPDATA%\PurpleMulti`, hors du dépôt.

Seuls les noms visibles ont changé. La classe `RobloxAccountManager`, le fichier
`packaging/EvanovarRAM.spec` et les URL de l'updater gardent leur nom, pour que
les fusions avec l'original restent simples.

## Comment l'app fonctionne

| Partie | Fichier | Rôle |
| --- | --- | --- |
| Interface | `src/utils/ui.py` | Toute l'UI PySide6 (8 800 lignes) |
| Comptes | `src/classes/account_manager.py` | Liste des comptes, sauvegarde atomique, `.bak`, connexion via Selenium |
| API Roblox | `src/classes/roblox_api.py` | Cookie → ticket d'authentification → lien `roblox-player:` → lancement du client |
| Chiffrement | `src/classes/encryption.py` | Modes Windows (DPAPI), mot de passe, ou aucun |
| Multi-instance | `src/features/account_actions.py` | Mutex singleton de Roblox, ou fermeture du handle via Handle64 |
| Suivi | `src/features/launch_monitor.py`, `presence.py`, `auto_rejoin.py` | Confirmation du lancement par les logs du client, présence, reconnexion |
| Fenêtres | `src/features/window_*.py`, `headless_manager.py` | Renommage, grille, masquage |

Pour se connecter, Roblox demande un ticket à usage unique à partir du cookie
`.ROBLOSECURITY`, puis l'app ouvre le client avec ce ticket. Le cookie est donc
l'équivalent d'une session ouverte : qui le possède contrôle le compte.

## Différences avec l'original

- Mode « Hardware » : DPAPI, lié au compte Windows, au lieu d'une clé déduite
  d'identifiants matériels lisibles par n'importe quel programme.
- Mode mot de passe : PBKDF2-SHA256 à 600 000 itérations au lieu de
  PBKDF2-SHA1 à 100 000.
- Les anciens fichiers et leur `.bak` sont convertis à l'ouverture.
- L'auto-update ne remplace plus jamais l'application par la version d'origine.

- Interface refaite : thème violet par défaut, nouvelle icône, barre latérale,
  cartes, interrupteurs et réglages en onglets.
- `Ctrl+1`, `Ctrl+2`… ouvrent les pages de la barre latérale, dans l'ordre.
- Page Donations masquée pour l'instant. Pour la remettre avec tes infos :
  change `_DONATION_URL`, `_DONATION_USERNAME` et les textes de
  `_build_donations_panel` dans `src/utils/ui.py`, puis passe
  `SHOW_DONATIONS_PAGE` à `True`.
- Listes vides (comptes, Auto-Rejoin, jeux récents) : message centré qui dit
  quoi faire. Avatars pas encore chargés : initiales du pseudo.
- Le lanceur fait `uv sync` à chaque démarrage (instantané si rien n'a changé),
  donc les nouvelles dépendances arrivent toutes seules après une fusion.

## Légèreté

- Dépendances : `pyside6-essentials` + `pyside6-addons` au lieu du paquet
  `pyside6`, qui installait aussi WebEngine et Pdf (355 Mo jamais utilisés).
  Addons ne sert qu'à QtMultimedia, pour les fonds vidéo.
- Exe (`scripts/build.py`) : le `.spec` exclut les modules Python et les
  fichiers Qt que l'app ne charge jamais (Selenium macOS/Linux, DevTools et
  trio, QtQuick/QML/Pdf, rendu OpenGL logiciel, traductions Qt…). Si un jour
  une fonction a besoin de l'un d'eux, retire-le des listes `EXCLUDED_*`.
- Le module WebSocket n'est chargé que si le serveur est activé.

Si `uv sync` laisse PySide6 cassé (`DLL load failed while importing QtCore`),
les paquets PySide6 se partagent des fichiers :
`uv sync --reinstall-package pyside6-essentials --reinstall-package pyside6-addons --reinstall-package shiboken6`.

## Interface

| Partie | Fichier | Rôle |
| --- | --- | --- |
| Styles | `src/utils/theme_styles.py` | Tous les composants, avec les variantes de boutons (`primary`, `ghost`, `danger`, `icon`) |
| Briques de page | `src/utils/ui_kit.py` | Cartes, en-têtes de page, pastilles, lignes de réglage, `EmptyState`, `OptionCard`, `initials()` |
| Couleurs | `src/features/color_themes.py` | Palette `default` (Purple) et les 7 autres thèmes |
| Thème actif | `src/utils/theme_runtime.py` | Jetons `@RAM_*@`, interrupteurs SVG, barre de titre Windows |

Pour changer une couleur ou un composant, modifie ces fichiers plutôt que
d'ajouter un style dans `ui.py`. Les champs numériques ont besoin de la règle
`subcontrol-origin: border` de `theme_styles.py`, sans quoi leur zone de saisie
retombe à 1 px.

## Limites

- DPAPI protège contre le vol du fichier seul et contre les autres comptes
  Windows, pas contre un programme qui tourne sous ta session. Le mode mot de
  passe résiste mieux à ce cas, au prix d'une saisie à chaque démarrage.
- DPAPI ne survit pas à une réinstallation de Windows ni à une réinitialisation
  forcée du mot de passe Windows. Fais un export (`Settings > Misc`) de temps en
  temps : c'est le seul moyen de récupérer les comptes dans ces cas.
- Les exports `.rambak` faits ici ne s'ouvrent pas dans la version d'origine.

## Récupérer les nouveautés de l'original

L'interface ayant été largement réécrite, attends-toi à des conflits dans
`src/utils/ui.py` quand l'original modifie ses pages.

Une fois tes changements commités :

```powershell
git fetch upstream
git merge upstream/main
uv sync --locked
```
