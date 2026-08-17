import React, {useState} from 'react';

/** Corrigé repliable, à placer dans un <Exercise>. */
export function Solution({children}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="tm-solution">
      <button type="button" className="tm-solution-toggle" onClick={() => setOpen(!open)}>
        {open ? 'Masquer la solution' : 'Voir la solution'}
      </button>
      {open && <div className="tm-solution-body">{children}</div>}
    </div>
  );
}

/** Bloc exercice. <Exercise n={1} title="..."> énoncé + <Solution>...</Solution> </Exercise> */
export default function Exercise({n, title, children}) {
  return (
    <section className="tm-exercise">
      <header>
        <span className="tm-kicker">{n ? 'Exercice ' + n : 'Exercice'}</span>
        {title && <h4>{title}</h4>}
      </header>
      <div className="tm-exercise-body">{children}</div>
    </section>
  );
}
