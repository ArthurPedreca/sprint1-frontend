# Sistema de Gestão de Ativos Industriais

Aplicação web para cadastro técnico de equipamentos industriais (motores, bombas, compressores, ventiladores) e visualização das leituras dos seus sensores em tempo real. Construída com Streamlit.

O sistema mantém uma ficha técnica completa de cada ativo (potência, tensão, corrente, RPM, frequência, localização, status operacional) e oferece um painel de monitoramento que converte os sinais brutos do ADC em unidades de engenharia (V, A, RPM, °C, mm/s), aplicando cores semânticas baseadas em normas como a ISO 10816 para vibração.

---

## Funcionalidades

- **Consulta de equipamentos** — datatable com filtros por TAG, modelo, fabricante, tipo e status, mais cards de resumo (total, ativos, em manutenção, inativos).
- **Cadastro técnico** — formulário completo com validação inline, TAG única, e suporte a edição da ficha existente.
- **Exclusão protegida** — confirmação explícita antes de remover qualquer registro.
- **Painel de sensores** — leituras de tensão, corrente, rotação, temperatura e vibração, com:
  - Conversão automática do sinal bruto (ADC 12-bit, 0–4095) para unidades de engenharia.
  - Cards de "última leitura" com cor semântica (verde / amarelo / vermelho) por grandeza.
  - Indicador global de saúde do equipamento.
  - Gráficos de tendência (Plotly) com linhas de referência das faixas nominais e dos limites ISO.
  - Exportação dos dados em CSV e JSON (tanto convertidos quanto brutos).
- **Tema dark** de alto contraste, layout responsivo e sidebar de navegação.

---

## Arquitetura

A aplicação é organizada em camadas, com a UI completamente desacoplada das regras de negócio e da persistência. Isso permite trocar o framework de interface (ex.: Streamlit → Gradio, FastAPI + React) sem alterar o backend, e vice-versa.

```
.
├── app.py                          # Entry point Streamlit (apenas roteamento)
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Tema visual
├── data/
│   └── equipamentos.json           # Persistência local
└── src/
    ├── config/
    │   └── settings.py             # Constantes globais
    ├── backend/
    │   ├── models.py               # Dataclass Equipamento
    │   ├── repository.py           # Camada de persistência
    │   ├── sensor_simulator.py     # Gerador de leituras brutas
    │   └── converters.py           # ADC → unidade de engenharia
    └── frontend/
        ├── components/
        │   └── sidebar.py          # Menu lateral
        └── pages/
            ├── consulta.py         # Tela inicial / datatable
            ├── cadastro.py         # Formulário de cadastro / edição
            └── dados_brutos.py     # Painel de sensores
```

### Como as camadas se conectam

| Camada | Responsabilidade | Pontos de extensão |
|---|---|---|
| `src/backend/models` | Define o domínio (`Equipamento`). Não conhece UI nem persistência. | Adicionar novos campos ou criar entidades relacionadas. |
| `src/backend/repository` | Persistência. Hoje em JSON local. | Substituir por SQLite / Postgres / Supabase mantendo a mesma API. |
| `src/backend/sensor_simulator` | Gera leituras simuladas. | Trocar por um adaptador real (Modbus, MQTT, OPC-UA) que respeite `gerar_amostras()`. |
| `src/backend/converters` | Converte sinal bruto em unidade física. | Ajustar curvas de calibração ou adicionar novas grandezas. |
| `src/frontend` | Tudo que é Streamlit. | Pode ser reescrito em outro framework sem tocar no backend. |

---

## Como rodar localmente

### Pré-requisitos

- Python 3.10+
- pip

### Instalação

```bash
git clone <url-do-repositorio>
cd challenge_sprint1_frontend

# (opcional) ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate            # Windows PowerShell

pip install -r requirements.txt
streamlit run app.py
```

A interface fica disponível em `http://localhost:8501`. O repositório já vem com 4 equipamentos de exemplo em `data/equipamentos.json`.

---

## Deploy

A aplicação pode ser publicada em qualquer ambiente que sustente um processo Python persistente com WebSocket. Vercel **não é compatível** (arquitetura serverless). Alternativas que funcionam de graça:

### Streamlit Community Cloud (mais simples)

1. Suba o repositório no GitHub (público).
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com GitHub.
3. **New app** → escolha o repositório → arquivo `app.py` → **Deploy**.
4. A URL pública é gerada em ~2 minutos no formato `https://<app>.streamlit.app`.

### Render.com (free tier)

- Tipo: **Web Service**
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Hugging Face Spaces

- Crie um Space tipo **Streamlit** e faça push do código.

### Railway / Fly.io

- Mesmo padrão: comando de start `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`.

---

## Conversão de sinal: como funciona

Os sensores entregam um inteiro de 12 bits (`0` a `4095`) representando o valor analógico amostrado. Cada grandeza é mapeada linearmente para sua faixa física, usando os parâmetros nominais do equipamento:

| Grandeza | Fórmula | Faixa de saída |
|---|---|---|
| Tensão (V) | `raw × 2 × Vnominal / 4095` | 0 a 2× nominal |
| Corrente (A) | `raw × 2 × Inominal / 4095` | 0 a 2× nominal |
| Rotação (RPM) | `raw × 2 × RPMnominal / 4095` | 0 a 2× nominal |
| Temperatura (°C) | `raw × 150 / 4095` | 0 a 150 °C |
| Vibração (mm/s) | `raw × 10 / 4095` | 0 a 10 mm/s (faixa típica ISO 10816) |

Os valores brutos são preservados ao lado dos convertidos: se a calibração mudar, os dados podem ser reconvertidos sem perda de informação.

### Limites de saúde

| Grandeza | Normal | Atenção | Crítico |
|---|---|---|---|
| Tensão | desvio < 5% do nominal | 5–10% | > 10% |
| Corrente | < 110% do nominal | 110–120% | > 120% |
| Temperatura | < 70 °C | 70–90 °C | > 90 °C |
| Vibração | < 2.8 mm/s (ISO A/B) | 2.8–4.5 (ISO B/C) | > 4.5 (ISO C/D) |

---

## Decisões de UX

| Princípio | Implementação |
|---|---|
| Latência | `@st.cache_data` na simulação dos sensores; spinners em operações perceptíveis. |
| Confirmação explícita | Exclusão exige passo de confirmação; validações inline antes da submissão do formulário. |
| Cores semânticas | Verde / amarelo / vermelho nas leituras, com limiares baseados em ISO 10816 (vibração) e desvios percentuais (elétricas). |
| Acessibilidade | Tema dark de alto contraste; ícones acompanham texto; tooltips em campos não-óbvios. |
| Feedback | Mensagens de sucesso, erro e atenção contextualizadas. |

---

## Stack

- **Python 3.10+**
- **Streamlit** — UI
- **Pandas** — manipulação tabular
- **Plotly** — gráficos interativos
- **JSON** — persistência local

---

## Roadmap

A arquitetura desacoplada permite evoluir o sistema sem reescrever a UI:

- Integração com modelo preditivo (treinamento offline + inferência online).
- Detecção de anomalias e alertas em tempo real.
- Dashboard analítico com estimativa de RUL (*Remaining Useful Life*).
- Substituição do simulador por driver real (Modbus / MQTT / OPC-UA).
- Migração da persistência para banco relacional (Postgres / Supabase).

---

## Licença

Projeto educacional.
