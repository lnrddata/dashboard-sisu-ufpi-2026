"""Constantes do painel: centros, cotas, colunas exigidas e apelidos de cursos."""

# Ordem institucional dos centros: primeiro Teresina, depois os campi do interior.
# O CEAD fica entre os dois grupos por não ser campus presencial.
ORDEM_CENTROS = ["CCS", "CCN", "CCHL", "CCE", "CT", "CCA", "CEAD", "CSHNB", "CPCE", "CAFS"]

COTAS = ["AC", "PPI-1", "PPI-2", "EP-1", "EP-2", "PCD-1", "PCD-2", "Q-1"]
COTA_DESC = {"AC": "Ampla concorrência", "PPI-1": "Pretos, pardos e indígenas", "PPI-2": "Pretos, pardos e indígenas",
             "EP-1": "Escola pública", "EP-2": "Escola pública", "PCD-1": "Pessoa com deficiência",
             "PCD-2": "Pessoa com deficiência", "Q-1": "Quilombola"}

# Colunas obrigatórias de cada aba do Excel.
REQ = {"vagas": {"centro", "Grau", "curso", "turno", "semestre", "modalidade", "vagas"},
       "convocacoes": {"Chamada", "campus", "curso", "turno", "grau", "cota", "aluno", "semestre", "matriculado", "motivo"},
       "lista_espera": {"centro", "curso", "grau", "turno", "inscrição", "candidato", "modalidade", "nota", "classificação"}}

# Nomes de curso que divergem entre abas: (centro, nome normalizado) -> nome usado em `vagas`.
ALIAS = {("CCE", "DESIGN DE MODA"): "MODA, DESIGN E ESTILISMO",
         ("CCHL", "LETRAS - LINGUA PORTUGUESA E LITERATURA DE LINGUA PORTUGUESA"): "LETRAS - LINGUA PORTUGUESA",
         ("CSHNB", "LETRAS - LINGUA PORTUGUESA E LITERATURA DE LINGUA PORTUGUESA"): "LETRAS - PORTUGUES",
         ("CCS", "ABI - EDUCACAO FISICA"): "EDUCACAO FISICA"}


def chave_centro(x) -> int:
    """Chave de ordenação institucional dos centros (desconhecidos vão para o fim)."""
    return ORDEM_CENTROS.index(x) if x in ORDEM_CENTROS else len(ORDEM_CENTROS)
