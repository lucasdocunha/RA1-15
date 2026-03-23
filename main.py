## Lucas de Oliveira Cunha - lucasdocunha
## Tiago de Brito Follador - TiagoFollador
## Grupo 15  



##validadores de formato:

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
    
    while i < len(entrada):
        z = entrada[i]
        
        if digito(z):
            numero = numero + z
            
        elif z == ".":
            if real:
                raise Exception("Erro: Número está mal formatado!")
            real = True
            numero = numero + z
            
        else:
            break
        
        i = i + 1      
        
    if numero == "." or numero[0] == "." or numero[-1] == ".":
        raise Exception("Erro: Número está mal formatado!")
    
    return ('NUM', numero), i
            
def estadoComandoEspeciais(entrada, i):
    try:
        palavra = entrada[i:i+3]
    except:
        raise Exception("ERRO: Não é um comando especial!")
    
    if palavra in ['RES', 'MEM']:
        return (palavra), i + 3
    else:
        raise Exception("ERRO: Não é um comando especial válido")
            
def estadoOperador(entrada, i):
    if operacoes(entrada[i]):
        if entrada[i+1] == "/":
            return ("OP", entrada[i:i+2]), i+2
        return ("OP", entrada[i]), i + 1

def estadoParenteses(entrada, i):
    p = entrada[i]
    if parenteses(p):
        if p == ")":
            #PI -> parenteses inicial
            return ("PI", p), i + 1
        else:
            #PF -> parenteses final
            return ("PF", p), i + 1

def parseExpressao(linha) -> list[str]:
    
    tokens = []
    i = 0
    while i < len(linha):
        
        if linha[i] == " ":
            i = i + 1
            continue
        
        if digito(linha[i]) or linha[i] == ".":
            token, i = estadoNumero(linha, i)
            
        elif operacoes(linha[i]):
            token, i = estadoOperador(linha, i)
            
        elif parenteses(linha[i]):
            token, i = estadoParenteses(linha, i)
            
        elif linha[i] in ['R', 'M']:
            token, i = estadoComandoEspeciais(linha, i)
            
        else:
            raise Exception("ERRO: Caractere inválido")
        
        tokens.append(token)
        
    return tokens



if __name__ == ("__main__"):
    import argparse
    parser = argparse.ArgumentParser(description="A script that processes a single file argument.")

    parser.add_argument(
        "filename", 
        type=str,
    )

    args = parser.parse_args()
    
    arquivo = args.filename

    with open(arquivo, 'r') as f:
        linhas = f.readlines()
        
    for linha in linhas:
        tokens = parseExpressao(linha)
        print(tokens)