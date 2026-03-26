# Lucas de Oliveira Cunha - lucasdocunha
# Tiago de Brito Follador - TiagoFollador
# Grupo 15  

variaveis = {}

# salvar/pegar variaveis globais
def salvarOuPegarVariavel(nome, valor):
    if nome in variaveis:
        return ['NUM', variaveis[nome]]
    else:
        variaveis[nome] = valor
        return ['NUM', valor]

#validadores de formato:
def digito(z):
    if z >= '0' and z <= '9':
        return True
    return False
    
def operacoes(z):
    if z in ['/', '*', '-', '+', '%', "^", "//"]:
        return True
    return False

def parenteses(z):
    if z in ["(", ")"]:
        return True
    return False

#estados:
def estadoNumero(entrada, i):
    numero = ""
    real = False
    erro = False
    
    while i < len(entrada):
        z = entrada[i]
        
        if digito(z):
            numero = numero + z
            
        elif z == ".":
            if real:
                erro = True
            real = True
            
            numero = numero + z
            
        else:
            break
        
        i = i + 1      
    
    #numero não pode ser só ., não pode começar ou terminar com .
    if numero == "." or numero[0] == "." or numero[-1] == ".":
        erro = True
    
    return ('NUM', numero), i, erro 
            
def estadoComandoEspeciais(entrada, i):
    palavra = ""
    erro = False
    while i < len(entrada):
        #pega até não ser mais maiusculo
        if entrada[i].isupper():
            palavra += entrada[i]
            i += 1 
        else: 
            break
    
    #CE -> Comando especial
    #VAR -> Variável
    return (("CE", palavra) if palavra == "RES" else ("VAR", palavra)), i, erro
            
def estadoOperador(entrada, i):
    erro = False
    if operacoes(entrada[i]):
        if operacoes(entrada[i:i+2]):
            return ("OP", entrada[i:i+2]), i+2, erro #verificação do //
        return ("OP", entrada[i]), i + 1, erro

def estadoParenteses(entrada, i):
    p = entrada[i]
    erro = False
    if parenteses(p):
        if p == "(":
            #PI -> parenteses inicial
            return ("PI", p), i + 1, erro
        else:
            #PF -> parenteses final
            return ("PF", p), i + 1, erro
    

def parseExpressao(linha) -> list[str]:
    tokens = []
    i = 0
    erro = False
    while i < len(linha):
        if linha[i] == " " or linha[i] == '\n':
            i = i + 1
            continue
        
        if digito(linha[i]) or linha[i] == ".":
            token, i, erro = estadoNumero(linha, i)
            
        elif operacoes(linha[i]):
            token, i, erro = estadoOperador(linha, i)
            
        elif parenteses(linha[i]):
            token, i, erro = estadoParenteses(linha, i)
            
        elif linha[i].isupper():
            token, i, erro = estadoComandoEspeciais(linha, i)
        
        else:
            erro = True
            
        if erro:
            break
        
        tokens.append(token)
        
    return tokens, erro

def executarExpressao(tokens):

    # Recebe tuplas de tokens e retorna dicioinario em ordem de precedencia

    # precisamos abrir os tokens e inserir eles 
    # em ordem de precedencia(pilha)
    # onde os parenteses tem maior precedencia
    # e precisaomos entrar no mais afundo e retornar ao comeco com as expressoes
    #
    # - precisamos de uma pilha para armazenar a ordem dos tokens
    # - precisamos de uma variavel/contante para definir uma conta
    #   que é resultante da anterior ou concatena com a anterior
    
    pilha = []
    ordem = {}
    ordem_da_expressao = 0
    erro = False

    for token in tokens:
        if token[0] != 'PF':
            pilha.append(token)
        else:
            expressao_atual = []

            # contra pilha vazia
            if not pilha:
                erro = True

            while pilha and pilha[-1][0] != 'PI':
                expressao_atual.append(pilha.pop())

            # contra PI não encontrado
            if not pilha or pilha[-1][0] != 'PI':
                erro = True

            pilha.pop()

            expressao_atual.reverse()

            key = f"EXP{ordem_da_expressao}"
            ordem[key] = expressao_atual
            pilha.append(("EXP", key))
            ordem_da_expressao += 1

    # verifica se num tem parênteses não fechados
    itens_restantes = [t for t in pilha if t[0] == 'PI']
    if itens_restantes:
        erro = True

    return ordem, erro
    

def lerArquivo(arquivo:str):
    try:
        with open(arquivo, 'r') as f:
            return f.readlines()
    except Exception as e:
        print(f"Não foi possível abrir o arquivo {arquivo} - erro: {e}")
        
def gerarAssembly(tokens):    
    
    codigo_final, data = [], []
    codigo_final.append(".global _start")
    codigo_final.append("_start:")
        
    operadores = {
        '+': "VADD.F64",
        '-': "VSUB.F64",
        "*": "VMUL.F64",
        "/": "VDIV.F64",
        '^': "^",
        '%': "%",
        '//': "//"
    }
    
    #dicionário das expressões já resolvidas
    exp_result = {}
    n_const = 0
    for exp, dados in tokens.items():
        eh_variavel = False
        print(f"Gerando código para {exp} com dados {dados}")
        #é uma expressão já resolvida
        if len(dados) == 2:
            if dados[0][0] == 'VAR' and dados[1][0] == 'NUM':
                salvarOuPegarVariavel(dados[0][1], dados[1][1])
                return
            elif dados[0][0] == 'NUM' and dados[1][0] == 'VAR':
                salvarOuPegarVariavel(dados[1][1], dados[0][1])
                return

            else:
                operando_a = dados[0]
                operando_b = None
                operador = dados[1]
        else:
            #expressão não resolvida
            operando_a, operando_b, operador = dados

        if operando_a[0] == 'NUM':
            data, codigo_final, n_const = atribuir_valor(
                operando_a, n_const, data, codigo_final
            )
            op1 = f'D{n_const-1}'
        elif operando_a[0] == 'VAR':
            value = salvarOuPegarVariavel(operando_a[1], None)
            data, codigo_final, n_const = atribuir_valor(
                value, n_const, data, codigo_final
            )
            op1 = f'D{n_const-1}'
        else:
            #pega o resultado da exp resolvida
            op1 = exp_result[operando_a[1]]

        if operando_b:
            if operando_b[0] == 'NUM':
                data, codigo_final, n_const = atribuir_valor(
                    operando_b, n_const, data, codigo_final
                )
                op2 = f'D{n_const-1}'
            elif operando_b[0] == 'VAR':
                value = salvarOuPegarVariavel(operando_b[1], None)
                data, codigo_final, n_const = atribuir_valor(
                    value, n_const, data, codigo_final
                )
                op2 = f'D{n_const-1}'
            else:
                #pega o resultado da exp resolvida
                op2 = exp_result[operando_b[1]]

        # operação
        if operador[0] == 'OP':
            dest = f'D{n_const}'
            
            codigo_final.append( #pega exatamente qual é a operação e calcula, retornando a linha 
                calcular_expressao(operadores[operador[1]], dest, op1, op2, n_const)
            )

            exp_result[exp] = dest
            n_const += 1
            
    #passo para o registrador final
    print(len(list(exp_result.values())))
    print(exp_result)
    final_reg = list(exp_result.values())[-1]
    codigo_final.append(f'VMOV R3, R2, {final_reg}')
    
    codigo_final.append("_end:")
    codigo_final.append("B _end")
    final = []
    final.append(".data")
    final.extend(data)
    final.append(".text")
    final.extend(codigo_final)
    
    return "\n".join(final)
        
def atribuir_valor(operando, n_const, data, codigo_final):
    data.append(f'const_{n_const}: .double {operando[1]}')
    codigo_final.append(f'LDR R{n_const}, =const_{n_const}')
    codigo_final.append(f'VLDR.F64 D{n_const}, [R{n_const}]')
    n_const += 1
    
    return data, codigo_final, n_const
        
def calcular_expressao(operacao, var, v1, v2, n_const):
    
    if operacao == "^":
        return potencia(n_const, v1, v2, var)

    if operacao == "%":
        return resto(v1, v2, var)
    
    if operacao == "//":
        return divisao_inteira(v1, v2, var)

    return f"{operacao} {var}, {v1}, {v2}"
        
        
#TODO: Arrumar aqui -> não está fazendo de fato a potencia 
# preciso que seja para números reais tbm
def potencia(n_const, op1, op2, dest):
    label_loop = f"pow_loop_{n_const}"
    label_end  = f"pow_end_{n_const}"

    return f"""
        VCVT.S32.F64 S0, {op2} 
        VMOV R0, S0

        VMOV.F64 {dest}, =one

        {label_loop}:
        CMP R0, #0
        BEQ {label_end}

        VMUL.F64 {dest}, {dest}, {op1}
        SUB R0, R0, #1
        B {label_loop}

        {label_end}:
    """

def resto(op1, op2, dest):
    return f"""
        VDIV.F64 {dest}, {op1}, {op2}
        VCVT.F32.S64 {dest}, {dest}
        VCVT.F64.S32 {dest}, {dest}
        VMUL.F64 {dest}, {dest}, {op2}
        VSUB.F64 {dest}, {op1}, {dest}
    """

def divisao_inteira(op1, op2, dest):
    return f"""
        VDIV.F64 {dest}, {op1}, {op2}
        VCVT.F32.S64 {dest}, {dest}
        VCVT.F64.S32 {dest}, {dest}
    """
    
def exibirResultados(resultados):
    pass


if __name__ == ("__main__"):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", 
        type=str,
    )
    args = parser.parse_args()
    arquivo = args.filename
    
    linhas = lerArquivo(arquivo)

        
    for idx, linha in enumerate(linhas):
        tokens, erro = parseExpressao(linha)

        print(f"\nLinha {idx+1}: {tokens}")
        if erro:
            print(f"Linha inválida!")
        else:
            ordem, erro = executarExpressao(tokens)
            if erro:
                print(f"Linha inválida!")
            else:
                print(gerarAssembly(ordem))