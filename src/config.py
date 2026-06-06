from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PERFIL_PATH = DATA_DIR / "perfil_investidor.json"
PRODUTOS_PATH = DATA_DIR / "produtos_financeiros.json"
TRANSACOES_PATH = DATA_DIR / "transacoes.csv"
ATENDIMENTOS_PATH = DATA_DIR / "historico_atendimento.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")