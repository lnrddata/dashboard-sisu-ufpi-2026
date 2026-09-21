"""Camada de dados do painel SiSU: carga, limpeza, chaves de junção e métricas.

Uso: `python data.py --check` confere os números de referência da 1ª chamada.
"""
import io
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ARQ = Path(__file__).parent / "dados_sisu.xlsx"
COTAS = ["AC", "PPI-1", "PPI-2", "EP-1", "EP-2", "PCD-1", "PCD-2", "Q-1"]
COTA_DESC = {"AC": "Ampla concorrência", "PPI-1": "Pretos, pardos e indígenas", "PPI-2": "Pretos, pardos e indígenas",
             "EP-1": "Escola pública", "EP-2": "Escola pública", "PCD-1": "Pessoa com deficiência",
             "PCD-2": "Pessoa com deficiência", "Q-1": "Quilombola"}
REQ = {"vagas": {"centro", "Grau", "curso", "turno", "semestre", "modalidade", "vagas"},
       "convocacoes": {"Chamada", "campus", "curso", "turno", "grau", "cota", "aluno", "semestre", "matriculado", "motivo"},
       "lista_espera": {"centro", "curso", "grau", "turno", "inscrição", "candidato", "modalidade", "nota", "classificação"}}
# nomes de curso que divergem entre abas: (centro, nome normalizado) -> nome usado em `vagas`
ALIAS = {("CCE", "DESIGN DE MODA"): "MODA, DESIGN E ESTILISMO",
         ("CCHL", "LETRAS - LINGUA PORTUGUESA E LITERATURA DE LINGUA PORTUGUESA"): "LETRAS - LINGUA PORTUGUESA",
         ("CSHNB", "LETRAS - LINGUA PORTUGUESA E LITERATURA DE LINGUA PORTUGUESA"): "LETRAS - PORTUGUES",
         ("CCS", "ABI - EDUCACAO FISICA"): "EDUCACAO FISICA"}


def norm(s) -> str:
    """Maiúsculas, sem acentos, traços/barras uniformizados, espaços colapsados."""
    s = str(s).replace("–", "-").replace("—", "-").replace("/", " - ")
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    return re.sub(r"\s*-\s*", " - ", re.sub(r"\s+", " ", s)).strip().upper()


def _grau(s) -> str:
    g = norm(s)
    if "ABI" in g:
        return "ABI"
    return {"TECNOLOGO": "Tecnólogo", "TECNOLOGICO": "Tecnólogo",
            "LICENCIATURA - BACHARELADO": "Licenciatura/Bacharelado"}.get(g, g.title())


def _semestre(s) -> str:
    n = re.findall(r"\d", str(s))
    return "1º e 2º semestres" if len(n) > 1 else (f"{n[0]}º semestre" if n else "n/d")


def _carregar(src, mtime: float = 0.0) -> dict:
    """Lê o Excel e devolve as tabelas limpas. `mtime` só invalida o cache quando o arquivo muda."""
    x = pd.read_excel(io.BytesIO(src) if isinstance(src, bytes) else src, sheet_name=None)
    for aba, cols in REQ.items():
        if aba not in x:
            raise ValueError(f"Aba ausente no Excel: {aba}")
        if cols - set(x[aba].columns):
            raise ValueError(f"Colunas ausentes em '{aba}': {sorted(cols - set(x[aba].columns))}")
    v = x["vagas"].rename(columns={"Grau": "grau"})
    c = x["convocacoes"].rename(columns={"campus": "centro"})
    l = x["lista_espera"].rename(columns={"inscrição": "inscricao", "candidato": "aluno", "classificação": "classificacao"})

    lab = {}
    for d in (v, c, l):
        d["centro"] = d.centro.astype(str).str.strip()
        d["curso_key"] = [ALIAS.get((a, k), k) for a, k in zip(d.centro, d.curso.map(norm))]
    for d in (v, c, l):
        for k, o in zip(d.curso_key, d.curso):
            lab.setdefault(k, str(o).title() if str(o).isupper() else str(o))
        d["curso"] = d.curso_key.map(lab)
    for d in (v, c, l):
        d["grau"] = d.grau.map(_grau)
        d["turno"] = d.turno.astype(str).str.strip()
    for d in (v, c):
        d["semestre"] = d.semestre.map(_semestre)
    v["cota"] = v.modalidade.astype(str).str.strip().str.replace(" ", "-")
    c["cota"] = c.cota.astype(str).str.strip().str.upper()
    l["cota"] = l.modalidade.astype(str).str.split(" ou ").str[-1].str.strip()

    c["chamada_n"] = pd.to_numeric(c.Chamada.astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    sem_num = int(c.chamada_n.isna().sum())
    c["chamada_n"] = c.chamada_n.fillna(1).astype(int)
    c["chamada"] = c.chamada_n.astype(str) + "ª chamada"
    c["nome_key"] = c.aluno.map(lambda s: "" if pd.isna(s) else norm(s))
    c["matriculado"] = pd.to_numeric(c.matriculado, errors="coerce").fillna(0).astype(int)
    c["situacao"] = np.where(c.matriculado == 1, "Matriculado", np.where(c.motivo.notna(), "Não matriculado", "Pendente"))
    c["mat"] = (c.situacao == "Matriculado").astype(int)
    c["pend"] = (c.situacao == "Pendente").astype(int)
    c["indef"] = c.motivo.astype(str).str.upper().str.startswith("INDEFER").astype(int)

    l["nome_key"] = l.aluno.map(norm)
    chaves = set(zip(c.nome_key, c.centro, c.curso_key, c.cota))
    l["convocado"] = [k in chaves for k in zip(l.nome_key, l.centro, l.curso_key, l.cota)]
    l = l.sort_values("classificacao")
    grp = [l.centro, l.curso_key, l.grau, l.turno, l.cota]
    livre = (~l.convocado).astype(int)
    l["pos_atual"] = livre.groupby(grp).cumsum()      # posição efetiva, descontando quem já foi convocado
    l["na_fila"] = livre.groupby(grp).transform("sum")
    l.loc[l.convocado, "pos_atual"] = 0

    q = {"Cursos das convocações sem correspondência em vagas": sorted({lab[k] for k in set(c.curso_key) - set(v.curso_key)}),
         "Cursos da lista de espera sem correspondência em vagas": sorted({lab[k] for k in set(l.curso_key) - set(v.curso_key)}),
         "Cotas fora do padrão": sorted((set(c.cota) | set(l.cota) | set(v.cota)) - set(COTAS)),
         "Linhas de convocação totalmente duplicadas": int(x["convocacoes"].duplicated().sum()),
         "Chamadas sem número (tratadas como 1ª)": sem_num,
         "Convocados sem nome": int((c.nome_key == "").sum()),
         "Candidatos da lista de espera já convocados": int(l[l.convocado].inscricao.nunique())}
    return dict(v=v, c=c, l=l, lab=lab, q=q, nmax=int(c.chamada_n.max()))


carregar = st.cache_data(show_spinner="Carregando dados...")(_carregar)


def get_data() -> dict:
    """Carrega os dados (com cache atrelado à data do arquivo) ou pede upload."""
    try:
        if ARQ.exists():
            ts = ARQ.stat().st_mtime
            D = dict(carregar(str(ARQ), ts))
        else:
            if "xlsx" not in st.session_state:       # guarda o upload para valer nas duas páginas
                up = st.file_uploader("Envie o arquivo dados_sisu.xlsx", type="xlsx")
                if up is None:
                    st.info("Envie o dados_sisu.xlsx (ou coloque-o na pasta do app).")
                    st.stop()
                st.session_state["xlsx"], st.session_state["xlsx_ts"] = up.getvalue(), datetime.now().timestamp()
                st.rerun()
            ts = st.session_state["xlsx_ts"]
            D = dict(carregar(st.session_state["xlsx"], 0.0))
    except ValueError as e:
        st.error(str(e))
        st.stop()
    D["atualizado"] = datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
    return D


def unicos(c: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por (aluno, centro, curso, cota), valendo a chamada mais recente."""
    c = c.sort_values("chamada_n", kind="stable")
    ok = c.nome_key != ""
    return pd.concat([c[ok].drop_duplicates(["nome_key", "centro", "curso_key", "cota"], keep="last"), c[~ok]])


def filtrar(df: pd.DataFrame, sel: dict) -> pd.DataFrame:
    for col, vals in sel.items():
        if vals and col in df:
            df = df[df[col].isin(vals)]
    return df


def agg(v: pd.DataFrame, c: pd.DataFrame, by) -> pd.DataFrame:
    """Vagas × convocações por dimensões comuns. `preench` = matriculados ÷ vagas."""
    a = v.groupby(by).vagas.sum()
    b = c.groupby(by).agg(convocados=("mat", "size"), matriculados=("mat", "sum"),
                          indeferidos=("indef", "sum"), pendentes=("pend", "sum"))
    d = pd.concat([a, b], axis=1).fillna(0).reset_index()
    d["preench"] = np.where(d.vagas > 0, d.matriculados / d.vagas.where(d.vagas > 0, 1), np.nan)
    return d


if __name__ == "__main__" and "--check" in sys.argv:
    D = _carregar(str(ARQ))
    v, c, l = D["v"], D["c"], D["l"]
    if D["nmax"] > 1:
        print(f"AVISO: há {D['nmax']} chamadas; conferindo apenas a 1ª.")
    c1 = c[c.chamada_n == 1]
    cv = c1[c1.centro.isin(v.centro.unique())]
    checks = {"vagas = 5.374": int(v.vagas.sum()) == 5374,
              "vagas por cota (centros com modalidade)": v.groupby("cota").vagas.sum().to_dict() == {"AC": 2391, "PPI-1": 1054, "PPI-2": 1013,
                                  "PCD-1": 164, "PCD-2": 164, "EP-2": 112, "EP-1": 88, "Q-1": 88},
              "convocados = 5.371": len(c1) == 5371,
              "matriculados = 4.955": int(c1.mat.sum()) == 4955,
              "indeferidos = 416": int(c1.indef.sum()) == 416,
              "preenchimento ≈ 92,2%": round(c1.mat.sum() / v.vagas.sum(), 3) == round(4955 / 5374, 3),
              "inscrições únicas na lista = 13.350": l.inscricao.nunique() == 13350}
    for k, ok in checks.items():
        print("OK  " if ok else "FALHA", k)
    assert all(checks.values()), "Números de referência não conferem"
