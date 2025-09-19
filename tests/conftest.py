import pytest
import pandas as pd
from Paciente import Paciente

@pytest.fixture
def paciente_padrao():
    return Paciente(
        nome="João Teste",
        sexo="masculino",
        idade=30,
        peso=80,
        altura=180,
        objetivo="perder",
        nivel_atividade="moderado",
        restricoes="nenhuma",
        glicemia=90,
        tg=140,
        ldl=120,
        hdl=50,
        ferritina=150,
        hemoglobina=14
    )

@pytest.fixture
def saladas_df_mock():
    data = {
        "nome_salada": ["Salada Simples", "Salada Grega", "Salada de Verão", "Salada Colorida"],
        "ingrediente1": ["Alface", "Pepino", "Rúcula", "Tomate Cereja"],
        "ingrediente2": ["Tomate", "Tomate", "Manga", "Cenoura Ralada"],
        "ingrediente3": ["Cebola", "Azeitona", "Hortelã", "Milho"]
    }
    return pd.DataFrame(data)

@pytest.fixture
def foods_df_mock():
    """
    Cria um DataFrame de alimentos falso, mas realista, para ser usado
    nos testes do GeneticMealPlanner.
    """
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'food': ['banana', 'aveia', 'ovo_cozido', 'leite_integral', 'frango_grelhado', 'arroz_integral', 'feijao_preto', 'salmao', 'tofu', 'pao_integral'],
        'category': ['frutas_e_derivados', 'cereais_e_derivados', 'ovos_e_derivados', 'leite_e_derivados', 'carnes_e_derivados', 'cereais_e_derivados', 'leguminosas_e_derivados', 'pescados_e_frutos_do_mar', 'leguminosas_e_derivados', 'cereais_e_derivados'],
        'kcal': [105, 150, 78, 149, 165, 130, 131, 208, 76, 82],
        'protein_g': [1.3, 5, 6.3, 8, 31, 2.6, 9, 20, 8, 3],
        'fat_g': [0.4, 2.5, 5.3, 8, 3.6, 1, 0.5, 13, 5, 1],
        'fiber_g': [3.1, 4, 0, 0, 0, 1.8, 7, 0, 2, 2],
        'iron_mg': [0.3, 1, 1.2, 0.1, 0.5, 0.2, 2.1, 0.3, 2.7, 0.8],
        'sodium_mg': [1, 5, 62, 107, 74, 1, 1, 59, 7, 145],
        'vegan': [True, True, False, False, False, True, True, False, True, True],
        'contains_lactose': [False, False, False, True, False, False, False, False, False, False],
        'contains_milk': [False, False, False, True, False, False, False, False, False, False]
    }
    return pd.DataFrame(data)