import React from 'react';

/**
 * Trade décortiqué, gagnant ou perdant.
 * <TradeExample resultat="gain|perte" instrument direction setup entree stop objectif r>récit</TradeExample>
 */
export default function TradeExample({
  resultat = 'gain',
  instrument,
  direction,
  setup,
  entree,
  stop,
  objectif,
  r,
  children,
}) {
  const gain = resultat === 'gain';
  const rows = [
    ['Instrument', instrument],
    ['Direction', direction],
    ['Setup', setup],
    ['Entrée', entree],
    ['Stop', stop],
    ['Objectif', objectif],
  ].filter((row) => row[1]);

  return (
    <section className={'tm-trade ' + (gain ? 'tm-trade--gain' : 'tm-trade--perte')}>
      <header className="tm-trade-head">
        <span className="tm-trade-badge">{gain ? 'Trade gagnant' : 'Trade perdant'}</span>
        {r && <span className="tm-trade-r">{r}</span>}
      </header>
      <dl className="tm-trade-grid">
        {rows.map(([k, v]) => (
          <div key={k} className="tm-trade-cell">
            <dt>{k}</dt>
            <dd>{v}</dd>
          </div>
        ))}
      </dl>
      {children && <div className="tm-trade-body">{children}</div>}
    </section>
  );
}
