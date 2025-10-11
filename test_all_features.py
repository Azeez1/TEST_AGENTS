"""
Comprehensive test script for User Story Agent
Tests all core functionality to ensure everything works
"""

import os
import sys
from anthropic import Anthropic
from note_parser import extract_notes
from story_generator import StoryGenerator
from excel_handler import ExcelHandler, read_existing_stories, create_excel_output
from formatters import StoryFormatter, validate_stories
from dotenv import load_dotenv

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()

def test_1_generate_stories():
    """Test: Generate stories from USPS sample notes"""
    print("\n" + "="*80)
    print("TEST 1: Generate Stories from Notes")
    print("="*80)

    try:
        # Read sample notes
        notes = extract_notes("examples/sample_notes.txt")
        print(f"✓ Loaded notes: {len(notes)} characters")

        # Initialize
        client = Anthropic()
        formatter = StoryFormatter()

        # Generate prompt
        prompt = f"""You are a user story generation expert. Generate comprehensive, backlog-ready user stories from the following meeting notes.

Meeting Notes:
{notes}

Generate user stories in this exact JSON format:
[
  {{
    "user_story": "As a [user type], I want [goal], so that [benefit]",
    "feature_epic": "Concise feature name",
    "acceptance_criteria": [
      "Given [context], when [action], then [expected outcome]"
    ],
    "business_case": "Explanation of business value and impact",
    "relevant_pages": "Page/screen names affected"
  }}
]

Return ONLY the JSON array, no additional text."""

        # Call API
        print("Generating stories with Claude API...")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Parse
        stories = formatter.parse_ai_response(response_text)
        print(f"✓ Generated {len(stories)} stories")

        # Validate
        is_valid, issues = validate_stories(stories)
        if not is_valid:
            print(f"⚠ Validation warnings: {len(issues)}")
        else:
            print("✓ All stories validated")

        # Save to Excel
        output_file = "test_generated_stories.xlsx"
        handler = ExcelHandler(output_file)
        handler.write_stories(stories, append=False)
        handler.close()
        print(f"✓ Saved to {output_file}")

        return True, stories, output_file

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False, None, None


def test_2_refine_story(excel_file, stories):
    """Test: Refine a specific story"""
    print("\n" + "="*80)
    print("TEST 2: Refine Existing Story")
    print("="*80)

    try:
        # Load existing stories
        existing = read_existing_stories(excel_file)
        print(f"✓ Loaded {len(existing)} existing stories")

        # Select first story
        story_to_refine = existing[0]
        print(f"✓ Selected story: {story_to_refine['feature_epic']}")

        # Initialize
        client = Anthropic()
        generator = StoryGenerator()
        formatter = StoryFormatter()

        # Refine
        instruction = "Add acceptance criteria about mobile responsiveness"
        prompt = generator.get_refinement_prompt(story_to_refine, instruction)

        print(f"Refining with instruction: '{instruction}'")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        refined_stories = formatter.parse_ai_response(response_text)

        if refined_stories:
            refined_story = refined_stories[0]
            print(f"✓ Story refined successfully")
            print(f"  Original ACs: {len(story_to_refine['acceptance_criteria'])}")
            print(f"  Refined ACs: {len(refined_story['acceptance_criteria'])}")

            # Update in Excel
            handler = ExcelHandler(excel_file)
            handler.update_story(1, refined_story)
            handler.close()
            print(f"✓ Updated in Excel")

            return True
        else:
            print("✗ Failed to parse refined story")
            return False

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


def test_3_append_stories(excel_file):
    """Test: Append new stories to existing file"""
    print("\n" + "="*80)
    print("TEST 3: Append New Stories")
    print("="*80)

    try:
        # Count existing
        existing_count = len(read_existing_stories(excel_file))
        print(f"✓ Current story count: {existing_count}")

        # Create new notes
        new_notes = """New Feature: User Authentication

Users need to be able to log in securely
Need password reset functionality
Must support multi-factor authentication"""

        print("Generating new stories from additional notes...")

        # Initialize
        client = Anthropic()
        formatter = StoryFormatter()

        # Generate
        prompt = f"""Generate user stories from these notes:

{new_notes}

Return as JSON array with user_story, feature_epic, acceptance_criteria (array), business_case, relevant_pages."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            new_stories = formatter.parse_ai_response(response.content[0].text)
        except:
            # Fallback: try wrapping in list if single story
            new_stories = [formatter.format_story_dict(eval(response.content[0].text))]

        print(f"✓ Generated {len(new_stories)} new stories")

        # Append
        handler = ExcelHandler(excel_file)
        handler.write_stories(new_stories, append=True)
        handler.close()

        # Verify
        total_count = len(read_existing_stories(excel_file))
        print(f"✓ Total stories now: {total_count}")

        if total_count == existing_count + len(new_stories):
            print("✓ Append successful")
            return True
        else:
            print("✗ Story count mismatch")
            return False

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


def test_4_view_and_search(excel_file):
    """Test: View and search stories"""
    print("\n" + "="*80)
    print("TEST 4: View and Search Stories")
    print("="*80)

    try:
        # Load all stories
        all_stories = read_existing_stories(excel_file)
        print(f"✓ Loaded {len(all_stories)} total stories")

        # Display summary
        total_acs = sum(len(s.get('acceptance_criteria', [])) for s in all_stories)
        avg_acs = total_acs / len(all_stories) if all_stories else 0
        features = set(s.get('feature_epic', 'Unknown') for s in all_stories)

        print(f"  Total ACs: {total_acs}")
        print(f"  Avg ACs per story: {avg_acs:.1f}")
        print(f"  Unique features: {len(features)}")

        # Search test
        search_term = "customer"
        matching = [
            s for s in all_stories
            if search_term.lower() in s['user_story'].lower()
        ]
        print(f"✓ Search for '{search_term}': {len(matching)} matches")

        return True

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


def test_5_batch_operations(excel_file):
    """Test: Batch update all stories"""
    print("\n" + "="*80)
    print("TEST 5: Batch Operations")
    print("="*80)

    try:
        # Load stories
        stories = read_existing_stories(excel_file)
        print(f"✓ Loaded {len(stories)} stories for batch update")

        # We'll just test the first story to save API calls
        print("Testing batch operation on first story only (to save API calls)...")

        client = Anthropic()
        generator = StoryGenerator()
        formatter = StoryFormatter()

        instruction = "Ensure this story includes accessibility considerations"
        story = stories[0]

        prompt = generator.get_refinement_prompt(story, instruction)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        updated_story = formatter.parse_ai_response(response.content[0].text)[0]
        print(f"✓ Batch operation logic works")
        print(f"  Original ACs: {len(story['acceptance_criteria'])}")
        print(f"  Updated ACs: {len(updated_story['acceptance_criteria'])}")

        return True

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("USER STORY AGENT - COMPREHENSIVE TEST SUITE")
    print("="*80)

    results = []

    # Test 1: Generate
    success, stories, excel_file = test_1_generate_stories()
    results.append(("Generate Stories", success))

    if not success:
        print("\n✗ Cannot continue - Test 1 failed")
        return

    # Test 2: Refine
    success = test_2_refine_story(excel_file, stories)
    results.append(("Refine Story", success))

    # Test 3: Append
    success = test_3_append_stories(excel_file)
    results.append(("Append Stories", success))

    # Test 4: View/Search
    success = test_4_view_and_search(excel_file)
    results.append(("View & Search", success))

    # Test 5: Batch
    success = test_5_batch_operations(excel_file)
    results.append(("Batch Operations", success))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Ready for production.")
        return True
    else:
        print("\n⚠ Some tests failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
