import unittest

from generate_hugo_data import library_paper_record


class PublicationAuthorDisplayTests(unittest.TestCase):
    def paper(self, display_authors, all_authors):
        return library_paper_record(
            {
                "Title": "Test Paper",
                "Sort Date": "Aug 13, 2026",
                "Display Authors": display_authors,
                "all authors": all_authors,
            }
        )

    def test_display_authors_are_preserved(self):
        cases = [
            ("Chang, Arnett, and 378 others", "Tyler A. Chang; Catherine Arnett"),
            ("Zhang and Goldstein", "Ruichong Zhang; Daniel Goldstein"),
            (
                "Son, Kim, Arnett, Ko, Lee, Kang, Jiang, Yun, Lee, and 67 others",
                "Guijin Son; Seungone Kim; Catherine Arnett; Hyunwoo Ko",
            ),
            (
                "O'Mahony, Grinsztajn, Schoelkopf, and Biderman",
                "Laura O'Mahony; Stella Biderman",
            ),
            ("Laurençon, Névéol, Ilić, and Suárez", "Hugo Laurençon; Aurélie Névéol"),
            ("Komatsuzaki", "Aran Komatsuzaki"),
        ]

        for display_authors, all_authors in cases:
            with self.subTest(display_authors=display_authors):
                paper = self.paper(display_authors, all_authors)
                self.assertEqual(paper["authors"], display_authors)
                self.assertTrue(
                    all(author in paper["author_search"] for author in all_authors.split("; "))
                )

    def test_only_outer_whitespace_is_removed(self):
        paper = self.paper(
            "  Paulo, Marshall and Belrose  ",
            "Gonçalo Paulo; Jack Marshall; Nora Belrose",
        )

        self.assertEqual(paper["authors"], "Paulo, Marshall and Belrose")


if __name__ == "__main__":
    unittest.main()
