import pandas as pd

# Carregar os dois CSVs
df_principal = pd.read_csv('taco.csv')  # Com coluna 'carbs_g'
df_secundario = pd.read_csv('lanche_ceia.csv')  # Sem 'carbs_g'

# Supondo que 'id' seja a chave para cruzamento. Ajuste conforme necessário.
df_merged = df_secundario.merge(df_principal[['id', 'carbs_g']], on='id', how='left')

# Converter a coluna 'carbs_g' para float
# Isso também cuida de casos onde há vírgulas como separador decimal ou espaços
df_merged['carbs_g'] = (
    df_merged['carbs_g']
    .astype(str)                # garante que é string para processar
    .str.replace(',', '.', regex=False)  # troca vírgulas por ponto decimal
    .str.strip()                # remove espaços em branco
    .replace('', pd.NA)         # trata strings vazias como NA
    .astype(float)              # converte para float
)

# Salvar o resultado
df_merged.to_csv('lanche_ceia_atualizado.csv', index=False)

print("Coluna 'carbs_g' adicionada e convertida para float com sucesso!")
