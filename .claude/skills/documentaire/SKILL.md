---
name: documentaire
description: Produit un documentaire YouTube de 10 à 15 minutes construit à partir d'extraits de documentaires et de vidéos existants (archives, interviews, reportages), avec narration, citations audio des originaux, crédits à l'écran et motion design d'accompagnement (titres, chapitres, chiffres, cartes, frises, surlignages). Utiliser quand l'utilisateur demande un documentaire, une vidéo explicative longue, une vidéo "storytelling" ou "enquête" sur un sujet, à partir de liens vidéo ou d'un simple sujet.
---

# Documentaire (sources existantes + motion)

Le principe : **on raconte avec les images des autres, on ne remplace pas les images par du motion.**
Au moins **75 % du temps d'écran est de la vraie footage** issue de documentaires/vidéos existants. Le motion
design sert à guider (qui parle, quand, où, combien) — majoritairement en *overlay* sur la footage, rarement
en plein écran. Chaque extrait emprunté est **crédité à l'écran** automatiquement et listé dans `out/credits.txt`.

Pipeline : `sources.json` → `fetch_sources.py` (téléchargement + transcription + planches contact) → script →
`timeline.json` → `tts.py` (voix off) → `build_props.py` (vérifs) → `render.py --stills` (QA visuelle) →
`render.py --preview` → `render.py` (rendu complet) → `deliver.py`.

Tout tourne dans la session cloud (Linux). Lancer `bash scripts/setup.sh` si une commande manque.
Toutes les commandes se lancent depuis la racine du repo. Un projet = `projects/<slug>/`.

## 1. Cadrage (5 min)

Si l'utilisateur n'a pas tout donné, déduire des valeurs raisonnables plutôt que poser 10 questions.
Écrire `projects/<slug>/brief.md` : sujet, angle (la question à laquelle le film répond), public, langue
(défaut français), durée cible (défaut 12 min), ton (enquête, épique, intimiste…), voix, liens fournis.

## 2. Trouver les sources (le cœur du travail)

Chercher sur le web des **vidéos existantes** qui montrent le sujet : documentaires, reportages TV, interviews,
images d'archives, conférences, footage officiel. Viser **6 à 15 sources, 1 h+ de matière** pour 12 min de film.
Ordre de préférence (droits) — voir `references/sources-et-droits.md` :
1. liens fournis par l'utilisateur ;
2. domaine public / libre : archive.org, Wikimedia Commons, NASA, INA (extraits libres), archives nationales,
   chaînes YouTube sous Creative Commons (filtre « Creative Commons ») ;
3. documentaires/reportages YouTube : extraits courts (≤ 10–15 s par plan, ≤ 20–30 s pour une citation),
   transformés (narration, analyse, recadrage), toujours crédités.

Écrire `projects/<slug>/sources.json` :
```json
[{"id": "ina_1969", "url": "https://…", "title": "Journal télévisé du 21/07/1969", "credit": "Archives : INA",
  "license": "extrait – citation", "lang": "fr", "section": {"start": "00:02:00", "end": "00:09:30"}}]
```
`section` (optionnel) ne télécharge qu'une partie d'une longue vidéo. `file` (au lieu de `url`) pour un fichier
déjà présent dans le projet. `credit` est le texte affiché en haut à droite quand l'extrait passe à l'écran.

```bash
python scripts/fetch_sources.py <slug>
```
Produit dans `projects/<slug>/build/sources/` : `<id>.transcript.txt` (lignes `[mm:ss - mm:ss] texte`),
`<id>.sheet_XX.jpg` (planches contact : 1 vignette par plan, n° + timecode), `<id>.shots.json`.
Si YouTube bloque (« Sign in to confirm you're not a bot ») : réessayer une fois, puis passer à une autre source
(archive.org, Commons…) ou demander à l'utilisateur de déposer le fichier dans `projects/<slug>/media/sources/`
ou un fichier cookies (`YTDLP_COOKIES=/chemin/cookies.txt`). Ne pas bloquer tout le film pour une source.

**Dérusher** : ouvrir (Read) chaque planche contact et lire chaque transcript. Noter dans
`projects/<slug>/build/derush.md` les meilleurs plans (`id @ mm:ss — description — usage`) et les meilleures
**citations audio** (phrases fortes d'interviews/narrations originales, avec in/out précis). C'est ce dérush qui
fait la qualité du film : un plan précis par idée du script.

## 3. Écrire le script

Voir `references/ecriture.md`. En bref : ~140–150 mots/min de narration → **1 300 à 1 900 mots** de voix off pour
10–15 min, le reste étant des citations originales et des respirations.
Structure : cold open (accroche 30–45 s, souvent une citation d'archive) → titre → 4 à 6 chapitres
(problème → escalade → retournement) → conclusion qui répond à la question de départ.
Alterner : narration sur footage ↔ **citation d'archive** (le son original) toutes les 60–90 s.
Vérifier les faits (dates, chiffres, noms) par recherche web ; ne rien inventer.

## 4. Monter : `timeline.json`

Schéma complet et exemples : `references/timeline.md`. Catalogue des effets : `references/motion.md`.
Règles de montage :
- un segment = un paragraphe de voix off (1–3 phrases) **ou** une citation (`bite`) ;
- sur un paragraphe, couper entre plusieurs plans (`shots`, 2–6 s chacun) — ne jamais rester > 8 s sur un plan ;
- chaque idée du texte a son image dans le dérush (ce qui est dit = ce qui est montré) ;
- motion en overlay sur la footage : `lowerThird` au 1er passage d'un intervenant, `date` pour situer,
  `stat` pour un chiffre clé, `highlight` pour pointer un détail, `map` / `timeline` quand la géographie ou la
  chronologie compte ; cartes plein écran (`title`, `chapter`, `quote`, `map`, `timeline`) avec parcimonie ;
- `sourceVolume: 0.1–0.2` pour garder l'ambiance originale sous la narration ;
- transitions : `cut` par défaut à l'intérieur d'un segment, `fade` entre segments, `dip` avant un chapitre.

## 5. Voix, vérification, QA

```bash
python scripts/tts.py <slug>          # voix edge-tts (gratuite) ou ElevenLabs si meta.voice.engine = "elevenlabs"
python scripts/build_props.py <slug>  # rapport : durée, chapitres, % footage, erreurs
```
Corriger jusqu'à **0 ERROR** ; traiter les WARN (durée hors 10–15 min, footage < 75 %, plan qui déborde de sa
source, même passage réutilisé deux fois).
```bash
python scripts/render.py <slug> --stills    # 1 image par plan dans build/stills/
```
Ouvrir les stills (Read) et vérifier : cadrage (pas de logo/incrustation TV gênante, sujet visible), lisibilité des
textes, crédits présents, pas de doublons visuels. Corriger le timeline (autre `in`, `fit: "blur-fill"` pour du
4:3, `motion`, autre plan) puis relancer build_props + stills sur les plans corrigés (`--frames`).
```bash
python scripts/render.py <slug> --preview --sec 90   # MP4 basse déf des 90 premières secondes (son inclus)
```

## 6. Rendu et livraison

```bash
python scripts/render.py <slug>       # long : lancer en arrière-plan ; reprend là où il s'est arrêté
python scripts/deliver.py <slug>      # release GitHub si GH_TOKEN, sinon copie <95 Mo dans delivery/<slug>/
```
Sorties dans `projects/<slug>/out/` : `<slug>.mp4` (1080p, -14 LUFS), `<slug>.srt`, `chapters.txt`
(chapitres YouTube), `credits.txt` (à coller dans la description), `thumbnail.jpg`.
Si `deliver.py` fait une copie git : `git add delivery/<slug> && git commit && git push` sur la branche de session.
Ne jamais committer `projects/*/media` ni `build/` (gitignore).

Rendre compte à l'utilisateur : durée finale, nb de sources utilisées, % footage, où télécharger, et les
points à vérifier côté droits (sources non libres utilisées).
