from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus

def otimizar_agendamentos(pacientes, profissionais, kpi):
    # Cria o problema de otimização
    prob = LpProblem("Otimização_de_agendamentos", LpMaximize)
    
    # Cria as variáveis de decisão, incluindo a localidade
    x = LpVariable.dicts("x", [(p.nome, pr.nome, data, hora, local) 
                                 for p in pacientes 
                                 for pr in profissionais 
                                 for data in p.disponibilidade.keys() 
                                 for hora in p.disponibilidade[data] 
                                 for local in p.localidade.keys()], 
                          cat='Binary')

    # Função objetivo: maximizar o número de agendamentos priorizando os pacientes com mais sessões anteriores (caso seja fornecido)
    if kpi is not None:
        prob += lpSum([(kpi.get((p.nome, pr.nome), 0)* 2 + 1)* x[(p.nome, pr.nome, data, hora, local)] 
                        for p in pacientes 
                        for pr in profissionais 
                        for data in p.disponibilidade.keys() 
                        for hora in p.disponibilidade[data] 
                        for local in p.localidade.keys()])
    else:
        prob += lpSum([x[(p.nome, pr.nome, data, hora, local)] 
                        for p in pacientes 
                        for pr in profissionais 
                        for data in p.disponibilidade.keys() 
                        for hora in p.disponibilidade[data] 
                        for local in p.localidade.keys()])

    # Restrições
    # Restrição 1: cada paciente só pode ser agendado uma vez
    for p in pacientes:
        prob += lpSum([x[(p.nome, pr.nome, data, hora, local)] 
                        for pr in profissionais 
                        for data in p.disponibilidade.keys() 
                        for hora in p.disponibilidade[data] 
                        for local in p.localidade.keys()]) <= 1

    # Restrição 2: cada profissional não pode exceder o número de horas de trabalho
    for pr in profissionais:
        prob += lpSum([x[(p.nome, pr.nome, data, hora, local)] 
                        for p in pacientes 
                        for data in p.disponibilidade.keys() 
                        for hora in p.disponibilidade[data] 
                        for local in p.localidade.keys()]) <= pr.horas_semana

    # Restrição 3: cada paciente só pode ser agendado em horários disponíveis
    for p in pacientes:
        for data in p.disponibilidade.keys():
            for hora in p.disponibilidade[data]:
                prob += lpSum([x[(p.nome, pr.nome, data, hora, local)] 
                                for pr in profissionais 
                                for local in p.localidade.keys()]) <= 1

    # Restrição 4: cada profissional só pode atender um paciente que se encaixe na faixa de atendimento
    for pr in profissionais:
        for p in pacientes:
            if p.tipo in pr.faixa_atendimento:
                for data in p.disponibilidade.keys():
                    for hora in p.disponibilidade[data]:
                        for local in p.localidade.keys():
                            prob += x[(p.nome, pr.nome, data, hora, local)] <= 1

    # Resolve o problema de otimização
    prob.solve()

    # Verifica quais pacientes não foram agendados
    pacientes_nao_agendados = []
    for p in pacientes:
        agendado = False
        motivos = []
        for pr in profissionais:
            for data in p.disponibilidade.keys():
                for hora in p.disponibilidade[data]:
                    for local in p.localidade.keys():
                        if x[(p.nome, pr.nome, data, hora, local)].varValue == 1:
                            agendado = True
        if not agendado:
            if all([not p.pode_ser_agendado(hora, data) for data in p.disponibilidade.keys() for hora in p.disponibilidade[data]]):
                motivos.append("Fora da disponibilidade do paciente.")
            if all([not pr.pode_atender(data, hora, p.tipo) for data in p.disponibilidade.keys() for hora in p.disponibilidade[data]]):
                motivos.append("Fora da disponibilidade do profissional.")
            pacientes_nao_agendados.append((p.nome, motivos))
            
    # Verifica profissionais não agendados
    profissionais_nao_agendados = []
    for pr in profissionais:
        agendado = False
        for p in pacientes:
            for data in p.disponibilidade.keys():
                for hora in p.disponibilidade[data]:
                    for local in p.localidade.keys():
                        if x[(p.nome, pr.nome, data, hora, local)].varValue == 1:
                            agendado = True
                            break  # Se foi agendado, não precisa continuar verificando este profissional
        if not agendado:
            profissionais_nao_agendados.append(pr.nome)
    
    # Retorna o resultado
    return prob, x, pacientes_nao_agendados, profissionais_nao_agendados
