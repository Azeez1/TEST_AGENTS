# Gotchas — Flow Diagram

> Built from real failures. If you hit one of these, the fix is here.

## 1. display:none Breaks Mermaid Rendering
**Symptom:** Mermaid diagrams render as blank or zero-size in carousel/slideshow views.
**Root Cause:** Mermaid calculates SVG dimensions at render time. If the container has `display:none` (common in carousel slides that aren't active), Mermaid gets zero dimensions.
**Fix:** Use `visibility:hidden; position:absolute;` instead of `display:none` for inactive slides. Or re-render Mermaid when the slide becomes visible.
**Discovered:** Flow diagram skill development

---

## 2. Diagrams Don't Appear on Slide Switch
**Symptom:** In multi-slide carousels, switching to a slide with a diagram shows nothing until page refresh.
**Root Cause:** Same as above — Mermaid needs the container to be visible and have dimensions when `mermaid.init()` runs.
**Fix:** Call `mermaid.init(undefined, '.mermaid')` or `mermaid.run()` each time a new slide becomes active.
**Discovered:** Flow diagram skill development

---

## 3. Duplicate Element IDs Cause Silent Failures
**Symptom:** Only the first diagram renders correctly. Others are missing or show the first diagram's content.
**Root Cause:** Multiple Mermaid diagrams on the same page sharing the same container ID. Mermaid binds to the first match.
**Fix:** Give each diagram container a unique ID (e.g., `mermaid-1`, `mermaid-2`). Never reuse IDs.
**Discovered:** Flow diagram skill development

---

## 4. Diagrams Render Too Small
**Symptom:** Complex diagrams (many nodes, long labels) appear tiny or truncated.
**Root Cause:** Mermaid auto-fits to container width. If the container is narrow or the diagram is very complex, it compresses everything.
**Fix:** Set explicit `maxWidth` in Mermaid config, use `%%{init: {'theme':'base', 'themeVariables': {'fontSize':'16px'}}}%%` directives, or wrap in a wider container with horizontal scroll.
**Discovered:** Flow diagram skill development

---

## 5. Interactive HTML Needs Local Server
**Symptom:** Opening an interactive HTML diagram by double-clicking the file shows a blank page or broken functionality.
**Root Cause:** Interactive diagrams using fetch() or ES modules require HTTP protocol. The `file://` protocol blocks these requests due to CORS.
**Fix:** Serve locally: `python -m http.server 8080` then open `http://localhost:8080/diagram.html`. Or use VS Code Live Server extension.
**Discovered:** Flow diagram skill development
