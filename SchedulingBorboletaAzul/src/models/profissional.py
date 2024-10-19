class Profissional:
    def __init__(self, nome ,tipo, horas_semana, faixa_atendimento, disponibilidade, localidade):
        self.nome = nome # nome do profissional
        self.tipo = tipo # estagiario/voluntario
        self.horas_semana = horas_semana # 20, 30, 40
        self.faixa_atendimento = faixa_atendimento # infantil, adolescente, adulto 
        self.disponibilidade = disponibilidade # {'Segunda' : [9,10,11], 'Quarta' : [11,12,13]}
        self.localidade = localidade # Asa - PÁSSAROS
        self.horas_utilizadas = 0 # controle de horas utilizadas
        
    def pode_atender(self, dia, hora, tipo_paciente):
        if hora in self.disponibilidade[dia] and tipo_paciente in self.faixa_atendimento:
            return self.horas_utilizadas < self.horas_semana
        return False
    
    def pode_atender_localidade(self, localidade):
        return any(loc in localidade for loc in self.localidade.keys())
    
    def __str__(self):
        return f'Profissional: {self.nome} - Tipo: {self.tipo} - Horas Semana: {self.horas_semana} - Faixa Atendimento: {self.faixa_atendimento} - Localidade: {self.localidade} - Disponibilidade: {self.disponibilidade}'