# PurpleMulti

Gestionnaire de comptes Roblox pour Windows : organiser ses comptes, lancer
plusieurs clients en même temps et automatiser les tâches courantes.

PurpleMulti est une version personnelle d'[Evanovar RAM](https://github.com/evanovar/RobloxAccountManager),
le projet open source d'evanovar. Il en garde les fonctions et la licence
GPL-3.0, avec une interface refaite, un chiffrement renforcé et une
installation plus légère.

## Fonctions

- **Comptes** : groupes, notes, avatars, réorganisation par glisser-déposer,
  sélection multiple, import par cookie ou connexion via navigateur.
- **Lancement** : jeux publics, serveurs privés, serveur précis, plusieurs
  comptes à la suite.
- **Multi Roblox** : toujours actif, plusieurs clients à la fois (méthode par défaut ou Handle64).
- **Sauvegarde automatique** : copie chiffrée des comptes à intervalle régulier,
  restaurable sur n'importe quel PC.
- **Suivi** : Auto-Rejoin, Anti-AFK, présence et activité des comptes.
- **Fenêtres** : renommage, grille, masquage des clients Roblox.
- **Outils** : sélecteur de jeux, liens de serveurs privés, réglages Roblox
  avec application automatique.
- **Personnalisation** : thèmes de couleurs, fonds image, GIF ou vidéo.

## Ce qui change par rapport à l'original

- **Chiffrement** : le mode « Hardware » utilise DPAPI, lié au compte Windows,
  au lieu d'une clé tirée d'identifiants matériels lisibles par n'importe quel
  programme. Le mode mot de passe passe à PBKDF2-SHA256 avec 600 000
  itérations. Les anciens fichiers sont convertis à l'ouverture.
- **Interface** : thème violet, barre latérale, cartes, réglages en onglets,
  raccourcis `Ctrl+1`, `Ctrl+2`…
- **Plus léger** : environ 400 Mo installé au lieu de 740 Mo, exe de 48 Mo au
  lieu de 78 Mo.
- **Mises à jour** : l'app ne remplace jamais cette version par celle
  d'origine. Quand l'original publie une nouvelle version, elle indique
  comment la fusionner.

Les exports `.rambak` faits avec PurpleMulti ne s'ouvrent pas dans la version
d'origine.

## Installation

Il faut Windows 10 ou 11, [Git](https://git-scm.com/) et
[uv](https://docs.astral.sh/uv/). uv installe lui-même Python 3.15.

```powershell
git clone https://github.com/bleathingman/purplemulti.git
cd purplemulti
```

Ensuite, double-clic sur **`Lancer PurpleMulti.cmd`**. Le script installe les
dépendances au premier lancement et les met à jour aux suivants.

Pour un exécutable : `.\scripts\build.cmd`, qui produit `dist\PurpleMulti.exe`.

## Données et confidentialité

Avec le lanceur, les données sont dans `%LOCALAPPDATA%\PurpleMulti`, hors du
dépôt : comptes chiffrés et leur sauvegarde, réglages, groupes, jeux récents,
cache d'avatars, journaux. Un autre dossier peut être choisi avec
`--data-dir "D:\Profils\Alt"` ou la variable `RAM_DATA_DIR`.

Le cookie `.ROBLOSECURITY` d'un compte équivaut à une session ouverte : qui le
possède contrôle le compte. Il n'est envoyé qu'à Roblox. L'app n'a ni
télémétrie ni publicité. Ses requêtes réseau servent aux fonctions utilisées :
API Roblox, vérification des versions sur GitHub, Chromium portable, Handle64,
et tests de connexion pour Auto-Rejoin.

Le chiffrement DPAPI ne survit pas à une réinstallation de Windows. Active la
sauvegarde automatique (`Settings > Misc > Automatic Backup`) dans un dossier
qui y survit, comme OneDrive.

## Modifications du système

Selon les fonctions activées, l'app peut créer des raccourcis (démarrage de
Windows, menu Démarrer), télécharger Chromium, Handle64 ou des versions de
Roblox, modifier le fichier de réglages Roblox en gardant une copie
`.ram.bak`, et verrouiller temporairement des fichiers de Roblox pendant le
Multi Roblox.

Pour désinstaller : désactive « Roblox Installer Fix » si besoin, quitte
l'app, retire les raccourcis activés, puis supprime le dossier du dépôt et
`%LOCALAPPDATA%\PurpleMulti`.

## Développement

```powershell
uv run python scripts/run_tests.py --all    # tests
uvx ruff check .                            # lint
```

Pour récupérer les nouveautés de l'original :

```powershell
git fetch upstream
git merge upstream/main
uv sync --locked
```

## Avertissement

Ce projet sert à gérer ses propres comptes. Chacun est responsable du respect
des conditions d'utilisation de Roblox. Les auteurs ne sont pas responsables
des sanctions, pertes de données ou autres conséquences liées à son
utilisation.

## Licence

[GNU General Public License v3.0](LICENSE). Copyright d'origine : evanovar.
