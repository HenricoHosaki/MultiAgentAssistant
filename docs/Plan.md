# MultiAgentAssistant — Planejamento e Decisões

> Assistente de Atendimento ao Cliente Multiagente (SAC).
> Documento de planejamento — registra tudo que foi **decidido** e **planejado** antes da implementação.
> Última atualização: 2026-06-13.

---

## 1. Contexto e objetivo

Projeto **greenfield** (novo) com dois objetivos:

1. **Aprendizado** — primeira experiência prática com sistemas **multiagente + RAG**. O código será escrito manualmente, passo a passo, para fixar os conceitos.
2. **Caso de uso** — SAC para clientes externos com dúvidas recorrentes sobre **Produtos, Entregas e Pagamentos**, usando **agentes especializados por área**.

**Resultado esperado:** um assistente de web chat que recebe a pergunta do cliente, roteia para o agente especialista certo, responde **fundamentado em base de conhecimento (RAG)** com citações, e escala para humano quando não tiver confiança.

---

## 2. Decisões travadas

| Tópico | Decisão | Racional |
|---|---|---|
| Domínio | SAC externo: Produtos, Entregas, Pagamentos | Segue o card original do projeto |
| Framework | **CrewAI** (Crews + Flows) | Melhor retorno de aprendizado p/ 1º projeto; LangGraph fica como passo 2 |
| LLM | **Gemini** (`gemini-2.5-flash`) via **API key** (Google AI Studio, tier free) | Confirmado; usar **LiteLLM** p/ abstrair — trocar de modelo = mudar config |
| Canal | **Web chat** (widget próprio) | Mais controle de UX, mais simples de começar |
| Idioma do produto | **Bilíngue: PT-BR + Inglês** | Detecta o idioma da pergunta e responde no mesmo idioma |
| Idioma do código/docs | Inglês | Boa prática; conteúdo ao usuário final em PT-BR/EN |
| Vector store (MVP) | **Chroma** (local) | Simples para começar; evolui p/ pgvector/Qdrant |
| Gestão de dependências | **`uv`** | Rápido e moderno, com lock file reprodutível |

> ⚠️ **Pré-requisito:** gerar **API key do Gemini** no Google AI Studio (https://aistudio.google.com/apikey).
> A assinatura **"Gemini Plus"** do app **NÃO** habilita a API — são coisas diferentes.

---

## 3. Por que CrewAI (e o que são as alternativas)

| Framework | Modelo mental | Como funciona | Curva | Valor de aprendizado |
|---|---|---|---|---|
| **CrewAI** ✅ | "Equipe de especialistas" | `Agents` (papel, objetivo) + `Tasks` agrupados numa `Crew`. Modos: **Crews** (autônomos) e **Flows** (pipeline determinístico). | Suave (~20 linhas) | Conceitos centrais de multiagente, rápido |
| LangGraph | "Máquina de estados / grafo" | Sistema modelado como grafo; controle explícito de cada transição. | Íngreme (~60+ linhas) | Fundamentos de orquestração/estado; passo 2 |
| Híbrido | Protótipo + produção | CrewAI p/ prototipar, LangGraph nos caminhos críticos. | Alta | Bom a longo prazo |

> **Consenso do mercado (2026):** o framework importa menos que o **pipeline de avaliação, observabilidade e qualidade do RAG**. RAG + qualidade dos documentos respondem por **60–70%** do desempenho num caso de conhecimento como SAC.

---

## 4. Arquitetura proposta

### Fluxo principal (CrewAI Flow como espinha dorsal)

```
Web Chat (React)
  └── FastAPI  POST /chat
        └── CrewAI Flow (orquestração determinística)
              1. Guardrail de entrada  (PII / prompt-injection / fora de escopo)
                 + detecção de idioma   (PT-BR ou EN → responde no mesmo)
              2. Triage Agent          (classifica intenção → Produtos | Entregas | Pagamentos | Outro)
              3. Specialist Crew/Task   (1 agente especialista + RAG + tools)
                   ├── Produtos    → RAG: catálogo, manuais, specs
                   ├── Entregas    → RAG: políticas de envio + tool consulta_pedido()
                   └── Pagamentos  → RAG: políticas financeiras + tool consulta_fatura()
              4. Composer/QA Agent      (tom, idioma, política, adiciona citações)
              5. Escalation             (se confiança baixa → abre ticket / handoff humano)
        └── resposta + fontes citadas
```

**Por que Flow e não só Crew:** SAC precisa de previsibilidade (sempre passar por guardrail → triage → especialista → QA). O Flow dá esse caminho determinístico; cada especialista pode ser uma Task/Crew interna. O roteamento por intenção evita gastar tokens acionando todos os agentes.

### Agentes (especialistas por área)

| Agente | Papel | Tools / Conhecimento |
|---|---|---|
| Triage | Classifica a intenção e roteia | Saída estruturada (Pydantic) com `intent` + `confidence` |
| Produtos | Dúvidas de produto, specs, uso, disponibilidade | RAG (catálogo/manuais) |
| Entregas | Status de pedido, prazos, rastreio, políticas | RAG (políticas) + `consulta_pedido()` (API/mock) |
| Pagamentos | Faturas, formas de pagamento, reembolso | RAG (políticas) + `consulta_fatura()` (API/mock) |
| Composer/QA | Garante tom, idioma, política e citações | — |
| Escalation | Handoff p/ humano quando confiança baixa | `abrir_ticket()` (mock) |

### RAG (Retrieval-Augmented Generation)

| Camada | MVP (aprendizado) | Evolução (produção) |
|---|---|---|
| Vector store | **Chroma** (local, embutido) | pgvector ou Qdrant |
| Embeddings | Gemini embeddings (`text-embedding-004`) | mesmo, ou open-source |
| Ingestão | Script de **chunking** de FAQs/políticas (Markdown/PDF) | Pipeline agendado + versionamento de docs |
| Grounding | Citar a fonte em cada resposta | Reranking + avaliação contínua |

> **Chunking** = quebrar documentos grandes em pedaços pequenos (~800 tokens, com ~100 de sobreposição) para que cada pedaço seja transformado em embedding e recuperado individualmente na busca. A qualidade do chunking impacta muito a resposta.

---

## 5. Stack técnica

| Camada | Escolha | Observação |
|---|---|---|
| Linguagem | Python 3.12 | — |
| Orquestração | CrewAI + crewai-tools | Crews + Flows |
| LLM | Gemini via LiteLLM | `GEMINI_API_KEY` em `.env` |
| RAG | Chroma + Gemini embeddings | CrewAI Knowledge feature como alternativa |
| API | FastAPI + Uvicorn | Endpoint `/chat`, streaming opcional |
| Frontend | React + Vite (web chat) | Pode começar com Streamlit p/ MVP rápido |
| Observabilidade | AgentOps ou Langtrace | Tracing de agentes/tokens/custo |
| Avaliação | RAGAS + conjunto de Q&A dourado | Eval-driven desde cedo |
| Gestão de deps | **`uv`** | Padrão atual mais rápido; lock file reprodutível |

---

## 6. Estrutura de projeto (proposta)

```
MultiAgentAssistant/
├── pyproject.toml
├── .env.example              # GEMINI_API_KEY, MODEL, etc. (nunca commitar .env)
├── README.md
├── PLANEJAMENTO.md           # este documento
├── src/sac/
│   ├── flows/
│   │   └── support_flow.py   # Flow principal (guardrail→triage→specialist→QA)
│   ├── agents/
│   │   ├── triage.py
│   │   ├── produtos.py
│   │   ├── entregas.py
│   │   ├── pagamentos.py
│   │   └── composer.py
│   ├── tools/
│   │   ├── orders.py         # consulta_pedido() (mock primeiro)
│   │   ├── payments.py       # consulta_fatura()
│   │   └── tickets.py        # abrir_ticket()
│   ├── rag/
│   │   ├── ingest.py         # chunking + indexação no Chroma
│   │   └── retriever.py
│   ├── schemas/              # Pydantic (intent, response, citations)
│   ├── guardrails/           # PII, prompt-injection, fora de escopo
│   └── api/
│       └── main.py           # FastAPI
├── knowledge/                # docs-fonte (FAQ, políticas, catálogo)
├── eval/
│   ├── golden_set.jsonl      # perguntas + respostas/refs esperadas
│   └── run_eval.py           # RAGAS
└── web/                      # React web chat
```

---

## 7. Roadmap em fases

| Fase | Entrega | Aprende |
|---|---|---|
| **0 — Setup** | Repo, `.env`, API key Gemini, "hello crew" rodando | Fundamentos do CrewAI, LiteLLM |
| **1 — RAG single-agent** | Ingestão de 1 domínio (Produtos) + 1 agente respondendo com citações | RAG, embeddings, grounding |
| **2 — Multiagente** | Triage + 3 especialistas dentro de um Flow | Roteamento, papéis, Flows |
| **3 — Tools + guardrails** | Tools mock (pedido/fatura/ticket), guardrail de entrada, escalation | Tool calling, segurança, handoff |
| **4 — Web chat** | FastAPI `/chat` + UI React | Integração full-stack |
| **5 — Observabilidade + eval** | Tracing (AgentOps) + golden set (RAGAS) | Avaliar e medir qualidade |
| **6 — Hardening** | PII, prompt-injection, rate limit, custo, fallback | Prontidão p/ produção |

Cada fase é um marco testável de forma independente.

---

## 8. Padrões e boas práticas (2026)

- **Saída estruturada** (Pydantic) em triage e respostas — confiabilidade > prosa livre.
- **Grounding com citações** — toda resposta cita a fonte; reduz alucinação e gera confiança.
- **Bilíngue (PT-BR + EN)** — detectar idioma da pergunta e responder no mesmo; base de conhecimento idealmente nos dois idiomas.
- **Eval-driven** — golden set desde a Fase 1; mede regressão a cada mudança.
- **Observabilidade desde cedo** — tracing de tokens, custo e passos de cada agente.
- **Guardrails** — detecção de prompt-injection, PII e perguntas fora de escopo antes do LLM.
- **Abstração de LLM** (LiteLLM) — trocar Gemini↔local↔OpenAI sem reescrever agentes.
- **Fallback humano** — quando `confidence` < limiar, escalar em vez de inventar.
- **Controle de custo** — modelo barato (flash) p/ triage; modelo melhor só quando necessário.
- **Segredos fora do código** — `.env` + `.env.example`; nunca commitar chaves.

---

## 9. Pontos em aberto (decidir nas próximas fases — não bloqueiam o início)

| Tópico | Quando decidir |
|---|---|
| Fonte real dos dados de pedidos/pagamentos (API real vs mock) | Fase 3 |
| UI: Streamlit (MVP rápido) vs React desde já | Início da Fase 4 |
| Ferramenta de observabilidade (AgentOps vs Langtrace) | Fase 5 |
| Persistência de conversas / memória de longo prazo | Fase 5–6 |
| Multi-tenant / autenticação do cliente | Fase 6 |

---

## 10. Verificação (como validar cada fase)

- **Fase 0:** a crew responde a um prompt fixo usando Gemini (confirma chave + LiteLLM).
- **Fase 1:** perguntar algo coberto pela base → resposta correta **com citação**; perguntar algo fora → admite não saber.
- **Fase 2:** 3 perguntas (uma por domínio) roteiam para o especialista certo (logar `intent`).
- **Fase 3:** pergunta de status de pedido aciona `consulta_pedido()`; pergunta sensível dispara escalation/guardrail.
- **Fase 4:** enviar mensagem pela UI web → resposta renderizada com fontes.
- **Fase 5:** `run_eval.py` roda o golden set e reporta métricas RAGAS (faithfulness, answer relevancy).

---

## 11. Modo de trabalho

- O **código é escrito manualmente** pelo desenvolvedor, passo a passo, para fins de aprendizado.
- O assistente (Claude) atua como **instrutor**: explica o porquê, entrega o conteúdo para digitar e revisa depois — **não** cria/edita arquivos de código.
- Documentação (como este arquivo) pode ser gerada pelo assistente quando solicitado.
