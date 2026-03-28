# RA1 — Fase 1: Analisador léxico e geração de Assembly (ARMv7 / Cpulator)

## Instituição e disciplina

- **Instituição:** PUCPR — Pontifícia Universidade Católica do Paraná  
- **Disciplina:** Compiladores  
- **Professor:** Frank Alcantara  

## Grupo e integrantes

- **Grupo no Canvas:** 15  
- **Lucas de Oliveira Cunha** — [@lucasdocunha](https://github.com/lucasdocunha)  
- **Tiago de Brito Follador** — [@TiagoFollador](https://github.com/TiagoFollador)

## Descrição

Programa em **Python** que lê um ficheiro de texto com expressões em **notação polonesa reversa (RPN)**, faz a **análise léxica** (autómato finito determinístico com estados em funções) e gera **código Assembly** para o simulador **Cpulator**, alvo **ARMv7 DEC1-SOC (v16.1)**.

## Decisões de projeto

- O **display** mostra **uma casa decimal**.
- Se o valor (em módulo) **ultrapassar 9999.9**, ou ocorrer **divisão por zero**, o valor exibido **satura em 9999.9** (limite do visor).
- Usamos um **epsilon** pequeno no Assembly (`eps_dec`) para o **arredondamento** da primeira decimal ficar estável e não aparecerem artefactos (por exemplo `0.3999…` em vez de `0.4`).


## Como executar

Na raiz do repositório:

```bash
python3 main.py <ficheiro_de_teste.txt>
```

Exemplo:

```bash
python3 main.py teste1.txt
```

## Testes locais (`--test`)

O `main.py` inclui **testes locais** (funções com `assert`, sem dependências extra) que verificam um fluxo mínimo do léxico, da validação de estrutura e da geração de Assembly.

```bash
python3 main.py --test
```

Se tudo correr bem, imprime `testes locais: ok`. Use após alterações no gerador ou no AFD para uma verificação rápida antes de abrir o `saida.txt` no Cpulator.

## Saídas

- **`saida.txt`** — última geração de Assembly (Cpulator).  
- **`tokens.txt`** — tokens da última execução (uma linha por linha do ficheiro de entrada).

## Ficheiros de teste

São fornecidos pelo menos **três** ficheiros de exemplo (`teste1.txt`, `teste2.txt`, `teste3.txt`), cada um com **pelo menos 10 linhas** de expressões, cobrindo operações, comandos especiais e partes inválidas.

## Como testar

1. Executar `python3 main.py --test` para os testes locais rápidos.  
2. Executar `python3 main.py teste1.txt` (e `teste2.txt`, `teste3.txt`) para regenerar `saida.txt` e `tokens.txt`.  
3. Abrir `saida.txt` no **Cpulator** (ARMv7 DEC1-SOC), carregar e simular; conferir o display e o comportamento das expressões.  
4. Conferir `tokens.txt` se o léxico corresponde ao esperado.
