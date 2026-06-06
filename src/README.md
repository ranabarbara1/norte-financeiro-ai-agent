# Código da Aplicação

Esta pasta contém o código do protótipo funcional do **Norte Financeiro**, um agente financeiro consultivo para acompanhamento de metas, análise de gastos e orientações seguras com base no perfil do cliente.

A aplicação foi desenvolvida com **Streamlit** e utiliza os arquivos da pasta `data/` como base para montar as respostas.

---

## Estrutura

```text
src/
├── app.py              # Aplicação principal em Streamlit
├── agente.py           # Regras, carregamento dos dados e respostas do agente
├── config.py           # Caminhos dos arquivos e configurações do projeto
├── requirements.txt    # Dependências necessárias para rodar a aplicação
└── README.md           # Documentação desta pasta
```

---

## Arquivos

### `app.py`

Arquivo principal da aplicação.

Responsável por:

- exibir a interface do Norte Financeiro;
- mostrar o resumo do cliente;
- apresentar o chat;
- exibir perguntas rápidas;
- mostrar os dados carregados.

### `agente.py`

Contém a lógica principal do agente.

Responsável por:

- carregar os dados da pasta `data/`;
- calcular o progresso da reserva de emergência;
- identificar produtos compatíveis com o perfil do cliente;
- gerar respostas em modo demonstrativo;
- usar um modelo externo, caso uma chave de API seja configurada.

### `config.py`

Centraliza os caminhos dos arquivos e configurações do projeto.

Ele indica onde estão os arquivos:

- `perfil_investidor.json`;
- `produtos_financeiros.json`;
- `transacoes.csv`;
- `historico_atendimento.csv`.

Também lê configurações opcionais, como chave de API.

### `requirements.txt`

Lista as bibliotecas necessárias para executar o projeto.

---

## Dependências

```txt
streamlit
pandas
python-dotenv
openai
```

---

## Como Rodar

A partir da raiz do projeto, instale as dependências:

```bash
pip install -r src/requirements.txt
```

Depois, rode a aplicação:

```bash
streamlit run src/app.py
```

Se o comando `streamlit` não funcionar diretamente, use:

```bash
python -m streamlit run src/app.py
```

---

## Modo Demonstrativo

O protótipo funciona mesmo sem chave de API.

Nesse modo, o agente usa regras simples para responder perguntas comuns, como:

- quanto falta para completar a reserva;
- onde deixar o dinheiro da reserva;
- como guardar mais dinheiro;
- por que fundo de ações não é adequado para reserva de emergência;
- o que fazer quando a pergunta está fora do escopo.

Esse modo foi criado para facilitar a demonstração do projeto sem depender de serviços externos.

---

## Uso com API

Caso uma chave de API seja configurada, o projeto pode tentar usar um modelo externo para gerar respostas mais flexíveis.

Para isso, crie um arquivo `.env` na raiz do projeto com:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-5.5
```

O arquivo `.env` não deve ser enviado para o GitHub.

---

## Exemplos de Perguntas

- Quanto falta para completar minha reserva?
- Onde posso deixar o dinheiro da reserva?
- Como posso guardar mais dinheiro?
- Vale a pena colocar minha reserva em fundo de ações?
- Pode aplicar R$ 1.000 no CDB para mim?

---

## Observação

Este protótipo não realiza movimentações financeiras reais.

Ele apenas demonstra como um agente financeiro pode usar dados simulados para oferecer orientações mais claras, seguras e compatíveis com o perfil de um cliente fictício.