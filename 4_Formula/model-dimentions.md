The logs are clear: your **Kilo-Code** client is still trying to force a square peg into a round hole. Specifically, it is sending **4096-dimensional** vectors to a Qdrant collection that was hard-coded for **1536**.

### Why you are seeing "Got 4096"

Even though you pulled Nomic, Kilo-Code is likely using a default **Llama 3** or **Mistral** model for embeddings. These models natively output 4096 dimensions.

To fix this, you must synchronize the "Expected" (Qdrant) and the "Got" (Kilo-Code/Ollama).

---

### Step 1: Fix the Qdrant Collection

Qdrant cannot dynamically change the dimension size of an existing collection. You must delete the current one and recreate it with the size your model is actually outputting.

**Run this Python snippet to reset the collection:**

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient("localhost", port=6333)

# The specific collection ID from your logs
collection_name = "ws-4c18aac6061cace0"

# 1. Delete the mismatched collection
client.delete_collection(collection_name=collection_name)

# 2. Recreate it with the 4096 dimensions your model is sending
client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=4096, 
        distance=models.Distance.COSINE
    ),
)
print(f"Collection {collection_name} reset to 4096 dimensions.")

```

---

### Step 2: Ensure Kilo-Code uses Nomic (Optional)

If you specifically want to use **Nomic** (which is 768 dimensions and much faster/lighter than 4096), you need to change the settings inside the **Kilo-Code** UI or config file:

1. Set the **Embedding Model** to `nomic-embed-text`.
2. If you do this, change the `size` in the Python script above to **768** instead of 4096.

### Troubleshooting Checklist

* **Check Ollama's active model:** Run `ollama ps` in your terminal while Kilo-Code is running to see which model is actually being invoked.
* **Port Check:** Ensure Qdrant is still on `6333` and Ollama is on `11434`.
* **Wipe Storage:** If the collection won't delete, you can manually clear the `./storage` folder mentioned in your first log and restart Qdrant.

**Would you like me to help you find the specific configuration file for Kilo-Code to point it at the Nomic model?**