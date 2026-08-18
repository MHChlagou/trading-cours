"""
monte_carlo_drawdown.py  --  Cours de trading, niveau 7, chapitre 8
===================================================================

Statistiques et Monte Carlo sur une série de trades en R.

Le script :
  1. génère une série synthétique de trades (seed fixé) dont on CONNAÎT
     la vraie expectancy, pour voir ce que mesure un échantillon fini ;
  2. montre la distribution réelle des résultats d'un système
     (asymétrique, pas une cloche) ;
  3. calcule l'intervalle de confiance de l'expectancy de deux façons :
     formule (écart-type / racine de n) et bootstrap ;
  4. simule par Monte Carlo (rééchantillonnage des trades) des milliers
     de séquences pour obtenir la distribution du drawdown, de la plus
     longue série de pertes, et la probabilité de toucher un seuil de
     ruine (par exemple -20 R) ;
  5. compare le drawdown HISTORIQUE (une seule séquence) au drawdown
     PROBABLE (la distribution) ;
  6. montre l'effet de la taille d'échantillon sur la certitude.

Bibliothèques : numpy, pandas, matplotlib. Rien d'autre. Aucune donnée
externe, aucun appel réseau. Résultat reproductible.
Exécution : python monte_carlo_drawdown.py
Sortie    : console + monte_carlo_drawdown.png
"""

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 7
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------------------
# 1. Un système synthétique dont on connaît la vérité
# ---------------------------------------------------------------------------

def simulate_system(n, win_rate=0.5, p_c1_only=0.5, r_stop=-1.0,
                    r_c1=1.5, r_c2=3.0, r_be=0.0, cost=0.04):
    """Génère n résultats en R d'un système à trois issues, coûts déduits.

    - avec probabilité 1 - win_rate : perte au stop (r_stop) ;
    - sinon : gain ; parmi les gains, une fraction p_c1_only sort la moitié
      à C1 et le solde au breakeven (0,5*r_c1 + 0,5*r_be), le reste sort la
      moitié à C1 et l'autre à C2 (0,5*r_c1 + 0,5*r_c2).
    Un petit bruit uniforme simule le slippage variable.
    """
    u = rng.random(n)
    r = np.where(u > win_rate, r_stop, 0.0)
    gains = u <= win_rate
    v = rng.random(n)
    r_gain = np.where(v < p_c1_only, 0.5 * r_c1 + 0.5 * r_be, 0.5 * r_c1 + 0.5 * r_c2)
    r = np.where(gains, r_gain, r)
    r = r - cost + rng.uniform(-0.05, 0.05, n)
    return r


def true_expectancy(win_rate=0.5, p_c1_only=0.5, r_stop=-1.0, r_c1=1.5, r_c2=3.0, r_be=0.0, cost=0.04):
    e_gain = p_c1_only * (0.5 * r_c1 + 0.5 * r_be) + (1 - p_c1_only) * (0.5 * r_c1 + 0.5 * r_c2)
    return win_rate * e_gain + (1 - win_rate) * r_stop - cost


# ---------------------------------------------------------------------------
# 2. Statistiques descriptives et intervalle de confiance
# ---------------------------------------------------------------------------

def describe(r):
    r = np.asarray(r)
    n = len(r)
    mean = r.mean()
    sd = r.std(ddof=1)
    se = sd / np.sqrt(n)
    return dict(n=n, mean=mean, sd=sd, se=se, ci95=(mean - 1.96 * se, mean + 1.96 * se),
                win_rate=(r > 0).mean(), median=np.median(r),
                p10=np.percentile(r, 10), p90=np.percentile(r, 90))


def bootstrap_expectancy(r, n_boot=10_000):
    """Intervalle de confiance par bootstrap : on rééchantillonne les
    trades avec remise, on recalcule la moyenne, n_boot fois."""
    r = np.asarray(r)
    n = len(r)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = r[idx].mean(axis=1)
    return np.percentile(means, 2.5), np.percentile(means, 97.5), means


# ---------------------------------------------------------------------------
# 3. Monte Carlo des séquences : drawdown, séries, ruine
# ---------------------------------------------------------------------------

def max_drawdown(path):
    """Drawdown maximal (en R, valeur positive) d'une courbe cumulée."""
    peak = np.maximum.accumulate(path)
    return (peak - path).max()


def longest_loss_streak(r):
    best = cur = 0
    for x in r:
        cur = cur + 1 if x <= 0 else 0
        best = max(best, cur)
    return best


def monte_carlo(r, n_sims=5_000, horizon=None, ruin_level=-20.0):
    """Rééchantillonne les trades observés (avec remise) pour construire
    n_sims séquences de longueur horizon ; renvoie les distributions.

    Hypothèse : les trades sont indépendants et tirés de la même loi que
    l'échantillon (pas de régime, pas de dépendance). C'est optimiste sur
    les séries (le réel a des régimes) ; on le sait, on le dit.
    """
    r = np.asarray(r)
    n = len(r)
    if horizon is None:
        horizon = n
    idx = rng.integers(0, n, size=(n_sims, horizon))
    sims = r[idx]
    paths = np.cumsum(sims, axis=1)
    peaks = np.maximum.accumulate(paths, axis=1)
    dds = (peaks - paths).max(axis=1)
    finals = paths[:, -1]
    ruined = (paths.min(axis=1) <= ruin_level).mean()
    streaks = np.array([longest_loss_streak(s) for s in sims[:1000]])  # 1000 suffisent
    return dict(dd=dds, final=finals, ruin_prob=ruined, streaks=streaks, paths=paths)


# ---------------------------------------------------------------------------
# 4. Programme principal
# ---------------------------------------------------------------------------

def main():
    e_true = true_expectancy()
    print("=== Système synthétique ===")
    print(f"  vraie expectancy (connue) : {e_true:+.3f} R par trade")

    # ---- un échantillon de 120 trades, comme un backtest ou un an de journal
    r = simulate_system(120)
    d = describe(r)
    print("\n=== Échantillon de 120 trades ===")
    print(f"  moyenne (expectancy mesurée) : {d['mean']:+.3f} R")
    print(f"  écart-type des résultats     : {d['sd']:.2f} R")
    print(f"  erreur standard (sd / sqrt n): {d['se']:.3f} R")
    print(f"  IC 95 % (formule)            : [{d['ci95'][0]:+.3f} ; {d['ci95'][1]:+.3f}]")
    lo, hi, _ = bootstrap_expectancy(r)
    print(f"  IC 95 % (bootstrap)          : [{lo:+.3f} ; {hi:+.3f}]")
    print(f"  taux de réussite             : {d['win_rate'] * 100:.1f} %")
    print(f"  médiane / p10 / p90          : {d['median']:+.2f} / {d['p10']:+.2f} / {d['p90']:+.2f} R")
    print("  -> la distribution n'est pas une cloche : deux bosses (stops, gains) et une queue à droite")

    # ---- drawdown historique de CETTE séquence
    hist_dd = max_drawdown(np.cumsum(r))
    hist_streak = longest_loss_streak(r)
    print("\n=== Historique (la seule séquence observée) ===")
    print(f"  drawdown max historique      : {hist_dd:.1f} R")
    print(f"  plus longue série de pertes  : {hist_streak}")

    # ---- Monte Carlo : que peut produire le MÊME système sur 120 trades ?
    mc = monte_carlo(r, n_sims=5_000, horizon=120, ruin_level=-20.0)
    print("\n=== Monte Carlo : 5 000 séquences de 120 trades rééchantillonnées ===")
    print(f"  drawdown médian              : {np.median(mc['dd']):.1f} R")
    print(f"  drawdown 90e percentile      : {np.percentile(mc['dd'], 90):.1f} R")
    print(f"  drawdown 99e percentile      : {np.percentile(mc['dd'], 99):.1f} R")
    print(f"  série de pertes médiane / p95: {np.median(mc['streaks']):.0f} / {np.percentile(mc['streaks'], 95):.0f}")
    print(f"  P(toucher -20 R)             : {mc['ruin_prob'] * 100:.1f} %")
    print(f"  P(résultat final < 0)        : {(mc['final'] < 0).mean() * 100:.1f} %")
    print("  -> le drawdown historique est UNE valeur tirée de cette distribution, pas un maximum")

    # ---- horizon plus long : 500 trades (plusieurs années)
    mc5 = monte_carlo(r, n_sims=5_000, horizon=500, ruin_level=-20.0)
    print("\n=== Monte Carlo : horizon 500 trades ===")
    print(f"  drawdown médian / p90 / p99  : {np.median(mc5['dd']):.1f} / {np.percentile(mc5['dd'], 90):.1f} / {np.percentile(mc5['dd'], 99):.1f} R")
    print(f"  P(toucher -20 R)             : {mc5['ruin_prob'] * 100:.1f} %")
    print("  -> plus l'horizon est long, plus le pire drawdown rencontré est grand : c'est mécanique")

    # ---- taille d'échantillon et significativité
    print("\n=== Taille d'échantillon : largeur de l'IC 95 % sur l'expectancy ===")
    for n in (30, 60, 100, 200, 400, 800):
        widths = []
        for _ in range(200):
            rr = simulate_system(n)
            dd_ = describe(rr)
            widths.append(dd_["ci95"][1] - dd_["ci95"][0])
        neg = np.mean([simulate_system(n).mean() < 0 for _ in range(1000)])
        print(f"  n = {n:4d} : demi-largeur ≈ ±{np.mean(widths) / 2:.2f} R ; P(mesurer une expectancy < 0) ≈ {neg * 100:4.1f} %")
    print(f"  (rappel : la vraie expectancy est {e_true:+.3f} R)")

    # ---- figure
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].hist(r, bins=25)
    axes[0].set_title("Distribution des 120 résultats (R)")
    for k in range(60):
        axes[1].plot(mc["paths"][k], linewidth=0.6, alpha=0.6)
    axes[1].plot(np.cumsum(r), linewidth=2.0, color="black")
    axes[1].set_title("60 séquences Monte Carlo (noir : historique)")
    axes[1].set_xlabel("trade")
    axes[1].set_ylabel("R cumulés")
    axes[2].hist(mc["dd"], bins=30)
    axes[2].axvline(hist_dd, color="black", linewidth=2)
    axes[2].set_title("Drawdown max sur 120 trades (noir : historique)")
    axes[2].set_xlabel("R")
    fig.tight_layout()
    fig.savefig("monte_carlo_drawdown.png", dpi=110)
    print("\n  figure enregistrée : monte_carlo_drawdown.png")


if __name__ == "__main__":
    main()
