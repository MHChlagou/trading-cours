#!/usr/bin/env python3
"""Génère l'arborescence du cours (dossiers, _category_.json, stubs de chapitres).

Règle absolue : ne réécrit JAMAIS un fichier existant. On peut donc relancer
le script à tout moment sans risque pour les chapitres déjà rédigés.
"""
import json
import glob
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs"))

# (slug, titre, plan prévu)
LEVELS = [
    {
        "dir": "00-niveau-0-fondations",
        "label": "Niveau 0 · Fondations",
        "position": 1,
        "desc": "Comprendre les marchés, les ordres et l'écosystème avant de risquer un euro.",
        "chapters": [
            ("quest-ce-que-le-trading", "Qu'est-ce que le trading ?", []),
            ("les-classes-dactifs", "Les classes d'actifs : actions, forex, futures, options, crypto, commodities", [
                "Panorama de chaque marché : qui y échange quoi, et pourquoi",
                "Tailles de contrats, horaires et liquidité comparés",
                "Coûts et effet de levier de chaque classe d'actifs",
                "Quel marché pour quel profil et quel capital de départ",
                "Tableau récapitulatif à conserver",
            ]),
            ("market-mechanics", "Market mechanics : bid, ask, spread, liquidité, slippage", [
                "Le carnet d'ordres et la formation du prix",
                "Bid, ask et spread : qui paie quoi",
                "La liquidité selon les heures et les instruments",
                "Le slippage mesuré sur des cas concrets",
                "Conséquences directes sur les stratégies court terme",
            ]),
            ("les-types-dordres", "Les types d'ordres", [
                "Market, limit, stop et stop-limit : usages et pièges",
                "Ordres OCO et bracket pour encadrer un trade",
                "Time in force : GTC, IOC, FOK",
                "Les erreurs d'exécution classiques du débutant",
                "Exercices de placement d'ordres sur scénarios",
            ]),
            ("choisir-son-broker", "Choisir son broker", [
                "Régulation et sécurité des fonds : AMF, FCA, NFA, CFTC",
                "La structure de coûts réelle : commissions, spreads, financement",
                "Qualité d'exécution et modèle du broker",
                "Futures, CFD, actions au comptant : ce que change le véhicule",
                "Grille d'évaluation imprimable pour comparer",
            ]),
            ("infrastructure-de-trading", "Infrastructure de trading", [
                "Matériel : ce qui est utile, ce qui est du gadget",
                "Plateformes : TradingView, Sierra Chart, NinjaTrader, MT5",
                "Flux de données et abonnements nécessaires",
                "Organisation du poste et des espaces de travail",
                "Plan de secours en cas de panne pendant une position",
            ]),
        ],
    },
    {
        "dir": "01-niveau-1-risque",
        "label": "Niveau 1 · Risque et maths du trading",
        "position": 2,
        "desc": "La compétence non négociable : survivre assez longtemps pour laisser l'avantage s'exprimer.",
        "chapters": [
            ("pourquoi-la-plupart-perdent", "Pourquoi la plupart des traders perdent", [
                "Ce que disent les statistiques publiées par les brokers",
                "Espérance négative par défaut : le rôle des coûts",
                "Sur-risque, sur-trading et absence de process",
                "Le risque comme cœur du métier, pas comme contrainte",
                "Les règles de survie adoptées dès aujourd'hui",
            ]),
            ("position-sizing", "Position sizing", [
                "Le risque fixe en pourcentage du compte",
                "Calculer la taille de position à partir du stop",
                "Adapter la taille aux futures, au forex et à la crypto",
                "Kelly et fraction de Kelly : intérêt et dangers",
                "Calculateur pas à pas et cas pratiques",
            ]),
            ("r-multiples-et-expectancy", "R-multiples et expectancy", [
                "Définir le R et penser tous ses trades en R",
                "La distribution des résultats d'un système",
                "Calculer l'expectancy et l'interpréter",
                "Expectancy par setup et par contexte",
                "Lire un relevé de trades comme un professionnel",
            ]),
            ("drawdown-et-risk-of-ruin", "Drawdown et risk of ruin", [
                "Drawdown maximal, durée et profondeur",
                "Les séries de pertes statistiquement attendues",
                "La probabilité de ruine et ses paramètres",
                "Dimensionner son compte et son risque en conséquence",
                "Règles de réduction du risque en période difficile",
            ]),
            ("correlation-et-portfolio-risk", "Corrélation et risque de portefeuille", [
                "Corrélations entre actifs : mesurer plutôt que supposer",
                "L'exposition agrégée réelle de positions simultanées",
                "Le heat total du portefeuille et ses limites",
                "Diversification utile contre diversification illusoire",
                "Construire et lire une matrice de corrélation",
            ]),
            ("money-management-avance", "Money management avancé", [
                "Pyramider une position gagnante proprement",
                "Scaling in et scaling out : quand et pourquoi",
                "Budgets de risque par jour, par semaine, par session",
                "Ajuster le risque selon la courbe d'equity",
                "Plans de progression du risque dans le temps",
            ]),
        ],
    },
    {
        "dir": "02-niveau-2-analyse-technique",
        "label": "Niveau 2 · Analyse technique",
        "position": 3,
        "desc": "Lire un graphique proprement : structure, niveaux, volatilité et volume.",
        "chapters": [
            ("lire-un-graphique", "Lire un graphique : bougies et unités de temps", [
                "Anatomie d'une bougie et ce qu'elle raconte",
                "Choisir ses unités de temps selon son horizon",
                "Bougies en contexte plutôt que figures isolées",
                "Les pièges des patterns appris par cœur",
                "Protocole de lecture d'un graphique vierge",
            ]),
            ("market-structure", "Market structure", [
                "Swings : plus hauts et plus bas significatifs",
                "Tendance, range et phases de transition",
                "Structure interne et structure externe",
                "Définir des invalidations objectives",
                "Exercice : annoter dix graphiques vierges",
            ]),
            ("analyse-multi-timeframe", "Analyse multi-timeframe", [
                "La hiérarchie des unités de temps",
                "Du contexte à l'exécution : la routine top-down",
                "Gérer les signaux alignés et les signaux en conflit",
                "Combien d'unités de temps utiliser, et lesquelles",
                "Les erreurs multi-timeframe les plus coûteuses",
            ]),
            ("supports-et-resistances", "Supports et résistances", [
                "Identifier les niveaux horizontaux majeurs",
                "Des zones plutôt que des lignes",
                "Le changement de polarité support-résistance",
                "Confluence avec la structure et les niveaux ronds",
                "Nettoyer son graphique : moins de niveaux, mieux choisis",
            ]),
            ("volatilite-et-atr", "Volatilité et ATR", [
                "Mesurer la volatilité et ses régimes",
                "L'ATR pour dimensionner stops et objectifs",
                "Adapter la taille de position à la volatilité",
                "Expansion et contraction : ce qu'elles annoncent",
                "Cas pratiques sur indices, or et forex",
            ]),
            ("le-volume", "Le volume", [
                "Ce que le volume mesure vraiment selon les marchés",
                "Confirmations et divergences prix-volume",
                "Le volume aux niveaux clés",
                "Volume relatif et anomalies",
                "Les limites du volume en forex spot",
            ]),
        ],
    },
    {
        "dir": "03-niveau-3-prix-avance",
        "label": "Niveau 3 · Prix avancé : SMC, ICT, Wyckoff",
        "position": 4,
        "desc": "Lire les intentions derrière le prix : liquidité, déséquilibres et campagnes d'accumulation.",
        "chapters": [
            ("introduction-aux-smc", "Introduction aux Smart Money Concepts", [
                "La logique de la liquidité : pourquoi le prix va la chercher",
                "Qui est en face de vous et comment il exécute",
                "La carte des concepts SMC et leur articulation",
                "SMC et analyse technique classique : rupture ou continuité",
                "Le plan de progression de ce niveau",
            ]),
            ("liquidite-et-liquidity-sweeps", "Liquidité et liquidity sweeps", [
                "Où dort la liquidité : stops, equal highs, equal lows",
                "Sweep contre cassure : les critères de distinction",
                "La réaction post-sweep et ce qu'elle valide",
                "Sweeps de session et sweeps de niveaux hebdomadaires",
                "Exemples annotés sur NQ et EUR/USD",
            ]),
            ("displacement-et-fair-value-gaps", "Displacement et Fair Value Gaps", [
                "Reconnaître un displacement significatif",
                "Définition stricte d'un FVG et conditions de validité",
                "Le FVG comme zone d'intérêt, pas comme signal",
                "Mitigation, inversion et invalidation d'un FVG",
                "FVG multi-timeframe et confluence",
            ]),
            ("order-blocks-et-breakers", "Order Blocks et Breaker Blocks", [
                "Définition et critères de validité d'un order block",
                "Order blocks haussiers et baissiers : sélection",
                "Raffiner un order block sur unité de temps inférieure",
                "Breaker blocks et changements de polarité",
                "Hiérarchie pratique entre OB, FVG et sweep",
            ]),
            ("bos-choch-et-structure", "Break of Structure et CHoCH", [
                "BOS : la continuation confirmée",
                "CHoCH : le premier indice de retournement",
                "Cassures valides contre cassures de liquidité",
                "La structure SMC complète sur un cycle entier",
                "Protocole d'annotation systématique",
            ]),
            ("la-boite-a-outils-ict", "La boîte à outils ICT", [
                "Killzones et heures qui concentrent les mouvements",
                "Power of Three : accumulation, manipulation, distribution",
                "Premium, discount et OTE",
                "Modèles de session : le cas du silver bullet",
                "Assembler les outils ICT sans en faire une religion",
            ]),
            ("wyckoff-fondamentaux", "Wyckoff : fondamentaux", [
                "Les trois lois de Wyckoff",
                "Accumulation et distribution : les schémas de base",
                "Les phases A à E et leurs événements",
                "Springs et upthrusts",
                "Effort contre résultat : lire le volume avec Wyckoff",
            ]),
            ("wyckoff-avance", "Wyckoff avancé", [
                "Schématiques détaillées et variantes réelles",
                "Le composite man comme grille de lecture",
                "Réaccumulation et redistribution",
                "Projections d'objectifs",
                "Faire dialoguer Wyckoff et SMC moderne",
            ]),
        ],
    },
    {
        "dir": "04-niveau-4-order-flow",
        "label": "Niveau 4 · Order flow et volume avancé",
        "position": 5,
        "desc": "Voir les transactions derrière les bougies : profils, footprint, delta et open interest.",
        "chapters": [
            ("volume-profile-bases", "Volume Profile : les bases", [
                "Construction d'un profil de volume",
                "POC, value area, VAH et VAL",
                "Les formes de profils et leur signification",
                "Profils de session et profils de range",
                "Premiers usages : niveaux et contexte",
            ]),
            ("volume-profile-avance", "Volume Profile avancé", [
                "Profils composites sur plusieurs semaines",
                "Naked POC et niveaux résiduels",
                "Migration de la value area et lecture de tendance",
                "Profils d'événements : news, ouvertures, expirations",
                "Intégrer le profil à la structure et aux SMC",
            ]),
            ("footprint-et-delta", "Footprint et delta", [
                "Lire un graphique footprint cellule par cellule",
                "Delta, delta cumulé et leurs limites",
                "Absorption et déséquilibres agressifs",
                "Divergences de delta aux extrêmes",
                "Exemples décortiqués sur ES",
            ]),
            ("dom-et-tape-reading", "DOM et tape reading", [
                "La profondeur de marché en temps réel",
                "Icebergs, spoofing et fausses tailles",
                "Lire le tape sur les moments clés",
                "Utiliser le DOM pour affiner l'exécution",
                "Ce que le retail peut et ne peut pas en tirer",
            ]),
            ("open-interest-et-funding", "Open interest et funding", [
                "L'open interest sur les futures et sa lecture",
                "Prix, volume, OI : la grille combinée",
                "Le funding des perpetuals crypto",
                "Positionnement extrême et squeezes",
                "Signaux d'alerte et cas historiques",
            ]),
        ],
    },
    {
        "dir": "05-niveau-5-macro",
        "label": "Niveau 5 · Macro et fondamental",
        "position": 6,
        "desc": "Le contexte qui pilote les tendances : taux, dollar, cycles et positionnement.",
        "chapters": [
            ("macroeconomie-pour-traders", "Macroéconomie pour traders", [
                "Le cycle économique et ses phases",
                "Inflation, emploi, croissance : les données qui comptent",
                "Lire un rapport macro en dix minutes",
                "Du chiffre macro au mouvement de prix",
                "Construire sa veille macro hebdomadaire",
            ]),
            ("banques-centrales-et-taux", "Banques centrales et taux", [
                "Fed, BCE, BoJ : mandats et fonctionnement",
                "Les outils : taux directeurs, QE, QT, forward guidance",
                "La courbe des taux et ses messages",
                "Ce que le marché anticipe déjà : futures de taux",
                "Réactions typiques des actifs aux décisions",
            ]),
            ("analyse-intermarket", "Analyse intermarket", [
                "Obligations, dollar, actions, matières premières : le carré directeur",
                "Les corrélations structurelles et leurs ruptures",
                "Risk-on, risk-off en pratique",
                "Le DXY comme boussole des marchés",
                "Construire un tableau de bord intermarket",
            ]),
            ("calendrier-economique-et-news", "Calendrier économique et news", [
                "Hiérarchiser les publications : ce qui bouge vraiment les prix",
                "CPI, NFP, FOMC : anatomie des grandes annonces",
                "Trader les news ou s'en protéger : deux écoles",
                "Le comportement type du prix autour des annonces",
                "Un protocole news écrit et non négociable",
            ]),
            ("cot-et-positionnement", "COT et positionnement", [
                "Lire le rapport COT de la CFTC",
                "Commercials, large speculators, small traders",
                "Les extrêmes de positionnement et leur exploitation",
                "Construire un index COT",
                "Les limites du COT et son bon horizon",
            ]),
            ("seasonality", "Saisonnalité, et sa combinaison avec le COT", [
                "Les saisonnalités robustes par classe d'actifs",
                "Construire une carte saisonnière fiable",
                "Combiner saisonnalité et positionnement COT",
                "Fenêtres statistiques et taille d'échantillon",
                "Les pièges : cherry-picking et années atypiques",
            ]),
            ("sentiment-et-regimes", "Sentiment et détection de régime", [
                "Les indicateurs de sentiment et leur lecture contrarian",
                "VIX et volatilité implicite comme thermomètres",
                "Définir un régime de marché : tendance, range, stress",
                "Une matrice de régimes opérationnelle",
                "Adapter ses setups au régime en cours",
            ]),
        ],
    },
    {
        "dir": "06-niveau-6-marches",
        "label": "Niveau 6 · Marchés spécifiques",
        "position": 7,
        "desc": "Les terrains de jeu en détail : indices futures, métaux, énergie, forex, options et crypto.",
        "chapters": [
            ("futures-es-et-nq", "Futures indices : ES et NQ", [
                "Spécifications des contrats, ticks et marges",
                "Sessions, heures clés et volumes types",
                "Personnalité de l'ES contre personnalité du NQ",
                "Les niveaux qui comptent chaque jour",
                "Une journée type décortiquée de bout en bout",
            ]),
            ("or-et-petrole", "Or et pétrole", [
                "Les drivers fondamentaux de l'or et du brut",
                "GC et CL : contrats, horaires, pièges",
                "Stocks EIA, OPEP et géopolitique",
                "Corrélations avec le dollar et les taux réels",
                "Profils de volatilité et conséquences pratiques",
            ]),
            ("sessions-forex", "Forex : sessions et paires", [
                "Sydney, Tokyo, Londres, New York : la journée du forex",
                "Le comportement du prix par session",
                "Paires majeures, croisées et exotiques",
                "Spreads, rollover et heures à éviter",
                "Construire une stratégie autour d'une session",
            ]),
            ("options-et-greeks", "Options et les Greeks", [
                "Calls, puts et profils de gains",
                "Delta, gamma, theta, vega : ce que chacun mesure",
                "La volatilité implicite et son rôle central",
                "Usages concrets pour un trader directionnel",
                "L'empreinte du marché d'options sur les indices",
            ]),
            ("specificites-crypto", "Spécificités crypto", [
                "La microstructure des exchanges crypto",
                "Perpetuals, funding et bases",
                "Les liquidations en cascade et leurs signatures",
                "Données on-chain utiles au trader",
                "Les risques propres : plateformes, week-ends, manipulation",
            ]),
        ],
    },
    {
        "dir": "07-niveau-7-strategie-quant",
        "label": "Niveau 7 · Stratégie, backtesting et quant",
        "position": 8,
        "desc": "Transformer une idée en système mesuré : setups, données, statistiques et code.",
        "chapters": [
            ("construire-une-strategie", "Construire une stratégie", [
                "De l'idée floue à la règle testable",
                "Contexte, signal, exécution : les trois blocs",
                "Critères d'entrée, de sortie et de gestion écrits",
                "La fiche de stratégie standard du cours",
                "Erreurs de conception les plus fréquentes",
            ]),
            ("setup-1-sweep-fvg", "Setup avancé 1 : sweep et FVG sur indices", [
                "Le contexte requis avant même de chercher le setup",
                "Le déclencheur précis, critère par critère",
                "Entrée, stop, objectifs et variantes",
                "La gestion active du trade",
                "Statistiques attendues et conditions d'invalidité",
            ]),
            ("setup-2-session-londres", "Setup avancé 2 : ouverture de Londres en forex", [
                "La logique de session derrière le setup",
                "Range asiatique, manipulation et vraie direction",
                "Conditions de validation et filtres",
                "Exécution, gestion et sorties",
                "Le journal spécifique de ce setup",
            ]),
            ("setup-3-swing-macro", "Setup avancé 3 : swing macro multi-jours", [
                "Le filtre de régime macro préalable",
                "La confluence COT et saisonnalité",
                "Le déclencheur technique d'entrée",
                "Pyramidage, sorties partielles et trailing",
                "Le suivi hebdomadaire de la position",
            ]),
            ("bibliotheque-de-setups", "Bibliothèque de setups", [
                "Des dizaines de setups classés par contexte de marché",
                "La fiche standardisée : conditions, déclencheur, gestion",
                "Quand chaque setup fonctionne, et quand il échoue",
                "Choisir trois setups et ignorer le reste",
                "Construire sa sélection personnelle",
            ]),
            ("backtesting-manuel", "Backtesting manuel", [
                "Le protocole bar par bar sans triche",
                "La taille d'échantillon minimale",
                "La feuille de collecte des trades",
                "Les mesures à enregistrer systématiquement",
                "Les biais du backtest manuel et leurs parades",
            ]),
            ("backtesting-python", "Backtesting en Python", [
                "Préparer et nettoyer des données OHLC",
                "Backtest vectorisé contre event-driven",
                "Simuler coûts, spread et slippage honnêtement",
                "Les métriques de sortie : expectancy, profit factor, drawdown",
                "Un script complet commenté, prêt à adapter",
            ]),
            ("stats-et-monte-carlo", "Statistiques avancées et Monte Carlo", [
                "La distribution réelle des rendements d'un système",
                "Intervalles de confiance sur l'expectancy",
                "La simulation Monte Carlo expliquée pas à pas",
                "Drawdown probable contre drawdown historique",
                "Taille d'échantillon et significativité",
            ]),
            ("overfitting-et-validation", "Overfitting et validation", [
                "La sur-optimisation et les degrés de liberté",
                "In-sample contre out-of-sample",
                "Le walk-forward en pratique",
                "Tests de robustesse : paramètres, marchés, périodes",
                "La checklist anti-overfitting du cours",
            ]),
            ("algo-et-ia", "Systèmes algorithmiques et IA", [
                "Automatiser une stratégie : architecture minimale",
                "Exécution, surveillance et garde-fous",
                "La recherche quantitative au quotidien",
                "Les usages réalistes de l'IA pour un trader",
                "Ce que l'IA ne fera pas à votre place",
            ]),
        ],
    },
    {
        "dir": "08-niveau-8-psychologie",
        "label": "Niveau 8 · Psychologie et process",
        "position": 9,
        "desc": "Le trader est le maillon faible du système : process, journal et données personnelles.",
        "chapters": [
            ("psychologie-du-trading", "Psychologie du trading", [
                "Les biais cognitifs qui coûtent le plus cher",
                "Tilt et revenge trading : détection précoce",
                "Peur, avidité, ennui : les trois saboteurs",
                "La discipline par le process, pas par la volonté",
                "Protocoles d'urgence en cas de dérapage",
            ]),
            ("journal-de-trading", "Le journal de trading professionnel", [
                "La structure d'un journal réellement utile",
                "Captures, annotations et contexte de chaque trade",
                "Tags et catégories pour l'analyse future",
                "La revue hebdomadaire pas à pas",
                "Modèles de journal fournis avec le cours",
            ]),
            ("performance-analytics", "Performance analytics", [
                "Les métriques par setup, par session, par contexte",
                "Courbe d'equity en R et sa lecture",
                "Trouver ses heures et ses jours profitables",
                "Détecter les fuites : où part le R perdu",
                "Construire son tableau de bord personnel",
            ]),
            ("routine-quotidienne", "La routine quotidienne", [
                "La préparation pré-marché en trente minutes",
                "L'exécution en séance : règles et limites",
                "Le débrief post-marché en dix minutes",
                "Hygiène de vie et capacité de décision",
                "La routine hebdomadaire et mensuelle",
            ]),
        ],
    },
    {
        "dir": "09-niveau-9-professionnalisation",
        "label": "Niveau 9 · Professionnalisation",
        "position": 10,
        "desc": "Assembler le tout : playbook, études de cas complètes et plan de progression.",
        "chapters": [
            ("construire-son-playbook", "Construire son Trading Playbook", [
                "La structure du playbook professionnel",
                "Les fiches de setups personnelles",
                "Règles de risque, de session et de news",
                "Les critères de revue et de mise à jour",
                "Un document vivant, pas un trophée",
            ]),
            ("etude-de-cas-futures", "Étude de cas 1 : de la macro à l'entrée sur NQ", [
                "Le contexte macro et le régime du jour",
                "L'analyse top-down complète",
                "La construction du scénario et des niveaux",
                "L'exécution, la gestion, la sortie",
                "Le débrief chiffré et les alternatives",
            ]),
            ("etude-de-cas-forex", "Étude de cas 2 : swing EUR/USD complet", [
                "Régime, intermarket et positionnement",
                "Les niveaux hebdomadaires retenus",
                "Le déclencheur et l'entrée",
                "La gestion sur plusieurs jours",
                "Les leçons et les variantes du scénario",
            ]),
            ("roadmap-30-60-90", "Roadmap 30, 60, 90 jours", [
                "Les objectifs de chaque phase",
                "Le volume de travail hebdomadaire réaliste",
                "Du paper trading au petit réel : critères de passage",
                "Les jalons mesurables et les points de contrôle",
                "Les erreurs qui font recommencer à zéro",
            ]),
            ("checklists-imprimables", "Checklists imprimables", [
                "Checklist de préparation pré-marché",
                "Checklist d'entrée en position",
                "Checklist de gestion et de sortie",
                "Checklist de revue hebdomadaire",
                "Toutes disponibles en version imprimable",
            ]),
            ("aller-plus-loin", "Aller plus loin : capital et carrière", [
                "Prop firms : promesses, règles et pièges",
                "Gérer un compte qui grossit",
                "Fiscalité : les points de vigilance à vérifier localement",
                "La formation continue du trader",
                "Communautés, mentors et signaux d'alarme",
            ]),
        ],
    },
]

STUB = """---
title: {title}
description: {desc}
---

# {plain_title}

:::info Chapitre en préparation
Ce chapitre sera livré lors de la rédaction du **{label}**. Le plan ci-dessous est contractuel : chaque point sera couvert avec graphiques annotés, trades décortiqués, exercices corrigés et quiz.
:::

## Plan prévu

{plan}
"""

EXAM = """---
title: {title}
sidebar_label: {sidebar_label}
---

# {plain_title}

:::info Examen en préparation
Cet examen sera activé une fois tous les chapitres du niveau rédigés.
Format prévu : 25 questions corrigées et une étude de cas notée. Score de passage : 80 %.
:::
"""


def exists(folder, index, slug):
    """Vrai si un fichier NN-slug.* existe déjà (md ou mdx)."""
    pattern = os.path.join(folder, "%02d-%s.*" % (index, slug))
    return len(glob.glob(pattern)) > 0


def write_if_missing(path, content):
    if os.path.exists(path):
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    created = 0
    for level in LEVELS:
        folder = os.path.join(ROOT, level["dir"])
        os.makedirs(folder, exist_ok=True)

        category = {
            "label": level["label"],
            "position": level["position"],
            "collapsed": True,
            "link": {
                "type": "generated-index",
                "slug": "/" + level["dir"].split("-", 1)[1],
                "description": level["desc"],
            },
        }
        cat_path = os.path.join(folder, "_category_.json")
        if write_if_missing(cat_path, json.dumps(category, ensure_ascii=False, indent=2) + "\n"):
            created += 1

        for i, (slug, title, plan) in enumerate(level["chapters"], start=1):
            if exists(folder, i, slug):
                continue
            path = os.path.join(folder, "%02d-%s.md" % (i, slug))
            plan_md = "\n".join("- " + p for p in plan) if plan else "- Plan à définir"
            content = STUB.format(
                title=json.dumps(title, ensure_ascii=False),
                desc=json.dumps(level["label"] + " : chapitre en préparation.", ensure_ascii=False),
                plain_title=title,
                label=level["label"],
                plan=plan_md,
            )
            if write_if_missing(path, content):
                created += 1

        # Examen de fin de niveau
        is_final = level["dir"].startswith("09-")
        exam_slug = "examen-final" if is_final else "examen"
        if not exists(folder, 99, exam_slug):
            exam_title = "Examen final : certification du cours" if is_final else "Examen · " + level["label"]
            exam_label = "Examen final" if is_final else "Examen du niveau"
            path = os.path.join(folder, "99-%s.md" % exam_slug)
            content = EXAM.format(
                title=json.dumps(exam_title, ensure_ascii=False),
                sidebar_label=json.dumps(exam_label, ensure_ascii=False),
                plain_title=exam_title,
            )
            if write_if_missing(path, content):
                created += 1

    print("Fichiers créés : %d (les fichiers existants ne sont jamais modifiés)" % created)


if __name__ == "__main__":
    main()
