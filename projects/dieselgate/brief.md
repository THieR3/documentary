# Brief : Le Dieselgate de Volkswagen

## Cadrage
- **Format** : documentaire YouTube, **12 min** (10 à 15 min accepté), français, 1080p.
- **Chaîne** : « Affaires et scandales » : des histoires vraies racontées avec des images d'époque, ton enquête.
- **Public** : 18-45 ans, curieux d'économie et de faits divers d'entreprise ; aucune connaissance technique requise.
- **Voix** : `fr-FR-HenriNeural` (grave, posée), débit -4 %.
- **Style** : étalonnage `cinematic`, `archive` pour les images 2014-2015, couleur d'accent `#E8B04B`, sous-titres incrustés.
- **Musique** : piste Epidemic Sound choisie par l'utilisateur
  (https://www.epidemicsound.com/fr/music/tracks/5a2536b3-2ec2-4b9b-bc45-00abbf620352/), fournie dans
  `inputs/music/` (copiée vers `media/music/` par `fetch_sources.py`). Dans `timeline.json` :
  `"music": {"src": "music/dieselgate_theme_loop.mp3", "volume": 0.22}` (boucle de 14,4 min avec fondus enchaînés, faite à partir d'un enregistrement de 76 s de la piste). Ne pas la télécharger depuis le site (il faut un compte).
  Si le dossier est vide, rendre le film sans musique et le signaler. Rappeler à l'utilisateur que sa chaîne YouTube doit
  être déclarée dans son compte Epidemic Sound pour éviter les réclamations Content ID.

## Angle (la question du film)
**Comment trois chercheurs d'une petite université de Virginie-Occidentale, avec 70 000 dollars de budget, ont fait
tomber le plus grand constructeur automobile du monde ?**
On raconte une enquête : l'histoire se lit du point de vue de ceux qui ont découvert la fraude, puis on remonte vers
Wolfsburg pour comprendre comment une entreprise entière a pu mentir pendant presque dix ans.

## Titres proposés
1. « 11 millions de voitures. Un seul logiciel. Le mensonge de Volkswagen »
2. « Comment 3 étudiants ont fait tomber Volkswagen »
3. « Dieselgate : l'arnaque à 30 milliards »

Miniature : capot ou logo VW en gros plan + texte « 11 000 000 » + flèche rouge sur un pot d'échappement.

## Structure (≈ 1 600 mots de narration)
| bloc | durée | contenu |
|---|---|---|
| Cold open | 0:00–0:45 | Septembre 2015 : l'annonce de l'EPA ou des images de bourse. Une citation d'archive (« we have totally screwed up », Michael Horn). Question : comment en est-on arrivé là ? |
| Titre | ~0:50 | carte titre |
| 1. Le pari du « Clean Diesel » | ~2 min | Les ambitions de Winterkorn (devenir n°1 mondial en 2018), l'assaut sur le marché américain, les publicités « Clean Diesel », le prix Green Car of the Year 2009 pour la Jetta TDI, et le problème : les normes américaines sur les NOx sont impossibles à tenir à bas coût. |
| 2. Le test de Morgantown | ~2,5 min | 2013-2014 : l'ICCT commande une étude ; l'équipe CAFEE de WVU (Dan Carder, Arvind Thiruvengadam, Hemanth Kappanna…) teste une Jetta, une Passat et une BMW X5 sur route avec des appareils portables. Les VW émettent jusqu'à 15 à 35 fois la limite. Le doute, puis le rapport de mai 2014. |
| 3. Le mensonge | ~2,5 min | Le CARB enquête, VW parle d'un « problème technique » et fait un rappel bidon fin 2014. Le logiciel détecte qu'il est sur un banc d'essai (volant immobile, etc.) : c'est le *defeat device*. Aveux du 3 septembre 2015, avis de l'EPA le 18 septembre, Winterkorn démissionne le 23 septembre. |
| 4. L'addition | ~2,5 min | L'action perd environ un tiers en deux jours. 11 millions de véhicules dans le monde, audition de Michael Horn au Congrès (8 octobre 2015). Plaider-coupable de 2017 avec 4,3 milliards de dollars d'amendes aux États-Unis ; plus de 30 milliards d'euros au total. Arrestation d'Oliver Schmidt (7 ans de prison), James Liang, Rupert Stadler (Audi). Les tests sur des singes (2018). |
| Conclusion | ~1,5 min | Ce que ça a changé : nouveaux tests en conditions réelles (RDE/WLTP), effondrement du diesel en Europe, VW qui mise tout sur l'électrique. Retour à Morgantown : une petite équipe et 70 000 $. Le procès Winterkorn en Allemagne, toujours pas jugé. Image finale. |

## Faits à vérifier par recherche web avant d'écrire (2 sources chacun)
- Budget de l'étude WVU (environ 70 000 $), modèles testés, multiples de dépassement NOx annoncés (Jetta, Passat).
- Dates : rapport ICCT/WVU (mai 2014), rappel VW (décembre 2014), aveux (3 septembre 2015), avis de l'EPA (18 septembre 2015), démission de Winterkorn (23 septembre 2015), audition de Horn (8 octobre 2015), plaider-coupable (janvier 2017).
- Nombre de véhicules (482 000 aux États-Unis, 11 millions dans le monde), chute de l'action, coût total (plus de 30 Md€, chiffre récent).
- Condamnations : Oliver Schmidt, James Liang, Rupert Stadler, procès de Braunschweig (2025), situation actuelle de Winterkorn.
- Estimations sanitaires (études MIT 2015 et 2017 sur les décès prématurés) : formuler prudemment.
- Citation de Michael Horn « We have totally screwed up » (lancement Passat, Brooklyn, 21 septembre 2015).

## Sources d'images : voir `sources.json`
Plusieurs entrées sont des **recherches** (`ytsearch1:`) : vérifier le titre et la chaîne réellement téléchargés et remplacer
la recherche par l'URL exacte si ce n'est pas la bonne vidéo. Compléter avec : reportages ARD/ZDF/France 24/Arte,
conférences de presse VW, publicités « Clean Diesel », images de bourse, usines de Wolfsburg (Wikimedia Commons).
Objectif : 8 à 12 sources, plus d'une heure de matière, et au moins 75 % d'images réelles dans le film.

## Faits vérifiés (recherche web, novembre 2026)
- Étude WVU/CAFEE commandée par l'ICCT en 2013 : ~70 000 $ (69 387 $ exactement). Jetta (piège à NOx), Passat (SCR), BMW X5.
  Jetta 15 à 35 fois la norme Tier 2 Bin 5, Passat 5 à 20 fois ; BMW dans les clous. Résultats présentés en mai 2014 (15/05/2014),
  transmis au CARB et à l'EPA. — theicct.org (communiqué), magazine-archive.wvu.edu « Double exposure », Wikipedia.
- Rappel « volontaire » de décembre 2014 jugé insuffisant (lettre EPA/CARB). 3 septembre 2015 : VW reconnaît le defeat device devant
  l'EPA et le CARB. 18 septembre 2015 : avis d'infraction de l'EPA (482 000 voitures 2.0 TDI 2009-2015). 22 septembre : VW reconnaît
  11 millions de véhicules. 23 septembre : démission de Winterkorn. — CTV, CSMonitor, NPR, CBS, Scotsman.
- Action : -18,6 % à la clôture du 21/09/2015 (jusqu'à -23 % en séance), environ un tiers en quelques jours, ~25 Md€ de capitalisation.
  — NPR, Bloomberg via TPR, Business Standard (Xinhua), Euronews 22/09/2015.
- Michael Horn : « We have totally screwed up » (lancement Passat, Brooklyn, 21/09/2015 ; archive vidéo). Audition Chambre des
  représentants (Energy and Commerce) le 8/10/2015, « a couple of software engineers ». — NPR, CNN Money, The Register.
- Plaider-coupable janvier 2017 : 4,3 Md$ (2,8 Md$ pénal + 1,5 Md$ civil). Oliver Schmidt : 7 ans (06/12/2017). James Liang :
  40 mois (25/08/2017). — justice.gov, NPR.
- Rupert Stadler (Audi) : 1 an et 9 mois avec sursis + 1,1 M€ d'amende (Munich, 27/06/2023), premier membre du directoire condamné.
  — Time/AP, Euronews.
- Braunschweig, 26/05/2025 : quatre ex-managers condamnés pour fraude, dont deux à de la prison ferme (Jens Hadler 4,5 ans, Hanno Jelden).
  Winterkorn : procès séparé, suspendu pour raisons de santé (2024-2025), toujours pas jugé. — Euronews, Irish Times, Fortune.
- Coût total : ~32 à 33 Md€ (porte-parole VW 2025 : 33,8 Md€ ; Bloomberg août 2025 : 32 Md€). Dire « plus de trente milliards d'euros ».
- Santé (formuler prudemment) : étude MIT/Harvard 2015 ~59 décès prématurés estimés aux États-Unis ; étude MIT 2017 ~1 200 en Europe.
  — news.mit.edu, seas.harvard.edu.
- Singes : expérience de 2014 au Lovelace Respiratory Research Institute (Albuquerque), 10 macaques exposés aux gaz d'une Beetle
  diesel truquée, financée via l'EUGT ; révélée par le New York Times en janvier 2018. — NYT via Irish Times, Fortune, National Geographic.
