I'm building a modern RAG in Python which processes both structured data (e.g. CSVs) and unstructured data (e.g. Markdowns)

For unstructured data, using a vector database is the best way to store and process the data

For structured data, using a vector database can work in certain cases (e.g. "find the balance of John"), but isn't efficient in some other cases (e.g. "how many people have balance more than 10,000?"). So let's use DuckDB and Pandas (when applicable) for structured data

A naive approach would be to use a simple hybrid approach where the paths diverge for structured vs unstructured, and finally gets stitched back by the LLM. This can address the use cases mentioned above, but lack the flexibility to address more complex cases where one path is dependent on the results of the other(s). For example, examine a query like "summarize high-value customers and explain patterns". Resolving this requires first querying structured data to find high-value customers, then querying unstructured data to get more info about them and finally stitch them to create a summary. Again, the mistake would be to generalize this specific pattern and having a fixed (first structured, then unstructured) flow in all cases

What we need is a dynamic planner which creates a plan considering all the available data sources and tools, a way to execute the plan, and finally validate if we successfully resolved the query

Let's brainstorm and design this

---

Do we need LangGraph for this? Or can we build something minimal ourselves using Pydantic and basic tools?
