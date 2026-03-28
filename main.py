# Lucas de Oliveira Cunha - lucasdocunha
# Tiago de Brito Follador - TiagoFollador
# Grupo 15  

#TODO: verificar se o led não está ligando errado na última casa decimal
#TODO: tem que fazer a parte das variáveis funcionarem como no teste1 -> agr não tá indo

variaveis = {}
historico_linha = []
MAX_D = 16


def regD(indice: int):
    return f'D{indice % (MAX_D)}'

# salvar/pegar variaveis globais
# atua a nivel de token
def salvarOuPegarVariavel(nome, valor):
    if valor is not None:
        variaveis[nome] = valor
        return ['NUM', valor]

    if nome not in variaveis:
        variaveis[nome] = '0.0'

    return ['NUM', variaveis[nome]]
# atua a nivel de assembly
def atribuirVariavel(nome, variaveis_data: set, data: list, valor_inicial='0.0'):
    if nome not in variaveis_data:
        data.append(f'{nome}: .double {valor_inicial}')
        variaveis_data.add(nome)

def salvarHistorico(resultado):
    historico_linha.append(resultado)

def pegarHistorico(linha):
    if linha < 1 or linha > len(historico_linha):
        return None
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

            try:
                n_val = float(t0[1])
            except ValueError:
                return False

            # inteiro e positivo (N >= 1 abaixo)
            if n_val < 0 or n_val != int(n_val):
                return False

            n_linhas = int(n_val)
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
    

def lerArquivo(nome_arquivo:str):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        print(f"Não foi possível abrir o arquivo {nome_arquivo} - erro: {e}")
        
def salvarArquivo(nome_arquivo:str, conteudo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)


def salvar_tokens_txt(linhas_tokens: list[str]) -> None:
    """Grava só tokens.txt: uma linha por expressão — 'Linha N - …' ou 'Linha N - inválido'."""
    salvarArquivo(
        "tokens.txt",
        "\n".join(linhas_tokens) + ("\n" if linhas_tokens else ""),
    )


def salvar_assembly_txt(conteudo: str) -> None:
    """Grava só o assembly (arquivo separado de tokens.txt)."""
    salvarArquivo("saida.txt", conteudo)
        
def gerarAssembly(expressao):    
    
    codigo_final, data = [], []
    variaveis_data = set()

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
                value = salvarOuPegarVariavel(dados[0][1], None)[1]
                atribuirVariavel(dados[0][1], variaveis_data, data, value)
                codigo_final.append(f'LDR R4, ={dados[0][1]}')
                codigo_final.append(f'VLDR.F64 {regD(n_const)}, [R4]')
                dest = regD(n_const)
                exp_result[exp] = dest
                n_const += 1
                eh_variavel = True

            elif len(dados) == 2:
                if dados[0][0] == 'VAR' and dados[1][0] == 'NUM':
                    salvarOuPegarVariavel(dados[0][1], dados[1][1])
                    atribuirVariavel(dados[0][1], variaveis_data, data, dados[1][1])

                    data, codigo_final, n_const = atribuir_valor(
                        ('NUM', dados[1][1]), n_const, data, codigo_final
                    )
                    dest = regD(n_const-1)
                    codigo_final.append(f'LDR R4, ={dados[0][1]}')
                    codigo_final.append(f'VSTR.F64 {dest}, [R4]')
                    exp_result[exp] = dest
                    eh_variavel = True
                
                elif dados[0][0] == 'NUM' and dados[1][0] == 'VAR':
                    salvarOuPegarVariavel(dados[1][1], dados[0][1])
                    atribuirVariavel(dados[1][1], variaveis_data, data, dados[0][1])

                    data, codigo_final, n_const = atribuir_valor(
                        ('NUM', dados[0][1]), n_const, data, codigo_final
                    )
                    dest = regD(n_const-1)
                    codigo_final.append(f'LDR R4, ={dados[1][1]}')
                    codigo_final.append(f'VSTR.F64 {dest}, [R4]')
                    exp_result[exp] = dest
                    eh_variavel = True

                elif dados[0][0] == 'NUM' and dados[1][0] == 'CE':
                    if dados[1][1] == 'RES':
                        dest = regD(n_const)

                        label_historico = pegarHistorico(linhas)
                        if label_historico is None:
                            codigo_final.append('LDR R4, =fp_zero')
                        else:
                            codigo_final.append(f'LDR R4, ={label_historico}')
                        codigo_final.append(f'VLDR.F64 {dest}, [R4]')
                        
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
                    op1 = regD(n_const-1)
                elif operando_a[0] == 'VAR':
                    value = salvarOuPegarVariavel(operando_a[1], None)[1]
                    atribuirVariavel(operando_a[1], variaveis_data, data, value)
                    codigo_final.append(f'LDR R4, ={operando_a[1]}')
                    codigo_final.append(f'VLDR.F64 {regD(n_const)}, [R4]')
                    op1 = regD(n_const)
                    n_const += 1
                else:
                    #pega o resultado da exp resolvida
                    op1 = exp_result[operando_a[1]]

                if operando_b:
                    if operando_b[0] == 'NUM':
                        data, codigo_final, n_const = atribuir_valor(
                            operando_b, n_const, data, codigo_final
                        )
                        op2 = regD(n_const-1)
                    elif operando_b[0] == 'VAR':
                        value = salvarOuPegarVariavel(operando_b[1], None)[1]
                        atribuirVariavel(operando_b[1], variaveis_data, data, value)
                        codigo_final.append(f'LDR R4, ={operando_b[1]}')
                        codigo_final.append(f'VLDR.F64 {regD(n_const)}, [R4]')
                        op2 = regD(n_const)
                        n_const += 1
                    else:
                        #pega o resultado da exp resolvida
                        op2 = exp_result[operando_b[1]]

                # operação
                if operador[0] == 'OP':
                    dest = regD(n_const)
                    
                    codigo_final.append( #pega exatamente qual é a operação e calcula, retornando a linha 
                        calcular_expressao(operadores[operador[1]], dest, op1, op2, n_const)
                    )

                    exp_result[exp] = dest
                    n_const += 1

        #passo para o registrador final
        print(exp_result.values())
        final_reg = list(exp_result.values())[-1] if len(exp_result) > 0 else ''
        codigo_final.append(f'VMOV R3, R2, {final_reg}')
        codigo_final.append(f'LDR R4, =RES_LINHA_{linhas}')
        codigo_final.append(f'VSTR.F64 {final_reg}, [R4]')
        salvarHistorico(f"RES_LINHA_{linhas}")
        
            
    #passo para o registrador final
    final_reg = list(exp_result.values())[-1]
    codigo_final.append(f'VMOV R3, R2, {final_reg}')
    codigo_final.append(mover_numeros_para_display(final_reg))
    
    
    codigo_final.append("_end:")
    codigo_final.append("B _end")
    final = []
    final.append(digitos_display())
    final.append(".data")
    final.append('fp_zero: .double 0.0')
    final.append('eps_dec: .double 1e-7')
    final.append('dez: .double 10.0')
    final.append('um: .double 1.0')
    final.append('max_disp: .double 9999.9')
    final.extend(data)
    final.append(".text")
    final.extend(codigo_final)
    
    return "\n".join(final)
        
def atribuir_valor(operando, n_const, data, codigo_final):
    data.append(f'const_{n_const}: .double {operando[1]}')
    codigo_final.append(f'LDR R4, =const_{n_const}')
    codigo_final.append(f'VLDR.F64 {regD(n_const)}, [R4]')
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
    
def mover_numeros_para_display(final_d_reg):
    """
    Registradores fixos (GPR): R0–R1 temporários, R2–R3 MMIO, R4 ponteiro (.data),
    R6 máscara sinal, R8 inteiro |x|, R9 1ª decimal, R5 milhar, R10–R12 cent/dez/uni.
    Copia o resultado para D14 e usa D10–D13, D15 só neste bloco.
    Ordem física da placa (esquerda → direita): HEX5 … HEX0 = sinal+milhar | cent | dez | uni | . | dec
    0xFF200020: HEX0..3; 0xFF200030: HEX4..5 (HEX5 = dígito do milhar OR máscara de sinal).
    Se |x| > 9999.9, exibe ±9999.9.
    """
    return f"""
    @ cópia para área fixa do display (D14); literais via R4
    VMOV.F64 D14, {final_d_reg}

    @ se |x| > 9999.9 -> copysign(9999.9, x)
    LDR R4, =fp_zero
    VLDR.F64 D15, [R4]
    MOV R1, #0
    VCMPE.F64 D14, D15
    VMRS APSR_nzcv, FPSCR
    MOVLT R1, #1

    VABS.F64 D13, D14
    LDR R4, =max_disp
    VLDR.F64 D16, [R4]
    VCMPE.F64 D13, D16
    VMRS APSR_nzcv, FPSCR
    BLE disp_apos_clamp

    LDR R4, =max_disp
    VLDR.F64 D14, [R4]
    CMP R1, #0
    BEQ disp_apos_clamp
    VNEG.F64 D14, D14
disp_apos_clamp:

    @ === FPSCR: truncar (round toward zero) ===
    VMRS R0, FPSCR
    BIC  R0, R0, #0x00C00000
    ORR  R0, R0, #0x00C00000
    VMSR FPSCR, R0

    @ sinal (negativo < 0.0), máscara 0x40 = segmento '-'
    LDR R4, =fp_zero
    VLDR.F64 D15, [R4]
    VCMPE.F64 D14, D15
    VMRS APSR_nzcv, FPSCR
    MOV R6, #0
    MOVLT R6, #0x40

    @ parte inteira da magnitude |x| (trunc RZ)
    VABS.F64 D13, D14
    VCVT.S32.F64 S10, D13
    VMOV R8, S10

    @ 1ª decimal: dec = trunc(|x|*10 + eps) - trunc(|x|)*10
    @ (evita frac = |x| - int(|x|), que vira 0.3999... e 10*frac -> 3 em vez de 4)
    LDR R4, =dez
    VLDR.F64 D12, [R4]
    VMUL.F64 D11, D13, D12
    LDR R4, =eps_dec
    VLDR.F64 D15, [R4]
    VADD.F64 D11, D11, D15
    VCVT.S32.F64 S11, D11
    VMOV R9, S11
    MOV R1, #10
    MUL R0, R8, R1
    SUB R9, R9, R0

    @ === FPSCR: volta round to nearest ===
    VMRS R0, FPSCR
    BIC  R0, R0, #0x00C00000
    VMSR FPSCR, R0

    CMP R9, #0
    MOVLT R9, #0
    CMP R9, #9
    MOVGT R9, #9

    MOV R5, #0
    MOV R12, R8

disp_mil_loop:
    CMP R12, #1000
    BLT disp_cent_loop
    SUB R12, R12, #1000
    ADD R5, R5, #1
    B disp_mil_loop

disp_cent_loop:
    MOV R10, #0
disp_cent_sub:
    CMP R12, #100
    BLT disp_dez_loop
    SUB R12, R12, #100
    ADD R10, R10, #1
    B disp_cent_sub

disp_dez_loop:
    MOV R11, #0
disp_dez_sub:
    CMP R12, #10
    BLT disp_seg_digitos
    SUB R12, R12, #10
    ADD R11, R11, #1
    B disp_dez_sub

disp_seg_digitos:
    LDR R4, =digitos

    @ HEX0..3: dec _ uni dez  (direita: 7 _ 6 5 em -456.7)
    LDR R2, =0xFF200020
    MOV R3, #0
    LDR R0, [R4, R9, LSL #2]
    ORR R3, R3, R0
    MOV R1, #0x08
    ORR R3, R3, R1, LSL #8
    LDR R0, [R4, R12, LSL #2]
    ORR R3, R3, R0, LSL #16
    LDR R0, [R4, R11, LSL #2]
    ORR R3, R3, R0, LSL #24
    STR R3, [R2]

    @ HEX4..5: cent | (milhar + sinal em HEX5)
    LDR R2, =0xFF200030
    MOV R3, #0
    LDR R0, [R4, R10, LSL #2]
    ORR R3, R3, R0
    LDR R0, [R4, R5, LSL #2]
    ORR R0, R0, R6
    ORR R3, R3, R0, LSL #8
    STR R3, [R2]
    """
    

if __name__ == ("__main__"):
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", 
        type=str,
    )
    args = parser.parse_args()
    arquivo = args.filename

    linhas = lerArquivo(arquivo)
    if linhas is None:
        sys.exit(1)

    lista_tokens = []
    linhas_tokens = []

    if not linhas:
        linhas_tokens.append("Linha 1 - inválido")

    for idx, linha in enumerate(linhas):
        tokens, erro = parseExpressao(linha)

        print(f"\nLinha {idx+1}: {tokens}")
        if erro:
            print("Linha inválida! (léxico) — ignorada.")
            linhas_tokens.append(f"Linha {idx+1} - inválido")
            continue

        ordem, erro = executarExpressao(tokens, linha_idx=idx)
        if erro:
            print("Linha inválida! (estrutura) — ignorada.")
            linhas_tokens.append(f"Linha {idx+1} - inválido")
            continue

        print(f"Ordem de execução: {ordem}")
        lista_tokens.append(ordem)
        linhas_tokens.append(f"Linha {idx+1} - {tokens}")
    print("\nExpressões processadas:")
    print(lista_tokens)

    salvar_tokens_txt(linhas_tokens)
    if not lista_tokens:
        salvar_assembly_txt("")
    else:
        salvar_assembly_txt(gerarAssembly(lista_tokens))
