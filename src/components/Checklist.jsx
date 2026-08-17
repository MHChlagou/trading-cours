import React, {useState} from 'react';

/** Checklist interactive et imprimable. <Checklist title="..." items={['...', '...']} /> */
export default function Checklist({title = 'Checklist', items = []}) {
  const [checked, setChecked] = useState({});
  const done = items.filter((item, i) => checked[i]).length;

  return (
    <section className="tm-checklist">
      <header className="tm-checklist-head">
        <div>
          <span className="tm-kicker">Checklist</span>
          <h4>{title}</h4>
        </div>
        <div className="tm-checklist-tools">
          <span className="tm-checklist-count">{done} / {items.length}</span>
          <button
            type="button"
            className="button button--secondary button--sm"
            onClick={() => window.print()}>
            Imprimer
          </button>
        </div>
      </header>
      <ul>
        {items.map((item, i) => (
          <li key={i}>
            <label>
              <input
                type="checkbox"
                checked={!!checked[i]}
                onChange={() => setChecked((c) => ({...c, [i]: !c[i]}))}
              />
              <span>{item}</span>
            </label>
          </li>
        ))}
      </ul>
    </section>
  );
}
