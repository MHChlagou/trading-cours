"""
overfitting_walk_forward.py  --  Cours de trading, niveau 7, chapitre 9
=====================================================================

Montre, sur des données SANS AUCUN EDGE (marche aléatoire pure), comment
une optimisation de paramètres fabrique un backtest magnifique, et
comment la validation le démasque.

Le script :
  1. génère une série de prix quotidiens purement aléatoire (seed fixé) :
     par construction, AUCUNE règle ne peut y avoir d'expectancy positive ;
  2. définit une règle simple à trois paramètres (cassure d'un canal de
     N jours, filtre de moyenne mobile M, stop en multiple K de l'ATR) ;
  3. optimise (grille) les trois paramètres sur la première moitié
     (in-sample) et montre le meilleur résultat : impressionnant ;
  4. applique ces paramètres à la seconde moitié (out-of-sample) : le
     résultat s'effondre ;
  5. fait un walk-forward (ré-optimisation glissante) et montre que la
     concaténation des périodes hors échantillon est nulle ;
  6. mesure la robustesse : la surface des résultats autour du meilleur
     jeu de paramètres est-elle un plateau ou un pic ? ;
  7. quantifie l'effet du nombre de combinaisons testées (degrés de
     liberté) sur le meilleur résultat trouvé par hasard.

Bibliothèques : numpy, pandas, matplotlib. Aucune donnée externe.
Exécution : python overfitting_walk_forward.py
Sortie    : console + overfitting_walk_forward.png
"""

import itertools

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 2024
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------------------
# 1. Une marche aléatoire : aucun edge possible
# ---------------------------------------------------------------------------

def random_walk_ohlc(n_days=2000, start=100.0, vol=0.012):
    """Prix quotidiens : rendements gaussiens indépendants, moyenne nulle.
    On reconstruit un OHLC grossier à partir de 4 sous-pas."""
    rows = []
    price = start
    for _ in range(n_days):
        steps = rng.normal(0, vol / 2, 4)
        path = price * np.exp(np.cumsum(steps))
        o, c = price, path[-1]
        rows.append((o, max(o, path.max()), min(o, path.min()), c))
        price = c
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
    df.index = pd.bdate_range("2016-01-01", periods=n_days)
    return df


# ---------------------------------------------------------------------------
# 2. Une règle à trois paramètres, testée en event-driven simplifié
# ---------------------------------------------------------------------------

def atr(df, n=14):
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift(1)).abs()
    lc = (df["low"] - df["close"].shift(1)).abs()
    return pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(n).mean()


def backtest_rule(df, n_channel, m_filter, k_stop, cost_r=0.03):
    """Long only. Entrée : clôture au-dessus du plus haut des n_channel
    jours précédents ET clôture au-dessus de la moyenne m_filter.
    Stop : k_stop * ATR sous l'entrée. Sortie : stop, ou clôture sous la
    moyenne m_filter. Résultats en R, coût 0,03 R par trade.
    Renvoie la liste des R."""
    close = df["close"].values
    high = df["high"].values
    low = df["low"].values
    a = atr(df).values
    ma = df["close"].rolling(m_filter).mean().values
    upper = pd.Series(high).rolling(n_channel).max().shift(1).values
    n = len(df)
    results = []
    i = max(n_channel, m_filter, 15)
    while i < n - 1:
        if close[i] > upper[i] and close[i] > ma[i] and not np.isnan(a[i]):
            entry = close[i]
            risk = k_stop * a[i]
            stop = entry - risk
            j = i + 1
            while j < n:
                if low[j] <= stop:
                    results.append(-1.0 - cost_r)
                    break
                if close[j] < ma[j]:
                    results.append((close[j] - entry) / risk - cost_r)
                    break
                j += 1
            else:
                results.append((close[n - 1] - entry) / risk - cost_r)
            i = j + 1
        else:
            i += 1
    return np.array(results)


def score(results):
    """Score d'optimisation : R total (ce que la plupart des optimiseurs
    maximisent, et c'est déjà une partie du problème)."""
    return results.sum() if len(results) else 0.0


# ---------------------------------------------------------------------------
# 3-4. Optimisation in-sample, test out-of-sample
# ---------------------------------------------------------------------------

GRID = dict(
    n_channel=[10, 15, 20, 30, 40, 55, 80],
    m_filter=[20, 50, 100, 150, 200],
    k_stop=[1.0, 1.5, 2.0, 3.0],
)


def grid_search(df):
    rows = []
    for nc, mf, ks in itertools.product(GRID["n_channel"], GRID["m_filter"], GRID["k_stop"]):
        r = backtest_rule(df, nc, mf, ks)
        rows.append(dict(n_channel=nc, m_filter=mf, k_stop=ks, n=len(r),
                         total=score(r), exp=r.mean() if len(r) else 0.0))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Walk-forward
# ---------------------------------------------------------------------------

def walk_forward(df, train=500, test=250):
    """Fenêtres glissantes : on optimise sur `train` jours, on applique
    sur les `test` jours suivants, on avance de `test`, on concatène les
    résultats hors échantillon."""
    oos = []
    log = []
    start = 0
    while start + train + test <= len(df):
        tr = df.iloc[start : start + train]
        te = df.iloc[start + train : start + train + test]
        g = grid_search(tr)
        best = g.sort_values("total", ascending=False).iloc[0]
        r_te = backtest_rule(te, int(best.n_channel), int(best.m_filter), float(best.k_stop))
        oos.append(r_te)
        log.append(dict(fenetre=f"{te.index[0].date()} → {te.index[-1].date()}",
                        params=(int(best.n_channel), int(best.m_filter), float(best.k_stop)),
                        is_total=best.total, oos_total=r_te.sum(), oos_n=len(r_te)))
        start += test
    return np.concatenate(oos) if oos else np.array([]), pd.DataFrame(log)


# ---------------------------------------------------------------------------
# 7. Degrés de liberté : le meilleur de k tirages nuls
# ---------------------------------------------------------------------------

def best_of_k_null(k, n_trades=100, sd=1.4, n_rep=2000):
    """On tire k systèmes NULS (expectancy 0, écart-type sd) de n_trades,
    on garde le meilleur : quelle expectancy affiche-t-il en moyenne ?"""
    means = rng.normal(0, sd / np.sqrt(n_trades), size=(n_rep, k))
    return means.max(axis=1).mean()


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main():
    df = random_walk_ohlc()
    half = len(df) // 2
    ins, oos = df.iloc[:half], df.iloc[half:]

    print("=== Données : marche aléatoire, 2000 jours ; par construction AUCUN edge ===")

    g = grid_search(ins)
    g = g.sort_values("total", ascending=False).reset_index(drop=True)
    best = g.iloc[0]
    print(f"\n=== Optimisation in-sample ({len(g)} combinaisons testées) ===")
    print(f"  meilleur jeu : canal {int(best.n_channel)} j, MM {int(best.m_filter)}, stop {best.k_stop} ATR")
    print(f"  in-sample    : {int(best.n)} trades, total {best.total:+.1f} R, expectancy {best.exp:+.2f} R")
    print(f"  médiane des {len(g)} combinaisons in-sample : total {g.total.median():+.1f} R")
    print(f"  part des combinaisons positives in-sample  : {(g.total > 0).mean() * 100:.0f} %")

    r_oos = backtest_rule(oos, int(best.n_channel), int(best.m_filter), float(best.k_stop))
    print("\n=== Le même jeu de paramètres, out-of-sample ===")
    print(f"  out-of-sample : {len(r_oos)} trades, total {r_oos.sum():+.1f} R, expectancy {r_oos.mean() if len(r_oos) else 0:+.2f} R")
    print("  -> le meilleur in-sample n'était que le mieux ajusté au bruit passé")

    oos_wf, log = walk_forward(df)
    print("\n=== Walk-forward (train 500 j, test 250 j, ré-optimisation à chaque pas) ===")
    for _, row in log.iterrows():
        print(f"  {row.fenetre} : params {row.params} ; IS {row.is_total:+.1f} R -> OOS {row.oos_total:+.1f} R ({row.oos_n} trades)")
    print(f"  concaténation OOS : {len(oos_wf)} trades, total {oos_wf.sum():+.1f} R, expectancy {oos_wf.mean() if len(oos_wf) else 0:+.2f} R")
    print("  -> chaque fenêtre est belle en IS et nulle en OOS : c'est la signature du bruit ajusté")

    # robustesse : voisinage du meilleur jeu (in-sample)
    print("\n=== Robustesse : voisinage du meilleur jeu in-sample (canal x stop, MM fixée) ===")
    sub = g[g.m_filter == best.m_filter].pivot(index="n_channel", columns="k_stop", values="total")
    print(sub.round(1).to_string())
    print("  -> un pic isolé entouré de valeurs médiocres ou négatives = un artefact ; un plateau = un vrai comportement")

    print("\n=== Degrés de liberté : meilleur de k systèmes NULS sur 100 trades ===")
    for k in (1, 5, 20, 140, 1000):
        print(f"  k = {k:5d} combinaisons testées : meilleure expectancy trouvée ≈ {best_of_k_null(k):+.2f} R (vraie valeur : 0)")
    print("  -> plus on teste de combinaisons, plus le meilleur résultat par hasard est élevé ; 140 combinaisons ≈ +0,4 R de pur bruit")

    # figure
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    r_is = backtest_rule(ins, int(best.n_channel), int(best.m_filter), float(best.k_stop))
    axes[0].plot(np.cumsum(r_is), label="in-sample (optimisé)")
    axes[0].plot(np.arange(len(r_is), len(r_is) + len(r_oos)), r_is.sum() + np.cumsum(r_oos), label="out-of-sample")
    axes[0].axhline(0, linewidth=0.8)
    axes[0].set_title("Meilleur jeu IS puis OOS (R cumulés)")
    axes[0].legend()
    axes[1].plot(np.cumsum(oos_wf))
    axes[1].axhline(0, linewidth=0.8)
    axes[1].set_title("Walk-forward : OOS concaténés")
    im = axes[2].imshow(sub.values, aspect="auto", origin="lower")
    axes[2].set_xticks(range(len(sub.columns)))
    axes[2].set_xticklabels(sub.columns)
    axes[2].set_yticks(range(len(sub.index)))
    axes[2].set_yticklabels(sub.index)
    axes[2].set_xlabel("stop (ATR)")
    axes[2].set_ylabel("canal (jours)")
    axes[2].set_title("Surface IS autour du meilleur jeu")
    fig.colorbar(im, ax=axes[2])
    fig.tight_layout()
    fig.savefig("overfitting_walk_forward.png", dpi=110)
    print("\n  figure enregistrée : overfitting_walk_forward.png")


if __name__ == "__main__":
    main()
