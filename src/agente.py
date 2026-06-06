import json
import pandas as pd

from config import (
    PERFIL_PATH,
    PRODUTOS_PATH,
    TRANSACOES_PATH,
    ATENDIMENTOS_PATH,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def formatar_moeda(valor):
    """Formata valores no padrão brasileiro, escapando o cifrão para o Streamlit."""
    try:
        valor_formatado = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return valor_formatado.replace("$", "\\$")
    except Exception:
        return "R\\$ 0,00"


def carregar_json(caminho):
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

    meta_reserva = None

    for meta in perfil.get("metas", []):
        nome_meta = meta.get("meta", "").lower()

        if "reserva" in nome_meta:
            meta_reserva = meta
            break

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
        risco = str(produto.get("risco", "")).lower()
        liquidez = str(produto.get("liquidez", "")).lower()
        indicado_para = str(produto.get("indicado_para", "")).lower()
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
            resumo.append(f"- {categoria}: {formatar_moeda(valor)}")

    return "\n".join(resumo)


def montar_contexto(perfil, produtos, transacoes, atendimentos):
    """Monta um resumo organizado dos dados disponíveis."""
    reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)
    produtos_reserva = buscar_produtos_para_reserva(produtos)

    contexto = {
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


def system_prompt():
    """Instruções gerais do Norte Financeiro."""
    return """
Você é o Norte Financeiro, um agente financeiro consultivo.

Seu objetivo é ajudar o cliente a acompanhar metas, entender gastos e receber orientações seguras com base nos dados disponíveis.

Regras:
1. Use apenas os dados fornecidos no contexto.
2. Não invente produtos, taxas, saldos, prazos ou informações do cliente.
3. Não prometa ganhos futuros.
4. Se não houver dados suficientes, diga isso com clareza.
5. Se o cliente não aceita risco, não sugira produtos de alto risco.
6. Para reserva de emergência, priorize produtos de baixo risco e com facilidade de resgate.
7. Explique sempre o motivo da sugestão.
8. Não realize aplicações, resgates, transferências ou qualquer movimentação financeira.
9. Use linguagem clara, educada e acessível.
10. Em situações complexas, recomende atendimento humano.

Responda sempre em português do Brasil.
"""


def responder_com_modelo(pergunta, contexto):
    """
    Tenta responder usando uma API externa, caso a chave esteja configurada.
    Se não houver chave, retorna None e o app usa o modo demonstrativo.
    """
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
"""
        )

        return resposta.output_text

    except Exception as erro:
        return (
            "Não consegui consultar o modelo neste momento. "
            f"Detalhe técnico: {erro}"
        )


def resposta_demonstrativa(pergunta, perfil, produtos, transacoes):
    """
    Responde com regras simples quando não há chave de API configurada.
    Isso permite que o protótipo funcione mesmo em ambiente local.
    """
    pergunta = pergunta.lower()

    reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)
    produtos_reserva = buscar_produtos_para_reserva(produtos)

    if any(termo in pergunta for termo in ["senha", "cpf", "dados de outro cliente"]):
        return (
            "Não posso compartilhar senhas, documentos ou informações sensíveis. "
            "Posso ajudar apenas com orientações financeiras baseadas nos dados permitidos do projeto."
        )

    if any(termo in pergunta for termo in ["previsão do tempo", "clima", "futebol", "receita de bolo"]):
        return (
            "Eu sou especializado em organização financeira, metas, gastos e produtos financeiros disponíveis na base do projeto. "
            "Posso ajudar com algo relacionado às suas finanças?"
        )

    if any(termo in pergunta for termo in ["aplicar", "resgatar", "transferir", "transfere"]):
        return (
            "Não posso realizar aplicações, resgates ou transferências. "
            "Posso apenas explicar se um produto combina com seu perfil e sua meta. "
            "A decisão e a execução devem ser feitas por você nos canais oficiais da instituição financeira."
        )

    if "fundo de ações" in pergunta or "ações" in pergunta:
        return (
            "Para reserva de emergência, fundo de ações não é a opção mais adequada. "
            "Esse tipo de produto possui risco alto e rentabilidade variável. "
            "Como o cliente informou que não aceita risco, o mais indicado é priorizar produtos de baixo risco e com facilidade de resgate."
        )

    # Importante: esta regra vem antes da regra geral sobre reserva.
    # Assim, perguntas como "Onde posso deixar o dinheiro da reserva?"
    # são tratadas como pedido de orientação sobre produto.
    if any(
        termo in pergunta
        for termo in [
            "investir",
            "investimento",
            "produto",
            "onde deixar",
            "deixar o dinheiro",
            "cdb",
            "tesouro",
            "aplicar meu dinheiro",
        ]
    ):
        if not produtos_reserva:
            return (
                "Não encontrei produtos compatíveis com reserva de emergência na base disponível. "
                "Por segurança, não vou inventar uma recomendação."
            )

        resposta = [
            "Para reserva de emergência, o mais importante é segurança e facilidade de resgate.",
            "",
            "Com base nos produtos disponíveis, as opções mais compatíveis são:",
        ]

        for produto in produtos_reserva:
            resposta.append(
                f"- {produto.get('nome')}: risco {produto.get('risco')}, "
                f"aporte mínimo de {formatar_moeda(produto.get('aporte_minimo', 0))}, "
                f"indicado para {produto.get('indicado_para')}."
            )

        resposta.append("")
        resposta.append(
            "Essas opções combinam melhor com o perfil do cliente porque ele informou que não aceita risco."
        )

        return "\n".join(resposta)

    if any(termo in pergunta for termo in ["reserva", "emergência", "emergencia", "quanto falta"]):
        return (
            f"A reserva de emergência atual é de {formatar_moeda(reserva_atual)}. "
            f"A meta é chegar a {formatar_moeda(valor_meta)} até {prazo}. "
            f"Portanto, ainda faltam {formatar_moeda(valor_faltante)} para completar essa meta.\n\n"
            "Como o cliente informou que não aceita risco, o ideal é priorizar alternativas de baixo risco e com facilidade de resgate."
        )

    if any(termo in pergunta for termo in ["gastos", "gastei", "guardar mais", "economizar", "despesas"]):
        return (
            "Uma forma de guardar mais dinheiro é observar os gastos não essenciais e recorrentes. "
            "Esses gastos não precisam ser eliminados, mas podem ser ajustados.\n\n"
            f"Resumo das transações:\n{resumir_transacoes(transacoes)}\n\n"
            f"Como ainda faltam {formatar_moeda(valor_faltante)} para completar a reserva de emergência, pequenos ajustes mensais podem ajudar bastante."
        )

    return (
        "Posso ajudar com acompanhamento da reserva de emergência, análise de gastos e sugestões de produtos compatíveis com o perfil do cliente.\n\n"
        "Exemplos de perguntas:\n"
        "- Quanto falta para completar minha reserva?\n"
        "- Onde posso deixar o dinheiro da reserva?\n"
        "- Como posso guardar mais dinheiro?\n"
        "- Fundo de ações combina com minha reserva?"
    )


def responder(pergunta, perfil, produtos, transacoes, atendimentos):
    """Função principal chamada pela aplicação."""
    contexto = montar_contexto(perfil, produtos, transacoes, atendimentos)

    resposta_modelo = responder_com_modelo(pergunta, contexto)

    if resposta_modelo:
        return resposta_modelo

    return resposta_demonstrativa(pergunta, perfil, produtos, transacoes)