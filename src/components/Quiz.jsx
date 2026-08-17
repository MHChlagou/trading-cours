import React, {useState} from 'react';

/**
 * Quiz corrigé interactif.
 * <Quiz title="..." questions={[{q, options: [...], answer: index, explain}]} />
 */
export default function Quiz({title = 'Quiz de fin de chapitre', questions = []}) {
  const [choices, setChoices] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const pick = (qi, oi) => {
    if (submitted) return;
    setChoices((c) => ({...c, [qi]: oi}));
  };

  const score = questions.reduce(
    (acc, q, qi) => acc + (choices[qi] === q.answer ? 1 : 0),
    0
  );
  const allAnswered = questions.every((q, qi) => choices[qi] !== undefined);

  return (
    <section className="tm-quiz">
      <header className="tm-quiz-head">
        <span className="tm-kicker">Quiz</span>
        <h3>{title}</h3>
      </header>
      {questions.map((q, qi) => (
        <div className="tm-quiz-q" key={qi}>
          <p className="tm-quiz-question">{qi + 1}. {q.q}</p>
          <div className="tm-quiz-opts">
            {q.options.map((opt, oi) => {
              let cls = 'tm-quiz-opt';
              if (!submitted && choices[qi] === oi) cls += ' is-selected';
              if (submitted && oi === q.answer) cls += ' is-correct';
              if (submitted && choices[qi] === oi && oi !== q.answer) cls += ' is-wrong';
              return (
                <button type="button" key={oi} className={cls} onClick={() => pick(qi, oi)}>
                  {opt}
                </button>
              );
            })}
          </div>
          {submitted && q.explain && <p className="tm-quiz-explain">{q.explain}</p>}
        </div>
      ))}
      <div className="tm-quiz-actions">
        {!submitted ? (
          <button
            type="button"
            className="button button--primary"
            disabled={!allAnswered}
            onClick={() => setSubmitted(true)}>
            Valider mes réponses
          </button>
        ) : (
          <>
            <span className="tm-quiz-score">Score : {score} / {questions.length}</span>
            <button
              type="button"
              className="button button--secondary"
              onClick={() => {
                setChoices({});
                setSubmitted(false);
              }}>
              Recommencer
            </button>
          </>
        )}
      </div>
    </section>
  );
}
