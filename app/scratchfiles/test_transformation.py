#!/usr/bin/env python3
"""
Test script to verify the company transformation works correctly.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import our transformation module
sys.path.append(str(Path(__file__).parent))

from transform_companies import transform_companies_to_qa_format


def test_transformation():
    """Test the transformation with a small sample."""
    print("Testing company transformation...")

    # Test with a small sample - use Path to handle relative paths correctly
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    csv_path = (
        project_root / "data" / "datasets" / "external" / "companies-2023-q4-sm.csv"
    )
    output_path = (
        project_root / "data" / "datasets" / "test_transformed_companies.jsonl"
    )

    try:
        transform_companies_to_qa_format(csv_path, output_path, sample_size=10)

        # Verify the output file was created and has content
        if Path(output_path).exists():
            with open(output_path, "r") as f:
                lines = f.readlines()
                print(f"✅ Successfully created {output_path}")
                print(f"✅ Generated {len(lines)} QA pairs")

                # Show first few lines as preview
                print("\nPreview of first few QA pairs:")
                for i, line in enumerate(lines[:3]):
                    print(f"Line {i + 1}: {line.strip()}")

        else:
            print("❌ Output file was not created")

    except Exception as e:
        print(f"❌ Error during transformation: {e}")


if __name__ == "__main__":
    test_transformation()
