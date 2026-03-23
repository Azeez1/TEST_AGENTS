---
name: excalidraw-diagrams
description: Create editable diagrams as .excalidraw JSON files that the user can modify after creation. Outputs flowcharts, architecture diagrams, system designs, and wireframes openable in excalidraw.com or VS Code. Use when the user needs a diagram they can EDIT and rearrange later — for polished read-only diagrams optimized for sharing/social media, use flow-diagram instead.
allowed-tools: Read, Write, Bash, Glob
license: MIT
---

# Excalidraw Diagram Generator

Generate professional `.excalidraw` diagrams programmatically using Python. Unlike Mermaid (which renders static images), Excalidraw produces **fully editable, hand-drawn style diagrams** users can open and modify interactively.

## When to Use This Skill

Use instead of (or alongside) `flow-diagram` when:
- The user wants to **edit the diagram** after generation (drag nodes, add labels, etc.)
- Creating **architecture diagrams** for client deliverables or team whiteboards
- Building **system design** visuals with semantic components (users, services, databases)
- The output needs the **hand-drawn Excalidraw aesthetic**
- The diagram will live in **Obsidian, VS Code, or Notion** (all support `.excalidraw`)
- Creating **flowcharts** for processes, decision trees, CI/CD pipelines

**Use `flow-diagram` (Mermaid) instead when:**
- Output is embedded directly in Markdown/README files
- You need specific Mermaid diagram types (ER, Gantt, sequence, git graph)
- The diagram will be rendered as a static PNG/SVG only

## Output Format

`.excalidraw` files (JSON) that can be:
- **Opened at excalidraw.com** — drag & drop the file
- **Edited in VS Code** — install "Excalidraw" extension (free)
- **Used in Obsidian** — install "Excalidraw" plugin (free)
- **Embedded in Notion** — upload as file attachment

**No API key. No paid plan. No network calls required.**

---

## Quick Start

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/excalidraw-diagrams/scripts"))
# OR for project-level install:
sys.path.insert(0, ".claude/skills/excalidraw-diagrams/scripts")

from excalidraw_generator import Diagram, Flowchart, ArchitectureDiagram
```

### Example 1: Simple Flowchart

```python
from excalidraw_generator import Flowchart

fc = Flowchart()
s   = fc.start("Begin")
p1  = fc.process("Load data")
d   = fc.decision("Valid?")
p2  = fc.process("Handle error")
e   = fc.end("Done")

fc.connect(s, p1)
fc.connect(p1, d)
fc.connect(d, e, "yes")
fc.connect(d, p2, "no")
fc.connect(p2, p1, "retry")

fc.save("outputs/diagrams/user_flow.excalidraw")
```

### Example 2: Architecture Diagram

```python
from excalidraw_generator import ArchitectureDiagram

arch = ArchitectureDiagram()

# Add a grouping zone first (appears behind elements)
arch.zone(50, 150, 700, 200, "Backend Services", color="gray")

# Add components
u   = arch.user("User", x=100, y=200)
api = arch.service("API Gateway", x=350, y=200, color="violet")
db  = arch.database("PostgreSQL", x=600, y=200)
q   = arch.queue("Redis Queue", x=350, y=350)

# Connect them
arch.connect(u,   api, "HTTPS")
arch.connect(api, db,  "SQL")
arch.connect(api, q,   "async")

arch.save("outputs/diagrams/system_architecture.excalidraw")
```

### Example 3: Custom Diagram

```python
from excalidraw_generator import Diagram, DiagramStyle

d = Diagram(diagram_style=DiagramStyle(roughness=0, stroke_width=1))  # Clean style

d.text_box(100, 30, "Data Processing Pipeline", font_size=24)

ingestion  = d.box(100, 100, "Data Ingestion",   color="blue",   width=160, height=60)
validation = d.box(320, 100, "Validation",        color="yellow", width=140, height=60)
transform  = d.box(520, 100, "Transform",         color="violet", width=140, height=60)
storage    = d.box(320, 250, "Storage",           color="green",  width=140, height=60)
error      = d.box(520, 250, "Error Handler",     color="red",    width=140, height=60)

d.arrow_between(ingestion,  validation, "raw data")
d.arrow_between(validation, transform,  "valid")
d.arrow_between(validation, error,      "invalid")
d.arrow_between(transform,  storage,    "processed")

d.save("outputs/diagrams/pipeline.excalidraw")
```

---

## API Reference

### `Diagram` — General Purpose

| Method | Description |
|--------|-------------|
| `box(x, y, label, color, width, height, shape)` | Add a box. `shape`: "rectangle", "ellipse", "diamond" |
| `arrow_between(start, end, label, color, style)` | Connect two elements. `style`: "solid", "dashed", "dotted" |
| `text_box(x, y, text, font_size, color)` | Standalone text (no background) |
| `group_box(x, y, width, height, label, color)` | Background grouping zone |
| `line(x1, y1, x2, y2, color, style)` | Simple line (no arrowhead) |
| `save(path)` | Write `.excalidraw` file |

### `Flowchart` — Sequential Flows

| Method | Description |
|--------|-------------|
| `start(label)` | Green rounded start node |
| `end(label)` | Red rounded end node |
| `process(label, color)` | Blue rectangle node |
| `decision(label)` | Yellow diamond node |
| `connect(a, b, label)` | Arrow between nodes |

### `ArchitectureDiagram` — System Design

| Method | Description |
|--------|-------------|
| `user(label, x, y, id)` | Cyan ellipse with 👤 |
| `component(label, x, y, color, id)` | Blue rectangle |
| `service(label, x, y, color, id)` | Violet rectangle with ⚙️ |
| `database(label, x, y, color, id)` | Green ellipse with 🗄️ |
| `external(label, x, y, id)` | Orange rectangle with 🌐 |
| `queue(label, x, y, id)` | Yellow rectangle with 📨 |
| `connect(a, b, label, style)` | Arrow between elements |
| `zone(x, y, w, h, label, color)` | Background grouping zone |

### Colors Available

`blue`, `green`, `red`, `orange`, `violet`, `yellow`, `cyan`, `pink`, `gray`, `default`

### `DiagramStyle` Options

```python
DiagramStyle(
    roughness=1,          # 0=clean/sharp, 1=hand-drawn, 2=rough sketch
    stroke_style="solid", # "solid", "dashed", "dotted"
    stroke_width=2,        # 1–4
    font_family="hand-drawn",  # "hand-drawn", "normal", "monospace"
    font_size=16,
)
```

---

## Workflow

1. **Identify diagram type** — flowchart, architecture, or custom
2. **Plan layout** — sketch positions (x,y) for elements
3. **Write Python script** using the generator classes
4. **Save to `outputs/diagrams/`** as `.excalidraw`
5. **Share the file** — user opens it at excalidraw.com or VS Code
6. **Optionally export PNG** — user can export from Excalidraw UI (free)

## Output Path Convention

Always save to the team's outputs directory:
```python
# MARKETING_TEAM agents:
d.save("MARKETING_TEAM/outputs/diagrams/my_diagram.excalidraw")

# ENGINEERING_TEAM agents:
d.save("ENGINEERING_TEAM/outputs/diagrams/my_diagram.excalidraw")
```

## Viewing the Output

Tell the user:
> "I've saved the diagram to `outputs/diagrams/my_diagram.excalidraw`.
> To view it: go to [excalidraw.com](https://excalidraw.com) and drag-drop the file.
> To edit: open in VS Code with the free **Excalidraw** extension."
