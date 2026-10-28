"""Cabeçalho institucional (brasão da UFPI). Autônomo: não depende do theme.py."""
import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

LOGO = Path(__file__).parent / "assets" / "logo-ufpi.png"
LOGO_CONTORNO = Path(__file__).parent / "assets" / "logo-ufpi-contorno.png"   # só as linhas brancas do brasão (fundo transparente)

_CSS = """<style>
.inst {display:flex; align-items:center; gap:22px; flex-wrap:wrap; background:linear-gradient(180deg,#ffffff,#F7FAFF);
  border:1px solid #E6EAF1; border-radius:14px; padding:14px 26px; position:relative; z-index:1000;
  box-shadow:0 10px 26px -14px rgba(11,31,58,.30), 0 2px 6px rgba(11,31,58,.06); box-sizing:border-box;
  overflow:hidden}
/* o banner acompanha a rolagem (sticky) mas continua no fluxo da página: herda a largura e as margens do conteúdo */
[data-testid="stElementContainer"]:has(.inst), .element-container:has(.inst) {position:sticky; top:.75rem; z-index:1000; margin-bottom:.9rem}
/* faixa de fundo fixa acima do banner: impede que o conteúdo apareça rolando nesse espaço */
.inst-tampa {position:fixed; top:0; left:0; right:0; height:.75rem; background:#F4F6FA; z-index:999}
.inst::before {content:""; position:absolute; left:0; top:0; bottom:0; width:6px;
  background:linear-gradient(180deg,#2E6FD9,#0B1F3A)}
.inst img {height:96px; width:auto; filter:drop-shadow(0 3px 6px rgba(11,31,58,.18))}
.i1 {font-size:1.05rem; font-weight:800; color:#0B1F3A; letter-spacing:.03em}
.i2 {font-size:.9rem; color:#5B6B82; margin:2px 0 10px; padding-bottom:8px; border-bottom:1px solid #E9EEF6; display:inline-block}
.i3 {font-size:1.55rem; font-weight:800; letter-spacing:-.01em; line-height:1.2;
  background:linear-gradient(90deg,#123D82,#1F5FBF 60%,#2E6FD9); -webkit-background-clip:text; background-clip:text; color:transparent}
/* barra lateral recolhida: o banner ocupa a largura toda, deixando espaço para o botão de reabrir a barra */
body:has([data-testid="stSidebar"][aria-expanded="false"]) .inst {margin-left:3rem}
@media (max-width: 1100px) {
  .inst {padding:10px 18px; gap:14px; flex-wrap:nowrap}
  .inst > div {min-width:0}
  .inst img {height:62px}
  .i1 {font-size:.85rem}
  .i2 {font-size:.78rem; margin:1px 0 6px; padding-bottom:5px}
  .i3 {font-size:1.1rem}
}
@media (max-width: 900px) {
  .i2 {display:none}
  .i3 {font-size:1rem}
}
@media (max-width: 768px) {   /* abaixo disso a barra lateral vira sobreposta */
  .inst {margin-left:3rem; padding:8px 14px}
  .inst img {height:46px}
  .i3 {font-size:.95rem}
}
</style>"""


@lru_cache(maxsize=1)
def _logo_b64() -> str:
    return base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ""


def banner() -> None:
    """Cabeçalho com o brasão e os três títulos (exibido em todas as páginas)."""
    img = f'<img src="data:image/png;base64,{_logo_b64()}" alt="Brasão da UFPI">' if _logo_b64() else ""
    topo = (f'<style>[data-testid="stSidebarHeader"] {{background:url(data:image/png;base64,{_contorno_b64()}) no-repeat 22px 18px / auto 96px;'
            f' min-height:132px; opacity:1}}</style>') if _contorno_b64() else ""   # brasão só em contornos brancos no topo da barra lateral
    st.markdown(_CSS + topo + f'<div class="inst-tampa"></div><div class="inst">{img}<div><div class="i1">UNIVERSIDADE FEDERAL DO PIAUÍ</div>'
                '<div class="i2">PRÓ-REITORIA DE ENSINO DE GRADUAÇÃO</div>'
                '<div class="i3">ACOMPANHAMENTO DA OCUPAÇÃO DE VAGAS DO SISU</div></div></div>', unsafe_allow_html=True)


@lru_cache(maxsize=1)
def _contorno_b64() -> str:
    return base64.b64encode(LOGO_CONTORNO.read_bytes()).decode() if LOGO_CONTORNO.exists() else ""
