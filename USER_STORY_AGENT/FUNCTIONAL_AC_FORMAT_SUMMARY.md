# Functional AC Format Implementation Summary

**Date:** 2025-01-15
**System:** USER_STORY_AGENT
**Feature:** Added "Functional (Behavior-Focused)" AC format option

---

## What Was Added

A third Acceptance Criteria format option called **"Functional (Behavior-Focused)"** that produces ACs with:
- Hierarchical numbering (1, a, i, 1) - same structure as Explicit/Detailed
- **Pure functional language** - NO design adjectives
- Focus on WHAT the system DOES, not HOW it looks

---

## The 3 AC Format Options

### 1. Gherkin (Given/When/Then)
- **Structure:** Scenario-based testing format
- **Style:** `Given [context], when [action], then [outcome]`
- **Use case:** BDD testing, QA test cases

### 2. Explicit/Detailed
- **Structure:** Hierarchical (1, a, i, 1), 30-50 lines
- **Style:** Detailed requirements with design language ALLOWED
- **Language:** Can use "modern", "prominent", "streamlined", "clean"
- **Use case:** Comprehensive requirements with UX considerations

### 3. Functional (Behavior-Focused) ← **NEW**
- **Structure:** Hierarchical (1, a, i, 1), 30-50 lines
- **Style:** Pure functional requirements
- **PRIMARY Language:** **"The user will be able to [action]"** (emphasizes user capabilities)
- **SECONDARY Language:** "will display", "will show", "when user selects"
- **AVOID:** ALL design adjectives - NO "modern", "prominent", "streamlined", "clean", "intuitive", "visual hierarchy"
- **Use case:** Technical specifications focused on user capabilities and system behavior

---

## Functional Format Specification

### Language Rules (CRITICAL)

**✅ PRIMARY PATTERN (Use This Most):**
- **"The user will be able to [action]"** ← MAIN PATTERN!
- Example: "The user will be able to navigate through product images"
- Example: "The user will be able to expand to full screen gallery mode"
- Example: "The user will be able to view photos in Full-size resolution"
- Focus on USER CAPABILITIES and what user can DO

**✅ SECONDARY PATTERNS (Supporting):**
- "The [element] will [verb]" - for automatic system behavior
  - Example: "The product image will dynamically change once user selects different images"
- "When user selects [X], [result]" - for user interactions
- "The [page/section] will display [content]" - for what shows on screen
- "will be displayed", "will show", "displays"
- Describe WHAT the system DOES

**❌ AVOID ALL DESIGN LANGUAGE:**
- NO "modern", "modernized", "streamlined", "clean"
- NO "prominent", "prominently", "elevated", "intuitive"
- NO "visual hierarchy", "aesthetics", "seamless"
- NO subjective visual descriptions

**❌ AVOID UI IMPLEMENTATION TERMS:**
- NO "button" → USE "call-to-action" or "selectable option"
- NO "dropdown" → USE "selection menu" or "options list"
- NO "modal", "popup" → USE "overlay message" or "notification"
- NO "accordion", "collapsible" → USE "expandable section"
- NO "carousel", "slider" → USE "navigable images"
- NO "toggle", "switch" → USE "option to enable/disable"
- NO "checkbox" → USE "selectable option" or "multiple-selection option"
- NO "radio button" → USE "single-selection option"
- NO "tab" → USE "section" or "area"
- NO "icon" → USE "indicator" or "symbol"
- NO "sidebar", "navbar" → USE "navigation area"

**Focus on FUNCTIONALITY, not implementation!**

### UI Terms Reference (Quick Lookup)

| ❌ DON'T Use | ✅ DO Use |
|--------------|-----------|
| button | call-to-action, selectable option |
| click button | select, choose |
| dropdown | selection menu, options list |
| modal, popup | overlay message, notification |
| accordion, collapsible | expandable section |
| carousel, slider | navigable images, image sequence |
| toggle, switch | option to enable/disable |
| checkbox | selectable option, multiple-selection option |
| radio button | single-selection option |
| tab | section, area |
| icon | indicator, symbol |
| sidebar, navbar | navigation area |
| hover | focus on, move to |
| tooltip | information overlay |

### Content Coverage

**✅ INCLUDE:**
- What displays/shows on screen (specific elements)
- User interactions and system responses
- Conditional logic (If/then statements)
- Data availability states (pending, unavailable, error)
- User state differences (guest/logged-in)
- Navigation flows (redirects to specific pages)
- Field behaviors (required, optional, auto-populate, dynamic)
- Mobile responsive statement

**❌ AVOID:**
- Design adjectives or subjective descriptions
- Pixel-perfect design specs
- Exhaustive analytics/accessibility (put in Notes section)

### Example Format (Story #5 - User Capability Pattern)

```
1. The user will be able to navigate through product images within the product detail page
    a. The product image will dynamically change once user selects a different image
2. The user will be able to expand to full screen view, showing multiple product angles and images
    a. The user will be able to exit full screen view and navigate back to product detail page
3. The user will be able to view photos in full-size resolution

Notes:
- Performance: Images load progressively, full-size available on demand
- Accessibility: Image navigation keyboard accessible, alt text on all images
- Future: Add zoom functionality, image comparison feature
```

**Notice:** Uses functional language only - "full screen view" not "modal", "selects" not "clicks button", "navigate" not "button to go to"

### Additional Example (Story #1 - System Display Pattern)

```
1. The Product Details Page will display a 'How it Works' section below the product information
2. The 'How it Works' section will display the following information
    a. Definition of the product
    b. Hyperlink to related section for additional information
3. If the 'How it Works' section is pending or under maintenance, the section will display placeholder messaging
4. The 'How it Works' section will be mobile responsive

Notes:
- Performance: Section loads with page, no additional requests
- Accessibility: Links have descriptive text, section has proper heading
- Future: Expand to additional product categories
```

---

## Files Modified

### 1. `story_generator.py`
**Lines 38-143:** Added functional format instructions in `get_story_generation_prompt()`
- Updated docstring to include "functional" as accepted parameter
- Added complete functional format prompt with language rules and examples

**Lines 251-381:** Added functional format instructions in `get_refinement_prompt()`
- Updated docstring to include "functional" as accepted parameter
- Added comprehensive refinement guidelines for functional format

### 2. `app_ui.py`
**Lines 355-381 (Tab 1 - Generate Stories):**
- Added "Functional (Behavior-Focused)" radio button option
- Updated help text to explain all 3 formats
- Updated ac_format_value logic to handle 3 options

**Lines 645-671 (Tab 2 - Refine Stories):**
- Added "Functional (Behavior-Focused)" radio button option
- Updated help text
- Updated refine_ac_format_value logic

**Lines 893-919 (Tab 3 - Add More Stories):**
- Added "Functional (Behavior-Focused)" radio button option
- Updated help text
- Updated append_ac_format_value logic

**Lines 124-155 (`generate_stories_from_notes` function):**
- Added functional format example and requirement for API prompts
- Provides real-world example from your Excel file

---

## Testing Results

**Test File:** `test_functional_format.py`

✅ **All Tests Passed:**
- Functional format keywords: **6/6 found**
- Explicit format: Still works correctly
- Gherkin format: Still works correctly
- Functional refinement prompts: Working correctly

**Keywords Verified:**
1. "will display" ✓
2. "will show" ✓
3. "user will be able to" ✓
4. "Functional format" ✓
5. "NO design adjectives" ✓
6. "AVOID ALL DESIGN LANGUAGE" ✓

---

## How to Use

### In the Streamlit UI:

1. **Tab 1 (Generate Stories):**
   - Choose input method (upload file or paste text)
   - Under "Acceptance Criteria Format", select **"Functional (Behavior-Focused)"**
   - Generate stories

2. **Tab 2 (Refine Stories):**
   - Upload existing Excel file
   - Select story to refine
   - Choose **"Functional (Behavior-Focused)"** under AC format
   - Provide refinement instructions
   - Refine with AI

3. **Tab 3 (Add More Stories):**
   - Upload new notes and existing Excel
   - Select **"Functional (Behavior-Focused)"** under AC format
   - Add new stories

### Expected Output:

Stories will have ACs with:
- **PRIMARY pattern:** "The user will be able to [action]" (emphasizing user capabilities)
- **SECONDARY patterns:** "will display", "when user selects", "will show"
- NO design adjectives ("modern", "prominent", etc.)
- Hierarchical structure (1, a, i, 1)
- Focus on user capabilities and system behavior
- Notes section at the end

---

## Comparison: Explicit vs Functional

| Aspect | Explicit/Detailed | Functional (Behavior-Focused) |
|--------|------------------|-------------------------------|
| **Structure** | Hierarchical (1, a, i, 1) | Hierarchical (1, a, i, 1) |
| **Length** | 30-50 lines | 30-50 lines |
| **Design Language** | ✅ Allowed | ❌ NOT allowed |
| **Primary Pattern** | Can use design language | **"The user will be able to [action]"** |
| **Example Language** | "prominently displays modern interface" | "The user will be able to navigate..." |
| **Focus** | Requirements + UX considerations | User capabilities + system behavior |
| **Use Case** | Comprehensive specs with design intent | Technical specs without design opinions |

---

## Real-World Example Comparison

**User Story:** Product image gallery feature

### Explicit/Detailed Format:
```
1. The product detail page prominently displays a modern, intuitive image gallery
   a. Users can navigate through high-quality images in a streamlined carousel
   b. Elevated full-screen mode with clean visual hierarchy
   c. Images display with sophisticated, polished presentation
```

### Functional Format:
```
1. The user will be able to navigate through product images within the product detail page
    a. The product image will dynamically change once user selects different images on product detail page
2. The user will be able to expand to a full screen gallery mode, showing multiple product angles and images
    a. The user will be able to exit full screen mode and be navigated to product detail page
3. The user will be able to view photos in Full-size resolution without pixelation or quality loss
```

**Notice:**
- **Functional** emphasizes USER CAPABILITIES with "The user will be able to [action]"
- **Explicit** can use design adjectives like "prominently", "modern", "intuitive", "streamlined", "elevated", "clean", "sophisticated", "polished"
- **Functional** describes WHAT the user can DO and what the system DOES (behavior)
- **Explicit** describes both behavior AND appearance/design intent

---

## Notes

- All three AC formats (Gherkin, Explicit/Detailed, Functional) are now available
- The system automatically uses the selected format in prompts sent to Claude API
- Format choice persists throughout the session for each tab
- Excel output format remains the same - only the AC content changes
- Always includes a Notes section with performance, accessibility, analytics, and future enhancements

---

## Troubleshooting

**Q: Stories still have design language in Functional format**
**A:** The AI may occasionally slip in design adjectives. Try:
1. Re-generate with more explicit feedback: "Strictly avoid all design adjectives"
2. Use the refine function to remove design language
3. Check that "Functional (Behavior-Focused)" is selected

**Q: How do I know which format to use?**
**A:**
- **Gherkin:** For QA/testing teams who write automated tests
- **Explicit/Detailed:** When design intent and UX considerations are important
- **Functional:** When you want purely technical specifications without design opinions

---

**Implementation Complete:** 2025-01-15
**Updated:** 2025-01-15 - Emphasized "The user will be able to [action]" as primary pattern based on Excel Story #5
**Tested:** ✅ All format options working correctly
**Status:** Ready for production use

---

## Version History

**v1.2 (2025-01-15):**
- Added comprehensive UI implementation terms to AVOID list
- Added functional language replacements (button → call-to-action, etc.)
- Added UI Terms Reference table for quick lookup
- Updated all examples to remove UI component names
- Focus purely on FUNCTIONALITY, not implementation details

**v1.1 (2025-01-15):**
- Updated to emphasize **"The user will be able to [action]"** as PRIMARY pattern
- Based on real Excel examples (Postal Store Story #5)
- Reordered language rules to put user capabilities first
- Updated all examples to match Story #5 pattern
- Secondary patterns still available for system-focused statements

**v1.0 (2025-01-15):**
- Initial implementation of Functional AC format
- Added as third option alongside Gherkin and Explicit/Detailed
