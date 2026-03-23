# Campaign Spec: {Campaign Name}

| Field | Value |
|-------|-------|
| **Author** | {name} |
| **Date** | {YYYY-MM-DD} |
| **Team** | MARKETING_TEAM |
| **Status** | Draft / In Review / Approved / Live |
| **Campaign Type** | Product Launch / Brand Awareness / Lead Gen / Content Series |

## Objective

{What is this campaign trying to achieve? Be specific and measurable.}

**Primary KPI:** {e.g., 500 qualified leads in 30 days}
**Secondary KPIs:** {e.g., 10K impressions, 5% CTR, 200 email signups}

## Target Audience

| Attribute | Detail |
|-----------|--------|
| **Primary audience** | {Job title, company size, industry} |
| **Pain point** | {What problem keeps them up at night?} |
| **Decision stage** | Awareness / Consideration / Decision |
| **Channels they use** | {LinkedIn, Twitter/X, TikTok, email, etc.} |

## Brand Voice Requirements

- **Tone:** {Reference brand_voice.json or specify: calm power, stoic precision, etc.}
- **Messaging pillars:** {Key themes to reinforce}
- **Avoid:** {What NOT to say — competitors to not mention, claims to not make}

## Content Deliverables

| # | Type | Channel | Format | Owner Agent |
|---|------|---------|--------|-------------|
| 1 | {Blog post} | {Website} | {2000 words} | {copywriter} |
| 2 | {LinkedIn post} | {LinkedIn} | {carousel + caption} | {social-media-manager} |
| 3 | {Email sequence} | {Gmail} | {3-email drip} | {email-specialist} |
| 4 | {Header image} | {LinkedIn} | {1200x627 PNG} | {visual-designer} |

## Timeline

| Phase | Dates | Deliverables |
|-------|-------|-------------|
| Content creation | {start} - {end} | All content drafted |
| Review & approval | {start} - {end} | Final versions approved |
| Launch | {date} | First posts go live |
| Optimization | {start} - {end} | Iterate based on performance |

## Acceptance Criteria

```gherkin
Given the campaign is launched
When 7 days have elapsed
Then all scheduled content has been published on time

Given a LinkedIn post is published
When viewed by target audience
Then engagement rate exceeds {X}%

Given the email sequence is sent
When recipients open the first email
Then open rate exceeds {X}%
```

## Out of Scope

- {Paid advertising / organic only}
- {Channels not included}
- {Follow-up campaigns}

## Dependencies

- {Brand assets: logo, colors, fonts from visual_guidelines.json}
- {Email list: segment from {source}}
- {Approvals: {who needs to sign off}}

## Notes

{Links to inspiration, competitor campaigns, previous campaign results}
