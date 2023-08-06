# VecDB

A minified version of [AI-Transform](https://github.com/RelevanceAI/ai-transform)

# Quickstart

```python
import os
import vecdb

api_key = os.getenv("DEVELOPMENT_TOKEN")

client = vecdb.Client(api_key)

client.delete_dataset("all-my-documents")
dataset = client.create_dataset("all-my-documents")

dataset.insert(
    documents=[
        {"_id": "doc1", "text": "tiger", "category": "land"},
        {"_id": "doc2", "text": "lion", "category": "land"},
        {"_id": "doc3", "text": "tigr", "category": "land"},
        {"_id": "doc4", "text": "car", "category": "land"},
    ]
)

```

*or*

```python
dataset.insert(
    data=["elephant", "zebra", "giraffe", "horse", "warthog"],
    metadata=[
        {"category": "land"},
        {"category": "land"},
        {"category": "land"},
        {"category": "land"},
        {"category": "land"},
    ],
)

```

## Vector Search

The text `horse` is vectorized on the fly

```python
dataset.search(page_size=4, text="horse")

```


```python
import random

vec = [random.random() for _ in range(768)]
dataset.search(vector=vec)

```

### Multiple vectors (or different model)


```python
import random

query = [
    {"model": "all-mpnet-base-v2", "vector": [random.random() for _ in range(768)], "field": "text_vector_"}
    for _ in range(2)
]
dataset.search(query=query)

```

## Regular Search

### Regular filters

```python
dataset.search(select_fields=["text"], filters=dataset["text"] == "tiger")

```

### Document Ids

```python
dataset.search(select_fields=["text"], filters=dataset["ids"] == "doc2")

```

### Multiple Ids

```python
dataset.search(select_fields=["text"], filters=dataset["ids"] == ["doc2", "doc3"])

```
### Delete with filters

```python
dataset.delete(filters=dataset["ids"] == "doc4")
docs = dataset.get_all()

fn = lambda x: x["_id"]
docs = [fn(doc) for doc in docs["documents"]]
docs

```

## Vectorize Locally


```python
import os
import vecdb

api_key = os.getenv("DEVELOPMENT_TOKEN")

client = vecdb.Client(api_key)

dataset_id = "custom-vector-documents"
client.delete_dataset(dataset_id)
dataset = client.create_dataset(dataset_id)

documents = [
    {"_id": "doc1", "text": "tiger"},
    {"_id": "doc2", "text": "lion"},
    {"_id": "doc3", "text": "tigr"},
    {"_id": "doc4", "text": "car"},
]

```


```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
model = model.eval()

```


```python
texts = [str(document.get("text")).strip() for document in documents]
vectors = model.encode(texts).tolist()

for document, vector in zip(documents, vectors):
    document["text_vector_"] = vector

dataset.insert(documents=documents)

```
