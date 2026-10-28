"""Tema visual: paleta, template Plotly, CSS e componentes reutilizáveis."""
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

NAVY, AZUL, TEAL, CINZA = "#0B1F3A", "#1F5FBF", "#12A594", "#C9D1DC"
VERDE, AMBAR, VERM = "#1E9E6A", "#E5A100", "#D64545"
AZUL_CLARO, AZUL_MEDIO, AZUL_ESCURO = "#D6E2F5", "#B9CDEE", "#123D82"
GRAD_AZUL = ["#2E6FD9", "#1F5FBF", "#123D82"]        # claro → escuro, para barras e o anel de ocupação
COR_COTA = {"AC": "#1F5FBF", "PPI-1": "#12A594", "PPI-2": "#7AD3C6", "EP-1": "#E58A00",
            "EP-2": "#F4C26B", "PCD-1": "#8E5BD6", "PCD-2": "#C2A5F0", "Q-1": "#D64545"}

pio.templates["sisu"] = go.layout.Template(layout=dict(
    font=dict(family="Segoe UI, Helvetica, Arial, sans-serif", size=13, color=NAVY),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", separators=",.",
    margin=dict(l=8, r=8, t=48, b=8), title=dict(x=0, font=dict(size=14)),
    barcornerradius=8,
    xaxis=dict(showgrid=False, zeroline=False, linecolor="#DDE3EC"),
    yaxis=dict(gridcolor="#EEF1F6", zeroline=False), hoverlabel=dict(bgcolor="white"),
    legend=dict(orientation="h", y=1.12, x=0)))
pio.templates.default = "sisu"

_CSS = """<style>
@keyframes subir {from {opacity:0; transform:translateY(10px)} to {opacity:1; transform:translateY(0)}}
#MainMenu, footer {visibility:hidden}
[data-testid="stExpandSidebarButton"] {position:fixed !important; left:.75rem !important; top:.9rem !important; z-index:1001}   /* botão de reabrir a barra: canto superior esquerdo, fora do banner */
[data-testid="stHeader"] {background:transparent !important}
/* filtros da barra lateral: o texto digitado herdava o branco da barra e sumia sobre o campo branco */
.stApp [data-testid="stSidebar"] [data-testid="stMultiSelect"] input {color:#0B1F3A !important; -webkit-text-fill-color:#0B1F3A !important; caret-color:#0B1F3A}
.stApp [data-testid="stSidebar"] [data-testid="stMultiSelect"] input::placeholder {color:#5B6B82 !important; -webkit-text-fill-color:#5B6B82 !important; opacity:1}
/* lista vazia: troca "No results" por português */
[data-testid="stMultiSelectDropdown"] [role="listbox"][data-empty="true"] [role="option"] > span {font-size:0 !important}
[data-testid="stMultiSelectDropdown"] [role="listbox"][data-empty="true"] [role="option"] > span::after {content:"Nenhum resultado"; font-size:.95rem; color:#5B6B82}   /* no celular o Streamlit pinta a barra e ela cobriria o banner */
[data-testid="InputInstructions"] {font-size:0 !important}      /* troca "Press Enter to apply" por português */
[data-testid="InputInstructions"]::after {content:"Pressione Enter para aplicar"; font-size:.78rem}
.stApp {background:radial-gradient(1200px 500px at 15% -10%, #EAF1FB 0%, #F4F6FA 45%) fixed}
.stApp [data-testid="stSidebar"] {width:19rem !important; min-width:19rem !important;
  background:linear-gradient(180deg,#0B1F3A 0%,#122C52 100%)}
.stApp [data-testid="stSidebar"] * {color:#E7ECF6 !important}
.stApp [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {background:#1F5FBF !important}
.stApp [data-testid="stSidebar"] button, .stApp [data-testid="stSidebar"] button * {color:#0B1F3A !important}
.stApp [data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.15)}
.stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {font-weight:600; letter-spacing:.02em}
.block-container {padding-top:.75rem; padding-left:1rem; padding-right:1rem; max-width:none; width:100%;
  margin-left:0; margin-right:0; box-sizing:border-box}
.stPlotlyChart, [data-testid="stPlotlyChart"] {width:100% !important;}
[data-testid="stHorizontalBlock"] {width:100%; flex-wrap:wrap; row-gap:1rem}
[data-testid="stColumn"] {min-width:min(100%, 280px)}   /* colunas quebram de linha em vez de serem espremidas */
[data-testid="stVerticalBlockBorderWrapper"] > div {width:100%;}
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {background:#fff; border:1px solid #E6EAF1 !important;
  border-radius:14px; box-shadow:0 2px 6px rgba(11,31,58,.06), 0 10px 24px -18px rgba(11,31,58,.25); animation:subir .45s ease both}
/* cartões lado a lado terminam na mesma altura */
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] {height:100%}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]) {flex:1 1 auto}
[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {height:100%; box-sizing:border-box}
.hdr .t {margin:0; font-size:1.4rem; color:#0B1F3A; letter-spacing:-.01em; font-weight:800}
.hdr p {margin:.25rem 0 1.2rem; color:#5B6B82}
.kpi {position:relative; overflow:hidden; background:#fff; border-radius:14px; padding:16px 18px 14px;
  box-shadow:0 2px 5px rgba(11,31,58,.05), 0 10px 22px -18px rgba(11,31,58,.3); margin-bottom:.6rem;
  border:1px solid #EEF1F7; transition:transform .18s ease, box-shadow .18s ease; animation:subir .45s ease both}
.kpi:hover {transform:translateY(-3px); box-shadow:0 6px 14px rgba(11,31,58,.09), 0 20px 34px -16px rgba(31,95,191,.3)}
.kpi::before {content:""; position:absolute; left:0; top:0; right:0; height:5px;
  background:linear-gradient(90deg, var(--c), color-mix(in srgb, var(--c) 55%, white))}
.kpi .ic svg {width:20px; height:20px; fill:none; stroke:color-mix(in srgb, var(--c) 78%, #0B1F3A); stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round}
.kpi.sm .ic svg {width:18px; height:18px; stroke:#4A5B75; stroke-width:1.9}
.kpi .ic {position:absolute; right:14px; top:14px; width:34px; height:34px; border-radius:10px; font-size:1.05rem;
  display:flex; align-items:center; justify-content:center; background:color-mix(in srgb, var(--c) 14%, white)}
.kl {font-size:.78rem; color:#5B6B82; font-weight:700; text-transform:uppercase; letter-spacing:.03em; margin-top:4px; padding-right:40px;
  overflow-wrap:normal; word-break:normal; hyphens:none}
.kpis {display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap:12px; margin-bottom:.6rem}
.kpis.sm {grid-template-columns:repeat(auto-fit, minmax(min(100%, 165px), 1fr))}
.kpis .kpi {margin:0; height:100%; box-sizing:border-box; min-width:0}
.kv {font-size:clamp(1.6rem, 1.2rem + .9vw, 2rem); font-weight:800; color:#0B1F3A; line-height:1.28; font-variant-numeric:tabular-nums; letter-spacing:-.01em}
.ks {font-size:.8rem; color:#5B6B82}
.kpi.sm {padding:11px 14px 10px} .kpi.sm .kv {font-size:1.3rem} .kpi.sm .ic {width:28px; height:28px; font-size:.9rem}
.kpi.sm .kl {padding-right:32px; font-size:.76rem}
.spark {display:block; margin-top:2px}
.badge {display:inline-block; color:#fff; padding:4px 14px; border-radius:999px; font-weight:600;
  box-shadow:0 4px 10px -4px rgba(0,0,0,.35)}
.pbc {display:flex; align-items:center; gap:10px; min-width:120px}
.tb-wrap {overflow-x:auto; max-width:100%}
.pbc .t {flex:1; height:11px; background:#E3EAF5; border-radius:6px; overflow:hidden}
.pbc .t i {display:block; height:100%; border-radius:6px; background:linear-gradient(90deg,#2E6FD9,#123D82)}
.pbc b {min-width:52px; text-align:right; color:#0B1F3A; font-variant-numeric:tabular-nums}
.pb {display:grid; grid-template-columns:78px 1fr 118px; gap:12px; align-items:center; margin:11px 0; font-size:.92rem}
.pb .n {text-align:right; color:#5B6B82; font-variant-numeric:tabular-nums}
.tb {width:100%; border-collapse:collapse; font-size:.9rem}
.tb th {text-align:right; color:#5B6B82; font-weight:600; padding:6px 8px; border-bottom:1px solid #E6EAF1}
.tb td {text-align:right; padding:9px 8px; border-bottom:1px solid #F0F3F8; font-variant-numeric:tabular-nums}
.tb th:first-child, .tb td:first-child, .tb th.l, .tb td.l {text-align:left}
.tb td:not(.l) {white-space:nowrap}
.tb-rolagem {max-height:460px; overflow:auto}
.tb-rolagem thead th {position:sticky; top:0; z-index:1; background:#fff; box-shadow:0 1px 0 #E6EAF1; border-bottom:none}
.tb tr.tot td {border-top:2px solid #C9D1DC; border-bottom:none; background:#F7F9FC}
.tb tbody tr:hover td {background:#F5F8FD}
.gx-h {font-size:1.15rem; font-weight:700; color:#0B1F3A}
.gx-s {color:#5B6B82; font-size:.88rem; margin:1px 0 6px}
.gx-l {display:flex; flex-wrap:wrap; gap:4px 18px; font-size:.82rem; color:#3D4F6B; margin:0 0 6px}
.gx-l i {display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:6px; vertical-align:-1px}
.hero {display:flex; align-items:center; gap:28px; flex-wrap:wrap; background:linear-gradient(120deg,#0B1F3A,#123D82 55%,#1F5FBF);
  border-radius:18px; padding:22px 28px; margin-bottom:1rem; box-shadow:0 14px 30px -16px rgba(11,31,58,.55); animation:subir .5s ease both}
.hero .ring {flex:none; width:150px; height:150px}
.hero {container-type:inline-size}
.hero .txt {flex:1 1 280px}
.hero .metricas {display:flex; align-items:stretch; margin-left:auto; padding-left:8px; border-left:1px solid rgba(255,255,255,.18)}
.hero .met {padding:4px 26px; min-width:150px}
.hero .met + .met {border-left:1px solid rgba(255,255,255,.12)}
.hero .met .ml {font-size:.78rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; color:#E6EEFB}
.hero .met .mv {font-size:2rem; font-weight:800; color:#fff; line-height:1.15; font-variant-numeric:tabular-nums}
.hero .met .ms {font-size:.88rem; color:#E6EEFB}
@container (max-width:900px) {.hero .metricas {margin-left:0; width:100%; padding:14px 0 0; border-left:0; border-top:1px solid rgba(255,255,255,.18)} .hero .met:first-child {padding-left:0}}
@container (max-width:560px) {.hero .metricas {flex-wrap:wrap; gap:12px 0} .hero .met {min-width:46%; padding:4px 12px 4px 0} .hero .met + .met {border-left:0}}
.hero .txt .ht {color:#fff; margin:0 0 6px; font-size:1.5rem; font-weight:800; line-height:1.25}
.hero .txt p {color:#C9D9F5; margin:0; font-size:.95rem; max-width:46ch}
.hero .pills {display:flex; gap:10px; flex-wrap:wrap; margin-top:12px}
.hero .pill {background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.25); color:#fff; border-radius:999px;
  padding:6px 14px; font-size:.82rem}
.hero .pill b {font-variant-numeric:tabular-nums}
</style>"""


def css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header(titulo: str, sub: str) -> None:
    st.markdown(f'<div class="hdr"><div class="t">{titulo}</div><p>{sub}</p></div>', unsafe_allow_html=True)


def _kpi_html(label: str, valor: str, sub: str = "", cor: str = AZUL, sm: bool = False, icon: str = "") -> str:
    ic = f'<div class="ic">{icon}</div>' if icon else ""
    return (f'<div class="kpi{" sm" if sm else ""}" style="--c:{cor}">{ic}<div class="kl">{label}</div>'
            f'<div class="kv">{valor}</div><div class="ks">{sub}</div></div>')


def kpi_card(label: str, valor: str, sub: str = "", cor: str = AZUL, sm: bool = False, icon: str = "") -> None:
    st.markdown(_kpi_html(label, valor, sub, cor, sm, icon), unsafe_allow_html=True)


def kpi_grid(cards, sm: bool = False) -> None:
    """Fileira de KPIs numa grade CSS responsiva. Substitui `st.columns`: os cartões quebram de linha conforme a
    largura disponível (sem espremer o texto) e os da mesma linha ficam com a mesma altura.
    cards = [(rótulo, valor, subtítulo, cor, ícone), ...]  (subtítulo, cor e ícone são opcionais)"""
    html = "".join(_kpi_html(*(list(c) + [""] * (5 - len(c)))[:3], cor=(c[3] if len(c) > 3 else AZUL), sm=sm,
                             icon=(c[4] if len(c) > 4 else "")) for c in cards)
    st.markdown(f'<div class="kpis{" sm" if sm else ""}">{html}</div>', unsafe_allow_html=True)


def chart_head(titulo: str, sub: str = "", legenda=()) -> None:
    """Cabeçalho de gráfico em HTML (título + subtítulo + legenda de quadradinhos coloridos)."""
    leg = "".join(f'<span><i style="background:{c}"></i>{t}</span>' for c, t in legenda)
    st.markdown(f'<div class="gx-h">{titulo}</div><div class="gx-s">{sub}</div>'
                + (f'<div class="gx-l">{leg}</div>' if leg else ""), unsafe_allow_html=True)


def donut(pct: float, titulo: str = "Ocupação geral", sub: str = "") -> go.Figure:
    """Anel de ocupação: azul institucional até `pct`, cinza claro no restante, valor grande ao centro."""
    p = 0.0 if pd.isna(pct) else max(min(pct, 1), 0)
    fig = go.Figure(go.Pie(values=[p, 1 - p], hole=.74, sort=False, direction="clockwise", rotation=-90,
                          marker=dict(colors=["#5B9CF0", "rgba(255,255,255,.18)"], line=dict(color="rgba(0,0,0,0)", width=0)),
                          textinfo="none", hoverinfo="skip"))
    fig.update_layout(showlegend=False, height=190, margin=dict(l=0, r=0, t=0, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      annotations=[dict(text=f"<b>{fp(pct)}</b>", x=.5, y=.57, showarrow=False, font=dict(size=30, color="#0B1F3A")),
                                  dict(text=titulo, x=.5, y=.36, showarrow=False, font=dict(size=12, color="#C9D9F5"))])
    return fig


_ICONES = {   # ícones de traço único (24×24), na cor de destaque do cartão
    "capelo": '<path d="M2 9.5 12 4.5l10 5-10 5Z"/><path d="M6 12v4.2c0 1.4 2.7 2.8 6 2.8s6-1.4 6-2.8V12"/><path d="M22 9.5V15"/>',
    "megafone": '<path d="M3 10.5v3a1 1 0 0 0 1 1h2.5L13 18.5v-13L6.5 9.5H4a1 1 0 0 0-1 1Z"/><path d="M16.5 9a4.2 4.2 0 0 1 0 6"/><path d="M6.8 14.5 8 19h2.6"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.8 2.8 5.4-5.8"/>',
    "grafico": '<circle cx="12" cy="12" r="9"/><path d="M12 3v9h9"/>',
    "vagas": '<rect x="3" y="3" width="7.5" height="7.5" rx="1.8"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.8"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.8"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.8" stroke-dasharray="2.4 2.4"/>',
    "pendente": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.2 2"/>',
    "livro": '<path d="M2.5 5.5H9a3 3 0 0 1 3 3V20a2.2 2.2 0 0 0-2.2-2.2H2.5Z"/><path d="M21.5 5.5H15a3 3 0 0 0-3 3V20a2.2 2.2 0 0 1 2.2-2.2h7.3Z"/>',
    "predio": '<path d="M2.5 9.5 12 4l9.5 5.5Z"/><path d="M5 20.5h14M6 10v8M10 10v8M14 10v8M18 10v8"/>',
    "pessoas": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.4 2.7-6 6-6s6 2.6 6 6"/><circle cx="17.2" cy="9.2" r="2.5"/><path d="M17.5 14.2c2.5.2 4.5 2.3 4.5 5.3"/>',
    "balanca": '<path d="M12 4v16M6 20.5h12M5 7.5h14"/><path d="M5 7.5 2.3 14a3.2 3.2 0 0 0 5.4 0Z"/><path d="M19 7.5 16.3 14a3.2 3.2 0 0 0 5.4 0Z"/>',
}


def icone(nome: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICONES[nome]}</svg>'


def anel_html(pct: float, rotulo: str = "Ocupação geral") -> str:
    """Anel de ocupação em SVG (para o cartão de destaque azul-escuro): trecho preenchido em azul claro e o valor ao centro."""
    ok = not pd.isna(pct)
    p = max(min(pct, 1), 0) if ok else 0.0
    circ = 2 * 3.14159265 * 50
    txt = fp(pct) if ok else "n/d"
    arco = (f'<circle cx="60" cy="60" r="50" fill="none" stroke="#5B9CF0" stroke-width="11" stroke-linecap="round" '
            f'stroke-dasharray="{p * circ:.2f} {circ:.2f}" transform="rotate(-90 60 60)"/>') if p > 0 else ""
    return (f'<svg class="ring" viewBox="0 0 120 120" role="img" aria-label="{rotulo}: {txt}">'
            '<circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,.16)" stroke-width="11"/>' + arco +
            f'<text x="60" y="58" text-anchor="middle" font-size="25" font-weight="800" fill="#fff">{txt}</text>'
            f'<text x="60" y="76" text-anchor="middle" font-size="10.5" fill="#C9D9F5">{rotulo}</text></svg>')


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
    return f'<div class="tb-wrap"><table class="tb"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
