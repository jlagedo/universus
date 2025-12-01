#!/usr/bin/env python3
"""
Test runner script for Universus.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run with coverage report
    python run_tests.py --verbose    # Run with verbose output
    python run_tests.py --module database  # Run specific module tests
"""

import sys
import subprocess
import argparse


def run_tests(module=None, verbose=False, coverage=False):
    """Run tests with specified options."""
    
    cmd = ["pytest"]
    
    # Add test file if module specified
    if module:
        cmd.append(f"test_{module}.py")
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing:skip-covered", "--cov-report=html"])
    
    # Run tests
    print(f"Running: {' '.join(cmd)}")
    print("=" * 70)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        if coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n" + "=" * 70)
        print("❌ Some tests failed!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run Universus tests")
    parser.add_argument(
        "--module",
        choices=["database", "api_client", "service", "ui"],
        help="Run tests for specific module only"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Run tests with verbose output"
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests without coverage"
    )
    
    args = parser.parse_args()
    
    # Quick mode overrides coverage
    if args.quick:
        args.coverage = False
    
    run_tests(
        module=args.module,
        verbose=args.verbose,
        coverage=args.coverage
    )


if __name__ == "__main__":
    main()
