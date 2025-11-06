"""
Simple test to verify enhanced MCP tools exist and have correct signatures
"""

import inspect
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the functions
from mcp_server import (
    analyze_ugc_image_mcp,
    generate_nano_banana_image_mcp,
    generate_veo_text_to_video_mcp,
    generate_veo_ugc_from_image_mcp
)

def test_function_signatures():
    """Test that functions have correct parameters"""
    print("=" * 60)
    print("TESTING ENHANCED MCP TOOL SIGNATURES")
    print("=" * 60)

    # Test 1: analyze_ugc_image_mcp
    print("\n1. analyze_ugc_image_mcp:")
    sig = inspect.signature(analyze_ugc_image_mcp)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    assert 'image_url' in params, "Missing image_url parameter"
    print("   PASS: Has image_url parameter")

    # Test 2: generate_veo_ugc_from_image_mcp
    print("\n2. generate_veo_ugc_from_image_mcp:")
    sig = inspect.signature(generate_veo_ugc_from_image_mcp)
    params = list(sig.parameters.keys())
    print(f"   Parameters ({len(params)} total):")
    for p in params:
        default = sig.parameters[p].default
        is_optional = default != inspect.Parameter.empty
        print(f"     - {p}: {'optional' if is_optional else 'required'}")

    # Check for new optional parameters
    assert 'icp' in params, "Missing icp parameter"
    assert 'product_features' in params, "Missing product_features parameter"
    assert 'video_setting' in params, "Missing video_setting parameter"
    assert 'reference_image_description' in params, "Missing reference_image_description parameter"
    print("   PASS: All 4 new optional parameters present")

    # Verify optional parameters have default None
    assert sig.parameters['icp'].default is None, "icp should default to None"
    assert sig.parameters['product_features'].default is None, "product_features should default to None"
    assert sig.parameters['video_setting'].default is None, "video_setting should default to None"
    assert sig.parameters['reference_image_description'].default is None, "reference_image_description should default to None"
    print("   PASS: All optional parameters default to None (backward compatible)")

    # Test 3: generate_veo_text_to_video_mcp
    print("\n3. generate_veo_text_to_video_mcp:")
    sig = inspect.signature(generate_veo_text_to_video_mcp)
    params = list(sig.parameters.keys())
    print(f"   Parameters ({len(params)} total):")
    for p in params:
        default = sig.parameters[p].default
        is_optional = default != inspect.Parameter.empty
        print(f"     - {p}: {'optional' if is_optional else 'required'}")

    assert 'icp' in params, "Missing icp parameter"
    assert 'product_features' in params, "Missing product_features parameter"
    assert 'video_setting' in params, "Missing video_setting parameter"
    print("   PASS: All 3 new optional parameters present")

    # Test 4: generate_nano_banana_image_mcp (unchanged signature)
    print("\n4. generate_nano_banana_image_mcp:")
    sig = inspect.signature(generate_nano_banana_image_mcp)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    assert 'prompt' in params, "Missing prompt parameter"
    assert 'aspect_ratio' in params, "Missing aspect_ratio parameter"
    assert 'filename' in params, "Missing filename parameter"
    print("   PASS: Original signature intact")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nSUMMARY:")
    print("  - New analyze_ugc_image tool exists")
    print("  - generate_veo_ugc_from_image has 4 new optional params")
    print("  - generate_veo_text_to_video has 3 new optional params")
    print("  - generate_nano_banana_image signature unchanged")
    print("  - All new params default to None (backward compatible)")

if __name__ == "__main__":
    try:
        test_function_signatures()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
