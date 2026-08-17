# Trading : de Zéro à la Maîtrise

Cours de trading complet sous forme de site statique (Docusaurus 3), pensé pour être hébergé gratuitement sur GitHub Pages.

- 10 niveaux, 63 chapitres, 10 examens de fin de niveau
- Gabarit de chapitre : théorie, graphiques annotés, trades décortiqués, exercices corrigés, quiz interactif
- Recherche locale intégrée (aucun service externe)
- Mode sombre par défaut, impression des checklists

## Démarrage local

Prérequis : Node.js 20 ou plus récent.

```bash
npm install
npm start        # http://localhost:3000
npm run build    # build de production dans ./build
npm run serve    # prévisualiser le build
```

Sous Windows, lancer ces commandes depuis WSL fonctionne sans réglage particulier.

## Configuration GitHub Pages (déjà renseignée)

Dans `docusaurus.config.js`, les valeurs suivantes sont réglées pour ce repo :

| Champ | Valeur |
| --- | --- |
| `url` | `https://MHChlagou.github.io` |
| `organizationName` | `MHChlagou` |
| `projectName` | `trading-cours` |
| `baseUrl` | `/trading-cours/` |
| lien GitHub de la navbar | `https://github.com/MHChlagou/trading-cours` |

Si le repo est renommé ou forké, mettre à jour ces cinq valeurs.

## Déploiement sur GitHub Pages

1. Le repo distant est `https://github.com/MHChlagou/trading-cours.git` ; pousser ce dossier sur la branche `main`.
2. Dans le repo : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. C'est tout. Le workflow `.github/workflows/deploy.yml` construit et déploie le site à chaque push sur `main`.

Le site sera disponible sur `https://MHChlagou.github.io/trading-cours/`.

## Structure du projet

```
docs/                        Le cours (une arborescence = la sidebar)
  00-niveau-0-fondations/    Un dossier par niveau, un fichier par chapitre
  ...
  09-niveau-9-professionnalisation/
  10-annexes/                Avertissement, glossaire, livres, sources
  index.md                   Page Programme (racine de /cours)
src/components/              Composants pédagogiques (Quiz, Exercise, ...)
src/theme/MDXComponents.js   Rend les composants disponibles partout sans import
src/pages/index.js           Page d'accueil
scripts/generate_stubs.py    Génère les stubs manquants (ne réécrit jamais un fichier)
.github/workflows/deploy.yml Déploiement automatique GitHub Pages
```

## Écrire un chapitre : les composants

Les composants sont disponibles dans tous les fichiers `.md` / `.mdx` sans import.

```mdx
<Figure caption="Figure 1 · Légende.">
  <svg className="tm-svg" viewBox="0 0 720 300">...</svg>
</Figure>

<TradeExample resultat="gain" instrument="Futures NQ" direction="Long"
  setup="Sweep + FVG" entree="21 540" stop="21 510" objectif="21 610" r="+2,3R">
  Récit et leçons du trade.
</TradeExample>

<Exercise n={1} title="Titre de l'exercice">
  Énoncé.
  <Solution>Corrigé repliable.</Solution>
</Exercise>

<Checklist title="Pré-marché" items={['Point 1', 'Point 2']} />

<Quiz title="Valider le chapitre" questions={[
  {q: 'Question ?', options: ['A', 'B', 'C'], answer: 1, explain: 'Pourquoi.'},
]} />
```

Le chapitre `docs/00-niveau-0-fondations/01-quest-ce-que-le-trading.mdx` sert de référence : tout nouveau chapitre suit ce gabarit.

## Générer les stubs manquants

```bash
python3 scripts/generate_stubs.py
```

Le script crée uniquement les fichiers absents. Les chapitres déjà rédigés ne sont jamais touchés.

## Feuille de route de rédaction

| Lot | Contenu |
| --- | --- |
| 1 | Socle technique + squelette complet (ce dépôt) |
| 2 → 11 | Rédaction des niveaux 0 à 9, un niveau par lot, examen inclus |
| 12 | Scripts Python de backtesting et Monte Carlo (niveau 7) |
| 13 | Études de cas transversales, checklists finales, relecture |

## Avertissement

Contenu strictement éducatif. Le trading comporte un risque élevé de perte en capital. Voir la page Avertissement du site.
