"""Página 2: acompanhamento individual do candidato."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import COTAS, agg, get_data, norm, unicos
from theme import AMBAR, AZUL, CINZA, COR_COTA, VERDE, VERM, fi, fp, header, kpi_card, show

D = get_data()
v, c, l = D["v"], D["c"], D["l"]
header("Acompanhamento do candidato", "Busque pelo nome e veja sua situação e sua posição")
cu = unicos(c)
tab = agg(v, cu, ["centro", "curso_key", "cota"])
tab["abertas"] = (tab.vagas - tab.matriculados).clip(lower=0)
tab = tab.set_index(["centro", "curso_key", "cota"])

q = st.text_input("Nome", placeholder="Digite seu nome completo ou parte dele", label_visibility="collapsed")
toks = norm(q).split() if q else []
if len(q.strip()) < 3:
    st.info("Digite pelo menos 3 letras do nome. A busca ignora acentos e maiúsculas.")
    st.stop()


def casa(s):
    return np.logical_and.reduce([s.str.contains(t, regex=False) for t in toks])


ml, mc = l[casa(l.nome_key)], c[casa(c.nome_key) & (c.nome_key != "")]
ent = {(nk, ins): g.aluno.iloc[0] for (nk, ins), g in ml.groupby(["nome_key", "inscricao"])}
for nk, nome in mc.groupby("nome_key").aluno.first().items():
    if not any(k[0] == nk for k in ent):
        ent[(nk, None)] = nome
if not ent:
    st.warning("Nenhum candidato encontrado. Confira a grafia ou tente apenas nome e sobrenome.")
    st.stop()
chaves = sorted(ent, key=lambda k: ent[k])
if len(chaves) > 50:
    st.caption(f"{len(chaves)} resultados; mostrando os 50 primeiros. Refine a busca para reduzir.")
nomes_conv = set(mc.nome_key)


def rot(k):
    tags = (["convocado(a)"] if k[0] in nomes_conv else []) + ([f"lista de espera · insc. ****{str(k[1])[-4:]}"] if k[1] else [])
    return f"{ent[k].title()} — " + " · ".join(tags)


nk, ins = st.selectbox("Resultados", chaves[:50], format_func=rot)
h = c[c.nome_key == nk].sort_values("chamada_n")
L = l[l.inscricao == ins] if ins else l.iloc[0:0]


def comp(cen, ck, cota):
    """Convocados do curso por cota, com a cota do candidato em destaque."""
    d = cu[(cu.centro == cen) & (cu.curso_key == ck)].groupby("cota").size().reindex(COTAS).dropna()
    fig = go.Figure()
    for ct, k in d.items():
        fig.add_bar(y=[""], x=[k], name=ct, orientation="h", marker_color=COR_COTA.get(ct, CINZA), opacity=1 if ct == cota else .3,
                    text=f"{ct}<br>{int(k)}", textposition="inside", hovertemplate=f"{ct}: {int(k)} convocados<extra></extra>")
    fig.update_layout(barmode="stack", height=220, showlegend=False, xaxis_title=None, yaxis_visible=False,
                      margin=dict(l=16, r=16, t=58, b=20),
                      title="Convocados do curso por cota (a sua em destaque)")
    return fig


st.markdown(f"## {ent[(nk, ins)].title()}")
if len(h) and len(L):
    st.markdown(f"#### Convocado(a) em {h.iloc[-1].curso} e na lista de espera de {', '.join(sorted(set(L.curso)))}")

# ---------------------------------------------------------------- A) convocação
if len(h):
    u = h.iloc[-1]
    cor = {"Matriculado": VERDE, "Não matriculado": VERM, "Pendente": AMBAR}[u.situacao]
    motivo = f" · {u.motivo}" if pd.notna(u.motivo) else ""
    st.markdown(f'<span class="badge" style="background:{cor}">{u.situacao}{motivo}</span>', unsafe_allow_html=True)
    st.markdown(f"**{u.curso}** · {u.centro} · {u.turno} · {u.grau} · {u.semestre} · cota {u.cota} · CPF {u.cpf}")
    g = tab.loc[(u.centro, u.curso_key, u.cota)]
    k = st.columns(5)
    for col, (a, b) in zip(k, [("Vagas na cota", fi(g.vagas) if g.vagas else "n/d"), ("Convocados na cota", fi(g.convocados)),
                               ("Matriculados", fi(g.matriculados)), ("Indeferidos", fi(g.indeferidos)),
                               ("Preenchimento", fp(g.preench))]):
        with col:
            kpi_card(a, b, cor=AZUL, sm=True)
    with st.container(border=True):
        show(comp(u.centro, u.curso_key, u.cota))
    if len(h) > 1:
        st.markdown("**Histórico:** " + " → ".join(f"{r.chamada}: {r.curso} ({r.cota}), {r.situacao.lower()}" for r in h.itertuples()))
    st.caption("A base de convocações não traz nota nem classificação; por isso não há posição para quem já foi convocado(a).")

# ---------------------------------------------------------------- B) lista de espera
if len(L):
    T = L.merge(tab.reset_index()[["centro", "curso_key", "cota", "vagas", "convocados", "matriculados", "abertas"]],
                on=["centro", "curso_key", "cota"], how="left")
    T["a_frente"] = (T.pos_atual - 1).clip(lower=0)
    T["faltam"] = (T.pos_atual - T.abertas).clip(lower=0)
    T.loc[T.vagas.fillna(0) == 0, ["abertas", "faltam"]] = np.nan
    T["rel"] = np.where(T.convocado, 9, T.pos_atual / T.na_fila.clip(lower=1))
    st.markdown("### Lista de espera")
    show_t = pd.DataFrame({"Modalidade": T.cota, "Curso": T.curso + " · " + T.centro + " · " + T.turno,
                           "Posição original": T.classificacao, "Posição atual": T.pos_atual, "Na fila": T.na_fila,
                           "Nota": T.nota, "À frente": T.a_frente, "Vagas": T.vagas, "Convocados": T.convocados,
                           "Matriculados": T.matriculados, "Vagas abertas": T.abertas, "Faltam": T.faltam})
    st.dataframe(show_t, hide_index=True)
    idx = list(T.index)
    i = st.radio("Modalidade", idx, index=idx.index(T.rel.idxmin()), horizontal=True,
                 format_func=lambda j: f"{T.cota[j]} · {T.curso[j]} ({T.turno[j]})")
    r = T.loc[i]
    if r.convocado:
        st.info("Você já aparece como convocado(a) nesta modalidade.")
    else:
        msg = f"Você é o **{int(r.pos_atual)}º** da fila" + (f" (posição original: {int(r.classificacao)}º)" if r.pos_atual != r.classificacao else "") + "."
        if pd.isna(r.abertas):
            msg += " Não há vagas cadastradas para esta cota neste curso."
        elif r.pos_atual <= r.abertas:
            msg += f" Há {int(r.abertas)} vagas abertas nesta cota e sua posição está dentro desse número."
        else:
            msg += f" Há {int(r.abertas)} vagas abertas nesta cota; faltam {int(r.faltam)} serem liberadas para chegar a sua vez."
        st.success(msg)
    st.caption("Estimativa com base nos dados publicados; a convocação real segue o edital e o remanejamento entre cotas.")

    f1 = go.Figure(go.Bar(y=[""], x=[r.na_fila], orientation="h", marker_color="#E3E9F2", hoverinfo="skip"))
    f1.add_scatter(x=[r.pos_atual], y=[""], mode="markers+text", text=[f"{int(r.pos_atual)}º"], textposition="top center",
                   marker=dict(size=18, color=AZUL, symbol="diamond"), hovertemplate="Posição atual: %{x}<extra></extra>")
    if pd.notna(r.abertas):
        f1.add_vline(x=r.abertas, line_dash="dash", line_color=VERDE, annotation_text=f"vagas abertas ({int(r.abertas)})")
    f1.update_layout(title=f"Posição na fila (de {int(r.na_fila)})", height=320, showlegend=False, yaxis_visible=False,
                     margin=dict(l=16, r=16, t=64, b=30),
                     xaxis=dict(range=[0, max(r.na_fila, 1) * 1.08]))
    G = l[(l.centro == r.centro) & (l.curso_key == r.curso_key) & (l.grau == r.grau) & (l.turno == r.turno) & (l.cota == r.cota)]
    f2 = go.Figure(go.Histogram(x=G.nota, nbinsx=25, marker_color="#B9CDEE", hovertemplate="Nota: %{x}<br>%{y} candidatos<extra></extra>"))
    f2.add_vline(x=r.nota, line_color=AZUL, line_width=3, annotation_text=f"Sua nota: {r.nota:.2f}".replace(".", ","))
    f2.update_layout(title=f"Notas da fila: a sua supera {fp((G.nota < r.nota).mean(), 0)} dos candidatos", height=320, bargap=.05,
                 margin=dict(l=16, r=16, t=64, b=30))
    a, b = st.columns(2)
    for col, f in ((a, f1), (b, f2)):
        with col, st.container(border=True):
            show(f)
    with st.container(border=True):
        show(comp(r.centro, r.curso_key, r.cota))

st.caption(f"Considera até a {D['nmax']}ª chamada · {D['q']['Candidatos da lista de espera já convocados']} candidatos da lista de espera já aparecem como convocados.")
