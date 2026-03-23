## 26.7.1 Aluno 1: Função parseExpressao e Analisador Léxico com Autômato Finito Determinístico

**Responsabilidades:** Criar e administrar o repositório no GitHub. Além disso:

* Implementar `parseExpressao(std::string linha, std::vector<std::string>& _tokens_)` (ou equivalente em Python/C) para analisar uma linha de expressão RPN e extrair tokens.
* Implementar o analisador léxico usando Autômatos Finitos Determinísticos (AFDs), com cada estado como uma função (ex.: `estadoNumero`, `estadoOperador`, `estadoParenteses`).
* Validar tokens:
    * Números reais (ex.: 3.14) usando ponto como separador decimal;
    * Operadores (`+`, `-`, `*`, `/`, `%`, `^`);
    * Comandos especiais (`RES`, `MEM`) e parênteses;
* Detectar erros como números malformados (ex.: 3.14.5) ou tokens inválidos;
* Criar funções de teste para o analisador léxico, cobrindo entradas válidas e inválidas.

**Tarefas Específicas:**
* Escrever `parseExpressao` para dividir a linha em tokens usando um Autômato Finito Determinístico.

**Interface:**
* Recebe uma linha de texto e retorna um vetor de tokens;
* Fornece tokens válidos para `executarExpressao`.

> **Warning:** A palavra parser usada neste texto deve ser interpretada em seu sentido mais amplo: percorrer, varrer, um texto ou uma coleção de dados. Neste caso, refere-se o processo de análise léxica. O uso de expressões regulares, ou das bibliotecas de expressões regulares disponíveis em Python, C ou C++, para a implementação do analisador léxico, é proibido e resultará no zeramento do trabalho.

---

## 26.7.2 Aluno 2: Função executarExpressao e Gerenciamento de Memória

**Responsabilidades:**

* Testar o Autômato Finito Determinístico com entradas diversificadas `(3.14 2.0 +)`, `(5 RES)`, `(3.14.5 2.0 +)` (inválido). Use esta função para validar o código Assembly que será gerado posteriormente. Lembre-se você não está fazendo um compilador completo, mas sim um gerador de código Assembly a partir do vetor de tokens gerado pelo analisador léxico. O código Assembly deve ser funcional e compatível com a arquitetura ARMv7 DEC1-SOC(v16.1) para que o resultado do programa seja obtido pelo cálculo realizado no Cpulator-ARMv7 DEC1-SOC(v16.1). E, como você irá criar os arquivos de teste, não teremos nenhum erro sintático, ou semântico nestes arquivos.
* Criar um método para lidar com parênteses aninhados para geração das expressões em Assembly.
* Implementar `executarExpressao(...)` usando uma estrutura de dicionário/mapa para gerenciar múltiplas variáveis na memória.
* Gerenciar a memória MEM para comandos `(V MEM)` e `(MEM)`.
* Manter um histórico de resultados para suportar `(N RES)`.
* Criar funções de teste para validar a execução de expressões e comandos especiais.

**Tarefas Específicas:**
* Usar uma pilha para avaliar expressões RPN (ex.: em C++: `std::stack<float>`);
* Implementar operações (`+`, `-`, `*`, `/`, `//`, `%`, `^`) com precisão de 64 bits (IEEE 754);
* Tratar divisão inteira e resto separadamente.

**Interface:**
* Recebe tokens de `parseExpressao` e atualiza resultados e memoria;
* Fornece resultados para `exibirResultados` e Assembly.

---

## 26.7.3 Aluno 3: Função gerarAssembly e Leitura de Arquivo

**Responsabilidades:**

* Testar com expressões como `(3.14 2.0 +)`, `((1.5 2.0 *) (3.0 4.0 *) /)`, `(5.0 MEM)`, `(2 RES)`.
* Implementar `gerarAssembly(const std::vector<std::string>& _tokens_, std::string& codigoAssembly)` para gerar o código Assembly.
* Implementar `lerArquivo(std::string nomeArquivo, std::vector<std::string>& linhas)` para ler o arquivo de entrada.
* Criar funções de teste para validar a leitura de arquivos e a geração de Assembly. Lembre-se o Assembly deve conter todas as operações do texto de teste.

**Tarefas Específicas:**
* A função `gerarAssembly` deve receber o vetor de tokens gerado pelo analisador léxico e traduzi-lo para Assembly ARMv7.
* Gerar Assembly ARMv7 para operações RPN e comandos especiais;
* Testar com arquivos contendo 10 linhas, ou mais, incluindo expressões aninhadas e comandos especiais;
* Verificar erros de abertura de arquivo e exibir mensagens claras.

**Interface:**
* `lerArquivo` fornece linhas para `parseExpressao`;
* `gerarAssembly` produz código Assembly.

---

## 26.7.4 Aluno 4: Função exibirResultados, Interface do Usuário e Testes

**Responsabilidades:**

* Implementar `exibirResultados(const std::vector<float>& resultados)` para exibir os resultados das expressões.
* Implementar e gerenciar a interface no `main`, incluindo leitura do argumento de linha de comando.
* Corrigir problemas de entrada (ex.: em C++: `std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n')`).
* Criar funções de teste para validar a saída e o comportamento do programa completo.

**Tarefas Específicas:**
* Exibir resultados com formato claro (ex.: uma casa decimal para números reais);
* Implementar o `main` para chamar `lerArquivo`, `parseExpressao`, `executarExpressao`, e `exibirResultados`;
* Testar com arquivos de teste fornecidos, verificando saídas para expressões simples e complexas;
* Testar o FSM com comandos especiais como `(V MEM)` e `(MEM)`.

**Interface:**
* Usa resultados de `executarExpressao` para exibir saídas;
* Gerencia a execução do programa via argumento de linha de comando.