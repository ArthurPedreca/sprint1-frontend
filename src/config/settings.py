"""Configurações globais da aplicação."""

from pathlib import Path

APP_TITLE = "Gestão de Ativos Industriais"
APP_ICON = "⚙️"
APP_DESCRIPTION = "Sprint 1 - Cadastro técnico e visualização de dados de sensores"

# Caminhos de dados
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_FILE = DATA_DIR / "equipamentos.json"

# Tipos de equipamentos suportados
TIPOS_EQUIPAMENTO = [
    "Motor Elétrico",
    "Bomba Centrífuga",
    "Compressor",
    "Ventilador / Exaustor",
    "Gerador",
    "Redutor",
    "Outro",
]

STATUS_OPCOES = ["Ativo", "Manutenção", "Inativo"]

# Limites para classificação semântica de leituras (cores no dashboard)
# Vibração: zonas ISO 10816 para máquinas médias rígidas (15-300 kW)
VIBRACAO_LIMITE_BOM = 2.8     # mm/s (zona A/B)
VIBRACAO_LIMITE_ALERTA = 4.5  # mm/s (zona B/C)
VIBRACAO_LIMITE_CRITICO = 7.1 # mm/s (zona C/D)

# Temperatura típica de carcaça de motor industrial
TEMPERATURA_LIMITE_BOM = 70      # °C
TEMPERATURA_LIMITE_ALERTA = 90   # °C

# Resolução do conversor analógico-digital simulado (12 bits)
ADC_RESOLUTION = 4095
