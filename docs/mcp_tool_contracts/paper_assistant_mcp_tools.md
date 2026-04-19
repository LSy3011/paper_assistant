# Paper Assistant MCP Tool Contracts

This file defines the planned MCP tools for exposing Paper Assistant as a reusable knowledge service.

## paper_search

Purpose: retrieve relevant paper chunks.

Input:

```json
{
  "query": "How does VecPAC handle precision-aware vectorization?",
  "top_k": 5
}
```

Output:

```json
{
  "results": [
    {
      "paper": "VecPAC_A_Vectorizable_and_Precision-Aware_CGRA.pdf",
      "chunk": "Relevant text snippet",
      "score": 0.82,
      "reason": "Matches precision-aware vectorization and CGRA architecture"
    }
  ]
}
```

## paper_ask

Purpose: answer a question with GraphRAG.

Input:

```json
{
  "question": "Compare VecPAC and DRIPS in terms of CGRA optimization strategy.",
  "mode": "hybrid"
}
```

Output:

```json
{
  "answer": "Generated answer",
  "mode": "hybrid",
  "contexts": [
    {
      "paper": "paper name",
      "chunk": "supporting context"
    }
  ]
}
```

## graph_neighbors

Purpose: inspect graph relationships around a technical entity.

Input:

```json
{
  "entity": "CGRA",
  "depth": 2
}
```

Output:

```json
{
  "entity": "CGRA",
  "neighbors": [
    {
      "target": "VecPAC",
      "relation": "optimized_by",
      "depth": 1
    }
  ]
}
```

## list_papers

Purpose: list indexed papers.

Input:

```json
{}
```

Output:

```json
{
  "papers": [
    "VecPAC_A_Vectorizable_and_Precision-Aware_CGRA.pdf"
  ]
}
```

