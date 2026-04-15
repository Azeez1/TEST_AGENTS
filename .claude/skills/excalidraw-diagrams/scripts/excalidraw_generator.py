#!/usr/bin/env python3
"""
Excalidraw Diagram Generator
============================
Programmatically create .excalidraw files — fully editable, hand-drawn style
diagrams that open at excalidraw.com or in VS Code (free Excalidraw extension).

No API key. No paid plan. No network calls.

Usage:
    from excalidraw_generator import Diagram, Flowchart, ArchitectureDiagram

Classes:
    Diagram             — General purpose: boxes, arrows, text, lines
    Flowchart           — Auto-positioned sequential flows with start/end/process/decision
    ArchitectureDiagram — System design with users, services, databases, queues
"""

import json
import random
import time
import os
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any

# ---------------------------------------------------------------------------
# Color palette
# Each color has a stroke (border) and fill (background) value.
# ---------------------------------------------------------------------------
COLORS: Dict[str, Dict[str, str]] = {
    "blue":    {"stroke": "#1971c2", "fill": "#d0ebff"},
    "green":   {"stroke": "#2f9e44", "fill": "#d3f9d8"},
    "red":     {"stroke": "#c92a2a", "fill": "#ffe3e3"},
    "orange":  {"stroke": "#e8590c", "fill": "#ffe8cc"},
    "violet":  {"stroke": "#6741d9", "fill": "#ede9fe"},
    "yellow":  {"stroke": "#e67700", "fill": "#fff9db"},
    "cyan":    {"stroke": "#0c8599", "fill": "#c5f6fa"},
    "pink":    {"stroke": "#a61e4d", "fill": "#ffdeeb"},
    "gray":    {"stroke": "#495057", "fill": "#f1f3f5"},
    "default": {"stroke": "#1e1e1e", "fill": "transparent"},
}

# Font family IDs used by Excalidraw:
#   1 = Virgil (hand-drawn)
#   2 = Helvetica (normal/clean)
#   3 = Cascadia Code (monospace)
FONT_FAMILIES: Dict[str, int] = {
    "hand-drawn": 1,
    "normal": 2,
    "monospace": 3,
}


def _uid() -> str:
    """Generate a random 20-char alphanumeric element ID."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choices(chars, k=20))


def _seed() -> int:
    """Generate a random seed integer for Excalidraw's rough rendering."""
    return random.randint(100_000, 999_999_999)


def _now() -> int:
    """Current timestamp in milliseconds."""
    return int(time.time() * 1000)


# ---------------------------------------------------------------------------
# Style configuration dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DiagramStyle:
    """
    Global visual style for all elements in a diagram.

    Attributes:
        roughness:    0 = clean/precise, 1 = hand-drawn (default), 2 = rough sketch
        stroke_style: "solid" | "dashed" | "dotted"
        stroke_width: Line thickness 1-4
        font_family:  "hand-drawn" | "normal" | "monospace"
        font_size:    Base font size in pixels
    """
    roughness: int = 1
    stroke_style: str = "solid"
    stroke_width: int = 2
    font_family: str = "hand-drawn"
    font_size: int = 16


@dataclass
class FlowchartStyle:
    """Colors for each flowchart node type."""
    start_color: str = "green"
    end_color: str = "red"
    process_color: str = "blue"
    decision_color: str = "yellow"


@dataclass
class ArchitectureStyle:
    """Colors for each architecture component type."""
    user_color: str = "cyan"
    component_color: str = "blue"
    service_color: str = "violet"
    database_color: str = "green"
    external_color: str = "orange"
    queue_color: str = "yellow"


@dataclass
class LayoutConfig:
    """Auto-layout spacing for Flowchart diagrams."""
    horizontal_spacing: int = 150
    vertical_spacing: int = 100
    start_x: float = 120
    start_y: float = 100


# ---------------------------------------------------------------------------
# Element reference (returned by box/node methods)
# ---------------------------------------------------------------------------

class Element:
    """
    Reference to a placed diagram element.
    Used as argument to arrow_between() and connect().
    """
    def __init__(self, id: str, x: float, y: float, width: float, height: float):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Center point — used for arrow attachment calculations
        self.cx = x + width / 2
        self.cy = y + height / 2

    def __repr__(self):
        return f"Element(id={self.id!r}, x={self.x}, y={self.y})"


# ---------------------------------------------------------------------------
# Base Diagram class
# ---------------------------------------------------------------------------

class Diagram:
    """
    General-purpose diagram builder.

    Example:
        d = Diagram()
        a = d.box(100, 100, "Start", color="green")
        b = d.box(350, 100, "Process", color="blue")
        c = d.box(600, 100, "End",   color="red")
        d.arrow_between(a, b)
        d.arrow_between(b, c)
        d.save("my_diagram.excalidraw")
    """

    def __init__(self, diagram_style: Optional[DiagramStyle] = None):
        self.style = diagram_style or DiagramStyle()
        self._elements: List[Dict] = []
        # Map shape_id → Element for boundElement updates
        self._shape_map: Dict[str, Dict] = {}

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _base(self, type: str, x: float, y: float, w: float, h: float) -> Dict:
        """Build a base element dict with all required Excalidraw fields."""
        return {
            "id": _uid(),
            "type": type,
            "x": round(x, 2),
            "y": round(y, 2),
            "width": round(w, 2),
            "height": round(h, 2),
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": self.style.stroke_width,
            "strokeStyle": self.style.stroke_style,
            "roughness": self.style.roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 3},
            "seed": _seed(),
            "version": 1,
            "versionNonce": _seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": _now(),
            "link": None,
            "locked": False,
        }

    def _text_element(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        color: str = "#1e1e1e",
        container_id: Optional[str] = None,
        font_size: Optional[int] = None,
        text_align: str = "center",
        vertical_align: str = "middle",
    ) -> Dict:
        """Create a text element, optionally bound to a container shape."""
        fs = font_size or self.style.font_size
        ff = FONT_FAMILIES.get(self.style.font_family, 1)
        line_height = 1.25
        text_height = fs * line_height

        # When inside a container, y/x are relative; Excalidraw centers it.
        # When standalone, position it at the given coordinates.
        if container_id:
            text_x = x
            text_y = y + (height - text_height) / 2
        else:
            text_x = x
            text_y = y

        return {
            "id": _uid(),
            "type": "text",
            "x": round(text_x, 2),
            "y": round(text_y, 2),
            "width": round(width, 2),
            "height": round(text_height, 2),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": _seed(),
            "version": 1,
            "versionNonce": _seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": _now(),
            "link": None,
            "locked": False,
            # Text-specific fields
            "text": text,
            "fontSize": fs,
            "fontFamily": ff,
            "textAlign": text_align,
            "verticalAlign": vertical_align,
            "baseline": round(fs * 0.9),
            "containerId": container_id,
            "originalText": text,
            "lineHeight": line_height,
            "autoResize": True,
        }

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def box(
        self,
        x: float,
        y: float,
        label: str,
        color: str = "default",
        width: float = 150,
        height: float = 60,
        shape: str = "rectangle",
    ) -> Element:
        """
        Add a labeled box to the diagram.

        Args:
            x, y:   Top-left position in pixels
            label:  Text inside the box
            color:  One of: blue, green, red, orange, violet, yellow, cyan, pink, gray, default
            width:  Box width (auto-sized if not set)
            height: Box height
            shape:  "rectangle" | "ellipse" | "diamond"

        Returns:
            Element — pass to arrow_between() to connect
        """
        colors = COLORS.get(color, COLORS["default"])
        el = self._base(shape, x, y, width, height)
        el["strokeColor"] = colors["stroke"]
        el["backgroundColor"] = colors["fill"]

        # Shape-specific roundness
        if shape == "diamond":
            el["roundness"] = None
        elif shape == "ellipse":
            el["roundness"] = {"type": 2}
        else:
            el["roundness"] = {"type": 3}

        shape_id = el["id"]

        # Create bound text label
        text_el = self._text_element(
            label, x, y, width, height,
            color=colors["stroke"],
            container_id=shape_id,
        )
        text_id = text_el["id"]
        el["boundElements"] = [{"id": text_id, "type": "text"}]

        self._elements.append(el)
        self._elements.append(text_el)
        self._shape_map[shape_id] = el

        return Element(shape_id, x, y, width, height)

    def text_box(
        self,
        x: float,
        y: float,
        text: str,
        font_size: int = 20,
        color: str = "#1e1e1e",
    ) -> Element:
        """
        Add standalone text (no background shape).

        Useful for section headers, annotations, and titles.
        """
        ff = FONT_FAMILIES.get(self.style.font_family, 1)
        # Estimate width based on character count
        estimated_width = len(text) * font_size * 0.55
        line_height = 1.25

        el = {
            "id": _uid(),
            "type": "text",
            "x": round(x, 2),
            "y": round(y, 2),
            "width": round(estimated_width, 2),
            "height": round(font_size * line_height, 2),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": _seed(),
            "version": 1,
            "versionNonce": _seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": _now(),
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": ff,
            "textAlign": "left",
            "verticalAlign": "top",
            "baseline": round(font_size * 0.9),
            "containerId": None,
            "originalText": text,
            "lineHeight": line_height,
            "autoResize": True,
        }
        self._elements.append(el)
        return Element(el["id"], x, y, estimated_width, font_size * line_height)

    def arrow_between(
        self,
        start: Element,
        end: Element,
        label: str = "",
        color: str = "default",
        style: str = "solid",
        bidirectional: bool = False,
    ) -> str:
        """
        Draw an arrow from start to end element.

        Args:
            start:         Source element (returned by box())
            end:           Target element (returned by box())
            label:         Optional label on the arrow
            color:         Arrow color (see COLORS)
            style:         "solid" | "dashed" | "dotted"
            bidirectional: If True, adds arrowhead on both ends

        Returns:
            Arrow element ID string
        """
        colors = COLORS.get(color, COLORS["default"])
        stroke = colors["stroke"] if color != "default" else "#1e1e1e"

        sx, sy = start.cx, start.cy
        ex, ey = end.cx, end.cy
        dx, dy = ex - sx, ey - sy

        arrow_id = _uid()
        arrow = {
            "id": arrow_id,
            "type": "arrow",
            "x": round(sx, 2),
            "y": round(sy, 2),
            "width": round(abs(dx), 2),
            "height": round(abs(dy), 2),
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": self.style.stroke_width,
            "strokeStyle": style,
            "roughness": self.style.roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": _seed(),
            "version": 1,
            "versionNonce": _seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": _now(),
            "link": None,
            "locked": False,
            "points": [[0, 0], [round(dx, 2), round(dy, 2)]],
            "startBinding": {
                "elementId": start.id,
                "focus": 0.0,
                "gap": 8,
            },
            "endBinding": {
                "elementId": end.id,
                "focus": 0.0,
                "gap": 8,
            },
            "startArrowhead": "arrow" if bidirectional else None,
            "endArrowhead": "arrow",
            "elbowed": False,
        }
        self._elements.append(arrow)

        # Register the arrow as a bound element on start and end shapes
        for sid in (start.id, end.id):
            if sid in self._shape_map:
                self._shape_map[sid]["boundElements"].append(
                    {"id": arrow_id, "type": "arrow"}
                )

        # Optional midpoint label
        if label:
            mid_x = (sx + ex) / 2
            mid_y = (sy + ey) / 2 - 18
            lw = max(len(label) * 9, 60)
            label_el = self._text_element(
                label, mid_x - lw / 2, mid_y, lw, 20,
                color=stroke, font_size=13, text_align="center",
                vertical_align="top",
            )
            label_el["containerId"] = None
            self._elements.append(label_el)

        return arrow_id

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str = "default",
        style: str = "solid",
    ) -> str:
        """Draw a simple line with no arrowhead."""
        colors = COLORS.get(color, COLORS["default"])
        stroke = colors["stroke"] if color != "default" else "#1e1e1e"
        dx, dy = x2 - x1, y2 - y1

        el = {
            "id": _uid(),
            "type": "line",
            "x": round(x1, 2),
            "y": round(y1, 2),
            "width": round(abs(dx), 2),
            "height": round(abs(dy), 2),
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": self.style.stroke_width,
            "strokeStyle": style,
            "roughness": self.style.roughness,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": _seed(),
            "version": 1,
            "versionNonce": _seed(),
            "isDeleted": False,
            "boundElements": [],
            "updated": _now(),
            "link": None,
            "locked": False,
            "points": [[0, 0], [round(dx, 2), round(dy, 2)]],
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": None,
        }
        self._elements.append(el)
        return el["id"]

    def group_box(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str = "",
        color: str = "gray",
    ) -> str:
        """
        Add a background grouping zone (cluster / swim lane).

        Should be called BEFORE adding elements inside it so it renders behind them.
        """
        colors = COLORS.get(color, COLORS["gray"])
        el = self._base("rectangle", x, y, width, height)
        el["strokeColor"] = colors["stroke"]
        el["backgroundColor"] = colors["fill"]
        el["fillStyle"] = "hachure"
        el["roughness"] = 0
        el["opacity"] = 25
        el["roundness"] = {"type": 3}

        # Insert at the beginning so it renders behind other elements
        self._elements.insert(0, el)

        if label:
            text_el = self._text_element(
                label, x + 12, y + 8, width - 24, 22,
                color=colors["stroke"], font_size=13,
                text_align="left", vertical_align="top",
            )
            text_el["containerId"] = None
            self._elements.insert(1, text_el)

        return el["id"]

    def save(self, path: str) -> str:
        """
        Write the diagram to a .excalidraw file.

        Args:
            path: File path (e.g., "outputs/diagrams/architecture.excalidraw")

        Returns:
            Absolute path of the saved file
        """
        data = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self._elements,
            "appState": {
                "gridSize": 20,
                "viewBackgroundColor": "#ffffff",
            },
            "files": {},
        }

        # Create output directory if needed
        dir_path = os.path.dirname(os.path.abspath(path))
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        abs_path = os.path.abspath(path)
        print(f"✅ Saved: {abs_path}")
        print(f"   → Open at https://excalidraw.com (drag & drop the file)")
        print(f"   → Or open in VS Code with the free 'Excalidraw' extension")
        return abs_path


# ---------------------------------------------------------------------------
# Flowchart — auto-positioned sequential flow
# ---------------------------------------------------------------------------

class Flowchart(Diagram):
    """
    Auto-positioned sequential flowchart.

    Nodes are placed top-to-bottom automatically. Use connect() to draw arrows.

    Example:
        fc = Flowchart()
        s  = fc.start("Begin")
        p1 = fc.process("Fetch data")
        d  = fc.decision("Valid?")
        p2 = fc.process("Log error")
        e  = fc.end("Done")

        fc.connect(s,  p1)
        fc.connect(p1, d)
        fc.connect(d,  e,  "yes")
        fc.connect(d,  p2, "no")
        fc.connect(p2, p1, "retry")

        fc.save("flow.excalidraw")
    """

    def __init__(
        self,
        diagram_style: Optional[DiagramStyle] = None,
        flowchart_style: Optional[FlowchartStyle] = None,
        layout_config: Optional[LayoutConfig] = None,
    ):
        super().__init__(diagram_style)
        self.fc_style = flowchart_style or FlowchartStyle()
        self.layout = layout_config or LayoutConfig()
        self._cursor_y = self.layout.start_y

    def _next_y(self, height: float) -> float:
        """Advance the vertical cursor and return the current position."""
        y = self._cursor_y
        self._cursor_y += height + self.layout.vertical_spacing
        return y

    def start(self, label: str = "Start") -> Element:
        """Oval start node (green by default)."""
        y = self._next_y(50)
        return self.box(
            self.layout.start_x, y, label,
            color=self.fc_style.start_color,
            shape="ellipse", width=130, height=50,
        )

    def end(self, label: str = "End") -> Element:
        """Oval end node (red by default)."""
        y = self._next_y(50)
        return self.box(
            self.layout.start_x, y, label,
            color=self.fc_style.end_color,
            shape="ellipse", width=130, height=50,
        )

    def process(self, label: str, color: Optional[str] = None) -> Element:
        """Rectangle process node (blue by default)."""
        y = self._next_y(60)
        c = color or self.fc_style.process_color
        return self.box(self.layout.start_x, y, label, color=c, width=160, height=60)

    def decision(self, label: str) -> Element:
        """Diamond decision node (yellow by default)."""
        y = self._next_y(80)
        return self.box(
            self.layout.start_x, y, label,
            color=self.fc_style.decision_color,
            shape="diamond", width=180, height=80,
        )

    def connect(self, a: Element, b: Element, label: str = "", style: str = "solid") -> str:
        """Draw an arrow between two flowchart nodes."""
        return self.arrow_between(a, b, label=label, style=style)


# ---------------------------------------------------------------------------
# ArchitectureDiagram — semantic system design components
# ---------------------------------------------------------------------------

class ArchitectureDiagram(Diagram):
    """
    System architecture diagram with semantic component types.

    Components:
        user()       — Person/actor (cyan ellipse with 👤)
        component()  — Generic component (blue rectangle)
        service()    — Microservice (violet rectangle with ⚙️)
        database()   — Data store (green ellipse with 🗄️)
        external()   — External system (orange rectangle with 🌐)
        queue()      — Message queue / cache (yellow rectangle with 📨)
        zone()       — Background grouping zone

    Example:
        arch = ArchitectureDiagram()

        # Background zones (call before adding components)
        arch.zone(40, 140, 720, 200, "Core Services", color="gray")

        u   = arch.user("User",         x=100, y=200, id="user")
        api = arch.service("API",       x=350, y=200, id="api")
        db  = arch.database("Postgres", x=600, y=200, id="db")
        q   = arch.queue("Redis",       x=350, y=360, id="cache")

        arch.connect(u,   api, "HTTPS")
        arch.connect(api, db,  "SQL")
        arch.connect(api, q,   "cache", style="dashed")

        arch.save("outputs/diagrams/architecture.excalidraw")
    """

    def __init__(
        self,
        diagram_style: Optional[DiagramStyle] = None,
        arch_style: Optional[ArchitectureStyle] = None,
    ):
        super().__init__(diagram_style)
        self.arch_style = arch_style or ArchitectureStyle()
        self._nodes: Dict[str, Element] = {}

    def _register(self, id: Optional[str], el: Element) -> Element:
        if id:
            self._nodes[id] = el
        return el

    def user(
        self, label: str, x: float = 100, y: float = 200, id: Optional[str] = None
    ) -> Element:
        """Person / actor node."""
        el = self.box(x, y, f"👤 {label}", color=self.arch_style.user_color,
                      shape="ellipse", width=130, height=60)
        return self._register(id, el)

    def component(
        self, label: str, x: float = 100, y: float = 200,
        color: Optional[str] = None, id: Optional[str] = None,
    ) -> Element:
        """Generic component rectangle."""
        c = color or self.arch_style.component_color
        el = self.box(x, y, label, color=c, width=160, height=60)
        return self._register(id, el)

    def service(
        self, label: str, x: float = 100, y: float = 200,
        color: Optional[str] = None, id: Optional[str] = None,
    ) -> Element:
        """Microservice or API node."""
        c = color or self.arch_style.service_color
        el = self.box(x, y, f"⚙️ {label}", color=c, width=160, height=60)
        return self._register(id, el)

    def database(
        self, label: str, x: float = 100, y: float = 200,
        color: Optional[str] = None, id: Optional[str] = None,
    ) -> Element:
        """Database / data store node."""
        c = color or self.arch_style.database_color
        el = self.box(x, y, f"🗄️ {label}", color=c,
                      shape="ellipse", width=160, height=60)
        return self._register(id, el)

    def external(
        self, label: str, x: float = 100, y: float = 200, id: Optional[str] = None
    ) -> Element:
        """External system / third-party API."""
        el = self.box(x, y, f"🌐 {label}", color=self.arch_style.external_color,
                      width=160, height=60)
        return self._register(id, el)

    def queue(
        self, label: str, x: float = 100, y: float = 200, id: Optional[str] = None
    ) -> Element:
        """Message queue, cache, or event bus."""
        el = self.box(x, y, f"📨 {label}", color=self.arch_style.queue_color,
                      width=160, height=60)
        return self._register(id, el)

    def connect(
        self,
        a: Element,
        b: Element,
        label: str = "",
        style: str = "solid",
        bidirectional: bool = False,
    ) -> str:
        """Draw a labeled arrow between two architecture nodes."""
        return self.arrow_between(a, b, label=label, style=style,
                                  bidirectional=bidirectional)

    def connect_by_id(self, a_id: str, b_id: str, label: str = "") -> str:
        """
        Connect two nodes registered with string IDs.

        Requires that both nodes were created with the `id=` parameter.
        """
        if a_id not in self._nodes:
            raise KeyError(f"Node '{a_id}' not found. Register nodes with id= parameter.")
        if b_id not in self._nodes:
            raise KeyError(f"Node '{b_id}' not found. Register nodes with id= parameter.")
        return self.connect(self._nodes[a_id], self._nodes[b_id])

    def zone(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str,
        color: str = "gray",
    ) -> str:
        """
        Add a background grouping zone (cluster / swim lane).

        ALWAYS call zone() BEFORE adding the elements that should appear inside it,
        so the zone renders behind them.
        """
        return self.group_box(x, y, width, height, label, color)


# ---------------------------------------------------------------------------
# AutoLayoutFlowchart — simple column-based auto-layout (no external deps)
# ---------------------------------------------------------------------------

class AutoLayoutFlowchart(Diagram):
    """
    Multi-column auto-layout flowchart.

    Automatically arranges nodes in multiple columns to avoid overlapping,
    useful for complex flowcharts with many branches.

    Example:
        fc = AutoLayoutFlowchart(columns=3)
        nodes = {}
        for name in ["Ingest", "Validate", "Transform", "Load", "Report", "Archive"]:
            nodes[name] = fc.add_node(name, color="blue")
        fc.connect_nodes(nodes["Ingest"], nodes["Validate"])
        fc.connect_nodes(nodes["Validate"], nodes["Transform"])
        fc.connect_nodes(nodes["Transform"], nodes["Load"])
        fc.connect_nodes(nodes["Load"], nodes["Report"])
        fc.connect_nodes(nodes["Report"], nodes["Archive"])
        fc.save("multi_flow.excalidraw")
    """

    def __init__(
        self,
        columns: int = 2,
        col_width: float = 200,
        row_height: float = 80,
        padding: float = 80,
        diagram_style: Optional[DiagramStyle] = None,
    ):
        super().__init__(diagram_style)
        self.columns = columns
        self.col_width = col_width
        self.row_height = row_height
        self.padding = padding
        self._counter = 0

    def add_node(
        self, label: str, color: str = "blue",
        shape: str = "rectangle", width: float = 150, height: float = 60,
    ) -> Element:
        """Add a node — position is auto-calculated based on insertion order."""
        col = self._counter % self.columns
        row = self._counter // self.columns
        x = self.padding + col * (self.col_width + self.padding)
        y = self.padding + row * (self.row_height + self.padding)
        self._counter += 1
        return self.box(x, y, label, color=color, width=width, height=height, shape=shape)

    def connect_nodes(self, a: Element, b: Element, label: str = "") -> str:
        """Connect two nodes."""
        return self.arrow_between(a, b, label=label)
