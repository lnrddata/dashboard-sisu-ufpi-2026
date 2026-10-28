"""Página 1: visão geral do processo (KPIs e gráficos)."""
import inspect
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import COTAS, agg, filtrar, get_data, unicos
from theme import AZUL, AZUL_CLARO, CINZA, NAVY, anel_html, barra, chart_head, fi, fp, header, icone, kpi_grid, progresso_linhas, show, tabela_barra

# O "Select all" (em inglês) é redundante aqui: seleção vazia já significa "todos". O parâmetro só existe em versões novas do Streamlit.
_SEM_TODOS = {"select_all": False} if "select_all" in inspect.signature(st.multiselect).parameters else {}

D = get_data()
v, c, l, lab, nmax = D["v"], D["c"], D["l"], D["lab"], D["nmax"]
header("Visão geral do processo seletivo", f"Dados consolidados até a última chamada · arquivo atualizado em {D['atualizado']}")

# ---------------------------------------------------------------- filtros
NOMES = {"grau": "Grau", "turno": "Turno", "semestre": "Semestre", "cota": "Cota"}

# Ordem institucional dos centros: primeiro Teresina, depois os campi do interior.
# CEAD fica entre os dois grupos por não ser campus presencial.
ORDEM_CENTROS = ["CCS", "CCN", "CCHL", "CCE", "CT", "CCA", "CEAD", "CSHNB", "CPCE", "CAFS"]

def chave_centro(x):
    try:
        return ORDEM_CENTROS.index(x)
    except ValueError:
        return len(ORDEM_CENTROS)


def limpar():
    for k in ("centro", "curso_key", *NOMES):
        st.session_state.pop("f_" + k, None)


def opts(col):
    o = list(set(v[col].dropna()) | set(c[col].dropna()))
    if col == "cota":
        return sorted(o, key=lambda x: COTAS.index(x) if x in COTAS else 99)
    if col == "centro":
        return sorted(o, key=chave_centro)
    return sorted(o)


sb = st.sidebar
sb.header("Filtros")
sel = {"centro": sb.multiselect("Centro / Campus", opts("centro"), key="f_centro", placeholder="Selecione uma ou mais opções", **_SEM_TODOS)}
pool = pd.concat([v[["centro", "curso_key"]], c[["centro", "curso_key"]]]).drop_duplicates()
if sel["centro"]:
    pool = pool[pool.centro.isin(sel["centro"])]
cursos = sorted(set(pool.curso_key), key=lambda k: lab[k])
st.session_state["f_curso_key"] = [k for k in st.session_state.get("f_curso_key", []) if k in cursos]
sel["curso_key"] = sb.multiselect("Curso", cursos, format_func=lab.get, key="f_curso_key", placeholder="Selecione uma ou mais opções", **_SEM_TODOS)
for col, nome in NOMES.items():
    sel[col] = sb.multiselect(nome, opts(col), key="f_" + col, placeholder="Selecione uma ou mais opções", **_SEM_TODOS)
sb.button("Limpar filtros", on_click=limpar)
if sb.button("Recarregar dados"):
    st.cache_data.clear()
    st.rerun()

vf = filtrar(v, sel)
c_all = filtrar(c, sel)
# O painel trabalha sempre com o processo consolidado até a última chamada.
cf = unicos(c_all)
cv = cf[cf.centro.isin(vf.centro.unique())]          # centros presentes no quadro de vagas, incluindo CEAD
lf = filtrar(l[~l.convocado], {k: sel[k] for k in ("centro", "curso_key", "cota")})

# ---------------------------------------------------------------- KPIs
BLUE_L = "#D6E2F5"
nv, ncv, npd = int(vf.vagas.sum()), len(cf), int(cf.pend.sum())
ocup = int(cv.mat.sum())
pre = ocup / nv if nv else np.nan
nab = max(nv - ocup, 0)                                   # vagas remanescentes (com remanejamento entre cotas)
nl = lf.inscricao.nunique()

cards = [("Vagas ofertadas", fi(nv), "conforme quadro de vagas", AZUL, icone("capelo")),
         ("Convocados", fi(ncv), f"{fp(len(cv) / nv if nv else np.nan)} das vagas", AZUL, icone("megafone")),
         ("Vagas ocupadas", fi(ocup), "matrículas confirmadas", AZUL, icone("check")),
         ("Ocupação", fp(pre), "ocupadas ÷ ofertadas", AZUL, icone("grafico")),
         ("Vagas remanescentes", fi(nab), "ofertadas − ocupadas", AZUL, icone("vagas"))]
if npd:
    cards.append(("Pendentes", fi(npd), "sem matrícula nem motivo", NAVY, icone("pendente")))
kpi_grid(cards)
peq = [("Cursos ofertados", fi(vf.groupby(["centro", "curso_key"]).ngroups), icone("livro")),
       ("Centros", fi(len(set(vf.centro) | set(cf.centro))), icone("predio")),
       ("Na lista de espera", fi(nl), icone("pessoas")),
       ("Candidatos por vaga remanescente", f"{nl / nab:.1f}".replace(".", ",") if nab else "n/d", icone("balanca"))]
kpi_grid([(a, b, "", CINZA, ic) for a, b, ic in peq], sm=True)


# ---------------------------------------------------------------- destaque
cursos_n = fi(vf.groupby(["centro", "curso_key"]).ngroups)

# três destaques que não repetem os indicadores acima (e que respeitam os filtros)
destaques = []
dc = agg(vf, cv, "centro")
dc = dc[dc.vagas > 0].reset_index(drop=True)
if len(dc) >= 2:
    mx, mn = dc.loc[dc.preench.idxmax()], dc.loc[dc.preench.idxmin()]
    destaques += [("Maior ocupação", fp(mx.preench), escape(str(mx.centro))), ("Menor ocupação", fp(mn.preench), escape(str(mn.centro)))]
dm = agg(vf, cv, "cota")
dm = dm[dm.vagas > 0].reset_index(drop=True)
if len(dm):
    dm["sobra"] = (dm.vagas - dm.matriculados).clip(lower=0)
    if dm.sobra.max() > 0:
        top = dm.loc[dm.sobra.idxmax()]
        destaques.append(("Mais vagas remanescentes", fi(top.sobra), f"modalidade {escape(str(top.cota))}"))
metricas = ('<div class="metricas">' + "".join(f'<div class="met"><div class="ml">{a}</div><div class="mv">{b}</div><div class="ms">{c_}</div></div>'
                                              for a, b, c_ in destaques) + "</div>") if destaques else ""
st.markdown(
    '<div class="hero">' + anel_html(pre) + '<div class="txt">'
    f'<div class="ht">{fp(pre)} das vagas ofertadas já foram ocupadas</div>'
    f'<p>{fi(ocup)} de {fi(nv)} vagas confirmadas, com {fi(nab)} vagas remanescentes distribuídas em {cursos_n} cursos.</p>'
    '</div>' + metricas + '</div>', unsafe_allow_html=True)


def rem(d):
    """Vagas remanescentes de cada linha: ofertadas − ocupadas (nunca negativo)."""
    return (d.vagas - d.matriculados).clip(lower=0)


col1, col2 = st.columns(2)

# ---------------------------------------------------------------- 1) ocupação por centro
with col1, st.container(border=True):
    chart_head("Ocupação por centro", "Percentual de vagas ocupadas em cada centro/campus.")
    d = agg(vf, cv, "centro")
    d = d[d.vagas > 0].copy()
    d["_ordem"] = d.centro.map(chave_centro)
    d = d.sort_values("_ordem").drop(columns="_ordem")
    st.markdown(progresso_linhas([(r.centro, r.preench, f"{fi(r.matriculados)} / {fi(r.vagas)}") for r in d.itertuples()])
                or "Sem dados para os filtros escolhidos.", unsafe_allow_html=True)

# ---------------------------------------------------------------- 2) ocupação por modalidade
with col2, st.container(border=True):
    chart_head("Ocupação por modalidade", "Vagas ofertadas, ocupadas e remanescentes em cada ação afirmativa.")
    d = agg(vf, cv, "cota")
    d = d[d.vagas > 0].assign(r=rem).sort_values("cota", key=lambda s: s.map(lambda x: COTAS.index(x) if x in COTAS else 99))
    linhas = [[r.cota, fi(r.vagas), fi(r.matriculados), fi(r.r)] for r in d.itertuples()]
    tot = ([ "Total", fi(d.vagas.sum()), fi(d.matriculados.sum()), fi(max(d.vagas.sum() - d.matriculados.sum(), 0))], d.matriculados.sum() / d.vagas.sum()) if len(d) else None
    st.markdown(tabela_barra(["Modalidade", "Vagas ofertadas", "Vagas ocupadas", "Vagas remanescentes"], linhas, list(d.preench), tot)
                if len(d) else "Sem dados para os filtros escolhidos.", unsafe_allow_html=True)

# ---------------------------------------------------------------- 3) ocupação por chamada
lin = []
for k in sorted(c_all.chamada_n.dropna().unique()):
    ac = unicos(c_all[c_all.chamada_n <= k])
    oc = int(ac[ac.centro.isin(vf.centro.unique())].mat.sum())     # ocupação acumulada até a chamada k
    lin.append((f"{k}ª chamada", oc, max(nv - oc, 0), oc / nv if nv else np.nan))
f3 = go.Figure()
if lin:
    x, oc_, rm_, pc_ = zip(*lin)
    f3.add_bar(x=x, y=oc_, name="Vagas ocupadas", marker_color=AZUL, width=.3, text=[fi(a) for a in oc_],
               textposition="inside", textfont=dict(color="white"))
    f3.add_bar(x=x, y=rm_, name="Vagas remanescentes", marker_color=BLUE_L, width=.3, text=[fi(a) for a in rm_],
               textposition="inside", textfont=dict(color=NAVY))
    # percentual de ocupação no topo de cada barra, com o acréscimo sobre a chamada anterior (substitui a linha, que repetia a mesma informação)
    rotulos = []
    for i_, p_ in enumerate(pc_):
        extra = f"<br><span style='font-size:12px;color:#5B6B82'>{(p_ - pc_[i_ - 1]) * 100:+.1f}".replace(".", ",") + " p.p. na chamada</span>" if i_ else ""
        rotulos.append(f"<b>{fp(p_)}</b>" + extra)
    f3.add_scatter(x=x, y=[a + b for a, b in zip(oc_, rm_)], mode="text", text=rotulos, textposition="top center", textfont=dict(size=17, color=NAVY),
                   hoverinfo="skip", cliponaxis=False)
f3.update_layout(showlegend=False, height=340, barmode="stack", margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                 yaxis=dict(range=[0, max(nv, 1) * 1.3], visible=False),
                 xaxis=dict(type="category", tickmode="array", tickvals=list(x), ticktext=list(x), tickfont=dict(size=14),
                            showticklabels=True, ticklabeloverflow="allow", automargin=True))
with st.container(border=True):
    chart_head(f"Ocupação por chamada · {fi(nv)} vagas ofertadas", "Acumulado até cada chamada. O percentual no topo é a ocupação, com o acréscimo sobre a chamada anterior.",
               [(AZUL, "Vagas ocupadas"), (AZUL_CLARO, "Vagas remanescentes")])
    show(f3)

# ---------------------------------------------------------------- 4) tabela por curso / centro
with st.container(border=True):
    chart_head("Vagas e ocupação por curso", "Detalhe por centro, curso, grau e turno, com a ocupação acumulada em cada chamada.")
    niveis = {
        "Centro": ["centro"],
        "Centro e curso": ["centro", "curso"],
        "Centro, curso e grau": ["centro", "curso", "grau"],
        "Centro, curso, grau e turno": ["centro", "curso", "grau", "turno"],
    }
    nivel = st.segmented_control("Detalhar por", list(niveis), default="Centro e curso") or "Centro e curso"
    dims = niveis[nivel]
    t = agg(vf, cf, dims)
    t = t.assign(rem=rem(t))
    # Mantém os centros na ordem institucional: Teresina primeiro, interior depois.
    t["_ordem_centro"] = t["centro"].map(chave_centro)
    outras_dims = [d for d in dims if d != "centro"]
    t = t.sort_values(["_ordem_centro", *outras_dims], kind="stable").drop(columns="_ordem_centro").reset_index(drop=True)

    # Ocupação acumulada em cada chamada: conta matrículas confirmadas
    # entre a 1ª chamada e a chamada indicada, sem duplicar o candidato.
    chamadas = sorted({int(k) for k in cf.chamada_n.dropna().unique()})
    for k in chamadas:
        ck = cf[cf.chamada_n <= k]
        uk = unicos(ck)
        oc = uk.groupby(dims).mat.sum().rename(f"ocup_{int(k)}")
        t = t.join(oc, on=dims)
        t[f"ocup_{int(k)}"] = t[f"ocup_{int(k)}"].fillna(0).astype(int)

    nomes = {"centro": "Centro", "curso": "Curso", "grau": "Grau", "turno": "Turno"}
    colunas_ocup = [f"ocup_{int(k)}" for k in chamadas]
    ocup_pct = (t.matriculados / t.vagas.where(t.vagas > 0)).astype(float)          # vazio quando não há vagas cadastradas
    cab = ([nomes[d_] for d_ in dims] + ["Vagas ofertadas", "Vagas ocupadas", "Vagas remanescentes"]
           + [f"Ocupadas até a {int(k)}ª chamada" for k in chamadas] + ["Ocupação"])
    th = "".join(f'<th class="l">{h}</th>' if i < len(dims) else f"<th>{h}</th>" for i, h in enumerate(cab))
    linhas = []
    for i, r in t.iterrows():
        tds = "".join(f'<td class="l">{escape(str(r[d_]))}</td>' for d_ in dims)
        tds += "".join(f"<td>{fi(r[c_])}</td>" for c_ in ("vagas", "matriculados", "rem", *colunas_ocup))
        tds += f"<td>{barra(ocup_pct[i])}</td>" if pd.notna(ocup_pct[i]) else "<td>n/d</td>"
        linhas.append(f"<tr>{tds}</tr>")
    st.markdown('<div class="tb-wrap tb-rolagem"><table class="tb"><thead><tr>' + th + "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table></div>",
                unsafe_allow_html=True)

    exp = t[[*dims, "vagas", "matriculados", "rem", *colunas_ocup]].rename(columns={
        **nomes, "vagas": "Vagas ofertadas", "matriculados": "Vagas ocupadas", "rem": "Vagas remanescentes",
        **{f"ocup_{int(k)}": f"Ocupadas até a {int(k)}ª chamada" for k in chamadas}})
    for c_ in ("Vagas ofertadas", "Vagas ocupadas", "Vagas remanescentes"):
        exp[c_] = exp[c_].round().astype("Int64")                                   # inteiros, sem "50,0"
    exp["Ocupação (%)"] = (ocup_pct * 100).round(1)
    st.download_button("Baixar tabela (CSV)", exp.to_csv(sep=";", index=False, decimal=",").encode("utf-8-sig"),
                       file_name="vagas_ocupacao_por_curso.csv", mime="text/csv", icon=":material/download:")

st.caption("Ocupação = vagas ocupadas (matrículas confirmadas) ÷ vagas ofertadas. O quadro considera todos os centros presentes na base de vagas, incluindo o CEAD. "
           "Por modalidade a ocupação pode passar de 100%: vagas não preenchidas em uma modalidade migram para outra (remanejamento), "
           "por isso remanescentes por linha não precisam somar o total.")
