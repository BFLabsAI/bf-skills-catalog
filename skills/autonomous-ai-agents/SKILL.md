---
name: autonomous-ai-agents
description: "Arquitetura e engenharia de agentes autônomos de IA em loop contínuo: percepção, planejamento com DAGs, execução com ferramentas sandbox, observação com loop fechado e persistência com memória tripla."
category: agents
license: MIT
metadata:
  author: BF Labs & NousResearch
  version: "1.0.0"
---

# Autonomous AI Agents — Architecture & Runtime Operations

Guia mestre de engenharia, arquitetura e operação de agentes autônomos de IA com execução em loop fechado, memória tripla e orquestração maestro-trabalhadores.

## 🔄 O Loop Contínuo de Autonomia

```text
┌─────────────────────────────────────────────────────────────────┐
│                 AUTONOMOUS AGENT RUNTIME CORE                   │
├─────────────────────────────────────────────────────────────────┤
│  1. PERCEPÇÃO          2. PLANEJAMENTO        3. EXECUÇÃO       │
│  ┌──────────────┐      ┌───────────────┐      ┌───────────────┐ │
│  │ User Prompt  │ ───> │ Intent Map    │ ───> │ Sandbox Tools │ │
│  │ Context Tree │      │ Task DAG      │      │ Bash / Eval   │ │
│  │ Environment  │      │ Pre-flight QA │      │ MCP / Browser │ │
│  └──────────────┘      └───────────────┘      └───────┬───────┘ │
│                                                       │         │
│                        5. PERSISTÊNCIA & REFLEXÃO     ▼         │
│                        ┌──────────────────────────────────────┐ │
│                        │ Episodic Context (Turn History)      │ │
│                        │ Semantic Memory (ClawMem / pgvector) │ │
│                        │ Self-Correction / Skill Synthesis    │ │
│                        └──────────────────────────────────────┘ │
│                                       ▲                         │
│                                       │                         │
│                                4. OBSERVAÇÃO                    │
│                                ┌───────────────┐                │
│                                │ Exit Code     │                │
│                                │ Output Diff   │ ───────────────┘
│                                │ Verification  │                │
│                                └───────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 Os 4 Pilares da Autonomia SOTA

1. **Loop Fechado Obrigatório**: Nenhuma tarefa é dada por concluída sem prova observável (exit code 0, inspeção de diff ou teste aprovado).
2. **Memória Tripla**:
   - **Camada 0**: Working Memory (Janela ativa de contexto do modelo).
   - **Camada 1**: Memória Episódica (Histórico de turnos da sessão e snapshots).
   - **Camada 2**: Memória Semântica Vetorial (Longo prazo com busca semântica).
3. **Auto-Correção Diagnóstica**: Falhas de ferramentas não são repetidas. O agente formula hipóteses, instrumenta, aplica a menor correção atômica e verifica a regressão.
4. **Hierarquia Maestro-Trabalhadores**: O agente coordenador decompõe o trabalho em subagentes especializados (`scout` para leitura rápida, `task` para mutações e `reviewer` para QA de segurança).
