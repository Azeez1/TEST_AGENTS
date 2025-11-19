"""
Configuration management for RFP Agent.
Loads environment variables and agent configuration.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = Path(__file__).parent


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(default="openai")
    model_small: str = Field(default="gpt-4o-mini")
    model_strong: str = Field(default="gpt-4o")
    api_key: str = Field(default="")
    temperature: float = Field(default=0.3)
    max_tokens: int = Field(default=4000)


class PineconeConfig(BaseModel):
    """Pinecone vector database configuration."""

    api_key: str = Field(default="")
    environment: str = Field(default="us-east-1")
    index_name: str = Field(default="rfp-knowledge-base")
    namespace: str = Field(default="default")


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""

    provider: str = Field(default="openai")
    model: str = Field(default="text-embedding-3-small")
    dimension: int = Field(default=1536)


class GeminiConfig(BaseModel):
    """Gemini File Search configuration (backup RAG system)."""

    api_key: str = Field(default="")
    file_search_store_name: str = Field(default="rfp-compliance-backup")
    model: str = Field(default="gemini-2.0-flash-exp")
    temperature: float = Field(default=0.3)
    enabled: bool = Field(default=False)


class Config:
    """Main configuration class."""

    def __init__(self):
        # LLM Configuration
        self.llm = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            model_small=os.getenv("LLM_MODEL_SMALL", "gpt-4o-mini"),
            model_strong=os.getenv("LLM_MODEL_STRONG", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY", ""),
        )

        # Pinecone Configuration
        self.pinecone = PineconeConfig(
            api_key=os.getenv("PINECONE_API_KEY", ""),
            environment=os.getenv("PINECONE_ENV", "us-east-1"),
            index_name=os.getenv("PINECONE_INDEX", "rfp-knowledge-base"),
            namespace=os.getenv("PINECONE_NAMESPACE", "default"),
        )

        # Embedding Configuration
        self.embedding = EmbeddingConfig(
            provider=os.getenv("EMBEDDING_PROVIDER", "openai"),
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            dimension=int(os.getenv("EMBEDDING_DIMENSION", "1536")),
        )

        # Gemini Configuration (Backup RAG)
        self.gemini = GeminiConfig(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            file_search_store_name=os.getenv("GEMINI_FILE_SEARCH_STORE", "rfp-compliance-backup"),
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.3")),
            enabled=os.getenv("GEMINI_ENABLED", "false").lower() == "true",
        )

        # Paths
        self.schemas_dir = SRC_ROOT / "schemas"
        self.prompts_dir = SRC_ROOT / "prompts"
        self.templates_dir = SRC_ROOT / "templates"
        self.config_dir = SRC_ROOT / "config"

        # Processing settings
        self.chunk_size = 6000
        self.chunk_overlap = 400
        self.max_retrieval_results = 10

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Load agent configuration
        self.agents = self._load_agents_config()

    def _load_agents_config(self) -> Dict[str, Any]:
        """Load agents.yml configuration."""
        agents_file = self.config_dir / "agents.yml"
        if not agents_file.exists():
            return {}

        with open(agents_file, "r") as f:
            config = yaml.safe_load(f)

        # Expand environment variables in config
        return self._expand_env_vars(config)

    def _expand_env_vars(self, data: Any) -> Any:
        """Recursively expand environment variables in config."""
        if isinstance(data, dict):
            return {k: self._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            var_name = data[2:-1]
            return os.getenv(var_name, data)
        return data

    def get_prompt(self, prompt_name: str) -> str:
        """Load a prompt template."""
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_file}")

        with open(prompt_file, "r") as f:
            return f.read()

    def get_template(self, template_name: str) -> str:
        """Load a Jinja template."""
        template_file = self.templates_dir / f"{template_name}.md"
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        with open(template_file, "r") as f:
            return f.read()


# Global config instance
config = Config()
