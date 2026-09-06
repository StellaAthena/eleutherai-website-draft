import unittest

import generate_hugo_data as generator


def paper(title, date, marker="TRUE", url=None, venue=""):
    return {
        "Title": title,
        "Sort Date": date,
        "Highest Impact": marker,
        "Link": url or f"https://example.com/papers/{title.lower()}",
        "Conference or Journal": venue,
        "Workshop": "",
        "Status": "Accepted" if venue else "Preprint",
    }


def blog(title, date):
    return {
        "title": title,
        "date": date,
        "url": f"https://blog.example.com/{title.lower()}/",
    }


class HighestImpactMarkerTests(unittest.TestCase):
    def test_marker_parsing_matches_sheet_checkbox_values(self):
        self.assertTrue(generator.parse_highest_impact_marker(" TRUE "))
        self.assertTrue(generator.parse_highest_impact_marker("true"))
        self.assertFalse(generator.parse_highest_impact_marker(""))
        self.assertFalse(generator.parse_highest_impact_marker("FALSE"))
        with self.assertRaises(ValueError):
            generator.parse_highest_impact_marker("yes")

    def test_highest_impact_header_normalizes_only_its_spacing_and_case(self):
        headers = list(generator.REQUIRED_PAPER_HEADERS) + ["  highest   IMPACT "]
        self.assertEqual(generator.highest_impact_header(headers), "  highest   IMPACT ")
        self.assertFalse(generator.REQUIRED_PAPER_HEADERS.issubset(set(headers) - {"Title"}))

    def test_paper_identity_tolerates_sheet_position_prefix_drift(self):
        title = "Don't Just Fix it in Post: A Science of AI Must Study Learning Dynamics"
        self.assertEqual(generator.paper_identity_title(f"Position: {title}"), title)


class RecentOutputsTests(unittest.TestCase):
    def test_blog_posts_are_excluded_and_papers_sort_by_exact_date(self):
        outputs = generator.recent_outputs(
            [paper("Paper A", "Jan 3, 2026"), paper("Paper B", "Jan 1, 2026")],
            [blog("Blog A", "2026-01-02T23:30:00-00:00")],
            limit=10,
        )
        self.assertEqual([item["title"] for item in outputs], ["Paper A", "Paper B"])

    def test_marked_papers_appear_once(self):
        marked = paper("Marked", "Jan 2, 2026")
        outputs = generator.recent_outputs(
            [marked, dict(marked), paper("Unmarked", "Jan 3, 2026", marker="")],
            [blog("Blog", "2026-01-01")],
            limit=10,
        )
        self.assertEqual([(item["kind"], item["title"]) for item in outputs], [("Paper", "Marked")])

    def test_limit_keeps_only_four_newest_without_kind_quotas(self):
        papers = [paper(f"Paper {day}", f"Jan {day}, 2026") for day in range(1, 6)]
        outputs = generator.recent_outputs(papers, [blog("Older Blog", "2025-12-31")])
        self.assertEqual(len(outputs), 4)
        self.assertEqual([item["title"] for item in outputs], ["Paper 5", "Paper 4", "Paper 3", "Paper 2"])


if __name__ == "__main__":
    unittest.main()
