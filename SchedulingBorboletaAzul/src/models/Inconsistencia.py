import datetime
import pandas as pd

class Inconsistencia:
    def __init__(self, tabela, tipo, mensagem):
        self.tabela = tabela  # 'pacientes', 'profissionais', 'dispoPaciente', 'disponProfissional', 'localPaciente', 'localProfissional'
        self.tipo = tipo  # 'erro' ou 'aviso'
        self.mensagem = mensagem  # mensagem de erro ou aviso
        self.dt_atualizacao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')  # data e hora da atualização

    def to_df(self):
        return pd.DataFrame([self.to_dict()])

    def __str__(self):
        return f'{self.tipo.upper()} - {self.tabela}: {self.mensagem} - {self.dt_atualizacao}'


# Função genérica para verificar inconsistências nas informações básicas
def verificar_informacoes_basicas(nome, valor, tabela, tipo, campo, min_val=None, max_val=None):
    inconsistencias = []
    if pd.isna(nome) or nome == "":
        inconsistencias.append(Inconsistencia(
            tabela=tabela,
            tipo='erro',
            mensagem=f"{tipo.capitalize()} sem nome: {nome}"
        ))
    if pd.isna(valor) or (min_val is not None and valor < min_val) or (max_val is not None and valor > max_val):
        inconsistencias.append(Inconsistencia(
            tabela=tabela,
            tipo='erro',
            mensagem=f"{campo.capitalize()} inválido para {tipo} {nome}: {valor}"
        ))
    return inconsistencias


# Função genérica para verificar disponibilidade
def verificar_disponibilidade(nome, dispon_df, tabela, tipo):
    inconsistencias = []
    disponibilidade = dispon_df[dispon_df[tipo] == nome]
    if disponibilidade.empty:
        inconsistencias.append(Inconsistencia(
            tabela=tabela,
            tipo='aviso',
            mensagem=f"{tipo.capitalize()} {nome} não possui disponibilidade cadastrada."
        ))
    return inconsistencias


# Função genérica para verificar localidade
def verificar_localidade(index, local_df, tabela, nome, tipo):
    inconsistencias = []
    localidade = local_df.loc[index, :]
    if localidade.isnull().all():
        inconsistencias.append(Inconsistencia(
            tabela=tabela,
            tipo='aviso',
            mensagem=f"{tipo.capitalize()} {nome} não possui localidade cadastrada."
        ))
    return inconsistencias


def verificar_inconsistencias_pacientes(pacientes_df, dispon_paciente_df, local_paciente_df):
    """Verifica inconsistências nos dados de pacientes."""
    inconsistencias = []

    for index, row in pacientes_df.iterrows():
        nome = row['paciente']
        idade = row['idade']

        # Verificar informações básicas (nome e idade)
        inconsistencias += verificar_informacoes_basicas(
            nome, idade, tabela='pacientes', tipo='paciente', campo='idade', min_val=0, max_val=120
        )

        # Verificar disponibilidade do paciente
        inconsistencias += verificar_disponibilidade(
            nome, dispon_paciente_df, tabela='dispon_paciente', tipo='paciente'
        )

        # Verificar localidade do paciente
        inconsistencias += verificar_localidade(
            index, local_paciente_df, tabela='local_paciente', nome=nome, tipo='paciente'
        )

    return inconsistencias


def verificar_inconsistencias_profissionais(profissionais_df, dispon_profissional_df, local_profissional_df):
    """Verifica inconsistências nos dados de profissionais."""
    inconsistencias = []

    for index, row in profissionais_df.iterrows():
        nome = row['profissional']
        horas_semana = row['horas_semana']

        # Verificar informações básicas (nome e horas semanais)
        inconsistencias += verificar_informacoes_basicas(
            nome, horas_semana, tabela='profissionais', tipo='profissional', campo='horas semanais', min_val=1, max_val=60
        )

        # Verificar disponibilidade do profissional
        inconsistencias += verificar_disponibilidade(
            nome, dispon_profissional_df, tabela='dispon_profissional', tipo='profissional'
        )

        # Verificar localidade do profissional
        inconsistencias += verificar_localidade(
            index, local_profissional_df, tabela='local_profissional', nome=nome, tipo='profissional'
        )

    return inconsistencias

def verificar_inconsistencias_nao_agendamento(pacientes_nao_agendado, profissionais_nao_agendado):
    inconsistencias = []
    if len(pacientes_nao_agendado) > 0:
        for paciente in pacientes_nao_agendado:
            inconsistencias.append(Inconsistencia(
                tabela='Solução',
                tipo='aviso',
                mensagem=f"Paciente {paciente} não foi agendado."
            ))
    if len(profissionais_nao_agendado) > 0:
        for profissional in profissionais_nao_agendado:
            inconsistencias.append(Inconsistencia(
                tabela='Solução',
                tipo='aviso',
                mensagem=f"Profissional {profissional} não foi agendado."
            ))
    return inconsistencias
