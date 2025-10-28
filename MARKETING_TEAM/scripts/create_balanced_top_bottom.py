"""Create balanced mind map - 6 EPICs above, 6 EPICs below the center"""
import pandas as pd

FILE1 = r"C:\Users\sabaa\Downloads\DMA_Epic & Features Hierarchy - FY26Q1P2.xlsx"
FILE2 = r"C:\Users\sabaa\Downloads\DMA Q1Part2 Features.xlsx"
OUTPUT = r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\diagrams\obo_balanced_top_bottom.mmd"

def clean_text(text):
    """Clean text for Mermaid - keep O&M and OBO"""
    if pd.isna(text):
        return ""
    text = str(text)

    # Preserve O&M and OBO
    text = text.replace('O&M', '<<<OandM>>>')
    text = text.replace('OBO', '<<<OBO>>>')

    # Clean special characters
    text = text.replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')
    text = text.replace('"', '').replace("'", '')
    text = text.replace('&', 'and')
    text = text.replace(':', '-')
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('?', '')
    text = text.replace(',', '')
    text = text.replace('#', 'num')

    # Restore O&M and OBO
    text = text.replace('<<<OandM>>>', 'O&M')
    text = text.replace('<<<OBO>>>', 'OBO')

    # Shorten text
    if len(text) > 45:
        text = text[:42] + '...'

    return text.strip()

def make_id(text, prefix=''):
    """Create valid node ID"""
    clean = ''.join(c if c.isalnum() else '_' for c in text)
    return f"{prefix}{clean[:20]}"

# Read Excel files
print("Reading Excel files...")
df1 = pd.read_excel(FILE1)
df2 = pd.read_excel(FILE2)

# Get all EPICs
epics_with_features = {}
for parent in df2['Parent'].dropna().unique():
    features = df2[df2['Parent'] == parent]
    epics_with_features[parent] = list(features['Title'])

# Handle orphans
orphans = df2[df2['Parent'].isna()]
if len(orphans) > 0:
    epics_with_features['Uncategorized'] = list(orphans['Title'])

# Split into top and bottom
epic_items = sorted(epics_with_features.items())
mid_point = len(epic_items) // 2
top_epics = epic_items[:mid_point]
bottom_epics = epic_items[mid_point:]

print(f"Creating balanced layout:")
print(f"  Top: {len(top_epics)} EPICs")
print(f"  Bottom: {len(bottom_epics)} EPICs")

# Create flowchart
lines = [
    "graph TB",
    "    ",
    "    classDef rootStyle fill:#2ecc71,stroke:#333,stroke-width:5px,color:#fff,font-size:20px,font-weight:bold",
    "    classDef epicStyle fill:#667eea,stroke:#333,stroke-width:3px,color:#fff,font-size:14px",
    "    classDef featureStyle fill:#f093fb,stroke:#333,stroke-width:2px,font-size:12px",
    ""
]

# TOP SECTION - 6 EPICs above (they connect TO the root)
print("\nTop EPICs:")
for epic_name, features in top_epics:
    epic_clean = clean_text(epic_name)
    epic_id = make_id(epic_name, 'TOP_')
    print(f"  - {epic_clean}")

    lines.append(f"    subgraph {epic_id}_GROUP[\" \"]")
    lines.append(f"        direction TB")

    # For top EPICs: Add features first (they'll appear above)
    # Chain from top to bottom: Feature3 -> Feature2 -> Feature1 -> EPIC
    feature_ids = []
    for idx, feature in enumerate(features):
        feature_clean = clean_text(feature)
        feature_id = make_id(feature, f'{epic_id}_F{idx}_')
        feature_ids.append(feature_id)
        lines.append(f"        {feature_id}[{feature_clean}]")

    # Add EPIC at the bottom
    lines.append(f"        {epic_id}[{epic_clean}]")

    # Chain features downward to EPIC (reverse order so topmost feature is first)
    if feature_ids:
        # Chain features together from top to bottom
        for i in range(len(feature_ids) - 1, 0, -1):
            lines.append(f"        {feature_ids[i]} --> {feature_ids[i-1]}")
        # Connect last feature to EPIC
        lines.append(f"        {feature_ids[0]} --> {epic_id}")

    lines.append(f"    end")
    lines.append(f"    {epic_id} --> ROOT")
    lines.append("")

# ROOT NODE (center)
lines.append("    ROOT([OBO Construction Initiatives])")
lines.append("")

# BOTTOM SECTION - 6 EPICs below (root connects TO them)
print("\nBottom EPICs:")
for epic_name, features in bottom_epics:
    epic_clean = clean_text(epic_name)
    epic_id = make_id(epic_name, 'BOT_')
    print(f"  - {epic_clean}")

    lines.append(f"    ROOT --> {epic_id}")
    lines.append(f"    subgraph {epic_id}_GROUP[\" \"]")
    lines.append(f"        direction TB")
    lines.append(f"        {epic_id}[{epic_clean}]")

    # Add features - chain them vertically
    prev_id = epic_id
    for idx, feature in enumerate(features):
        feature_clean = clean_text(feature)
        feature_id = make_id(feature, f'{epic_id}_F{idx}_')
        lines.append(f"        {feature_id}[{feature_clean}]")
        lines.append(f"        {prev_id} --> {feature_id}")
        prev_id = feature_id  # Chain to next feature

    lines.append(f"    end")
    lines.append("")

# Apply styles
lines.append("    class ROOT rootStyle")
for epic_name, _ in top_epics:
    epic_id = make_id(epic_name, 'TOP_')
    lines.append(f"    class {epic_id} epicStyle")
for epic_name, _ in bottom_epics:
    epic_id = make_id(epic_name, 'BOT_')
    lines.append(f"    class {epic_id} epicStyle")

mermaid_code = "\n".join(lines)

# Save
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(mermaid_code)

print(f"\nSaved: {OUTPUT}")
print(f"Total EPICs: {len(epics_with_features)}")
print(f"Total Features: {sum(len(f) for f in epics_with_features.values())}")
