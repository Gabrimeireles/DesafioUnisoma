import pandas as pd
import numpy as np

from models.profissional import Profissional
from models.paciente import Paciente

def traduzir_pacientes(idade_paciente_df, dispon_paciente_df, local_paciente_df):
    pacientes = []
    
    for index, row in idade_paciente_df.iterrows():
        nome = row['paciente']
        idade = row['idade']
        
        disponibilidade_dict = {dia: [] for dia in ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb']}
        dispon_paciente_df['paciente'] = dispon_paciente_df['paciente'].ffill()
        disponibilidade_paciente = dispon_paciente_df[dispon_paciente_df['paciente'] == nome]
        for dia_semana in disponibilidade_paciente['dia_semana'].unique():
            dias_disponiveis = disponibilidade_paciente[disponibilidade_paciente['dia_semana'] == dia_semana]

            # Verifica se há disponibilidade para o dia e preenche o dicionário
            if not dias_disponiveis.empty:
                disponibilidade = dias_disponiveis.iloc[0]
                horarios_disponiveis = [hora for hora in range(8, 21) if is_marked(disponibilidade[f'hr_{hora}'])]

                disponibilidade_dict[dia_semana] = horarios_disponiveis

        localidade = {}
        for dia_semana in local_paciente_df.columns[2:]:
            locais_disponiveis = []
            if is_marked(local_paciente_df.loc[index, dia_semana]):
                locais_disponiveis.append(dia_semana)
            if is_marked(local_paciente_df.loc[index, 'virtual_epsi']):
                locais_disponiveis.append('virtual')
            localidade[dia_semana] = locais_disponiveis
        
        pacientes.append(Paciente(nome, idade, disponibilidade_dict, localidade))
    return pacientes

def traduzir_profissional(regra_profissional_df, dispon_profissional_df, local_profissional_df):
    profissionais = []
    
    for index, row in regra_profissional_df.iterrows():
        nome = row['profissional']
        tipo = row['tipo']
        horas_semana = row['horas_semana']
        
        faixa_atendimento = []
        if is_marked(row['infantil']):
            faixa_atendimento.append('infantil')
        if is_marked(row['adolescente']):
            faixa_atendimento.append('adolescente')
        if is_marked(row['adulto']):
            faixa_atendimento.append('adulto')
        
        disponibilidade_dict = {dia: [] for dia in ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb']}
        dispon_profissional_df['profissional'] = dispon_profissional_df['profissional'].ffill()
        disponibilidade_paciente = dispon_profissional_df[dispon_profissional_df['profissional'] == nome]
        for dia_semana in disponibilidade_paciente['dia_semana'].unique():
            dias_disponiveis = disponibilidade_paciente[disponibilidade_paciente['dia_semana'] == dia_semana]

            # Verifica se há disponibilidade para o dia e preenche o dicionário
            if not dias_disponiveis.empty:
                disponibilidade = dias_disponiveis.iloc[0]
                horarios_disponiveis = [hora for hora in range(8, 21) if is_marked(disponibilidade[f'hr_{hora}'])]

                disponibilidade_dict[dia_semana] = horarios_disponiveis
                
        localidade = {}
        for dia_semana in local_profissional_df.columns[1:]:
            locais_disponiveis = []
            if is_marked(local_profissional_df.loc[index, dia_semana]):
                locais_disponiveis.append(dia_semana)
            if is_marked(local_profissional_df.loc[index, 'virtual_epsi']):
                locais_disponiveis.append('virtual')
            localidade[dia_semana] = locais_disponiveis
        
        profissionais.append(Profissional(nome, tipo, horas_semana, faixa_atendimento, disponibilidade_dict, localidade))
    return profissionais

def is_marked(cell):
    return str(cell).strip().lower() == 'x'

def agendamento_to_df(agendamentos):
    dados = {
        'paciente': [ag.paciente for ag in agendamentos],
        'profissional': [ag.profissional for ag in agendamentos],
        'dia_semana': [ag.dia_semana for ag in agendamentos],
        'hora': [ag.hora for ag in agendamentos],
        'local': [ag.local for ag in agendamentos],
        'dt_atualizacao': [ag.dt_atualizacao for ag in agendamentos]  # Formata a data e hora
    }
    return pd.DataFrame(dados)
    