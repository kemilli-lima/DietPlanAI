import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from MealPlanGenerator import MealPlanGenerator
from Paciente import Paciente

def test_inicializacao_calcula_metricas_corretamente(paciente_padrao, saladas_df_mock):
    """Testa se o construtor da classe calcula corretamente as métricas de saúde."""
    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)

    assert generator.imc == 24.69
    assert generator.classificacao_imc == "peso normal"
    assert pytest.approx(generator.tdee, 0.01) == 2345.15

@patch('MealPlanGenerator.GeneticMealPlanner')
def test_gerar_cardapio_chama_planner_para_refeicoes(mock_planner, paciente_padrao, saladas_df_mock):
    """Testa se `gerar_cardapio` instancia e executa o GeneticMealPlanner para as refeições."""
    foods_df_falso = pd.DataFrame({'id': [1], 'food': ['banana']})
    mock_instancia_planner = MagicMock()
    mock_instancia_planner.run.return_value = foods_df_falso
    mock_planner.return_value = mock_instancia_planner

    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)
        generator.gerar_cardapio()

    assert mock_planner.call_count == 6
    assert len(generator.refeicoes_dict) == 6

def test_gerar_markdown_final_contem_todas_secoes(paciente_padrao, saladas_df_mock):
    """Testa a estrutura final do markdown."""
    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)
        generator.refeicoes_dict = {"jantar": {"meta": {}, "foods": pd.DataFrame()}}

    markdown_final = generator.gerar_markdown_final()

    assert f"**- Nome:** {paciente_padrao.nome}" in markdown_final
    assert "## 🥤 Hidratação" in markdown_final
    assert "## 🍲 Jantar" in markdown_final

@patch('MealPlanGenerator.dicionario_alimentos')
def test_formatar_refeicoes_com_nomes_especificos(mock_dicionario, paciente_padrao, saladas_df_mock):
    """Cobre as linhas 69 e 71, testando a formatação de Pão e Ovo."""
    mock_dicionario.get.side_effect = lambda key, default: {'pao_integral': 'Pão Integral', 'ovo_cozido': 'Ovo Cozido'}.get(key, default)
    
    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)

    foods_df_falso = pd.DataFrame({
        'id': [1, 2], 'food': ['pao_integral', 'ovo_cozido'],
        'kcal': [80, 78], 'protein_g': [3, 6], 'fat_g': [1, 5], 'fiber_g': [2, 0]
    })
    generator.refeicoes_dict = {"cafe_da_manha": {"meta": {}, "foods": foods_df_falso}}
    
    resultado_md = generator._formatar_refeicoes()

    assert "| Pão Integral (2 fatias ~ 60-70g)" in resultado_md
    assert "| Ovo Cozido (2 ovos médios)" in resultado_md

def test_formatar_refeicoes_adiciona_queijo_no_lanche(paciente_padrao, saladas_df_mock):
    """Cobre as linhas 83-90, testando a adição de queijo."""
    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)

    foods_df_falso = pd.DataFrame({'id': [1], 'food': ['maca'], 'kcal': [95], 'protein_g': [0.5], 'fat_g': [0.3], 'fiber_g': [4]})
    generator.refeicoes_dict = {"lanche_tarde": {"meta": {}, "foods": foods_df_falso}}
    
    resultado_md = generator._formatar_refeicoes()

    assert "| Queijo (1 fatia ~30g)" in resultado_md
    assert "**Total Nutricional:** 185 kcal" in resultado_md

def test_formatar_refeicoes_adiciona_whey_na_ceia_normal(paciente_padrao, saladas_df_mock):
    """Cobre as linhas 94 e 100-105, testando a adição de whey normal."""
    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)

    foods_df_falso = pd.DataFrame({'id': [1], 'food': ['banana'], 'kcal': [105], 'protein_g': [1.3], 'fat_g': [0.4], 'fiber_g': [3.1]})
    generator.refeicoes_dict = {"ceia": {"meta": {}, "foods": foods_df_falso}}

    resultado_md = generator._formatar_refeicoes()
    
    assert "| Whey Protein (1 dose)" in resultado_md
    assert "**Total Nutricional:** 225 kcal" in resultado_md

def test_formatar_refeicoes_adiciona_whey_na_ceia_lactointolerante(saladas_df_mock):
    """Cobre as linhas 95-99, testando a adição de whey isolado."""
    paciente_lacto = Paciente(nome="Teste Lacto", sexo="f", idade=30, peso=60, altura=165, nivel_atividade="leve", restricoes="lactointolerante")
    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_lacto)

    foods_df_falso = pd.DataFrame({'id': [1], 'food': ['banana'], 'kcal': [105], 'protein_g': [1.3], 'fat_g': [0.4], 'fiber_g': [3.1]})
    generator.refeicoes_dict = {"ceia": {"meta": {}, "foods": foods_df_falso}}

    resultado_md = generator._formatar_refeicoes()

    assert "| Whey Isolado (1 dose e meia)" in resultado_md
    assert "**Total Nutricional:** 285 kcal" in resultado_md

@patch('MealPlanGenerator.HealthUtils.divisao_refeicoes')
@patch('MealPlanGenerator.GeneticMealPlanner')
def test_gerar_cardapio_pula_refeicao_sem_meta(mock_planner, mock_divisao, paciente_padrao, saladas_df_mock):
    """Cobre a linha 131, testando o `continue` para refeições sem meta."""
    metas_incompletas = [{
        "Refeicao": "cafe_da_manha", "Kcal": 500, "Proteina": 30,
        "Carbo": 50, "Gordura": 20, "Fibra": 10
    }]
    mock_divisao.return_value = metas_incompletas

    with patch('pandas.read_csv', return_value=saladas_df_mock):
        generator = MealPlanGenerator(paciente=paciente_padrao)
        generator.gerar_cardapio()

    assert mock_planner.call_count == 1