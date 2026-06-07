import os
from pathlib import Path

import streamlit as st

from agente import (
    carregar_dados,
    calcular_reserva,
    formatar_data_meta,
    formatar_moeda,
    responder,
)
from config import OLLAMA_MODEL


# =========================
# Constantes da interface
# =========================

APP_TITLE = "Norte Financeiro"
APP_DESCRIPTION = (
    "Agente financeiro consultivo para reserva de emergência, "
    "metas, gastos e orientações seguras."
)

ASSETS_DIR = Path("assets")
LOGO_PATH = ASSETS_DIR / "logo.png"
FAVICON_PATH = ASSETS_DIR / "favicon.png"

PERGUNTAS_RAPIDAS = [
    "Quanto falta para completar minha reserva?",
    "Onde posso deixar o dinheiro da reserva?",
    "Como posso guardar mais dinheiro?",
    "Vale a pena colocar minha reserva em fundo de ações?",
    "Pode aplicar R$ 1.000 no CDB para mim?",
    "Qual a previsão do tempo para amanhã?",
    "O que você acha do mercado internacional?",
]

MENSAGEM_INICIAL = (
    "Olá! Sou o Norte Financeiro. Posso ajudar você a acompanhar sua reserva de emergência, "
    "entender seus gastos e avaliar opções compatíveis com seu perfil."
)

MENSAGEM_REINICIO = (
    "Conversa reiniciada. Posso ajudar com reserva de emergência, "
    "gastos ou produtos compatíveis com o perfil do cliente."
)


# =========================
# Configuração da página
# =========================

def configurar_pagina():
    """Configura título, ícone e layout da aplicação."""
    page_icon = str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧭"

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=page_icon,
        layout="wide",
    )


# =========================
# Estado da sessão
# =========================

def inicializar_estado():
    """Inicializa as variáveis usadas na sessão do Streamlit."""
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": MENSAGEM_INICIAL,
            }
        ]

    if "pergunta_pendente" not in st.session_state:
        st.session_state.pergunta_pendente = None


def enviar_pergunta(pergunta):
    """Registra uma pergunta rápida para ser processada pelo chat."""
    st.session_state.pergunta_pendente = pergunta


def limpar_conversa():
    """Reinicia o histórico da conversa."""
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": MENSAGEM_REINICIO,
        }
    ]
    st.session_state.pergunta_pendente = None
    st.rerun()


# =========================
# Dados
# =========================

def carregar_base():
    """Carrega os dados do projeto e interrompe a aplicação em caso de erro."""
    try:
        return carregar_dados()
    except Exception as erro:
        st.error(f"Erro ao carregar os dados da pasta data/: {erro}")
        st.stop()


# =========================
# Componentes visuais
# =========================

def renderizar_cabecalho():
    """Renderiza logo, título e descrição."""
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)

    st.title(APP_TITLE)
    st.caption(APP_DESCRIPTION)


def renderizar_metricas(perfil, reserva_atual, valor_faltante, prazo):
    """Renderiza os indicadores principais do cliente."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Cliente", perfil.get("nome", "Não informado"))

    with col2:
        st.metric("Reserva atual", formatar_moeda(reserva_atual))

    with col3:
        st.metric("Falta para a meta", formatar_moeda(valor_faltante))

    with col4:
        st.metric("Prazo", formatar_data_meta(prazo))

    st.divider()


def renderizar_resumo_perfil(perfil):
    """Renderiza o resumo lateral do perfil financeiro."""
    st.subheader("Resumo do perfil")

    st.write(f"**Perfil:** {perfil.get('perfil_investidor', 'Não informado')}")
    st.write(f"**Aceita risco:** {'Sim' if perfil.get('aceita_risco') else 'Não'}")
    st.write(f"**Objetivo:** {perfil.get('objetivo_principal', 'Não informado')}")

    st.success(f"Modelo local configurado: {OLLAMA_MODEL}")

    if os.getenv("OPENAI_API_KEY"):
        st.caption("API externa também configurada")
    else:
        st.caption("Sem chave de API externa")


def renderizar_perguntas_rapidas():
    """Renderiza os botões de perguntas rápidas."""
    st.subheader("Perguntas rápidas")

    for pergunta in PERGUNTAS_RAPIDAS:
        st.button(
            pergunta,
            use_container_width=True,
            on_click=enviar_pergunta,
            args=(pergunta,),
        )


def renderizar_sidebar(perfil):
    """Renderiza a coluna lateral da aplicação."""
    renderizar_resumo_perfil(perfil)

    st.divider()

    renderizar_perguntas_rapidas()

    st.divider()

    st.button(
        "Limpar conversa",
        use_container_width=True,
        on_click=limpar_conversa,
    )


def renderizar_mensagens():
    """Renderiza o histórico de mensagens dentro do container do chat."""
    chat_container = st.container(height=520, border=True)

    with chat_container:
        for mensagem in st.session_state.mensagens:
            with st.chat_message(mensagem["role"]):
                st.markdown(mensagem["content"])


def obter_pergunta_do_usuario():
    """Obtém uma pergunta digitada ou selecionada nos botões rápidos."""
    pergunta_digitada = st.chat_input("Digite sua pergunta...")
    pergunta_final = pergunta_digitada or st.session_state.pergunta_pendente

    if pergunta_final:
        st.session_state.pergunta_pendente = None

    return pergunta_final


def processar_pergunta(pergunta, perfil, produtos, transacoes, atendimentos):
    """Envia a pergunta ao agente e atualiza o histórico do chat."""
    st.session_state.mensagens.append(
        {
            "role": "user",
            "content": pergunta,
        }
    )

    resposta = responder(
        pergunta,
        perfil,
        produtos,
        transacoes,
        atendimentos,
    )

    st.session_state.mensagens.append(
        {
            "role": "assistant",
            "content": resposta,
        }
    )

    st.rerun()


def renderizar_chat(perfil, produtos, transacoes, atendimentos):
    """Renderiza a área principal de chat."""
    st.subheader("Chat")

    renderizar_mensagens()

    pergunta = obter_pergunta_do_usuario()

    if pergunta:
        processar_pergunta(
            pergunta,
            perfil,
            produtos,
            transacoes,
            atendimentos,
        )


def renderizar_dados_carregados(perfil, produtos, transacoes, atendimentos):
    """Renderiza os dados carregados em abas para conferência."""
    st.divider()

    with st.expander("Ver dados carregados"):
        aba_perfil, aba_produtos, aba_transacoes, aba_atendimentos = st.tabs(
            ["Perfil", "Produtos", "Transações", "Atendimentos"]
        )

        with aba_perfil:
            st.json(perfil)

        with aba_produtos:
            st.json(produtos)

        with aba_transacoes:
            st.dataframe(transacoes, use_container_width=True)

        with aba_atendimentos:
            st.dataframe(atendimentos, use_container_width=True)


# =========================
# Aplicação principal
# =========================

def main():
    """Executa a aplicação Streamlit."""
    configurar_pagina()
    inicializar_estado()

    perfil, produtos, transacoes, atendimentos = carregar_base()

    reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)

    renderizar_cabecalho()
    renderizar_metricas(
        perfil=perfil,
        reserva_atual=reserva_atual,
        valor_faltante=valor_faltante,
        prazo=prazo,
    )

    col_chat, col_lateral = st.columns([2, 1])

    with col_chat:
        renderizar_chat(
            perfil,
            produtos,
            transacoes,
            atendimentos,
        )

    with col_lateral:
        renderizar_sidebar(perfil)

    renderizar_dados_carregados(
        perfil,
        produtos,
        transacoes,
        atendimentos,
    )


if __name__ == "__main__":
    main()
