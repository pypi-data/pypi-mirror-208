import unittest

from sphinx_api_sidebar.sphinx_api_sidebar import update_html_context


class TestSphinxApiSidebar(unittest.TestCase):
    def test_update_html_context(self):
        config = type("", (), {})()  # Create a simple object to act as the config
        config.html_context = {}

        api_docs = ["project1", "project2"]

        update_html_context(config, api_docs)

        self.assertIn("api_docs", config.html_context)
        self.assertEqual(api_docs, config.html_context["api_docs"])


if __name__ == "__main__":
    unittest.main()
