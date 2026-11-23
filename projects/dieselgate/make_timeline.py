"""Génère timeline.json pour le documentaire Dieselgate.  python3 projects/dieselgate/make_timeline.py"""
import json
from pathlib import Path


def V(source, t, motion=None, dur=None, **kw):
    s = {"type": "video", "source": source, "in": t}
    if motion:
        s["motion"] = motion
    if dur:
        s["dur"] = dur
    s.update(kw)
    return s


def ndr(t, motion="zoom-in", **kw):  # NDR 45 Min : logo « 45 » en bas à gauche, on zoome légèrement
    return V("news_report_de", t, motion, **kw)


def seg(vo, shots, overlays=None, **kw):
    s = {"vo": vo, "shots": shots, "sourceVolume": 0.12}
    if overlays:
        s["overlays"] = overlays
    s.update(kw)
    return s


def bite(source, a, b, sub=None, overlays=None, visual=None, **kw):
    s = {"bite": {"source": source, "in": a, "out": b, "volume": 1.0}}
    if sub:
        s["bite"]["subtitle"] = sub
    if overlays:
        s["overlays"] = overlays
    if visual:
        s["visual"] = visual
    s.update(kw)
    return s


def chapter(n, title, bg):
    return {"duration": 3.6, "transition": "dip", "visual": {"type": "chapter", "number": n, "title": title, "bg": bg}}


def date(text, at=0.6, dur=3):
    return {"type": "date", "at": at, "dur": dur, "text": text}


def lt(title, subtitle, at=0.6, dur=4):
    return {"type": "lowerThird", "at": at, "dur": dur, "title": title, "subtitle": subtitle}


def stat(value, label, prefix="", suffix="", decimals=0, position="right", at=0.6, dur=3.5):
    return {"type": "stat", "at": at, "dur": dur, "value": value, "prefix": prefix, "suffix": suffix,
            "label": label, "decimals": decimals, "position": position}


ARCH = {"grade": "archive"}

cold_open = [
    bite("horn_screwed_up", 33.1, 46.3,
         "Soyons clairs. Notre entreprise a été malhonnête avec l'EPA, avec l'agence californienne de l'air, et avec vous tous. "
         "Pour le dire à l'allemande : on a complètement merdé.",
         overlays=[date("21 SEPTEMBRE 2015 · BROOKLYN", 0.4, 3.2), lt("Michael Horn", "PDG de Volkswagen of America", 4.0, 4)],
         visual=V("horn_screwed_up", 33.1, "zoom-in", **ARCH)),
    seg("Cet homme, c'est le patron de Volkswagen aux États-Unis. Ce soir-là, il devait présenter la nouvelle Passat. "
        "Trois jours plus tôt, l'agence américaine de l'environnement a révélé qu'un logiciel caché trompait les contrôles anti-pollution.",
        [V("horn_screwed_up", 70, "pan-right", **ARCH), ndr("40:35"), V("defeat_device_explained", "01:20.5", "drift", dur=3.5)],
        transition="fade"),
    seg("Onze millions de voitures dans le monde. Plus de trente milliards d'euros de pénalités. Des dirigeants en prison.",
        [V("news_report_fr", "03:32", "zoom-in"), V("stock_plunge", "00:43", "zoom-in", **ARCH), V("wolfsburg_factory", "00:42", "drift")]),
    seg("Et au départ de tout ça, il n'y a ni enquête de police, ni lanceur d'alerte. "
        "Il y a trois voitures, une petite équipe de chercheurs, et un budget de soixante-dix mille dollars.",
        [V("wvu_news", "00:51.3", "zoom-in", dur=2.6, **ARCH), ndr("22:32"), V("wvu_news", "00:42.3", "pan-left", dur=3.4, **ARCH)]),
    seg("Comment un laboratoire de Virginie-Occidentale a-t-il fait tomber le plus grand constructeur automobile du monde ?",
        [V("wolfsburg_factory", "00:55", "zoom-in", letterbox=True)]),
    {"duration": 5, "transition": "fade",
     "visual": {"type": "title", "title": "Le mensonge de Volkswagen", "subtitle": "Dieselgate : l'enquête",
                "bg": V("wolfsburg_factory", "01:33")}},
]

ch1 = [
    chapter(1, "Le pari du « Clean Diesel »", ndr("07:36")),
    seg("Wolfsburg, en Basse-Saxe. Une ville construite autour d'une usine, et une usine grande comme une ville. "
        "C'est ici que bat le cœur de Volkswagen.",
        [V("wolfsburg_factory", "00:15", "drift"), V("wolfsburg_factory", "01:06", "pan-left"), ndr("07:40", "pan-right", grade="archive")],
        [lt("Wolfsburg", "Siège de Volkswagen, Allemagne", 0.8, 3.5)]),
    seg("En deux-mille-sept, un nouveau patron prend les commandes : Martin Winterkorn. Un ingénieur perfectionniste, réputé connaître "
        "chaque vis de chaque voiture. Il fixe un cap : faire de Volkswagen le numéro un mondial avant deux-mille-dix-huit. "
        "Devant Toyota. Devant General Motors.",
        [ndr("06:32", "drift"), ndr("16:17", dur=2.8), ndr("23:53", "zoom-in", grade="archive"), ndr("08:12", "pan-left")],
        [lt("Martin Winterkorn", "PDG du groupe Volkswagen (2007-2015)", 0.8, 4)]),
    seg("Pour y arriver, il lui manque un marché : les États-Unis. Les Américains boudent la marque. Volkswagen y vend peu, et cher.",
        [ndr("00:22", "drift"), V("stock_plunge", "00:03", "zoom-in", **ARCH), V("stock_plunge", "00:08", "pan-right", **ARCH)]),
    seg("Sa carte maîtresse, c'est le diesel. Un moteur sobre et puissant, que l'Europe adore. Volkswagen le vend aux Américains "
        "comme une alternative écologique à l'hybride : le « Clean Diesel », le diesel propre.",
        [V("defeat_device_explained", "01:09.3", "zoom-in", dur=2.6), V("defeat_device_explained", "00:17.2", "drift", dur=2.0),
         V("clean_diesel_ads_2", "00:27.2", "static", dur=2.6), ndr("29:41", "drift")]),
    seg("Les publicités s'enchaînent. Dans l'une d'elles, trois dames âgées se disputent dans une Golf.",
        [V("clean_diesel_ads", "00:02.2", "zoom-in", dur=2.0), V("clean_diesel_ads", "00:04.2", "drift")]),
    bite("clean_diesel_ads", 11.6, 14.4, "Ça, c'était avant. On est en 2015 !", visual=V("clean_diesel_ads", 11.6, "static")),
    seg("Pour le prouver, l'une d'elles frotte une écharpe blanche contre le pot d'échappement. L'écharpe ressort immaculée.",
        [V("clean_diesel_ads", "00:22.1", "zoom-in", dur=2.8), V("clean_diesel_ads", "00:25.1", "static", dur=1.9),
         V("clean_diesel_ads", "00:27.0", "static", dur=1.6), ndr("14:44", "drift")]),
    seg("Le pari marche. En deux-mille-neuf, la Jetta TDI est élue voiture verte de l'année aux États-Unis. "
        "Des centaines de milliers d'Américains achètent un diesel Volkswagen en pensant faire un geste pour la planète.",
        [ndr("16:36", "drift"), ndr("15:10", "drift"), ndr("15:52", "pan-left"), ndr("15:30", "drift")],
        [date("2009", 0.6, 2.5)]),
    seg("Mais il y a un problème, et à Wolfsburg, les ingénieurs le connaissent depuis le début. Les normes américaines sur les oxydes "
        "d'azote, les NOx, sont parmi les plus sévères au monde. Ces gaz irritent les poumons, et forment le smog des grandes villes.",
        [ndr("09:07", "drift"), V("defeat_device_explained", "01:56.3", "zoom-in", dur=2.8), ndr("14:25", "pan-right"), ndr("02:52")]),
    seg("Pour les respecter, il faut un système de dépollution coûteux et encombrant, qui consomme du carburant ou un additif. "
        "La voiture devient plus chère, et moins sobre. Exactement l'inverse de la promesse.",
        [V("defeat_device_explained", "00:24.3", "zoom-in", dur=3.5), V("defeat_device_explained", "00:28.3", "pan-left", dur=2.0), ndr("03:17", "drift")]),
    seg("Alors, dès la fin de l'année deux-mille-six, des ingénieurs du groupe choisissent une autre voie. "
        "Une solution simple, bon marché, et invisible.",
        [ndr("02:17", "drift"), ndr("03:40", "zoom-in"), ndr("04:20", "drift")],
        [date("NOVEMBRE 2006", 0.6, 2.8)]),
    seg("Une solution qui va tenir près de dix ans. Jusqu'à ce qu'elle croise la route d'une université de Virginie-Occidentale.",
        [ndr("05:27", "drift"), ndr("22:15", "pan-right", letterbox=True)]),
]

ch2 = [
    chapter(2, "Le test de Morgantown", ndr("22:18")),
    seg("Deux-mille-treize. L'ICCT, une organisation qui milite pour des transports moins polluants, veut comparer les diesels vendus "
        "en Europe et aux États-Unis. Son raisonnement : si les modèles américains sont propres, l'Europe peut faire mieux.",
        [V("defeat_device_explained", "00:30.3", "drift", dur=2.8), ndr("33:43", "zoom-in"), V("defeat_device_explained", "02:07.2", "drift", dur=2.8)],
        [date("2013", 0.6, 2.5)]),
    seg("Pour mesurer les émissions en conditions réelles, elle lance un appel d'offres. Le contrat est minuscule : "
        "soixante-dix mille dollars.",
        [V("wvu_news", "00:46.3", "zoom-in", dur=3.5, **ARCH), V("wvu_researchers", "06:30", "zoom-in")],
        [stat(70000, "budget de l'étude", suffix=" $", position="right", at=2.0, dur=3.8)]),
    seg("Il est remporté par un petit laboratoire de l'université de Virginie-Occidentale, à Morgantown : le CAFEE. "
        "Ses chercheurs travaillent d'habitude sur les moteurs de camions.",
        [V("wvu_news", "00:33", "pan-left", **ARCH), V("wvu_researchers", "05:51", "zoom-in"), ndr("18:15", "drift")],
        [lt("Morgantown", "Université de Virginie-Occidentale (WVU)", 0.8, 3.5)]),
    seg("L'équipe se procure trois voitures : une Jetta, une Passat, et un BMW X5. Dans le coffre, elle installe un appareil de mesure "
        "portable, alimenté par un générateur. Un tuyau relie le pot d'échappement à ce laboratoire roulant.",
        [ndr("22:38", "zoom-in"), ndr("22:48", "drift"), ndr("22:57", "drift"), ndr("23:10", "zoom-in")]),
    seg("Arvind Thiruvengadam et ses collègues prennent la route. Le centre de Los Angeles, San Diego. Puis un trajet bien plus long.",
        [ndr("14:30", "drift"), V("defeat_device_explained", "01:12.3", "drift", dur=3.5), V("defeat_device_explained", "01:16.3", "pan-right", dur=3.5)]),
    bite("wvu_researchers", 422.9, 439.6,
         "On s'est dit : on va rouler de Los Angeles à Seattle, aller-retour. Un trajet éprouvant, sans place dans la voiture, "
         "le matériel prenait tout. On ne pouvait pas incliner les sièges. On est restés comme ça pendant vingt-quatre heures.",
         overlays=[lt("Arvind Thiruvengadam", "Chercheur au CAFEE (WVU)", 0.6, 4)],
         visual=V("wvu_researchers", 422.9, "zoom-in")),
    seg("Pendant ce temps, un autre membre de l'équipe teste les mêmes voitures en laboratoire, sur un banc à rouleaux du CARB, "
        "l'agence californienne de l'air. Là, tout est parfait : les émissions sont quasi nulles.",
        [ndr("27:33", "drift"), ndr("18:50", "zoom-in"), ndr("23:20", "drift")]),
    seg("Mais sur la route, les courbes s'envolent.", [ndr("32:41", "zoom-in")]),
    bite("wvu_researchers", 666.7, 679.8,
         "Quand je l'ai rejoint pour les essais sur route en Californie, je lui ai demandé : on ne voit pas cette tendance proche de zéro "
         "que tu observes. Est-ce qu'on fait quelque chose de travers ?",
         visual=V("wvu_researchers", 666.7, "zoom-out")),
    seg("Les chercheurs pensent d'abord à une erreur. Ils vérifient leurs appareils. Ils refont les mesures. Encore. Et encore. "
        "Le résultat ne change pas.",
        [ndr("23:02", "drift"), V("wvu_researchers", "10:00", "zoom-in"), ndr("32:45", "pan-left"), ndr("33:01", "drift")]),
    seg("Sur la route, la Jetta rejette jusqu'à trente-cinq fois la limite américaine d'oxydes d'azote. La Passat, jusqu'à vingt fois. "
        "La BMW, elle, reste dans les clous.",
        [V("defeat_device_explained", "01:24.3", "drift", dur=3.6,
           overlays=[stat(35, "la limite de NOx · Jetta", prefix="× ", position="center", at=0.4, dur=3.8)]),
         V("clean_diesel_ads_2", "00:02.2", "zoom-in",
           overlays=[stat(20, "la limite de NOx · Passat", prefix="× ", position="right", at=0.3, dur=3.2)]),
         ndr("01:30", "drift")]),
    seg("En mai deux-mille-quatorze, l'équipe présente ses résultats lors d'une conférence. Elle ne cite aucune marque, "
        "et n'accuse personne.",
        [V("wvu_researchers", "01:40", "drift"), ndr("21:35", "drift")],
        [date("MAI 2014", 0.6, 2.8)]),
    bite("wvu_news", 55.3, 61.6,
         "Nous ne tirerions jamais la moindre conclusion à partir de deux véhicules. Nous avons présenté ce que nous avons vu.",
         overlays=[lt("Équipe du CAFEE", "Université de Virginie-Occidentale", 0.5, 3.5)],
         visual=V("wvu_news", 55.3, "static", **ARCH)),
    seg("Mais dans la salle, des employés de Volkswagen écoutent. Et le rapport atterrit sur le bureau des régulateurs.",
        [ndr("21:45", "drift"), ndr("27:40", "zoom-in")]),
]

ch3 = [
    chapter(3, "Le mensonge", ndr("31:18")),
    seg("Le CARB ouvre une enquête. Ses ingénieurs interrogent Volkswagen. La réponse : un problème technique, rien de plus.",
        [ndr("28:31", "drift"), ndr("26:50", "zoom-in"), ndr("28:40", "drift")],
        [lt("Stanley Young", "Agence californienne de l'air (CARB)", 0.6, 3.5)]),
    seg("En décembre deux-mille-quatorze, le constructeur lance un rappel pour mettre à jour le logiciel de près d'un demi-million "
        "de voitures. Les nouveaux tests ne montrent quasiment aucune amélioration.",
        [V("stock_plunge", "00:31", "zoom-in", **ARCH), ndr("29:22", "zoom-in"), ndr("31:25", "drift")],
        [date("DÉCEMBRE 2014", 0.6, 2.8)]),
    seg("Pire : selon les enquêteurs, cette mise à jour a servi à perfectionner la triche.",
        [ndr("31:47", "drift"), ndr("31:17", "zoom-in")],
        [lt("Thorsten Holz", "Expert en sécurité informatique, université de Bochum", 0.5, 3.2)]),
    seg("Car la vérité est dans le code. Le calculateur du moteur surveille des dizaines de paramètres : la vitesse, "
        "la durée de fonctionnement, la pression de l'air. Et surtout, la position du volant.",
        [ndr("32:05", "drift"), V("defeat_device_explained", "00:19.3", "zoom-in"), V("defeat_device_explained", "01:45.3", "static")]),
    seg("Sur un banc d'essai, personne ne tourne le volant. Le logiciel en déduit qu'il est testé, et active la dépollution à plein "
        "régime. Sur la route, il la réduit. La voiture peut alors polluer jusqu'à quarante fois plus.",
        [ndr("32:20", "zoom-in"), V("defeat_device_explained", "00:33.3", "drift", dur=2.0), V("defeat_device_explained", "00:35.5", "pan-left")],
        [{"type": "highlight", "at": 1.2, "dur": 2.6, "box": [28, 20, 44, 55], "label": "« Lenkwinkel » : l'angle du volant",
          "shape": "rect"}]),
    seg("Ce mécanisme a un nom : le « defeat device ». Un dispositif d'invalidation, strictement interdit par la loi américaine "
        "sur la qualité de l'air.",
        [ndr("33:08", "drift"), V("defeat_device_explained", "01:59.3", "pan-right")]),
    seg("Pendant plus d'un an, Volkswagen multiplie les explications techniques. Jusqu'à l'été deux-mille-quinze, où les régulateurs "
        "posent un ultimatum : pas d'explication, pas d'homologation pour les diesels de l'année suivante.",
        [ndr("35:21", "drift"), ndr("36:34", "zoom-in"), ndr("36:15", "drift")]),
    seg("Le 3 septembre, lors d'une réunion avec l'EPA et le CARB, les représentants de Volkswagen finissent par avouer.",
        [ndr("35:30", "drift"), V("wolfsburg_factory", "01:26", "zoom-in")],
        [date("3 SEPTEMBRE 2015", 0.6, 3)]),
    seg("Le vendredi 18 septembre, l'agence américaine de l'environnement rend l'affaire publique.",
        [ndr("39:53", "zoom-in"), ndr("40:23", "drift"), V("epa_announcement", "00:47", "zoom-in", **ARCH)],
        [date("18 SEPTEMBRE 2015", 0.6, 3)]),
    seg("Quatre cent quatre-vingt-deux mille voitures sont concernées aux États-Unis. Quatre jours plus tard, Volkswagen l'admet : "
        "il y en a onze millions dans le monde.",
        [V("stock_plunge", "00:13", "drift", dur=4.5,
           overlays=[stat(482000, "voitures aux États-Unis", position="right", at=0.4, dur=3.6)]),
         V("wolfsburg_factory", "00:28", "zoom-in",
           overlays=[stat(11000000, "voitures dans le monde", position="center", at=0.3, dur=4)])]),
    seg("À Wolfsburg, Martin Winterkorn enregistre une déclaration vidéo.", [ndr("06:08", "zoom-in")]),
    bite("winterkorn_apology", 61.1, 73.9,
         "Je suis infiniment désolé que nous ayons trahi cette confiance. Je présente mes excuses les plus sincères à nos clients, "
         "aux autorités et à l'ensemble du public pour ce comportement fautif.",
         overlays=[date("22 SEPTEMBRE 2015", 0.4, 3)], visual=V("winterkorn_apology", 61.1, "zoom-in", **ARCH)),
    seg("Le lendemain, il démissionne. Il assume la responsabilité du scandale, mais affirme n'avoir rien su de la fraude.",
        [ndr("42:16", "drift"), ndr("42:40", "zoom-in")],
        [date("23 SEPTEMBRE 2015", 0.6, 3)]),
]

ch4 = [
    chapter(4, "L'addition", ndr("41:49")),
    seg("Sur les marchés, la sanction est immédiate. Le lundi 21 septembre, l'action Volkswagen perd près d'un cinquième de sa valeur. "
        "En quelques jours, elle abandonne environ un tiers.",
        [ndr("41:50", "drift", dur=4.6,
             overlays=[stat(18.6, "en une séance · 21 septembre 2015", prefix="− ", suffix=" %", decimals=1, position="center",
                            at=0.4, dur=3.8)]),
         ndr("41:36", "zoom-in"), V("stock_plunge", "00:25", "drift", **ARCH)]),
    seg("Le 8 octobre, Michael Horn est convoqué devant une commission de la Chambre des représentants.",
        [V("horn_hearing", "00:17.5", "drift", **ARCH), V("horn_hearing", "00:08", "zoom-in", **ARCH)],
        [date("8 OCTOBRE 2015 · WASHINGTON", 0.6, 3)]),
    bite("horn_hearing", 151.4, 161.5,
         "… contenaient un dispositif d'invalidation, sous la forme d'un logiciel caché, capable de reconnaître si le véhicule roulait "
         "dans un laboratoire d'essai ou sur la route.",
         overlays=[lt("Michael Horn", "PDG de Volkswagen of America", 0.5, 4)], visual=V("horn_hearing", 151.4, "zoom-in", **ARCH)),
    seg("Sa ligne de défense : la fraude serait l'œuvre de quelques ingénieurs du logiciel, qui auraient agi seuls. "
        "Les élus n'y croient pas.",
        [V("horn_hearing", "00:37.5", "zoom-in", **ARCH), V("horn_hearing", "03:50", "drift", **ARCH)]),
    bite("horn_hearing", 203.6, 211.5,
         "Ces événements sont profondément troublants. Je ne pensais pas qu'une telle chose était possible au sein du groupe Volkswagen.",
         visual=V("horn_hearing", 203.6, "zoom-in", **ARCH)),
    seg("La justice américaine, elle, remonte la chaîne. En janvier deux-mille-dix-sept, Volkswagen plaide coupable. "
        "Le groupe accepte de payer quatre milliards trois cents millions de dollars d'amendes.",
        [V("schmidt_sentencing", "00:39.8", "zoom-in", dur=4.2, **ARCH), V("schmidt_sentencing", "00:11.5", "drift", dur=5.5, **ARCH), ndr("42:25", "drift")],
        [date("JANVIER 2017", 0.6, 2.6), stat(4.3, "d'amendes pénales et civiles", suffix=" Md$", decimals=1, position="right",
                                               at=4.0, dur=3.5)]),
    seg("Les cadres tombent un à un. James Liang, un ingénieur qui a participé à la conception du logiciel, écope de quarante mois de "
        "prison. Oliver Schmidt, ancien responsable des questions environnementales de Volkswagen aux États-Unis, est arrêté à Miami, "
        "à la fin de ses vacances.",
        [V("news_report_fr", "03:52", "zoom-in"), V("schmidt_sentencing", "00:03", "zoom-in", **ARCH),
         V("schmidt_sentencing", "00:27", "zoom-in", **ARCH)]),
    bite("schmidt_sentencing", 17.8, 25.5,
         "Le juge a donné à Schmidt exactement ce que demandait l'accusation : sept ans de prison. Une peine très, très lourde.",
         overlays=[lt("Oliver Schmidt", "Condamné à 7 ans de prison (décembre 2017)", 0.5, 4)],
         visual=V("schmidt_sentencing", 17.8, "zoom-in", **ARCH)),
    seg("En Allemagne, l'ancien patron d'Audi, Rupert Stadler, est condamné en deux-mille-vingt-trois à un an et neuf mois de prison "
        "avec sursis. C'est le premier membre du directoire du groupe à être condamné.",
        [V("news_report_fr", "04:12", "zoom-in"), ndr("43:31", "drift")]),
    seg("Et en deux-mille-dix-huit, le New York Times révèle une autre affaire. Un institut financé par Volkswagen, Daimler et BMW a "
        "exposé dix singes aux gaz d'échappement d'une Beetle diesel. Une Beetle équipée, elle aussi, du logiciel truqué.",
        [V("stock_plunge", "00:18.5", "zoom-in", **ARCH), V("news_report_fr", "02:50", "zoom-in"), ndr("11:12", "drift")],
        [date("2018", 0.6, 2.5)]),
    seg("Au total, le scandale a coûté au groupe plus de trente milliards d'euros.",
        [V("wolfsburg_factory", "01:21", "drift",
           overlays=[stat(30, "coût total pour Volkswagen", prefix="+ ", suffix=" Md€", position="center", at=0.3, dur=3.8)])]),
    seg("Le coût humain, lui, est plus difficile à mesurer. Des chercheurs du MIT estiment que ces émissions en trop pourraient "
        "provoquer environ mille deux cents morts prématurées en Europe.",
        [ndr("00:30", "drift"), ndr("09:12", "pan-left"), ndr("14:32", "drift")]),
]

conclusion = [
    chapter(5, "Dix ans après", V("vw_ev_pivot", "01:22")),
    seg("Dix ans plus tard, le paysage a changé. En Europe, les voitures sont désormais homologuées avec des tests sur route, "
        "en conditions réelles. Et le diesel s'est effondré dans les ventes de voitures neuves.",
        [V("defeat_device_explained", "02:10.3", "drift", dur=2.5), ndr("43:40", "drift"), ndr("01:08", "pan-right")]),
    seg("Volkswagen, lui, a choisi de tourner la page en misant sur l'électrique. En deux-mille-dix-neuf, à Francfort, le groupe "
        "présente l'ID.3, une voiture pensée comme le symbole d'un nouveau départ.",
        [V("vw_ev_pivot", "01:25", "drift"), V("vw_ev_pivot", "04:01", "zoom-in"), V("vw_ev_pivot", "05:20", "drift")],
        [date("SEPTEMBRE 2019 · FRANCFORT", 0.6, 3)]),
    seg("Mais le passé n'est pas soldé. En mai deux-mille-vingt-cinq, à Braunschweig, quatre anciens cadres sont reconnus coupables "
        "de fraude. Deux sont condamnés à de la prison ferme.",
        [ndr("20:49", "zoom-in"), ndr("20:55", "drift")],
        [date("MAI 2025 · BRAUNSCHWEIG", 0.6, 3)]),
    seg("Martin Winterkorn, lui, n'a toujours pas été jugé. Son procès a été suspendu pour raisons de santé.",
        [ndr("16:26", "zoom-in"), V("winterkorn_apology", "00:30", "zoom-in", **ARCH)]),
    bite("winterkorn_apology", 44.7, 50.7,
         "Et pour être clair : des manipulations chez Volkswagen, cela ne doit plus jamais se reproduire.",
         visual=V("winterkorn_apology", 44.7, "static", **ARCH)),
    seg("Tout est parti d'un petit laboratoire, de trois voitures, et de soixante-dix mille dollars.",
        [V("wvu_researchers", "03:00", "zoom-in"), V("wvu_researchers", "09:00", "drift")], transition="fade"),
    seg("Ces chercheurs voulaient montrer que le diesel pouvait être propre. "
        "Ils ont mis au jour l'une des plus grandes fraudes de l'histoire de l'industrie.",
        [V("wolfsburg_factory", "01:41", "zoom-out", letterbox=True)], pad=1.5),
    {"duration": 4, "transition": "fade", "visual": V("wolfsburg_factory", "01:56", "static", letterbox=True)},
]

timeline = {
    "meta": {
        "title": "Le mensonge de Volkswagen",
        "lang": "fr", "fps": 30, "width": 1920, "height": 1080,
        "voice": {"engine": "edge", "name": "fr-FR-HenriNeural", "rate": "-4%"},
        "music": {"src": "music/dieselgate_theme_loop.mp3", "volume": 0.22},
        "captions": True,
        "grade": "cinematic",
        "style": {"accent": "#E8B04B", "text": "#F5F1E8", "headingFont": "PlayfairDisplay", "grain": 0.35, "vignette": 0.5},
    },
    "chapters": [
        {"title": "Cold open", "segments": cold_open},
        {"title": "Le pari du Clean Diesel", "segments": ch1},
        {"title": "Le test de Morgantown", "segments": ch2},
        {"title": "Le mensonge", "segments": ch3},
        {"title": "L'addition", "segments": ch4},
        {"title": "Dix ans après", "segments": conclusion},
    ],
}

out = Path(__file__).with_name("timeline.json")
out.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n")
words = sum(len(s.get("vo", "").split()) for c in timeline["chapters"] for s in c["segments"])
print(f"timeline -> {out}  ({words} mots de narration)")
