# Brand Voice Compliance Check

Ensure all content matches Dux Machina brand voice and guidelines.

## What This Does

The editor agent reviews content for brand voice compliance (target tone score 7+).

## Usage

```
/brand-check [file path or content]
```

## Example

```
/brand-check blog-post.md
/brand-check "Check this email copy: [paste content]"
```

## Process

1. **Content Analysis** (editor)
   - Review against Dux Machina brand guidelines
   - Tone: "Tech Samurai meets McKinsey Strategist"
   - Score content on brand alignment (0-10 scale)
   - Identify off-brand language

2. **Feedback Report**
   - Overall brand score
   - Line-by-line feedback on issues
   - Specific suggestions for improvement
   - Examples of better alternatives

3. **Revision** (if score < 7)
   - Rewrite problematic sections
   - Maintain original intent
   - Elevate to brand standards

## Deliverables

- Brand compliance report with score
- Annotated content with suggested changes
- Revised version (if needed)

## Brand Voice Guidelines

**Dux Machina Voice:**
- Authoritative yet accessible
- Strategic thinking with tactical execution
- Data-driven decision making
- No fluff, pure value
- Tech-forward without jargon
- Confident but not arrogant

**Avoid:**
- Overhype and marketing speak
- Buzzwords without substance
- Passive voice
- Generic platitudes
- Excessive enthusiasm

## Time Estimate

10-20 minutes per document
