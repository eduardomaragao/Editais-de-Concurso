# Ficha de campos do edital
**App de acompanhamento de concursos — v1**
Piloto: Procurador (PGE/PGM) · Banca de referência: FCC

Este documento lista, tela por tela, os dados que o app precisa e **de onde cada um vem**. Serve como contrato de saída do seu parser: o que ele extrai do edital, o que ele apenas sugere pra você confirmar, o que é inserido por curadoria e o que o próprio candidato preenche no app.

## Legenda de origem

| Código | Significado |
|---|---|
| **AUTO** | O parser extrai direto do edital, com boa confiança. |
| **REVISÃO** | O parser sugere, mas **você confirma antes de publicar** (campo crítico). |
| **CURADORIA** | Inserido por você/equipe — não vem do texto do edital (ex.: PDFs de provas). |
| **USUÁRIO** | Preenchido pelo candidato dentro do app (não é tarefa do parser). |

---

## 1. Identificação do edital

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Órgão | texto | AUTO | Ex.: PGE-SP, PGM-SP |
| Cargo | texto | AUTO | Ex.: Procurador do Estado |
| Banca | texto | AUTO | Ex.: FCC, FGV, Cebraspe |
| Número/ano do edital | texto | AUTO | Ex.: 01/2026 |
| Link do edital oficial (PDF) | url | AUTO | Fonte primária |
| Data de publicação | data | AUTO | |
| Vagas | número | AUTO | |
| Cadastro reserva | booleano | AUTO | |
| Remuneração | texto/moeda | AUTO | |
| Requisitos/escolaridade | texto | AUTO | |
| Status | enum | derivado | aberto · inscrições encerradas · em andamento · concluído |

---

## 2. Datas & prazos (cronograma)

É uma **lista de eventos**. Cada evento alimenta a tabela de status e o calendário/exportação `.ics`.

**Estrutura de cada evento**

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Tipo | enum | AUTO | ver lista abaixo |
| Título | texto | AUTO | rótulo exibido |
| Data início | data | AUTO | |
| Data fim / hora | data-hora | AUTO | prova tem hora; prazo tem intervalo |
| Status | enum | derivado | encerrado · em andamento · futuro · referência |
| Fonte | url | AUTO | edital ou retificação de origem |

**Tipos de evento a capturar:** publicação · inscrições · pedido de isenção · resultado da isenção · pagamento · entrega de laudos/documentos · **prova objetiva** · **prova discursiva/subjetiva** · **prova oral** · resultados (preliminar/final) · prazos de recurso · convocações.

> A **prova objetiva/subjetiva/oral** aqui guarda apenas **data e hora**. O *local* fica na tela "Dados da prova" (seção 3), porque é individual.

---

## 3. Dados da prova

Dividido em dois: o que vem do edital e o que **o candidato preenche** (porque cada um recebe um local e uma sala).

**Do edital**

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Fase | texto | AUTO | objetiva, oral etc. |
| Data | data | AUTO | mesma da seção 2 |
| Horário de início | hora | AUTO | |
| Abertura/fechamento dos portões | hora | AUTO | |
| Duração | texto | AUTO | |

**Do candidato (por local — pode haver mais de um)**

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Identificação | texto | USUÁRIO | Ex.: "Prova objetiva", "Prova oral" |
| CEP | texto | USUÁRIO | dispara busca de endereço (ViaCEP/Correios) |
| Endereço | texto | USUÁRIO | preenchido pelo CEP; editável |
| Número/complemento | texto | USUÁRIO | |
| Sala de aplicação | texto | USUÁRIO | |
| Coordenadas (lat/lng) | par | derivado | geradas do endereço, para os links |
| Links de transporte | ação | derivado | Uber, 99, Google Maps (carro/transporte público) a partir das coordenadas |

---

## 4. Corte de conteúdo cobrado

Campo crítico — é o que derruba candidato. **Sempre em REVISÃO.** Costuma vir como **referência relativa**, não como data cravada.

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Legislação exigida até | data | REVISÃO | data **resolvida** (ex.: 31/03/2026) |
| Jurisprudência exigida até | data | REVISÃO | idem |
| Forma de expressão | enum | AUTO | `explicita` (traz a data) · `relativa` ("data de publicação deste edital") |
| Referência (se relativa) | texto | AUTO | ex.: "primeira publicação do edital" |
| Afetado por retificação? | booleano | REVISÃO | em geral **não** — trava na 1ª publicação |
| Trecho do edital | texto | AUTO | citação literal (ex.: item 16.32) |
| Informado no edital? | booleano | AUTO | se não houver cláusula, marca "não informado" |

> Padrão comum (Cebraspe, item 16.32): "legislação vigente na data da primeira publicação" e "jurisprudência publicada até a data de publicação". Como é **referência relativa**, o parser resolve para uma data e você confirma qual publicação conta (data do edital vs. Diário Oficial). E lembra: retificação **não** move esse corte.

---

## 5. Conteúdo programático (árvore)

Hierarquia de três níveis: **matéria → tópico → subtópico**. O texto tem que sair **idêntico ao edital**, e a **estrutura inteira passa pela sua confirmação**: o parser propõe a árvore, mas quem decide o que é tópico, o que é subtópico e o que fica agrupado é você.

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| id | id | AUTO | identificador do nó (mecânico) |
| parent_id | id | REVISÃO | agrupamento — o parser sugere, você reorganiza |
| Nível | enum | REVISÃO | materia · topico · subtopico — você promove/rebaixa itens |
| Título | texto | REVISÃO | **texto literal do edital** — revisar fidelidade |
| Ordem | número | AUTO | segue a sequência do edital; reajusta se você reagrupar |
| Revisado | booleano | REVISÃO | trava: fica rascunho até você confirmar a árvore |
| Concluído | booleano | USUÁRIO | por candidato + edital; **não é do parser** |

> Na prática o parser entrega um **rascunho da árvore** e uma tela de revisão onde você promove a tópico, rebaixa a subtópico, agrupa ou separa e corrige o texto. Nada é publicado antes desse "ok". É onde o parser mais erra: quebra de linha, "e" virando item novo, ou algo que deveria ser subtópico aparecendo como tópico.

---

## 6. Provas anteriores

Não vêm do edital — são **curadoria/upload**. Janela: de 2020 pra frente (definir se é fixo em 2020 ou móvel de 5 anos).

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Banca / Órgão / Cargo | texto | CURADORIA | |
| Ano | número | CURADORIA | |
| Tipo | enum | CURADORIA | objetiva · subjetiva · oral |
| Arquivo da prova (PDF) | arquivo | CURADORIA | hospedado no app |
| Arquivo de respostas (PDF) | arquivo | CURADORIA | **gabarito** (objetiva) · **padrão de resposta** (subjetiva) · **espelho/critérios** (oral) |
| Fonte oficial | url | CURADORIA | rastreabilidade |

---

## 7. Isenções

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Há isenção? | booleano | AUTO | |
| Público-alvo | texto | AUTO | ex.: doadores, hipossuficientes, CadÚnico |
| Período (início/fim) | data | AUTO | também vira evento na seção 2 |
| Documentos exigidos | texto | AUTO | |
| Link do pedido | url | AUTO/CURADORIA | |

---

## 8. Links & controle

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Site do curso | url | CURADORIA | eduardoaragao.com |
| Edital oficial (PDF) | url | AUTO | |
| Página da banca | url | AUTO | |
| Retificações | lista | AUTO | data + link de cada retificação |

> **Retificações importam:** editais mudam datas e conteúdo depois de publicados. O parser/admin precisa detectar retificação e reprocessar o edital.

---

## Regras de publicação (travas)

O edital **não vai pro aluno** enquanto você não confirmar:

1. Data e hora da prova objetiva
2. Corte de legislação e jurisprudência
3. A árvore de conteúdo — **estrutura** (tópico/subtópico, agrupamento) **e títulos literais**

O resto pode publicar como rascunho e ir refinando.

---

## Exemplo de registro (alvo de saída do parser)

```json
{
  "edital": {
    "orgao": "PGE-SP",
    "cargo": "Procurador do Estado",
    "banca": "FCC",
    "numero": "01/2026",
    "link_oficial": "https://...",
    "status": "inscricoes_encerradas",
    "conteudo_revisado": false,
    "corte_conteudo": {
      "legislacao_ate": "2026-03-31",
      "jurisprudencia_ate": "2026-03-31",
      "trecho_edital": "Serão exigidas legislação e jurisprudência publicadas até 31/03/2026.",
      "informado": true,
      "revisado": false
    }
  },
  "cronograma": [
    { "tipo": "prova_objetiva", "titulo": "Prova objetiva",
      "inicio": "2026-09-11T08:00:00", "hora_portoes": "07:30", "duracao": "5h" },
    { "tipo": "prova_oral", "titulo": "Prova oral", "inicio": "2026-09-27" }
  ],
  "conteudo": [
    { "id": "adm", "parent_id": null, "nivel": "materia",
      "titulo": "Direito Administrativo", "ordem": 2 },
    { "id": "adm-resp", "parent_id": "adm", "nivel": "topico",
      "titulo": "Responsabilidade civil do Estado", "ordem": 5 },
    { "id": "adm-resp-1", "parent_id": "adm-resp", "nivel": "subtopico",
      "titulo": "Responsabilidade por atos comissivos e omissivos", "ordem": 1 }
  ],
  "provas_anteriores": [
    { "ano": 2024, "tipo": "objetiva",
      "arquivo_prova": "provas/pge-sp-2024-obj.pdf",
      "arquivo_resposta": "provas/pge-sp-2024-gabarito.pdf",
      "fonte": "https://..." }
  ]
}
```

*Progresso do candidato (conteúdo concluído) e o local de prova individual não entram aqui — ficam na conta do usuário no app.*
