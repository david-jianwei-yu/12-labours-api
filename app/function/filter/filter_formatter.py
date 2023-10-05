"""
Functionality for generating different types of filter format
- generate_sidebar_filter_format
- generate_filter_format
"""


class FilterFormatter:
    """
    fg -> filter editor object is required
    """

    def __init__(self, fe):
        self.__filter_cache = fe.cache_loader()

    def _handle_element_content(self, mapped_element, private_filter):
        """
        Handler for switching element content between public and private
        """
        if mapped_element in private_filter:
            return private_filter[mapped_element]
        return self.__filter_cache[mapped_element]

    def generate_sidebar_filter_format(self, private_filter):
        """
        Format for portal map integrated viewer sidebar
        """
        sidebar_format = []
        for mapped_element in self.__filter_cache:
            content = self._handle_element_content(mapped_element, private_filter)
            parent_format = {
                "key": "",
                "label": "",
                "children": [],
            }
            parent_format["key"] = f"{content['node']}>{content['field']}"
            parent_format["label"] = content["title"].capitalize()
            for facet_name in content["facets"]:
                children_format = {
                    "facetPropPath": "",
                    "label": "",
                }
                children_format["facetPropPath"] = parent_format["key"]
                children_format["label"] = facet_name
                parent_format["children"].append(children_format)
            sidebar_format.append(parent_format)
        return sidebar_format

    def generate_filter_format(self, private_filter):
        """
        Format for portal data browser
        """
        format_ = {
            "size": len(self.__filter_cache),
            "titles": [],
            "nodes>fields": [],
            "elements": [],
        }
        for mapped_element in self.__filter_cache:
            content = self._handle_element_content(mapped_element, private_filter)
            format_["titles"].append(content["title"].capitalize())
            format_["nodes>fields"].append(f"{content['node']}>{content['field']}")
            format_["elements"].append(list(content["facets"].keys()))
        return format_
