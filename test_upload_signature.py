"""
Quick test to verify the upload API endpoint signature
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_upload_signature():
    """Test that upload function has correct signature"""

    print("="*70)
    print("UPLOAD API SIGNATURE TEST")
    print("="*70)

    try:
        from routers.documents import upload_documents
        import inspect

        sig = inspect.signature(upload_documents)

        print("\n✅ Upload function found: upload_documents")
        print("\n📋 Function Parameters:")

        for param_name, param in sig.parameters.items():
            annotation = param.annotation if param.annotation != inspect.Parameter.empty else 'Any'
            default = param.default if param.default != inspect.Parameter.empty else 'Required'

            print(f"   • {param_name}")
            print(f"     Type: {annotation}")
            print(f"     Default: {default}")
            print()

        # Check for problematic file_path parameter
        if 'file_path' in sig.parameters:
            print("❌ ERROR: Found unexpected 'file_path' parameter!")
            print("   This should not be in the upload function signature.")
            return False
        else:
            print("✅ No 'file_path' parameter found - CORRECT")

        # Check required parameters
        required_params = ['background_tasks', 'files', 'current_user', 'db']
        for param in required_params:
            if param in sig.parameters:
                print(f"✅ Required parameter '{param}' found")
            else:
                print(f"❌ Missing required parameter '{param}'")
                return False

        # Check optional parameters
        optional_params = ['order_number', 'driver_user_id', 'customer_id']
        for param in optional_params:
            if param in sig.parameters:
                print(f"✅ Optional parameter '{param}' found")

        print("\n" + "="*70)
        print("✅ UPLOAD API SIGNATURE IS CORRECT")
        print("="*70)
        print("\nThe /api/documents/upload endpoint should work correctly.")
        print("If you're getting an error, please share the exact error message.")

        return True

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Cannot import the upload function - check if file exists")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_upload_signature()
    sys.exit(0 if success else 1)

