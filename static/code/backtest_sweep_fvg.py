"""
backtest_sweep_fvg.py  --  Cours de trading, niveau 7, chapitre 7
=================================================================

Backtest complet, commenté et reproductible d'une version simplifiée du
setup 1 (sweep + displacement + FVG) sur des données OHLC synthétiques.

Le script fait, dans l'ordre :
  1. génère des données OHLC 5 minutes synthétiques (seed fixé, aucune
     donnée externe, aucun appel réseau) ;
  2. les nettoie comme on nettoierait un vrai fichier (doublons, trous,
     bougies incohérentes, filtre de séance) ;
  3. montre un backtest VECTORISÉ (règle simple : croisement de moyennes)
     pour illustrer la méthode et ses limites ;
  4. exécute un backtest EVENT-DRIVEN, bougie par bougie, du setup
     sweep + displacement + FVG avec stop, cibles, breakeven et coûts ;
  5. calcule les métriques : expectancy, taux de réussite, profit factor,
     drawdown, série de pertes ;
  6. trace la courbe de capital en R et la distribution des résultats.

Bibliothèques : pandas, numpy, matplotlib. Rien d'autre.
Exécution :  python backtest_sweep_fvg.py
Sortie     :  texte dans la console + fichier backtest_sweep_fvg.png

Les données sont synthétiques : les résultats n'ont AUCUNE valeur
prédictive. Le but est la méthode, pas le chiffre.
"""

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # rendu hors écran, reproductible
import matplotlib.pyplot as plt

SEED = 42
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# 1. Données synthétiques : 5 minutes, séance 15 h 30 - 22 h 00 (Paris),
#    500 jours, un prix qui ressemble à un indice (tendances, ranges, sweeps).
# ---------------------------------------------------------------------------

def make_synthetic_ohlc(n_days=500, bars_per_day=78, start_price=5000.0):
    """Construit un DataFrame OHLC 5 min avec un régime qui alterne.

    Le processus : rendement = dérive de régime + bruit à queues épaisses
    (loi de Student à 3 degrés de liberté) ; la dérive et la volatilité
    changent tous les 5 à 20 jours (tendance haussière, baissière, range).
    Deux comportements sont injectés volontairement, sans quoi le setup ne
    pourrait pas exister dans des données purement aléatoires :
      - des impulsions aléatoires (1,5 % des bougies) de 2 à 4 fois la
        volatilité, dans un sens ou dans l'autre (les "displacements") ;
      - une réaction sur le plus bas de la veille : quand le prix passe
        sous le PDL, une impulsion haussière suit dans 60 % des cas
        (la bougie du sweep se referme au-dessus, la suivante affiche le
        "displacement"), et dans la moitié de ces cas une dérive positive
        persiste le reste de la séance (la "continuation").
    Le backtest mesure donc ce qu'on a mis dans les données ; c'est le
    point pédagogique : un backtest ne prouve rien sur le futur, il
    mesure une règle sur un passé donné.
    Les bougies OHLC sont reconstruites à partir d'un chemin intra-bougie.
    """
    rows = []
    price = start_price
    day = pd.Timestamp("2024-01-02")
    regime_left = 0
    drift = 0.0
    vol = 0.00035  # écart-type d'un rendement 5 min (~0,035 %)
    prev_day_low = None
    for _ in range(n_days):
        # week-ends sautés
        while day.weekday() >= 5:
            day += pd.Timedelta(days=1)
        if regime_left == 0:
            regime_left = int(rng.integers(5, 21))
            # dérive de régime ; le -0.000028 compense en moyenne les
            # réactions et continuations haussières injectées plus bas,
            # pour que le prix ne parte pas dans une seule direction
            drift = rng.choice([0.00004, -0.00004, 0.0]) - 0.000028
            vol = float(rng.choice([0.00025, 0.00035, 0.0005]))
        regime_left -= 1
        t = day + pd.Timedelta(hours=15, minutes=30)
        day_low = np.inf
        pending_impulse = 0.0  # impulsion à appliquer sur la bougie suivante
        swept_today = False
        day_drift = 0.0  # dérive intraday ajoutée après une réaction (continuation)
        for _b in range(bars_per_day):
            # 8 sous-pas par bougie ; bruit de Student (queues épaisses)
            noise = rng.standard_t(3, 8) * vol / np.sqrt(8) / np.sqrt(3)
            steps = (drift + day_drift) / 8 + noise
            # impulsion aléatoire dans un sens ou l'autre
            if rng.random() < 0.015:
                pending_impulse += rng.choice([-1, 1]) * rng.uniform(2.0, 4.0) * vol * 3
            if pending_impulse != 0.0:
                steps = steps + pending_impulse / 8
                pending_impulse = 0.0
            path = price * np.exp(np.cumsum(steps))
            # réaction sur le plus bas de la veille (une fois par jour) :
            # si le chemin passe sous le PDL, dans 45 % des cas un acheteur
            # "se sert" : la bougie se referme au-dessus (45 % de l'impulsion
            # dans la bougie du sweep) et la bougie suivante affiche le
            # reste (le displacement).
            if prev_day_low is not None and not swept_today and path.min() < prev_day_low:
                swept_today = True
                if rng.random() < 0.6:
                    impulse = rng.uniform(3.0, 5.0) * vol * 3
                    k = int(np.argmax(path < prev_day_low))
                    if k < 7:
                        steps[k + 1 :] += 0.45 * impulse / (7 - k)
                        pending_impulse += 0.55 * impulse
                    else:
                        pending_impulse += impulse
                    # dans la moitié des cas, la réaction devient une
                    # continuation : dérive positive le reste de la séance
                    if rng.random() < 0.5:
                        day_drift = 0.5 * vol
                    path = price * np.exp(np.cumsum(steps))
            o = price
            c = path[-1]
            h = max(o, path.max())
            l = min(o, path.min())
            volume = int(rng.integers(800, 4000))
            rows.append((t, o, h, l, c, volume))
            price = c
            day_low = min(day_low, l)
            t += pd.Timedelta(minutes=5)
        prev_day_low = day_low
        # gap de nuit
        price *= np.exp(rng.normal(0, 0.002))
        day += pd.Timedelta(days=1)
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
    df = df.set_index("time")
    # arrondi au tick de 0,25 (comme ES/MES)
    for col in ["open", "high", "low", "close"]:
        df[col] = (df[col] / 0.25).round() * 0.25
    return df


def inject_defects(df):
    """Simule les défauts d'un vrai fichier : doublons, trous, bougies fausses."""
    df = df.copy()
    # 20 lignes dupliquées
    dup_idx = rng.choice(len(df), 20, replace=False)
    df = pd.concat([df, df.iloc[dup_idx]]).sort_index()
    # 15 bougies manquantes
    drop_idx = rng.choice(len(df), 15, replace=False)
    df = df.drop(df.index[drop_idx])
    # 5 bougies incohérentes (high < low)
    bad_idx = rng.choice(len(df), 5, replace=False)
    df.iloc[bad_idx, df.columns.get_loc("high")] = df.iloc[bad_idx]["low"] - 1.0
    # 3 prix aberrants (fat finger)
    ff_idx = rng.choice(len(df), 3, replace=False)
    df.iloc[ff_idx, df.columns.get_loc("low")] = df.iloc[ff_idx]["low"] * 0.9
    return df


# ---------------------------------------------------------------------------
# 2. Nettoyage
# ---------------------------------------------------------------------------

def clean_ohlc(df, session_start="15:30", session_end="22:00"):
    """Nettoyage standard d'un fichier OHLC.

    - index datetime trié, doublons supprimés (on garde la première ligne) ;
    - bougies incohérentes retirées (high < low, high < max(o,c), etc.) ;
    - prix aberrants retirés (écart de plus de 5 % au précédent close) ;
    - filtre de séance ;
    - trous : on NE comble PAS les bougies manquantes (les remplir invente
      des prix) ; on les compte pour information.
    """
    df = df.sort_index()
    n0 = len(df)
    df = df[~df.index.duplicated(keep="first")]
    n_dup = n0 - len(df)

    coherent = (
        (df["high"] >= df["low"])
        & (df["high"] >= df[["open", "close"]].max(axis=1))
        & (df["low"] <= df[["open", "close"]].min(axis=1))
    )
    n_bad = int((~coherent).sum())
    df = df[coherent]

    prev_close = df["close"].shift(1)
    jump = (df["low"] / prev_close - 1).abs()
    aberrant = jump > 0.05
    n_ff = int(aberrant.sum())
    df = df[~aberrant]

    df = df.between_time(session_start, session_end)

    # comptage des trous : écart de plus de 5 min à l'intérieur d'une journée
    gaps = df.index.to_series().diff()
    same_day = df.index.to_series().dt.date == df.index.to_series().dt.date.shift(1)
    n_gaps = int(((gaps > pd.Timedelta(minutes=5)) & same_day).sum())

    report = dict(doublons=n_dup, incoherentes=n_bad, aberrantes=n_ff, trous=n_gaps, lignes=len(df))
    return df, report


# ---------------------------------------------------------------------------
# 3. Backtest vectorisé (illustration) : croisement de moyennes 20 / 50
# ---------------------------------------------------------------------------

def vectorized_ma_cross(df, fast=20, slow=50, cost_per_trade=0.0002):
    """Backtest vectorisé : une position +1 / -1 / 0 par bougie, P&L en %.

    Avantages : dix lignes, instantané. Limites : pas de stop, pas de
    cibles, une position par bougie, coûts approximés par changement de
    position ; impossible de modéliser un ordre limite ou un breakeven.
    """
    close = df["close"]
    ma_f = close.rolling(fast).mean()
    ma_s = close.rolling(slow).mean()
    # position décidée sur la clôture, appliquée à la bougie SUIVANTE
    # (sinon on utilise le futur : biais look-ahead)
    pos = np.sign(ma_f - ma_s).shift(1).fillna(0)
    ret = close.pct_change().fillna(0)
    gross = pos * ret
    turnover = pos.diff().abs().fillna(0)
    net = gross - turnover * cost_per_trade
    return net.cumsum()


# ---------------------------------------------------------------------------
# 4. Backtest event-driven du setup sweep + displacement + FVG (long only,
#    version simplifiée et entièrement mécanique)
# ---------------------------------------------------------------------------

def atr(df, n=14):
    """ATR classique sur l'unité du DataFrame."""
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift(1)).abs()
    lc = (df["low"] - df["close"].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def event_driven_backtest(
    df,
    tick=0.25,
    tick_value=1.25,          # MES : 1,25 $ par tick
    commission_rt=1.0,        # $ aller-retour par contrat (ordre de grandeur)
    slippage_ticks_market=1,  # slippage sur les ordres au marché (stop)
    sweep_min_ticks=2,
    disp_atr=1.5,
    fvg_atr=0.4,
    stop_atr_margin=0.5,
    c1_ratio=1.5,
    c2_ratio=3.0,
    max_wait_bars=18,         # 90 min en M5 pour être servi
    last_entry_time="21:00",
):
    """Rejoue le marché bougie par bougie.

    Réservoir : le plus bas de la veille (PDL), le seul réservoir modélisé ici.
    Signal long :
      S1 sweep      : low < PDL - sweep_min_ticks * tick ET close > PDL
      S2 displacement : dans les 3 bougies suivantes, une bougie haussière
                      de range >= disp_atr * ATR(M15 approx = ATR M5 * sqrt(3)),
                      corps >= 60 % du range, clôture > dernier LH interne
                      (approximé par le plus haut des 6 bougies avant le sweep)
      S3 FVG        : low[bougie+1] > high[bougie-1] et hauteur >= fvg_atr * ATR
    Entrée : limite au bord haut du FVG + 1 tick, servie si une bougie
             passe SOUS ce prix (règle conservatrice), dans les max_wait_bars.
    Stop   : plus bas du sweep - stop_atr_margin * ATR.
    Cibles : C1 = entrée + c1_ratio * risque (50 % sortis, stop à BE + 1 tick),
             C2 = entrée + c2_ratio * risque. En cas de doute (stop et cible
             touchés dans la même bougie) : stop d'abord.
    Sortie sur temps : 21 h 15.
    Un seul trade à la fois.
    """
    df = df.copy()
    df["atr5"] = atr(df, 14)
    df["atr15"] = df["atr5"] * np.sqrt(3)  # approximation de l'ATR M15
    df["date"] = df.index.date
    daily_low = df.groupby("date")["low"].min()
    pdl_map = daily_low.shift(1)  # plus bas de la VEILLE
    df["pdl"] = df["date"].map(pdl_map)

    o = df["open"].values
    h = df["high"].values
    l = df["low"].values
    c = df["close"].values
    a15 = df["atr15"].values
    pdl = df["pdl"].values
    times = df.index
    n = len(df)

    trades = []
    i = 20
    while i < n - 4:
        if np.isnan(pdl[i]) or np.isnan(a15[i]):
            i += 1
            continue
        # ---- S1 : sweep du PDL avec clôture au-dessus
        if l[i] < pdl[i] - sweep_min_ticks * tick and c[i] > pdl[i]:
            sweep_low = l[i]
            sweep_i = i
            lh_internal = h[i - 6:i].max()  # approximation du dernier LH interne
            found = None
            for j in range(i + 1, min(i + 4, n - 2)):
                rng_j = h[j] - l[j]
                body_j = c[j] - o[j]
                if (
                    body_j > 0
                    and rng_j >= disp_atr * a15[j]
                    and body_j >= 0.6 * rng_j
                    and c[j] > lh_internal
                ):
                    # ---- S3 : FVG entre high[j-1] et low[j+1]
                    fvg_low = h[j - 1]
                    fvg_high = l[j + 1]
                    if fvg_high - fvg_low >= fvg_atr * a15[j]:
                        found = (j, fvg_low, fvg_high)
                    break
            if found is None:
                i += 1
                continue
            j, fvg_low, fvg_high = found
            entry_px = fvg_high + tick
            stop_px = sweep_low - stop_atr_margin * a15[j]
            stop_px = np.floor(stop_px / tick) * tick
            risk = entry_px - stop_px
            if risk <= 0:
                i += 1
                continue
            c1 = entry_px + c1_ratio * risk
            c2 = entry_px + c2_ratio * risk
            # ---- attente d'exécution de la limite (bougie j+2 et suivantes)
            filled = None
            k = j + 2
            while k < n and k <= j + 1 + max_wait_bars:
                if times[k].date() != times[j].date():
                    break  # la limite meurt à la fin de la séance
                if times[k].strftime("%H:%M") > last_entry_time:
                    break
                # invalidation avant exécution : traversée du FVG en clôture
                # ou retour sous le plus bas du sweep
                if c[k] < fvg_low or l[k] < sweep_low:
                    break
                if l[k] < entry_px - tick:  # traversée d'un tick : servi
                    filled = k
                    break
                k += 1
            if filled is None:
                i = j + 1
                continue
            # ---- gestion bougie par bougie
            qty = 2  # 2 contrats pour permettre la sortie de 50 %
            remaining = qty
            realized_ticks = 0.0
            stop_now = stop_px
            mfe = 0.0
            mae = 0.0
            exit_reason = None
            m = filled
            while m < n:
                if times[m].date() != times[filled].date():
                    exit_reason = "fin de séance"
                    m -= 1
                    px = c[m]
                    realized_ticks += remaining * (px - entry_px) / tick
                    remaining = 0
                    break
                mfe = max(mfe, (h[m] - entry_px) / risk)
                mae = max(mae, (entry_px - l[m]) / risk)
                # stop d'abord (règle conservatrice)
                if l[m] <= stop_now:
                    px = stop_now - slippage_ticks_market * tick
                    realized_ticks += remaining * (px - entry_px) / tick
                    remaining = 0
                    exit_reason = "stop" if stop_now == stop_px else "breakeven"
                    break
                if remaining == qty and h[m] >= c1 + tick:
                    realized_ticks += (qty / 2) * (c1 - entry_px) / tick
                    remaining = qty / 2
                    stop_now = entry_px + tick
                if remaining < qty and h[m] >= c2 + tick:
                    realized_ticks += remaining * (c2 - entry_px) / tick
                    remaining = 0
                    exit_reason = "C2"
                    break
                if times[m].strftime("%H:%M") >= "21:15":
                    px = c[m]
                    realized_ticks += remaining * (px - entry_px) / tick
                    remaining = 0
                    exit_reason = "sortie sur temps"
                    break
                m += 1
            if remaining > 0:  # fin de données
                px = c[min(m, n - 1)]
                realized_ticks += remaining * (px - entry_px) / tick
                exit_reason = "fin de données"
            gross = realized_ticks * tick_value
            costs = qty * commission_rt
            net = gross - costs
            risk_dollars = qty * risk / tick * tick_value
            trades.append(
                dict(
                    entry_time=times[filled],
                    exit_time=times[min(m, n - 1)],
                    entry=entry_px,
                    stop=stop_px,
                    risk_ticks=risk / tick,
                    r_net=net / risk_dollars,
                    mfe=mfe,
                    mae=mae,
                    reason=exit_reason,
                )
            )
            i = max(m, j) + 1
        else:
            i += 1
    return pd.DataFrame(trades)


# ---------------------------------------------------------------------------
# 5. Métriques
# ---------------------------------------------------------------------------

def metrics(trades):
    """Expectancy, taux, profit factor, drawdown, série de pertes."""
    r = trades["r_net"]
    n = len(r)
    if n == 0:
        return {}
    wins = r[r > 0]
    losses = r[r <= 0]
    equity = r.cumsum()
    peak = equity.cummax()
    dd = equity - peak
    # plus longue série de pertes
    streak = best = 0
    for x in r:
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)
    return dict(
        n=n,
        expectancy=r.mean(),
        stderr=r.std(ddof=1) / np.sqrt(n),
        win_rate=len(wins) / n,
        avg_win=wins.mean() if len(wins) else 0.0,
        avg_loss=losses.mean() if len(losses) else 0.0,
        profit_factor=(wins.sum() / -losses.sum()) if losses.sum() < 0 else np.inf,
        max_dd=dd.min(),
        longest_loss_streak=best,
        total_r=r.sum(),
        mfe_ge_1_5=(trades["mfe"] >= 1.5).mean(),
        mfe_ge_3=(trades["mfe"] >= 3.0).mean(),
    )


# ---------------------------------------------------------------------------
# 6. Programme principal
# ---------------------------------------------------------------------------

def main():
    raw = make_synthetic_ohlc()
    dirty = inject_defects(raw)
    df, report = clean_ohlc(dirty)
    print("=== Nettoyage ===")
    for k, v in report.items():
        print(f"  {k:14s}: {v}")

    print("\n=== Backtest vectorisé (croisement MM 20/50, illustration) ===")
    curve = vectorized_ma_cross(df)
    print(f"  rendement cumulé net : {curve.iloc[-1] * 100:+.2f} %  (aucun stop, aucune cible : à ne pas trader)")

    print("\n=== Backtest event-driven : sweep + displacement + FVG (long, PDL) ===")
    trades = event_driven_backtest(df)
    m = metrics(trades)
    if not m:
        print("  aucun trade")
        return
    print(f"  trades              : {m['n']}")
    print(f"  expectancy (R net)  : {m['expectancy']:+.3f} ± {m['stderr']:.3f} (1 écart-type)")
    print(f"  taux de réussite    : {m['win_rate'] * 100:.1f} %")
    print(f"  gain moyen / perte  : {m['avg_win']:+.2f}R / {m['avg_loss']:+.2f}R")
    print(f"  profit factor       : {m['profit_factor']:.2f}")
    print(f"  drawdown max        : {m['max_dd']:.1f}R")
    print(f"  série de pertes max : {m['longest_loss_streak']}")
    print(f"  total               : {m['total_r']:+.1f}R")
    print(f"  MFE >= 1,5R / 3R    : {m['mfe_ge_1_5'] * 100:.0f} % / {m['mfe_ge_3'] * 100:.0f} %")
    print("\n  sorties :")
    print(trades["reason"].value_counts().to_string())

    # ---- graphique
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    eq = trades["r_net"].cumsum()
    axes[0].plot(range(1, len(eq) + 1), eq.values)
    axes[0].axhline(0, linewidth=0.8)
    axes[0].set_title("Courbe de capital (R cumulés)")
    axes[0].set_xlabel("trade")
    axes[0].set_ylabel("R")
    axes[1].hist(trades["r_net"], bins=20)
    axes[1].set_title("Distribution des résultats (R net)")
    axes[1].set_xlabel("R")
    fig.tight_layout()
    fig.savefig("backtest_sweep_fvg.png", dpi=110)
    print("\n  figure enregistrée : backtest_sweep_fvg.png")


if __name__ == "__main__":
    main()
