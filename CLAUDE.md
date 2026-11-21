# Docu Studio

Ce repo fabrique des documentaires YouTube de 10 à 15 minutes à partir d'extraits de documentaires et vidéos existants,
avec narration TTS et motion design d'accompagnement. Il est fait pour tourner dans une **session Claude Code cloud**,
pas sur le PC de l'utilisateur (son PC est lent et n'a pas de GPU).

- Workflow complet : skill `documentaire` (`.claude/skills/documentaire/SKILL.md`). Le suivre pour toute demande de documentaire.
- Rendu vidéo : Remotion (`remotion/`, composition `Documentary`, piloté par `projects/<slug>/build/props.json`).
- Audio : mixé par ffmpeg dans `scripts/render.py`, pas par Remotion (les vidéos Remotion sont rendues `muted`).
- L'environnement s'installe au démarrage via `scripts/setup.sh` (hook SessionStart). Le relancer si ffmpeg, node_modules ou yt-dlp manquent.

## Premier lancement dans un nouvel environnement cloud
Faire un smoke test avant le premier vrai film :
```bash
python3 scripts/make_test_project.py
python3 scripts/fetch_sources.py _test --no-transcribe
python3 scripts/build_props.py _test
python3 scripts/render.py _test --stills
python3 scripts/render.py _test --preview --sec 40
```
Regarder 2-3 stills (Read) pour vérifier que les plans vidéo s'affichent (pas d'écran noir) ; les WARN sur la durée et le % de
footage sont normaux pour ce projet de test.

## Conventions
- Projets dans `projects/<slug>/` ; ne jamais committer `media/`, `build/`, `out/` (vidéos lourdes).
- Le film livré va dans une release GitHub (`scripts/deliver.py`, si `GH_TOKEN`) ou dans `delivery/<slug>/` (copie < 95 Mo) à committer.
- Langue de travail avec l'utilisateur : français.
- Rendus longs (`render.py` complet, `fetch_sources.py` avec transcription) : lancer en arrière-plan.
- Réseau : l'environnement cloud doit avoir un accès Internet complet (YouTube, archive.org, Microsoft TTS, Google Fonts).
