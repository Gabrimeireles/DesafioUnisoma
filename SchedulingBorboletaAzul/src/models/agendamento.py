import datetime

class Agendamento:
    def __init__(self, paciente, profissional, dia_semana, hora, local):
        self.paciente = paciente
        self.profissional = profissional
        self.dia_semana = dia_semana
        self.hora = hora
        self.local = local
        self.dt_atualizacao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
    def __str__(self):
        return f'Agendamento: {self.paciente} - {self.profissional} - {self.dia_semana} - {self.hora} - {self.local} - {self.dt_atualizacao}'