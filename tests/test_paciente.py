import pytest
import pandas as pd
from Paciente import Paciente

def test_criacao_paciente(paciente_padrao):
    """
    Teste 'smoke test' para garantir que um objeto Paciente pode ser criado
    e que seus atributos são atribuídos corretamente.
    """
    assert paciente_padrao.nome == "João Teste"
    assert paciente_padrao.idade == 30
    assert paciente_padrao.glicemia == 90

def test_from_dataframe_com_todos_os_dados():
    """
    Testa o construtor de classe from_dataframe quando a linha do CSV tem todos os dados.
    """
    dados_paciente = pd.Series({
        "nome": "Maria Completa", "sexo": "feminino", "idade": 45,
        "peso_kg": 65, "altura_cm": 160, "nivel_atividade": "leve",
        "objetivo": "manter", "restricoes": "gluten", "glicemia": 95,
        "tg": 130, "hdl": 55, "ldl": 110, "ferritina": 70, "hemoglobina": 13
    })
    
    paciente = Paciente.from_dataframe(dados_paciente)
    
    assert paciente.nome == "Maria Completa"
    assert paciente.peso == 65
    assert paciente.restricoes == "gluten"

def test_from_dataframe_com_dados_opcionais_ausentes():
    """
    Testa se from_dataframe usa os valores padrão corretos quando
    colunas opcionais estão ausentes.
    """
    dados_paciente = pd.Series({
        "nome": "Carlos Básico", "sexo": "masculino", "idade": 50,
        "peso_kg": 85, "altura_cm": 178, "nivel_atividade": "sedentario"
    })
    
    paciente = Paciente.from_dataframe(dados_paciente)
    
    assert paciente.nome == "Carlos Básico"
    assert paciente.objetivo == "perder"
    assert paciente.restricoes == "nenhuma"
    assert paciente.glicemia is None

def test_calcular_imc_delega_corretamente(mocker, paciente_padrao):
    """
    Testa se o método `calcular_imc` da classe Paciente chama corretamente
    o método da HealthUtils, sem re-testar o cálculo em si.
    """
    mock_calcular_imc = mocker.patch('Paciente.HealthUtils.calcular_imc', return_value=(24.69, 'peso normal'))
    
    paciente_padrao.calcular_imc()
    
    mock_calcular_imc.assert_called_once_with(paciente_padrao.peso, paciente_padrao.altura)

def test_avaliar_exames_delega_corretamente(mocker, paciente_padrao):
    """
    Testa se `avaliar_exames` chama todos os métodos correspondentes da HealthUtils.
    """
    mock_glicemia = mocker.patch('Paciente.HealthUtils.avaliar_glicemia', return_value='normal')
    mock_tg = mocker.patch('Paciente.HealthUtils.avaliar_triglicerideos', return_value='normal')
    mock_colesterol = mocker.patch('Paciente.HealthUtils.avaliar_colesterol', return_value={'ldl': 'normal', 'hdl': 'bom'})
    mock_ferro = mocker.patch('Paciente.HealthUtils.avaliar_ferro', return_value='normal')
    
    resultado = paciente_padrao.avaliar_exames()
    
    mock_glicemia.assert_called_once_with(paciente_padrao.glicemia)
    mock_tg.assert_called_once_with(paciente_padrao.tg)
    mock_colesterol.assert_called_once_with(paciente_padrao.ldl, paciente_padrao.hdl)
    mock_ferro.assert_called_once_with(paciente_padrao.ferritina, paciente_padrao.hemoglobina)
    
    assert "glicemia" in resultado
    assert resultado["ferro"] == 'normal'