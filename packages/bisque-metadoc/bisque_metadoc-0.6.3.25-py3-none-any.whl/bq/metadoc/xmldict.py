# Create python xml structures compatible with
# http://search.cpan.org/~grantm/XML-Simple-2.18/lib/XML/Simple.pm

from collections import OrderedDict
from itertools import groupby

from lxml import etree


def xml2d(e, attribute_prefix=None, group_lists=False, keep_tags=False):
    """Convert an etree into a dict structure"""

    def _get_tag(el):
        if el.tag == "tag" and not keep_tags:
            return el.get("name", "tag")
        else:
            return el.tag

    def _xml2d(e):
        # map attributes
        if attribute_prefix is not None:
            kids = {
                f"{attribute_prefix}{k}": v
                for k, v in e.attrib.items()
                if e.tag != "tag" or k != "name" or keep_tags
            }
        else:
            kids = {
                k: v
                for k, v in e.attrib.items()
                if e.tag != "tag" or k != "name" or keep_tags
            }
        # map text
        if kids.get("%svalue" % attribute_prefix) is not None:
            node_val = kids["%svalue" % attribute_prefix]
            del kids["%svalue" % attribute_prefix]
        else:
            node_val = e.text
        if node_val is not None:
            if len(e) == 0 and len(kids) == 0:
                kids = node_val
                return kids
            else:
                kids["%svalue" % attribute_prefix] = node_val
        # map children
        for k, g in groupby(
            sorted(e, key=lambda x: _get_tag(x)), key=lambda x: _get_tag(x)
        ):
            g = [_xml2d(x) for x in g]
            if group_lists:
                g = ",".join(g)
            kids[k] = g if len(g) > 1 else g[0]
        return kids

    return {_get_tag(e): _xml2d(e)}


def d2xml(d: dict, attribute_prefix=None, keep_value_attr: bool = False):
    """convert dict to etree"""
    if not isinstance(d, dict):
        raise ValueError(f" Expected dict, got {type(d)}")

    def _setval(node, val):
        val = str(val)  # TODO: need to come up with better solution for numbers etc
        if (
            keep_value_attr or val.strip() != val
        ):  # keep vals with leading/trailing spaces in value attr for subsequent naturalxml_to_tree
            node.set("value", val)
        else:
            node.text = val

    def _d2xml(d, p):
        for k, v in d.items():
            if isinstance(v, dict):
                try:
                    node = etree.SubElement(p, k)
                except ValueError:
                    # illegal xml tag
                    node = etree.SubElement(p, "tag", name=k)
                _d2xml(v, node)
            elif isinstance(v, list):
                for item in v:
                    try:
                        node = etree.SubElement(p, k)
                    except ValueError:
                        # illegal xml tag
                        node = etree.SubElement(p, "tag", name=k)
                    if isinstance(item, dict):
                        _d2xml(item, node)
                    else:
                        _setval(node, item)
            else:
                if k == "%svalue" % attribute_prefix:
                    _setval(p, v)
                else:
                    if k.startswith(attribute_prefix):
                        p.set(k.lstrip(attribute_prefix), v)
                    else:
                        try:
                            node = etree.SubElement(p, k)
                        except ValueError:
                            # illegal xml tag
                            node = etree.SubElement(p, "tag", name=k)
                        _setval(node, v)
                # p.set(k, v)

    k, v = list(d.items())[0]
    try:
        node = etree.Element(k)
    except ValueError:
        # illegal xml tag
        node = etree.Element("tag", name=k)
    if isinstance(v, dict):
        _d2xml(v, node)
    else:
        _setval(node, v)
    return node


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value

    return OrderedDict(items())


if __name__ == "__main__":

    X = """<T uri="boo"><a n="1"/><a n="2"/><b n="3"><c x="y"/></b></T>"""
    print(X)
    Y = xml2d(etree.XML(X))
    print(Y)
    Z = etree.tostring(d2xml(Y), encoding="unicode")
    print(Z)
    assert X == Z
