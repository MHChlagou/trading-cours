import React from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

const LEVELS = [
  {
    code: 'N0',
    name: 'Fondations',
    desc: 'Marchés, classes d\u2019actifs, ordres, broker, infrastructure.',
    count: '6 chapitres',
    to: '/cours/niveau-0-fondations',
  },
  {
    code: 'N1',
    name: 'Risque et maths du trading',
    desc: 'Position sizing, R-multiples, expectancy, drawdown, portefeuille.',
    count: '6 chapitres',
    to: '/cours/niveau-1-risque',
  },
  {
    code: 'N2',
    name: 'Analyse technique',
    desc: 'Structure de marché, multi-timeframe, niveaux, ATR, volume.',
    count: '6 chapitres',
    to: '/cours/niveau-2-analyse-technique',
  },
  {
    code: 'N3',
    name: 'Prix avancé : SMC, ICT, Wyckoff',
    desc: 'Liquidité, sweeps, FVG, order blocks, structure, campagnes.',
    count: '8 chapitres',
    to: '/cours/niveau-3-prix-avance',
  },
  {
    code: 'N4',
    name: 'Order flow et volume avancé',
    desc: 'Volume Profile, footprint, delta, DOM, open interest, funding.',
    count: '5 chapitres',
    to: '/cours/niveau-4-order-flow',
  },
  {
    code: 'N5',
    name: 'Macro et fondamental',
    desc: 'Banques centrales, intermarket, news, COT, saisonnalité, régimes.',
    count: '7 chapitres',
    to: '/cours/niveau-5-macro',
  },
  {
    code: 'N6',
    name: 'Marchés spécifiques',
    desc: 'ES et NQ, or, pétrole, sessions forex, options et Greeks, crypto.',
    count: '5 chapitres',
    to: '/cours/niveau-6-marches',
  },
  {
    code: 'N7',
    name: 'Stratégie, backtesting et quant',
    desc: 'Setups détaillés, backtesting Python, Monte Carlo, overfitting, IA.',
    count: '10 chapitres',
    to: '/cours/niveau-7-strategie-quant',
  },
  {
    code: 'N8',
    name: 'Psychologie et process',
    desc: 'Biais, journal professionnel, performance analytics, routine.',
    count: '4 chapitres',
    to: '/cours/niveau-8-psychologie',
  },
  {
    code: 'N9',
    name: 'Professionnalisation',
    desc: 'Playbook, études de cas complètes, roadmap 30/60/90, checklists.',
    count: '6 chapitres',
    to: '/cours/niveau-9-professionnalisation',
  },
];

export default function Home() {
  return (
    <Layout
      title="Programme"
      description="Cours de trading complet et gratuit : fondamentaux, risque, SMC, order flow, macro, quant et psychologie. Du niveau zéro à la maîtrise.">
      <header className="tm-hero">
        <div className="tm-hero-inner">
          <p className="tm-hero-eyebrow">Niveau 0 → Niveau 9 · 63 chapitres · 10 examens</p>
          <h1>
            Le trading, appris comme un métier.
          </h1>
          <p className="tm-hero-tagline">
            Un parcours unique qui part de zéro et monte jusqu’aux concepts
            professionnels : gestion du risque, Smart Money Concepts, order flow,
            macro, backtesting Python et construction de votre playbook.
          </p>
          <div className="tm-hero-ctas">
            <Link className="button button--primary button--lg" to="/cours/niveau-0-fondations/quest-ce-que-le-trading">
              Commencer au niveau 0
            </Link>
            <Link className="button button--secondary button--lg" to="/cours/">
              Voir le programme
            </Link>
          </div>
        </div>
      </header>

      <div className="tm-strip">
        théorie · graphiques annotés · trades décortiqués · exercices corrigés · quiz · examen par niveau
      </div>

      <main className="tm-levels">
        <h2 className="tm-levels-title">Le programme</h2>
        {LEVELS.map((lvl) => (
          <Link className="tm-level-row" to={lvl.to} key={lvl.code}>
            <span className="tm-level-code">{lvl.code}</span>
            <span>
              <span className="tm-level-name">{lvl.name}</span>
              <span className="tm-level-desc">{lvl.desc}</span>
            </span>
            <span className="tm-level-count">{lvl.count}</span>
          </Link>
        ))}
      </main>
    </Layout>
  );
}
