"""Página 2: acompanhamento individual do candidato."""
import numpy as np
import pandas as pd
import streamlit as st

from data import COTA_DESC, COTAS, agg, get_data, norm, unicos
from graficos import caixa_notas, caixa_vagas
from regua import regua_html
from theme import AMBAR, AZUL, VERDE, VERM, fi, fp, header, kpi_grid

_CSS = """<style>
.ver{background:#fff;border:1px solid #E6EAF1;border-left:6px solid var(--c);border-radius:12px;padding:14px 18px;
  margin:.4rem 0 .9rem;box-shadow:0 2px 6px rgba(11,31,58,.06),0 10px 24px -18px rgba(11,31,58,.25);animation:subir .45s ease both}
.ver .vt{font-weight:800;font-size:1.15rem;color:#0B1F3A}.ver .vx{color:#3D4F6B;margin-top:2px}
.ficha{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px 20px;background:#fff;border:1px solid #E6EAF1;
  border-radius:14px;padding:14px 18px;margin:.6rem 0 .8rem}
.ficha .k{font-size:.76rem;text-transform:uppercase;letter-spacing:.04em;color:#5B6B82;font-weight:700}
.ficha .v{color:#0B1F3A;font-weight:600}
.tl{margin:.4rem 0 .2rem 8px;padding-left:22px;border-left:2px solid #DCE4F0}
.tl-i{position:relative;padding:0 0 14px}.tl-i:last-child{padding-bottom:0}
.tl-i::before{content:"";position:absolute;left:-30px;top:3px;width:14px;height:14px;border-radius:50%;background:var(--c);
  border:3px solid #fff;box-shadow:0 0 0 2px var(--c)}
.tl-i b{display:block;color:#0B1F3A}.tl-i span{color:#5B6B82;font-size:.9rem}
.passos{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:.4rem 0 1rem}
.passo{background:#fff;border:1px solid #E6EAF1;border-radius:14px;padding:14px 16px}
.passo .n{width:28px;height:28px;border-radius:50%;background:#1F5FBF;color:#fff;font-weight:800;display:flex;
  align-items:center;justify-content:center;margin-bottom:8px}
.sec{font-size:1.45rem;font-weight:800;color:#0B1F3A;margin:1.1rem 0 .5rem;letter-spacing:-.01em}
.passo b{color:#0B1F3A}.passo p{margin:.2rem 0 0;color:#5B6B82;font-size:.9rem}
</style>"""
st.markdown(_CSS, unsafe_allow_html=True)

_PARTICULAS = {"da", "de", "do", "das", "dos", "e"}
COR_SIT = {"Matriculado": VERDE, "Não matriculado": VERM, "Pendente": AMBAR}


def bonito(nome) -> str:
    """Nome próprio em caixa alta/baixa correta (mantém 'da', 'de', 'dos'... em minúsculas)."""
    p = str(nome).split()
    return " ".join(w.lower() if i and w.lower() in _PARTICULAS else w.capitalize() for i, w in enumerate(p))


def veredito(cor: str, titulo: str, texto: str) -> None:
    st.markdown(f'<div class="ver" style="--c:{cor}"><div class="vt">{titulo}</div><div class="vx">{texto}</div></div>',
                unsafe_allow_html=True)


D = get_data()
v, c, l = D["v"], D["c"], D["l"]
header("Acompanhamento do candidato", "Busque pelo nome e veja sua situação e sua posição")
cu = unicos(c)
tab = agg(v, cu, ["centro", "curso_key", "cota"])
tab["abertas"] = (tab.vagas - tab.matriculados).clip(lower=0)
tab = tab.set_index(["centro", "curso_key", "cota"]).sort_index()

q = st.text_input("Nome", placeholder="🔎  Digite seu nome completo ou parte dele", label_visibility="collapsed")
toks = norm(q).split() if q else []
if len(q.strip()) < 3:
    kpi_grid([("Candidatos na lista de espera", fi(l.inscricao.nunique()), "inscrições únicas"),
              ("Candidatos convocados", fi(len(cu)), "até a última chamada"),
              ("Chamadas consideradas", fi(D["nmax"]), "dados publicados pela UFPI")], sm=True)
    st.markdown('<div class="passos">'
                '<div class="passo"><div class="n">1</div><b>Busque pelo nome</b><p>Use pelo menos 3 letras. A busca ignora acentos e maiúsculas.</p></div>'
                '<div class="passo"><div class="n">2</div><b>Escolha o seu cadastro</b><p>Se houver homônimos, o número da inscrição ajuda a diferenciar.</p></div>'
                '<div class="passo"><div class="n">3</div><b>Veja sua situação</b><p>Matrícula, posição na fila, vagas abertas e a distribuição das notas.</p></div>'
                '</div>', unsafe_allow_html=True)
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
qn = norm(q)
chaves = sorted(ent, key=lambda k: (not norm(ent[k]).startswith(qn), ent[k]))   # quem começa com o texto digitado vem primeiro
if len(chaves) > 50:
    st.caption(f"{len(chaves)} resultados; mostrando os 50 primeiros. Refine a busca para reduzir.")
else:
    st.caption(f"{len(chaves)} resultado{'s' if len(chaves) > 1 else ''} encontrado{'s' if len(chaves) > 1 else ''}.")
nomes_conv = set(mc.nome_key)


def rot(k):
    tags = (["convocado(a)"] if k[0] in nomes_conv else []) + ([f"lista de espera · insc. ****{str(k[1])[-4:]}"] if k[1] else [])
    return f"{bonito(ent[k])} — " + " · ".join(tags)


nk, ins = st.selectbox("Resultados", chaves[:50], format_func=rot)
h = c[c.nome_key == nk].sort_values("chamada_n")
L = l[l.inscricao == ins] if ins else l.iloc[0:0]


def dados_curso(cen, ck):
    """Vagas e matrículas por cota do curso (ou None se não houver)."""
    try:
        d = tab.loc[(cen, ck)]
    except KeyError:
        return None
    d = d.reindex([x for x in COTAS if x in d.index])
    d = d[(d.vagas > 0) | (d.matriculados > 0)]
    return None if d.empty else d


def comp_box(cen, ck, cota):
    d = dados_curso(cen, ck)
    if d is not None:
        caixa_vagas(d, cota, max(240, 70 + 56 * len(d)))


# ---------------------------------------------------------------- cabeçalho do candidato
pills = ([f'<span class="pill">Convocado(a) · <b>{h.iloc[-1].chamada}</b></span>'] if len(h) else []) \
    + ([f'<span class="pill">Lista de espera · <b>{len(L)}</b> modalidade{"s" if len(L) > 1 else ""}</span>'] if len(L) else [])
if len(h) and len(L):
    sub = f"Convocado(a) em {h.iloc[-1].curso} e na lista de espera de {', '.join(sorted(set(L.curso)))}"
elif len(h):
    sub = f"Convocado(a) em {h.iloc[-1].curso} · {h.iloc[-1].centro}"
else:
    sub = f"Lista de espera de {', '.join(sorted(set(L.curso)))}"
st.markdown(f'<div class="hero"><div class="txt"><div class="ht">{bonito(ent[(nk, ins)])}</div><p>{sub}</p>'
            f'<div class="pills">{"".join(pills)}</div></div></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- A) convocação
if len(h):
    u = h.iloc[-1]
    cor = COR_SIT[u.situacao]
    st.markdown('<div class="sec">Convocação</div>', unsafe_allow_html=True)
    motivo = f" · {u.motivo}" if pd.notna(u.motivo) and str(u.motivo).strip() else ""
    st.markdown(f'<span class="badge" style="background:{cor}">{u.situacao}{motivo}</span>', unsafe_allow_html=True)
    campos = [("Curso", u.curso), ("Centro", u.centro), ("Turno", u.turno), ("Grau", u.grau), ("Semestre", u.semestre),
              ("Cota", f"{u.cota} · {COTA_DESC.get(u.cota, '')}".rstrip(" ·")), ("CPF", u.cpf)]
    st.markdown('<div class="ficha">' + "".join(f'<div><div class="k">{a}</div><div class="v">{b}</div></div>' for a, b in campos) + "</div>",
                unsafe_allow_html=True)
    g = tab.loc[(u.centro, u.curso_key, u.cota)]
    kpi_grid([("Vagas na cota", fi(g.vagas) if g.vagas else "n/d"), ("Convocados na cota", fi(g.convocados)),
              ("Matriculados", fi(g.matriculados)), ("Indeferidos", fi(g.indeferidos)),
              ("Preenchimento", fp(g.preench))], sm=True)
    if len(h) > 1:
        with st.container(border=True):
            st.markdown("**Histórico de chamadas**")
            st.markdown('<div class="tl">' + "".join(
                f'<div class="tl-i" style="--c:{COR_SIT[r.situacao]}"><b>{r.chamada} · {r.situacao}</b>'
                f'<span>{r.curso} · cota {r.cota}</span></div>' for r in h.itertuples()) + "</div>", unsafe_allow_html=True)
    comp_box(u.centro, u.curso_key, u.cota)
    st.caption("A base de convocações não traz nota nem classificação; por isso não há posição para quem já foi convocado(a).")

# ---------------------------------------------------------------- B) lista de espera
if len(L):
    T = L.merge(tab.reset_index()[["centro", "curso_key", "cota", "vagas", "convocados", "matriculados", "abertas"]],
                on=["centro", "curso_key", "cota"], how="left")
    T["a_frente"] = (T.pos_atual - 1).clip(lower=0)
    T["faltam"] = (T.pos_atual - T.abertas).clip(lower=0)
    T.loc[T.vagas.fillna(0) == 0, ["abertas", "faltam"]] = np.nan
    T["rel"] = np.where(T.convocado, 9, T.pos_atual / T.na_fila.clip(lower=1))
    st.markdown('<div class="sec">Lista de espera</div>', unsafe_allow_html=True)
    show_t = pd.DataFrame({"Modalidade": T.cota, "Curso": T.curso + " · " + T.centro + " · " + T.turno,
                           "Posição original": T.classificacao, "Posição atual": T.pos_atual, "Na fila": T.na_fila,
                           "Nota": T.nota, "À frente": T.a_frente, "Vagas": T.vagas, "Convocados": T.convocados,
                           "Matriculados": T.matriculados, "Vagas abertas": T.abertas, "Faltam": T.faltam})
    def cel(x, nota=False):
        if pd.isna(x):
            return "n/d"
        return f"{x:.2f}".replace(".", ",") if nota else fi(x)
    cols_txt = ("Modalidade", "Curso")
    th = "".join(f'<th style="text-align:left">{h_}</th>' if h_ in cols_txt else f"<th>{h_}</th>" for h_ in show_t.columns)
    tr = "".join("<tr>" + "".join(
        f'<td style="text-align:left">{r_[h_]}</td>' if h_ in cols_txt else f'<td style="white-space:nowrap">{cel(r_[h_], h_ == "Nota")}</td>'
        for h_ in show_t.columns) + "</tr>" for _, r_ in show_t.iterrows())
    with st.container(border=True):
        st.markdown(f'<div class="tb-wrap"><table class="tb"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>', unsafe_allow_html=True)
    idx = list(T.index)
    if len(idx) > 1:
        i = st.radio("Modalidade", idx, index=idx.index(T.rel.idxmin()), horizontal=True,
                     format_func=lambda j: f"{T.cota[j]} · {T.curso[j]} ({T.turno[j]})")
    else:
        i = idx[0]
    r = T.loc[i]
    if r.convocado:
        veredito(AZUL, "Você já foi convocado(a) nesta modalidade", "Confira a situação da sua matrícula na seção de convocação.")
    else:
        orig = f" (posição original: {int(r.classificacao)}º)" if r.pos_atual != r.classificacao else ""
        titulo = f"Você é o {int(r.pos_atual)}º da fila{orig}"
        if pd.isna(r.abertas):
            veredito(AMBAR, titulo, "Não há vagas cadastradas para esta cota neste curso.")
        elif r.pos_atual <= r.abertas:
            veredito(VERDE, titulo, f"Há {int(r.abertas)} vagas abertas nesta cota e a sua posição está dentro desse número.")
        else:
            veredito(AZUL, titulo, f"Há {int(r.abertas)} vagas abertas nesta cota; faltam {int(r.faltam)} serem liberadas para chegar a sua vez.")
    st.caption("Estimativa com base nos dados publicados; a convocação real segue o edital e o remanejamento entre cotas.")

    G = l[(l.centro == r.centro) & (l.curso_key == r.curso_key) & (l.grau == r.grau) & (l.turno == r.turno) & (l.cota == r.cota)]
    if not r.convocado:
        fila, ja = G[~G.convocado].sort_values("classificacao"), G[G.convocado]
        ab = None if pd.isna(r.abertas) else int(r.abertas)
        ultimo = int(ja.classificacao.max()) if len(ja) else None
        alcance = int(fila.classificacao.iloc[ab - 1]) if ab and ab <= len(fila) else None
        with st.container(border=True):
            st.markdown(regua_html(int(G.classificacao.max()), int(r.classificacao), int(r.pos_atual), ultimo, alcance, ab), unsafe_allow_html=True)
        d = dados_curso(r.centro, r.curso_key)
        alt = max(320, 70 + 56 * (0 if d is None else len(d)))
        a, b = st.columns(2)
        with a:
            caixa_notas(G[~G.convocado].nota.dropna(), float(r.nota), int(r.pos_atual) - 1, max(int(r.na_fila) - int(r.pos_atual), 0), alt)
        if d is not None:
            with b:
                caixa_vagas(d, r.cota, alt)
    else:
        comp_box(r.centro, r.curso_key, r.cota)

st.caption(f"Considera até a {D['nmax']}ª chamada · {D['q']['Candidatos da lista de espera já convocados']} candidatos da lista de espera já aparecem como convocados.")
