# RAG Workflow

I'm building a modern RAG in Python which processes both structured data (e.g. CSVs) and unstructured data (e.g. Markdowns)

---

## Dynamic Tools

* Structured data:
  * Upload time:
    * Store metadata (schema, rows, etc.) using DuckDB along with original file
  * Query time:
    * If any structured data exists, add a single dynamic tool `SQL_Query` with metadata (e.g. of all CSVs joined) as the tool's description
    * Use DuckDB for resolving the query
* Unstructured data:
  * Upload time:
    * Chunk (intelligently using LLM, if size is reasonable) and store in vector database (e.g. ChromaDB)
  * Query time:
    * If any unstructured data exists, add a single dynamic tool `Vector_Search`

### What do I mean by dynamic tool binding?

If we have `customers.csv` and `compliances.md`, set tools=[`SQL_Query`,`Vector_Search`]

If we have only `compliances.md`, set tools=[`Vector_Search`]

Instead of static binding like in LangChain, we need dynamic tool binding based on actual data

---

## Workflow: Plan and Execute

Let's take a query "summarize high-value customers and explain patterns". Resolving this requires first querying structured data to find high-value customers, then querying unstructured data to get more info about each of them and finally stitching them together to create a summary and explain patterns. Even though this is the best way to handle this scenario, the mistake would be to generalize this specific pattern and having a static (first structured query, then unstructured query) flow in all cases

What we need is a dynamic planner which creates a multi-step plan using `dynamic tools`, a way to execute the plan, and finally validate if we successfully resolved the query
