"""Gráficos da Página 2: histograma das notas (Plotly) e vagas por cota (HTML/CSS, pílulas sem emenda e responsivas)."""
import html

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from config import COTA_DESC
from theme import AZUL, AZUL_CLARO, AZUL_ESCURO, NAVY, chart_head, fi, fp, show

AZ_MEDIO = "#A9C2EC"                      # notas menores
VOCE = NAVY                               # mesma cor do marcador "Você" da régua (azul-marinho institucional)
# vagas abertas: mesmo azul claro de "vagas remanescentes" da página 1 (AZUL_CLARO); texto em azul escuro (≥ 4,5:1)
CINZA_TXT = "#5B6B82"                      # cinza de texto com contraste ≥ 4,5:1
TRANSP = "rgba(0,0,0,0)"
BASE = dict(showlegend=False, title=None, font=dict(size=13, color=NAVY), bargap=.35, paper_bgcolor=TRANSP, plot_bgcolor=TRANSP)

cabecalho = chart_head  # alias: cabeçalho de gráfico compartilhado com a Página 1


def fig_notas(notas, nota, altura=320):
    """Histograma: notas maiores (azul), sua faixa (azul-marinho, como o "Você" da régua) e menores (azul claro).
    As barras têm topo arredondado e base reta: o arredondamento de baixo fica abaixo do eixo e é cortado pelo gráfico."""
    notas = np.asarray(notas, dtype=float)
    nb = int(np.clip(round(np.sqrt(max(len(notas), 1)) * 1.3), 8, 24))      # nº de faixas conforme o tamanho da fila
    cnt, ed = np.histogram(notas, bins=nb)
    mid, bw = (ed[:-1] + ed[1:]) / 2, ed[1] - ed[0]
    meu = int(min(max(np.searchsorted(ed, nota, side="right") - 1, 0), len(cnt) - 1))
    ix = np.arange(len(cnt))
    topo = max(int(cnt.max()), 1)
    piso = topo * .08                                                        # parte da barra que fica abaixo do eixo (cortada)
    fig = go.Figure()
    for cor, m in ((AZUL, ix > meu), (VOCE, ix == meu), (AZ_MEDIO, ix < meu)):
        fig.add_bar(x=mid[m], y=cnt[m] + piso, base=-piso, width=bw * .86, marker=dict(color=cor, cornerradius=6),
                    customdata=np.c_[ed[:-1][m], ed[1:][m], cnt[m]],
                    hovertemplate="Notas de %{customdata[0]:.0f} a %{customdata[1]:.0f}<br><b>%{customdata[2]}</b> candidatos<extra></extra>")
    rel = (nota - min(ed[0], nota)) / max(max(ed[-1], nota) - min(ed[0], nota), 1e-9)
    # "pino": linha da etiqueta até o topo da sua barra (não atravessa mais as outras barras)
    fig.add_shape(type="line", x0=nota, x1=nota, xref="x", y0=int(cnt[meu]), y1=topo * 1.12, yref="y", line=dict(color=NAVY, width=2))
    fig.add_annotation(x=nota, xref="x", y=1, yref="paper", yshift=4, showarrow=False, bgcolor=VOCE, borderpad=5,
                       text=f"<b>Sua nota: {nota:.2f}</b>".replace(".", ","), font=dict(color="white", size=13), yanchor="bottom",
                       xanchor="left" if rel < .15 else "right" if rel > .85 else "center")
    lo, hi = min(ed[0], nota), max(ed[-1], nota)          # garante que a nota apareça mesmo fora das faixas
    span = hi - lo
    eixo = dict(size=13, color=CINZA_TXT)
    fig.update_layout(**dict(BASE, bargap=0, height=altura, margin=dict(l=8, r=16, t=40, b=8)), barmode="overlay",
                      xaxis=dict(title=dict(text="Nota", standoff=8, font=eixo), automargin=True, showgrid=False, tickformat=".0f" if span >= 6 else ".1f", nticks=7 if span >= 6 else 4,
                                 tickfont=eixo, range=[lo - bw / 2, hi + bw / 2], linecolor="#DDE3EC", ticks="outside", tickcolor="#DDE3EC"),
                      yaxis=dict(title=dict(text="Candidatos", standoff=8, font=eixo), automargin=True, tickformat="d", tickfont=eixo,
                                 dtick=max(1, -(-topo // 5)), range=[0, topo * 1.12], gridcolor="#E9EDF4", griddash="dot", zeroline=False))
    return fig


_CSS_VAGAS = """<style>
.vg{container-type:inline-size;display:grid;gap:6px}
.vg-row{display:grid;grid-template-columns:minmax(112px,150px) 1fr 112px;align-items:center;gap:6px 14px;padding:8px 14px;border-radius:12px}
.vg-row.meu{background:#EAF1FC;box-shadow:inset 4px 0 0 #1F5FBF}
.vg-c{font-weight:800;color:#0B1F3A;font-size:.98rem;line-height:1.25}
.vg-row.meu .vg-c{color:#1F5FBF}
.vg-tag{display:inline-block;margin-left:8px;padding:1px 9px;border-radius:999px;background:#1F5FBF;color:#fff;font-size:.75rem;font-weight:700;vertical-align:1px}
.vg-d{display:block;color:#5B6B82;font-size:.82rem;line-height:1.25}
.vg-bar{display:flex;height:20px;border-radius:999px;overflow:hidden;background:#E3EAF5;box-shadow:0 0 0 1px #A9C2EC;
  animation:vgrev .9s cubic-bezier(.2,.8,.2,1) both}
.vg-oc{flex:none;width:var(--w);background:linear-gradient(90deg,#2E6FD9,#1F5FBF)}
.vg-ab{flex:1;background:#D6E2F5}
.vg-nd{background:repeating-linear-gradient(135deg,#DDE3EC 0 6px,#EDF0F5 6px 12px)}
.vg-n{font-size:.9rem;line-height:1.3;color:#0B1F3A;font-variant-numeric:tabular-nums;white-space:nowrap}
.vg-a{display:block;color:#123D82;font-weight:600}.vg-a.zero{color:#5B6B82;font-weight:400}
@keyframes vgrev{from{clip-path:inset(0 100% 0 0 round 999px)}to{clip-path:inset(0 0 0 0 round 999px)}}
@container (max-width:400px){.vg-row{grid-template-columns:1fr 112px;gap:8px 12px;padding:8px 12px}.vg-bar{grid-column:1/-1;order:3}}
@media (prefers-reduced-motion:reduce){.vg-bar{animation:none}}
</style>"""


def vagas_html(d, cota, altura=0) -> str:
    """Uma linha por cota: nome e descrição, pílula única (ocupadas em azul + abertas em verde, 100% das vagas da cota) e números.
    A cota do candidato ganha fundo de destaque e a etiqueta "sua cota"."""
    linhas = []
    for x, r in d.iterrows():
        v, m = float(r.vagas), float(r.matriculados)
        ab = max(v - m, 0)
        pct = fp(m / v, 0) if v else "n/d"
        desc = html.escape(COTA_DESC.get(x, ""))
        meu = x == cota
        tag = '<span class="vg-tag">sua cota</span>' if meu else ""
        if v > 0:
            w = min(m / v, 1) * 100
            resto = "" if w >= 99.99 else "<i class='vg-ab'></i>"
            nums = (f'<b>{fi(m)}</b> / {fi(v)} · {pct}<span class="vg-a{"" if ab > 0 else " zero"}">'
                    f'{(fi(ab) + (" aberta" if ab == 1 else " abertas")) if ab > 0 else "lotada"}</span>')
            alt = f"{x}: {fi(m)} de {fi(v)} vagas ocupadas ({pct}); {fi(ab)} {'aberta' if ab == 1 else 'abertas'}"
            conteudo, extra = f'<i class="vg-oc" style="--w:{w:.2f}%"></i>{resto}', ""
        else:
            nums = f'<b>{fi(m)}</b> matriculados<span class="vg-a zero">sem vagas cadastradas</span>'
            alt = f"{x}: {fi(m)} matriculados; sem vagas cadastradas"
            conteudo, extra = "", " vg-nd"
        alt_attr = html.escape(alt)
        barra = f'<div role="img" aria-label="{alt_attr}" class="vg-bar{extra}">{conteudo}</div>'
        linhas.append(f'<div class="vg-row{" meu" if meu else ""}" title="{alt_attr}"><div><span class="vg-c">{html.escape(str(x))}</span>{tag}'
                      f'<span class="vg-d">{desc}</span></div>{barra}<div class="vg-n">{nums}</div></div>')
    min_h = f"min-height:{max(int(altura) - 8, 0)}px;grid-template-rows:repeat({len(linhas)},1fr);" if altura else ""
    return _CSS_VAGAS + f'<div class="vg" style="{min_h}">{"".join(linhas)}</div>'


def caixa_notas(notas, nota, a_frente, atras, altura):
    with st.container(border=True):
        cabecalho("Distribuição das notas na fila", "Onde a sua nota fica entre os candidatos que ainda aguardam nesta cota.",
                  [(AZUL, f"{fi(a_frente)} com nota maior"), (VOCE, "Sua faixa"), (AZ_MEDIO, f"{fi(atras)} com nota menor")])
        show(fig_notas(notas, nota, altura))


def caixa_vagas(d, cota, altura):
    with st.container(border=True):
        cabecalho("Vagas do seu curso por cota", f"Sua cota ({cota}) em destaque · cada barra representa 100% das vagas da cota",
                  [(AZUL, "Vagas ocupadas"), (AZUL_CLARO, "Vagas abertas")])
        st.markdown(vagas_html(d, cota, altura), unsafe_allow_html=True)
