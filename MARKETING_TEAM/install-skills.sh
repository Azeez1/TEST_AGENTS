#!/bin/bash
# Install Anthropic skills to MARKETING_TEAM project

echo "Installing Anthropic skills to MARKETING_TEAM..."

# Create skills directory
mkdir -p .claude/skills

# Clone the official skills repo
echo "Cloning Anthropic skills repository..."
git clone https://github.com/anthropics/skills temp-anthropic-skills

# Copy skills to project
echo "Copying skills..."
cp -r temp-anthropic-skills/algorithmic-art .claude/skills/
cp -r temp-anthropic-skills/artifacts-builder .claude/skills/
cp -r temp-anthropic-skills/canvas-design .claude/skills/
cp -r temp-anthropic-skills/slack-gif-creator .claude/skills/
cp -r temp-anthropic-skills/theme-factory .claude/skills/
cp -r temp-anthropic-skills/internal-comms .claude/skills/
cp -r temp-anthropic-skills/brand-guidelines .claude/skills/
cp -r temp-anthropic-skills/mcp-builder .claude/skills/
cp -r temp-anthropic-skills/skill-creator .claude/skills/
cp -r temp-anthropic-skills/document-skills .claude/skills/

# Clean up
echo "Cleaning up..."
rm -rf temp-anthropic-skills

echo "✅ Skills installed successfully!"
echo ""
echo "Installed skills:"
ls -1 .claude/skills/
echo ""
echo "Skills are now available in Claude Code."
echo "Test with: 'Use the algorithmic-art skill to create a flow field design'"
