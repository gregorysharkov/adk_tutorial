#!/usr/bin/env python3
"""
Test script to verify the updated evaluation runner can load both datasets.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import our evaluation module
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.runner import get_dataset_stats, _load_eval_items


def test_dataset_loading():
    """Test that the evaluation runner can load both datasets."""
    print("Testing dataset loading...")

    # Test dataset statistics
    stats = get_dataset_stats()
    print("\n📊 Dataset Statistics:")
    print(
        f"Original dataset: {stats.get('original_dataset', {}).get('item_count', 'N/A')} items"
    )
    print(
        f"Transformed dataset: {stats.get('transformed_dataset', {}).get('item_count', 'N/A')} items"
    )
    print(
        f"Combined total: {stats.get('combined', {}).get('total_items', 'N/A')} items"
    )

    # Test loading combined datasets
    print("\n🔄 Testing combined dataset loading...")
    try:
        items = _load_eval_items()
        print(f"✅ Successfully loaded {len(items)} total items")

        # Show some sample items
        print(f"\n📝 Sample items:")
        for i, item in enumerate(items[:3]):
            print(f"  {i + 1}. {item.company}: {item.question[:50]}...")

        # Count items by source (approximate)
        original_companies = {"Google", "Apple", "Microsoft", "Amazon", "Meta"}
        original_count = sum(1 for item in items if item.company in original_companies)
        transformed_count = len(items) - original_count

        print(f"\n📈 Item breakdown:")
        print(f"  Original dataset items: ~{original_count}")
        print(f"  Transformed dataset items: ~{transformed_count}")

    except Exception as e:
        print(f"❌ Error loading combined datasets: {e}")


if __name__ == "__main__":
    test_dataset_loading()
