from models.Inconsistencia import verificar_inconsistencias_pacientes, verificar_inconsistencias_profissionais
from models.agendamento import Agendamento
from services.Optimizer import otimizar_agendamentos
from utils.helpers import agendamento_to_df, traduzir_pacientes, traduzir_profissionais, inconsistencias_to_df
from services.ExcelHandler import ExcelHandler
from pulp import LpStatus


def main():
    excel_handler = ExcelHandler('../data/cenario_4.xlsx')
    idade_paciente, dispon_patiente, local_paciente, regra_profissional, dispon_profissional, local_profissional, kpi_atendimento = excel_handler.ler_planilha()
    
    inconsistencias = verificar_inconsistencias_pacientes(idade_paciente, dispon_patiente, local_paciente)
    inconsistencias += verificar_inconsistencias_profissionais(regra_profissional, dispon_profissional, local_profissional)
    
    df_inconsistencia = inconsistencias_to_df(inconsistencias)
    excel_handler.escrever_inconsistencia(df_inconsistencia)
    
    if any(inc.tipo == 'erro' for inc in inconsistencias):
        print('************************************')
        print('Erros encontrados na planilha!')
        print(f'Arquivo: {excel_handler.file_path}')
        print(f'Número total de erros: {len(inconsistencias)}')
        print('\nDetalhes dos erros encontrados:')
        for i, inconsistencia in enumerate(inconsistencias, start=1):
            print(f"{i}. Tabela: {inconsistencia.tabela} | Tipo: {inconsistencia.tipo.upper()} | Mensagem: {inconsistencia.mensagem}")
        return
        
    pacientes = traduzir_pacientes(idade_paciente, dispon_patiente, local_paciente)
    profissionais = traduzir_profissionais(regra_profissional, dispon_profissional, local_profissional)
    
    prob, x, pacientes_nao_agendados = otimizar_agendamentos(pacientes, profissionais)
    
    agendamentos = []            
    for var in prob.variables():
        if var.varValue == 1:
            for chave, var_x in x.items():
                if var.name == var_x.name:
                    paciente, profissional, data, hora, local = chave
                    agendamentos.append(Agendamento(paciente, profissional, data, hora, local))

    df_solução = agendamento_to_df(agendamentos)
    excel_handler.escrever_solucao(df_solução)
                    
    print('************************************')
    print('Pacientes não agendados:')
    for paciente in pacientes_nao_agendados:
        print(paciente)
    print('************************************')
    
        
if __name__ == '__main__':
    main()