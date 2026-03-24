# Lucas de Oliveira Cunha - lucasdocunha
# Tiago de Brito Follador - TiagoFollador
# Grupo 15  

#validadores de formato:
def digito(z):
    if z >= '0' and z <= '9':
        return True
    return False
    
def operacoes(z):
    if z in ['/', '*', '-', '+', '%', "^"]:
        return True
    return False

def parenteses(z):
    if z in ["(", ")"]:
        return True
    return False

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
        
    if numero == "." or numero[0] == "." or numero[-1] == ".":
        erro = True
    
    return ('NUM', numero), i, erro 
            
def estadoComandoEspeciais(entrada, i):
    palavra = ""
    erro = False
    while i < len(entrada):
        if entrada[i].isupper():
            palavra += entrada[i]
            i += 1 
        else: 
            erro = True
            break
    
    return ("CE", palavra), i + 3, erro
            
def estadoOperador(entrada, i):
    erro = False
    if operacoes(entrada[i]):
        if entrada[i+1] == "/":
            return ("OP", entrada[i:i+2]), i+2, erro
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
        #print(linha[i])
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
    with open(arquivo, 'r') as f:
        return f.readlines()
    
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

        print(f"Linha {idx}: {tokens}")
        if erro:
            print(f"Linha inválida!")
        else:
            ordem, erro = executarExpressao(tokens)
            if erro:
                print(f"Linha inválida!")
            else:
                for key, value in ordem.items():
                    print(f"{key}: {value}")
        print("================================================================\n")