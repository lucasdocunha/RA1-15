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


if __name__ == ("__main__"):
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filename", 
        type=str,
    )

    args = parser.parse_args()
    
    arquivo = args.filename

    with open(arquivo, 'r') as f:
        linhas = f.readlines()
        
    for linha in linhas:
        tokens, erro = parseExpressao(linha)
        if erro:
            print("Linha inválida!")
        else:
            print(tokens)