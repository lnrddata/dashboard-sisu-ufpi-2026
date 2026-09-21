"""Tema visual: paleta, template Plotly, CSS e componentes reutilizáveis."""
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

NAVY, AZUL, TEAL, CINZA = "#0B1F3A", "#1F5FBF", "#12A594", "#C9D1DC"
VERDE, AMBAR, VERM = "#1E9E6A", "#E5A100", "#D64545"
COR_COTA = {"AC": "#1F5FBF", "PPI-1": "#12A594", "PPI-2": "#7AD3C6", "EP-1": "#E58A00",
            "EP-2": "#F4C26B", "PCD-1": "#8E5BD6", "PCD-2": "#C2A5F0", "Q-1": "#D64545"}

pio.templates["sisu"] = go.layout.Template(layout=dict(
    font=dict(family="Segoe UI, Helvetica, Arial, sans-serif", size=13, color=NAVY),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", separators=",.",
    margin=dict(l=8, r=8, t=48, b=8), title=dict(x=0, font=dict(size=14)),
    xaxis=dict(showgrid=False, zeroline=False, linecolor="#DDE3EC"),
    yaxis=dict(gridcolor="#EEF1F6", zeroline=False), hoverlabel=dict(bgcolor="white"),
    legend=dict(orientation="h", y=1.12, x=0)))
pio.templates.default = "sisu"

_CSS = """<style>
#MainMenu, footer {visibility:hidden}
.stApp [data-testid="stSidebar"] {width:18rem !important; min-width:18rem !important}
.block-container {padding-top:11.5rem; padding-left:1rem; padding-right:1rem; max-width:none; width:100%; margin-left:0; margin-right:0; box-sizing:border-box}
.stPlotlyChart, [data-testid="stPlotlyChart"] {width:100% !important;}
[data-testid="stHorizontalBlock"] {width:100%;}
[data-testid="stVerticalBlockBorderWrapper"] > div {width:100%;}
[data-testid="stVerticalBlockBorderWrapper"] {background:#fff; border:1px solid #E6EAF1 !important;
  border-radius:12px; box-shadow:0 1px 2px rgba(11,31,58,.05)}
.hdr h1 {margin:0; font-size:1.35rem; color:#0B1F3A; letter-spacing:-.01em}
.hdr p {margin:.25rem 0 1.1rem; color:#5B6B82}
.kpi {background:#fff; border-radius:10px; padding:14px 16px; border-top:4px solid var(--c);
  box-shadow:0 1px 2px rgba(11,31,58,.06); margin-bottom:.5rem}
.kl {font-size:.82rem; color:#5B6B82; font-weight:600}
.kv {font-size:1.9rem; font-weight:700; color:#0B1F3A; line-height:1.25}
.ks {font-size:.8rem; color:#7A8799}
.kpi.sm {padding:10px 14px} .kpi.sm .kv {font-size:1.25rem}
.badge {display:inline-block; color:#fff; padding:4px 14px; border-radius:999px; font-weight:600}
.pbc {display:flex; align-items:center; gap:10px; min-width:150px}
.pbc .t {flex:1; height:10px; background:#E3EAF5; border-radius:5px; overflow:hidden}
.pbc .t i {display:block; height:100%; background:#1F5FBF; border-radius:5px}
.pbc b {min-width:52px; text-align:right; color:#0B1F3A; font-variant-numeric:tabular-nums}
.pb {display:grid; grid-template-columns:78px 1fr 118px; gap:12px; align-items:center; margin:11px 0; font-size:.92rem}
.pb .n {text-align:right; color:#5B6B82; font-variant-numeric:tabular-nums}
.tb {width:100%; border-collapse:collapse; font-size:.9rem}
.tb th {text-align:right; color:#5B6B82; font-weight:600; padding:6px 8px; border-bottom:1px solid #E6EAF1}
.tb td {text-align:right; padding:9px 8px; border-bottom:1px solid #F0F3F8; font-variant-numeric:tabular-nums}
.tb th:first-child, .tb td:first-child {text-align:left}
.tb tr.tot td {border-top:2px solid #C9D1DC; border-bottom:none; background:#F7F9FC}
</style>"""


def css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header(titulo: str, sub: str) -> None:
    st.markdown(f'<div class="hdr"><h1>{titulo}</h1><p>{sub}</p></div>', unsafe_allow_html=True)


def kpi_card(label: str, valor: str, sub: str = "", cor: str = AZUL, sm: bool = False) -> None:
    st.markdown(f'<div class="kpi{" sm" if sm else ""}" style="--c:{cor}"><div class="kl">{label}</div>'
                f'<div class="kv">{valor}</div><div class="ks">{sub}</div></div>', unsafe_allow_html=True)


def fi(n) -> str:
    """Inteiro pt-BR (5.074)."""
    return "n/d" if pd.isna(n) else f"{n:,.0f}".replace(",", ".")


def fp(x, d: int = 1) -> str:
    """Percentual pt-BR (92,0%)."""
    return "n/d" if pd.isna(x) else f"{x * 100:.{d}f}%".replace(".", ",")


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False}, width="stretch")


def barra(p: float) -> str:
    """Barra de progresso em HTML (azul institucional); a largura é limitada a 100%."""
    w = 0 if pd.isna(p) else min(max(p, 0), 1) * 100
    return f'<div class="pbc"><div class="t"><i style="width:{w:.1f}%"></i></div><b>{fp(p)}</b></div>'


def progresso_linhas(itens) -> str:
    """Lista de barras de progresso: itens = [(rótulo, percentual, texto)]."""
    return "".join(f'<div class="pb"><span>{r}</span>{barra(p)}<span class="n">{tx}</span></div>' for r, p, tx in itens)


def tabela_barra(cab, linhas, pcts, total=None) -> str:
    """Tabela HTML com barra de progresso na última coluna. `total` = (linha, pct) opcional."""
    th = "".join(f"<th>{h}</th>" for h in [*cab, "Ocupação"])
    tr = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + f"<td>{barra(p)}</td></tr>" for r, p in zip(linhas, pcts))
    if total:
        tr += '<tr class="tot">' + "".join(f"<td><b>{x}</b></td>" for x in total[0]) + f"<td>{barra(total[1])}</td></tr>"
    return f'<table class="tb"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'
