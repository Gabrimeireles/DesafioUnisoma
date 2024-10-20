import pandas as pd
from models.profissional import Profissional
from models.paciente import Paciente

# Funções principais para traduzir pacientes e profissionais
def traduzir_pacientes(idade_paciente_df, dispon_paciente_df, local_paciente_df):
    return [
        Paciente(
            nome=row['paciente'],
            idade=row['idade'],
            disponibilidade=construir_disponibilidade(row['paciente'], dispon_paciente_df, 'paciente'),
            localidade=construir_localidade(index, local_paciente_df, local_paciente_df.columns[2:])
        )
        for index, row in idade_paciente_df.iterrows()
    ]

def traduzir_profissionais(regra_profissional_df, dispon_profissional_df, local_profissional_df):
    return [
        Profissional(
            nome=row['profissional'],
            tipo=row['tipo'],
            horas_semana=row['horas_semana'],
            faixa_atendimento=construir_faixa_atendimento(row),
            disponibilidade=construir_disponibilidade(row['profissional'], dispon_profissional_df, 'profissional'),
            localidade=construir_localidade(index, local_profissional_df, local_profissional_df.columns[1:])
        )
        for index, row in regra_profissional_df.iterrows()
    ]

# Função genérica para construir disponibilidade
def construir_disponibilidade(nome, dispon_df, nome_coluna):
    disponibilidade_dict = {dia: [] for dia in ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb']}
    
    dispon_df[nome_coluna] = dispon_df[nome_coluna].ffill()
    disponibilidade = dispon_df[dispon_df[nome_coluna] == nome]
    
    for dia_semana in disponibilidade['dia_semana'].unique():
        dias_disponiveis = disponibilidade[disponibilidade['dia_semana'] == dia_semana]
        if not dias_disponiveis.empty:
            disponibilidade_row = dias_disponiveis.iloc[0]
            horarios_disponiveis = [hora for hora in range(8, 21) if is_marked(disponibilidade_row[f'hr_{hora}'])]
            disponibilidade_dict[dia_semana] = horarios_disponiveis
    
    return disponibilidade_dict

# Função genérica para construir localidade
def construir_localidade(index, local_df, colunas):
    localidade = {}
    for dia_semana in colunas:
        locais_disponiveis = []
        if is_marked(local_df.loc[index, dia_semana]):
            locais_disponiveis.append(dia_semana)
        if is_marked(local_df.loc[index, 'virtual_epsi']):
            locais_disponiveis.append('virtual')
        localidade[dia_semana] = locais_disponiveis
    return localidade

# Função para construir faixa de atendimento
def construir_faixa_atendimento(row):
    faixa_atendimento = []
    if is_marked(row['infantil']):
        faixa_atendimento.append('infantil')
    if is_marked(row['adolescente']):
        faixa_atendimento.append('adolescente')
    if is_marked(row['adulto']):
        faixa_atendimento.append('adulto')
    return faixa_atendimento

# Função para verificar se a célula está marcada
def is_marked(cell):
    return str(cell).strip().lower() == 'x'

# Função para converter agendamentos para DataFrame
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

def inconsistencias_to_df(inconsistencias):
    """Converte uma lista de objetos Inconsistencia em um DataFrame."""
    # Usando list comprehension para coletar os dados das inconsistências
    dados = {
        'tabela': [inconsistencia.tabela for inconsistencia in inconsistencias],
        'tipo': [inconsistencia.tipo for inconsistencia in inconsistencias],
        'mensagem': [inconsistencia.mensagem for inconsistencia in inconsistencias],
        'dt_atualizacao': [inconsistencia.dt_atualizacao for inconsistencia in inconsistencias]
    }
    return pd.DataFrame(dados)
    