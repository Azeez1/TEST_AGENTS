"""
Script to update all agent tool references to use MCP prefixes
"""

import os
import re
from pathlib import Path

# Tool mappings: old name -> new MCP name
TOOL_MAPPINGS = {
    "generate_gpt4o_image": "mcp__marketing-tools__generate_gpt4o_image",
    "format_twitter_post": "mcp__marketing-tools__format_twitter_post",
    "format_linkedin_post": "mcp__marketing-tools__format_linkedin_post",
    "extract_hashtags": "mcp__marketing-tools__extract_hashtags",
    "optimize_post_for_engagement": "mcp__marketing-tools__optimize_post_for_engagement",
    "create_post_variations": "mcp__marketing-tools__create_post_variations",
    "send_gmail": "mcp__marketing-tools__send_gmail",
    "create_gmail_draft": "mcp__marketing-tools__create_gmail_draft",
    "send_email_campaign": "mcp__marketing-tools__send_email_campaign",
    "classify_intent": "mcp__marketing-tools__classify_intent",
    "get_agent_capabilities": "mcp__marketing-tools__get_agent_capabilities",
    "list_available_agents": "mcp__marketing-tools__list_available_agents",
    "format_agent_response": "mcp__marketing-tools__format_agent_response",
    "upload_file_to_drive": "mcp__marketing-tools__upload_file_to_drive",
    "generate_sora_video": "mcp__marketing-tools__generate_sora_video",
}

# Text replacements in instructions
TEXT_REPLACEMENTS = [
    ("Always use get_brand_voice tool first", "Read brand voice guidelines from memory/brand_voice.json"),
    ("Use get_brand_voice tool", "Read brand voice from memory/brand_voice.json"),
    ("Use get_visual_guidelines tool", "Read visual guidelines from memory/visual_guidelines.json"),
    ("get_visual_guidelines tool to load", "visual guidelines from memory/visual_guidelines.json for"),
]

def update_agent_file(file_path):
    """Update a single agent file"""
    print(f"\nUpdating: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # Update tool names in YAML frontmatter tools list
    for old_tool, new_tool in TOOL_MAPPINGS.items():
        # Match tool in list (with proper indentation)
        pattern = rf'^(\s+)-\s+{re.escape(old_tool)}$'
        replacement = rf'\1- {new_tool}'

        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            changes.append(f"  - Updated tool: {old_tool} -> {new_tool}")
            content = new_content

    # Update tool references in body text
    for old_tool, new_tool in TOOL_MAPPINGS.items():
        # Match tool names in markdown text, code blocks, etc.
        pattern = rf'\b{re.escape(old_tool)}\b'
        new_content = re.sub(pattern, new_tool, content)
        if new_content != content and old_tool not in str(changes):
            changes.append(f"  - Updated text reference: {old_tool}")
            content = new_content

    # Update get_brand_voice and get_visual_guidelines references
    for old_text, new_text in TEXT_REPLACEMENTS:
        if old_text in content:
            content = content.replace(old_text, new_text)
            changes.append(f"  - Updated instruction: '{old_text[:40]}...'")

    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  Changes made:")
        for change in changes:
            print(change)
        return True
    else:
        print("  No changes needed")
        return False

def main():
    """Update all agent files"""
    agents_dir = Path(__file__).parent / ".claude" / "agents"

    print(f"Scanning agents directory: {agents_dir}")

    if not agents_dir.exists():
        print(f"ERROR: Agents directory not found: {agents_dir}")
        return

    agent_files = list(agents_dir.glob("*.md"))
    print(f"Found {len(agent_files)} agent files")

    updated_count = 0
    for agent_file in agent_files:
        if update_agent_file(agent_file):
            updated_count += 1

    print(f"\n✅ Complete! Updated {updated_count}/{len(agent_files)} agent files")
    print("\nNext steps:")
    print("1. Review the changes in .claude/agents/*.md")
    print("2. Test agents by invoking them through Claude Code")
    print("3. Check that tools are registered: restart Claude Code if needed")

if __name__ == "__main__":
    main()
