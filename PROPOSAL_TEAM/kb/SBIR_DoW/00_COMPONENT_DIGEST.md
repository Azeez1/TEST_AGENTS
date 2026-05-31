# DoW FY26 SBIR — Component Digest

**Generated:** 2026-05-17 from parallel digestion of 8 component instruction PDFs (Army, DAF, DARPA, DHA, DLA, Navy, SCO, SOCOM) + the umbrella BAA Preface. Source PDFs in this folder.

**Reader assumption:** Dux Machina (hybrid AI advisory + implementation consultancy). Topic fit-scoring is biased toward applied AI, autonomy, advanced computing/software, decision-support, and AI-for-compliance use cases.

---

## CROSS-COMPONENT COMPARISON MATRIX

| Component | Release | Topics | Phase I $/PoP | Phase II / D2P2 $/PoP | CMMC | TABA | Tech Volume page limit | AI-fit topics |
|---|---|---|---|---|---|---|---|---|
| **Army** | 26.BX_R1 | 3 (1 xTech-gated) | $150–300K / 1–6 mo | varies; Phase II Enhancement $500K | L1 (Phase I) | **YES** dual-provider (Army-preferred $6.5K *added*; firm-selected $6.5K *in cap*) | **7 pp** Phase I / **15 pp** D2P2 | 1 (NV001 ITV Blockchain) |
| **DAF / Air Force** | 26.BZ_R1 D2P2 | 4 | — | $1.7M–$2M / 15–24 mo | L2 (Self) | **NO** | 35 pp/slides | 4 (all topics AI, but high feasibility bar) |
| **DARPA** | 26.BZ_R2 | 6 (5 Phase I + 1 dual D2P2) | $250K / 6–9 mo | DV010 D2P2: $600K + $600K / 12+12 mo | L2 (Self) | **YES** $6.5K / $50K (must be in overhead, listed as subcontractor) | **10pp white paper + 5 slides** (Phase I) / **20pp + 15 slides** (D2P2) — UNIQUE FORMAT | 1 strong (DV010 Low Resource Computing) + 2 stretch |
| **DHA** | 26.BZ_R1 v3 | 5 (1 D2P2) | $300K / 6 mo | $1.4M / 24 mo | L1 (I) / L2 (II) | **NO** (DHA-specific prohibition; CRP replaces) | 20 pp Phase I / 40 pp Phase II | 1 partial (NV004 biomarker wearable) |
| **DLA** | 26.BZ_R2 | **10** | $100K / up to 12 mo | $1M / up to 24 mo | L2 (Self) | **NO** | 20 pp + ORAL pitch (15 slides, 15min) for "Highly Acceptable" | **5 strong** (NV004 Decision Intel, NV005 Agentic Cyber, NV006 AI-RMF, NV007 STRIKE AI, NV009 WSRP) |
| **Navy** | 26.BZ_DP2_R1 v2 | 5 (NAVAIR 4 + NAVSEA 1) | — | $1.4M (NAVAIR) / $2M (NAVSEA); split Base + Option | L2 (Self) + SPRS upload required | **YES** $25K Phase II / $50K seq Phase II (counts inside cap) | 30 pp total (20 Feasibility + 10 Phase II Snapshot); **MUST use navysbir.com template** | 2 strong (DV042 AI/ML Avionics, DV044 SHM-ML) |
| **OSW-SCO** | 26.BZ_D2P2_R2 | 2 (both D2P2) | — | **$2M / 12 mo** (DV003 topic body says 18 mo — flag) | **L1** | **NO** | 15 pp total (5 Justification + 10 Technical) | **2/2** (DV003 GenAI for Compliance, DV004 Game-theoretic AI) |
| **SOCOM** | 26.BZ_DP2_R1 v2 | 2 (both D2P2) | — | DV001 $1M / DV002 **$3.5M** / 12 mo each (OTA) | L2 (Self) | **NO** (explicitly prohibited) | **10 pp** (only first 10 evaluated) | 1 strong (DV002 IRONWALKER — AI/AR manufacturing) |

**Total topics in bundle:** 37 across 8 components.

**TABA-friendly components:** Army, DARPA, Navy. **TABA-prohibited:** DAF, DLA, DHA, SCO, SOCOM (5 of 8).

**Page-limit extremes:** Army Phase I @ 7 pp (tightest) → DHA Phase II @ 40 pp (most generous). DARPA's white-paper + slide-deck format is the outlier and demands separate preparation.

**CMMC L1 (lowest barrier):** Army Phase I, DHA Phase I, SCO. Everyone else needs **L2 Self** at minimum (110 NIST 800-171 controls).

---

## RANKED TOPIC SHORTLIST FOR DUX MACHINA

**Tier 1 — Direct AI-consultancy fit, lower barriers:**

| Topic ID | Component | $ / PoP | Why it fits |
|---|---|---|---|
| **DLA26BZ02-NV004** | DLA | $100K → $1M | Enterprise digital thread + decision intelligence across Celonis/SAP/Oracle/ServiceNow/UiPath — pure AI advisory + integration play |
| **DLA26BZ02-NV006** | DLA | $100K → $1M | AI-Assisted RMF Pre-Adjudication — AI for ATO/compliance automation; classic "AI-for-paperwork" Dux Machina sweet spot |
| **OSW26BZ02-DV003** | SCO | $2M / 12 mo | GenAI for Secure Workflow Automation (SCGs, PPPs, OPSEC, insider threat) — high $, but needs cleared personnel + prior classified DoW work |
| **DLA26BZ02-NV005** | DLA | $100K → $1M | Agentic AI for defensive cyber + pen testing |

**Tier 2 — Strong fit but harder bar:**

| Topic ID | Component | $ / PoP | Why it fits / what's hard |
|---|---|---|---|
| **DPA26BZ02-DV010** | DARPA | $250K Phase I OR $1.2M D2P2 | Low Resource Computing — semantic overlays for legacy hardware; great fit, DARPA's white-paper format is a different beast |
| **DLA26BZ02-NV007** | DLA | $100K → $1M | STRIKE AI — AI-enabled mission planning for OT/critical infra defense |
| **DLA26BZ02-NV009** | DLA | $100K → $1M | Predictive sustainment / readiness analytics (WSRP) |
| **SOC26BZ01-DV002** | SOCOM | **$3.5M / 12 mo** | IRONWALKER — AI/AR expeditionary manufacturing; biggest single $ in the bundle, requires AR/manufacturing hardware partner |
| **DON26BZ01-DV042** | Navy NAVAIR | up to $1.4M | AI/ML avionics troubleshooting + AR overlay + on-device chatbot |
| **DON26BZ01-DV044** | Navy NAVSEA | up to $2M | Passive SHM with ML defect classification (ship hulls); digital-twin adjacent |
| **OSW26BZ02-DV004** | SCO | $2M / 12 mo | Game-theoretic AI for COA generation / wargaming (Nash-equilibrium self-play) |

**Tier 3 — Partial fit, deprioritize:**

- ARM26BX01-NV001 (Army — ITV Blockchain): AI angle is partial; blockchain hardware focus
- DAF26BZ01-DV007 (DAF — CHORD): closest DAF fit but needs SECRET clearance + existing fielded debrief tool
- DHA26BZ01-NV004 (DHA — biomarker wearable): hardware-dominated, only signal processing is AI-shaped

---

## STRATEGIC NOTES

1. **DLA is the highest-value target for Dux Machina** — 5 of 10 topics are direct AI/decision-intelligence/compliance plays, $100K Phase I entry barrier, no TABA admin overhead, L2 self-assessment CMMC (achievable). Downside: oral pitch gate for "Highly Acceptable" proposals adds a presentation deliverable.

2. **SCO is the highest-dollar / highest-bar play** — $2M for 12 months on pure AI topics, but both topics anticipate classified Phase II work, US-owned/operated NISPOM compliance, and prior classified DoW work. Not feasible without a cleared partner.

3. **DARPA DV010 (Low Resource Computing)** is the cleanest single-topic shot for a pure software/AI play — but DARPA's white-paper + slide-deck format means you can't reuse a standard Technical Volume; budget separate prep time.

4. **SOCOM DV002 IRONWALKER ($3.5M)** is the largest single award in the bundle. Needs an AR/manufacturing hardware partner; OTA contract vehicle (not standard FAR) so cost-proposal approach differs.

5. **Navy DP2 topics require the navysbir.com template** — non-compliance = automatic rejection. This is a procedural trap.

6. **Five of eight components forbid TABA** — Dux Machina cannot bake commercialization-support fees into those proposals.

7. **All components inherit DoW Preface evaluation criteria** (technical merit > PI quals > commercial potential), but DON, SOCOM, and DLA add their own evaluation overlays.

---

## ARTIFACT INVENTORY

- `00_BAA_Preface.pdf` — DoW 2026 SBIR umbrella (49 pp)
- `SBIR_components/Army_26.BX_R1.pdf` (38 pp)
- `SBIR_components/DAF_AF_26.BZ_R1_D2P2.pdf` (24 pp)
- `SBIR_components/DARPA_SBIR_26.BZ_R2.pdf` (40 pp)
- `SBIR_components/DHA_26.BZ_R1_v3.pdf` (20 pp)
- `SBIR_components/DLA_SBIR_26.BZ_R2.pdf` (31 pp)
- `SBIR_components/NAVY_26.BZ_DP2_R1_v2.pdf` (26 pp)
- `SBIR_components/SCO_SBIR_26BZ_D2P2_R2.pdf` (13 pp)
- `SBIR_components/SOCOM_26.BZ_DP2_R1_v2.pdf` (13 pp)

**Text extracts (UTF-8) for indexing:** `C:\Users\sabaa\AppData\Local\Temp\sbir_components\`

**Total source corpus:** ~254 pages of authoritative BAA + component instructions, ready for Pinecone indexing or `query_knowledge_base` retrieval during proposal writing.
