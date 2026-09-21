"""Página 1: visão geral do processo (KPIs e gráficos)."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import COTAS, agg, filtrar, get_data, unicos
from theme import AZUL, CINZA, NAVY, fi, fp, header, kpi_card, progresso_linhas, show, tabela_barra

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
sel = {"centro": sb.multiselect("Centro / Campus", opts("centro"), key="f_centro")}
pool = pd.concat([v[["centro", "curso_key"]], c[["centro", "curso_key"]]]).drop_duplicates()
if sel["centro"]:
    pool = pool[pool.centro.isin(sel["centro"])]
cursos = sorted(set(pool.curso_key), key=lambda k: lab[k])
st.session_state["f_curso_key"] = [k for k in st.session_state.get("f_curso_key", []) if k in cursos]
sel["curso_key"] = sb.multiselect("Curso", cursos, format_func=lab.get, key="f_curso_key")
for col, nome in NOMES.items():
    sel[col] = sb.multiselect(nome, opts(col), key="f_" + col)
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

cards = [("Vagas ofertadas", fi(nv), "conforme quadro de vagas", AZUL),
         ("Convocados", fi(ncv), f"{fp(len(cv) / nv if nv else np.nan)} das vagas", AZUL),
         ("Vagas ocupadas", fi(ocup), "matrículas confirmadas", AZUL),
         ("Ocupação", fp(pre), "ocupadas ÷ ofertadas", AZUL),
         ("Vagas remanescentes", fi(nab), "ofertadas − ocupadas", AZUL)]
if npd:
    cards.append(("Pendentes", fi(npd), "sem matrícula nem motivo", NAVY))
for col, (a, b, s_, cor) in zip(st.columns(len(cards)), cards):
    with col:
        kpi_card(a, b, s_, cor)
peq = [("Cursos ofertados", fi(vf.groupby(["centro", "curso_key"]).ngroups)),
       ("Centros", fi(len(set(vf.centro) | set(cf.centro)))),
       ("Na lista de espera", fi(nl)),
       ("Candidatos por vaga remanescente", f"{nl / nab:.1f}".replace(".", ",") if nab else "n/d")]
for col, (a, b) in zip(st.columns(4), peq):
    with col:
        kpi_card(a, b, sm=True, cor=CINZA)


def rem(d):
    """Vagas remanescentes de cada linha: ofertadas − ocupadas (nunca negativo)."""
    return (d.vagas - d.matriculados).clip(lower=0)


col1, col2 = st.columns(2)

# ---------------------------------------------------------------- 1) ocupação por centro
with col1, st.container(border=True):
    st.markdown("**Ocupação por centro**")
    d = agg(vf, cv, "centro")
    d = d[d.vagas > 0].copy()
    d["_ordem"] = d.centro.map(chave_centro)
    d = d.sort_values("_ordem").drop(columns="_ordem")
    st.markdown(progresso_linhas([(r.centro, r.preench, f"{fi(r.matriculados)} / {fi(r.vagas)}") for r in d.itertuples()])
                or "Sem dados para os filtros escolhidos.", unsafe_allow_html=True)

# ---------------------------------------------------------------- 2) ocupação por modalidade
with col2, st.container(border=True):
    st.markdown("**Ocupação por modalidade**")
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
    f3.add_bar(x=x, y=oc_, name="Vagas ocupadas", marker_color=AZUL, width=.4, text=[fi(a) for a in oc_],
               textposition="inside", textfont=dict(color="white"))
    f3.add_bar(x=x, y=rm_, name="Vagas remanescentes", marker_color=BLUE_L, width=.4, text=[fi(a) for a in rm_],
               textposition="inside", textfont=dict(color=NAVY))
    f3.add_scatter(x=x, y=pc_, name="Ocupação acumulada", yaxis="y2", mode="lines+markers+text", text=[fp(a) for a in pc_],
                   textposition="top center", line=dict(color=NAVY, width=3), marker=dict(size=10, color=NAVY),
                   hovertemplate="%{x}: %{y:.1%}<extra></extra>")
f3.update_layout(title=f"Ocupação por chamada · {fi(nv)} vagas ofertadas", height=400, barmode="stack",
                 yaxis=dict(range=[0, max(nv, 1) * 1.5], visible=False),
                 yaxis2=dict(overlaying="y", range=[-3.13, 1.22], visible=False),   # linha fica acima das barras
                 legend=dict(orientation="h", y=-0.08, x=0))
with st.container(border=True):
    show(f3)

# ---------------------------------------------------------------- 4) tabela por curso / centro
with st.container(border=True):
    st.markdown("**Vagas e ocupação por curso**")
    niveis = {
        "Centro": ["centro"],
        "Centro e curso": ["centro", "curso"],
        "Centro, curso e grau": ["centro", "curso", "grau"],
        "Centro, curso e turno": ["centro", "curso", "turno"],
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

    nomes = {"centro": "Centro", "curso": "Curso", "grau": "Grau", "turno": "Turno",
             "vagas": "Vagas ofertadas", "matriculados": "Vagas ocupadas",
             "rem": "Vagas remanescentes"}
    vis = t[[*dims, "vagas", "matriculados", "rem"] + [f"ocup_{int(k)}" for k in chamadas]].rename(columns=nomes)
    vis = vis.rename(columns={f"ocup_{int(k)}": f"Ocupação {int(k)}ª chamada" for k in chamadas})

    cfg = {}
    for k in chamadas:
        col = f"Ocupação {int(k)}ª chamada"
        cfg[col] = st.column_config.NumberColumn(col, format="%d")
    st.dataframe(vis, hide_index=True, height=420, column_config=cfg)

st.caption("Ocupação = vagas ocupadas (matrículas confirmadas) ÷ vagas ofertadas. O quadro considera todos os centros presentes na base de vagas, incluindo o CEAD. "
           "Por modalidade a ocupação pode passar de 100%: vagas não preenchidas em uma modalidade migram para outra (remanejamento), "
           "por isso remanescentes por linha não precisam somar o total.")
