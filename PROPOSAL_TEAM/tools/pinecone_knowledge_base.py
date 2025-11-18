"""
Pinecone Knowledge Base Manager
Handles indexing and retrieval of compliance framework documents with framework-aware chunking.
"""

import os
import hashlib
import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import re

# Import user's priority frameworks
try:
    from .user_priority_frameworks import (
        USER_PRIORITY_FRAMEWORKS,
        FRAMEWORK_BY_ID,
        UserFramework
    )
except ImportError:
    from user_priority_frameworks import (
        USER_PRIORITY_FRAMEWORKS,
        FRAMEWORK_BY_ID,
        UserFramework
    )

@dataclass
class DocumentChunk:
    """Represents a chunk of a compliance document."""
    chunk_id: str
    document_id: str
    framework_id: str
    framework_name: str
    chunk_text: str
    chunk_index: int
    total_chunks: int
    section_title: Optional[str]
    page_numbers: List[int]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

@dataclass
class IndexedDocument:
    """Represents an indexed compliance document."""
    document_id: str
    framework_id: str
    framework_name: str
    file_path: str
    file_name: str
    total_chunks: int
    index_status: str  # "pending", "indexed", "failed"
    metadata: Dict[str, Any]

class FrameworkAwareChunker:
    """
    Intelligent chunking for compliance documents based on framework type.
    """

    def __init__(self):
        # Framework-specific chunking patterns
        self.section_patterns = {
            "cmmc": [
                r"(?:Level\s+\d+)\s+(?:Practices|Requirements)",
                r"(?:AC|AT|AU|CA|CM|IA|IR|MA|MP|PE|PS|RA|SC|SI)[-.\s]\d+",
                r"Assessment\s+(?:Objectives|Methods)",
                r"Scoping\s+(?:Guidance|Requirements)"
            ],
            "fedramp": [
                r"(?:Low|Moderate|High)\s+Baseline",
                r"Control\s+(?:Family|Families)",
                r"(?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|RA|SA|SC|SI|SR)[-.\s]\d+",
                r"Continuous\s+Monitoring",
                r"Authorization\s+(?:Process|Package)"
            ],
            "nist_800_171": [
                r"\d+\.\d+\s+(?:Basic|Derived)\s+Security\s+Requirements",
                r"(?:Access|Audit|Configuration|Identification|Incident|Maintenance|Media|Personnel|Physical|Risk|Security|System)",
                r"Organization[-\s]Defined\s+Parameters",
                r"(?:NFO|CUI)\s+(?:Protection|Requirements)"
            ],
            "nist_800_53": [
                r"(?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|PT|RA|SA|SC|SI|SR)[-.\s]\d+",
                r"Control\s+(?:Family|Families)",
                r"(?:Low|Moderate|High)\s+(?:Baseline|Impact)",
                r"Privacy\s+Controls",
                r"Supply\s+Chain\s+(?:Controls|Risk)"
            ],
            "hipaa": [
                r"(?:Administrative|Physical|Technical)\s+Safeguards",
                r"(?:Privacy|Security|Breach)\s+Rule",
                r"§\s*16[024]\.\d+",
                r"Required|Addressable",
                r"Business\s+Associate"
            ],
            "pci_dss": [
                r"Requirement\s+\d+(?:\.\d+)?",
                r"(?:Build|Protect|Maintain|Implement|Monitor|Test)",
                r"Customized\s+Approach",
                r"Testing\s+Procedures",
                r"Guidance"
            ],
            "gdpr": [
                r"Article\s+\d+",
                r"Chapter\s+[IVX]+",
                r"(?:Controller|Processor|Data\s+Subject)",
                r"Recital\s+\d+",
                r"(?:Lawfulness|Consent|Rights|Principles)"
            ],
            "glba": [
                r"§\s*314\.\d+",
                r"(?:Safeguards|Privacy|Pretexting)\s+(?:Rule|Provisions)",
                r"Risk\s+Assessment",
                r"Information\s+Security\s+Program",
                r"Customer\s+Information"
            ],
            "dfars": [
                r"252\.204[-.\s]70\d+",
                r"(?:Covered|Controlled)\s+Defense\s+Information",
                r"(?:Incident|Cyber|Cloud)\s+(?:Reporting|Requirements)",
                r"72[-\s]hour",
                r"External\s+Service\s+Provider"
            ]
        }

        # Default chunking parameters by framework
        self.chunk_params = {
            "cmmc": {"size": 1500, "overlap": 200},
            "fedramp": {"size": 2000, "overlap": 300},
            "nist_800_171": {"size": 1500, "overlap": 200},
            "nist_800_53": {"size": 2000, "overlap": 300},
            "hipaa": {"size": 1200, "overlap": 150},
            "pci_dss": {"size": 1500, "overlap": 200},
            "gdpr": {"size": 1200, "overlap": 150},
            "soc2": {"size": 1000, "overlap": 100},
            "iso_27001": {"size": 1000, "overlap": 100},
            "glba": {"size": 1200, "overlap": 150},
            "dfars": {"size": 1500, "overlap": 200}
        }

    def chunk_document(self, text: str, framework_id: str, document_id: str,
                      file_name: str) -> List[DocumentChunk]:
        """
        Chunk a document using framework-aware strategies.

        Args:
            text: Document text
            framework_id: Framework identifier
            document_id: Unique document ID
            file_name: Original file name

        Returns:
            List of DocumentChunk objects
        """
        framework = FRAMEWORK_BY_ID.get(framework_id)
        if not framework:
            # Fallback to generic chunking
            return self._generic_chunking(text, framework_id, document_id, file_name)

        # Try section-based chunking first
        chunks = self._section_based_chunking(text, framework_id, document_id, file_name)

        if not chunks:
            # Fallback to sliding window chunking
            chunks = self._sliding_window_chunking(text, framework_id, document_id, file_name)

        return chunks

    def _section_based_chunking(self, text: str, framework_id: str,
                               document_id: str, file_name: str) -> List[DocumentChunk]:
        """Chunk based on framework-specific sections."""
        chunks = []
        patterns = self.section_patterns.get(framework_id, [])

        if not patterns:
            return chunks

        # Compile patterns
        compiled_patterns = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]

        # Find all section boundaries
        section_starts = []
        for pattern in compiled_patterns:
            for match in pattern.finditer(text):
                section_starts.append({
                    "pos": match.start(),
                    "title": match.group(0).strip(),
                    "pattern": pattern.pattern
                })

        if not section_starts:
            return chunks

        # Sort by position
        section_starts.sort(key=lambda x: x["pos"])

        # Create chunks from sections
        framework = FRAMEWORK_BY_ID[framework_id]
        params = self.chunk_params.get(framework_id, {"size": 1500, "overlap": 200})
        max_chunk_size = params["size"]

        for i, section in enumerate(section_starts):
            # Determine section end
            if i < len(section_starts) - 1:
                section_end = section_starts[i + 1]["pos"]
            else:
                section_end = len(text)

            section_text = text[section["pos"]:section_end].strip()

            # If section is too large, split it
            if len(section_text) > max_chunk_size:
                sub_chunks = self._split_large_section(
                    section_text, max_chunk_size, params["overlap"]
                )
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_id = f"{document_id}_s{i:03d}_p{j:03d}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        framework_id=framework_id,
                        framework_name=framework.name,
                        chunk_text=sub_chunk,
                        chunk_index=len(chunks),
                        total_chunks=0,  # Will be updated later
                        section_title=section["title"],
                        page_numbers=self._estimate_page_numbers(section["pos"], len(text)),
                        metadata={
                            "file_name": file_name,
                            "section_pattern": section["pattern"],
                            "sub_chunk": j
                        }
                    ))
            else:
                chunk_id = f"{document_id}_s{i:03d}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    framework_id=framework_id,
                    framework_name=framework.name,
                    chunk_text=section_text,
                    chunk_index=len(chunks),
                    total_chunks=0,  # Will be updated later
                    section_title=section["title"],
                    page_numbers=self._estimate_page_numbers(section["pos"], len(text)),
                    metadata={
                        "file_name": file_name,
                        "section_pattern": section["pattern"]
                    }
                ))

        # Update total chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)

        return chunks

    def _sliding_window_chunking(self, text: str, framework_id: str,
                                document_id: str, file_name: str) -> List[DocumentChunk]:
        """Chunk using sliding window approach."""
        chunks = []
        framework = FRAMEWORK_BY_ID.get(framework_id)
        if not framework:
            framework = UserFramework(
                id=framework_id, name=framework_id, category="",
                keywords=set(), pdf_count=0, description="", requirements=[]
            )

        params = self.chunk_params.get(framework_id, {"size": 1500, "overlap": 200})
        chunk_size = params["size"]
        overlap = params["overlap"]

        # Split text into chunks
        start = 0
        while start < len(text):
            # Find chunk end
            end = min(start + chunk_size, len(text))

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end
                sentence_end = text[start:end].rfind('. ')
                if sentence_end > chunk_size * 0.8:  # If we're at least 80% through
                    end = start + sentence_end + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = f"{document_id}_c{len(chunks):04d}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    framework_id=framework_id,
                    framework_name=framework.name,
                    chunk_text=chunk_text,
                    chunk_index=len(chunks),
                    total_chunks=0,  # Will be updated later
                    section_title=None,
                    page_numbers=self._estimate_page_numbers(start, len(text)),
                    metadata={
                        "file_name": file_name,
                        "chunk_method": "sliding_window"
                    }
                ))

            # Move start position
            start = end - overlap if end < len(text) else end

        # Update total chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)

        return chunks

    def _generic_chunking(self, text: str, framework_id: str,
                         document_id: str, file_name: str) -> List[DocumentChunk]:
        """Generic chunking for unknown frameworks."""
        # Use default parameters
        return self._sliding_window_chunking(
            text, "generic", document_id, file_name
        )

    def _split_large_section(self, text: str, max_size: int, overlap: int) -> List[str]:
        """Split a large section into smaller chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + max_size, len(text))

            # Try to break at paragraph boundary
            if end < len(text):
                para_end = text[start:end].rfind('\n\n')
                if para_end > max_size * 0.7:
                    end = start + para_end

            chunks.append(text[start:end].strip())
            start = end - overlap if end < len(text) else end

        return chunks

    def _estimate_page_numbers(self, position: int, total_length: int) -> List[int]:
        """Estimate page numbers based on position."""
        # Assume ~3000 characters per page
        chars_per_page = 3000
        start_page = position // chars_per_page + 1
        end_page = min((position + 2000) // chars_per_page + 1,
                      total_length // chars_per_page + 1)
        return list(range(start_page, end_page + 1))

class PineconeKnowledgeBase:
    """
    Main Pinecone knowledge base manager for compliance frameworks.
    """

    def __init__(self, api_key: str = None, index_name: str = "rfp-knowledge-base"):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name
        self.namespace = "compliance_frameworks"
        self.chunker = FrameworkAwareChunker()

        # In production, initialize Pinecone client here
        self.pinecone_client = None  # Would be initialized with actual client

        # Track indexed documents
        self.indexed_documents: Dict[str, IndexedDocument] = {}

    def index_compliance_document(self, file_path: str, framework_id: str,
                                 text: str = None) -> IndexedDocument:
        """
        Index a compliance framework document.

        Args:
            file_path: Path to the document
            framework_id: Framework identifier
            text: Optional pre-extracted text

        Returns:
            IndexedDocument object
        """
        file_path = Path(file_path)
        file_name = file_path.name

        # Generate document ID
        doc_id = self._generate_document_id(framework_id, file_name)

        # Extract text if not provided
        if text is None:
            text = self._extract_text(file_path)

        # Chunk the document
        chunks = self.chunker.chunk_document(text, framework_id, doc_id, file_name)

        # Create indexed document record
        indexed_doc = IndexedDocument(
            document_id=doc_id,
            framework_id=framework_id,
            framework_name=FRAMEWORK_BY_ID.get(framework_id, UserFramework(
                id=framework_id, name=framework_id, category="",
                keywords=set(), pdf_count=0, description="", requirements=[]
            )).name,
            file_path=str(file_path),
            file_name=file_name,
            total_chunks=len(chunks),
            index_status="pending",
            metadata={
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "chunk_method": "framework_aware",
                "indexed_at": None
            }
        )

        # In production, would upload chunks to Pinecone here
        # For now, store in memory
        self.indexed_documents[doc_id] = indexed_doc
        indexed_doc.index_status = "indexed"

        return indexed_doc

    def index_all_priority_documents(self, compliance_folder: str) -> Dict[str, List[IndexedDocument]]:
        """
        Index all 21 priority framework documents.

        Args:
            compliance_folder: Path to compliance documents folder

        Returns:
            Dictionary mapping framework_id to list of IndexedDocument objects
        """
        compliance_path = Path(compliance_folder)
        indexed_by_framework = {}

        # Document mappings for the 21 PDFs
        document_mappings = {
            "cmmc": [
                "CMMC_32 CFR 170 (CMMC Program Rule).pdf",
                "CMMC_AssessmentGuideL1v2.pdf",
                "CMMC_AssessmentGuideL2v2.pdf",
                "CMMC_ModelOverview.pdf",
                "CMMC_ScopingGuideL1v2.pdf",
                "CMMC_ScopingGuideL2v2.pdf"
            ],
            "fedramp": [
                "FEDRAMP_Agency_Authorization_Playbook.pdf",
                "FEDRAMP_CSP_Authorization_Playbook.pdf",
                "FEDRAMP_CSP_Continuous_Monitoring_Performance_Management_Guide.pdf"
            ],
            "nist_800_171": [
                "NIST.SP.800-171r3.pdf",
                "NIST.SP.800-171Ar3.pdf"
            ],
            "nist_800_53": [
                "NIST.SP.800-53r5.pdf",
                "NIST.SP.800-53Ar5.pdf",
                "NIST.SP.800-53B.pdf"
            ],
            "hipaa": [
                "HIPAA_privacysummary.pdf",
                "HIPAA_security101.pdf"
            ],
            "pci_dss": [
                "PCI-DSS-v4_0_1.pdf"
            ],
            "gdpr": [
                "GDPR_CELEX_32016R0679_EN_TXT.pdf"
            ],
            "glba": [
                "GLBA_16 CFR Part 314 (up to date as of 9-30-2025).pdf",
                "GLBA_Privacy_viii-1.1.pdf"
            ],
            "dfars": [
                "CMMC_DFARS 2019-D041 (Cybersecurity Requirements).pdf"
            ]
        }

        # Index each document
        for framework_id, pdf_files in document_mappings.items():
            indexed_docs = []

            for pdf_file in pdf_files:
                file_path = compliance_path / pdf_file

                if file_path.exists():
                    print(f"Indexing {framework_id}: {pdf_file}")
                    indexed_doc = self.index_compliance_document(
                        str(file_path), framework_id
                    )
                    indexed_docs.append(indexed_doc)
                else:
                    print(f"[WARNING] File not found: {pdf_file}")

            indexed_by_framework[framework_id] = indexed_docs

        # Handle frameworks without PDFs
        for fw_id in ["soc2", "iso_27001"]:
            indexed_by_framework[fw_id] = []
            print(f"[INFO] {fw_id}: No PDFs available (proprietary framework)")

        return indexed_by_framework

    def search(self, query: str, framework_ids: List[str] = None,
              top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks in the knowledge base.

        Args:
            query: Search query
            framework_ids: Optional list of framework IDs to filter
            top_k: Number of results to return

        Returns:
            List of search results with metadata
        """
        # In production, this would query Pinecone
        # For now, return mock results

        results = []

        # Filter by framework if specified
        docs_to_search = self.indexed_documents.values()
        if framework_ids:
            docs_to_search = [
                doc for doc in docs_to_search
                if doc.framework_id in framework_ids
            ]

        # Mock search results
        for doc in list(docs_to_search)[:top_k]:
            results.append({
                "document_id": doc.document_id,
                "framework_id": doc.framework_id,
                "framework_name": doc.framework_name,
                "file_name": doc.file_name,
                "relevance_score": 0.85,  # Mock score
                "chunk_text": f"Relevant content from {doc.framework_name}...",
                "metadata": doc.metadata
            })

        return results

    def get_framework_evidence(self, framework_id: str, requirements: List[str],
                              top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve evidence for specific framework requirements.

        Args:
            framework_id: Framework identifier
            requirements: List of requirements to find evidence for
            top_k: Number of results per requirement

        Returns:
            Dictionary mapping requirements to evidence
        """
        evidence_map = {}

        for req in requirements:
            # Search for evidence
            results = self.search(req, [framework_id], top_k)
            evidence_map[req[:100]] = results  # Truncate requirement key

        return evidence_map

    def _generate_document_id(self, framework_id: str, file_name: str) -> str:
        """Generate unique document ID."""
        hash_input = f"{framework_id}_{file_name}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _extract_text(self, file_path: Path) -> str:
        """Extract text from document (PDF extraction would go here)."""
        # In production, use PyPDF2 or similar to extract PDF text
        # For now, return placeholder
        return f"Text content from {file_path.name}"

    def get_index_statistics(self) -> Dict[str, Any]:
        """Get statistics about indexed documents."""
        stats = {
            "total_documents": len(self.indexed_documents),
            "frameworks_indexed": {},
            "total_chunks": 0,
            "index_status": {}
        }

        for doc in self.indexed_documents.values():
            # Count by framework
            if doc.framework_id not in stats["frameworks_indexed"]:
                stats["frameworks_indexed"][doc.framework_id] = {
                    "name": doc.framework_name,
                    "documents": 0,
                    "chunks": 0
                }
            stats["frameworks_indexed"][doc.framework_id]["documents"] += 1
            stats["frameworks_indexed"][doc.framework_id]["chunks"] += doc.total_chunks

            # Count by status
            if doc.index_status not in stats["index_status"]:
                stats["index_status"][doc.index_status] = 0
            stats["index_status"][doc.index_status] += 1

            # Total chunks
            stats["total_chunks"] += doc.total_chunks

        return stats

    def export_index_metadata(self, output_file: str):
        """Export index metadata to JSON file."""
        metadata = {
            "index_name": self.index_name,
            "namespace": self.namespace,
            "statistics": self.get_index_statistics(),
            "documents": []
        }

        for doc in self.indexed_documents.values():
            metadata["documents"].append({
                "document_id": doc.document_id,
                "framework_id": doc.framework_id,
                "framework_name": doc.framework_name,
                "file_name": doc.file_name,
                "total_chunks": doc.total_chunks,
                "status": doc.index_status
            })

        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Index metadata exported to: {output_file}")

# Export main classes
__all__ = [
    'PineconeKnowledgeBase',
    'FrameworkAwareChunker',
    'DocumentChunk',
    'IndexedDocument'
]