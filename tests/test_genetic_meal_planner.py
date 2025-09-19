import pytest
import pandas as pd
import random
from unittest.mock import patch
from GeneticMealPlanner import GeneticMealPlanner

@patch('GeneticMealPlanner.pd.read_csv')
def test_load_foods_aplica_restricao_corretamente(mock_read_csv, foods_df_mock):
    """
    Testa se o _load_foods aplica corretamente uma restrição (ex: vegano),
    filtrando o DataFrame de alimentos.
    """
    mock_read_csv.return_value = foods_df_mock
    
    planner = GeneticMealPlanner(refeicao="almoco", restricao="vegano")
    
    loaded_foods = planner.foods
    
    assert loaded_foods['vegan'].all()
    assert len(loaded_foods) < len(foods_df_mock)

@pytest.mark.parametrize("refeicao, restricao, esperado", [
    ("cafe_da_manha", "nenhuma", ["frutas_e_derivados", "cereais_e_derivados", "ovos_e_derivados"]),
    ("almoco", "nenhuma", [["carnes_e_derivados", "pescados_e_frutos_do_mar"], "leguminosas_e_derivados", ["cereais_e_derivados", "verduras_hortalicas_e_derivados"]]),
    ("cafe_da_manha", "lactointolerante", ["frutas_e_derivados", "cereais_e_derivados", "ovos_e_derivados"]),
    ("lanche_manha", "lactointolerante", ["frutas_e_derivados", "ovos_e_derivados"])
])
@patch('GeneticMealPlanner.pd.read_csv')
def test_get_required_categories(mock_read_csv, foods_df_mock, refeicao, restricao, esperado):
    """
    Testa a lógica de seleção de categorias para diferentes refeições e restrições.
    """
    mock_read_csv.return_value = foods_df_mock
    planner = GeneticMealPlanner(refeicao=refeicao, restricao=restricao)
    
    categorias = planner._get_required_categories()
    
    assert all(item in categorias for item in esperado)

@patch('GeneticMealPlanner.pd.read_csv')
def test_fitness_penaliza_e_bonifica_corretamente(mock_read_csv):
    """
    Testa o coração do GA: a função fitness.
    Usa um mock de alimentos controlado para isolar o bônus de ferro.
    """
    foods_data = {
        'id': [1, 2],
        'food': ['bife_sem_ferro', 'bife_com_ferro'],
        'category': ['carnes_e_derivados', 'carnes_e_derivados'],
        'kcal': [200, 200], 'protein_g': [30, 30], 'fat_g': [8, 8],
        'fiber_g': [0, 0], 'sodium_mg': [50, 50],
        'iron_mg': [0.1, 5.0]
    }
    controlled_foods_df = pd.DataFrame(foods_data)
    mock_read_csv.return_value = controlled_foods_df
    
    planner = GeneticMealPlanner(refeicao="almoco", nivel_ferro='baixa', target_kcal=200)
    
    individuo_bom = [2] 
    individuo_ruim = [1]
    
    fitness_bom = planner._fitness(individuo_bom)
    fitness_ruim = planner._fitness(individuo_ruim)
    
    assert fitness_bom > fitness_ruim

@patch('GeneticMealPlanner.pd.read_csv')
def test_crossover_gera_filho_valido(mock_read_csv, foods_df_mock):
    """
    Testa o operador de crossover com resultado determinístico.
    """
    random.seed(42)
    mock_read_csv.return_value = foods_df_mock
    planner = GeneticMealPlanner(refeicao="cafe_da_manha")

    pai1 = [1, 2, 3] 
    pai2 = [10, 4, 1] 
    
    filho = planner._crossover(pai1, pai2)
    
    assert len(filho) == len(planner.required_cats)
    assert filho == pai1

@patch('GeneticMealPlanner.pd.read_csv')
def test_run_executa_sem_erros_e_retorna_dataframe(mock_read_csv, foods_df_mock):
    """
    Teste de integração para o método run.
    """
    random.seed(42)
    mock_read_csv.return_value = foods_df_mock
    planner = GeneticMealPlanner(refeicao="almoco", target_kcal=500)
    
    resultado = planner.run(pop_size=10, generations=5)
    
    assert isinstance(resultado, pd.DataFrame)
    assert not resultado.empty