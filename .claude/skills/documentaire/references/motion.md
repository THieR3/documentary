# Motion design : quand et combien

Le motion doit *servir la footage*. Repères pour un film de 12 min (~120–180 plans) :

| élément | fréquence | usage |
|---|---|---|
| crédit source | auto | à chaque nouvelle source à l'écran |
| `lowerThird` | 1er passage de chaque intervenant/lieu | qui parle, sa fonction ; 3–4 s |
| `date` | à chaque saut temporel | « MARS 1986 » ; 2,5–3 s |
| `stat` | 4–8 par film | un chiffre qui compte, pas une liste ; `left`/`right` sur footage, `center` pour le chiffre clé du film |
| `highlight` | 3–6 par film | montrer ce que la narration désigne dans l'image (« regardez l'homme à gauche ») |
| `map` plein écran | 0–3 | quand la géographie explique quelque chose ; carte en `media/assets/` (Wikimedia Commons, Natural Earth) |
| `timeline` plein écran | 0–2 | récapituler une chronologie complexe |
| `quote` plein écran | 0–2 | citation écrite forte sans archive audio |
| `kinetic` | 0–2 | la phrase thèse du film |
| `chapter` | 1 par chapitre | 3–4 s, fond = plan du chapitre flouté |
| `title` | 1 | après le cold open, 4–5 s |

## Mouvements caméra sur footage
- Archives fixes / photos : toujours un `motion` (`zoom-in` lent par défaut, `pan-*` pour paysages/foules).
- Footage déjà en mouvement : `drift` (quasi imperceptible) ou `static`.
- Alterner les sens (`pan-left` puis `pan-right`) entre plans consécutifs ; éviter deux zooms identiques de suite.

## Étalonnage
- Un `grade` par défaut pour tout le film (`meta.grade`), `archive`/`bw` pour marquer le passé, `cold` pour la tension.
- `letterbox: true` sur les plans « cinéma » (paysages, moments de silence) — sans abuser.

## Rythme
- Plans de 2–6 s ; citations de 5–20 s ; respirations sans voix (musique + son original) de 3–6 s entre chapitres.
- Overlays : jamais deux en même temps (sauf crédit), et pas sur les 0,5 premières secondes d'un plan.
- Ne pas recouvrir un visage ou un texte d'origine important par un overlay : vérifier sur les stills.
