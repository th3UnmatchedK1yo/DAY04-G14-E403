from __future__ import annotations

import unittest

from tools.deduplicate.tool import deduplicate_items


class DeduplicateItemsTests(unittest.TestCase):
    def test_removes_tracking_url_and_title_duplicates(self) -> None:
        items = [
            {"title": "OpenAI launches a model", "url": "https://example.com/news?id=1&utm_source=x"},
            {"title": "Same URL, different title", "url": "https://example.com/news?id=1"},
            {"title": "OpenAI launches a model!", "url": "https://other.example/story"},
            {"title": "Distinct item", "url": "https://example.com/other"},
        ]

        result = deduplicate_items(items, strategy="url_or_title")

        self.assertEqual(result["input_count"], 4)
        self.assertEqual(result["item_count"], 2)
        self.assertEqual(result["removed_count"], 2)
        self.assertEqual(
            [item["title"] for item in result["items"]],
            ["OpenAI launches a model", "Distinct item"],
        )

    def test_rejects_unknown_strategy(self) -> None:
        with self.assertRaises(ValueError):
            deduplicate_items([], strategy="unknown")


if __name__ == "__main__":
    unittest.main()
