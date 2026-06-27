from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from agente import (
    carregar_dados,
    calcular_reserva,
    formatar_data_meta,
    formatar_moeda,
    responder,
)


# =========================
# Constantes da interface
# =========================

APP_TITLE = "Norte Financeiro"
APP_DESCRIPTION = (
    "Orientador financeiro para reserva de emergência, "
    "metas, gastos e escolhas mais seguras."
)

ASSETS_DIR = Path("assets")
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
# Configuração e estilo
# =========================

def configurar_pagina():
    """Configura título, ícone, layout e força a barra lateral aberta."""
    page_icon = str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧭"

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def aplicar_estilo():
    """CSS com cores fixas, independente do tema do navegador."""
    st.markdown(
        """
<style>
    :root {
        color-scheme: light !important;
        --azul-petroleo: #145C72;
        --azul-profundo: #0F4657;
        --azul-noite: #0B3442;
        --verde-menta: #DDF7EC;
        --verde-menta-2: #B9ECD7;
        --amarelo-suave: #FFF3C4;
        --fundo: #FFFDF7;
        --fundo-frio: #F4FBF8;
        --cartao: #FFFFFF;
        --texto: #16323D;
        --texto-suave: #647887;
        --borda: rgba(20, 92, 114, 0.15);
        --sombra: 0 18px 44px rgba(20, 92, 114, 0.11);
    }

    *, *::before, *::after {
        box-sizing: border-box;
        color-scheme: light !important;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        height: 100vh !important;
        min-height: 100vh !important;
        overflow: hidden !important;
        background: #FFFDF7 !important;
        color: var(--texto) !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(221, 247, 236, 0.95), transparent 30%),
            radial-gradient(circle at top right, rgba(255, 243, 196, 0.90), transparent 32%),
            linear-gradient(135deg, var(--fundo) 0%, var(--fundo-frio) 100%) !important;
    }

    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Mantém a lateral aberta e remove os controles de recolher/reabrir. */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarHeader"] button,
    button[aria-label="Close sidebar"],
    button[title="Close sidebar"] {
        display: none !important;
        visibility: hidden !important;
    }

    .block-container {
        max-width: 100% !important;
        width: 100% !important;
        height: 100vh !important;
        padding: 0.85rem 1rem 0.75rem 1rem !important;
        margin: 0 !important;
        overflow: hidden !important;
    }

    h1, h2, h3, p, span, label, div, button, input, textarea, pre {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }

    /* Sidebar nativa fixa, com cor própria. */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--azul-petroleo) 0%, var(--azul-profundo) 74%, var(--azul-noite) 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.18) !important;
        min-width: 300px !important;
        max-width: 300px !important;
        width: 300px !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        background: transparent !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: visible !important;
        padding: 0.2rem 0.85rem 0.75rem 0.85rem !important;
        gap: 0.6rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    .sidebar-brand {
    margin-top: -1rem;
    margin-bottom: 0.1rem;
    transform: translateY(-30px);
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) {
    margin-top: -1.5rem !important;
    }

    .sidebar-logo {
        width: 34px;
        height: 34px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--amarelo-suave), var(--verde-menta));
        color: var(--azul-petroleo) !important;
        font-size: 1rem;
        margin-top: 0;
        margin-bottom: 0.42rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
    }

    .sidebar-title {
        font-size: 1.08rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        line-height: 1.18;
        margin-top: 0;
        margin-bottom: 0.28rem;
        color: #FFFFFF !important;
    }

    .sidebar-subtitle {
        font-size: 0.74rem;
        line-height: 1.32;
        color: rgba(255, 255, 255, 0.78) !important;
        margin-top: 0;
        margin-bottom: 0;
        max-width: 260px;
    }

    .sidebar-section-title {
        margin-top: 0.15rem;
        margin-bottom: 0.12rem;
        font-size: 0.62rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(255, 255, 255, 0.70) !important;
    }

    .sidebar-quick-title {
    margin-top: -12px !important;
    margin-bottom: 2px !important;
    }

    .sidebar-summary {
        margin-top: 0.18rem;
        padding: 0.48rem 0.58rem;
        border: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.09);
        font-size: 0.68rem;
        line-height: 1.2;
        color: rgba(255, 255, 255, 0.82) !important;
    }

    .sidebar-summary b {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        height: 54px !important;
        min-height: 54px !important;
        max-height: 54px !important;
        padding: 0.34rem 0.55rem !important;
        border-radius: 13px !important;
        border: 1px solid rgba(255, 255, 255, 0.20) !important;
        background: rgba(255, 255, 255, 0.11) !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
        font-weight: 650 !important;
        font-size: 0.82rem !important;
        line-height: 1.18 !important;
        white-space: normal !important;
        text-align: center !important;
    }

    [data-testid="stSidebar"] div.stButton > button:hover,
    [data-testid="stSidebar"] div.stButton > button:focus {
        background: rgba(255, 255, 255, 0.20) !important;
        border-color: rgba(255, 255, 255, 0.34) !important;
        color: #FFFFFF !important;
    }

    /* Conteúdo principal */
    .hero-card {
    width: 100%;
    border: 1px solid var(--borda);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.86);
    box-shadow: var(--sombra);
    padding: 0.72rem 1rem;
    margin-bottom: 0.42rem;
    }

    .pill {
    display: inline-flex;
    align-items: center;
    gap: 0.28rem;
    padding: 0.24rem 0.58rem;
    border-radius: 999px;
    background: var(--verde-menta);
    color: var(--azul-petroleo) !important;
    font-size: 0.68rem;
    font-weight: 900;
    margin-bottom: 0.36rem;
    }

    .hero-title {
    font-size: clamp(1.45rem, 2.2vw, 2.15rem);
    line-height: 1.02;
    margin: 0 0 0.28rem 0;
    font-weight: 950;
    letter-spacing: -0.06em;
    color: var(--texto) !important;
    }

    .hero-description {
    font-size: 0.84rem;
    color: var(--texto-suave) !important;
    margin: 0;
    }

    .metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.42rem;
    margin-bottom: 0.34rem;
    }

    .metric-card {
    min-height: 62px;
    border: 1px solid var(--borda);
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.90);
    padding: 0.45rem 0.62rem;
    box-shadow: 0 8px 18px rgba(20, 92, 114, 0.07);
    }

    .metric-label {
    font-size: 0.56rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--texto-suave) !important;
    margin-bottom: 0.18rem;
    }

    .metric-value {
        font-size: 0.92rem;
        line-height: 1.05;
        font-weight: 950;
        letter-spacing: -0.035em;
        color: var(--texto) !important;
        margin-bottom: 0.12rem;
    }

    .metric-caption {
        font-size: 0.62rem;
        font-weight: 800;
        color: var(--azul-petroleo) !important;
    }

    .chat-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin: 0.12rem 0 0.42rem 0;
    }

    .chat-title {
        font-size: 1.03rem;
        font-weight: 950;
        letter-spacing: -0.045em;
        color: var(--texto) !important;
    }

    .demo-badge {
        border-radius: 999px;
        padding: 0.36rem 0.78rem;
        background: var(--amarelo-suave);
        color: var(--azul-petroleo) !important;
        font-size: 0.75rem;
        font-weight: 900;
    }

    /* Formulário fixo abaixo do chat. */
    div[data-testid="stForm"] {
        border: 1px solid var(--borda) !important;
        border-radius: 4px !important;
        background: rgba(255, 255, 255, 0.88) !important;
        padding: 0.55rem 0.62rem !important;
        margin-top: 0.54rem !important;
        box-shadow: 0 12px 30px rgba(20, 92, 114, 0.08) !important;
    }

    div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
        align-items: center !important;
    }

    div[data-testid="stForm"] input {
        height: 42px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(20, 92, 114, 0.16) !important;
        background: #FFFFFF !important;
        color: var(--texto) !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
    }

    div[data-testid="stForm"] input::placeholder {
        color: #9AAAB3 !important;
        opacity: 1 !important;
    }

    div[data-testid="stForm"] div.stButton > button {
        width: 100% !important;
        height: 42px !important;
        border-radius: 4px !important;
        border: 1px solid var(--azul-petroleo) !important;
        background: var(--azul-petroleo) !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        box-shadow: none !important;
    }

    div[data-testid="stForm"] div.stButton > button:hover,
    div[data-testid="stForm"] div.stButton > button:focus {
        background: var(--azul-profundo) !important;
        border-color: var(--azul-profundo) !important;
        color: #FFFFFF !important;
    }

    .stMarkdown, .stTextInput, .stButton {
        margin-bottom: 0 !important;
    }

    /* Scrollbar discreta, mas fixa. */
    ::-webkit-scrollbar {
        width: 9px;
        height: 9px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(20, 92, 114, 0.07);
        border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(20, 92, 114, 0.35);
        border-radius: 999px;
    }

    @media (max-width: 1150px) {
        .metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .hero-card {
            padding: 1rem 1.15rem;
        }
        .hero-title {
            font-size: 2.05rem;
        }
    }
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Estado da sessão
# =========================

def inicializar_estado():
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {"role": "assistant", "content": MENSAGEM_INICIAL}
        ]

    if "pergunta_pendente" not in st.session_state:
        st.session_state.pergunta_pendente = None

    if "processando" not in st.session_state:
        st.session_state.processando = False

    if "ultima_pergunta" not in st.session_state:
        st.session_state.ultima_pergunta = None


def enviar_pergunta(pergunta):
    st.session_state.pergunta_pendente = pergunta


def limpar_conversa():
    st.session_state.mensagens = [
        {"role": "assistant", "content": MENSAGEM_REINICIO}
    ]
    st.session_state.pergunta_pendente = None


# =========================
# Dados
# =========================

def carregar_base():
    try:
        return carregar_dados()
    except Exception as erro:
        st.error(f"Erro ao carregar os dados da pasta data/: {erro}")
        st.stop()


# =========================
# HTML utilitário
# =========================

def moeda_sem_escape(valor):
    """Remove escape do cifrão usado para Markdown, pois aqui renderizamos HTML."""
    return formatar_moeda(valor).replace("\\$", "$")


def metric_card(label, value, caption):
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div>'
        f'<div class="metric-caption">{escape(caption)}</div>'
        '</div>'
    )


def renderizar_chat_com_scroll():
    """
    Renderiza o chat inteiro dentro de components.html().

    HTML e JS ficam no mesmo iframe — sem cruzar fronteiras de documento,
    sem depender de window.parent, sem risco de sanitização pelo Streamlit.
    O MutationObserver dispara assim que todas as mensagens estão no DOM,
    independentemente do tempo de reflow.

    Altura: o iframe comunica sua posição ao pai via postMessage, e o pai
    responde com a altura disponível restante. Enquanto essa troca não ocorre
    (ou em navegadores sem suporte), usa-se CHAT_HEIGHT_INITIAL como padrão.

    Nota: st.markdown() remove tags <script> via DOMPurify antes de
    montar o HTML, então JS embutido em st.markdown nunca executa.
    components.html() é o único caminho garantido para rodar JavaScript.
    """
    linhas = []
    for mensagem in st.session_state.mensagens:
        role = mensagem.get("role", "assistant")
        content = escape(mensagem.get("content", ""))
        avatar = "🧭" if role == "assistant" else "👤"
        css_role = "assistant" if role == "assistant" else "user"
        linhas.append(
            f'<div class="message-row {css_role}">'
            f'<div class="avatar">{avatar}</div>'
            f'<div class="message-bubble">{content}</div>'
            '</div>'
        )

    msg_count = len(st.session_state.mensagens)
    mensagens_html = "".join(linhas)

    # Altura inicial do iframe (px). Reduzida em relação à versão anterior
    # pois o formulário agora ocupa espaço real abaixo do slot.
    # Anatomia do layout (valores aproximados para 900px de viewport):
    #   padding página   ≈  28px
    #   hero-card        ≈  90px
    #   metric-grid      ≈  80px
    #   chat-header-row  ≈  46px
    #   formulário       ≈  70px
    #   gaps/margens     ≈  30px
    #                    ────────
    #   total ocupado    ≈ 344px  →  sobra ≈ 556px para o chat
    # Usamos 380 como valor conservador que funciona em telas menores (~768px).
    CHAT_HEIGHT_INITIAL = 340

    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    background: transparent;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    overflow: hidden;
    width: 100%;
    height: 100%;
  }}

  .chat-box {{
    width: 100%;
    height: 100%;
    overflow-y: auto;
    border: 1px solid rgba(20, 92, 114, 0.15);
    border-radius: 25px;
    background: rgba(255, 255, 255, 0.72);
    padding: 1.05rem;
    scroll-behavior: smooth;
  }}

  .message-row {{
    display: flex;
    gap: 0.62rem;
    align-items: flex-start;
    margin-bottom: 0.68rem;
  }}

  .message-row.user {{ flex-direction: row-reverse; }}

  .avatar {{
    width: 31px;
    height: 31px;
    min-width: 31px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #DDF7EC;
    box-shadow: 0 10px 20px rgba(20, 92, 114, 0.08);
    font-size: 0.9rem;
    flex-shrink: 0;
  }}

  .message-bubble {{
    max-width: min(76%, 760px);
    border: 1px solid rgba(20, 92, 114, 0.12);
    border-radius: 17px;
    padding: 0.76rem 0.92rem;
    background: #FFFFFF;
    color: #2A4652;
    font-size: 0.9rem;
    line-height: 1.52;
    white-space: pre-wrap;
  }}

  .message-row.user .message-bubble {{
    background: #DDF7EC;
    color: #103C49;
    border-color: rgba(20, 92, 114, 0.16);
  }}

  ::-webkit-scrollbar {{ width: 9px; }}
  ::-webkit-scrollbar-track {{
    background: rgba(20, 92, 114, 0.07);
    border-radius: 999px;
  }}
  ::-webkit-scrollbar-thumb {{
    background: rgba(20, 92, 114, 0.35);
    border-radius: 999px;
  }}
</style>
</head>
<body>
  <div class="chat-box" id="chat-box">
    {mensagens_html}
    <div id="chat-bottom" style="height:1px;"></div>
  </div>

<script>
(function() {{
  var EXPECTED = {msg_count};

  /* ── Altura adaptativa ───────────────────────────────────────────
     O Streamlit define uma altura fixa para o iframe via o parâmetro
     height= de components.html(). Não conseguimos alterar esse valor
     de dentro do iframe, mas podemos ajustar o .chat-box para usar
     exatamente o espaço que o iframe nos deu (window.innerHeight).

     Adicionalmente, pedimos ao documento pai (via postMessage) a
     posição do iframe na página para calcular o espaço real abaixo
     dele. O pai responde com {{ type: 'CHAT_HEIGHT', value: N }}.
     Se a resposta chegar, redimensionamos o iframe via resizeObserver;
     caso contrário, window.innerHeight já é uma boa aproximação.    */

  function ajustarAltura(h) {{
    var box = document.getElementById('chat-box');
    if (box) box.style.height = (h || window.innerHeight) + 'px';
  }}

  // Aplica a altura inicial (= o que o Streamlit nos deu)
  ajustarAltura(window.innerHeight);

  // Solicita ao pai a altura disponível real
  try {{
    window.parent.postMessage({{ type: 'NORTE_ASK_HEIGHT' }}, '*');
  }} catch(e) {{}}

  // Escuta a resposta do pai
  window.addEventListener('message', function(evt) {{
    if (evt.data && evt.data.type === 'NORTE_REPLY_HEIGHT') {{
      ajustarAltura(evt.data.value);
      scrollToBottom();
    }}
  }});

  /* ── Scroll automático ───────────────────────────────────────────*/
  function scrollToBottom() {{
    var box = document.getElementById('chat-box');
    if (box) box.scrollTop = box.scrollHeight;
  }}

  function domCompleto() {{
    var box = document.getElementById('chat-box');
    if (!box) return false;
    return box.querySelectorAll('.message-row').length >= EXPECTED;
  }}

  if (domCompleto()) {{
    scrollToBottom();
    return;
  }}

  var observer = new MutationObserver(function(_, obs) {{
    if (domCompleto()) {{
      obs.disconnect();
      scrollToBottom();
    }}
  }});

  observer.observe(document.body, {{ childList: true, subtree: true }});

  setTimeout(function() {{
    observer.disconnect();
    scrollToBottom();
  }}, 5000);
}})();
</script>
</body>
</html>"""

    components.html(html, height=CHAT_HEIGHT_INITIAL, scrolling=False)


def injetar_receptor_altura():
    """
    Injeta um script no documento pai (via iframe height=0) que:
    1. Escuta a mensagem NORTE_ASK_HEIGHT enviada pelo iframe do chat.
    2. Calcula o espaço disponível abaixo do iframe na página.
    3. Responde com NORTE_REPLY_HEIGHT para que o chat-box se ajuste.

    Executado uma única vez por sessão via st.session_state.
    """
    if st.session_state.get("_receptor_altura_injetado"):
        return

    st.session_state["_receptor_altura_injetado"] = True

    components.html(
        """
<script>
(function() {
  // Evita registrar múltiplos listeners se o Streamlit re-executar este bloco
  if (window.__norteReceptorAtivo) return;
  window.__norteReceptorAtivo = true;

  window.addEventListener('message', function(evt) {
    if (!evt.data || evt.data.type !== 'NORTE_ASK_HEIGHT') return;

    var origem = evt.source;
    if (!origem) return;

    // Encontra o iframe que enviou a mensagem
    var iframes = document.querySelectorAll('iframe');
    var alvo = null;
    for (var i = 0; i < iframes.length; i++) {
      try {
        if (iframes[i].contentWindow === origem) {
          alvo = iframes[i];
          break;
        }
      } catch(e) {}
    }

    // Calcula o espaço disponível abaixo do iframe
    var alturaDisponivel = 380; // fallback seguro
    if (alvo) {
      var rect = alvo.getBoundingClientRect();
      var viewportH = window.innerHeight;
      // Margem de 80px para o formulário + gaps
      alturaDisponivel = Math.max(200, viewportH - rect.top - 130);
    }

    try {
      origem.postMessage({ type: 'NORTE_REPLY_HEIGHT', value: alturaDisponivel }, '*');
    } catch(e) {}
  });
})();
</script>
        """,
        height=0,
        scrolling=False,
    )


def renderizar_sidebar(perfil):
    with st.sidebar:
        st.markdown(
            """
<div class="sidebar-brand">
    <div class="sidebar-logo">🧭</div>
    <div class="sidebar-title">Norte Financeiro</div>
    <div class="sidebar-subtitle">Converse, acompanhe metas e entenda seus gastos com mais clareza.</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.button(
            "+ Nova conversa",
            use_container_width=True,
            on_click=limpar_conversa,
        )

        st.markdown(
            '<div class="sidebar-section-title sidebar-quick-title">Perguntas rápidas</div>',
            unsafe_allow_html=True,
        )

        for pergunta in PERGUNTAS_RAPIDAS:
            st.button(
                pergunta,
                use_container_width=True,
                on_click=enviar_pergunta,
                args=(pergunta,),
            )

        st.markdown(
            f'''
<div class="sidebar-section-title">Resumo</div>
<div class="sidebar-summary">
    <b>Perfil:</b> {escape(str(perfil.get('perfil_investidor', 'Não informado')))}<br>
    <b>Aceita risco:</b> {'Sim' if perfil.get('aceita_risco') else 'Não'}
</div>
            ''',
            unsafe_allow_html=True,
        )


def renderizar_area_principal(perfil, reserva_atual, valor_faltante, prazo):
    """
    Renderiza hero, métricas e cabeçalho do chat.
    Reserva um st.empty() para o iframe do chat e o retorna —
    o formulário será renderizado logo depois, e só então o slot
    será preenchido com o chat. Isso garante que o formulário
    nunca seja cortado pelo overflow: hidden do .block-container.
    """
    st.markdown(
        f'''
<div class="hero-card">
    <div class="pill">🧭 Seu norte para decisões financeiras</div>
    <div class="hero-title">{escape(APP_TITLE)}</div>
    <p class="hero-description">{escape(APP_DESCRIPTION)}</p>
</div>

<div class="metric-grid">
    {metric_card('Cliente', str(perfil.get('nome', 'Não informado')), 'Dados da simulação')}
    {metric_card('Reserva atual', moeda_sem_escape(reserva_atual), 'Valor já guardado')}
    {metric_card('Falta para a meta', moeda_sem_escape(valor_faltante), 'Caminho restante')}
    {metric_card('Prazo', formatar_data_meta(prazo), 'Meta cadastrada')}
</div>

<div class="chat-header-row">
    <div class="chat-title">Conversa</div>
</div>
        ''',
        unsafe_allow_html=True,
    )

    # Reserva a posição do chat no DOM agora,
    # mas deixa o preenchimento para depois do formulário.
    chat_slot = st.empty()
    return chat_slot


def obter_pergunta_do_usuario():
    pergunta_final = st.session_state.pergunta_pendente

    if pergunta_final:
        st.session_state.pergunta_pendente = None
        return pergunta_final

    with st.form("chat_form", clear_on_submit=True):
        col_input, col_botao = st.columns([12, 1])
        with col_input:
            pergunta_digitada = st.text_input(
                "Pergunta",
                placeholder="Digite sua pergunta...",
                label_visibility="collapsed",
            )
        with col_botao:
            enviar = st.form_submit_button("➜")

    if enviar and pergunta_digitada.strip():
        return pergunta_digitada.strip()

    return None


# =========================
# Aplicação principal
# =========================

def main():
    configurar_pagina()
    aplicar_estilo()
    inicializar_estado()

    perfil, produtos, transacoes, atendimentos = carregar_base()
    reserva_atual, _, valor_faltante, prazo = calcular_reserva(perfil)

    renderizar_sidebar(perfil)

    injetar_receptor_altura()

    # 1. Renderiza hero/métricas e reserva o slot do chat no DOM
    chat_slot = renderizar_area_principal(
        perfil,
        reserva_atual,
        valor_faltante,
        prazo,
    )

    # 2. Formulário renderiza ANTES do chat no código Python,
    #    mas ocupa a posição correta na tela (abaixo do slot reservado).
    #    Isso impede que o overflow: hidden corte o formulário.
    pergunta = obter_pergunta_do_usuario()

    # 3. Agora preenche o slot com o iframe do chat
    with chat_slot:
        renderizar_chat_com_scroll()

    if pergunta:
        st.session_state.mensagens.append(
            {
                "role": "user",
                "content": pergunta,
            }
        )
        st.session_state.processando = True
        st.session_state.ultima_pergunta = pergunta
        st.rerun()

    if st.session_state.get("processando"):
        resposta = responder(
            st.session_state.ultima_pergunta,
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

        st.session_state.processando = False
        st.rerun()


if __name__ == "__main__":
    main()