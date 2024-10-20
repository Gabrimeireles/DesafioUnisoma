import pandas as pd

class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.workbook = pd.ExcelFile(file_path)

    def ler_planilha(self):
        idade_paciente = pd.read_excel(self.workbook, 'IdadePaciente')
        dispon_patiente = pd.read_excel(self.workbook, 'DisponPaciente')
        local_paciente = pd.read_excel(self.workbook, 'LocalPaciente')
        regra_profissional = pd.read_excel(self.workbook, 'RegraProfissional')
        dispon_profissional = pd.read_excel(self.workbook, 'DisponProfissional')
        local_profissional = pd.read_excel(self.workbook, 'LocalProfissional')
        
        if 'numSessõesPaciente' in self.workbook.sheet_names:
            kpi_atendimento = pd.read_excel(self.workbook, 'numSessõesPaciente')
        else:
            kpi_atendimento = None
        
        return idade_paciente, dispon_patiente, local_paciente, regra_profissional, dispon_profissional, local_profissional, kpi_atendimento
    
    def escrever_solucao(self, solucao):
        with pd.ExcelWriter(self.file_path, mode='a', if_sheet_exists='replace') as writer:
            solucao.to_excel(writer, sheet_name='Solução')
            
    def escrever_kpi(self, kpi, sheet_name):
        with pd.ExcelWriter(self.file_path, mode='a', if_sheet_exists='replace') as writer:
            kpi.to_excel(writer, sheet_name=sheet_name)
    
    def escrever_inconsistencia(self, inconsistencia):
        with pd.ExcelWriter(self.file_path, mode='a', if_sheet_exists='replace') as writer:
            inconsistencia.to_excel(writer, sheet_name='Inconsistência')