# Gemini File Search Integration (Backup RAG System)

This document explains the Gemini File Search integration in the RFP Proposal Team system, which provides a fully managed backup RAG (Retrieval-Augmented Generation) system.

## Overview

**Gemini File Search** is Google's fully managed RAG-as-a-Service that automatically handles:
- Document chunking (automatic, optimized)
- Embedding generation (free)
- Vector storage (free)
- Semantic search and retrieval (free)
- Built-in citations and grounding

This integration serves as a **backup/fallback** to the primary Pinecone RAG system.

---

## Why Use Gemini File Search as Backup?

### Advantages

✅ **Zero Infrastructure** - Fully managed, no vector DB to maintain
✅ **Cost-Effective** - Storage and queries are FREE (only pay $0.15/1M tokens for initial indexing)
✅ **Minimal Setup** - Upload files and start querying in minutes
✅ **Built-in Grounding** - Automatic citations showing source documents
✅ **Auto-Chunking** - Google optimizes chunk sizes automatically
✅ **Reliability** - Google-scale infrastructure and uptime

### Trade-offs vs Pinecone

❌ **No Custom Chunking** - Cannot control framework-specific chunk strategies
❌ **LLM Lock-in** - Must use Gemini 2.5 models (no GPT-4o or Claude)
❌ **Less Metadata Control** - Limited custom metadata filtering
❌ **Generic Chunking** - Not optimized for compliance document sections

### When to Use It

1. **Backup/Fallback** - When Pinecone is unavailable or experiencing issues
2. **Cost Optimization** - For development/testing to save on Pinecone costs
3. **Comparison Testing** - To benchmark retrieval quality against Pinecone
4. **Rapid Prototyping** - Quick setup for proof-of-concept work
5. **Gemini Workflows** - When already using Gemini models

---

## Architecture Comparison

| Component | Pinecone (Primary) | Gemini File Search (Backup) |
|-----------|-------------------|----------------------------|
| **Vector DB** | Pinecone Serverless | Google-managed (hidden) |
| **Embeddings** | OpenAI text-embedding-3-small | Gemini Embedding (auto) |
| **Chunking** | Framework-aware (1000-2000 chars) | Auto-chunking (generic) |
| **LLM** | GPT-4o / GPT-4o-mini | Gemini 2.5 Pro/Flash only |
| **Metadata** | Rich custom metadata | Basic metadata |
| **Cost (Storage)** | $0.01/GB/month | FREE |
| **Cost (Queries)** | $0.0004/1K queries | FREE |
| **Cost (Indexing)** | One-time embedding cost | $0.15/1M tokens |
| **Setup Complexity** | Medium | Very Low |

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd /home/user/TEST_AGENTS/PROPOSAL_TEAM
pip install -r requirements.txt
```

This installs `google-genai>=0.2.0` along with other dependencies.

### 2. Get Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Click **"Get API Key"** (requires Google account)
3. Copy your API key

### 3. Configure Environment Variables

Edit your `.env` file (copy from `.env.example` if needed):

```bash
# Gemini File Search (Backup RAG System)
GEMINI_API_KEY=your-actual-gemini-api-key-here
GEMINI_FILE_SEARCH_STORE=rfp-compliance-backup
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.3
GEMINI_ENABLED=true  # Set to true to enable
```

### 4. Verify Installation

Test that the Gemini client can be imported:

```bash
python3 -c "from tools.legacy.gemini_file_search import GeminiFileSearch; print('✓ Gemini integration ready')"
```

---

## Usage

### Option 1: Upload Script (Recommended)

Upload all compliance documents at once:

```bash
# Verify documents exist (dry run)
python scripts/upload_compliance_to_gemini.py --verify-only

# Upload all documents
python scripts/upload_compliance_to_gemini.py

# Upload specific framework only
python scripts/upload_compliance_to_gemini.py --framework cmmc

# Dry run (show what would be uploaded)
python scripts/upload_compliance_to_gemini.py --dry-run

# List available frameworks
python scripts/upload_compliance_to_gemini.py --list-frameworks
```

### Option 2: Python API

Use the `GeminiFileSearch` class directly:

```python
from pathlib import Path
from tools.legacy.gemini_file_search import GeminiFileSearch

# Initialize client
gemini = GeminiFileSearch()

# Create or get file search store
store_name = gemini.get_or_create_store("rfp-compliance-backup")

# Upload a single document
pdf_path = Path("/path/to/CMMC_ModelOverview.pdf")
metadata = {
    "framework_id": "cmmc",
    "framework_name": "CMMC",
    "sector": "government",
    "document_type": "compliance_framework"
}
file_name = gemini.upload_file(pdf_path, metadata)
print(f"Uploaded: {file_name}")

# Upload multiple documents
file_paths = [Path(f) for f in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]]
uploaded = gemini.upload_files_batch(file_paths)
print(f"Uploaded {len(uploaded)} files")

# Query the knowledge base
query = "What are the CMMC Level 2 requirements for access control?"
results = gemini.query(query, top_k=10)

for result in results:
    print(f"Score: {result['score']}")
    print(f"Text: {result['text'][:200]}...")
    print(f"Metadata: {result['metadata']}")
    print()

# Query with AI-generated response and citations
result = gemini.query_with_context(
    "Explain CMMC scoping for Level 2 assessments"
)
print("AI Response:", result['response'])
print("\nSources:")
for source in result['sources']:
    print(f"  - {source['segment']}")
```

### Option 3: Integration with Existing RAG Pipeline

Modify your retrieval code to use Gemini as fallback:

```python
from tools.legacy.retrieval import KnowledgeBase  # Pinecone
from tools.legacy.gemini_file_search import GeminiFileSearch, GEMINI_AVAILABLE
from tools.legacy.config import config

def query_knowledge_base(query_text: str, top_k: int = 10):
    """Query KB with automatic fallback to Gemini."""

    # Try Pinecone first
    try:
        kb = KnowledgeBase()
        results = kb.query(query_text, top_k=top_k)
        print("✓ Using Pinecone")
        return results
    except Exception as e:
        print(f"⚠️  Pinecone unavailable: {e}")

        # Fallback to Gemini if enabled
        if config.gemini.enabled and GEMINI_AVAILABLE:
            print("→ Falling back to Gemini File Search")
            gemini = GeminiFileSearch()
            results = gemini.query(query_text, top_k=top_k)
            return results
        else:
            raise Exception("No RAG system available")
```

---

## Management Operations

### List Uploaded Files

```python
gemini = GeminiFileSearch()
files = gemini.list_files()

for file in files:
    print(f"Name: {file['display_name']}")
    print(f"Metadata: {file['metadata']}")
    print()
```

### Get Store Statistics

```python
gemini = GeminiFileSearch()
stats = gemini.get_store_stats()

print(f"Store: {stats['display_name']}")
print(f"Total files: {stats['total_files']}")
print(f"Model: {stats['model']}")
```

### Delete a File

```python
gemini = GeminiFileSearch()
success = gemini.delete_file("files/abc123xyz")
print(f"Deleted: {success}")
```

---

## Supported File Formats

Gemini File Search supports:

- ✅ PDF (`.pdf`)
- ✅ Plain text (`.txt`)
- ✅ Markdown (`.md`)
- ✅ Microsoft Word (`.docx`, `.doc`)
- ✅ Microsoft Excel (`.xlsx`, `.xls`)
- ✅ Microsoft PowerPoint (`.pptx`)
- ✅ CSV (`.csv`)
- ✅ HTML (`.html`)
- ✅ Code files (`.py`, `.js`, `.java`, etc.)

---

## Cost Analysis

### Gemini File Search Pricing

| Component | Cost |
|-----------|------|
| **Storage** | FREE |
| **Query Embeddings** | FREE |
| **Initial Indexing** | $0.15 per 1M tokens |
| **Gemini API Calls** | Varies by model |

### Example: Indexing 21 Compliance PDFs

Assuming average 500 pages per PDF, ~500 words/page:

```
21 PDFs × 500 pages × 500 words = 5,250,000 words ≈ 7M tokens
Indexing cost: 7M tokens × $0.15/1M = $1.05 (one-time)
```

**Total first-year cost:** ~$1-2 for indexing + Gemini API usage

Compare to Pinecone: ~$1,500/year (storage + queries + embeddings)

**Savings: ~$1,498/year** ✅

---

## Comparison Testing

To compare retrieval quality between Pinecone and Gemini:

```python
def compare_rag_systems(query: str):
    """Compare Pinecone vs Gemini for the same query."""

    # Query Pinecone
    kb_pinecone = KnowledgeBase()
    pinecone_results = kb_pinecone.query(query, top_k=5)

    # Query Gemini
    gemini = GeminiFileSearch()
    gemini_results = gemini.query(query, top_k=5)

    # Compare
    print("=" * 80)
    print("PINECONE RESULTS")
    print("=" * 80)
    for i, result in enumerate(pinecone_results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   {result['text'][:200]}...")
        print(f"   Metadata: {result['metadata'].get('framework_id')}")

    print("\n" + "=" * 80)
    print("GEMINI RESULTS")
    print("=" * 80)
    for i, result in enumerate(gemini_results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   {result['text'][:200]}...")
        print(f"   Metadata: {result['metadata'].get('framework_id')}")
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'google.genai'"

**Solution:**
```bash
pip install google-genai
```

### "Gemini API key required"

**Solution:**
1. Get API key from: https://aistudio.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`
3. Verify it's loaded: `echo $GEMINI_API_KEY`

### "Failed to create file search store"

**Possible causes:**
- Invalid API key
- Network connectivity issues
- API quota exceeded (free tier limits)

**Solution:**
- Verify API key is correct
- Check internet connection
- Check quota: https://aistudio.google.com/app/prompts

### Uploads succeed but queries return no results

**Cause:** File store may not be fully indexed yet (can take a few minutes)

**Solution:** Wait 2-5 minutes after upload before querying

### "GEMINI_AVAILABLE = False"

**Cause:** `google-genai` package not installed

**Solution:**
```bash
pip install google-genai
# Restart Python interpreter
```

---

## API Reference

### `GeminiFileSearch` Class

#### Constructor

```python
GeminiFileSearch(
    api_key: Optional[str] = None,
    store_name: Optional[str] = None,
    model: Optional[str] = None
)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `create_file_search_store(display_name)` | Create new file search store | Store resource name |
| `get_or_create_store(display_name)` | Get existing or create new store | Store resource name |
| `upload_file(file_path, metadata)` | Upload single file | File resource name |
| `upload_files_batch(file_paths, metadata_list)` | Upload multiple files | List of file names |
| `query(query_text, top_k, metadata_filter)` | Search documents | List of results |
| `query_with_context(query_text, top_k)` | Query with AI response | Dict with response + sources |
| `delete_file(file_name)` | Delete a file | Boolean success |
| `list_files()` | List all files in store | List of file metadata |
| `get_store_stats()` | Get store statistics | Dict with stats |

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (required) | Gemini API key from Google AI Studio |
| `GEMINI_FILE_SEARCH_STORE` | `rfp-compliance-backup` | Name of the file search store |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model for queries |
| `GEMINI_TEMPERATURE` | `0.3` | Temperature for response generation |
| `GEMINI_ENABLED` | `false` | Enable/disable Gemini integration |

### Available Gemini Models

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| `gemini-2.0-flash-exp` | Fast queries | ⚡⚡⚡ | ⭐⭐⭐ |
| `gemini-2.5-pro` | Complex reasoning | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| `gemini-2.5-flash` | Balanced | ⚡⚡⚡ | ⭐⭐⭐⭐ |

---

## Best Practices

1. **Use as Backup, Not Primary** - Keep Pinecone as primary for your custom chunking strategy
2. **Test Retrieval Quality** - Compare results before relying on it for production
3. **Monitor Costs** - Track Gemini API usage in Google AI Studio
4. **Metadata Strategy** - Use simple, consistent metadata (Gemini has limited filtering)
5. **Batch Uploads** - Upload all documents at once for efficiency
6. **Wait After Upload** - Allow 2-5 minutes for indexing before querying
7. **Error Handling** - Implement proper fallback logic between Pinecone and Gemini

---

## Next Steps

1. ✅ Set up Gemini API key
2. ✅ Upload compliance documents
3. ✅ Test queries and compare with Pinecone
4. ✅ Integrate into retrieval pipeline with fallback logic
5. ✅ Monitor performance and cost

---

## Support

- **Gemini API Documentation:** https://ai.google.dev/gemini-api/docs/file-search
- **Get API Key:** https://aistudio.google.com/app/apikey
- **API Quotas:** https://aistudio.google.com/app/prompts
- **Community:** https://discuss.ai.google.dev/

---

## Version History

- **v1.0.0** (2025-11-19) - Initial Gemini File Search integration
  - Core API wrapper
  - Upload script for compliance documents
  - Configuration and environment setup
  - Documentation and examples
