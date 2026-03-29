Build barebones (just a subset needed to run and test RAG flow, skip non-essential stuff like linting, unittests, etc. for now) backend based on requirements in @README.md. Refer to @docs/ai/rag-workflow.md for the RAG data flow

Avoid vendor lock by using abstractions like OpenRouter where applicable

---

We are starting the project from scratch. The only files in the current directory are:

```
$ tree
.
├── backend
│   └── venv/*
├── rag-reference-data
│   ├── call_scripts.md
│   ├── fdcpa_quick_reference.md
│   ├── glossary.md
│   └── sample_accounts.csv
└── README.md
```

Don't read `backend/venv/*`. I already ran `source backend/venv/bin/activate` in the current session, so you can directly use binaries like `python3`, etc.