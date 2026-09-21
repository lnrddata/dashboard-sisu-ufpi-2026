# Painel SiSU

Dashboard em Streamlit com duas páginas: **Visão geral** (ocupação de vagas) e **Acompanhamento do candidato**.

## Rodar localmente
```
pip install -r requirements.txt
streamlit run app.py
```
O `dados_sisu.xlsx` (abas `vagas`, `convocacoes`, `lista_espera`) fica na pasta do app; os dados são os publicados pela UFPI.
Sem o arquivo, o app pede o upload.

## Atualizar a cada chamada
Acrescente as linhas na aba `convocacoes` ("2º Chamada", "3º Chamada"...), salve e recarregue a página.
Para atualizar o app publicado, substitua o `dados_sisu.xlsx` no repositório (`git add`, `git commit`, `git push`,
ou **Add file → Upload files** no GitHub); o Streamlit Cloud reimplanta sozinho.

## Validar os dados
```
python data.py --check
```
