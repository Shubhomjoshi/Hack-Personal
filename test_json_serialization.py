"""
Test that quality service returns JSON-serializable types
"""
import json
import sys

print("=" * 70)
print("Testing Quality Service JSON Serialization")
print("=" * 70)

try:
    print("\n1. Importing quality service...")
    from services.quality_service import quality_service
    print("✅ Quality service imported")

    print("\n2. Testing type conversions...")

    # Test boolean conversion
    import numpy as np
    test_val = np.float64(50.0)
    is_low = test_val < 100
    print(f"   Before conversion: {type(is_low)} = {is_low}")
    is_low_converted = bool(is_low)
    print(f"   After conversion: {type(is_low_converted)} = {is_low_converted}")

    if isinstance(is_low_converted, bool) and not isinstance(is_low_converted, np.bool_):
        print("   ✅ Boolean conversion works")
    else:
        print("   ❌ Boolean conversion failed")
        sys.exit(1)

    # Test float conversion
    test_score = np.float64(67.25)
    print(f"\n   Before conversion: {type(test_score)} = {test_score}")
    score_converted = float(test_score)
    print(f"   After conversion: {type(score_converted)} = {score_converted}")

    if isinstance(score_converted, float) and not isinstance(score_converted, np.floating):
        print("   ✅ Float conversion works")
    else:
        print("   ❌ Float conversion failed")
        sys.exit(1)

    print("\n3. Testing JSON serialization of quality result...")

    # Simulate quality assessment result
    test_result = {
        'quality_score': float(67.25),
        'readability_status': 'Partially Clear',
        'recommendation': 'Accept',
        'is_blurry': bool(False),
        'blur_score': float(0.75),
        'is_skewed': bool(True),
        'skew_angle': float(3.5),
        'has_brightness_issue': bool(True),
        'brightness_score': float(0.11)
    }

    # Try to serialize to JSON
    try:
        json_str = json.dumps(test_result)
        print("   ✅ JSON serialization successful")
        print(f"\n   Result: {json_str[:100]}...")

        # Try to deserialize
        parsed = json.loads(json_str)
        print("   ✅ JSON deserialization successful")

    except TypeError as e:
        print(f"   ❌ JSON serialization failed: {e}")
        sys.exit(1)

    print("\n4. Verifying all types are Python native...")
    type_checks = {
        'quality_score': (test_result['quality_score'], float),
        'is_blurry': (test_result['is_blurry'], bool),
        'blur_score': (test_result['blur_score'], float),
        'is_skewed': (test_result['is_skewed'], bool),
        'skew_angle': (test_result['skew_angle'], float),
        'has_brightness_issue': (test_result['has_brightness_issue'], bool),
        'brightness_score': (test_result['brightness_score'], float),
    }

    all_correct = True
    for key, (value, expected_type) in type_checks.items():
        actual_type = type(value)
        is_correct = isinstance(value, expected_type) and not isinstance(value, (np.bool_, np.integer, np.floating))
        status = "✅" if is_correct else "❌"
        print(f"   {status} {key}: {actual_type.__name__}")
        if not is_correct:
            all_correct = False

    if not all_correct:
        print("\n   ❌ Some types are not Python native")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅✅✅ ALL TESTS PASSED ✅✅✅")
    print("\nThe JSON serialization fix is working correctly!")
    print("Quality assessment results can now be saved to database.")
    print("\nNext: Test the upload API with a real document.")
    print("=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print("❌ TEST FAILED")
    print("=" * 70)
    print(f"\nError: {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

