# Lucas de Oliveira Cunha - lucasdocunha
# Tiago de Brito Follador - TiagoFollador
# Grupo 15  

#TODO: fazer a parte dos testes -> principalmente da 2
#TODO: verificar se o led não está ligando errado na última casa decimal
#TODO: tem que fazer a parte das variáveis funcionarem como no teste1 -> agr não tá indo

variaveis = {}
historico_linha = []
# salvar/pegar variaveis globais
def salvarOuPegarVariavel(nome, valor):
    if nome in variaveis:
        return ['NUM', variaveis[nome]]
    else:
        variaveis[nome] = valor
        return ['NUM', valor]
    
def salvarHistorico(resultado):
    historico_linha.append(resultado)

def pegarHistorico(linha):
    return historico_linha[len(historico_linha) - linha]


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


def valida_operando(t):
    """Operando válido em subexpressão binária: número, memória ou subexpressão já fechada."""
    return t[0] in ("NUM", "VAR", "EXP")


def validarSubexpressao(expr, linha_idx):
    """
    Valida um bloco entre parênteses (já em ordem RPN interna).
    - (MEM): um token VAR
    - (V MEM): NUM + VAR
    - (N RES): NUM (inteiro N >= 0) + CE RES; exige linha alvo existente (N linhas acima)
    - (A B op): três tokens, último OP
    """

    #para quando a lista estiver vazia
    if not expr:
        return False

    
    n = len(expr)
    if n == 1:
        return expr[0][0] == "VAR"
    if n == 2:
        t0, t1 = expr[0], expr[1]

        #valido se é RES
        if t1[0] == "CE" and t1[1] == "RES":
            #o primeiro token deve ser um número
            if t0[0] != "NUM":
                return False

            #valido se o número é inteiro e positivo
            if t0[1] < 0 or t0[1] != int(t0[1]):
                return False

            
            n_linhas = int(t0[1])
            # resultado da expressão N linhas anteriores: precisa haver linha alvo
            if n_linhas < 1:
                return False

            #valido se a linha alvo existe
            alvo = linha_idx - n_linhas
            return alvo >= 0

        #valido se é um número e uma variável
        if t0[0] == "NUM" and t1[0] == "VAR":
            return True

        return False

    #se for uma operação, tem que ter 3
    if n == 3:
        if expr[2][0] != "OP":
            return False
        return valida_operando(expr[0]) and valida_operando(expr[1])
    return False


def executarExpressao(tokens, linha_idx=0):
    """
    Agrupa tokens por parênteses e valida formato (RPN / comandos especiais).
    linha_idx: índice 0-based da linha no arquivo (para validar (N RES)).
    """
    pilha = []
    ordem = {}
    ordem_da_expressao = 0
    erro = False

    for token in tokens:
        if token[0] != "PF":
            pilha.append(token)
        else:
            expressao_atual = []
            if not pilha:
                erro = True
            else:
                while pilha and pilha[-1][0] != "PI":
                    expressao_atual.append(pilha.pop())
                if not pilha or pilha[-1][0] != "PI":
                    erro = True
                else:
                    pilha.pop()
                    expressao_atual.reverse()
                    if not validarSubexpressao(expressao_atual, linha_idx):
                        erro = True
                    key = f"EXP{ordem_da_expressao}"
                    ordem[key] = expressao_atual
                    pilha.append(("EXP", key))
                    ordem_da_expressao += 1

    if any(t[0] == "PI" for t in pilha):
        erro = True
    if len(pilha) != 1 or pilha[0][0] != "EXP":
        erro = True

    return ordem, erro
    

def lerArquivo(arquivo:str):
    try:
        with open(arquivo, 'r') as f:
            return f.readlines()
    except Exception as e:
        print(f"Não foi possível abrir o arquivo {arquivo} - erro: {e}")
        
def salvarArquivo(arquivo:str, conteudo):
    with open(arquivo, 'w') as f:
        f.write(conteudo)
        
def gerarAssembly(expressao):    
    
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
    n_const = 0
    linhas = 0
    for tokens in expressao:
        #dicionário das expressões já resolvidas
        linhas += 1
        exp_result = {}
        codigo_final.append(f"RES_LINHA_{linhas}: .double 0.0")

        for exp, dados in tokens.items():
            print(exp, dados)
            #é uma expressão já resolvida
            eh_variavel = False

            if len(dados) == 1 and dados[0][0] == 'VAR':
                exp_result[exp] = dest
                eh_variavel = True

            elif len(dados) == 2:
                if dados[0][0] == 'VAR' and dados[1][0] == 'NUM':
                    salvarOuPegarVariavel(dados[0][1], dados[1][1])
                    eh_variavel = True
                
                elif dados[0][0] == 'NUM' and dados[1][0] == 'VAR':
                    salvarOuPegarVariavel(dados[1][1], dados[0][1])
                    eh_variavel = True

                elif dados[0][0] == 'NUM' and dados[1][0] == 'CE':
                    if dados[1][1] == 'RES':
                        dest = f'D{n_const}'

                        codigo_final.append(f'LDR R0, ={pegarHistorico(linhas)}')
                        codigo_final.append(f'VLDR.F64 {dest}, [R0]')
                        
                        eh_variavel = True
                        exp_result[exp] = dest
                        n_const += 1
                else:
                    operando_a = dados[0]
                    operando_b = None
                    operador = dados[1]
            else:
                #expressão não resolvida
                # print(dados)
                operando_a, operando_b, operador = dados
            
            if not eh_variavel:
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
        print(exp_result.values())
        final_reg = list(exp_result.values())[-1] if len(exp_result) > 0 else ''
        codigo_final.append(f'VMOV R3, R2, {final_reg}')
        codigo_final.append(f'LDR R0, =RES_LINHA_{linhas}')
        codigo_final.append(f'VSTR.F64 {final_reg}, [R0]')
        salvarHistorico(f"RES_LINHA_{linhas}")
        
            
    #passo para o registrador final
    final_reg = list(exp_result.values())[-1]
    codigo_final.append(f'VMOV R3, R2, {final_reg}')
    codigo_final.append(mover_numeros_para_display(n_const, final_reg))
    
    
    codigo_final.append("_end:")
    codigo_final.append("B _end")
    final = []
    final.append(digitos_display())
    final.append(".data")
    final.append('dez: .double 10.0')
    final.append('um: .double 1.0')
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
        
        
def potencia(n_const, op1, op2, dest):
    label_loop = f"pow_loop_{n_const}"
    label_end  = f"pow_end_{n_const}"

    return f"""
        VCVT.S32.F64 S0, {op2} 
        VMOV R0, S0

        LDR R1, =um
        VLDR.F64 {dest}, [R1]

        CMP R0, #0
        BLE {label_end}

        {label_loop}:
        VMUL.F64 {dest}, {dest}, {op1}
        SUB R0, R0, #1
        CMP R0, #0
        BGT {label_loop}

        {label_end}:
    """

def resto(op1, op2, dest):
    return f"""
        @ quociente em double
        VDIV.F64 D10, {op1}, {op2}

        @ parte inteira do quociente
        VCVT.S32.F64 S10, D10

        @ volta pra double
        VCVT.F64.S32 D11, S10

        @ multiplica pelo divisor
        VMUL.F64 D11, D11, {op2}

        @ resto = op1 - (quociente * op2)
        VSUB.F64 {dest}, {op1}, D11
    """

def divisao_inteira(op1, op2, dest):
    return f"""
        VDIV.F64 {dest}, {op1}, {op2}
        VCVT.S32.F64 S0, {dest}
        VCVT.F64.S32 {dest}, S0
    """
    
def exibirResultados(resultados):
    pass

def digitos_display():
    return"""digitos:
    .word 0x3F @ 0
    .word 0x06 @ 1
    .word 0x5B @ 2
    .word 0x4F @ 3
    .word 0x66 @ 4
    .word 0x6D @ 5
    .word 0x7D @ 6
    .word 0x07 @ 7
    .word 0x7F @ 8
    .word 0x6F @ 9
    """
    
#TODO: deixar o código truncar ao invés de ele arredondar -> Não consegui fazer
def mover_numeros_para_display(n_const, d_reg):
    return f"""
    @ === Seta FPSCR para truncar (Round toward Zero) ===
    VMRS R0, FPSCR
    BIC  R0, R0, #0x00C00000    @ limpa bits [23:22]
    ORR  R0, R0, #0x00C00000    @ seta RZ = 11 (truncar)
    VMSR FPSCR, R0

    @ =========================
    @ inteiro (agora trunca)
    @ =========================
    VCVT.S32.F64 S10, {d_reg}
    VMOV R{n_const}, S10

    @ =========================
    @ decimal (agora trunca)
    @ =========================
    VCVT.F64.S32 D10, S10
    VSUB.F64 D11, {d_reg}, D10

    LDR R0, =dez
    VLDR.F64 D12, [R0]
    VMUL.F64 D11, D11, D12

    VCVT.S32.F64 S11, D11       @ trunca a 1ª casa decimal
    VMOV R{n_const+1}, S11

    @ === Restaura FPSCR para Round to Nearest ===
    VMRS R0, FPSCR
    BIC  R0, R0, #0x00C00000    @ limpa bits [23:22] → volta a 00 (RN)
    VMSR FPSCR, R0

    CMP R{n_const+1}, #0
    BGE check_max
    MOV R{n_const+1}, #0

    check_max:
    CMP R{n_const+1}, #9
    BLE ok_decimal
    MOV R{n_const+1}, #9

    ok_decimal:

    @ =========================
    @ separar dígitos
    @ =========================
    MOV R{n_const+2}, #0
    MOV R{n_const+3}, #0
    MOV R{n_const+4}, R{n_const}

cent_loop:
    CMP R{n_const+4}, #100
    BLT dez_loop
    SUB R{n_const+4}, R{n_const+4}, #100
    ADD R{n_const+2}, R{n_const+2}, #1
    B cent_loop

dez_loop:
    CMP R{n_const+4}, #10
    BLT final_digitos
    SUB R{n_const+4}, R{n_const+4}, #10
    ADD R{n_const+3}, R{n_const+3}, #1
    B dez_loop

final_digitos:
    LDR R{n_const+5}, =digitos

    LDR R{n_const+6}, [R{n_const+5}, R{n_const+2}, LSL #2]
    LDR R{n_const+7}, [R{n_const+5}, R{n_const+3}, LSL #2]
    LDR R{n_const+8}, [R{n_const+5}, R{n_const+4}, LSL #2]
    LDR R{n_const+9}, [R{n_const+5}, R{n_const+1}, LSL #2]

    LDR R2, =0xFF200020
    MOV R3, #0

    ORR R3, R3, R{n_const+9}          @ HEX0 (decimal)
    MOV R1, #0x08
    ORR R3, R3, R1, LSL #8            @ HEX1 ("_")
    ORR R3, R3, R{n_const+8}, LSL #16 @ HEX2 (unidades)
    ORR R3, R3, R{n_const+7}, LSL #24 @ HEX3 (dezenas)

    STR R3, [R2]

    LDR R2, =0xFF200030
    MOV R3, #0
    ORR R3, R3, R{n_const+6}          @ HEX4 (centenas)

    STR R3, [R2]
    """
    

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

    wagner = []
        
    for idx, linha in enumerate(linhas):
        tokens, erro = parseExpressao(linha)

        print(f"\nLinha {idx+1}: {tokens}")
        if erro:
            print(f"Linha inválida!")
        else:
            ordem, erro = executarExpressao(tokens, linha_idx=idx)
            if erro:
                print(f"Linha inválida!")
            else:
                print(f"Ordem de execução: {ordem}")
                wagner.append(ordem)
    print("\nExpressões processadas:")
    print(wagner)
    salvarArquivo('saida.txt', gerarAssembly(wagner))
