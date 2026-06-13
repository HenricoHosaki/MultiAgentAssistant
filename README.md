# MultiAgentAssistant

Assistente de Atendimento ao Cliente (SAC) multiagente — responde dúvidas sobre
**Produtos, Entregas e Pagamentos** usando agentes especializados + RAG.

> Arquitetura, decisões e roadmap: ver [docs/PLANEJAMENTO.md](./docs/PLANEJAMENTO.md) e [docs/ROADMAP_ESTUDOS.md](./docs/ROADMAP_ESTUDOS.md).

## Tech stack

- **Python 3.12** · **uv** (gestão de dependências)
- **CrewAI** (orquestração multiagente)
- **Gemini** (LLM, via LiteLLM)
- _RAG (Chroma), FastAPI e React — adicionados nas próximas fases_

## Pré-requisitos

- API key do Gemini ([Google AI Studio](https://aistudio.google.com/apikey)) — o tier gratuito é suficiente

### 1. Instalar o `uv` (gestor de dependências)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Feche e reabra o terminal e confirme: `uv --version`

### 2. Instalar o Python (via uv)

```powershell
uv python install 3.12
```

### 3. Instalar o CLI do CrewAI

```powershell
uv tool install crewai
uv tool update-shell    # adiciona o crewai ao PATH (reabra o terminal depois)
```
Confirme: `crewai version`

## Setup

O código da crew fica em `sac_assistant/` (gerado pelo CLI do CrewAI).

1. Clonar o repositório
2. Entrar na pasta da crew: `cd sac_assistant`
3. Criar o `.env` com:
   ```
   MODEL=gemini/gemini-2.5-flash
   GEMINI_API_KEY=sua_chave_aqui
   ```
4. Instalar dependências: `crewai install`

## Como rodar

```powershell
cd sac_assistant
crewai run
```

Gera um `report.md` ao final. (Na Fase 0 o conteúdo é o template genérico; será
customizado para o SAC nas próximas fases.)

## Estrutura do projeto

```
MultiAgentAssistant/
├── docs/                       # PLANEJAMENTO.md, ROADMAP_ESTUDOS.md
├── README.md
└── sac_assistant/              # projeto CrewAI
    ├── .env                    # segredos (não vai pro git)
    ├── pyproject.toml          # dependências + comandos
    ├── knowledge/              # base p/ RAG (Fase 1)
    └── src/sac_assistant/
        ├── main.py             # ponto de entrada (run/train/test)
        ├── crew.py             # monta a Crew (Agents + Tasks + Process)
        └── config/
            ├── agents.yaml     # define os agentes
            └── tasks.yaml      # define as tarefas
```

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `GEMINI_API_KEY` | Chave da API do Gemini — **nunca commitar** (fica só no `.env`) |
| `MODEL` | Modelo usado (ex.: `gemini/gemini-2.5-flash`) |

---

## Progresso

- [x] **Passo 1** — Tooling instalado (uv 0.11.21, Python 3.12.13)
- [x] **Passo 2** — API key do Gemini gerada
- [x] **Passo 3** — Criar o projeto (scaffold CrewAI em `sac_assistant/`)
- [x] **Passo 4** — `.env` configurado; `.gitignore` já protege o `.env`
- [x] **Passo 5** — hello-crew validado com Gemini (`crewai run` gerou `report.md`)

**✅ Fase 0 concluída** — CrewAI + Gemini funcionando. Próximo: Fase 1 (RAG single-agent).
