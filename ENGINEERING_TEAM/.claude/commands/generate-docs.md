# Generate Documentation

Create comprehensive technical documentation suite.

## What This Does

Technical-writer creates complete documentation with API docs and architecture diagrams.

## Usage

```
/generate-docs [scope: api | architecture | user | full]
```

## Example

```
/generate-docs api
/generate-docs architecture
/generate-docs full
```

## Process

### API Documentation (technical-writer + backend-architect)

1. **API Reference**
   - OpenAPI/Swagger specification
   - Endpoint documentation
   - Request/response examples
   - Authentication guide
   - Error code reference
   - Rate limiting details

2. **API Guides**
   - Getting started guide
   - Authentication setup
   - Common use cases
   - Code examples (multiple languages)
   - Postman collection

### Architecture Documentation (system-architect + technical-writer)

3. **System Architecture**
   - High-level architecture diagram (Mermaid.js)
   - Component diagrams
   - Data flow diagrams
   - Sequence diagrams
   - Deployment architecture
   - Technology stack overview

4. **Architecture Decision Records (ADRs)**
   - Key technical decisions
   - Context and rationale
   - Alternatives considered
   - Consequences
   - Status (proposed, accepted, deprecated)

### User Documentation (technical-writer + ui-ux-designer)

5. **User Guides**
   - Getting started tutorial
   - Feature guides
   - How-to articles
   - Troubleshooting
   - FAQ
   - Video tutorials (if applicable)

6. **Admin Documentation**
   - Installation guide
   - Configuration reference
   - Deployment guide
   - Monitoring and maintenance
   - Backup and recovery

### Developer Documentation (technical-writer + cto)

7. **Development Guides**
   - Development environment setup
   - Code contribution guidelines
   - Coding standards
   - Git workflow
   - Testing guidelines
   - Release process

8. **Database Documentation** (database-architect)
   - Schema diagrams (ERD)
   - Table documentation
   - Relationship descriptions
   - Migration guides
   - Query examples

## Deliverables

**API Documentation:**
- OpenAPI specification (YAML/JSON)
- Interactive API docs (Swagger UI / ReDoc)
- Postman collection
- Getting started guide

**Architecture Documentation:**
- Architecture diagrams (Mermaid.js + PNG exports)
- ADR documents (Markdown)
- Technology stack documentation
- Deployment architecture guide

**User Documentation:**
- User guide (Markdown + PDF)
- Tutorial videos (if applicable)
- FAQ document
- Troubleshooting guide

**Developer Documentation:**
- README.md
- CONTRIBUTING.md
- Development setup guide
- Code style guide

## Documentation Standards

- **Clarity:** Non-technical users can understand
- **Completeness:** All features documented
- **Accuracy:** Code examples work as-is
- **Up-to-date:** Matches current version
- **Searchable:** Good information architecture

## Time Estimate

- API only: 2-3 hours
- Architecture only: 2-3 hours
- User docs only: 3-4 hours
- Full suite: 6-10 hours

## Output Formats

- Markdown (for Git/GitHub)
- PDF (for distribution)
- HTML (for documentation sites)
- OpenAPI YAML/JSON (for API)

## Documentation Site

Optionally generate documentation site using:
- MkDocs
- Docusaurus
- GitBook
- Sphinx
