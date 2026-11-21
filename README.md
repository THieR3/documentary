# Docu Studio

Fabrique de documentaires (10 à 15 min) faits **par Claude dans le cloud** : Claude cherche des extraits de
documentaires et vidéos existants, les télécharge, les transcrit, écrit le script, monte le film en s'appuyant sur ces
images (au moins 75 % du temps d'écran), ajoute la voix off, les citations d'archives, les crédits à l'écran et le motion
design d'accompagnement, puis rend un MP4 1080p.

## Mise en place (une seule fois)

1. Créer un repo GitHub **privé** vide (ex. `docu-studio`) et y pousser ce dossier :
   ```bash
   git remote add origin https://github.com/<ton-compte>/docu-studio.git
   git push -u origin main
   ```
2. Sur https://claude.ai/code : connecter GitHub, choisir ce repo et créer un **environnement** avec
   **accès réseau complet** (« Full »), sinon YouTube, archive.org et la voix TTS seront bloqués.
   Variables d'environnement facultatives : `GH_TOKEN` (livraison par release GitHub, jusqu'à 2 Go),
   `ELEVENLABS_API_KEY` (voix ElevenLabs), `WHISPER_MODEL` (`base` par défaut).
3. Première session : demander « lance le smoke test du CLAUDE.md ».

## Utilisation

Dans une session cloud sur ce repo, par exemple :

> Fais un documentaire de 12 min sur la catastrophe de Tchernobyl, ton enquête, voix masculine.
> Utilise ces vidéos en priorité : <liens YouTube / archive.org>

Claude suit le skill `documentaire` : sources → dérush → script → montage → voix → contrôle visuel → rendu.
Le film arrive en release GitHub ou dans `delivery/<slug>/`, avec les sous-titres `.srt`, les chapitres YouTube,
les crédits pour la description et une miniature.

Musique : déposer des pistes libres de droits dans `projects/<slug>/media/music/` (ou les donner en lien).

## Contenu

| chemin | rôle |
|---|---|
| `.claude/skills/documentaire/` | le skill (workflow, schéma du montage, règles de motion, écriture, droits) |
| `scripts/fetch_sources.py` | téléchargement (yt-dlp), transcription, détection de plans, planches contact |
| `scripts/tts.py` | voix off (edge-tts gratuit ou ElevenLabs) avec timing mot par mot |
| `scripts/build_props.py` | timeline → props Remotion + plan audio, contrôles (durée, % footage, erreurs) |
| `scripts/render.py` | stills de contrôle, preview, rendu complet par morceaux (reprise possible), mix audio -14 LUFS |
| `scripts/deliver.py` | livraison (release GitHub ou copie < 95 Mo) |
| `remotion/` | composants vidéo : Ken Burns, étalonnage, letterbox, titres, chapitres, bandeaux, chiffres, cartes, frises, surlignages, citations, sous-titres |

Droits : les extraits sont courts, transformés et crédités, mais tu restes responsable de ce que tu publies.
Préfère les sources libres (archive.org, Wikimedia, NASA, INA, Creative Commons). Voir `references/sources-et-droits.md`.
