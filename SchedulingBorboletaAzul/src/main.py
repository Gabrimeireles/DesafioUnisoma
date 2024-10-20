import argparse
from utils.helpers import processar_agendamentos
from view.dashboard import dashboard

def executar_terminal(file_path):
    resultado = processar_agendamentos(file_path)
    
    if resultado['status'] == 'erro':
        inconsistencias = resultado['inconsistencias']
        print('************************************')
        print('Erros encontrados na planilha!')
        print(f'Arquivo: {file_path}')
        print(f'Número total de erros: {len(inconsistencias)}')
        print('\nDetalhes dos erros encontrados:')
        for i, inconsistencia in enumerate(inconsistencias, start=1):
            print(f"{i}. Tabela: {inconsistencia.tabela} | Tipo: {inconsistencia.tipo.upper()} | Mensagem: {inconsistencia.mensagem}")
        print('Execução interrompida.')
        return
    else:
        agendamentos = resultado['agendamentos']
        pacientes_nao_agendados = resultado['pacientes_nao_agendados']
        
        print('************************************')
        print('Pacientes Agendados:')
        for paciente in agendamentos:
            print(paciente)
        print('************************************')
        print('Execução concluída com sucesso.')
        
        print('************************************')
        print('Pacientes não agendados:')
        for paciente in pacientes_nao_agendados:
            print(paciente)
        print('************************************')
        print('Execução concluída com sucesso.')


def main():
    dashboard() # Executa o dashboard do Streamlit


if __name__ == '__main__':
    main()
