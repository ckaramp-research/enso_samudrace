"""Shared figure style for the ENSO benchmark.

Every figure imports from here rather than setting rcParams itself, so the
style cannot drift between panels of the same paper.

House rules:

* monospace throughout;
* **no titles on axes or figures** -- the manuscript caption carries that,
  and an in-figure title has to be stripped before submission anyway;
* **x tick labels vertical, never diagonal**, whenever the text is long.

Colours are the six-check-validated categorical set used across the
benchmark. ORAS5 is the reference and is drawn in ink rather than a hue, so
it reads as the baseline the models are measured against rather than as one
more series.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

INK = "#212529"
MUTED = "#868E96"
GRID = "#DEE2E6"

_RUNS = (
    "control_0311",
    "control_0313",
    "control_0315",
    "control_0317",
    "control_0319",
)

ENSEMBLES = {"SamudrACE": list(_RUNS)}
# The CMIP6 piControl members vary with what the mirror holds, so figures that
# show CMIP6 fill this from their results with ``set_cmip6``.
ENSEMBLES["CMIP6"] = []

# Plain strong colours: blue for the emulator, red for its parent model,
# green for CMIP6 and black for the reanalysis. Its display label is
# "Reanalysis": the key holds ORAS5 for ocean fields and ERA5 for atmospheric
# ones, so naming either product would mislabel the other.
COLORS = {
    "SamudrACE": "#0000CD",
    "GFDL-CM4": "#DC0000",
    "ORAS5": INK,
    "CMIP6": "#008000",
}
LABELS = {
    "SamudrACE": "SamudrACE",
    "GFDL-CM4": "GFDL-CM4",
    "ORAS5": "ORAS5",
    "CMIP6": "CMIP6",
}
ORDER = ["SamudrACE", "GFDL-CM4", "ORAS5", "CMIP6"]


def set_cmip6(results: dict) -> list[str]:
    """Register the CMIP6 members present in ``results`` (keys ``CMIP6_<model>``)."""
    ENSEMBLES["CMIP6"] = sorted(k for k in results if k.startswith("CMIP6_"))
    return ENSEMBLES["CMIP6"]


def members(key: str) -> list[str]:
    """Underlying result keys for a display entry."""
    return ENSEMBLES.get(key, [key])


def present(results: dict) -> list[str]:
    """Display entries, in house order, that ``results`` can supply."""
    return [k for k in ORDER if any(m in results for m in members(k))]


def gather(results: dict, key: str, extract) -> list[float]:
    """Apply ``extract`` to each member of ``key`` that is present."""
    out = []
    for m in members(key):
        if m in results:
            try:
                value = extract(results[m])
            except (KeyError, TypeError):
                continue
            if value is not None:
                out.append(value)
    return out


def apply(font_size: float = 9.0) -> None:
    """Set the house rcParams. Call once, before creating any figure."""
    plt.rcParams.update(
        {
            "font.family": "monospace",
            "font.size": font_size,
            "axes.labelsize": font_size,
            "axes.titlesize": font_size,
            "axes.edgecolor": MUTED,
            "axes.linewidth": 0.6,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "xtick.labelsize": font_size - 1,
            "ytick.labelsize": font_size - 1,
            "legend.frameon": False,
            "legend.fontsize": font_size - 1,
            "figure.dpi": 150,
            "savefig.bbox": "tight",
            "savefig.dpi": 300,
        }
    )


def category_axis(ax, keys, rotation: int = 0) -> None:
    """Label a categorical x axis.

    Horizontal while the entry names are short. Pass ``rotation=90``
    where they are not; diagonal is never used.
    """
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([LABELS.get(k, k) for k in keys], rotation=rotation, ha="center")
    ax.set_xlim(-0.6, len(keys) - 0.4)


def tidy(ax, axis: str = "y") -> None:
    """Recessive grid, no top/right spines, grid behind the data."""
    ax.grid(axis=axis, color=GRID, lw=0.5, alpha=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def panel_label(ax, text: str, letter: str | None = None, dx: float = 0.0, dy: float = 1.02):
    """Identify a panel without giving it a title.

    ``letter`` prefixes "(a) ", so panels can be referenced from the caption
    and the text. Small and left-aligned, above the axes.
    """
    label = f"({letter}) {text}" if letter else text
    ax.text(
        dx,
        dy,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=plt.rcParams["font.size"],
        color=INK,
    )


def letters(n: int) -> list[str]:
    """Panel letters a, b, c, ... for an n-panel figure."""
    alphabet = [chr(ord("a") + i) for i in range(26)]
    # past z continue aa, ab, ... rather than running into punctuation
    return [alphabet[i] if i < 26 else alphabet[i // 26 - 1] + alphabet[i % 26] for i in range(n)]


def strip(ax, x: float, values, colour: str, spread=None, width: float = 0.28,
          n_label: bool = False, hollow: bool = False, points: bool = True) -> None:
    """One entry of a strip panel: the mean as a bar, members as ticks, a spread.

    ``values`` are full-record values (one per member); their mean is drawn as
    a short horizontal bar and, when there are several, each one as a thinner
    tick. ``spread`` is a distribution (segments, or one value per CMIP6
    model) drawn as jittered points over an interquartile box and a 5--95%
    whisker. ``width`` is the half-width of the mean bar; the box, ticks and
    jitter scale with it. ``hollow`` draws the mean as an open marker frame
    (e.g. for a value that is not significant).
    """
    spread = np.asarray([] if spread is None else spread, dtype=float)
    spread = spread[np.isfinite(spread)]
    if spread.size >= 3:
        lo, hi = np.percentile(spread, [5, 95])
        q1, q3 = np.percentile(spread, [25, 75])
        ax.plot([x, x], [lo, hi], color=colour, lw=1.0, alpha=0.8,
                solid_capstyle="round", zorder=2)
        ax.add_patch(plt.Rectangle((x - 0.6 * width, q1), 1.2 * width, max(q3 - q1, 1e-12),
                                   facecolor=colour, alpha=0.45, edgecolor="none", zorder=2))
        if points:
            rng = np.random.default_rng(0)
            ax.scatter(x + rng.uniform(-0.4 * width, 0.4 * width, spread.size), spread,
                       s=9, color=colour, alpha=0.9, linewidths=0, zorder=3)
    if n_label and spread.size:
        ax.text(x, 1.0, f"n={spread.size}", transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=plt.rcParams["font.size"] - 1.5, color=colour)
    values = [v for v in np.atleast_1d(np.asarray(values, dtype=float)) if np.isfinite(v)]
    if not values:
        return
    if len(values) > 1:
        for v in values:
            ax.plot([x - 0.46 * width, x + 0.46 * width], [v, v], color=colour, lw=1.0,
                    alpha=0.9, zorder=4)
    mean = float(np.mean(values))
    if hollow:
        ax.plot([x - width, x + width], [mean, mean], color=colour, lw=1.9, ls=(0, (1.5, 1.2)),
                zorder=6)
        return
    ax.plot([x - width, x + width], [mean, mean], color="white", lw=3.4,
            solid_capstyle="round", zorder=5)
    ax.plot([x - width, x + width], [mean, mean], color=colour, lw=1.9,
            solid_capstyle="round", zorder=6)


def zero_line(ax) -> None:
    """A zero reference line, only where zero lies inside the data range."""
    lo, hi = ax.get_ylim()
    if lo < 0 < hi:
        ax.axhline(0, color=GRID, lw=0.8, zorder=1)
    ax.set_ylim(lo, hi)


def strip_handles(spread_label: str = "CMIP6 models (5–95%, IQR box)") -> list:
    """Legend entries for strip panels."""
    from matplotlib.lines import Line2D

    return [
        Line2D([], [], color=INK, lw=1.9, label="full record (SamudrACE: mean of runs)"),
        Line2D([], [], color=INK, lw=1.0, label="SamudrACE run"),
        Line2D([], [], color=INK, lw=1.0, alpha=0.8, label=spread_label),
        Line2D([], [], color=COLORS["CMIP6"], marker="o", ls="none", ms=3.2,
               label="CMIP6: one point per model"),
    ]


def save(fig, out) -> None:
    """Write PNG for review and PDF for the manuscript."""
    out.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}")


def scorecard(ax, data: dict, metrics: list, runs=_RUNS,
              legend: bool = True) -> None:
    """One row per metric, each on its own axis in native units, aligned at the CMIP6 mean.

    ``data`` maps a source key to ``{"full": {metric: value}, "segments": {metric: [..]}}``;
    CMIP6 models are the keys starting with ``CMIP6_``. ``metrics`` is a list of
    ``(metric, label, unit)``. Each row spans three CMIP6 standard deviations on either
    side of the CMIP6 mean: the models as dots over their interquartile box and
    5-95% line, SamudrACE (mean of ``runs``, each run as a small open circle), GFDL-CM4
    and ORAS5 as markers, and, where segments exist, their 5-95% range as bars.
    """
    from matplotlib.legend_handler import HandlerTuple
    from matplotlib.ticker import MaxNLocator

    small = plt.rcParams["font.size"]
    cmip6 = [k for k in data if k.startswith("CMIP6_")]
    sam = {m: np.mean([data[r]["full"][m] for r in runs]) for m, _, _ in metrics}
    marks = [("SamudrACE", sam, "o"), ("GFDL-CM4", data["GFDL-CM4"]["full"], "s"),
             ("ORAS5", data["ORAS5"]["full"], "*")]
    rng = np.random.default_rng(0)
    any_segments = False
    for row, (m, label, unit) in enumerate(metrics):
        y = -row
        vals = np.array([data[k]["full"].get(m, np.nan) for k in cmip6], float)
        vals = vals[np.isfinite(vals)]
        mu, sd = vals.mean(), vals.std(ddof=1)
        z = (vals - mu) / sd
        q1, q3 = np.percentile(z, [25, 75])
        lo, hi = np.percentile(z, [5, 95])
        ax.plot([lo, hi], [y, y], color=COLORS["CMIP6"], lw=1.0, alpha=0.8, zorder=1)
        ax.add_patch(plt.Rectangle((q1, y - 0.16), q3 - q1, 0.32, fc=COLORS["CMIP6"],
                                   alpha=0.3, ec="none", zorder=1))
        ax.scatter(np.clip(z, -3.0, 3.0), y + rng.uniform(-0.12, 0.12, z.size), s=6,
                   color=COLORS["CMIP6"], alpha=0.7, lw=0, zorder=2)
        for key, recs, dy in (("SamudrACE", runs, 0.34), ("GFDL-CM4", ("GFDL-CM4",), 0.22)):
            seg = np.concatenate([np.asarray(data[r].get("segments", {}).get(m, []), float)
                                  for r in recs])
            seg = seg[np.isfinite(seg)]
            if seg.size >= 3:
                any_segments = True
                slo, shi = (np.percentile(seg, [5, 95]) - mu) / sd
                ax.plot([slo, shi], [y + dy, y + dy], color=COLORS[key], lw=2.2, alpha=0.5,
                        solid_capstyle="butt", zorder=3)
        obs = data["ORAS5"].get("range", {}).get(m)
        if obs is not None:
            olo, ohi = np.clip((np.asarray(obs) - mu) / sd, -3.0, 3.0)
            ax.plot([olo, ohi], [y + 0.1, y + 0.1], color=COLORS["ORAS5"], lw=2.2, alpha=0.5,
                    solid_capstyle="butt", zorder=3)
        for r in runs:
            ax.scatter((data[r]["full"][m] - mu) / sd, y, s=16, facecolor="none",
                       edgecolor=COLORS["SamudrACE"], lw=0.6, zorder=4)
        for key, full, marker in marks:
            zk = (full[m] - mu) / sd
            if abs(zk) > 3.0:
                # beyond the row's axis: drawn at its edge with an arrow and the value
                edge = 3.0 * np.sign(zk)
                ax.annotate("", xy=(edge + 0.18 * np.sign(zk), y), xytext=(edge, y),
                            arrowprops=dict(arrowstyle="-|>", color=COLORS[key], lw=0.8),
                            zorder=5)
                ax.text(edge - 0.12 * np.sign(zk), y + 0.2, f"{full[m]:.3g}",
                        ha="right" if zk > 0 else "left", va="bottom", color=COLORS[key],
                        fontsize=small - 3)
                zk = edge
            ax.scatter(zk, y, s=60 if marker == "*" else 30, marker=marker,
                       color=COLORS[key], edgecolor="white", lw=0.5, zorder=5)
        # this row's own axis in native units
        ax.plot([-3, 3], [y - 0.3, y - 0.3], color=MUTED, lw=0.5, zorder=0)
        ticks = MaxNLocator(nbins=5).tick_values(mu - 3 * sd, mu + 3 * sd)
        for t in ticks[(ticks >= mu - 3 * sd) & (ticks <= mu + 3 * sd)]:
            zt = (t - mu) / sd
            ax.plot([zt, zt], [y - 0.3, y - 0.36], color=MUTED, lw=0.5, zorder=0)
            ax.text(zt, y - 0.39, f"{t:g}", ha="center", va="top", color=MUTED,
                    fontsize=small - 3)
        name = f"{label} ({unit})" if unit else label
        ax.text(-3.25, y, name, ha="right", va="center", fontsize=small - 1)
    ax.axvline(0, color=GRID, lw=0.8, zorder=0)
    ax.text(0, -len(metrics) + 0.25, "CMIP6 mean", ha="center", va="top", color=MUTED,
            fontsize=small - 2.5)
    if legend:
        handles = [plt.Line2D([], [], ls="", marker="o", color=COLORS["SamudrACE"]),
                   plt.Line2D([], [], ls="", marker="s", color=COLORS["GFDL-CM4"]),
                   plt.Line2D([], [], ls="", marker="*", ms=9, color=COLORS["ORAS5"]),
                   plt.Line2D([], [], ls="", marker="o", mfc="none", ms=4,
                              mec=COLORS["SamudrACE"])]
        labels = ["SamudrACE", "GFDL-CM4", "ORAS5", "each run"]
        if any_segments:
            handles.append((plt.Line2D([], [], color=COLORS["SamudrACE"], lw=2.4, alpha=0.5),
                            plt.Line2D([], [], color=COLORS["GFDL-CM4"], lw=2.4, alpha=0.5)))
            labels.append("segments 5-95%")
        ax.legend(handles, labels, handler_map={tuple: HandlerTuple(ndivide=None, pad=0.2)},
                  loc="upper center", ncol=len(labels), frameon=False, columnspacing=0.8,
                  handletextpad=0.2, fontsize=small - 2.5, bbox_to_anchor=(0.36, 1.0))
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-len(metrics) + 0.15, 1.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)


def pair_panel(ax, data: dict, mx: str, my: str, runs=_RUNS,
               corr: bool = True, corr_at=(0.97, 0.03), obs_range: dict | None = None) -> None:
    """Two metrics against each other: CMIP6 models as dots, the datasets as markers.

    ``data`` maps a source key to ``{metric: value}``; CMIP6 models are the keys
    starting with ``CMIP6_``. SamudrACE is the mean of ``runs``, with each run as a
    small open circle; the rank correlation across the CMIP6 models is printed.
    """
    small = plt.rcParams["font.size"]
    cmip6 = [k for k in data if k.startswith("CMIP6_")]
    xs = np.array([data[k].get(mx, np.nan) for k in cmip6], float)
    ys = np.array([data[k].get(my, np.nan) for k in cmip6], float)
    ok = np.isfinite(xs) & np.isfinite(ys)
    ax.scatter(xs[ok], ys[ok], s=14, color=COLORS["CMIP6"], alpha=0.75, lw=0, zorder=2)
    if corr and ok.sum() > 3:
        from scipy import stats

        r = stats.spearmanr(xs[ok], ys[ok])[0]
        ax.text(*corr_at, f"CMIP6 ρ={r:.2f}", transform=ax.transAxes,
                ha="right" if corr_at[0] > 0.5 else "left",
                va="bottom" if corr_at[1] < 0.5 else "top", color=COLORS["CMIP6"],
                fontsize=small - 2)
    for r_ in runs:
        ax.scatter(data[r_][mx], data[r_][my], s=22, facecolor="none",
                   edgecolor=COLORS["SamudrACE"], lw=0.7, zorder=4)
    sam = (np.mean([data[r_][mx] for r_ in runs]), np.mean([data[r_][my] for r_ in runs]))
    if obs_range:
        obs_whiskers(ax, data["ORAS5"][mx], data["ORAS5"][my], obs_range.get(mx),
                     obs_range.get(my))
    for key, xy, marker in (("SamudrACE", sam, "o"),
                            ("GFDL-CM4", (data["GFDL-CM4"][mx], data["GFDL-CM4"][my]), "s"),
                            ("ORAS5", (data["ORAS5"][mx], data["ORAS5"][my]), "*")):
        ax.scatter(*xy, s=110 if marker == "*" else 55, marker=marker, color=COLORS[key],
                   edgecolor="white", lw=0.7, zorder=5)


def obs_bootstrap(component: str) -> dict:
    """Bootstrap ranges of the reanalysis diagnostics (``run_obs_bootstrap.py``), or {}."""
    import json
    from pathlib import Path

    path = Path("../data/obs_bootstrap") / f"{component}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def obs_whiskers(ax, x: float, y: float, xr_=None, yr_=None, zorder: int = 4) -> None:
    """5-95% bootstrap range of a reanalysis point, as thin black whiskers."""
    if xr_ is not None:
        ax.plot(xr_, [y, y], color=COLORS["ORAS5"], lw=1.0, alpha=0.8, zorder=zorder)
    if yr_ is not None:
        ax.plot([x, x], yr_, color=COLORS["ORAS5"], lw=1.0, alpha=0.8, zorder=zorder)


def obs_band(ax, x, lo_hi, horizontal: bool = False) -> None:
    """5-95% bootstrap range of a reanalysis curve, as light gray shading."""
    lo, hi = np.asarray(lo_hi[0], float), np.asarray(lo_hi[1], float)
    if horizontal:
        ax.fill_betweenx(x, lo, hi, color=COLORS["ORAS5"], alpha=0.15, lw=0, zorder=1)
    else:
        ax.fill_between(x, lo, hi, color=COLORS["ORAS5"], alpha=0.15, lw=0, zorder=1)


def pair_handles(n6: int) -> list:
    return [plt.Line2D([], [], ls="", marker="o", color=COLORS["SamudrACE"], label="SamudrACE"),
            plt.Line2D([], [], ls="", marker="s", color=COLORS["GFDL-CM4"], label="GFDL-CM4"),
            plt.Line2D([], [], ls="", marker="*", ms=10, color=COLORS["ORAS5"],
                       label="ORAS5/ERA5"),
            plt.Line2D([], [], ls="", marker="o", ms=4, color=COLORS["CMIP6"],
                       label=f"CMIP6 models (n={n6})")]


def column_header(ax, text: str, y: float = 1.2) -> None:
    """Header of a figure column: the name above a rule across the axes."""
    ax.text(0.0, y + 0.03, text, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=plt.rcParams["font.size"] + 2, color=INK)
    ax.plot([0, 1], [y, y], transform=ax.transAxes, color=INK, lw=1.2, clip_on=False)
