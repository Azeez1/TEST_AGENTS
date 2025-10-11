"""
Test script to verify all 7 AC templates are present and comprehensive
"""

from story_generator import StoryGenerator

def test_template_presence():
    """Verify all 7 templates are included in the prompt"""
    generator = StoryGenerator()

    test_notes = "Test meeting notes about a feature"
    prompt = generator.get_story_generation_prompt(test_notes, ac_format="explicit")

    print("="*80)
    print("COMPREHENSIVE TEMPLATE VERIFICATION")
    print("="*80)

    # Check for all 7 templates
    templates = [
        ("Template 1 - UI/Form", "TEMPLATE 1: UI/FORM STORIES"),
        ("Template 2 - Dashboard", "TEMPLATE 2: DASHBOARD/LIST STORIES"),
        ("Template 3 - Backend/API", "TEMPLATE 3: BACKEND/API STORIES"),
        ("Template 4 - Notifications", "TEMPLATE 4: NOTIFICATION STORIES"),
        ("Template 5 - Business Logic", "TEMPLATE 5: BUSINESS LOGIC/CALCULATION STORIES"),
        ("Template 6 - Reports", "TEMPLATE 6: REPORT/EXPORT STORIES"),
        ("Template 7 - Search", "TEMPLATE 7: SEARCH/FILTER STORIES"),
    ]

    print("\n[TEMPLATE PRESENCE CHECK]")
    all_present = True
    for name, marker in templates:
        present = marker in prompt
        status = "[PASS]" if present else "[FAIL]"
        print(f"{status} {name}")
        if not present:
            all_present = False

    # Check for universal checklist
    print("\n[UNIVERSAL CHECKLIST]")
    universal_items = [
        "UNIVERSAL CHECKLIST",
        "Trigger/Entry Point",
        "Inputs",
        "Processing/Logic",
        "Outputs",
        "Validation Rules",
        "Error Handling",
        "Edge Cases",
        "Permissions",
        "State Changes",
        "Success Criteria"
    ]

    for item in universal_items:
        present = item in prompt
        status = "[PASS]" if present else "[FAIL]"
        print(f"{status} {item}")
        if not present:
            all_present = False

    # Check for common patterns
    print("\n[COMMON PATTERNS]")
    patterns = [
        "COMMON PATTERNS",
        "Validation:",
        "Navigation:",
        "Cross-reference:",
        "Pre-population:",
        "Permissions:"
    ]

    for pattern in patterns:
        present = pattern in prompt
        status = "[PASS]" if present else "[FAIL]"
        print(f"{status} {pattern}")
        if not present:
            all_present = False

    # Check for template selection guide
    print("\n[TEMPLATE SELECTION GUIDE]")
    guide_items = [
        "TEMPLATE SELECTION GUIDE",
        "Template 1 - UI/Form Stories",
        "Template 2 - Dashboard/List Views",
        "Template 3 - Backend/API",
        "Template 4 - Notifications",
        "Template 5 - Business Logic",
        "Template 6 - Reports/Exports",
        "Template 7 - Search/Filter"
    ]

    for item in guide_items:
        present = item in prompt
        status = "[PASS]" if present else "[FAIL]"
        print(f"{status} {item}")
        if not present:
            all_present = False

    # Check template structures
    print("\n[TEMPLATE STRUCTURE ELEMENTS]")
    structure_elements = [
        ("Hierarchical numbering", "hierarchical numbering"),
        ("HTTP status codes (API)", "HTTP 200"),
        ("Error response handling", "Error (HTTP"),
        ("Timeout handling", "Timeout handling"),
        ("Notification triggers", "Notification triggers"),
        ("Calculation logic", "Calculation logic"),
        ("Report filters", "Report filters"),
        ("Search behavior", "Search behavior"),
        ("Empty state handling", "Empty state"),
    ]

    for name, marker in structure_elements:
        present = marker in prompt
        status = "[PASS]" if present else "[FAIL]"
        print(f"{status} {name}")
        if not present:
            all_present = False

    # Test refinement prompt
    print("\n[REFINEMENT PROMPT CHECK]")
    test_story = {
        'user_story': 'As a user, I want to search packages',
        'feature_epic': 'Search',
        'acceptance_criteria': ['Test AC'],
        'business_case': 'Test case',
        'relevant_pages': 'Search Page'
    }

    refinement_prompt = generator.get_refinement_prompt(
        test_story,
        "Add error handling",
        ac_format="explicit"
    )

    refinement_checks = [
        ("Template selection in refinement", "Template Selection"),
        ("Universal requirements in refinement", "Universal Requirements"),
        ("Common patterns in refinement", "Common Patterns"),
        ("What to avoid in refinement", "What to Avoid"),
    ]

    for name, marker in refinement_checks:
        present = marker in refinement_prompt
        status = "[PASS]" if present else "[FAIL]"
        print(f"{status} {name}")
        if not present:
            all_present = False

    # Summary
    print("\n" + "="*80)
    if all_present:
        print("[SUCCESS] All templates and elements are present!")
        print("="*80)
        return True
    else:
        print("[FAILURE] Some elements are missing. Review output above.")
        print("="*80)
        return False

def test_template_examples():
    """Show example story types for each template"""
    print("\n" + "="*80)
    print("TEMPLATE USE CASE EXAMPLES")
    print("="*80)

    examples = {
        "Template 1 (UI/Form)": [
            "User enters shipping address",
            "User fills out payment form",
            "User completes multi-step checkout wizard"
        ],
        "Template 2 (Dashboard)": [
            "User views shipping history dashboard",
            "User sees list of saved addresses",
            "Admin views user management table"
        ],
        "Template 3 (Backend/API)": [
            "System processes payment via payment gateway",
            "System syncs tracking data from carrier API",
            "System validates address via USPS API"
        ],
        "Template 4 (Notifications)": [
            "User receives package delivery notification",
            "User gets email about failed payment",
            "User receives push alert for tracking update"
        ],
        "Template 5 (Business Logic)": [
            "System calculates shipping rate based on weight",
            "System determines user eligibility for discount",
            "System applies tax calculation rules"
        ],
        "Template 6 (Reports)": [
            "User exports shipping history to CSV",
            "Admin generates monthly revenue report",
            "System creates PDF invoice for order"
        ],
        "Template 7 (Search)": [
            "User searches for package by tracking number",
            "User filters addresses by city",
            "User queries orders by date range"
        ]
    }

    for template, use_cases in examples.items():
        print(f"\n{template}:")
        for i, use_case in enumerate(use_cases, 1):
            print(f"  {i}. {use_case}")

    print("\n" + "="*80)

if __name__ == "__main__":
    # Run template presence test
    success = test_template_presence()

    # Show examples
    test_template_examples()

    # Final result
    if success:
        print("\n[PASS] All comprehensive template tests passed!")
        exit(0)
    else:
        print("\n[FAIL] Some tests failed. Review output above.")
        exit(1)
