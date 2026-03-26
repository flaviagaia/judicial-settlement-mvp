# Judicial Settlement MVP

MVP técnico para apoio à proposta de acordos em processos judiciais a partir de PDFs incompletos. A solução foi desenhada para demonstrar, de forma objetiva para uma equipe técnica, como combinar ingestão documental, enriquecimento externo, modelagem relacional em grafo, recuperação de casos similares e um motor de proposta explicável.

## Objetivo

O problema de negócio é transformar documentos processuais com baixa densidade informacional em uma base consolidada suficiente para:

- recuperar contexto externo do caso;
- montar histórico comparável;
- identificar sinais de conciliabilidade;
- estimar chance de aceite;
- sugerir proposta de acordo com justificativa auditável.

## Leitura do projeto para uma equipe técnica

Este repositório foi estruturado como um `decision-support MVP` para uma plataforma de acordos judiciais digitais. A proposta é mostrar, de forma pragmática, como sair de um PDF processual com poucos dados para uma recomendação final de acordo baseada em:

- extração documental;
- enriquecimento externo;
- histórico comparável;
- modelagem relacional;
- score preditivo;
- explicação final rastreável.

## Escopo do MVP

O MVP recebe um PDF do processo, extrai campos estruturados, consulta uma camada de enriquecimento simulada inspirada em fontes como DataJud, monta uma visão em grafo das relações do caso, recupera processos semelhantes e sugere uma proposta de acordo.

## Arquitetura

```mermaid
flowchart LR
    A["PDF do processo"] --> B["OCR leve / parsing PDF"]
    B --> C["Extração estruturada"]
    C --> D["Base canônica do caso"]
    D --> E["Enriquecimento externo"]
    E --> F["Casos similares"]
    E --> G["Features tabulares"]
    E --> H["Grafo relacional"]
    F --> I["Motor de proposta"]
    G --> I
    H --> J["Justificativa contextual"]
    I --> K["Proposta final"]
    J --> K
```

## Fluxo funcional do MVP

1. O usuário envia um PDF do processo.
2. O sistema extrai campos estruturados mínimos do documento.
3. O caso é convertido em uma representação canônica.
4. Uma camada de enriquecimento busca sinais externos e comparáveis históricos.
5. Um grafo relacional organiza entidades e processos similares.
6. Um modelo baseline estima a chance de aceite.
7. Um motor de proposta converte o score e os comparáveis em oferta sugerida.
8. A interface exibe proposta, justificativa e evidências.

## O que a demonstração já faz

- gera PDFs jurídicos sintéticos para demonstração;
- extrai dados-chave do PDF via parsing;
- usa uma base histórica de apoio com acordos anteriores;
- recupera casos similares por `TF-IDF + cosine similarity`;
- cria um grafo com processo, partes, classe, assunto, tribunal e casos similares;
- treina um baseline de `Logistic Regression` para score de aceite;
- converte o score e os comparáveis em proposta sugerida;
- apresenta tudo em uma interface `Streamlit`.

## Técnicas usadas

### 1. Ingestão documental

Os PDFs demo são gerados com `reportlab` e lidos com `pypdf`. Nesta primeira versão o objetivo não é OCR pesado, e sim o desenho arquitetural da solução. Em uma fase seguinte, o parsing pode ser substituído por `PaddleOCR`, `PyMuPDF` e `pdfplumber`.

### 2. Extração estruturada

A extração usa expressões regulares orientadas a campos processuais:

- número CNJ;
- tribunal;
- vara/unidade;
- classe processual;
- assunto;
- partes;
- fase;
- valor da causa;
- data;
- tipo documental;
- pedido principal.

### 3. Enriquecimento externo

O enriquecimento usa uma base histórica sintética, mas desenhada no formato de uma futura camada que pode receber integrações reais com:

- API pública do DataJud;
- diários oficiais;
- consulta processual complementar;
- APIs comerciais parceiras.

No MVP, cada sinal também registra a origem simulada, para já refletir um desenho auditável.

Os conectores futuros mais aderentes a uma solução de produção seriam:

- `DataJud` para metadados processuais e movimentações;
- diários oficiais para publicações e eventos relevantes;
- APIs processuais comerciais para cobertura ampliada;
- scraping direcionado por número CNJ, apenas como camada complementar e rastreável.

### 4. Recuperação de casos similares

Cada caso histórico é transformado em uma representação textual curta:

`classe + assunto + fase + réu`

Depois, o pipeline aplica:

- `TfidfVectorizer`
- `cosine_similarity`

Isso produz uma lista ranqueada de casos comparáveis, que servem tanto para o score quanto para a justificativa.

### 5. Grafo relacional

O grafo é montado com `networkx` e exibido com `Plotly`. Ele conecta:

- processo atual;
- autor;
- réu;
- classe;
- assunto;
- tribunal;
- casos similares.

O papel do grafo aqui é explicativo e contextual: ele mostra como o caso está conectado a padrões históricos e ajuda a defender a proposta sugerida.

### 6. Modelo preditivo

O baseline de aceite usa `Logistic Regression` com:

- variáveis categóricas codificadas por `OneHotEncoder`;
- variáveis numéricas padronizadas com `StandardScaler`.

Features usadas:

- classe;
- assunto;
- fase;
- réu;
- valor da causa;
- proxy de movimentações;
- proxy de dias em aberto;
- proxy de audiência;
- tentativa prévia de acordo;
- taxa histórica de acordo do réu;
- taxa histórica de acordo do assunto;
- taxa histórica de acordo da classe;
- taxa de acordo entre casos similares;
- mediana da razão `acordo / valor da causa`.

Esta escolha foi deliberada para o MVP:

- é rápida de treinar e explicar;
- funciona bem como baseline tabular;
- deixa claro onde entram futuras evoluções com `LightGBM`, `CatBoost` e features de grafo.

### 7. Motor de proposta

A proposta é construída a partir de:

- probabilidade estimada de aceite;
- mediana da razão de acordo dos casos similares;
- valor da causa;
- alternativa à vista e alternativa parcelada.

O MVP devolve:

- chance estimada de aceite;
- valor sugerido à vista;
- parcelamento sugerido;
- fatores mais relevantes;
- justificativa narrativa.

## Interface

O app em `Streamlit` está organizado em quatro abas:

1. `PDF e extração`
   Exibe os campos estruturados e o texto extraído.
2. `Enriquecimento`
   Mostra sinais externos e casos similares.
3. `Grafo`
   Exibe relações do caso com entidades e comparáveis.
4. `Proposta final`
   Apresenta score, valores sugeridos e justificativa.

## Resultado demonstrado pelo MVP

Na execução demo atual, o pipeline já entrega:

- processo identificado a partir do PDF;
- histórico de casos semelhantes ranqueados por similaridade;
- sinais externos consolidados por origem;
- grafo relacional com entidades e comparáveis;
- probabilidade estimada de aceite;
- proposta à vista e parcelada;
- justificativa técnica baseada em evidências.

Exemplo de saída do pipeline:

```text
process_number: 0839393-11.2025.8.19.0001
defendant: Energia Leste S.A.
similar_cases_found: 5
acceptance_probability: 0.9428
suggested_cash_value: 8607.84
installment_count: 6
suggested_installment_value: 1549.41
sources_used: 4
graph_nodes: 13
graph_edges: 17
```

## Estrutura do repositório

```text
judicial-settlement-mvp/
├── app.py
├── main.py
├── requirements.txt
├── src/
│   ├── extraction.py
│   ├── enrichment.py
│   ├── graphing.py
│   ├── modeling.py
│   ├── pipeline.py
│   └── sample_data.py
├── tests/
│   └── test_pipeline.py
└── data/
    ├── raw/
    └── runtime/
```

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
streamlit run app.py
```

## Leitura correta do MVP

Este projeto foi desenhado como um `technical proposal MVP`, não como produto final.

O que ele prova:

- a arquitetura é viável;
- o fluxo de enriquecimento faz sentido;
- a camada de grafo agrega explicabilidade;
- o score e a proposta podem ser construídos sobre uma base enriquecida.

Próximos passos naturais:

- trocar parsing simples por OCR real;
- conectar integrações reais com DataJud e diários;
- ampliar a base histórica;
- calibrar o modelo com dados reais de acordos;
- adicionar agentes para enriquecimento, revisão e justificativa;
- expor a solução também via API.

## Evolução técnica sugerida

### Fase 1
- OCR real com `PaddleOCR` ou `DocTR`;
- conectores externos reais;
- aumento de cobertura documental.

### Fase 2
- base histórica mais rica;
- embeddings para busca vetorial;
- features relacionais extraídas do grafo;
- `LightGBM` ou `CatBoost` para score de aceite.

### Fase 3
- agentes para revisão e explicação;
- proposta guiada por política negocial;
- trilha de auditoria e revisão humana;
- serving por API para integração com fluxo jurídico maior.
