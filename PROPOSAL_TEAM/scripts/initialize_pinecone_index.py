#!/usr/bin/env python3
"""
Initialize Pinecone index for RFP Knowledge Base
Configures the index with optimal settings for compliance documentation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

# Fix Windows encoding issues with Unicode
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

def initialize_pinecone_index():
    """Initialize Pinecone index with optimal settings for compliance documents"""

    # Get configuration from environment
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "rfp-knowledge-base")
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

    if not api_key:
        print("❌ Error: PINECONE_API_KEY not found in environment variables")
        return False

    print(f"🔄 Initializing Pinecone client...")

    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)

        # Check if index already exists
        existing_indexes = pc.list_indexes()
        index_names = [index.name for index in existing_indexes]

        if index_name in index_names:
            print(f"⚠️ Index '{index_name}' already exists")

            # Get index details
            index = pc.Index(index_name)
            stats = index.describe_index_stats()

            print(f"\n📊 Existing Index Details:")
            print(f"  - Dimension: {stats.get('dimension', 'Unknown')}")
            print(f"  - Total vectors: {stats.get('total_vector_count', 0):,}")
            print(f"  - Namespaces: {list(stats.get('namespaces', {}).keys())}")

            # Ask if user wants to delete and recreate
            response = input(f"\n❓ Do you want to DELETE and recreate the index? (yes/no): ")

            if response.lower() == 'yes':
                print(f"🗑️ Deleting index '{index_name}'...")
                pc.delete_index(index_name)

                # Wait for deletion to complete
                print("⏳ Waiting for deletion to complete...")
                time.sleep(10)
            else:
                print("✅ Using existing index")
                return True

        # Create new index
        print(f"\n🚀 Creating new Pinecone index: {index_name}")
        print(f"  - Dimension: {dimension} (optimized for text-embedding-3-large)")
        print(f"  - Metric: cosine (best for semantic similarity)")
        print(f"  - Cloud: AWS")
        print(f"  - Region: us-east-1")

        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        # Wait for index to be ready
        print("⏳ Waiting for index to be ready...")
        time.sleep(5)

        # Verify index creation
        index = pc.Index(index_name)
        stats = index.describe_index_stats()

        print(f"\n✅ Index '{index_name}' created successfully!")
        print(f"\n📊 Index Configuration:")
        print(f"  - Dimension: {stats.get('dimension', dimension)}")
        print(f"  - Metric: cosine")
        print(f"  - Status: Ready")
        print(f"  - Namespaces: Will be created during document upload")
        print(f"    • compliance_frameworks - For compliance PDFs")
        print(f"    • company_knowledge - For company docs (resumes, case studies)")

        # Show next steps
        print(f"\n📝 Next Steps:")
        print(f"  1. Run 'python scripts/index_compliance_frameworks.py' to index compliance docs")
        print(f"  2. Run 'python scripts/index_company_knowledge.py' to index company docs")
        print(f"  3. Test retrieval with 'python scripts/test_pinecone_search.py'")

        return True

    except Exception as e:
        print(f"❌ Error initializing Pinecone index: {str(e)}")
        return False

def verify_configuration():
    """Verify all required configuration is present"""

    print("🔍 Verifying configuration...")

    required_vars = {
        "PINECONE_API_KEY": "Pinecone API key",
        "OPENAI_API_KEY": "OpenAI API key (for embeddings)",
        "ANTHROPIC_API_KEY": "Anthropic API key (for proposal writing)",
        "EMBEDDING_MODEL": "Embedding model name",
        "EMBEDDING_DIMENSION": "Embedding dimension",
        "LLM_MODEL_STRONG": "Strong LLM model for writing",
    }

    missing = []
    configured = []

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            configured.append(f"  ✅ {description}: Configured")
            if var == "EMBEDDING_MODEL":
                configured.append(f"     Model: {value}")
            elif var == "EMBEDDING_DIMENSION":
                configured.append(f"     Dimension: {value}")
            elif var == "LLM_MODEL_STRONG":
                configured.append(f"     Model: {value}")
        else:
            missing.append(f"  ❌ {description}: Missing")

    print("\n".join(configured))

    if missing:
        print("\n⚠️ Missing configuration:")
        print("\n".join(missing))
        return False

    return True

def main():
    """Main execution"""

    print("=" * 60)
    print("🚀 Pinecone Index Initialization for RFP Knowledge Base")
    print("=" * 60)

    # Verify configuration
    if not verify_configuration():
        print("\n❌ Please configure missing environment variables in config/.env")
        return

    # Initialize index
    if initialize_pinecone_index():
        print("\n✨ Pinecone index initialization complete!")
    else:
        print("\n❌ Failed to initialize Pinecone index")

if __name__ == "__main__":
    main()