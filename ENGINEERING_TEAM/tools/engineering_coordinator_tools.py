"""
Engineering Coordinator Tools
Intent classification and agent selection for CTO coordination
"""

from claude_agent_sdk import tool
import json


# Engineering request types and their agent mappings
ENGINEERING_INTENTS = {
    "build_feature": {
        "agents": ["technical-writer", "ui-ux-designer", "backend-architect", "frontend-developer", "test-engineer", "code-reviewer"],
        "description": "Full-stack feature development from PRD to deployment",
        "keywords": ["build", "create", "develop", "feature", "implement", "new feature"],
        "phases": ["planning", "design", "development", "testing", "review"]
    },
    "deploy_infrastructure": {
        "agents": ["devops-engineer", "security-auditor", "test-engineer", "technical-writer"],
        "description": "Infrastructure deployment and DevOps automation",
        "keywords": ["deploy", "infrastructure", "ci/cd", "kubernetes", "docker", "terraform", "helm"],
        "phases": ["infrastructure", "security", "validation", "documentation"]
    },
    "audit_security": {
        "agents": ["security-auditor", "code-reviewer", "technical-writer"],
        "description": "Security audit and vulnerability scanning",
        "keywords": ["security", "audit", "vulnerability", "scan", "compliance", "secrets"],
        "phases": ["scanning", "review", "reporting"]
    },
    "optimize_ai": {
        "agents": ["ai-engineer", "prompt-engineer", "technical-writer"],
        "description": "AI/LLM optimization and prompt engineering",
        "keywords": ["optimize", "ai", "prompt", "llm", "agent", "rag", "embedding"],
        "phases": ["analysis", "optimization", "benchmarking", "documentation"]
    },
    "design_database": {
        "agents": ["database-architect", "backend-architect", "technical-writer"],
        "description": "Database design and data modeling",
        "keywords": ["database", "schema", "data model", "migration", "sql", "nosql"],
        "phases": ["modeling", "architecture", "migration", "documentation"]
    },
    "design_ui": {
        "agents": ["ui-ux-designer", "frontend-developer", "technical-writer"],
        "description": "UI/UX design and implementation",
        "keywords": ["ui", "ux", "design", "wireframe", "user flow", "interface", "dashboard"],
        "phases": ["research", "wireframing", "implementation", "documentation"]
    },
    "troubleshoot_issue": {
        "agents": ["debugger", "test-engineer", "code-reviewer"],
        "description": "Debug and troubleshoot issues",
        "keywords": ["debug", "fix", "troubleshoot", "error", "issue", "bug", "problem"],
        "phases": ["diagnosis", "fix", "validation", "review"]
    },
    "create_tests": {
        "agents": ["test-engineer", "code-reviewer"],
        "description": "Test automation and quality assurance",
        "keywords": ["test", "testing", "qa", "quality", "coverage", "automation"],
        "phases": ["strategy", "implementation", "review"]
    },
    "review_code": {
        "agents": ["code-reviewer", "security-auditor", "test-engineer"],
        "description": "Code quality and security review",
        "keywords": ["review", "code review", "quality", "refactor", "improve"],
        "phases": ["review", "security", "testing", "recommendations"]
    },
    "create_documentation": {
        "agents": ["technical-writer"],
        "description": "Technical documentation creation",
        "keywords": ["document", "documentation", "prd", "spec", "api doc", "guide"],
        "phases": ["writing", "review"]
    },
    "design_api": {
        "agents": ["backend-architect", "technical-writer", "security-auditor"],
        "description": "API design and architecture",
        "keywords": ["api", "rest", "microservice", "backend", "architecture"],
        "phases": ["design", "documentation", "security review"]
    },
    "build_frontend": {
        "agents": ["ui-ux-designer", "frontend-developer", "code-reviewer"],
        "description": "Frontend development with React/Next.js",
        "keywords": ["frontend", "react", "next.js", "component", "responsive"],
        "phases": ["design", "implementation", "review"]
    }
}


@tool(
    "classify_engineering_request",
    "Classify engineering request to determine which specialist agents to invoke",
    {
        "user_request": str,
        "context": dict  # Optional: additional context like project info
    }
)
async def classify_engineering_request(args):
    """
    Classify engineering request based on content
    Returns intent category, recommended agents, and execution phases
    """
    user_request = args["user_request"].lower()
    context = args.get("context", {})

    # Score each intent
    intent_scores = {}
    for intent, config in ENGINEERING_INTENTS.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in user_request:
                score += 1
        intent_scores[intent] = score

    # Get highest scoring intent
    if max(intent_scores.values()) > 0:
        best_intent = max(intent_scores, key=intent_scores.get)
        intent_config = ENGINEERING_INTENTS[best_intent]

        result = {
            "intent": best_intent,
            "confidence": "high" if intent_scores[best_intent] >= 2 else "medium",
            "agents_to_invoke": intent_config["agents"],
            "phases": intent_config["phases"],
            "description": intent_config["description"],
            "user_request": args["user_request"]
        }
    else:
        # No clear intent - ask for clarification
        result = {
            "intent": "unclear",
            "confidence": "low",
            "agents_to_invoke": [],
            "phases": [],
            "description": "Unable to determine intent",
            "user_request": args["user_request"],
            "suggested_clarification": "Could you specify what type of engineering work you need? (e.g., build feature, deploy infrastructure, security audit, troubleshoot issue)"
        }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "get_engineer_capabilities",
    "Get detailed capabilities of a specific engineering agent",
    {
        "agent_name": str
    }
)
async def get_engineer_capabilities(args):
    """
    Return detailed capabilities of a specific engineering agent
    """
    agent_name = args["agent_name"]

    # Engineering agent capabilities database
    capabilities = {
        "devops-engineer": {
            "role": "Production DevOps automation specialist",
            "capabilities": [
                "Complete CI/CD pipelines (GitHub Actions)",
                "Infrastructure as Code (Terraform for AWS/GCP)",
                "Kubernetes deployments (Helm charts)",
                "Monitoring stack (Prometheus, Grafana)",
                "Security scanning (Trivy, kube-bench, gitleaks)",
                "Deployment strategies (blue-green, canary, rolling)"
            ],
            "outputs": ["CI/CD pipelines", "Terraform configs", "Helm charts", "Monitoring dashboards"],
            "tools": ["Docker", "Kubernetes", "Terraform", "Helm", "Prometheus"],
            "approach": "Production-ready configurations with 886 lines of battle-tested code",
            "best_for": "Complete deployment automation from containerization to production monitoring"
        },
        "frontend-developer": {
            "role": "Modern React application and UI component specialist",
            "capabilities": [
                "React component architecture (hooks, context, performance)",
                "Responsive CSS with Tailwind/CSS-in-JS",
                "State management (Redux, Zustand, Context API)",
                "Frontend performance optimization",
                "Accessibility (WCAG compliance)"
            ],
            "outputs": ["React components", "Responsive UIs", "Component libraries"],
            "tools": ["React", "Next.js", "TypeScript", "Tailwind CSS"],
            "approach": "Component-first, mobile-first, performance-focused",
            "best_for": "Modern web applications and component libraries"
        },
        "backend-architect": {
            "role": "Scalable API design and microservices architecture",
            "capabilities": [
                "RESTful API design with versioning",
                "Microservices architecture and service boundaries",
                "Database schema design (normalization, indexes)",
                "Caching strategies and performance optimization",
                "Security patterns (auth, rate limiting)"
            ],
            "outputs": ["API specifications", "Architecture diagrams", "Service designs"],
            "tools": ["OpenAPI", "Database modeling", "Architecture diagrams"],
            "approach": "Contract-first API design with horizontal scalability planning",
            "best_for": "Backend architecture for scalable systems"
        },
        "security-auditor": {
            "role": "Application security and vulnerability assessment",
            "capabilities": [
                "Hardcoded secret scanning (API keys, passwords)",
                "Vulnerability identification (OWASP Top 10)",
                "Authentication and authorization review",
                "Dependency vulnerability scanning",
                "Compliance audits (GDPR, HIPAA, SOC2)"
            ],
            "outputs": ["Security audit reports", "Vulnerability scans", "Compliance reports"],
            "tools": ["Bandit", "Safety", "pip-audit", "Trivy"],
            "approach": "Comprehensive security analysis with severity ratings",
            "best_for": "Security audits across all systems and API key management"
        },
        "technical-writer": {
            "role": "Technical documentation and specification specialist",
            "capabilities": [
                "Product Requirements Documents (PRDs)",
                "Technical specifications with architecture diagrams",
                "API documentation (OpenAPI/Swagger)",
                "System architecture diagrams (Mermaid, PlantUML)",
                "User guides and tutorials"
            ],
            "outputs": ["PRDs", "Technical specs", "API docs", "User guides"],
            "tools": ["Markdown", "Mermaid", "OpenAPI", "PlantUML"],
            "approach": "Clear, comprehensive documentation with diagrams",
            "best_for": "Complete technical documentation for all systems"
        },
        "ai-engineer": {
            "role": "LLM applications, RAG systems, and agent frameworks",
            "capabilities": [
                "LLM integration (OpenAI, Anthropic, open models)",
                "RAG systems (vector databases, embeddings)",
                "Prompt engineering and optimization",
                "Agent frameworks (LangChain, LangGraph, CrewAI)",
                "Token optimization and cost management"
            ],
            "outputs": ["RAG systems", "Agent frameworks", "Prompt optimizations"],
            "tools": ["LangChain", "Vector databases", "OpenAI", "Anthropic"],
            "approach": "Production-ready AI/ML systems with optimization",
            "best_for": "Optimizing all 35 agents and building RAG systems"
        },
        "ui-ux-designer": {
            "role": "User-centered design and interface systems",
            "capabilities": [
                "User research and persona development",
                "Wireframing (low and high-fidelity)",
                "Design systems and component libraries",
                "Accessibility (WCAG compliance)",
                "Information architecture and user flows"
            ],
            "outputs": ["Wireframes", "Design systems", "User flows", "Prototypes"],
            "tools": ["Figma", "Design systems", "User research"],
            "approach": "User needs first, progressive disclosure, consistent patterns",
            "best_for": "Complete design systems and user experience optimization"
        },
        "code-reviewer": {
            "role": "Expert code review for quality and maintainability",
            "capabilities": [
                "Code quality analysis (readability, naming)",
                "Security review (secrets, input validation)",
                "Error handling verification",
                "Test coverage assessment",
                "Performance considerations"
            ],
            "outputs": ["Code review reports", "Quality assessments", "Fix recommendations"],
            "tools": ["Git diff analysis", "Static analysis"],
            "approach": "Proactive review with priority-based feedback",
            "best_for": "Quality assurance across all codebases"
        },
        "test-engineer": {
            "role": "Comprehensive test automation and QA",
            "capabilities": [
                "Test pyramid strategy (unit, integration, E2E)",
                "Automation frameworks (Jest, Playwright, pytest)",
                "Performance testing (load, stress)",
                "Test suite management and CI/CD integration",
                "Coverage analysis and quality gates"
            ],
            "outputs": ["Test strategies", "Automation suites", "Quality reports"],
            "tools": ["Jest", "Playwright", "pytest", "Cypress"],
            "approach": "Test pyramid with CI/CD integration",
            "best_for": "Complete test automation strategies"
        },
        "prompt-engineer": {
            "role": "Expert LLM prompt optimization",
            "capabilities": [
                "Prompt techniques (few-shot, chain-of-thought)",
                "Model-specific optimization (Claude, GPT)",
                "Structured output formatting",
                "Constitutional AI principles",
                "Performance benchmarking"
            ],
            "outputs": ["Optimized prompts", "Prompt pipelines", "Benchmarks"],
            "tools": ["LLM APIs", "Prompt testing frameworks"],
            "approach": "Systematic optimization with benchmarking",
            "best_for": "Optimizing all 35 agent prompts for better performance"
        },
        "database-architect": {
            "role": "Database architecture and data modeling",
            "capabilities": [
                "Data modeling (ER design, normalization)",
                "Scalability planning (sharding, replication)",
                "Polyglot persistence (SQL, NoSQL, cache)",
                "Microservices data patterns (CQRS, event sourcing)",
                "Migration strategies with rollback"
            ],
            "outputs": ["Database schemas", "Data models", "Migration scripts"],
            "tools": ["Database design tools", "Migration frameworks"],
            "approach": "Scalable design with data consistency planning",
            "best_for": "Unified analytics and content management databases"
        },
        "debugger": {
            "role": "Root cause analysis and troubleshooting",
            "capabilities": [
                "Error message and stack trace analysis",
                "Reproduction step identification",
                "Failure location isolation",
                "Hypothesis formation and testing",
                "Strategic debug logging"
            ],
            "outputs": ["Debug reports", "Root cause analysis", "Fix recommendations"],
            "tools": ["Debuggers", "Logging analysis", "Hypothesis testing"],
            "approach": "Systematic troubleshooting with hypothesis testing",
            "best_for": "Troubleshooting agent coordination, API integration, and workflow issues"
        }
    }

    if agent_name in capabilities:
        result = {
            "agent": agent_name,
            "details": capabilities[agent_name]
        }
    else:
        result = {
            "agent": agent_name,
            "error": "Agent not found",
            "available_agents": list(capabilities.keys())
        }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "list_engineering_agents",
    "List all 12 engineering specialist agents and their purposes",
    {}
)
async def list_engineering_agents(args):
    """
    Return list of all 12 engineering agents
    """
    agents = [
        {
            "name": "devops-engineer",
            "category": "Infrastructure",
            "purpose": "Production DevOps automation (CI/CD, Docker, K8s, Terraform)",
            "use_for": "Complete deployment pipelines and infrastructure",
            "specialty": "Production-ready configurations (886 lines of code)"
        },
        {
            "name": "frontend-developer",
            "category": "Development",
            "purpose": "Modern React applications and UI components",
            "use_for": "Web applications and component libraries",
            "specialty": "React, Next.js, Tailwind, accessibility"
        },
        {
            "name": "backend-architect",
            "category": "Architecture",
            "purpose": "Scalable API design and microservices",
            "use_for": "Backend architecture and API specifications",
            "specialty": "RESTful APIs, microservices, scalability"
        },
        {
            "name": "security-auditor",
            "category": "Security",
            "purpose": "Application security and vulnerability scanning",
            "use_for": "Security audits and compliance checks",
            "specialty": "OWASP Top 10, secret scanning, compliance"
        },
        {
            "name": "technical-writer",
            "category": "Documentation",
            "purpose": "Technical documentation and specifications",
            "use_for": "PRDs, specs, API docs, user guides",
            "specialty": "Comprehensive docs with diagrams"
        },
        {
            "name": "ai-engineer",
            "category": "AI/ML",
            "purpose": "LLM applications, RAG systems, agent frameworks",
            "use_for": "AI optimization and RAG system development",
            "specialty": "Perfect for optimizing all 35 agents"
        },
        {
            "name": "ui-ux-designer",
            "category": "Design",
            "purpose": "User-centered design and interface systems",
            "use_for": "Wireframes, design systems, user flows",
            "specialty": "User research, accessibility, design systems"
        },
        {
            "name": "code-reviewer",
            "category": "Quality",
            "purpose": "Expert code review for quality and security",
            "use_for": "Code quality assurance and reviews",
            "specialty": "3.2K community downloads, proven in production"
        },
        {
            "name": "test-engineer",
            "category": "Quality",
            "purpose": "Comprehensive test automation and QA",
            "use_for": "Test strategies and automation suites",
            "specialty": "Test pyramid with CI/CD integration"
        },
        {
            "name": "prompt-engineer",
            "category": "AI/ML",
            "purpose": "Expert LLM prompt optimization",
            "use_for": "Optimizing agent prompts and AI systems",
            "specialty": "2.4K downloads, can optimize all 35 agents"
        },
        {
            "name": "database-architect",
            "category": "Data",
            "purpose": "Database architecture and data modeling",
            "use_for": "Database design and data layer planning",
            "specialty": "Scalable design with polyglot persistence"
        },
        {
            "name": "debugger",
            "category": "Support",
            "purpose": "Root cause analysis and troubleshooting",
            "use_for": "Debugging and issue resolution",
            "specialty": "Systematic troubleshooting with hypothesis testing"
        }
    ]

    result = {
        "total_agents": len(agents),
        "categories": {
            "Infrastructure": ["devops-engineer"],
            "Development": ["frontend-developer"],
            "Architecture": ["backend-architect"],
            "Security": ["security-auditor"],
            "Documentation": ["technical-writer"],
            "AI/ML": ["ai-engineer", "prompt-engineer"],
            "Design": ["ui-ux-designer"],
            "Quality": ["code-reviewer", "test-engineer"],
            "Data": ["database-architect"],
            "Support": ["debugger"]
        },
        "agents": agents
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "create_execution_plan",
    "Create multi-phase execution plan for complex engineering workflows",
    {
        "request_type": str,
        "agents_needed": list,
        "additional_requirements": dict  # Optional: constraints, timeline, etc.
    }
)
async def create_execution_plan(args):
    """
    Create phased execution plan with dependencies and sequencing
    """
    request_type = args["request_type"]
    agents_needed = args["agents_needed"]
    additional_requirements = args.get("additional_requirements", {})

    # Define common workflow patterns
    workflow_patterns = {
        "build_feature": {
            "phases": [
                {
                    "phase": 1,
                    "name": "Planning & Design",
                    "agents": ["technical-writer", "ui-ux-designer"],
                    "deliverables": ["PRD", "Wireframes", "User flows"],
                    "duration": "2-3 days"
                },
                {
                    "phase": 2,
                    "name": "Architecture",
                    "agents": ["database-architect", "backend-architect"],
                    "deliverables": ["Database schema", "API specification"],
                    "duration": "2-3 days",
                    "depends_on": [1]
                },
                {
                    "phase": 3,
                    "name": "Development",
                    "agents": ["frontend-developer", "backend-architect"],
                    "deliverables": ["UI components", "API implementation"],
                    "duration": "5-7 days",
                    "depends_on": [2]
                },
                {
                    "phase": 4,
                    "name": "Testing & Review",
                    "agents": ["test-engineer", "code-reviewer", "security-auditor"],
                    "deliverables": ["Test suite", "Code review", "Security audit"],
                    "duration": "2-3 days",
                    "depends_on": [3]
                },
                {
                    "phase": 5,
                    "name": "Deployment",
                    "agents": ["devops-engineer"],
                    "deliverables": ["CI/CD pipeline", "Production deployment"],
                    "duration": "1-2 days",
                    "depends_on": [4]
                },
                {
                    "phase": 6,
                    "name": "Documentation",
                    "agents": ["technical-writer"],
                    "deliverables": ["API docs", "User guide", "Deployment docs"],
                    "duration": "1-2 days",
                    "depends_on": [5]
                }
            ],
            "total_duration": "13-20 days",
            "critical_path": [1, 2, 3, 4, 5, 6]
        },
        "deploy_infrastructure": {
            "phases": [
                {
                    "phase": 1,
                    "name": "Infrastructure Design",
                    "agents": ["devops-engineer"],
                    "deliverables": ["Terraform configs", "Kubernetes manifests", "CI/CD pipeline"],
                    "duration": "3-5 days"
                },
                {
                    "phase": 2,
                    "name": "Security Review",
                    "agents": ["security-auditor"],
                    "deliverables": ["Security scan report", "Compliance check"],
                    "duration": "1-2 days",
                    "depends_on": [1]
                },
                {
                    "phase": 3,
                    "name": "Deployment Testing",
                    "agents": ["test-engineer"],
                    "deliverables": ["Deployment tests", "Smoke tests", "Load tests"],
                    "duration": "2-3 days",
                    "depends_on": [2]
                },
                {
                    "phase": 4,
                    "name": "Documentation",
                    "agents": ["technical-writer"],
                    "deliverables": ["Deployment guide", "Runbooks", "Architecture diagrams"],
                    "duration": "1-2 days",
                    "depends_on": [3]
                }
            ],
            "total_duration": "7-12 days",
            "critical_path": [1, 2, 3, 4]
        },
        "optimize_ai": {
            "phases": [
                {
                    "phase": 1,
                    "name": "Analysis",
                    "agents": ["ai-engineer", "prompt-engineer"],
                    "deliverables": ["Current prompt analysis", "Performance metrics"],
                    "duration": "2-3 days"
                },
                {
                    "phase": 2,
                    "name": "Optimization",
                    "agents": ["ai-engineer", "prompt-engineer"],
                    "deliverables": ["Optimized prompts", "Reduced token usage"],
                    "duration": "3-5 days",
                    "depends_on": [1]
                },
                {
                    "phase": 3,
                    "name": "Benchmarking",
                    "agents": ["ai-engineer", "prompt-engineer"],
                    "deliverables": ["Performance benchmarks", "A/B test results"],
                    "duration": "2-3 days",
                    "depends_on": [2]
                },
                {
                    "phase": 4,
                    "name": "Documentation",
                    "agents": ["technical-writer"],
                    "deliverables": ["Optimization report", "Prompt guidelines"],
                    "duration": "1-2 days",
                    "depends_on": [3]
                }
            ],
            "total_duration": "8-13 days",
            "critical_path": [1, 2, 3, 4]
        }
    }

    # Get workflow pattern or create custom
    if request_type in workflow_patterns:
        plan = workflow_patterns[request_type]
    else:
        # Create simple sequential plan for custom requests
        plan = {
            "phases": [
                {
                    "phase": i + 1,
                    "name": f"Phase {i + 1}",
                    "agents": [agent],
                    "deliverables": ["TBD"],
                    "duration": "TBD"
                }
                for i, agent in enumerate(agents_needed)
            ],
            "total_duration": "TBD",
            "critical_path": list(range(1, len(agents_needed) + 1))
        }

    result = {
        "request_type": request_type,
        "execution_plan": plan,
        "agents_involved": agents_needed,
        "additional_requirements": additional_requirements,
        "notes": [
            "Phases can run in parallel if no dependencies",
            "Critical path shows minimum time to completion",
            "Adjust durations based on team size and complexity"
        ]
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }
