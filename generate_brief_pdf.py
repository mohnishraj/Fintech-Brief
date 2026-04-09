#!/usr/bin/env python3
"""
Credit Intelligence Brief — Static PDF Generator
Converts a brief HTML file into a clean, print-ready PDF:
  1. Parses Chart.js data from embedded JS
  2. Renders each chart as a static matplotlib image (base64-encoded PNG)
  3. Replaces <canvas> elements with <img> elements
  4. Injects print-optimised CSS overrides
  5. Runs weasyprint to produce a clean paginated PDF

Usage:
    python3 generate_brief_pdf.py --all               # all three archive briefs
    python3 generate_brief_pdf.py <path/to/brief.html> [output.pdf]
"""

import re, sys, base64, io
from pathlib import Path
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Colour palette (mirrors brief-style.css) ─────────────────────────────────
NAVY  = "#0d1b2a";  ACCENT = "#00c2cb";  ACCENT2 = "#f5a623"
GREEN = "#27ae60";  RED    = "#e74c3c";  YELLOW  = "#f39c12"
AMBER = "#b35c00";  BLUE   = "#1a5276";  SMB_G   = "#1e8449"


# ── STEP 1: extract Chart.js calls from embedded JS ──────────────────────────
def _extract_chartjs_calls(html_text: str) -> list:
    charts = []
    pattern = re.compile(
        r"new Chart\(document\.getElementById\(['\"](\w+)['\"]\)\s*,\s*(\{)",
        re.DOTALL
    )
    script_blocks = re.findall(r"<script[^>]*>(.*?)</script>", html_text, re.DOTALL)
    full_js = "\n".join(script_blocks)

    for m in pattern.finditer(full_js):
        canvas_id = m.group(1)
        start = m.start(2)
        depth, end = 0, start
        for i, ch in enumerate(full_js[start:], start):
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        raw = full_js[start:end]

        # chart type
        type_m     = re.search(r"type\s*:\s*['\"](\w+)['\"]", raw)
        chart_type = type_m.group(1) if type_m else "bar"

        # labels (top-level array)
        labels = []
        lm = re.search(r"labels\s*:\s*\[([^\]]+)\]", raw, re.DOTALL)
        if lm:
            labels = [x.strip().strip("'\"") for x in lm.group(1).split(",") if x.strip()]

        # datasets: pair every label string with the next data:[] block
        datasets = []
        ds_labels = re.findall(r"\blabel\s*:\s*['\"]([^'\"]+)['\"]", raw)
        ds_datas  = re.findall(r"\bdata\s*:\s*\[([^\]]+)\]", raw)
        for ds_label, raw_data in zip(ds_labels, ds_datas):
            vals = []
            for tok in raw_data.split(","):
                tok = tok.strip()
                if tok.lower() in ("null", "undefined", ""):
                    vals.append(None)
                else:
                    try:    vals.append(float(tok))
                    except: vals.append(None)
            datasets.append({"label": ds_label, "data": vals})

        # axis bounds
        y_min, y_max = None, None
        ymi = re.search(r"\bmin\s*:\s*([\d.]+)", raw)
        yma = re.search(r"\bmax\s*:\s*([\d.]+)", raw)
        if ymi: y_min = float(ymi.group(1))
        if yma: y_max = float(yma.group(1))

        charts.append({
            "canvas_id": canvas_id, "chart_type": chart_type,
            "labels": labels, "datasets": datasets,
            "y_min": y_min, "y_max": y_max,
        })
    return charts


# ── STEP 2: render each chart to a base64 PNG ────────────────────────────────
def _sloos_colours(vals):
    out = []
    for v in vals:
        if v is None:   out.append("#ccc")
        elif v >= 25:   out.append(RED)
        elif v >= 10:   out.append(YELLOW)
        else:           out.append(GREEN)
    return out

def _smb_colours(n):
    # last bar is confirmed (darker green), rest are estimates (light green)
    return ["#b7e0c9"] * (n - 1) + [SMB_G]


def render_chart(info: dict) -> str:
    cid, ctype = info["canvas_id"], info["chart_type"]
    labels, datasets = info["labels"], info["datasets"]
    y_min, y_max = info["y_min"], info["y_max"]

    if not labels or not datasets:
        raise ValueError("No labels or datasets extracted")

    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafcff")
    ax.tick_params(labelsize=7.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.22, linewidth=0.6, zorder=0)

    x = np.arange(len(labels))

    if ctype == "line":
        for i, ds in enumerate(datasets):
            vals  = ds["data"]
            xs    = [j for j, v in enumerate(vals) if v is not None]
            ys    = [v for v in vals if v is not None]
            color = AMBER if (i == 0 and cid == "dieselChart") else ("#888" if i > 0 else BLUE)
            style = "--" if (cid == "dieselChart" and i > 0) else "-"
            ax.plot(xs, ys, color=color, lw=2.0 if i == 0 else 1.2,
                    linestyle=style, marker="o" if i == 0 else None,
                    markersize=3.5, label=ds["label"], zorder=3)
            if i == 0:
                ax.fill_between(xs, ys, alpha=0.07, color=color, zorder=1)
        ax.legend(fontsize=7, loc="upper left", framealpha=0.5)
        # Annotate diesel spike
        if cid == "dieselChart" and datasets:
            vals = datasets[0]["data"]
            if len(vals) >= 16 and vals[15] is not None:
                ax.annotate("$5.64 ✓", xy=(15, vals[15]),
                            xytext=(13.2, vals[15] - 0.55),
                            fontsize=7, color=AMBER,
                            arrowprops=dict(arrowstyle="->", color=AMBER, lw=0.9))
        # x-tick thinning for dense labels
        if len(labels) > 10:
            step = 2
            ax.set_xticks(range(0, len(labels), step))
            ax.set_xticklabels(labels[::step], rotation=38, ha="right", fontsize=7)
        else:
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=7)

    elif ctype == "bar":
        vals = datasets[0]["data"] if datasets else []
        if cid == "sloosChart":
            colours = _sloos_colours(vals)
        elif cid == "smbDemandChart":
            colours = _smb_colours(len(vals))
        else:
            colours = [BLUE] * len(vals)
        ax.bar(x, vals, color=colours, width=0.65, zorder=2)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=7)

        if cid == "smbDemandChart":
            from matplotlib.patches import Patch
            ax.legend(handles=[
                Patch(facecolor=SMB_G,     label="Confirmed (SLOOS)"),
                Patch(facecolor="#b7e0c9", label="Estimated"),
            ], fontsize=7, loc="upper left", framealpha=0.5)
        if cid == "sloosChart":
            from matplotlib.patches import Patch
            ax.legend(handles=[
                Patch(facecolor=RED,    label="≥25% (severe)"),
                Patch(facecolor=YELLOW, label="10–24% (elevated)"),
                Patch(facecolor=GREEN,  label="<10% (easing)"),
            ], fontsize=7, loc="upper right", framealpha=0.5)

    if y_min is not None: ax.set_ylim(bottom=y_min)
    if y_max is not None: ax.set_ylim(top=y_max)
    plt.tight_layout(pad=0.4)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


# ── STEP 3: print CSS overrides ──────────────────────────────────────────────
PRINT_CSS = """
<style id="pdf-overrides">
.action-bar, .share-dropdown { display: none !important; }

@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
  @bottom-center {
    content: "Credit Intelligence Brief · Private · Page " counter(page) " of " counter(pages);
    font-family: Arial, sans-serif; font-size: 8pt; color: #8fa3b8;
  }
}
body { font-size: 11.5pt; line-height: 1.55; background: #fff !important; }

/* Keep components intact */
.story-card, .macro-section, .fuel-section, .deep-dive, .smb-section,
.thought-seed, .risk-card, .data-card, .fuel-cards-row, .charts-row,
.competitor-card, .validation-bar, .bias-legend, .brief-footer,
.bias-meter, .other-side, .synthesis-box, .so-what-box {
  break-inside: avoid; page-break-inside: avoid;
}
/* Section breaks */
.section-title       { page-break-before: always; margin-top: 0; }
.brief-footer        { page-break-before: always; }
.brief-header        { page-break-after:  avoid;  break-after: avoid; }

/* Charts */
canvas { display: none !important; }
.chart-static-img {
  width: 100%; max-height: 230px; object-fit: contain;
  display: block; margin: 6px 0;
}
/* Grids */
.charts-row       { grid-template-columns: 1fr 1fr; gap: 12px; }
.fuel-cards-row   { grid-template-columns: 1fr 1fr; gap: 12px; }
.smb-grid         { grid-template-columns: 1fr 1fr; gap: 12px; }
.bias-axes-grid   { grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.competitor-grid  { grid-template-columns: repeat(3, 1fr); gap: 10px; }
.data-cards       { grid-template-columns: repeat(3, 1fr); gap: 12px; }
.risk-cards       { grid-template-columns: repeat(3, 1fr); gap: 12px; }
.content          { max-width: 100%; padding: 6px 0; }

/* Print colour fidelity */
.brief-header, .validation-bar, .thought-seed, .brief-footer,
.bias-legend, .action-bar, .signal-reading {
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
/* Suppress href printout for action buttons */
a[class*="btn"]::after, .filter-btn::after { content: "" !important; }
</style>
"""


# ── STEP 4: assemble print HTML and convert ──────────────────────────────────
def html_to_pdf(html_path: Path, pdf_path: Path):
    from weasyprint import HTML

    html_text = html_path.read_text(encoding="utf-8")
    soup      = BeautifulSoup(html_text, "html.parser")

    # Render charts and inject <img> siblings
    chart_infos = _extract_chartjs_calls(html_text)
    for info in chart_infos:
        try:
            b64 = render_chart(info)
            img = soup.new_tag("img", src=b64,
                               alt=f"Chart: {info['canvas_id']}",
                               **{"class": "chart-static-img"})
            canvas = soup.find("canvas", {"id": info["canvas_id"]})
            if canvas:
                canvas.insert_after(img)
            print(f"    ✓ chart: {info['canvas_id']}")
        except Exception as e:
            print(f"    ✗ chart {info['canvas_id']}: {e}")

    # Inject print CSS
    head = soup.find("head")
    if head:
        head.append(BeautifulSoup(PRINT_CSS, "html.parser"))

    # Make CSS href absolute
    for link in soup.find_all("link", rel="stylesheet"):
        href = link.get("href", "")
        if not href.startswith(("http", "data:", "/")):
            link["href"] = (html_path.parent / href).resolve().as_uri()

    # Remove Chart.js CDN script (not needed)
    for script in soup.find_all("script", src=re.compile(r"chart", re.I)):
        script.decompose()

    print(f"    ⏳ weasyprint …")
    HTML(string=str(soup), base_url=str(html_path.parent)).write_pdf(str(pdf_path))
    print(f"    ✅ {pdf_path.name}")


# ── CLI ───────────────────────────────────────────────────────────────────────
BRIEFS_DIR = Path("/sessions/determined-kind-noether/mnt/Documents/Claude/Projects/Credit Intelligence Report")
OUT_DIR    = Path("/sessions/determined-kind-noether/mnt/Downloads")

ALL_BRIEFS = [
    (BRIEFS_DIR / "brief-v2.html",                    "brief-edition-001.pdf"),
    (BRIEFS_DIR / "briefs" / "brief-2026-04-06.html", "brief-edition-002.pdf"),
    (BRIEFS_DIR / "briefs" / "brief-2026-04-08.html", "brief-edition-003.pdf"),
]

def convert_all():
    for src, dst_name in ALL_BRIEFS:
        print(f"\n── {src.name} → {dst_name}")
        if not src.exists():
            print(f"    ✗ source not found"); continue
        html_to_pdf(src, OUT_DIR / dst_name)

def convert_one(html_str: str, out_str: str = None):
    src = Path(html_str)
    dst = Path(out_str) if out_str else OUT_DIR / (src.stem + ".pdf")
    print(f"\n── {src.name} → {dst.name}")
    html_to_pdf(src, dst)

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--all":
        convert_all()
    else:
        convert_one(*args)
