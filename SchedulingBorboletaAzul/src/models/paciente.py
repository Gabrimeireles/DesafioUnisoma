class Paciente:
    def __init__(self, nome, idade, disponibilidade, virtual, localidade):
        self.name = nome # nome do paciente
        self.idade = idade # idade do paciente
        self.disponibilidade = disponibilidade # {'Segunda' : [9,10,11], 'Quarta' : [11,12,13]}
        self.virtual = virtual # True ou False
        self.localidade = localidade # Asa - PÁSSAROS 
        self.tipo = self.definir_tipo() # infatil, adolescente, adulto
        
    def definir_tipo(self):
        if self.idade < 12:
            return 'infatil'
        elif 12 <= self.idade < 18:
            return 'adolescente'
        elif self.idade > 18:
            return 'adulto'
    
    
    def pode_ser_agendado(self, horario, dia):
        if horario in self.disponibilidade[dia]: # dia = 'Segunda', horario = 9
            return True
        return False
    
    def atende_virtual(self):
        return self.virtual 
    
    def __str__(self):
        return f'Paciente: {self.name} - Idade: {self.idade} - Tipo: {self.tipo} - Localidade: {self.localidade} - Virtual: {self.virtual} - Disponibilidade: {self.disponibilidade}'
    
    
    