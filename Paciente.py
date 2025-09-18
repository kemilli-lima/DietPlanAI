from HealthUtils import HealthUtils


class Paciente:
    def __init__(self, nome, sexo, idade, peso, altura, nivel_atividade,
                 objetivo="perder", restricoes="nenhuma",
                 glicemia=None, tg=None, hdl=None, ldl=None,
                 ferritina=None, hemoglobina=None):
        self.nome = nome
        self.sexo = sexo
        self.idade = idade
        self.peso = peso
        self.altura = altura
        self.nivel_atividade = nivel_atividade
        self.objetivo = objetivo
        self.restricoes = restricoes
        self.glicemia = glicemia
        self.tg = tg
        self.hdl = hdl
        self.ldl = ldl
        self.ferritina = ferritina
        self.hemoglobina = hemoglobina

    @classmethod
    def from_dataframe(cls, row):
        """Cria um Paciente a partir de uma linha de DataFrame."""
        return cls(
            nome=row["nome"],
            sexo=row["sexo"],
            idade=row["idade"],
            peso=row["peso_kg"],
            altura=row["altura_cm"],
            nivel_atividade=row["nivel_atividade"],
            objetivo=row.get("objetivo", "perder"),
            restricoes=row.get("restricoes", "nenhuma"),
            glicemia=row.get("glicemia"),
            tg=row.get("tg"),
            hdl=row.get("hdl"),
            ldl=row.get("ldl"),
            ferritina=row.get("ferritina"),
            hemoglobina=row.get("hemoglobina"),
        )

    def calcular_imc(self):
        return HealthUtils.calcular_imc(self.peso, self.altura)

    def avaliar_exames(self):
        return {
            "glicemia": HealthUtils.avaliar_glicemia(self.glicemia),
            "triglicerideos": HealthUtils.avaliar_triglicerideos(self.tg),
            "colesterol": HealthUtils.avaliar_colesterol(self.ldl, self.hdl),
            "ferro": HealthUtils.avaliar_ferro(self.ferritina, self.hemoglobina),
        }
