# MultiAgentAssistant — Roadmap de Estudos

> O que estudar **antes e durante** a construção do projeto, na ordem de dependência.
> Cada bloco usa o anterior. Companion do [PLANEJAMENTO.md](./PLANEJAMENTO.md).
> Última atualização: 2026-06-13.

---

## Como usar este roadmap

**Não estude todos os 6 blocos antes de codar.** O ciclo eficiente é:

```
Bloco 0 → 1 → 2 → 3  →  [FASE 0: hello crew com Gemini]
                              ↓
                          Bloco 4  →  [FASE 1: RAG]
                              ↓
                          Bloco 5  →  Bloco 6  →  [FASES 4, 5, 6]
```

Aprender → aplicar na prática → aprender o próximo. Muito melhor que estudar tudo de uma vez.

---

## Bloco 0 — Fundamentos (usados o tempo todo)

*Rápido, mas não pule — o resto trava sem isso.*

| Tópico | Por que importa aqui | Onde estudar |
|---|---|---|
| Python: ambientes virtuais, `pip`/`uv`, imports, módulos | Todo o projeto é Python; venv evita "funciona na minha máquina" | https://docs.astral.sh/uv/ |
| `async` / `await` (noção básica) | FastAPI e chamadas a LLM são assíncronas | https://realpython.com/async-io-python/ |
| **Pydantic** (modelos, validação) | Como os agentes devolvem saída estruturada e confiável | https://docs.pydantic.dev/latest/ |
| Variáveis de ambiente / `.env` | Onde a API key do Gemini vai morar (fora do código) | conceito + `python-dotenv` |

---

## Bloco 1 — Conceitos de LLM e agentes (base mental)

| Tópico | O que entender |
|---|---|
| O que é um LLM, tokens, contexto, temperatura | Por que o "contexto" é limitado e custa dinheiro |
| **Prompt engineering** básico | System prompt, papel, instruções — é o "cérebro" de cada agente |
| O que é um **agente** (LLM + objetivo + ferramentas + loop) | Diferença entre "chamar um LLM" e "um agente que decide e age" |
| **Tool / function calling** | Como o agente chama `consulta_pedido()` etc. |
| Por que **multiagente** (especialização, roteamento) | A razão de existir do projeto |

> Conceitos do CrewAI sobre agentes: https://docs.crewai.com/concepts/agents

---

## Bloco 2 — CrewAI (framework escolhido) → prepara Fases 0 e 2

| Tópico | Onde |
|---|---|
| Agents, Tasks, Crews (o "hello crew") | https://docs.crewai.com/quickstart |
| Processos: sequential vs hierarchical | https://docs.crewai.com/concepts/processes |
| **Flows** (orquestração determinística — nossa espinha dorsal) | https://docs.crewai.com/concepts/flows |
| Tools e Memory | https://docs.crewai.com/concepts/tools |

---

## Bloco 3 — Gemini + LiteLLM → prepara Fase 0

| Tópico | Onde |
|---|---|
| Gerar a **API key** e o "hello world" do Gemini | https://aistudio.google.com/apikey + https://ai.google.dev/gemini-api/docs |
| Como o CrewAI fala com o Gemini via **LiteLLM** | https://docs.crewai.com/concepts/llms |

> ⚠️ A assinatura "Gemini Plus" do app **não** habilita a API. É preciso a API key do Google AI Studio.

---

## Bloco 4 — RAG → prepara Fase 1 (o coração do projeto)

| Tópico | O que entender |
|---|---|
| O problema que o RAG resolve | O LLM não conhece os seus dados privados |
| **Embeddings** e busca por similaridade | Por que texto vira vetor numérico |
| **Chunking** (tamanho, overlap) | A qualidade da resposta depende disso |
| **Vector store** (Chroma) | Onde os vetores ficam guardados |
| Pipeline completo: ingestão → retrieval → grounding com citação | O fluxo de ponta a ponta |

> Docs: https://docs.trychroma.com/ + Knowledge do CrewAI: https://docs.crewai.com/concepts/knowledge

---

## Bloco 5 — Web (API + UI) → prepara Fase 4

| Tópico | Onde |
|---|---|
| **FastAPI** (endpoint, request/response, async) | https://fastapi.tiangolo.com/ |
| Noção de React + fetch (ou Streamlit p/ MVP rápido) | (já tem alguma base de front pelo CompassPI) |

---

## Bloco 6 — Qualidade e produção → prepara Fases 5 e 6

| Tópico | Por que |
|---|---|
| **Avaliação de RAG** (RAGAS: faithfulness, answer relevancy) | Medir se as respostas são boas, não só "parecem" boas |
| **Observabilidade** (tracing de agentes/tokens/custo) | Enxergar o que cada agente fez |
| **Guardrails** (prompt-injection, PII) | Segurança em SAC com cliente real |

---

## Checklist de prontidão por fase

- [ ] **Blocos 0–3 concluídos** → pronto para a **Fase 0** (hello crew com Gemini)
- [ ] **Bloco 4 concluído** → pronto para a **Fase 1** (RAG single-agent)
- [ ] (Fases 2 e 3 reusam Blocos 1–4)
- [ ] **Bloco 5 concluído** → pronto para a **Fase 4** (web chat)
- [ ] **Bloco 6 concluído** → pronto para as **Fases 5–6** (eval, observabilidade, hardening)
