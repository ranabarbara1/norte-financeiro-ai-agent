# Base de Conhecimento

## Dados Utilizados

A base de conhecimento do **Norte Financeiro** foi criada com os arquivos disponíveis na pasta `data/`.

Esses arquivos reúnem as principais informações necessárias para o agente entender a situação financeira do cliente e oferecer orientações mais úteis.

| Arquivo                     | Formato | Utilização no Agente                                                      |
| --------------------------- | ------- | ------------------------------------------------------------------------- |
| `historico_atendimento.csv` | CSV     | Entender conversas anteriores e evitar repetir orientações já dadas       |
| `perfil_investidor.json`    | JSON    | Conhecer o perfil, a renda, as metas e as preferências do cliente         |
| `produtos_financeiros.json` | JSON    | Verificar quais produtos estão disponíveis e quais combinam com o cliente |
| `transacoes.csv`            | CSV     | Analisar entradas, saídas e hábitos de consumo do cliente                 |

Esses dados ajudam o agente a responder considerando o contexto do cliente, em vez de tratar cada pergunta como uma conversa isolada.

---

## Adaptações nos Dados

Os dados originais foram adaptados para ficarem mais próximos do caso de uso do **Norte Financeiro**.

A proposta do agente é ajudar o cliente a acompanhar metas financeiras, entender seus gastos e receber sugestões seguras. Para isso, os arquivos receberam novas informações que tornam essa análise mais completa.

### Adaptações no arquivo `perfil_investidor.json`

O perfil do cliente recebeu novas informações para deixar as orientações mais adequadas à sua realidade.

Foram adicionados campos como:

* preferência por liquidez;
* valor de aporte mensal desejado;
* canal preferido de atendimento;
* nível de conhecimento financeiro;
* autorização para receber alertas;
* frequência desejada para revisão das metas.

Esses dados ajudam o agente a respeitar melhor as preferências do cliente.

Por exemplo, se o cliente não aceita risco e prefere liquidez alta, o agente deve evitar produtos arriscados e priorizar alternativas que permitam resgate rápido.

### Adaptações no arquivo `transacoes.csv`

O histórico de transações foi ampliado para mostrar mais meses da movimentação financeira do cliente.

Também foram adicionados campos como:

* `essencial`: indica se o gasto é necessário ou se pode ser revisto;
* `recorrente`: indica se o gasto acontece com frequência;
* `meta_relacionada`: indica se a movimentação tem relação com alguma meta financeira.

Com essas informações, o agente consegue diferenciar gastos obrigatórios de gastos que podem ser ajustados.

Isso permite, por exemplo, sugerir que o cliente reduza despesas não essenciais e direcione parte desse valor para a reserva de emergência.

### Adaptações no arquivo `produtos_financeiros.json`

A lista de produtos financeiros recebeu novas informações para ajudar o agente a fazer sugestões mais cuidadosas.

Foram adicionados campos como:

* liquidez;
* indicação para reserva de emergência;
* observações sobre o uso do produto.

Essas informações ajudam o agente a verificar se um produto combina com a necessidade do cliente.

Para uma reserva de emergência, por exemplo, o agente deve priorizar produtos de baixo risco e com facilidade de resgate.

### Adaptações no arquivo `historico_atendimento.csv`

O histórico de atendimento foi ampliado para registrar melhor o que já foi conversado com o cliente.

Foram adicionados campos como:

* intenção do cliente;
* próxima ação sugerida;
* prioridade do atendimento.

Esses dados ajudam o agente a manter continuidade na conversa.

Assim, se o cliente já demonstrou interesse em completar a reserva de emergência, o agente pode retomar esse assunto em uma próxima interação sem começar do zero.

---

## Estratégia de Integração

### Como os dados são carregados?

Os arquivos da pasta `data/` são carregados pela aplicação quando o agente é iniciado.

Os arquivos `.json` guardam informações mais organizadas, como o perfil do cliente e a lista de produtos financeiros.

Os arquivos `.csv` guardam históricos, como transações e atendimentos anteriores.

Antes de responder, o agente consulta essas informações para entender melhor o pedido do cliente.

### Como os dados são usados no atendimento?

Os dados são usados para orientar as respostas do agente.

O agente consulta a base de conhecimento quando precisa responder sobre:

* perfil financeiro do cliente;
* metas cadastradas;
* histórico de gastos;
* atendimentos anteriores;
* produtos financeiros disponíveis;
* relação entre produto, objetivo e perfil do cliente.

O agente não deve inventar informações que não estejam nos arquivos.

Antes de sugerir qualquer produto financeiro, ele deve verificar:

* se o cliente aceita ou não aceita risco;
* qual é o objetivo financeiro do cliente;
* se o cliente precisa de facilidade para resgatar o dinheiro;
* qual é o valor mínimo para aplicar no produto;
* se o produto combina com a meta informada.

Essa forma de uso ajuda o agente a dar respostas mais seguras e evita sugestões incompatíveis com a situação do cliente.

---

## Exemplo de Contexto Montado

Abaixo está um exemplo de como as informações podem ser organizadas antes da resposta do agente:

```text
Dados do Cliente:
- Nome: João Silva
- Idade: 32 anos
- Profissão: Analista de Sistemas
- Renda mensal: R$ 5.000,00
- Perfil de investidor: Moderado
- Aceita risco: Não
- Objetivo principal: Construir reserva de emergência
- Reserva de emergência atual: R$ 10.000,00
- Meta da reserva de emergência: R$ 15.000,00
- Valor restante para a meta: R$ 5.000,00
- Preferência por liquidez: Alta
- Valor de aporte mensal desejado: R$ 600,00
- Nível de conhecimento financeiro: Iniciante

Metas Financeiras:
1. Completar reserva de emergência
   - Valor necessário: R$ 15.000,00
   - Prazo: Junho de 2026

2. Entrada do apartamento
   - Valor necessário: R$ 50.000,00
   - Prazo: Dezembro de 2027

Resumo das Transações:
- Receita mensal recorrente: Salário
- Despesas essenciais: moradia, alimentação, transporte e contas básicas
- Despesas não essenciais: lazer, delivery, assinaturas e compras eventuais
- Gastos recorrentes identificados: aluguel, internet, streaming e supermercado

Produtos disponíveis compatíveis com reserva de emergência:
1. Tesouro Selic
   - Categoria: Renda fixa
   - Risco: Baixo
   - Liquidez: Diária
   - Aporte mínimo: R$ 30,00
   - Indicado para: Reserva de emergência e iniciantes

2. CDB Liquidez Diária
   - Categoria: Renda fixa
   - Risco: Baixo
   - Liquidez: Diária
   - Aporte mínimo: R$ 100,00
   - Indicado para: Quem busca segurança com rendimento diário

Histórico de Atendimento:
- Cliente demonstrou interesse em completar a reserva de emergência
- Cliente prefere opções seguras
- Próxima ação sugerida: acompanhar evolução da reserva e sugerir aporte mensal
```

Com esse contexto, o agente pode responder de forma mais clara e personalizada.

Exemplo de resposta possível:

```text
João, sua reserva de emergência atual é de R$ 10.000,00 e sua meta é chegar a R$ 15.000,00 até junho de 2026. Portanto, ainda faltam R$ 5.000,00.

Como você informou que não aceita risco e prefere liquidez alta, as alternativas mais compatíveis são produtos de baixo risco e com possibilidade de resgate rápido, como Tesouro Selic ou CDB com liquidez diária.

Considerando seu aporte mensal desejado de R$ 600,00, você pode avançar de forma constante em direção à sua meta. Posso ajudar a acompanhar esse progresso mês a mês.
```

---

## Cuidados no Uso da Base de Conhecimento

Para garantir respostas confiáveis, o agente deve seguir algumas regras:

* usar apenas informações presentes nos arquivos da pasta `data/`;
* não inventar produtos, taxas, saldos ou condições;
* não prometer ganhos futuros;
* não sugerir produtos incompatíveis com o perfil do cliente;
* priorizar produtos de baixo risco quando o cliente não aceitar risco;
* considerar facilidade de resgate para objetivos como reserva de emergência;
* informar quando não houver dados suficientes para responder;
* sugerir atendimento humano em situações mais complexas.

Esses cuidados ajudam o **Norte Financeiro** a oferecer orientações mais seguras, claras e coerentes com os dados disponíveis.