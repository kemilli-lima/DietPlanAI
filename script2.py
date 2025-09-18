import pandas as pd

# Recarrega os arquivos
files = [
    "almoco_jantar.csv",
    "lanche_ceia.csv",
    "cafe_da_manha.csv",
]

unique_foods = set()
for file in files:
    df = pd.read_csv(file)
    if "food" in df.columns:
        unique_foods.update(df["food"].unique())

# Função simples: substitui underscores por espaço e coloca título
def format_food_name(food):
    return food.replace("_", " ").title()

# Cria o dicionário final com todos os alimentos
mapping = {food: format_food_name(food) for food in sorted(unique_foods)}

# Salva em um arquivo .py
output_path_py = "dicionario_alimentos_completo.py"
with open(output_path_py, "w", encoding="utf-8") as f:
    f.write("dicionario_alimentos = {\n")
    for k, v in mapping.items():
        f.write(f'    "{k}": "{v}",\n')
    f.write("}\n")

output_path_py
