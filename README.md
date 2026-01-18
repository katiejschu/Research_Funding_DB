# Research Funding Ecosystem Explorer  
*A Graph-Based Visualization & Exploration Tool for Research Funding Decisions*

## Overview
This project models research funding as a **connected ecosystem** and provides interactive, graph-based visualizations to support **exploration, sense-making, and decision awareness**.

Rather than producing definitive rankings or conclusions, the tool helps users *see* how funding relationships form, cluster, and evolve — enabling more informed conversations, questions, and strategic decisions.

---

## Why Graph-Based Exploration?
Research funding decisions are inherently relational:
- Investigators collaborate across institutions
- Funding agencies shape research directions
- Topics overlap and evolve over time
- A small number of actors often connect many others

Traditional tables and dashboards summarize *what* happened.
Graph visualizations help reveal *how* and *why* it happened.

This project emphasizes **visual structure and relational context** over isolated metrics.

---

## Intended Use
This tool is designed to support:
- Exploratory analysis by research administration offices
- Strategic planning and portfolio review
- Identification of collaboration patterns
- Hypothesis generation for deeper analysis
- Communication between technical and non-technical stakeholders

It is **not** intended to:
- Produce final performance rankings
- Replace expert judgment
- Make automated funding decisions

---

## Core Concept
Each entity involved in research funding is represented as a node, and their relationships are modeled as edges. Users can visually explore how:

- Grants connect investigators and institutions
- Funding agencies influence research communities
- Research themes cluster or bridge domains
- AI-related funding patterns differ from the broader ecosystem

Understanding emerges through **navigation, comparison, and context**, not single-number scores.

---

## Data & Graph Model
**Node Types**
- `Grant`
- `PrincipalInvestigator`
- `Institution`
- `FundingAgency`
- `ResearchTheme`

**Relationship Types**
- `FUNDED_BY`
- `AWARDED_TO`
- `LED_BY`
- `ASSOCIATED_WITH`
- `COLLABORATES_WITH`

The model prioritizes interpretability and visual clarity.

---

## Visualization & Exploration Features
- Interactive graph views of funding networks
- Subgraph filtering (e.g., AI-tagged grants)
- Visual comparison of institutional or thematic clusters
- Contextual highlighting of connectors and bridges
- Drill-down exploration from high-level views to individual grants

Graph algorithms (e.g., centrality, community detection) are used **as lenses**, not verdicts — to guide exploration rather than dictate outcomes.

---

## Tools & Technologies
- **Neo4j** – Graph database & visualization
- **Cypher** – Relationship-driven querying
- **Python** – Data preparation and enrichment
- **Streamlit** – Interactive exploration interface (prototype)

---

## Example Questions This Tool Helps Explore
- How are research communities structured across institutions?
- Which investigators or themes connect otherwise separate clusters?
- Where does AI-related funding sit within the broader ecosystem?
- How concentrated or distributed are funding relationships?

These questions are intentionally open-ended and exploratory.

---

## Project Structure
```text
├── data/
│   ├── raw/
│   └── processed/
├── neo4j/
│   ├── schema/
│   └── cypher_queries/
├── analysis/
│   └── exploratory_views/
├── app/
│   └── streamlit_app.py
├── docs/
│   └── methodology.md
└── README.md
