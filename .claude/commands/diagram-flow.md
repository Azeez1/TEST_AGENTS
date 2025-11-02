# Create Flow Diagrams

Generate professional flow diagrams for processes, sequences, and data flows.

## What This Does

System-architect creates Mermaid.js flow diagrams with interactive visualizations.

## Usage

```
/diagram-flow [diagram type] [subject]
```

## Example

```
/diagram-flow sequence "User authentication flow"
/diagram-flow flowchart "Payment processing workflow"
/diagram-flow data-flow "Event data pipeline"
/diagram-flow state "Order lifecycle state machine"
```

## Diagram Types

### 1. Sequence Diagram
**Use for:** API calls, service interactions, user workflows

```
/diagram-flow sequence "OAuth authentication"
```

**Shows:**
- Actor interactions over time
- Request/response flows
- Synchronous and asynchronous calls
- Error handling paths

### 2. Flowchart
**Use for:** Business logic, decision trees, algorithms

```
/diagram-flow flowchart "Lead scoring algorithm"
```

**Shows:**
- Decision points
- Process steps
- Conditional branches
- Loop structures

### 3. Data Flow Diagram
**Use for:** Data pipelines, ETL processes, data transformations

```
/diagram-flow data-flow "Analytics data pipeline"
```

**Shows:**
- Data sources
- Transformation steps
- Data stores
- Data consumers

### 4. State Diagram
**Use for:** Object lifecycle, status workflows, finite state machines

```
/diagram-flow state "Pull request lifecycle"
```

**Shows:**
- States
- Transitions
- Triggers
- Terminal states

### 5. Class Diagram
**Use for:** Object-oriented design, data models, relationships

```
/diagram-flow class "E-commerce domain model"
```

**Shows:**
- Classes and attributes
- Methods
- Relationships (inheritance, composition, association)
- Cardinality

### 6. Entity Relationship Diagram
**Use for:** Database schema, data modeling

```
/diagram-flow erd "Multi-tenant SaaS database"
```

**Shows:**
- Tables/entities
- Columns/attributes
- Relationships
- Primary/foreign keys

### 7. Gantt Chart
**Use for:** Project timelines, roadmaps, sprints

```
/diagram-flow gantt "Q1 feature roadmap"
```

**Shows:**
- Tasks and milestones
- Dependencies
- Timeline
- Resource allocation

### 8. User Journey
**Use for:** User experience flows, customer journeys

```
/diagram-flow journey "New user onboarding"
```

**Shows:**
- User touchpoints
- Actions and decisions
- Emotional journey
- Pain points

## Process

1. **Requirement Gathering** (system-architect)
   - Understand the process/flow to diagram
   - Identify all actors/components
   - Clarify decision points
   - Define scope and level of detail

2. **Diagram Design** (system-architect)
   - Choose appropriate diagram type
   - Create logical flow
   - Apply best practices (top-to-bottom, left-to-right)
   - Use consistent notation
   - Add descriptive labels

3. **Mermaid.js Implementation**
   - Write clean Mermaid syntax
   - Apply styling for clarity
   - Use subgraphs for organization
   - Add notes and annotations
   - Optimize layout

4. **Visual Enhancement**
   - Color coding for clarity
   - Icons and symbols
   - Grouping related elements
   - Highlighting critical paths
   - Adding legends

5. **Documentation** (technical-writer)
   - Diagram description
   - Key takeaways
   - Assumptions and constraints
   - References to related diagrams

## Deliverables

- Mermaid.js source code
- Rendered diagram (PNG/SVG export)
- Interactive HTML visualization
- Diagram documentation
- Multiple detail levels (if needed):
  - High-level overview
  - Detailed technical view

## Diagram Best Practices

**Clarity:**
- Clear, descriptive labels
- Logical flow direction
- Appropriate level of detail
- Minimal crossing lines

**Consistency:**
- Consistent notation
- Uniform shape usage
- Standard color coding
- Aligned elements

**Completeness:**
- All paths shown
- Error handling included
- Edge cases considered
- Legend provided (if needed)

**Aesthetics:**
- Balanced layout
- Proper spacing
- Professional appearance
- Print-ready quality

## Mermaid.js Features

**Styling:**
```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ff6b6b'}}}%%
```

**Subgraphs:**
```mermaid
subgraph "Authentication Service"
  ...
end
```

**Links:**
```mermaid
A-->|"Success"|B
A-->|"Failure"|C
```

**Notes:**
```mermaid
Note right of User: User enters credentials
```

**Classes:**
```mermaid
class Success success
class Error error
```

## Time Estimate

- Simple diagram (5-10 elements): 15-30 minutes
- Medium diagram (10-20 elements): 30-60 minutes
- Complex diagram (20+ elements): 1-2 hours

## Output Format

- Markdown file with embedded Mermaid
- Standalone Mermaid `.mmd` file
- PNG export (high resolution, 300 DPI)
- SVG export (vector, scalable)
- Interactive HTML with live editor

## Use Cases

**Engineering:**
- System architecture
- API flows
- Database schemas
- Deployment pipelines

**Product:**
- User journeys
- Feature workflows
- Decision trees
- Roadmaps

**DevOps:**
- CI/CD pipelines
- Infrastructure topology
- Incident response flows
- Deployment strategies

**Marketing:**
- Customer journey maps
- Campaign workflows
- Lead lifecycle
- Content strategy

## Interactive Features

The system-architect uses the flow-diagram skill which includes:
- Live Mermaid editor
- Real-time preview
- Export to multiple formats
- Template library (13+ templates)
- Color theme options
