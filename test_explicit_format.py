"""
Test script to verify the Explicit/Detailed AC format
"""

from story_generator import StoryGenerator

# Test prompt generation
generator = StoryGenerator()

test_notes = """
Meeting Notes:
- Users need to enter package weight
- Weight must be in pounds and ounces
- Maximum weight is 70 pounds
- System should validate input
"""

# Generate prompt with explicit format
prompt = generator.get_story_generation_prompt(test_notes, ac_format="explicit")

print("="*80)
print("EXPLICIT FORMAT PROMPT TEST")
print("="*80)
print(prompt)
print("\n" + "="*80)
print("PROMPT VERIFICATION CHECKLIST:")
print("="*80)

# Check for key elements in the prompt
checks = [
    ("Hierarchical numbering mentioned", "hierarchical numbering" in prompt.lower()),
    ("Start with page template", "The [Page" in prompt),
    ("Required fields marking", "(Required)" in prompt),
    ("If...then statements", "If...then" in prompt or "If the user" in prompt),
    ("Validation rules", "validation" in prompt.lower()),
    ("Progress Bar mentioned", "Progress Bar" in prompt),
    ("Cancel mentioned", "Cancel" in prompt),
    ("Continue section", "Continue" in prompt),
    ("Error messages", "error message" in prompt.lower()),
    ("Example provided", "Example" in prompt),
]

for check_name, passed in checks:
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {check_name}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
