# timeline.json — schéma

Temps : secondes (`12.5`) ou timecode (`"01:02.5"`, `"1:02:03"`). Les `in` / `out` sont des positions **dans la
source**. Les `at` / `dur` des overlays sont relatifs au **début du segment**.

```jsonc
{
  "meta": {
    "title": "Apollo 11 : les 8 minutes qui ont failli tout gâcher",
    "lang": "fr",
    "fps": 30, "width": 1920, "height": 1080,
    "voice": { "engine": "edge", "name": "fr-FR-HenriNeural", "rate": "-4%" },
    // ou { "engine": "elevenlabs", "name": "<voice_id>", "model": "eleven_multilingual_v2" }
    "music": { "src": "music/tension.mp3", "volume": 0.22 },   // optionnel, fichier dans media/music/
    "captions": true,                                            // sous-titres incrustés (mot actif surligné)
    "grade": "cinematic",                                        // étalonnage par défaut des plans vidéo
    "style": { "accent": "#E8B04B", "text": "#F5F1E8", "headingFont": "PlayfairDisplay", "grain": 0.35, "vignette": 0.5 }
  },
  "chapters": [
    {
      "title": "Cold open",                       // devient un chapitre YouTube
      "segments": [
        // citation d'archive : son original, durée = out - in
        { "id": "open1",
          "bite": { "source": "ina_1969", "in": "03:12.0", "out": "03:19.5", "volume": 1.0,
                    "subtitle": "traduction si la citation n'est pas en français" },
          "overlays": [ { "type": "date", "at": 0.3, "dur": 3, "text": "20 JUILLET 1969" } ] },

        // narration sur plusieurs plans (durée = voix off + pad ; partagée entre les shots sans "dur")
        { "id": "open2",
          "vo": "À 384 000 kilomètres de la Terre, deux hommes descendent vers une plaine grise. Il leur reste soixante secondes de carburant.",
          "shots": [
            { "type": "video", "source": "nasa_16mm", "in": "12:03", "motion": "zoom-in", "dur": 3.5 },
            { "type": "video", "source": "nasa_16mm", "in": "14:40", "motion": "pan-right" },
            { "type": "video", "source": "doc_bbc", "in": "22:10", "grade": "archive", "fit": "blur-fill",
              "overlays": [ { "type": "stat", "at": 0.2, "dur": 3, "value": 60, "suffix": " s", "label": "de carburant", "position": "right" } ] }
          ],
          "sourceVolume": 0.15,                     // ambiance originale sous la voix
          "transition": "fade", "transitionDur": 0.5 }
      ]
    },
    {
      "title": "La course",
      "segments": [
        { "duration": 3.5, "transition": "dip",
          "visual": { "type": "chapter", "number": 1, "title": "La course", "bg": { "type": "video", "source": "doc_bbc", "in": "05:00" } } },
        { "vo": "…", "visual": { "type": "video", "source": "itw_aldrin", "in": "01:10" },
          "overlays": [ { "type": "lowerThird", "at": 0.5, "dur": 4, "title": "Buzz Aldrin", "subtitle": "Pilote du module lunaire" } ] }
      ]
    }
  ]
}
```

## Champs d'un segment

| champ | rôle |
|---|---|
| `id` | facultatif (auto `c<chap>s<seg>`). Sert de nom au fichier voix `media/vo/<id>.mp3`. |
| `vo` | texte de narration (généré par `tts.py`). |
| `bite` | `{source, in, out, volume?, subtitle?}` : extrait avec son original. Image = cette source à `in` sauf si `visual`/`shots` donné. |
| `visual` | un seul visuel (voir types). |
| `shots` | liste de visuels coupés dans l'ordre ; `dur` optionnel par shot ; chaque shot peut avoir `overlays`, `transition`. |
| `duration` | durée minimale (s). Durée réelle = max(duration, voix + pad, bite). |
| `pad` | silence après la voix (défaut 0,35 s). `voDelay` : décale la voix. |
| `overlays` | overlays sur le 1er shot (ou sur le segment). |
| `sourceVolume` | volume (0–1) du son original des shots vidéo sous la narration. |
| `credit` | `false` pour masquer le crédit auto, ou un texte pour le remplacer. |
| `transition` / `transitionDur` | `cut` · `fade` · `dip` (noir) · `whip` (glissé flou). |

## Types de visuels

- `video` : `source` (id de sources.json), `in`, `rate` (vitesse, 0.5 = ralenti), `motion`, `grade`, `fit`, `letterbox`.
- `image` : `src` (relatif à `media/`, ex. `assets/photo.jpg`), `motion` (défaut zoom-in), `grade`, `fit`.
- `title` : `title`, `subtitle`, `bg` (visuel flouté derrière).
- `chapter` : `number`, `title`, `bg`.
- `quote` : `text`, `author`, `bg` — citation écrite plein écran (pour une citation *sans* archive audio).
- `map` : `src` (image de carte dans `media/assets/`), `pins: [{x, y, label, at?}]` (x/y en % de l'image).
- `timeline` : `events: [{year, label}]`, `active` (index mis en avant), `bg`.
- `color` : `color`.

`motion` : `static`, `zoom-in`, `zoom-out`, `pan-left`, `pan-right`, `pan-up`, `pan-down`, `drift` (défaut vidéo).
`grade` : `none`, `cinematic`, `warm`, `cold`, `bw`, `archive`.
`fit` : `cover` (défaut 16:9), `contain`, `blur-fill` (défaut auto pour 4:3 / vertical : fond flouté).

## Types d'overlays (`at`, `dur` + champs)

- `lowerThird` : `title`, `subtitle` — identifier un intervenant / un lieu.
- `date` : `text` — situer dans le temps (haut gauche).
- `stat` : `value`, `prefix`, `suffix`, `label`, `decimals`, `position` (`center` assombrit l'image, `left`/`right` non).
- `highlight` : `box: [x, y, w, h]` en % de l'écran, `label`, `shape` (`rect`/`circle`) — pointer un détail de l'image.
- `quote` : `text`, `author` — citation en bas d'écran sur la footage.
- `kinetic` : `lines: ["mot", "mot", "MOT FINAL"]` — phrase choc mot à mot (rare : 1–2 fois par film).
- `credit` : ajouté automatiquement avec le `credit` de la source à chaque nouveau passage d'une source.
