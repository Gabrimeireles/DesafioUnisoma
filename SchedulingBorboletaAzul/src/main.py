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
    parser = argparse.ArgumentParser(description="Ferramenta de Agendamento Psicológico")
    parser.add_argument('--file', type=str, help="Caminho para o arquivo Excel")
    parser.add_argument('--mode', type=str, default="terminal", help="Modo de execução: terminal ou streamlit")

    args = parser.parse_args()
    print(args)

    if args.mode == "terminal":
        dashboard() # Executa o dashboard do Streamlit
        if args.file:
            executar_terminal(args.file)
        else:
            print("Por favor, forneça o caminho para o arquivo Excel usando o argumento --file.")


if __name__ == '__main__':
    main()
