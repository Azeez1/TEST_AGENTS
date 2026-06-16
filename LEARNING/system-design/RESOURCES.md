# System Design Resources

Curated, high-trust sources. Teaching claims are grounded here, not in parametric memory. Pruned ruthlessly — better five sharp sources than thirty mediocre ones.

## Knowledge

- [Book: _Designing Data-Intensive Applications_ (2nd ed.) — Martin Kleppmann (O'Reilly)](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/)
  The canonical, vendor-neutral text on why distributed systems are built the way they are. Reasons from fundamentals (reliability, scalability, maintainability) rather than tools. Use for: the *why* behind replication, partitioning, consistency, consensus. This is the spine of the whole mission.
- [The System Design Primer — donnemartin (GitHub, open source)](https://github.com/donnemartin/system-design-primer)
  Free, community-vetted (200k+ stars) study guide with worked examples (URL shortener, Twitter feed, etc.) and component breakdowns. Use for: interview-style walkthroughs and a map of standard components.
- [High Scalability (blog)](http://highscalability.com/)
  Real-world architecture teardowns of how large companies actually built their systems. Use for: concrete case studies that turn abstract patterns into "here's how X really did it."

## Wisdom (Communities)

- [r/ExperiencedDevs](https://www.reddit.com/r/ExperiencedDevs/) and [r/systemdesign](https://www.reddit.com/r/systemdesign/)
  Use for: critique of a design you've drafted, and "is this trade-off reasonable?" gut-checks from practitioners.
- _AI/agent-architecture angle:_ EZ's own multi-agent system (67 agents, 8 teams) is a live lab. Use it as the real-world test bed where classic patterns get applied — the best "community" here is shipping and observing.

## Gaps
- Need a strong, trusted source specifically on **AI/agent system architecture** from first principles (the "blend" half of the mission). To find in a later session — most distributed-systems canon predates LLM agents.
