"""
Test runner for Tata AI Legal Document Intelligence.
Discovers and runs all unit and integration tests using Python's built-in unittest framework.
"""

import sys
import unittest

def run_all_tests():
    print("=" * 60)
    print("⚖️  Tata AI Legal Document Intelligence - Running Test Suite")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed successfully!")
        return 0
    else:
        print(f"\n❌ Test suite finished with {len(result.failures)} failures and {len(result.errors)} errors.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
