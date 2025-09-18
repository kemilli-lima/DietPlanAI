from HealthUtils import HealthUtils
from Paciente import Paciente
from GeneticMealPlanner import GeneticMealPlanner
from dicionario_alimentos import dicionario_alimentos
import pandas as pd
import random

class MealPlanGenerator:

    def __init__(self, paciente: Paciente, saladas_csv="saladas.csv"):
        self.paciente = paciente
        self.refeicoes_dict = {}
        self.saladas_df = pd.read_csv(saladas_csv)

        self.imc, self.classificacao_imc = paciente.calcular_imc()
        self.tmb, self.tdee = HealthUtils.calcular_tbm_tdee_calorias(
            paciente.sexo, paciente.idade, paciente.peso,
            paciente.altura, paciente.nivel_atividade, paciente.objetivo
        )
        # arredonda TDEE para 2 casas
        self.tdee = round(self.tdee, 2)
        self.macros = HealthUtils.metas_macros(
            self.tmb, self.tdee, paciente.peso, paciente.sexo, paciente.idade,
            paciente.altura, paciente.nivel_atividade, paciente.objetivo,
            paciente.glicemia, paciente.tg
        )

    def _formatar_refeicoes(self):
        nomes_refeicoes = {
            "cafe_da_manha": "🥐 Café da Manhã",
            "lanche_manha": "🍎 Lanche da Manhã",
            "almoco": "🍽️ Almoço",
            "lanche_tarde": "☕ Lanche da Tarde",
            "jantar": "🍲 Jantar",
            "ceia": "🥛 Ceia"
        }
        
        refeicoes_formatadas = ""
        
        for refeicao, dados in self.refeicoes_dict.items():
            meta = dados["meta"]
            df = dados["foods"]
            titulo = nomes_refeicoes.get(refeicao, refeicao.title())
            
            refeicoes_formatadas += f"\n## {titulo}\n"
            # refeicoes_formatadas += (
            #     f"- Meta: {meta['Kcal']} kcal | {meta['Proteina']}g proteína | "
            #     f"{meta['Gordura']}g gordura | {meta['Carbo']}g carboidrato | {meta['Fibra']}g fibras\n\n"
            # )
            
            refeicoes_formatadas += "| Alimento | Calorias | Proteínas | Gorduras | Carboidratos | Fibras |\n"
            refeicoes_formatadas += "|----------|----------|-----------|----------|---------------|--------|\n"
            
            total_kcal = total_proteina = total_gordura = total_carbo = total_fibra = 0

            for _, row in df.iterrows():
                kcal = row['kcal']
                protein = row['protein_g']
                fat = row['fat_g']
                carbs = round((kcal - (4 * protein) - (9 * fat)) / 4, 1) if kcal and protein and fat else 0
                fiber = row['fiber_g'] if pd.notna(row['fiber_g']) and row['fiber_g'] != "nang" else 0
                
                # Nome bonitinho com dicionário
                food_id = row['id']
                food_name = dicionario_alimentos.get(row['food'], row['food']).title()

                # Ajustes específicos
                if "Pão" in food_name:
                    food_name += " (2 fatias ~ 60-70g)"
                if "Ovo" in food_name:
                    food_name += " (2 ovos médios)"

                refeicoes_formatadas += f"| {food_name} | {kcal} | {protein} | {fat} | {carbs} | {fiber} |\n"
                
                total_kcal += kcal
                total_proteina += protein
                total_gordura += fat
                total_carbo += carbs
                total_fibra += fiber

            # Adicionar queijo nos lanches
            if refeicao in ["lanche_manha", "lanche_tarde"]:
                tem_queijo = any("queijo" in row['food'].lower() for _, row in df.iterrows())
                
                if ("lactointolerante" not in self.paciente.restricoes) and not tem_queijo:
                    refeicoes_formatadas += "| Queijo (1 fatia ~30g) | 90 | 6 | 7 | 1 | 0 |\n"
                    total_kcal += 90
                    total_proteina += 6
                    total_gordura += 7
                    total_carbo += 1

            # Whey na ceia
            if refeicao == "ceia":
                if self.paciente.restricoes == "lactointolerante":
                    refeicoes_formatadas += "| Whey Isolado (1 dose e meia) | 180 | 36 | 1 | 2 | 0 |\n"
                    total_kcal += 180
                    total_proteina += 36
                    total_gordura += 1
                    total_carbo += 2
                else:
                    refeicoes_formatadas += "| Whey Protein (1 dose) | 120 | 24 | 1 | 2 | 0 |\n"
                    total_kcal += 120
                    total_proteina += 24
                    total_gordura += 1
                    total_carbo += 2

            # Totais da refeição
            refeicoes_formatadas += f"\n**Total Nutricional:** {round(total_kcal,1)} kcal | {round(total_proteina,1)}g proteína | {round(total_gordura,1)}g gordura | {round(total_carbo,1)}g carboidrato | {round(total_fibra,1)}g fibras\n"

            # Saladas no almoço e jantar
            if refeicao in ["almoco", "jantar"]:
                saladas = self.saladas_df.sample(3)
                refeicoes_formatadas += "\n### 🥗 Sugestões de saladas (Podem ser ingeridas na quantidade desejada pelo paciente, aumentando ainda mais a ingestão de fibras):\n"
                for _, s in saladas.iterrows():
                    ingredientes = [s[c] for c in s.index if c.startswith("ingrediente") and pd.notna(s[c])]
                    refeicoes_formatadas += f"- {s['nome_salada']}: " + ", ".join(ingredientes) + "\n"
        
        return refeicoes_formatadas

    def gerar_cardapio(self):
        refeicoes = ["cafe_da_manha", "lanche_manha", "almoco", "lanche_tarde", "jantar", "ceia"]
        exames = self.paciente.avaliar_exames()

        for ref in refeicoes:
            metas = HealthUtils.divisao_refeicoes(
                self.paciente.objetivo, self.paciente.glicemia, self.macros,
                self.tdee, self.paciente.restricoes
            )
            meta_ref = next((m for m in metas if m["Refeicao"] == ref), None)
            if not meta_ref:
                continue

            planner = GeneticMealPlanner(
                refeicao=ref,
                restricao=self.paciente.restricoes,
                target_kcal=meta_ref["Kcal"],
                target_protein_g=meta_ref["Proteina"],
                target_carbs_g=meta_ref["Carbo"],
                target_fat_g=meta_ref["Gordura"],
                nivel_triglicerideos=exames["triglicerideos"],
                nivel_hdl=exames["colesterol"]["hdl"],
                nivel_ldl=exames["colesterol"]["ldl"],
                nivel_ferro=exames["ferro"],
                target_fibers_g=meta_ref["Fibra"],
                objetivo=self.paciente.objetivo
            )
            foods = planner.run()
            self.refeicoes_dict[ref] = {"meta": meta_ref, "foods": foods}

    def gerar_markdown_final(self):
        agua = round(self.paciente.peso * 35 / 1000, 1)

        refeicoes_formatadas = self._formatar_refeicoes()
        md = f"""# 🍽️ Cardápio Diário Personalizado

        ## 👤 Dados do Paciente
        **- Nome:** {self.paciente.nome}
        **- Sexo:** {self.paciente.sexo}
        **- Idade:** {self.paciente.idade} anos
        **- Peso:** {self.paciente.peso} kg
        **- Altura:** {self.paciente.altura} cm
        **- Objetivo:** {self.paciente.objetivo} peso
        **- Restrições alimentares:** {self.paciente.restricoes}
        **- IMC:** {self.imc} ({self.classificacao_imc})
        **- *TMB:** {self.tmb} kcal
        **- TDEE:** {self.tdee:.2f} kcal (meta diária de calorias)
        **- Metas diárias:** {self.macros['proteina_g']} g proteínas, {self.macros['gordura_g']} g gorduras, {self.macros['carboidratos_g']} g carboidratos, {self.macros['fibras_g']} g fibras

        ## 🥤 Hidratação
        - Recomendação diária: **{agua} litros de água**
        - Café e chá sem açúcar à vontade no café da manhã e nos lanches, mas cuidado com a quantidade de cafeína ao longo do dia! ☕
        - ☕ UMA xícara de café (sem açúcar) pode ajudar na queima de gordura, mas evite exageros!

        ---
        {refeicoes_formatadas}
        """
        return md


if __name__ == "__main__":
    df_pacientes = HealthUtils.load_patient_data("pacientes_ro.csv")
    paciente = Paciente.from_dataframe(df_pacientes.iloc[2])

    generator = MealPlanGenerator(paciente)
    generator.gerar_cardapio()
    markdown = generator.gerar_markdown_final()

    with open("cardapio_final.md", "w", encoding="utf-8") as f:
        f.write(markdown)

    print("✅ Cardápio gerado em cardapio_final.md")
