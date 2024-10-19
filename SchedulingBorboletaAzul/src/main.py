from models.agendamento import Agendamento
from services.Optimizer import otimizar_agendamentos
from utils.helpers import agendamento_to_df, traduzir_pacientes, traduzir_profissional
from services.ExcelHandler import ExcelHandler
from pulp import LpStatus


def main():
    excel_handler = ExcelHandler('../data/cenario_4.xlsx')
    idade_paciente, dispon_patiente, local_paciente, regra_profissional, dispon_profissional, local_profissional, kpi_atendimento = excel_handler.ler_planilha()
    
    pacientes = traduzir_pacientes(idade_paciente, dispon_patiente, local_paciente)
    profissionais = traduzir_profissional(regra_profissional, dispon_profissional, local_profissional)
    
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