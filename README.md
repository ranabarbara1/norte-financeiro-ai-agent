# Norte Financeiro

Protótipo funcional de um assistente financeiro criado para ajudar um cliente fictício a acompanhar metas, entender gastos e avaliar opções financeiras compatíveis com seu perfil.

O projeto usa dados simulados para demonstrar como uma aplicação pode oferecer orientações claras, seguras e contextualizadas. Ele não realiza movimentações financeiras reais.

---

## Objetivo do Projeto

O **Norte Financeiro** ajuda o cliente a:

- acompanhar a evolução da reserva de emergência;
- entender entradas, saídas e principais categorias de gasto;
- identificar gastos recorrentes e gastos que podem ser revistos;
- consultar metas financeiras cadastradas;
- avaliar produtos financeiros disponíveis no projeto;
- receber orientações compatíveis com seu perfil e sua tolerância a risco.

O foco do projeto é demonstrar uma solução simples, segura e explicável para apoiar a organização financeira pessoal.

---

## Cliente Fictício

O cliente usado no projeto é **João Silva**.

Principais dados do perfil:

- idade: 32 anos;
- profissão: Analista de Sistemas;
- renda mensal: R$ 5.000,00;
- perfil de investidor: moderado;
- tolerância a risco: não aceita risco;
- objetivo principal: construir reserva de emergência;
- reserva atual: R$ 10.000,00;
- meta da reserva: R$ 15.000,00;
- prazo da reserva: junho de 2026.

Com base nesses dados, o assistente responde perguntas como:

```text
Quanto falta para completar minha reserva?
Onde posso deixar o dinheiro da reserva?
Qual é meu perfil de investidor?
Como posso guardar mais dinheiro?
```

---

## Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Python Dotenv
- Requests
- OpenAI SDK
- Ollama, opcional, para uso com modelo local

---

## Estrutura do Projeto

```text
norte-financeiro-ai-agent/
├── assets/
│   ├── favicon.png
│   └── logo.png
│
├── data/
│   ├── perfil_investidor.json
│   ├── produtos_financeiros.json
│   ├── transacoes.csv
│   └── historico_atendimento.csv
│
├── docs/
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
│
├── src/
│   ├── app.py
│   ├── agente.py
│   ├── config.py
│   ├── requirements.txt
│   └── README.md
│
└── README.md
```

---

## Principais Arquivos

### `src/app.py`

Arquivo principal da aplicação.

Responsável por:

- exibir a tela do Norte Financeiro;
- mostrar os indicadores principais do cliente;
- apresentar o chat;
- exibir perguntas rápidas;
- mostrar os dados carregados para conferência.

### `src/agente.py`

Contém as regras e funções principais do assistente.

Responsável por:

- carregar os dados do projeto;
- calcular o progresso da reserva de emergência;
- interpretar perguntas do usuário;
- gerar respostas no modo de demonstração;
- consultar produtos compatíveis;
- analisar transações;
- consultar histórico de atendimentos;
- usar o Ollama, caso esteja configurado;
- usar uma chave externa, caso esteja configurada.

### `src/config.py`

Centraliza caminhos e configurações do projeto.

Define:

- localização da pasta `data/`;
- caminho dos arquivos JSON e CSV;
- configuração do Ollama;
- configuração opcional de chave externa.

### `src/requirements.txt`

Lista as bibliotecas necessárias para executar o projeto.

---

## Dados Utilizados

A aplicação usa os arquivos da pasta `data/`.

| Arquivo | Função |
|---|---|
| `perfil_investidor.json` | Dados do cliente, perfil financeiro, objetivos e metas. |
| `produtos_financeiros.json` | Produtos disponíveis, risco, liquidez, aporte mínimo e indicação de uso. |
| `transacoes.csv` | Entradas, saídas, categorias, recorrência e relação com metas. |
| `historico_atendimento.csv` | Atendimentos anteriores, temas, canais, intenções e próximas ações. |

O assistente deve usar apenas esses dados para responder. Quando uma informação não estiver disponível, ele deve informar isso com clareza.

---

## Instalação

A partir da raiz do projeto, crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r src/requirements.txt
```

---

## Como Rodar

Execute a aplicação com Streamlit:

```bash
python -m streamlit run src/app.py
```

Ou, se o comando `streamlit` estiver disponível diretamente:

```bash
streamlit run src/app.py
```

Depois de iniciar, a aplicação normalmente fica disponível em:

```text
http://localhost:8501
```

---

## Uso com Ollama

O projeto pode usar o Ollama para gerar respostas localmente.

Modelo padrão configurado:

```text
llama3.2:1b
```

Para baixar o modelo:

```bash
ollama pull llama3.2:1b
```

Para testar no terminal:

```bash
ollama run llama3.2:1b
```

Se o Ollama não estiver rodando, o projeto continua funcionando no modo de demonstração.

---

## Uso com Chave Externa

Opcionalmente, é possível configurar uma chave externa.

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-5.5
```

O arquivo `.env` não deve ser enviado para o GitHub.

---

## Modo de Demonstração

O projeto funciona mesmo sem Ollama e sem chave externa.

Nesse modo, o assistente usa regras simples para responder perguntas comuns sobre:

- identidade do cliente fictício;
- perfil de investidor;
- reserva de emergência;
- metas financeiras;
- produtos compatíveis;
- transações;
- gastos recorrentes;
- gastos não essenciais;
- histórico de atendimentos;
- perguntas fora do escopo;
- pedidos de movimentação financeira.

Esse modo facilita a apresentação do projeto sem depender de serviços externos.

---

## Exemplos de Perguntas

```text
Qual é meu nome?
Qual é meu perfil de investidor?
Quanto falta para completar minha reserva?
Quais são minhas metas financeiras?
Onde posso deixar o dinheiro da reserva?
LCI/LCA serve para minha reserva de emergência?
Fundo de ações combina com minha reserva?
Qual foi meu total de saídas?
Quais gastos não essenciais posso revisar?
Já perguntei sobre CDB antes?
Pode aplicar R$ 1.000 no CDB para mim?
Qual a previsão do tempo para amanhã?
```

---

## Regras de Segurança

O assistente deve:

- usar apenas os dados fornecidos no projeto;
- não inventar produtos, taxas, saldos, prazos ou dados do cliente;
- não prometer ganhos futuros;
- não sugerir produtos incompatíveis com o perfil do cliente;
- evitar produtos de alto risco para clientes que não aceitam risco;
- priorizar produtos de baixo risco e resgate fácil para reserva de emergência;
- recusar pedidos de senha, CPF ou dados sensíveis;
- recusar pedidos sobre dados de outro cliente;
- não realizar aplicações, resgates ou transferências;
- informar quando não houver dados suficientes.

---

## Testes

O assistente foi testado com perguntas relacionadas a cada arquivo do projeto:

- `perfil_investidor.json`;
- metas financeiras dentro do perfil;
- `produtos_financeiros.json`;
- `transacoes.csv`;
- `historico_atendimento.csv`.

Os testes verificam:

- se a resposta está correta;
- se respeita o perfil do cliente;
- se evita informações inventadas;
- se recusa pedidos fora do escopo;
- se explica as sugestões de forma clara.

A documentação dos testes está em:

```text
docs/04-metricas.md
```

---

## Documentação

A documentação do projeto está organizada na pasta `docs/`.

| Arquivo | Conteúdo |
|---|---|
| `01-documentacao-agente.md` | Caso de uso, público-alvo, arquitetura e funcionamento. |
| `02-base-conhecimento.md` | Explicação dos dados utilizados e como eles são usados. |
| `03-prompts.md` | Regras de comportamento, exemplos e casos limite. |
| `04-metricas.md` | Testes, critérios de avaliação e resultados. |
| `05-pitch.md` | Roteiro sugerido para apresentação do projeto. |

---

## Limitações

Este projeto é um protótipo acadêmico.

Ele não realiza movimentações financeiras reais.

O assistente não substitui um consultor financeiro profissional.

As respostas são baseadas apenas em dados simulados e nos produtos disponíveis no projeto.

O projeto não deve ser usado para tomar decisões financeiras reais sem validação profissional.

---

## Status do Projeto

Protótipo funcional concluído.

Funcionalidades implementadas:

- interface em Streamlit;
- carregamento de dados locais;
- chat com histórico de conversa;
- perguntas rápidas;
- modo de demonstração;
- uso opcional com Ollama;
- uso opcional com chave externa;
- testes por arquivo do projeto;
- documentação de funcionamento, dados, regras e métricas.

---

## Observação Final

O **Norte Financeiro** demonstra como uma aplicação pode usar dados simulados para oferecer orientações financeiras mais claras, seguras e compatíveis com o perfil de um cliente.

O foco do projeto é apresentar uma solução simples, responsável e fácil de entender.
