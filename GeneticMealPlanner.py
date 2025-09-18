import pandas as pd
import random
from HealthUtils import HealthUtils


class GeneticMealPlanner:
    """Classe para gerar refeições com Algoritmo Genético considerando metas de macronutrientes."""

    BLUEPRINT = {
        "cafe_da_manha": ["frutas_e_derivados", "cereais_e_derivados", "ovos_e_derivados"],
        "lanche_manha": ["frutas_e_derivados", "leite_e_derivados"],
        "almoco_jantar": [
            ["carnes_e_derivados", "pescados_e_frutos_do_mar"],
            "leguminosas_e_derivados",
            ["cereais_e_derivados", "verduras_hortalicas_e_derivados"]
        ],
        "lanche_tarde": ["frutas_e_derivados", ["leite_e_derivados", "ovos_e_derivados"]],
    }

    def __init__(self, refeicao="cafe_da_manha", restricao=None,
                 target_kcal=500, target_protein_g=None,
                 target_carbs_g=None, target_fat_g=None,
                 nivel_triglicerideos=None,
                 nivel_hdl=None, nivel_ldl=None, nivel_ferro=None,
                 target_fibers_g=None, objetivo=None):
        self.refeicao = refeicao
        self.restricao = restricao
        self.target_kcal = target_kcal
        self.target_protein_g = target_protein_g
        self.target_carbs_g = target_carbs_g
        self.target_fat_g = target_fat_g
        self.nivel_triglicerideos = nivel_triglicerideos
        self.nivel_hdl = nivel_hdl
        self.nivel_ldl = nivel_ldl
        self.nivel_ferro = nivel_ferro
        self.target_fibers_g = target_fibers_g
        self.objetivo = objetivo

        self.foods = self._load_foods()
        self.required_cats = self._get_required_categories()

    # =============================
    # Carregamento de alimentos
    # =============================
    def _load_foods(self):
        if self.refeicao in ["cafe_da_manha", "lanche_tarde"]:
            #if self.refeicao == "lanche_tarde" and self.objetivo == "perder":
            #     df = pd.read_csv("lanche_ceia.csv")
            # else:
            df = pd.read_csv("cafe_da_manha.csv")
        elif self.refeicao in ["almoco", "jantar"]:
            df = pd.read_csv("almoco_jantar.csv")
        elif self.refeicao in ["lanche_manha", "ceia"]:
            df = pd.read_csv("lanche_ceia.csv")
        else:
            raise ValueError(f"Refeição '{self.refeicao}' não reconhecida")

        df = HealthUtils.aplicar_restricao(df.copy(), self.restricao) if self.restricao else df.copy()
        if df.empty:
            raise ValueError(f"Nenhum alimento disponível para '{self.refeicao}' com a restrição '{self.restricao}'")
        return df

    def _get_required_categories(self):
        if self.refeicao == "cafe_da_manha":
            cats = GeneticMealPlanner.BLUEPRINT["cafe_da_manha"].copy()
        elif self.refeicao == "lanche_tarde":
            cats = GeneticMealPlanner.BLUEPRINT["lanche_tarde"].copy()
        elif self.refeicao in ["almoco", "jantar"]:
            cats = GeneticMealPlanner.BLUEPRINT["almoco_jantar"].copy()
        elif self.refeicao in ["lanche_manha", "ceia"]:
            cats = GeneticMealPlanner.BLUEPRINT["lanche_manha"].copy()
        else:
            cats = []

        # Restrição para intolerantes à lactose
        if self.restricao == "lactointolerante" and "leite_e_derivados" in cats:
            cats.remove("leite_e_derivados")
            cats.extend(["frutas_e_derivados", "ovos_e_derivados"])
        
        if self.refeicao == "cafe_da_manha" and self.restricao == "gluten":
            cats = ["leite_e_derivados" if c == "cereais_e_derivados" else c for c in cats]

        return cats

    def _create_individual(self): 
        chosen = []
        for cat in self.required_cats:
            if isinstance(cat, list):
                selected_cat = random.choice(cat) 
            else:
                selected_cat = cat 
        
            candidates = self.foods[self.foods["category"] == selected_cat]
            if not candidates.empty:
                chosen.append(candidates.sample(1)["id"].iloc[0])
        return chosen
    # =============================
    # Operadores Genéticos
    # =============================
    def _fitness(self, ind):
        subset = self.foods[self.foods["id"].isin(ind)]
        
        kcal = subset["kcal"].sum()
        protein = subset["protein_g"].sum()
        fat = subset["fat_g"].sum()
        fibers = subset["fiber_g"].fillna(0).sum()
        iron = subset["iron_mg"].fillna(0).sum()
        sodium = subset["sodium_mg"].fillna(0).sum()

        # Usa carb_g se estiver disponível, senão estima
        if "carbs_g" in subset.columns:
            carbs = subset["carbs_g"].sum()
        else:
            carbs = (kcal - (protein * 4 + fat * 9)) / 4
            carbs = max(0, carbs)  # evita valores negativos

        # Diferenças absolutas
        diff_kcal = abs(self.target_kcal - kcal)
        diff_protein = abs((self.target_protein_g or 0) - protein)
        diff_fat = abs((self.target_fat_g or 0) - fat)
        diff_fibers = abs((self.target_fibers_g or 0) - fibers)
        diff_carbs = abs((self.target_carbs_g or 0) - carbs)

        # Penalidade inicial com pesos ajustados
        penalty = (
            diff_kcal * 2 +         
            diff_protein * 5 +      
            diff_carbs * 2 +
            diff_fat * 2 +
            diff_fibers * 5
        )

        if self.target_protein_g and protein < self.target_protein_g:
            penalty += (self.target_protein_g - protein) * 8
        if self.target_fibers_g and fibers < self.target_fibers_g:
            penalty += (self.target_fibers_g - fibers) * 6

        if self.nivel_triglicerideos in ['moderado', 'alto']:
            penalty += fat * 0.4
        if self.nivel_ldl in ['moderado', 'critico']:
            penalty += fat * 0.5
        if self.nivel_ferro == 'baixa':
            penalty -= iron * 1.0  

      
        penalty += sodium / 100

        if kcal > self.target_kcal * 1.15:
            return -float("inf")  # indivíduo é descartado

        # Bonificação por variedade de categorias
        variety = subset["category"].nunique()
        return -penalty + variety * 5

    def _select(self, population):
        a, b = random.sample(population, 2)
        return a if self._fitness(a) > self._fitness(b) else b

    def _crossover(self, p1, p2):
        child = []
        for i, cat in enumerate(self.required_cats):
            chosen = None
            for parent in [p1, p2]:
                candidate = parent[i] if i < len(parent) else None
                if candidate and candidate not in child:
                    chosen = candidate
                    break
            if not chosen:
                if isinstance(cat, list):
                    cat = random.choice(cat)
                candidates = self.foods[self.foods["category"] == cat]
                if not candidates.empty:
                    chosen = candidates.sample(1)["id"].iloc[0]
            if chosen:
                child.append(chosen)
        return child

    def _mutate(self, ind):
        if random.random() < 0.2:
            idx = random.randrange(len(ind))
            cat = self.required_cats[idx]
            if isinstance(cat, list):
                cat = random.choice(cat)
            candidates = self.foods[self.foods["category"] == cat]
            if not candidates.empty:
                ind[idx] = candidates.sample(1)["id"].iloc[0]
        return ind

    # =============================
    # Execução do Algoritmo Genético
    # =============================
    def run(self, pop_size=50, generations=100):
        population = [self._create_individual() for _ in range(pop_size)]

        for _ in range(generations):
            new_pop = []
            for _ in range(pop_size):
                p1 = self._select(population)
                p2 = self._select(population)
                child = self._crossover(p1, p2)
                child = self._mutate(child)
                new_pop.append(child)
            population = new_pop

        best = max(population, key=lambda ind: self._fitness(ind))
        return self.foods[self.foods["id"].isin(best)]

