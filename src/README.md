# Código da Aplicação

Esta pasta contém o código principal do **Norte Financeiro**, uma aplicação em Streamlit que permite conversar com um assistente financeiro baseado nos dados simulados do projeto.

O código desta pasta é responsável por carregar os dados, exibir a interface, processar perguntas e gerar respostas com base nas regras definidas.

---

## Estrutura da Pasta

```text
src/
├── app.py
├── agente.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Arquivos

### `app.py`

Arquivo principal da aplicação.

Responsável por:

* configurar a página do Streamlit;
* exibir o logo, título e indicadores principais;
* mostrar o resumo do cliente;
* apresentar o chat;
* exibir perguntas rápidas;
* mostrar os dados carregados para conferência.

Este é o arquivo executado para iniciar a aplicação.

---

### `agente.py`

Contém a lógica principal do assistente.

Responsável por:

* carregar os arquivos da pasta `data/`;
* calcular o progresso da reserva de emergência;
* formatar valores, datas e textos;
* interpretar perguntas do usuário;
* responder sobre perfil, metas, produtos, transações e histórico de atendimentos;
* bloquear perguntas fora do escopo;
* impedir pedidos de movimentação financeira;
* usar o Ollama, se estiver configurado;
* usar uma chave externa, se estiver configurada.

---

### `config.py`

Centraliza os caminhos e configurações usados pela aplicação.

Define:

* caminho da pasta `data/`;
* caminho dos arquivos `perfil_investidor.json`, `produtos_financeiros.json`, `transacoes.csv` e `historico_atendimento.csv`;
* configurações do Ollama;
* configurações opcionais de chave externa.

---

### `requirements.txt`

Lista as bibliotecas necessárias para executar a aplicação.

Dependências principais:

```txt
streamlit
pandas
python-dotenv
openai
requests
```

---

## Como Executar

A partir da raiz do projeto, instale as dependências:

```bash
pip install -r src/requirements.txt
```

Depois, rode:

```bash
python -m streamlit run src/app.py
```

A aplicação normalmente ficará disponível em:

```text
http://localhost:8501
```

---

## Observação sobre os Dados

Os arquivos de dados não ficam dentro da pasta `src/`.

Eles ficam na pasta `data/`, na raiz do projeto:

```text
data/
├── perfil_investidor.json
├── produtos_financeiros.json
├── transacoes.csv
└── historico_atendimento.csv
```

O arquivo `config.py` é responsável por indicar esses caminhos para a aplicação.

---

## Funcionamento Geral

O fluxo básico da aplicação é:

1. O Streamlit inicia o arquivo `app.py`.
2. O `app.py` chama as funções de `agente.py`.
3. O `agente.py` carrega os dados da pasta `data/`.
4. A interface mostra o resumo do cliente e o chat.
5. O usuário faz uma pergunta.
6. O assistente responde com base nos dados e nas regras do projeto.

---

## Modo de Demonstração

Mesmo sem Ollama ou chave externa, a aplicação continua funcionando.

Nesse caso, o arquivo `agente.py` usa regras simples para responder perguntas sobre:

* dados do cliente;
* reserva de emergência;
* metas financeiras;
* produtos disponíveis;
* transações;
* histórico de atendimentos;
* perguntas fora do escopo;
* pedidos que não podem ser executados.

---

## Cuidados ao Alterar o Código

Ao modificar esta pasta, é importante manter:

* os nomes das funções usadas por `app.py`;
* os caminhos definidos em `config.py`;
* as regras de segurança em `agente.py`;
* o uso dos dados apenas a partir da pasta `data/`;
* a separação entre interface, lógica e configuração.

---

## Arquivo Principal

Para rodar a aplicação, o arquivo principal é:

```text
src/app.py
```

Comando recomendado:

```bash
python -m streamlit run src/app.py
```
