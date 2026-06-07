"""Lógica do agente Norte Financeiro.

Este módulo concentra:
- carregamento dos dados do projeto;
- formatação de textos, moedas e datas;
- regras demonstrativas para perguntas frequentes;
- integração opcional com Ollama e OpenAI.

A ideia é manter cada grupo de regras em uma função própria para facilitar
manutenção e testes.
"""

import json
from typing import Any

import pandas as pd
import requests

from config import (
    PERFIL_PATH,
    PRODUTOS_PATH,
    TRANSACOES_PATH,
    ATENDIMENTOS_PATH,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OLLAMA_URL,
    OLLAMA_MODEL,
)


# =============================================================================
# Constantes
# =============================================================================

TRADUCOES_TEXTO = {
    "em_andamento": "em andamento",
    "planejada": "planejada",
    "alta": "alta",
    "media": "média",
    "baixo": "baixo",
    "medio": "médio",
    "alto": "alto",
    "variavel": "variável",
    "diaria": "diária",
    "apos_90_dias": "após 90 dias",
    "renda_fixa": "renda fixa",
    "alimentacao": "alimentação",
    "saude": "saúde",
    "nao": "não",
    "sim": "sim",
    "nao_aplicavel": "não aplicável",
    "baixa": "baixa",
    "entender_produto": "entender produto",
    "resolver_problema": "resolver problema",
    "acompanhar_meta": "acompanhar meta",
    "atualizar_dados": "atualizar dados",
    "reduzir_gastos": "reduzir gastos",
}

MESES = {
    "01": "janeiro",
    "02": "fevereiro",
    "03": "março",
    "04": "abril",
    "05": "maio",
    "06": "junho",
    "07": "julho",
    "08": "agosto",
    "09": "setembro",
    "10": "outubro",
    "11": "novembro",
    "12": "dezembro",
}

TERMOS_FORA_DO_ESCOPO = [
    "mercado internacional",
    "internacional",
    "nível internacional",
    "nivel internacional",
    "investir fora",
    "investir no exterior",
    "exterior",
    "fora do brasil",
    "fora do país",
    "fora do pais",
    "bolsa americana",
    "nasdaq",
    "s&p",
    "s&p 500",
    "dow jones",
    "ações americanas",
    "acoes americanas",
    "ações estrangeiras",
    "acoes estrangeiras",
    "dólar",
    "dolar",
    "câmbio",
    "cambio",
    "cripto",
    "criptomoeda",
    "criptomoedas",
    "bitcoin",
    "ethereum",
    "etf",
    "etfs",
    "bdr",
    "bdrs",
    "stock",
    "stocks",
    "ibovespa hoje",
    "selic hoje",
    "cdi hoje",
    "previsão da bolsa",
    "previsao da bolsa",
]


# =============================================================================
# Utilidades de formatação e busca
# =============================================================================


def normalizar_texto(valor: Any) -> str:
    """Normaliza valores para comparação textual simples."""
    return str(valor or "").strip().lower()


def contem(pergunta: str, termos: list[str]) -> bool:
    """Verifica se a pergunta contém algum termo esperado."""
    return any(termo in pergunta for termo in termos)


def formatar_moeda(valor: Any) -> str:
    """Formata valores no padrão brasileiro, escapando o cifrão para o Streamlit."""
    try:
        valor_formatado = (
            f"R$ {float(valor):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        return valor_formatado.replace("$", "\\$")
    except Exception:
        return "R\\$ 0,00"


def formatar_texto_base(valor: Any) -> str:
    """Formata textos técnicos da base para linguagem natural."""
    if valor is None:
        return "não informado"

    texto = normalizar_texto(valor)
    return TRADUCOES_TEXTO.get(texto, texto.replace("_", " "))


def formatar_data_meta(valor: Any) -> str:
    """Converte datas de meta como 2026-06 para junho de 2026."""
    if not valor:
        return "não informado"

    texto = str(valor).strip()
    partes = texto.split("-")

    if len(partes) == 2:
        ano, mes = partes
        nome_mes = MESES.get(mes)

        if nome_mes:
            return f"{nome_mes} de {ano}"

    return texto


def formatar_data_brasileira(valor: Any) -> str:
    """Converte datas como 2025-10-30 para 30/10/2025."""
    if not valor:
        return "não informado"

    try:
        data = pd.to_datetime(valor, errors="coerce")

        if pd.notna(data):
            return data.strftime("%d/%m/%Y")

    except Exception:
        pass

    return str(valor)


def primeira_linha_por_termo(df: pd.DataFrame, termo: str) -> pd.DataFrame:
    """Filtra linhas de um DataFrame que contenham o termo em qualquer coluna."""
    return df[
        df.apply(
            lambda linha: termo in " ".join(linha.astype(str)).lower(),
            axis=1,
        )
    ]


def encontrar_meta(perfil: dict[str, Any], termo: str) -> dict[str, Any] | None:
    """Busca uma meta pelo nome."""
    for meta in perfil.get("metas", []):
        if termo in normalizar_texto(meta.get("meta")):
            return meta

    return None


def encontrar_produto_por_nome(
    produtos: list[dict[str, Any]],
    *termos: str,
) -> dict[str, Any] | None:
    """Busca um produto por um ou mais termos no nome."""
    for produto in produtos:
        nome_produto = normalizar_texto(produto.get("nome"))

        if any(termo in nome_produto for termo in termos):
            return produto

    return None


# =============================================================================
# Carregamento e preparação de dados
# =============================================================================


def carregar_json(caminho):
    """Carrega um arquivo JSON com codificação UTF-8."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_dados():
    """Carrega os arquivos da pasta data."""
    perfil = carregar_json(PERFIL_PATH)
    produtos = carregar_json(PRODUTOS_PATH)
    transacoes = pd.read_csv(TRANSACOES_PATH)
    atendimentos = pd.read_csv(ATENDIMENTOS_PATH)

    return perfil, produtos, transacoes, atendimentos


def calcular_reserva(perfil):
    """Calcula quanto falta para completar a reserva de emergência."""
    reserva_atual = float(perfil.get("reserva_emergencia_atual", 0))
    meta_reserva = encontrar_meta(perfil, "reserva")

    if not meta_reserva:
        return reserva_atual, 0, 0, "Não informado"

    valor_meta = float(meta_reserva.get("valor_necessario", 0))
    prazo = meta_reserva.get("prazo", "Não informado")
    valor_faltante = max(valor_meta - reserva_atual, 0)

    return reserva_atual, valor_meta, valor_faltante, prazo


def buscar_produtos_para_reserva(produtos):
    """Filtra produtos compatíveis com reserva de emergência."""
    produtos_compativeis = []

    for produto in produtos:
        risco = normalizar_texto(produto.get("risco"))
        liquidez = normalizar_texto(produto.get("liquidez"))
        indicado_para = normalizar_texto(produto.get("indicado_para"))
        adequado = produto.get("adequado_para_reserva", False)

        if risco == "baixo" and (
            adequado is True
            or "reserva" in indicado_para
            or "diaria" in liquidez
            or "diária" in liquidez
        ):
            produtos_compativeis.append(produto)

    return produtos_compativeis


def resumir_transacoes(transacoes):
    """Cria um resumo simples das transações."""
    if transacoes.empty:
        return "Não há transações disponíveis."

    df = transacoes.copy()

    if "valor" not in df.columns:
        return "O arquivo de transações não possui a coluna 'valor'."

    if "tipo" in df.columns:
        df["tipo"] = df["tipo"].astype(str).str.lower()
        entradas = df[df["tipo"] == "entrada"]["valor"].sum()
        saidas = df[df["tipo"] == "saida"]["valor"].sum()
    else:
        entradas = 0
        saidas = df["valor"].sum()

    saldo = entradas - saidas
    resumo = [
        f"Total de entradas: {formatar_moeda(entradas)}",
        f"Total de saídas: {formatar_moeda(saidas)}",
        f"Saldo aproximado no período: {formatar_moeda(saldo)}",
    ]

    if "categoria" in df.columns and "tipo" in df.columns:
        saidas_df = df[df["tipo"] == "saida"]
        gastos_categoria = (
            saidas_df.groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        resumo.append("Principais categorias de gasto:")

        for categoria, valor in gastos_categoria.items():
            resumo.append(f"- {formatar_texto_base(categoria)}: {formatar_moeda(valor)}")

    return "\n".join(resumo)


def montar_contexto(perfil, produtos, transacoes, atendimentos):
    """Monta um resumo organizado dos dados disponíveis."""
    reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)
    produtos_reserva = buscar_produtos_para_reserva(produtos)

    contexto = {
        "identidade_da_conversa": {
            "usuario_atual_representa": "cliente_ficticio",
            "instrucao": (
                "O usuário desta conversa está simulando o próprio cliente descrito em 'cliente'. "
                "Perguntas em primeira pessoa devem ser interpretadas como perguntas do próprio cliente."
            ),
        },
        "cliente": {
            "nome": perfil.get("nome"),
            "idade": perfil.get("idade"),
            "profissao": perfil.get("profissao"),
            "renda_mensal": perfil.get("renda_mensal"),
            "perfil_investidor": perfil.get("perfil_investidor"),
            "aceita_risco": perfil.get("aceita_risco"),
            "objetivo_principal": perfil.get("objetivo_principal"),
            "reserva_emergencia_atual": reserva_atual,
            "meta_reserva": valor_meta,
            "valor_faltante_reserva": valor_faltante,
            "prazo_reserva": prazo,
            "preferencia_liquidez": perfil.get("preferencia_liquidez"),
            "valor_aporte_mensal_desejado": perfil.get("valor_aporte_mensal_desejado"),
            "nivel_conhecimento_financeiro": perfil.get("nivel_conhecimento_financeiro"),
        },
        "produtos_compativeis_reserva": produtos_reserva,
        "resumo_transacoes": resumir_transacoes(transacoes),
        "ultimos_atendimentos": atendimentos.tail(3).to_dict(orient="records"),
    }

    return json.dumps(contexto, ensure_ascii=False, indent=2)


# =============================================================================
# Prompts e modelos externos
# =============================================================================


def system_prompt():
    """Instruções gerais do Norte Financeiro."""
    return """
Você é o Norte Financeiro, um agente financeiro consultivo.

IDENTIDADE DA CONVERSA:
- O usuário desta conversa está simulando o próprio cliente fictício descrito no contexto.
- Quando o usuário disser "eu", "meu", "minha", "meus dados", "minha reserva", "meu perfil" ou termos semelhantes, interprete como referência ao cliente do contexto.
- Não diga que está compartilhando informações de outro cliente quando a pergunta for sobre o próprio cliente do contexto.
- Você pode responder sobre dados financeiros fictícios do cliente presentes no contexto.
- Só recuse se o usuário pedir senhas, documentos sensíveis, dados de outro cliente, ou tentar realizar movimentações financeiras.

Você trabalha com dados fictícios e simulados deste projeto acadêmico. Esses dados foram fornecidos pela própria aplicação e podem ser usados para responder ao cliente fictício.

Seu objetivo é ajudar o cliente a acompanhar metas, entender gastos e receber orientações seguras com base nos dados disponíveis.

Regras:
1. Use apenas os dados fornecidos no contexto.
2. Não invente produtos, taxas, saldos, prazos ou informações do cliente.
3. Não use informações externas sobre mercado financeiro, bolsa, câmbio, criptomoedas ou notícias econômicas.
4. Se uma informação não estiver no contexto, diga que não possui dados suficientes.
5. Não prometa ganhos futuros.
6. Se o cliente não aceita risco, não sugira produtos de alto risco.
7. Para reserva de emergência, priorize produtos de baixo risco e com facilidade de resgate.
8. Explique sempre o motivo da sugestão.
9. Não realize aplicações, resgates, transferências ou qualquer movimentação financeira.
10. Use linguagem clara, educada e acessível.

Importante:
- Os dados do contexto são fictícios e fazem parte do projeto.
- Você pode usar esses dados para responder perguntas sobre o cliente fictício.
- Não trate os dados fornecidos no contexto como informação proibida.
- O usuário é o próprio cliente fictício durante esta simulação.

Responda sempre em português do Brasil.
"""


def responder_com_modelo(pergunta, contexto):
    """Tenta responder usando a API externa, caso a chave esteja configurada."""
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        resposta = client.responses.create(
            model=OPENAI_MODEL,
            instructions=system_prompt(),
            input=f"""
Contexto disponível:
{contexto}

Pergunta do cliente:
{pergunta}
""",
        )
        return resposta.output_text

    except Exception:
        return None


def responder_com_ollama(pergunta, contexto):
    """Tenta responder usando o modelo local do Ollama."""
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt()},
            {
                "role": "user",
                "content": f"""
Contexto disponível:
{contexto}

Pergunta do cliente:
{pergunta}
""",
            },
        ],
    }

    try:
        resposta = requests.post(OLLAMA_URL, json=payload, timeout=90)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados.get("message", {}).get("content")

    except Exception:
        return None


# =============================================================================
# Respostas reutilizáveis
# =============================================================================


def resposta_fora_do_escopo():
    return (
    "Não tenho dados suficientes no projeto para responder sobre esse assunto com segurança.\n\n"
    "O Norte Financeiro foi criado para ajudar com reserva de emergência, análise de gastos, "
    "metas financeiras e produtos disponíveis nos dados do projeto.\n\n"
    "Posso ajudar, por exemplo, com perguntas como:\n"
    "- Quanto falta para completar minha reserva?\n"
    "- Onde posso deixar o dinheiro da reserva?\n"
    "- Como posso guardar mais dinheiro?"
)


def resposta_fallback():
    return (
        "Posso ajudar com acompanhamento da reserva de emergência, análise de gastos e sugestões de produtos compatíveis com o perfil do cliente.\n\n"
        "Exemplos de perguntas:\n"
        "- Quanto falta para completar minha reserva?\n"
        "- Onde posso deixar o dinheiro da reserva?\n"
        "- Como posso guardar mais dinheiro?\n"
        "- Fundo de ações combina com minha reserva?"
    )


# =============================================================================
# Grupos de regras demonstrativas
# =============================================================================


def responder_seguranca(pergunta):
    """Responde pedidos sensíveis ou fora do papel do agente."""
    if contem(pergunta, ["senha", "cpf", "dados de outro cliente"]):
        return (
            "Não posso compartilhar senhas, documentos ou informações sensíveis. "
            "Posso ajudar apenas com orientações financeiras baseadas nos dados permitidos do projeto."
        )

    if contem(pergunta, ["outro cliente", "outra pessoa", "dados de terceiros"]):
        return (
            "Não posso compartilhar dados de outro cliente. "
            "Nesta simulação, posso responder apenas sobre o cliente fictício carregado no contexto."
        )

    if contem(pergunta, ["previsão do tempo", "clima", "futebol", "receita de bolo"]):
        return (
            "Eu posso ajudar com organização financeira, metas, gastos e produtos disponíveis no projeto. "
            "Não tenho informações sobre esse assunto.\n\n"
            "Posso ajudar com algo relacionado às suas finanças?"
        )

    if contem(pergunta, ["aplicar", "resgatar", "transferir", "transfere"]):
        return (
            "Não posso realizar aplicações, resgates ou transferências. "
            "Posso apenas explicar se um produto combina com seu perfil e sua meta. "
            "A decisão e a execução devem ser feitas por você nos canais oficiais da instituição financeira."
        )

    return None


def responder_historico(pergunta, atendimentos):
    """Responde perguntas baseadas no histórico de atendimentos."""
    termos_historico = [
        "últimos atendimentos",
        "ultimos atendimentos",
        "atendimento mais recente",
        "último atendimento",
        "ultimo atendimento",
        "canal usei no último atendimento",
        "canal usei no ultimo atendimento",
        "tema do meu último atendimento",
        "tema do meu ultimo atendimento",
        "atendimento de alta prioridade",
        "próxima ação sugerida",
        "proxima acao sugerida",
        "perguntei sobre tesouro",
        "perguntei sobre cdb",
        "problema no app",
        "alerta de gastos",
        "recebi algum alerta",
        "atendimentos foram resolvidos",
        "intenção do atendimento",
        "intencao do atendimento",
    ]

    if not contem(pergunta, termos_historico):
        return None

    if atendimentos is None or atendimentos.empty:
        return "Não encontrei histórico de atendimentos na base do projeto."

    df = atendimentos.copy()

    if "data" in df.columns:
        df["data_convertida"] = pd.to_datetime(df["data"], errors="coerce")
        df = df.sort_values("data_convertida")

    if contem(pergunta, ["últimos atendimentos", "ultimos atendimentos"]):
        resposta = ["Seus últimos atendimentos registrados foram:"]

        for _, linha in df.tail(3).iterrows():
            resposta.append(
                f"- {formatar_data_brasileira(linha.get('data'))}, "
                f"pelo canal {linha.get('canal', 'não informado')}, "
                f"tema {linha.get('tema', 'não informado')}, "
                f"prioridade {formatar_texto_base(linha.get('prioridade', 'não informada'))}."
            )

        return "\n".join(resposta)

    if contem(pergunta, ["canal usei no último atendimento", "canal usei no ultimo atendimento"]):
        ultimo = df.iloc[-1]
        return (
            f"No último atendimento, em {formatar_data_brasileira(ultimo.get('data'))}, "
            f"você usou o canal {ultimo.get('canal', 'não informado')}."
        )

    if contem(pergunta, ["tema do meu último atendimento", "tema do meu ultimo atendimento"]):
        ultimo = df.iloc[-1]
        return (
            f"O tema do seu último atendimento, em {formatar_data_brasileira(ultimo.get('data'))}, "
            f"foi {ultimo.get('tema', 'não informado')}."
        )

    if contem(pergunta, ["atendimento mais recente", "último atendimento", "ultimo atendimento"]):
        ultimo = df.iloc[-1]
        return (
            f"Seu atendimento mais recente foi em {formatar_data_brasileira(ultimo.get('data'))}, "
            f"pelo canal {ultimo.get('canal', 'não informado')}. "
            f"O tema foi {ultimo.get('tema', 'não informado')}. "
            f"Resumo: {ultimo.get('resumo', 'não informado')}."
        )

    if contem(pergunta, ["atendimento de alta prioridade", "alta prioridade"]):
        alta_prioridade = df[df["prioridade"].astype(str).str.lower() == "alta"]

        if alta_prioridade.empty:
            return "Não encontrei atendimentos de alta prioridade na base."

        resposta = ["Encontrei os seguintes atendimentos de alta prioridade:"]

        for _, linha in alta_prioridade.iterrows():
            resposta.append(
                f"- {formatar_data_brasileira(linha.get('data'))}: "
                f"{linha.get('tema', 'não informado')}. "
                f"Resumo: {linha.get('resumo', 'não informado')}"
            )

        return "\n".join(resposta)

    if contem(pergunta, ["próxima ação sugerida", "proxima acao sugerida"]):
        atend_reserva = df[
            df["resumo"].fillna("").astype(str).str.lower().str.contains("reserva")
        ]

        if atend_reserva.empty:
            return "Não encontrei atendimento relacionado à reserva na base."

        linha = atend_reserva.iloc[-1]
        return (
            f"A próxima ação sugerida sobre sua reserva, no atendimento de "
            f"{formatar_data_brasileira(linha.get('data'))}, foi: "
            f"{linha.get('proxima_acao_sugerida', 'não informada')}."
        )

    if contem(pergunta, ["perguntei sobre tesouro", "tesouro selic antes"]):
        atend_tesouro = primeira_linha_por_termo(df, "tesouro")

        if atend_tesouro.empty:
            return "Não encontrei atendimento anterior sobre Tesouro Selic."

        linha = atend_tesouro.iloc[-1]
        return (
            f"Sim. Você já teve atendimento sobre Tesouro Selic em "
            f"{formatar_data_brasileira(linha.get('data'))}, pelo canal "
            f"{linha.get('canal', 'não informado')}. Resumo: {linha.get('resumo', 'não informado')}."
        )

    if contem(pergunta, ["perguntei sobre cdb", "cdb antes"]):
        atend_cdb = primeira_linha_por_termo(df, "cdb")

        if atend_cdb.empty:
            return "Não encontrei atendimento anterior sobre CDB."

        linha = atend_cdb.iloc[-1]
        return (
            f"Sim. Você já teve atendimento sobre CDB em {formatar_data_brasileira(linha.get('data'))}, "
            f"pelo canal {linha.get('canal', 'não informado')}. "
            f"Resumo: {linha.get('resumo', 'não informado')}."
        )

    if contem(pergunta, ["problema no app", "erro no app"]):
        atend_app = df[
            df.apply(
                lambda linha: "app" in " ".join(linha.astype(str)).lower()
                or "extrato" in " ".join(linha.astype(str)).lower(),
                axis=1,
            )
        ]

        if atend_app.empty:
            return "Não encontrei atendimento anterior sobre problema no app."

        linha = atend_app.iloc[0]
        return (
            f"Sim. Houve um atendimento sobre problema no app em "
            f"{formatar_data_brasileira(linha.get('data'))}. "
            f"Resumo: {linha.get('resumo', 'não informado')}. "
            f"Resolvido: {formatar_texto_base(linha.get('resolvido', 'não informado'))}."
        )

    if contem(pergunta, ["alerta de gastos", "recebi algum alerta"]):
        atend_alerta = df[
            df.apply(
                lambda linha: "alerta" in " ".join(linha.astype(str)).lower()
                or "gastos" in " ".join(linha.astype(str)).lower(),
                axis=1,
            )
        ]

        if atend_alerta.empty:
            return "Não encontrei atendimento anterior sobre alerta de gastos."

        linha = atend_alerta.iloc[-1]
        return (
            f"Sim. Em {formatar_data_brasileira(linha.get('data'))}, você recebeu um alerta de gastos. "
            f"Resumo: {linha.get('resumo', 'não informado')}. "
            f"Próxima ação sugerida: {linha.get('proxima_acao_sugerida', 'não informada')}."
        )

    if contem(pergunta, ["atendimentos foram resolvidos", "quais atendimentos foram resolvidos"]):
        if "resolvido" not in df.columns:
            return "Não encontrei a coluna de resolução nos atendimentos."

        resolvidos = df[df["resolvido"].astype(str).str.lower() == "sim"]
        return (
            f"Foram encontrados {len(resolvidos)} atendimentos resolvidos "
            f"de um total de {len(df)} registros."
        )

    if contem(pergunta, ["intenção do atendimento", "intencao do atendimento", "metas financeiras"]):
        atend_metas = df[
            df["tema"].fillna("").astype(str).str.lower().str.contains("metas")
        ]

        if atend_metas.empty:
            return "Não encontrei atendimento sobre metas financeiras na base."

        linha = atend_metas.iloc[-1]
        return (
            f"No atendimento sobre metas financeiras, em {formatar_data_brasileira(linha.get('data'))}, "
            f"a intenção registrada foi "
            f"{formatar_texto_base(linha.get('intencao_cliente', 'não informada'))}. "
            f"Resumo: {linha.get('resumo', 'não informado')}."
        )

    return None


def responder_produtos(pergunta, produtos, produtos_reserva):
    """Responde perguntas sobre produtos financeiros."""
    if contem(pergunta, ["lci", "lca", "lci/lca"]):
        produto = encontrar_produto_por_nome(produtos, "lci", "lca")

        if not produto:
            return (
                "Não encontrei LCI/LCA na base de produtos disponível. "
                "Por segurança, não vou inventar uma recomendação."
            )

        return (
            f"A {produto.get('nome')} não é a opção mais indicada para sua reserva de emergência imediata. "
            f"Embora tenha risco {formatar_texto_base(produto.get('risco'))}, sua liquidez é "
            f"{formatar_texto_base(produto.get('liquidez'))}, ou seja, o dinheiro pode não estar disponível imediatamente.\n\n"
            "Para reserva de emergência, o ideal é priorizar produtos de baixo risco e com resgate mais fácil, "
            "como Tesouro Selic e CDB Liquidez Diária, que estão marcados na base como compatíveis com reserva."
        )

    if contem(
        pergunta,
        [
            "quais produtos financeiros estão disponíveis",
            "produtos financeiros disponíveis",
            "quais produtos disponíveis",
            "listar produtos",
        ],
    ):
        if not produtos:
            return "Não encontrei produtos financeiros cadastrados na base do projeto."

        resposta = ["Os produtos financeiros disponíveis na base são:"]

        for produto in produtos:
            resposta.append(
                f"- {produto.get('nome', 'Produto sem nome')}: "
                f"risco {formatar_texto_base(produto.get('risco'))}, "
                f"liquidez {formatar_texto_base(produto.get('liquidez'))}, "
                f"aporte mínimo de {formatar_moeda(produto.get('aporte_minimo', 0))}, "
                f"indicado para {produto.get('indicado_para', 'não informado')}."
            )

        return "\n".join(resposta)

    if contem(
        pergunta,
        [
            "quais produtos servem para minha reserva",
            "produtos servem para minha reserva",
            "produtos compatíveis com minha reserva",
            "produtos compativeis com minha reserva",
        ],
    ):
        return resposta_produtos_reserva(produtos_reserva)

    if contem(pergunta, ["tesouro selic serve", "tesouro serve", "tesouro selic combina"]):
        produto = encontrar_produto_por_nome(produtos, "tesouro selic")
        return resposta_produto_compativel_reserva(produto, "Tesouro Selic")

    if contem(
        pergunta,
        ["cdb liquidez diária serve", "cdb liquidez diaria serve", "cdb serve", "cdb combina"],
    ):
        produto = encontrar_produto_por_nome(produtos, "cdb")
        return resposta_produto_compativel_reserva(produto, "CDB Liquidez Diária")

    if contem(pergunta, ["fundo multimercado", "multimercado"]):
        produto = encontrar_produto_por_nome(produtos, "multimercado")

        if not produto:
            return "Não encontrei Fundo Multimercado na base de produtos disponível."

        return (
            f"O {produto.get('nome')} não deve ser prioridade para sua reserva de emergência. "
            f"Ele tem risco {formatar_texto_base(produto.get('risco'))}, liquidez "
            f"{formatar_texto_base(produto.get('liquidez'))} e não está marcado como adequado para reserva.\n\n"
            "Como você informou que não aceita risco, o mais indicado é priorizar produtos de baixo risco "
            "e com facilidade de resgate, como Tesouro Selic e CDB Liquidez Diária."
        )

    if "fundo de ações" in pergunta or "ações" in pergunta:
        return (
            "Para reserva de emergência, fundo de ações não é a opção mais adequada. "
            "Esse tipo de produto possui risco alto e rentabilidade variável. "
            "Como você informou que não aceita risco, o mais indicado é priorizar produtos de baixo risco "
            "e com facilidade de resgate."
        )

    if contem(
        pergunta,
        [
            "menor aporte mínimo",
            "menor aporte minimo",
            "menor valor de aporte",
            "menor aplicação mínima",
            "menor aplicacao minima",
        ],
    ):
        produto = min(produtos, key=lambda item: float(item.get("aporte_minimo", 0)))
        return (
            f"O produto com menor aporte mínimo é {produto.get('nome')}, "
            f"com aporte mínimo de {formatar_moeda(produto.get('aporte_minimo', 0))}."
        )

    if contem(pergunta, ["maior risco", "produto mais arriscado", "mais arriscado"]):
        ordem_risco = {"baixo": 1, "medio": 2, "médio": 2, "alto": 3}
        produto = max(
            produtos,
            key=lambda item: ordem_risco.get(normalizar_texto(item.get("risco")), 0),
        )
        return (
            f"O produto com maior risco na base é {produto.get('nome')}, "
            f"classificado como risco {formatar_texto_base(produto.get('risco'))}."
        )

    if contem(
        pergunta,
        ["liquidez diária", "liquidez diaria", "produtos com liquidez diária", "produtos com liquidez diaria"],
    ):
        produtos_liquidez_diaria = [
            produto
            for produto in produtos
            if formatar_texto_base(produto.get("liquidez")) == "diária"
        ]

        if not produtos_liquidez_diaria:
            return "Não encontrei produtos com liquidez diária na base disponível."

        resposta = ["Os produtos com liquidez diária na base são:"]

        for produto in produtos_liquidez_diaria:
            resposta.append(
                f"- {produto.get('nome')}: risco {formatar_texto_base(produto.get('risco'))}, "
                f"aporte mínimo de {formatar_moeda(produto.get('aporte_minimo', 0))}."
            )

        return "\n".join(resposta)

    if contem(
        pergunta,
        [
            "investir",
            "investimento",
            "produto",
            "onde deixar",
            "deixar o dinheiro",
            "cdb",
            "tesouro",
            "aplicar meu dinheiro",
        ],
    ):
        return resposta_produtos_reserva(produtos_reserva)

    return None


def resposta_produto_compativel_reserva(produto, nome_busca):
    """Monta resposta para produto adequado à reserva."""
    if not produto:
        return f"Não encontrei {nome_busca} na base de produtos disponível."

    return (
        f"Sim. O {produto.get('nome')} serve para sua reserva de emergência porque tem risco "
        f"{formatar_texto_base(produto.get('risco'))}, liquidez "
        f"{formatar_texto_base(produto.get('liquidez'))} e aporte mínimo de "
        f"{formatar_moeda(produto.get('aporte_minimo', 0))}.\n\n"
        "Ele está marcado na base como adequado para reserva de emergência."
    )


def resposta_produtos_reserva(produtos_reserva):
    """Monta resposta listando produtos compatíveis com reserva."""
    if not produtos_reserva:
        return (
            "Não encontrei produtos compatíveis com reserva de emergência na base disponível. "
            "Por segurança, não vou inventar uma recomendação."
        )

    resposta = [
        "Para sua reserva de emergência, os produtos mais compatíveis são:",
        "",
    ]

    for produto in produtos_reserva:
        resposta.append(
            f"- {produto.get('nome')}: risco {formatar_texto_base(produto.get('risco'))}, "
            f"liquidez {formatar_texto_base(produto.get('liquidez'))}, "
            f"aporte mínimo de {formatar_moeda(produto.get('aporte_minimo', 0))}."
        )

    resposta.append("")
    resposta.append(
        "Essas opções combinam melhor com seu perfil porque você informou que não aceita risco "
        "e precisa de facilidade de resgate."
    )

    resposta.append("")
    resposta.append(
        "A decisão final e qualquer aplicação devem ser feitas por você nos canais oficiais da instituição financeira."
    )

    return "\n".join(resposta)


def responder_perfil(pergunta, perfil):
    """Responde perguntas sobre dados cadastrais e perfil do cliente."""
    if contem(pergunta, ["meu nome", "qual é meu nome", "qual meu nome", "quem sou eu", "como eu me chamo"]):
        return (
            f"Seu nome é {perfil.get('nome', 'Não informado')}. "
            "Nesta simulação, você está conversando como o cliente fictício carregado na base de dados."
        )

    if contem(pergunta, ["meu perfil", "perfil de investidor", "qual é meu perfil", "qual meu perfil", "perfil investidor"]):
        aceita_risco = "aceita risco" if perfil.get("aceita_risco") else "não aceita risco"
        return (
            f"{perfil.get('nome', 'Cliente')}, seu perfil de investidor é "
            f"{perfil.get('perfil_investidor', 'Não informado')}. "
            f"Na base do projeto, também consta que você {aceita_risco}."
        )

    if contem(pergunta, ["quantos anos", "anos eu tenho", "minha idade"]):
        return f"Você tem {perfil.get('idade', 'Não informado')} anos, de acordo com os dados fictícios carregados na base."

    if contem(pergunta, ["profissão", "profissao", "meu trabalho", "minha ocupação", "minha ocupacao"]):
        return f"Sua profissão registrada é {perfil.get('profissao', 'Não informado')}."

    if contem(pergunta, ["renda", "renda mensal", "quanto eu ganho", "salário", "salario"]):
        return f"Sua renda mensal registrada é de {formatar_moeda(perfil.get('renda_mensal', 0))}."

    if contem(pergunta, ["aceito risco", "aceita risco", "tolerância a risco", "tolerancia a risco"]):
        if perfil.get("aceita_risco"):
            return "Sim. Na base do projeto consta que você aceita risco."
        return "Não. Na base do projeto consta que você não aceita risco."

    if contem(pergunta, ["objetivo principal", "meu objetivo", "objetivo financeiro"]):
        return f"Seu objetivo principal é {perfil.get('objetivo_principal', 'Não informado')}."

    if contem(pergunta, ["patrimônio", "patrimonio", "patrimônio total", "patrimonio total"]):
        return f"Seu patrimônio total registrado é de {formatar_moeda(perfil.get('patrimonio_total', 0))}."

    if contem(pergunta, ["preferência de liquidez", "preferencia de liquidez", "liquidez preferida", "minha liquidez"]):
        return f"Sua preferência de liquidez é {perfil.get('preferencia_liquidez', 'Não informado')}."

    if contem(
        pergunta,
        ["aportar por mês", "aportar por mes", "aporte mensal", "quanto quero aportar", "guardar por mês", "guardar por mes"],
    ):
        return f"Seu valor de aporte mensal desejado é de {formatar_moeda(perfil.get('valor_aporte_mensal_desejado', 0))}."

    if contem(pergunta, ["nível de conhecimento", "nivel de conhecimento", "conhecimento financeiro"]):
        return f"Seu nível de conhecimento financeiro registrado é {perfil.get('nivel_conhecimento_financeiro', 'Não informado')}."

    if contem(pergunta, ["frequência", "frequencia", "revisar minhas metas", "revisão de metas", "revisao de metas"]):
        return f"Sua frequência desejada para revisão das metas é {perfil.get('frequencia_revisao_metas', 'Não informado')}."

    if contem(pergunta, ["canal preferido", "canal de atendimento", "onde quero ser atendido"]):
        return f"Seu canal preferido de atendimento é {perfil.get('canal_preferido', 'Não informado')}."

    return None


def responder_metas(pergunta, perfil):
    """Responde perguntas sobre metas financeiras."""
    metas = perfil.get("metas", [])

    if contem(pergunta, ["quais são minhas metas", "minhas metas financeiras", "quais minhas metas", "listar minhas metas"]):
        if not metas:
            return "Não encontrei metas financeiras cadastradas na base do projeto."

        resposta = ["Suas metas financeiras cadastradas são:"]

        for meta in metas:
            resposta.append(
                f"- {meta.get('meta')}: valor necessário de {formatar_moeda(meta.get('valor_necessario', 0))}, "
                f"prazo {formatar_data_meta(meta.get('prazo'))}, "
                f"prioridade {formatar_texto_base(meta.get('prioridade', 'não informada'))} "
                f"e status {formatar_texto_base(meta.get('status', 'não informado'))}."
            )

        return "\n".join(resposta)

    if contem(pergunta, ["minha meta principal", "meta principal", "principal meta"]):
        if not metas:
            return "Não encontrei metas financeiras cadastradas na base do projeto."

        meta = metas[0]
        return (
            f"Sua meta principal cadastrada é {meta.get('meta')}. "
            f"O valor necessário é {formatar_moeda(meta.get('valor_necessario', 0))}, "
            f"com prazo em {formatar_data_meta(meta.get('prazo'))} "
            f"e prioridade {formatar_texto_base(meta.get('prioridade', 'não informada'))}."
        )

    if contem(pergunta, ["status da meta do apartamento", "status do apartamento"]):
        meta = encontrar_meta(perfil, "apartamento")

        if not meta:
            return "Não encontrei a meta da entrada do apartamento na base do projeto."

        return f"O status da meta de entrada do apartamento é {formatar_texto_base(meta.get('status', 'não informado'))}."

    if contem(pergunta, ["quanto preciso para completar minha reserva", "valor da minha reserva", "valor necessário da reserva", "valor necessario da reserva"]):
        reserva_atual, valor_meta, valor_faltante, _ = calcular_reserva(perfil)
        return (
            f"Para completar sua reserva de emergência, a meta cadastrada é de {formatar_moeda(valor_meta)}. "
            f"Como sua reserva atual é de {formatar_moeda(reserva_atual)}, ainda faltam {formatar_moeda(valor_faltante)}."
        )

    if contem(pergunta, ["prazo da minha reserva", "prazo da reserva"]):
        _, _, _, prazo = calcular_reserva(perfil)
        return f"O prazo cadastrado para sua reserva de emergência é {formatar_data_meta(prazo)}."

    if contem(pergunta, ["prioridade da minha reserva", "prioridade da reserva"]):
        meta = encontrar_meta(perfil, "reserva")

        if not meta:
            return "Não encontrei a meta de reserva de emergência na base do projeto."

        return f"A prioridade da sua meta de reserva de emergência é {formatar_texto_base(meta.get('prioridade', 'não informada'))}."

    if contem(pergunta, ["segunda meta", "segunda meta financeira", "outra meta"]):
        if len(metas) < 2:
            return "Não encontrei uma segunda meta financeira cadastrada na base do projeto."

        meta = metas[1]
        return (
            f"Sua segunda meta financeira é {meta.get('meta')}. "
            f"O valor necessário é {formatar_moeda(meta.get('valor_necessario', 0))}, "
            f"com prazo em {formatar_data_meta(meta.get('prazo'))} "
            f"e status {formatar_texto_base(meta.get('status', 'não informado'))}."
        )

    if contem(pergunta, ["quanto preciso para a entrada do apartamento", "valor da entrada do apartamento"]):
        meta = encontrar_meta(perfil, "apartamento")

        if not meta:
            return "Não encontrei a meta da entrada do apartamento na base do projeto."

        return (
            "Para a meta de entrada do apartamento, o valor necessário cadastrado é "
            f"{formatar_moeda(meta.get('valor_necessario', 0))}."
        )

    if contem(pergunta, ["prazo da entrada do apartamento", "prazo do apartamento"]):
        meta = encontrar_meta(perfil, "apartamento")

        if not meta:
            return "Não encontrei a meta da entrada do apartamento na base do projeto."

        return f"O prazo cadastrado para a entrada do apartamento é {formatar_data_meta(meta.get('prazo'))}."

    return None


def responder_transacoes(pergunta, transacoes):
    """Responde perguntas sobre movimentações financeiras."""
    if contem(pergunta, ["total de entradas", "minhas entradas", "quanto entrou"]):
        return resposta_total_por_tipo(transacoes, "entrada", "entradas")

    if contem(pergunta, ["total de saídas", "total de saidas", "minhas saídas", "minhas saidas", "quanto saiu"]):
        return resposta_total_por_tipo(transacoes, "saida", "saídas")

    if contem(pergunta, ["saldo aproximado", "saldo do período", "saldo do periodo"]):
        df = preparar_transacoes(transacoes)
        entradas = df[df["tipo"] == "entrada"]["valor"].sum()
        saidas = df[df["tipo"] == "saida"]["valor"].sum()
        saldo = entradas - saidas

        return (
            f"O saldo aproximado no período é de {formatar_moeda(saldo)}. "
            f"Foram {formatar_moeda(entradas)} em entradas e {formatar_moeda(saidas)} em saídas."
        )

    if contem(pergunta, ["principais categorias de gasto", "categorias de gasto", "maiores gastos por categoria"]):
        df = preparar_transacoes(transacoes)
        gastos_categoria = (
            df[df["tipo"] == "saida"]
            .groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=False)
        )

        if gastos_categoria.empty:
            return "Não encontrei gastos registrados por categoria."

        resposta = ["Suas principais categorias de gasto no período foram:"]

        for categoria, valor in gastos_categoria.items():
            resposta.append(f"- {formatar_texto_base(categoria)}: {formatar_moeda(valor)}")

        return "\n".join(resposta)

    categorias = {
        "moradia": ["quanto gastei com moradia", "gasto com moradia"],
        "alimentacao": ["quanto gastei com alimentação", "quanto gastei com alimentacao", "gasto com alimentação", "gasto com alimentacao"],
        "transporte": ["quanto gastei com transporte", "gasto com transporte"],
        "lazer": ["quanto gastei com lazer", "gasto com lazer"],
        "saude": ["quanto gastei com saúde", "quanto gastei com saude", "gasto com saúde", "gasto com saude"],
    }

    for categoria, termos in categorias.items():
        if contem(pergunta, termos):
            return resposta_gasto_categoria(transacoes, categoria)

    if contem(pergunta, ["quanto eu aportei", "aportei para a reserva", "aportes para reserva", "aporte para a reserva"]):
        if "meta_relacionada" not in transacoes.columns:
            return "Não encontrei a coluna de meta relacionada nas transações."

        aportes = transacoes[
            transacoes["meta_relacionada"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains("reserva")
        ]["valor"].sum()

        return f"No período analisado, você aportou {formatar_moeda(aportes)} para a reserva de emergência."

    if contem(pergunta, ["gastos são recorrentes", "gastos recorrentes", "despesas recorrentes"]):
        return resposta_transacoes_agrupadas(
            transacoes,
            filtro_coluna="recorrente",
            filtro_valor="sim",
            titulo="Os gastos recorrentes identificados foram:",
            vazio="Não encontrei gastos recorrentes no período analisado.",
        )

    if contem(pergunta, ["gastos não essenciais", "gastos nao essenciais", "não essenciais posso revisar", "nao essenciais posso revisar"]):
        df = preparar_transacoes(transacoes)
        nao_essenciais = df[(df["tipo"] == "saida") & (df["essencial"] == "nao")]

        if nao_essenciais.empty:
            return "Não encontrei gastos não essenciais no período analisado."

        total = nao_essenciais["valor"].sum()
        resposta = [
            f"Os gastos não essenciais somam {formatar_moeda(total)} no período analisado.",
            "Alguns itens que podem ser revisados são:",
        ]
        resposta.extend(linhas_transacoes_agrupadas(nao_essenciais))

        return "\n".join(resposta)

    if contem(pergunta, ["em qual mês eu gastei mais", "em qual mes eu gastei mais", "mês que gastei mais", "mes que gastei mais"]):
        df = preparar_transacoes(transacoes)
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        saidas = df[df["tipo"] == "saida"].copy()
        saidas["mes"] = saidas["data"].dt.to_period("M")
        gastos_mes = saidas.groupby("mes")["valor"].sum()

        if gastos_mes.empty:
            return "Não encontrei gastos mensais no período analisado."

        mes_maior = gastos_mes.idxmax()
        valor_maior = gastos_mes.max()

        return f"O mês com maior gasto foi {formatar_data_meta(str(mes_maior))}, com {formatar_moeda(valor_maior)} em saídas."

    if contem(pergunta, ["quanto gastei em outubro de 2025", "gastos de outubro de 2025", "gastei em outubro"]):
        df = preparar_transacoes(transacoes)
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        saidas_outubro = df[
            (df["tipo"] == "saida")
            & (df["data"].dt.year == 2025)
            & (df["data"].dt.month == 10)
        ]["valor"].sum()

        return f"Em outubro de 2025, você gastou {formatar_moeda(saidas_outubro)} em saídas."

    return None


def preparar_transacoes(transacoes):
    """Retorna uma cópia normalizada do DataFrame de transações."""
    colunas_obrigatorias = {"tipo", "valor"}

    if not colunas_obrigatorias.issubset(transacoes.columns):
        raise ValueError("O arquivo de transações não possui as colunas necessárias.")

    df = transacoes.copy()
    df["tipo"] = df["tipo"].astype(str).str.lower()

    for coluna in ["categoria", "essencial", "recorrente", "meta_relacionada"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("").astype(str).str.lower()

    return df


def resposta_total_por_tipo(transacoes, tipo, rotulo):
    df = preparar_transacoes(transacoes)
    total = df[df["tipo"] == tipo]["valor"].sum()
    return f"O total de {rotulo} registrado no período é de {formatar_moeda(total)}."


def resposta_gasto_categoria(transacoes, categoria):
    df = preparar_transacoes(transacoes)
    valor = df[(df["tipo"] == "saida") & (df["categoria"] == categoria)]["valor"].sum()
    return f"Você gastou {formatar_moeda(valor)} com {formatar_texto_base(categoria)} no período analisado."


def resposta_transacoes_agrupadas(transacoes, filtro_coluna, filtro_valor, titulo, vazio):
    df = preparar_transacoes(transacoes)
    filtradas = df[(df["tipo"] == "saida") & (df[filtro_coluna] == filtro_valor)]

    if filtradas.empty:
        return vazio

    resposta = [titulo]
    resposta.extend(linhas_transacoes_agrupadas(filtradas))

    return "\n".join(resposta)


def linhas_transacoes_agrupadas(transacoes_filtradas):
    agrupadas = (
        transacoes_filtradas.groupby(["descricao", "categoria"])["valor"]
        .sum()
        .sort_values(ascending=False)
    )

    return [
        f"- {descricao}: {formatar_moeda(valor)}, categoria {formatar_texto_base(categoria)}."
        for (descricao, categoria), valor in agrupadas.items()
    ]


def responder_reserva(pergunta, perfil):
    """Responde perguntas gerais sobre reserva de emergência."""
    if not contem(pergunta, ["reserva", "emergência", "emergencia", "quanto falta"]):
        return None

    reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)

    return (
        f"A reserva de emergência atual é de {formatar_moeda(reserva_atual)}. "
        f"A meta é chegar a {formatar_moeda(valor_meta)} até {formatar_data_meta(prazo)}. "
        f"Portanto, ainda faltam {formatar_moeda(valor_faltante)} para completar essa meta.\n\n"
        "Como você informou que não aceita risco, o ideal é priorizar alternativas de baixo risco "
        "e com facilidade de resgate."
    )


def responder_gastos_generico(pergunta, transacoes, valor_faltante):
    """Resposta geral sobre economia e análise de gastos."""
    if any(termo in pergunta for termo in ["guardar mais", "economizar", "gastos", "gastei", "despesas"]):
        if "essencial" not in transacoes.columns:
            return (
                "Uma forma de guardar mais dinheiro é revisar gastos não essenciais e recorrentes. "
                "No entanto, não encontrei a coluna de essencialidade nas transações para detalhar esses gastos."
            )

    df = transacoes.copy()

    nao_essenciais = df[
        (df["tipo"].astype(str).str.lower() == "saida")
        & (df["essencial"].astype(str).str.lower() == "nao")
    ]

    if nao_essenciais.empty:
        return (
            "Não encontrei gastos não essenciais no período analisado. "
            "Mesmo assim, vale acompanhar os gastos recorrentes e revisar o orçamento mensalmente."
        )

    total_nao_essencial = nao_essenciais["valor"].sum()

    nao_essenciais_agrupados = (
        nao_essenciais.groupby(["descricao", "categoria"])["valor"]
        .sum()
        .sort_values(ascending=False)
    )

    resposta = [
        "Uma forma de guardar mais dinheiro é revisar os gastos não essenciais.",
        "",
        f"No período analisado, esses gastos somam {formatar_moeda(total_nao_essencial)}.",
        "Alguns itens que podem ser avaliados são:",
    ]

    for (descricao, categoria), valor in nao_essenciais_agrupados.items():
        resposta.append(
            f"- {descricao}: {formatar_moeda(valor)}, "
            f"categoria {formatar_texto_base(categoria)}."
        )

    resposta.append("")
    resposta.append(
        "Esses gastos não precisam ser eliminados, mas podem ser ajustados. "
        f"Como ainda faltam {formatar_moeda(valor_faltante)} para completar sua reserva, "
        "parte dessa economia poderia ser direcionada para a meta."
    )

    return "\n".join(resposta)


# =============================================================================
# Orquestração das regras
# =============================================================================


def resposta_demonstrativa(
    pergunta,
    perfil,
    produtos,
    transacoes,
    atendimentos=None,
    usar_fallback=True,
):
    """Responde por regras simples ou devolve fallback quando permitido."""
    pergunta_normalizada = normalizar_texto(pergunta)

    if verificar_fora_do_escopo(pergunta_normalizada):
        return resposta_fora_do_escopo()

    reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)
    produtos_reserva = buscar_produtos_para_reserva(produtos)

    grupos_de_regras = [
        lambda: responder_historico(pergunta_normalizada, atendimentos),
        lambda: responder_seguranca(pergunta_normalizada),
        lambda: responder_produtos(pergunta_normalizada, produtos, produtos_reserva),
        lambda: responder_perfil(pergunta_normalizada, perfil),
        lambda: responder_metas(pergunta_normalizada, perfil),
        lambda: responder_transacoes(pergunta_normalizada, transacoes),
        lambda: responder_reserva(pergunta_normalizada, perfil),
        lambda: responder_gastos_generico(pergunta_normalizada, transacoes, valor_faltante),
    ]

    for regra in grupos_de_regras:
        resposta = regra()

        if resposta:
            return resposta

    if not usar_fallback:
        return None

    return resposta_fallback()


def verificar_fora_do_escopo(pergunta):
    """Identifica perguntas que não fazem parte da base do projeto."""
    pergunta_normalizada = normalizar_texto(pergunta)
    return any(termo in pergunta_normalizada for termo in TERMOS_FORA_DO_ESCOPO)


def responder(pergunta, perfil, produtos, transacoes, atendimentos):
    """Função principal chamada pela aplicação."""
    if verificar_fora_do_escopo(pergunta):
        return resposta_fora_do_escopo()

    resposta_regras = resposta_demonstrativa(
        pergunta,
        perfil,
        produtos,
        transacoes,
        atendimentos=atendimentos,
        usar_fallback=False,
    )

    if resposta_regras:
        return resposta_regras

    contexto = montar_contexto(perfil, produtos, transacoes, atendimentos)

    resposta_ollama = responder_com_ollama(pergunta, contexto)

    if resposta_ollama:
        return resposta_ollama

    resposta_modelo = responder_com_modelo(pergunta, contexto)

    if resposta_modelo:
        return resposta_modelo

    return resposta_demonstrativa(
        pergunta,
        perfil,
        produtos,
        transacoes,
        atendimentos=atendimentos,
        usar_fallback=True,
    )
