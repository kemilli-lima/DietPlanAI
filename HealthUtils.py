import unicodedata
import pandas as pd


class HealthUtils:
    """Classe utilitária para cálculos e avaliações de saúde."""

    @staticmethod
    def normalizar_texto(texto):
        nfkd = unicodedata.normalize("NFKD", texto)
        return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()

    @staticmethod
    def calcular_imc(peso, altura):
        if altura <= 0:
            return None, "Altura inválida."

        imc = peso / ((altura/100) ** 2)
        if imc < 18.5: classificacao = "Abaixo do peso"
        elif 18.5 <= imc < 25: classificacao = "Peso normal"
        elif 25 <= imc < 30: classificacao = "Sobrepeso"
        elif 30 <= imc < 35: classificacao = "Obesidade grau 1"
        elif 35 <= imc < 40: classificacao = "Obesidade grau 2"
        else: classificacao = "Obesidade grau 3"

        return round(imc, 2), HealthUtils.normalizar_texto(classificacao)

    @staticmethod
    def calcular_tbm_tdee_calorias(sexo, idade, peso, altura, nivel_atividade, objetivo):
        sexo = HealthUtils.normalizar_texto(sexo)
        objetivo = HealthUtils.normalizar_texto(objetivo)
        nivel_atividade = HealthUtils.normalizar_texto(nivel_atividade)

        if sexo == 'masculino':
            tmb = 10 * peso + 6.25 * altura - 5 * idade + 5
        else:
            tmb = 10 * peso + 6.25 * altura - 5 * idade - 161

        fatores = {"sedentario": 1.2, "leve": 1.375, "moderado": 1.55, "intenso": 1.725}
        tdee = tmb * fatores[nivel_atividade]

        if objetivo == 'perder':
            return tmb, tdee * 0.85
        elif objetivo == 'ganhar':
            return tmb, tdee * 1.10
        return round(tmb, 2), round(tdee, 2)

    @staticmethod
    def avaliar_glicemia(glicemia):
        if glicemia < 100: return 'normal'
        elif 100 <= glicemia <= 125: return 'pre_diabetes'
        else: return 'diabetes'

    @staticmethod
    def avaliar_triglicerideos(tg):
        if 150 <= tg < 200: return 'moderado'
        elif tg >= 200: return 'alto'
        return 'normal'

    @staticmethod
    def avaliar_colesterol(ldl, hdl):
        resultado = {}
        resultado['ldl'] = 'normal' if ldl < 100 else 'moderado' if ldl < 160 else 'critico'
        if hdl < 40: resultado['hdl'] = 'ruim'
        elif 40 <= hdl <= 60: resultado['hdl'] = 'moderado'
        else: resultado['hdl'] = 'bom'
        return resultado

    @staticmethod
    def avaliar_ferro(ferritina, hemoglobina):
        if ferritina < 30 or hemoglobina < 12:
            return 'baixa'
        return "normal"

    @staticmethod
    def metas_macros(tmb, tdee, peso, sexo, idade, altura, nivel_atividade, objetivo, glicemia=None, tg=None):
        if objetivo == 'perder': proteina_g = peso * 1.5
        elif objetivo == 'ganhar': proteina_g = peso * 1.7
        else: proteina_g = peso * 1.2

        if glicemia and glicemia >= 100:
            proteina_g = max(proteina_g, peso * 1.5)

        gordura_kcal = tdee * 0.30
        gordura_g = gordura_kcal / 9
        fibras_g = (tdee/1000) * 14

        restante_kcal = tdee - (proteina_g * 4 + gordura_g * 9 + fibras_g * 2)
        carboidratos_g = restante_kcal / 4

        if glicemia and glicemia >= 100:
            carboidratos_g = (tdee * 0.4) / 4
        if tg and tg >= 200:
            carboidratos_g = (tdee * 0.35) / 4

        return {
            'tmb': round(tmb),
            'total_kcal': round(tdee),
            'proteina_g': round(proteina_g),
            'gordura_g': round(gordura_g),
            'carboidratos_g': round(carboidratos_g),
            'fibras_g': round(fibras_g)
        }

    @staticmethod
    def divisao_refeicoes(objetivo, glicemia, macros, total_kcal, restricao=None):
        objetivo = HealthUtils.normalizar_texto(objetivo)
        kcal_ref = {
            "cafe_da_manha": 0.25, "lanche_manha": 0.1, "almoco": 0.35,
            "lanche_tarde": 0.1, "jantar": 0.15, "ceia": 0.05
        }

        if HealthUtils.avaliar_glicemia(glicemia) in ['diabetes', 'pre-diabetes']:
            kcal_ref = {
                "cafe_da_manha": 0.2, "lanche_manha": 0.1, "almoco": 0.25,
                "lanche_tarde": 0.1, "jantar": 0.25, "ceia": 0.1
            }
        elif objetivo == 'perder':
            kcal_ref = {
                "cafe_da_manha": 0.2, "almoco": 0.3, "lanche_manha": 0.1,
                "lanche_tarde": 0.1, "jantar": 0.25, "ceia": 0.05
            }
        elif objetivo == 'ganhar':
            kcal_ref = {
                "cafe_da_manha": 0.2, "lanche_manha": 0.1, "almoco": 0.3,
                "lanche_tarde": 0.15, "jantar": 0.3, "ceia": 0.05
            }

        dados_refs = []
        for refeicao, percentual in kcal_ref.items():
            kcal = total_kcal * percentual
            dados_refs.append({
                "Refeicao": refeicao,
                "Kcal": round(kcal, 1),
                "Carbo": round(macros['carboidratos_g'] * percentual, 1),
                "Proteina": round(macros['proteina_g'] * percentual, 1),
                "Gordura": round(macros['gordura_g'] * percentual, 1),
                "Fibra": round(macros['fibras_g'] * percentual, 1),
                "Restricao": restricao if restricao else "Nenhuma"
            })

        return dados_refs

    @staticmethod
    def aplicar_restricao(df, restricao):
        restricao = restricao.lower()
        if restricao == "lactointolerante":
            return df[(df["contains_lactose"] == False) & (df["contains_milk"] == False)]
        elif restricao == "gluten":
            return df[df["contains_gluten"] == False]
        elif restricao == "frutos_do_mar":
            return df[df["contains_shellfish"] == False]
        elif restricao == "alergia_amendoim":
            return df[df["contains_peanut"] == False]
        elif restricao == "vegano":
            return df[df["vegan"] == True]
        elif restricao == "vegetariano":
            return df[df["vegetarian"] == True]
        elif restricao == "hipertensao":
            return df[df["sodium_mg"].fillna(0) < 400]
        return df

    @staticmethod
    def load_patient_data(file_path):
        return pd.read_csv(file_path)
