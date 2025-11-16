# Knowledge Base

This directory stores reusable content that gets retrieved during proposal generation.

## Directory Structure

```
kb/
├── resumes/              # Personnel resumes for staffing sections
├── past_performance/     # Project examples and case studies
├── case_studies/         # Detailed success stories
├── technical/            # Technical documentation and writeups
├── boilerplate/          # Reusable proposal content
├── certifications/       # Company and personnel certifications
└── company_info/         # Company background and capabilities
```

## Document Types

### resumes/
Personnel resumes used for staffing requirements.
- Format: PDF or DOCX
- Naming: `lastname_firstname.pdf`
- Include: Skills, experience, education, clearances

### past_performance/
Project examples demonstrating relevant experience.
- Format: PDF or DOCX
- Naming: `project_name_YYYY.pdf`
- Include: Client, scope, outcomes, metrics

### case_studies/
Detailed success stories.
- Format: PDF or DOCX
- Naming: `casestudy_topic_YYYY.pdf`
- Include: Challenge, solution, results, testimonials

### technical/
Technical documentation and white papers.
- Format: PDF, DOCX, or Markdown
- Naming: `topic_description.pdf`
- Include: Architecture, methodology, tools, standards

### boilerplate/
Reusable proposal content sections.
- Format: Markdown preferred
- Naming: `section_name.md`
- Include: Company info, standard approaches, QA processes

### certifications/
Company and personnel certifications.
- Format: PDF
- Naming: `cert_type_YYYY.pdf`
- Include: ISO, CMMI, industry-specific certs

### company_info/
Company background and capabilities.
- Format: Markdown or DOCX
- Include: History, mission, capabilities, differentiators

## Indexing to Pinecone

To make documents searchable, index them to Pinecone:

```bash
# Index resumes
python ../dux_rfp_agent/scripts/index_kb.py \
  --input resumes \
  --type resume \
  --sector government

# Index past performance
python ../dux_rfp_agent/scripts/index_kb.py \
  --input past_performance \
  --type past_performance \
  --sector government

# Index technical docs
python ../dux_rfp_agent/scripts/index_kb.py \
  --input technical \
  --type technical_writeup
```

## Metadata Schema

Each indexed document includes:
- `doc_id`: Unique identifier
- `doc_type`: Document category
- `content_type`: full_document, section, paragraph
- `title`: Document title
- `sector`: Industry sectors (government, healthcare, etc.)
- `tags`: Skills, technologies, keywords
- `source_file`: Original filename

See `../dux_rfp_agent/src/dux_rfp_agent/schemas/pinecone_metadata.schema.json` for full schema.

## Best Practices

1. **Keep Updated**: Regularly add new projects and resumes
2. **Quality Over Quantity**: Only include high-quality, relevant content
3. **Consistent Format**: Use standard naming and structure
4. **Tag Appropriately**: Add relevant skills and keywords
5. **Version Control**: Track changes to important documents
6. **Sector Tagging**: Tag with applicable industries
7. **Review Annually**: Remove outdated content

## Usage During Proposal Generation

When processing an RFP, the system:
1. Extracts requirements from the RFP
2. Queries Pinecone KB using semantic search
3. Retrieves relevant resumes, projects, technical docs
4. Incorporates evidence into compliance matrix
5. Cites KB sources in proposal: `[KB: doc_id]`

The more comprehensive your KB, the better your automated proposals!
