"""Cabeçalho institucional (brasão da UFPI). Autônomo: não depende do theme.py."""
import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

LOGO = Path(__file__).parent / "assets" / "logo-ufpi.png"

_CSS = """<style>
.inst {display:flex; align-items:center; gap:22px; flex-wrap:wrap; background:#fff; border:1px solid #E6EAF1;
  border-left:6px solid #1F5FBF; border-radius:12px; padding:14px 24px; position:fixed; top:3.25rem; z-index:1000;
  box-shadow:0 4px 14px rgba(11,31,58,.10); left:19rem; right:1rem; box-sizing:border-box}
.inst img {height:96px; width:auto}
.i1 {font-size:1.05rem; font-weight:700; color:#0B1F3A; letter-spacing:.02em}
.i2 {font-size:.9rem; color:#5B6B82; margin:2px 0 8px}
.i3 {font-size:1.5rem; font-weight:700; color:#1F5FBF; line-height:1.2}
.inst-spacer {height:154px;}
@media (max-width: 900px) {
  .inst {left:1rem; right:1rem; width:auto;}
}
</style>"""


@lru_cache(maxsize=1)
def _logo_b64() -> str:
    return base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ""


def banner() -> None:
    """Cabeçalho com o brasão e os três títulos (exibido em todas as páginas)."""
    img = f'<img src="data:image/png;base64,{_logo_b64()}" alt="Brasão da UFPI">' if _logo_b64() else ""
    st.markdown(_CSS + f'<div class="inst">{img}<div><div class="i1">UNIVERSIDADE FEDERAL DO PIAUÍ</div>'
                '<div class="i2">PRÓ-REITORIA DE ENSINO DE GRADUAÇÃO</div>'
                '<div class="i3">ACOMPANHAMENTO DA OCUPAÇÃO DE VAGAS DO SISU</div></div></div>', unsafe_allow_html=True)
