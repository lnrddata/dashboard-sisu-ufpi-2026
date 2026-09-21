"""Ponto de entrada: streamlit run app.py"""
from pathlib import Path

import streamlit as st
from PIL import Image

from cabecalho import LOGO, banner
from theme import css

st.set_page_config(page_title="UFPI · Ocupação de vagas do SiSU", layout="wide",
                   page_icon=Image.open(LOGO) if LOGO.exists() else "📊")
css()
banner()
st.navigation(
    [st.Page("views/visao_geral.py", title="Visão geral", icon="📊", default=True),
     st.Page("views/candidato.py", title="Acompanhamento do candidato", icon="🔎")],
    position="sidebar",
).run()
