import pytest
import pandas as pd
from HealthUtils import HealthUtils

# Testes para a função normalizar_texto
@pytest.mark.parametrize("entrada, esperado", [
    ("Masculino", "masculino"),
    ("  PERDER  ", "perder"),
    ("Situação Crítica", "situacao critica"),
    ("ATIVIDADE FÍSICA", "atividade fisica")
])
def test_normalizar_texto(entrada, esperado):
    """Testa se a normalização de texto remove acentos, espaços e converte para minúsculas."""
    assert HealthUtils.normalizar_texto(entrada) == esperado

# Testes para a função calcular_imc
@pytest.mark.parametrize("peso, altura, imc_esperado, classif_esperada", [
    (80, 180, 24.69, "peso normal"),
    (50, 170, 17.3, "abaixo do peso"),
    (90, 175, 29.39, "sobrepeso"),
    (110, 180, 33.95, "obesidade grau 1"),
    (130, 185, 37.98, "obesidade grau 2"),
    (150, 185, 43.83, "obesidade grau 3"),
    (80, 0, None, "Altura inválida.")
])
def test_calcular_imc(peso, altura, imc_esperado, classif_esperada):
    """Testa o cálculo do IMC e sua classificação para diferentes cenários."""
    imc_calculado, classif_calculada = HealthUtils.calcular_imc(peso, altura)
    assert imc_calculado == imc_esperado
    assert classif_calculada == classif_esperada

# Testes para a função calcular_tbm_tdee_calorias
@pytest.mark.parametrize("sexo, idade, peso, altura, atividade, objetivo, tdee_esperado", [
    ("masculino", 30, 80, 180, "moderado", "perder", 2345.15),
    ("feminino", 25, 60, 165, "leve", "manter", 1849.72),
    ("masculino", 40, 90, 175, "intenso", "ganhar", 3413.13)
])
def test_calcular_tbm_tdee_calorias(sexo, idade, peso, altura, atividade, objetivo, tdee_esperado):
    """Testa o cálculo de TMB e TDEE, aplicando os modificadores de objetivo."""
    tmb, tdee = HealthUtils.calcular_tbm_tdee_calorias(sexo, idade, peso, altura, atividade, objetivo)
    assert tdee == pytest.approx(tdee_esperado, 0.01) # Usa approx para comparar floats

@pytest.mark.parametrize("glicemia, esperado", [(80, 'normal'), (110, 'pre_diabetes'), (130, 'diabetes')])
def test_avaliar_glicemia(glicemia, esperado):
    assert HealthUtils.avaliar_glicemia(glicemia) == esperado

@pytest.mark.parametrize("tg, esperado", [(140, 'normal'), (170, 'moderado'), (220, 'alto')])
def test_avaliar_triglicerideos(tg, esperado):
    assert HealthUtils.avaliar_triglicerideos(tg) == esperado

@pytest.mark.parametrize("ferritina, hemoglobina, esperado", [(50, 14, 'normal'), (25, 14, 'baixa'), (50, 11, 'baixa')])
def test_avaliar_ferro(ferritina, hemoglobina, esperado):
    assert HealthUtils.avaliar_ferro(ferritina, hemoglobina) == esperado

def test_avaliar_colesterol():
    """Testa a avaliação de colesterol para diferentes combinações de LDL e HDL."""
    assert HealthUtils.avaliar_colesterol(ldl=90, hdl=70) == {'ldl': 'normal', 'hdl': 'bom'}
    assert HealthUtils.avaliar_colesterol(ldl=150, hdl=35) == {'ldl': 'moderado', 'hdl': 'ruim'}
    assert HealthUtils.avaliar_colesterol(ldl=180, hdl=50) == {'ldl': 'critico', 'hdl': 'moderado'}

def test_aplicar_restricao():
    """Testa se o filtro de restrição funciona corretamente."""
    df_teste = pd.DataFrame({
        'food': ['leite', 'frango', 'tofu'],
        'vegan': [False, False, True]
    })
    
    df_filtrado = HealthUtils.aplicar_restricao(df_teste, "vegano")
    
    assert len(df_filtrado) == 1
    assert df_filtrado.iloc[0]['food'] == 'tofu'