import os
import streamlit as st

from agente import (
    carregar_dados,
    calcular_reserva,
    formatar_moeda,
    responder,
)


st.set_page_config(
    page_title="Norte Financeiro",
    page_icon="🧭",
    layout="wide"
)


def enviar_pergunta(pergunta):
    st.session_state.pergunta_pendente = pergunta


st.title("🧭 Norte Financeiro")
st.caption("Agente financeiro consultivo para metas, gastos e orientações seguras.")

try:
    perfil, produtos, transacoes, atendimentos = carregar_dados()
except Exception as erro:
    st.error(f"Erro ao carregar os dados da pasta data/: {erro}")
    st.stop()

reserva_atual, valor_meta, valor_faltante, prazo = calcular_reserva(perfil)

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": (
                "Olá! Sou o Norte Financeiro. Posso ajudar você a acompanhar sua reserva de emergência, "
                "entender seus gastos e avaliar opções compatíveis com seu perfil."
            ),
        }
    ]

if "pergunta_pendente" not in st.session_state:
    st.session_state.pergunta_pendente = None


# =========================
# Resumo superior
# =========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Cliente", perfil.get("nome", "Não informado"))

with col2:
    st.metric("Reserva atual", formatar_moeda(reserva_atual))

with col3:
    st.metric("Falta para a meta", formatar_moeda(valor_faltante))

with col4:
    st.metric("Prazo", prazo)

st.divider()


# =========================
# Layout principal
# =========================

col_chat, col_lateral = st.columns([2, 1])

with col_lateral:
    st.subheader("Resumo do perfil")

    st.write(f"**Perfil:** {perfil.get('perfil_investidor', 'Não informado')}")
    st.write(f"**Aceita risco:** {'Sim' if perfil.get('aceita_risco') else 'Não'}")
    st.write(f"**Objetivo:** {perfil.get('objetivo_principal', 'Não informado')}")

    if os.getenv("OPENAI_API_KEY"):
        st.success("Modo com modelo conectado")
    else:
        st.info("Modo demonstrativo sem chave de API")

    st.divider()

    st.subheader("Perguntas rápidas")

    perguntas_rapidas = [
        "Quanto falta para completar minha reserva?",
        "Onde posso deixar o dinheiro da reserva?",
        "Como posso guardar mais dinheiro?",
        "Vale a pena colocar minha reserva em fundo de ações?",
        "Pode aplicar R$ 1.000 no CDB para mim?",
        "Qual a previsão do tempo para amanhã?",
    ]

    for pergunta in perguntas_rapidas:
        st.button(
            pergunta,
            use_container_width=True,
            on_click=enviar_pergunta,
            args=(pergunta,),
        )

    st.divider()

    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": (
                    "Conversa reiniciada. Posso ajudar com reserva de emergência, gastos ou produtos compatíveis com o perfil do cliente."
                ),
            }
        ]
        st.session_state.pergunta_pendente = None
        st.rerun()


with col_chat:
    st.subheader("Chat")

    chat_container = st.container(height=520, border=True)

    with chat_container:
        for mensagem in st.session_state.mensagens:
            with st.chat_message(mensagem["role"]):
                st.markdown(mensagem["content"])

    pergunta_digitada = st.chat_input("Digite sua pergunta...")

    pergunta_final = pergunta_digitada or st.session_state.pergunta_pendente

    if pergunta_final:
        st.session_state.pergunta_pendente = None

        st.session_state.mensagens.append(
            {"role": "user", "content": pergunta_final}
        )

        resposta = responder(
            pergunta_final,
            perfil,
            produtos,
            transacoes,
            atendimentos,
        )

        st.session_state.mensagens.append(
            {"role": "assistant", "content": resposta}
        )

        st.rerun()


st.divider()


# =========================
# Dados do projeto
# =========================

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