# Technical/Service Approach Section Prompt

## Objective
Draft the Technical or Service Approach section that directly answers RFP requirements with evidence-backed claims.

## Structure (Answer-First Pattern)

### For Each Requirement:
1. **Direct Answer** (first sentence)
   - Mirror the requirement verbatim
   - State your capability clearly
   - Example: "We shall provide 24/7 NOC coverage with <2min response time."

2. **Process/Architecture** (2-3 paragraphs)
   - How you'll deliver
   - Tools and methodologies
   - Integration points
   - Quality controls

3. **Proof Callout** (evidence box)
   ```
   📊 PROOF: [Metric or evidence]
   Source: [Case study, cert, or RAG citation]
   ```

4. **Risks & Mitigations** (table)
   | Risk | Probability | Impact | Mitigation |
   |------|-------------|--------|------------|
   | ... | Low/Med/High | ... | ... |

5. **So-What** (last sentence)
   - Benefit to evaluator/buyer
   - Example: "This approach reduces Government risk while ensuring Day-1 operational readiness."

## RAG Usage
- For technical standards: `rag.search("NIST 800-171 requirement X", filters={jurisdiction:"US"})`
- For compliance: `rag.search("FAR 15.X requirement", filters={standard:"FAR"})`
- Always cite: **Title + Source URL**

## Federal-Specific
- Reference evaluation criteria from Section M
- Map each paragraph to a specific eval factor
- Include compliance matrix cross-references

## Enterprise-Specific
- Lead with ROI/TCO outcomes
- Emphasize pilot/POC plan
- Security integration prominently
- Change management approach

## Quality Checks
- [ ] Every "shall/must/will" answered in first sentence
- [ ] ≥60% of value statements have proof
- [ ] All technical terms defined on first use
- [ ] Graphics have So-What captions
- [ ] Risk register complete
