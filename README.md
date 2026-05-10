# ⚙️ Sistema de Gestão de Ativos Industriais — Sprint 1

Aplicação **Streamlit** para cadastro técnico inicial de equipamentos industriais e visualização de dados brutos de sensores. Entrega da **Sprint 1** do Challenge: fundamentos do ativo e interface de cadastro.

> 🎯 **Objetivo da Sprint:** garantir que o sistema "conheça" o equipamento. Operador cadastra o ativo, visualiza sua ficha técnica e inspeciona os dados que virão dos sensores nas próximas fases.

---

## 📸 Funcionalidades

- ✅ **Tela inicial de consulta** com data table dos equipamentos cadastrados, filtros por status / tipo / busca, e métricas resumo
- ✅ **Módulo de cadastro técnico** com formulário completo: TAG, modelo, fabricante, potência, tensão, corrente, RPM, frequência, localização, data de instalação, status e observações
- ✅ **Edição e exclusão** de equipamentos (com confirmação — *human-in-the-loop*)
- ✅ **Visualização de dados brutos** dos sensores (ADC 12-bit, 0–4095) **convertidos** para unidades de engenharia: **V, A, RPM, °C, mm/s**
- ✅ **Cores semânticas** nas leituras (verde / amarelo / vermelho) baseadas em **ISO 10816** (vibração) e limites de operação
- ✅ **Exportação** dos dados em CSV / JSON
- ✅ **Sidebar** com menu de navegação preparado para receber novas páginas nos próximos sprints

---

## 🏗️ Arquitetura

A aplicação segue arquitetura em camadas para permitir **desenvolvimento desacoplado**: o backend (modelo, persistência, simulação) pode evoluir independentemente do frontend, e a camada de UI pode ser migrada para **Gradio**, **FastAPI + React**, ou outro framework sem afetar o restante do código.

```
challenge_sprint1/
├── app.py                          # Entry point Streamlit (apenas roteamento)
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Tema visual (dark, premium)
├── data/
│   └── equipamentos.json           # Persistência JSON (Sprint 1)
└── src/
    ├── config/
    │   └── settings.py             # Constantes globais
    ├── backend/
    │   ├── models.py               # Dataclass Equipamento (modelo de domínio)
    │   ├── repository.py           # Persistência (JSON; trocável por SQL/Supabase)
    │   ├── sensor_simulator.py     # Gera dados brutos (substituível por driver real)
    │   └── converters.py           # Raw ADC → unidade de engenharia
    └── frontend/
        ├── components/
        │   └── sidebar.py          # Menu lateral reutilizável
        └── pages/
            ├── consulta.py         # Tela inicial / data table
            ├── cadastro.py         # Formulário de cadastro / edição
            └── dados_brutos.py     # Visualização das leituras
```

### Por que essa estrutura?

| Necessidade da Sprint | Como atendida |
|---|---|
| Trabalhar **simultaneamente** em modelo (ML) e UI | Backend e frontend não se conhecem; ambos consomem `models.py` |
| **Migrar de framework** em sprints futuros | Toda lógica fica em `src/backend`. Trocar Streamlit por Gradio = reescrever `src/frontend` |
| **Substituir simulador por sensor real** | Basta criar nova classe que respeite a interface `gerar_amostras()` |
| **Trocar persistência** (JSON → Postgres/Supabase) | Reescrever `EquipamentoRepository` mantendo a mesma API |

---

## 🚀 Como rodar localmente

### Pré-requisitos
- Python **3.10+**
- pip

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/<seu-usuario>/<seu-repo>.git
cd <seu-repo>

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux / Mac
# .venv\Scripts\activate            # Windows PowerShell

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode a aplicação
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`. Já vem com **4 equipamentos de exemplo** carregados (`data/equipamentos.json`) para você gravar o vídeo sem precisar cadastrar do zero.

---

## ☁️ Deploy

### ⚠️ Sobre Vercel
**Streamlit não é compatível com Vercel** (Vercel é serverless e Streamlit precisa de um processo Python persistente com WebSocket). As opções gratuitas que **funcionam** são:

### Opção 1 — Streamlit Community Cloud (recomendado, 3 cliques)
1. Suba o repositório para o GitHub (público)
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com GitHub
3. Clique em **New app** → escolha o repositório → arquivo `app.py` → **Deploy**
4. Em ~2 min sua URL pública está pronta (formato `https://<app>.streamlit.app`)

### Opção 2 — Render.com (free tier)
1. Crie um **Web Service** apontando para o repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Opção 3 — Hugging Face Spaces
1. Crie um Space tipo **Streamlit**
2. Faça push do código

### Opção 4 — Railway / Fly.io
Mesmo padrão: comando de start `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`.

---

## 🎨 Decisões de UX (atendendo "design para latência, human-in-the-loop, cores semânticas")

| Princípio | Aplicação |
|---|---|
| **Latência** | `@st.cache_data` na simulação dos sensores; spinners em operações > 200 ms |
| **Human-in-the-loop** | Exclusão exige **confirmação** explícita; validações inline no formulário antes de submeter; `clear_on_submit` controlado |
| **Cores semânticas** | Verde (normal) / Amarelo (atenção) / Vermelho (crítico) nas métricas, baseadas em **ISO 10816** para vibração e desvios % para grandezas elétricas |
| **Acessibilidade** | Tema dark de alto contraste; ícones + texto (não confiar só em cor); tooltips em campos não-óbvios |
| **Feedback** | `st.success`, `st.error`, `st.warning`, `st.balloons` em cadastros bem-sucedidos |

---

## 🧪 Conversão de sinal: como funciona

Os sensores entregam um inteiro **0–4095** (ADC 12-bit). Cada grandeza é mapeada linearmente:

| Grandeza | Fórmula | Faixa |
|---|---|---|
| Tensão (V) | `raw × 2 × Vnominal / 4095` | 0 a 2× nominal |
| Corrente (A) | `raw × 2 × Inominal / 4095` | 0 a 2× nominal |
| Rotação (RPM) | `raw × 2 × RPMnominal / 4095` | 0 a 2× nominal |
| Temperatura (°C) | `raw × 150 / 4095` | 0 a 150 °C |
| Vibração (mm/s) | `raw × 10 / 4095` | 0 a 10 mm/s (ISO 10816) |

Os valores **brutos** ficam preservados ao lado dos convertidos, permitindo recálculo caso a calibração seja revisada no futuro.

---

## 🔮 Próximos sprints

- **Sprint 2** — modelo preditivo (treinamento offline) integrado via interface comum
- **Sprint 3** — detecção de anomalias online + alertas
- **Sprint 4** — dashboard analítico, RUL (Remaining Useful Life)
- **Sprint 5** — substituir o simulador por driver real (Modbus / MQTT / OPC-UA)

A arquitetura atual já permite incorporar tudo isso sem reescrever a camada de UI.

---

## 📦 Stack

- **Python 3.10+**
- **Streamlit** — framework de UI
- **Pandas** — manipulação tabular
- **Plotly** — gráficos interativos
- **JSON** — persistência local (Sprint 1)

---

## 📄 Licença

Projeto educacional — Challenge FIAP / 2025.
