import streamlit as st
import os

from utils.helpers import agendamento_to_df, processar_agendamentos

def listar_arquivos(diretorio):
    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.xlsx')]
    return arquivos

def mostrar_agendamentos(agendamentos):
    df_agendamentos = agendamento_to_df(agendamentos)
    st.dataframe(df_agendamentos)
 
def dashboard():   
    st.title('Dashboard do Gerenciador de Agendamentos dos Atendimentos')

    pasta_dados = '../data'
    arquivos = listar_arquivos(pasta_dados)
    arquivo_selecionado = st.selectbox('Selecione o arquivo de dados', arquivos)

    if st.button('Executar Otimização dos Agendamentos'):
        if arquivo_selecionado:
            st.write('Executando otimização dos agendamentos...')
            st.write('Arquivo selecionado:', arquivo_selecionado)
            
            caminho_arquivo = os.path.join(pasta_dados, arquivo_selecionado)
            resultado = processar_agendamentos(caminho_arquivo)
            
            if resultado['status'] == 'erro':
                inconsistencias = resultado['inconsistencias']
                st.error(f'Erros encontrados na planilha! Número total de erros: {len(inconsistencias)}')
                for i, inconsistencia in enumerate(inconsistencias, start=1):
                    st.error(f"{i}. Tabela: {inconsistencia.tabela} | Tipo: {inconsistencia.tipo.upper()} | Mensagem: {inconsistencia.mensagem}")
                    
            else:
                agendamentos = resultado['agendamentos']
                nao_agendados = resultado['inconsistencias']
                st.success('Otimização dos agendamentos realizada com sucesso!')
                
                st.subheader('Agendamentos realizados:')
                mostrar_agendamentos(agendamentos)
                
                if nao_agendados:
                    for i, nao_agendados in enumerate(nao_agendados, start=1):
                        st.warning(f"{i}. Tabela: {nao_agendados.tabela} | {nao_agendados.tipo.upper()} | Mensagem: {nao_agendados.mensagem}")
        else:
            st.error('Selecione um arquivo para executar a otimização dos agendamentos.')