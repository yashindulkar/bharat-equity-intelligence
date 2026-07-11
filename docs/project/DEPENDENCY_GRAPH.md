# Dependency Graph

```mermaid
flowchart TD
  H["Human/legal decisions"] --> L["Licensed field-level data path"]
  L --> C["Provider and canonical contracts"]
  C --> S["Security master + immutable raw store"]
  S --> P["PIT fundamentals, prices, actions"]
  P --> Q["Quality gates + lineage"]
  Q --> F["Sector-aware features"]
  F --> D["Deterministic score + abstention CLI"]
  D --> B["Bias-safe backtest"]
  B --> V["Independent validation"]
  H --> U["Suitability/privacy approval"]
  U --> R["Portfolio risk"]
  D --> R
  V --> R
  R --> A["Secured private application"]
  A --> M["ML challenger / shadow use"]
  M --> X["Separately gated broker expansion"]
```

Work may proceed in parallel only when contracts are stable and files do not overlap. Licensing blocks real ingestion; suitability blocks personalized actions; independent validation blocks backtest claims; security/privacy review blocks personal data and external AI.
