"""Test."""
import io
import tempfile
import unittest

from utils.xmlx import _, render_link_styles, style

TEST_BODY = _(
    'body',
    [
        _('h1', 'This is header 1', style(font_family='Georgia')),
        _('p', 'This is a paragraph'),
        _(
            'div',
            [
                _('span', 'This is a span in a div'),
                _(
                    'a',
                    'This is a a(link) in a div',
                    dict(href='https://pypi.org/project/utils-nuuuwan'),
                ),
            ],
        ),
    ],
)


class TestXMLX(unittest.TestCase):
    """Test."""

    def test_render_link_styles(self):
        """Test."""
        expected = '''<?xml version="1.0" ?>
<link rel="stylesheet" href="styles.css"/>
'''
        actual = str(render_link_styles())
        self.assertEqual(expected, actual)

    def test_repr(self):
        """Test."""
        expected = '<?xml version="1.0" ?>\n<p>This is a paragraph</p>\n'

        actual = repr(_('p', 'This is a paragraph'))
        self.assertEqual(expected, actual)

    def test_log_metric(self):
        """Test."""
        head = _('head')
        body = TEST_BODY
        html = _('html', [head, body])
        actual_file = tempfile.NamedTemporaryFile(
            prefix="utils.tests.test_xmlx.", suffix=".html"
        ).name
        html.store(actual_file)

        expected_file = 'tests/test_xmlx_example1.html'
        self.assertListEqual(
            list(io.open(actual_file)),
            list(io.open(expected_file)),
        )
