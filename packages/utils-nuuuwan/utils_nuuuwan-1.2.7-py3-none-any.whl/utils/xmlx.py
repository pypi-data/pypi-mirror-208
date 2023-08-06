import xml.dom.minidom as minidom
import xml.etree.ElementTree as ElementTree

from utils import String
from utils.file.File import File

FONT_FAMILY = 'sans-serif'
DEFAULT_ATTRIB_MAP = {
    'html': {
        'style': 'font-family: %s;' % FONT_FAMILY,
    },
    'svg': {
        'xmlns': 'http://www.w3.org/2000/svg',
    },
}


def render_link_styles(css_file='styles.css'):
    return _('link', None, {'rel': 'stylesheet', 'href': css_file})


def style(**kwargs):
    style_content = ''.join(
        list(
            map(
                lambda item: '%s:%s;'
                % (String(str(item[0])).kebab, str(item[1])),
                kwargs.items(),
            )
        )
    )
    return dict(style=style_content)


class _:
    def __init__(
        self,
        tag: str,
        child_list_or_str_or_other: list or str or None = None,
        attrib_custom: dict or None = {},
    ):
        self.tag = tag
        self.child_list_or_str_or_other = child_list_or_str_or_other
        self.attrib_custom = attrib_custom

    @property
    def expanded_attrib(self):
        expanded_attrib = DEFAULT_ATTRIB_MAP.get(self.tag, {})
        expanded_attrib.update(self.attrib_custom)
        expanded_attrib = dict(
            zip(
                list(
                    map(lambda k: k.replace('_', '-'), expanded_attrib.keys())
                ),
                list(map(str, expanded_attrib.values())),
            ),
        )
        return expanded_attrib

    @property
    def tag_real(self):
        return self.tag.split('-')[0]

    @property
    def child_element_list(self):
        if not isinstance(self.child_list_or_str_or_other, list):
            return []
        nonnull_child_list = list(
            filter(
                lambda child_or_none: child_or_none is not None,
                self.child_list_or_str_or_other,
            )
        )
        return list(
            map(
                lambda child: child.element,
                nonnull_child_list,
            )
        )

    @property
    def text(self):
        if isinstance(self.child_list_or_str_or_other, str):
            return self.child_list_or_str_or_other
        return ''

    @property
    def element(self):
        element = ElementTree.Element(self.tag_real)
        element.attrib = self.expanded_attrib
        for child_element in self.child_element_list:
            element.append(child_element)
        element.text = self.text
        return element

    def __str__(self):
        s = ElementTree.tostring(self.element, encoding='utf-8').decode()
        parsed_s = minidom.parseString(s)
        return parsed_s.toprettyxml(indent='  ')

    def __repr__(self):
        return self.__str__()

    def store(self, xml_file):
        File(xml_file).write(str(self))
