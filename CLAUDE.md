# CLAUDE.md — Cours de trading (Docusaurus 3)

## Contexte

Site de cours de trading en français, 10 niveaux (N0 à N9), 63 chapitres, 10 examens.
Le squelette est complet et le build passe. Chaque chapitre non rédigé est un stub
contenant l'admonition `:::info Chapitre en préparation` et un « Plan prévu » contractuel.
Chaque examen non rédigé contient `:::info Examen en préparation`.

Référence de qualité obligatoire : `docs/00-niveau-0-fondations/01-quest-ce-que-le-trading.mdx`.
Tout nouveau chapitre doit lui ressembler en structure et en niveau d'exigence.

## Mission

Rédiger tous les fichiers encore en préparation. Un fichier est « à rédiger » si et
seulement si il contient l'une des deux admonitions ci-dessus. La mission est
reprenable : au démarrage, lister ces fichiers et reprendre au premier dans l'ordre.

## Ordre de travail

1. Niveau par niveau, N0 puis N1... jusqu'à N9. Dans un niveau : ordre des préfixes numériques.
2. Pour chaque chapitre : rédiger, puis `npm run build`, corriger toute erreur ou lien cassé, puis commit.
3. L'examen du niveau se rédige en dernier, après tous les chapitres du niveau.
4. Après chaque niveau : ajouter les nouveaux termes à `docs/10-annexes/02-glossaire.md` (sections alphabétiques existantes), puis commit.
5. S'arrêter en fin de niveau et rendre un bilan : chapitres rédigés, volume, état du build.

## Gabarit d'un chapitre (obligatoire)

- Renommer le stub `.md` en `.mdx` (même préfixe numérique, même slug : les URLs ne changent pas).
- Conserver le `title` du frontmatter ; réécrire la `description` (une phrase réelle du contenu).
- Couvrir CHAQUE point du « Plan prévu » du stub, puis supprimer l'admonition et la section plan.
- Longueur : 1 200 à 2 500 mots de théorie expliquée depuis zéro, jargon anglais conservé.
- 2 à 4 figures SVG annotées via `<Figure caption="Figure N · ...">`.
- 1 trade gagnant et 1 trade perdant via `<TradeExample>`, toujours présentés comme des reconstitutions pédagogiques.
- Un encadré `:::tip À retenir` de 3 à 5 puces.
- Au moins 2 `<Exercise>` avec `<Solution>` ; tous les calculs vérifiés à la main.
- Un `<Quiz>` d'au moins 5 questions ; `answer` est l'index de la bonne option, `explain` obligatoire.
- Une courte section « Prochain chapitre » en fin de fichier.
- Marchés à privilégier dans les exemples : futures ES/NQ, or, pétrole, forex, crypto.

Exceptions : les études de cas (N9) et le chapitre `checklists-imprimables` adaptent le
gabarit (quiz facultatif) ; le chapitre checklists est construit autour de composants
`<Checklist>` complets et imprimables.

## Examens

- Remplacer le stub `99-examen*.md` par un `.mdx`, conserver `title` et `sidebar_label`.
- 25 questions au total via `<Quiz>` (un bloc unique ou des blocs thématiques de 5), couvrant tout le niveau.
- Une étude de cas notée, corrigée via `<Exercise>` + `<Solution>`.
- Rappeler le score de passage : 80 %.

## Composants (globaux, aucun import nécessaire)

Voir les exemples d'appel dans `README.md` et le chapitre de référence.
Disponibles partout : `Figure`, `TradeExample`, `Exercise`, `Solution`, `Checklist`, `Quiz`.

## Contraintes MDX et SVG (le build casse sinon)

- Attributs JSX uniquement : `className`, `strokeWidth`, `fontSize`, `textAnchor`, `fontWeight`. Jamais `class=` ni `style="..."`.
- Pas de `<`, `>`, `{`, `}` bruts dans la prose : écrire « inférieur à », « supérieur à », ou mettre en code inline.
- SVG : `className="tm-svg"` sur la racine, `viewBox` d'environ 720 de large, et les classes de thème
  `.gold`, `.green`, `.red`, `.muted`, `.mono`, `.box`, `.line` (elles s'adaptent au mode clair et sombre).
  Ne jamais coder de couleur en dur, sauf `fill="#ffffff"` pour du texte posé sur un rectangle coloré.
- Vert et rouge sont réservés au P&L et aux zones haussières ou baissières.

## Style rédactionnel

- Français direct et concret, phrases courtes, pas de tirets cadratins.
- Chiffres réalistes, jamais de fausse précision ni de statistique inventée avec source fictive.
- Aucune promesse de gains ; ton cohérent avec `docs/10-annexes/01-avertissement.md`.
- Les pertes sont traitées comme du matériau pédagogique, pas comme des échecs honteux.

## Niveau 7 : code Python

- Scripts complets dans `static/code/` (servis sur le site à `/code/...`), liés depuis les chapitres.
- Bibliothèques autorisées : pandas, numpy, matplotlib. Rien d'autre.
- Chaque script génère ses propres données synthétiques (seed fixé, aucune donnée externe, aucun appel réseau).
- Exécuter chaque script avant livraison ; il doit tourner sans erreur et produire une sortie reproductible.
- Les extraits importants sont repris dans le chapitre en blocs ```python commentés.

## Interdits

- Ne jamais modifier un chapitre déjà rédigé (fichier sans admonition « en préparation »).
- Ne pas toucher `src/`, `docusaurus.config.js`, `custom.css` ni `sidebars.js`, sauf bug bloquant expliqué dans le commit.
- Ne pas supprimer `scripts/generate_stubs.py`.
- Ne pas ajouter de dépendance npm.

## Validation et commits

- `npm install` au premier lancement si `node_modules` est absent (Node 20+).
- `npm run build` doit passer sans erreur ni avertissement de lien cassé avant chaque commit.
- Un commit par chapitre : `feat(n0): market-mechanics`. Examen : `feat(n0): examen`. Glossaire : `docs: glossaire n0`.
