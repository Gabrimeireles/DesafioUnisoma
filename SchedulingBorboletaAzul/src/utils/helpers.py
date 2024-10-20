import pandas as pd
import os
from models.profissional import Profissional
from models.paciente import Paciente
from models.Inconsistencia import verificar_inconsistencias_nao_agendamento, verificar_inconsistencias_pacientes, verificar_inconsistencias_profissionais
from models.agendamento import Agendamento
from services.Optimizer import otimizar_agendamentos
from services.ExcelHandler import ExcelHandler

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


def processar_agendamentos(file_path, considerar_sessoes_anteriores):
    excel_handler = ExcelHandler(file_path)
    idade_paciente, dispon_patiente, local_paciente, regra_profissional, dispon_profissional, local_profissional, kpi_atendimento = excel_handler.ler_planilha()
    
    if not considerar_sessoes_anteriores:
        kpi_atendimento = None
    
    inconsistencias = verificar_inconsistencias_pacientes(idade_paciente, dispon_patiente, local_paciente)
    inconsistencias += verificar_inconsistencias_profissionais(regra_profissional, dispon_profissional, local_profissional)
    
    df_inconsistencia = inconsistencias_to_df(inconsistencias)
    excel_handler.escrever_inconsistencia(df_inconsistencia)
    
    if any(inc.tipo == 'erro' for inc in inconsistencias):
        return {'status': 'erro', 'inconsistencias': inconsistencias}
    
    pacientes = traduzir_pacientes(idade_paciente, dispon_patiente, local_paciente)
    profissionais = traduzir_profissionais(regra_profissional, dispon_profissional, local_profissional)
    
    prob, x, pacientes_nao_agendados, profissionais_nao_agendados = otimizar_agendamentos(pacientes, profissionais, kpi_atendimento)
    
    inconsistencias_nao_agendamento = verificar_inconsistencias_nao_agendamento(pacientes_nao_agendados, profissionais_nao_agendados)
    df_inconsistencia_nao_agendamento = inconsistencias_to_df(inconsistencias_nao_agendamento)
    excel_handler.escrever_inconsistencia(df_inconsistencia_nao_agendamento)
    
    agendamentos = []            
    for var in prob.variables():
        if var.varValue == 1:
            for chave, var_x in x.items():
                if var.name == var_x.name:
                    paciente, profissional, data, hora, local = chave
                    agendamentos.append(Agendamento(paciente, profissional, data, hora, local))
    
    df_solução = agendamento_to_df(agendamentos)
    excel_handler.escrever_solucao(df_solução)

    # Salvando os dados em CSV
    salvar_dados_em_csv(pacientes, profissionais, df_solução, df_inconsistencia, kpi_atendimento)

    data_atual = pd.Timestamp.now()
    if kpi_atendimento is None:  # Escrevendo KPI de atendimento pela primeira vez
        kpi_atendimento = pd.DataFrame(columns=['paciente', 'profissional', 'sessões', 'dt_atualizacao'])
        kpi_atendimento['paciente'] = [ag.paciente for ag in agendamentos]
        kpi_atendimento['profissional'] = [ag.profissional for ag in agendamentos]
        kpi_atendimento['sessões'] = 1
        kpi_atendimento['dt_atualizacao'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
        excel_handler.escrever_kpi(kpi_atendimento, 'numSessõesPaciente')
    else:  # Atualizando KPI de atendimento
        ultima_atualizacao = pd.to_datetime(kpi_atendimento['dt_atualizacao'].max(), format='%Y-%m-%d %H:%M')
        if ultima_atualizacao.isocalendar()[1] == data_atual.isocalendar()[1]:
            kpi_atendimento = pd.DataFrame(columns=['paciente', 'profissional', 'sessões', 'dt_atualizacao'])
            kpi_atendimento['paciente'] = [ag.paciente for ag in agendamentos]
            kpi_atendimento['profissional'] = [ag.profissional for ag in agendamentos]
            kpi_atendimento['sessões'] = 1
            kpi_atendimento['dt_atualizacao'] = data_atual.strftime('%Y-%m-%d %H:%M')
        else:  # Atualizando sessões de atendimento
            for ag in agendamentos:
                index = kpi_atendimento[(kpi_atendimento['paciente'] == ag.paciente) & (kpi_atendimento['profissional'] == ag.profissional)].index
                if not index.empty:
                    kpi_atendimento.loc[index, 'sessões'] += 1
                else:
                    kpi_atendimento = kpi_atendimento.append({'paciente': ag.paciente, 'profissional': ag.profissional, 'sessões': 1}, ignore_index=True)
        excel_handler.escrever_kpi(kpi_atendimento, 'KPIAtendimento')
    
    return {'status': 'sucesso', 'agendamentos': agendamentos, 'inconsistencias': inconsistencias_nao_agendamento}

def salvar_dados_em_csv(pacientes, profissionais, df_solucao, df_inconsistencia, kpi_atendimento):
    pasta_dados = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'persist'))
    os.makedirs(pasta_dados, exist_ok=True)

    # Salvando pacientes
    df_pacientes = pd.DataFrame([{
        'nome': p.nome,
        'idade': p.idade,
        'localidade': p.localidade,
        'tipo': p.tipo
    } for p in pacientes])
    df_pacientes.to_csv(os.path.join(pasta_dados, f'pacientes.csv'), index=False)

    # Salvando profissionais
    df_profissionais = pd.DataFrame([{
        'nome': pr.nome,
        'horas_semana': pr.horas_semana,
        'faixa_atendimento': pr.faixa_atendimento,
        'localidade': pr.localidade
    } for pr in profissionais])
    df_profissionais.to_csv(os.path.join(pasta_dados, f'profissionais.csv'), index=False)

    # Salvando solução
    df_solucao.to_csv(os.path.join(pasta_dados, f'solucao.csv'), index=False)

    # Salvando inconsistências
    df_inconsistencia.to_csv(os.path.join(pasta_dados, f'inconsistencias.csv'), index=False)

    # Salvando KPI
    if kpi_atendimento is not None:
        kpi_atendimento.to_csv(os.path.join(pasta_dados, f'numSessõesPaciente.csv'), index=False)