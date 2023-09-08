class FilterFormat(object):
    def __init__(self, fg):
        self.FG = fg
        self.MAPPED_FILTERS = fg.get_mapped_filter()

    def generate_sidebar_filter_information(self, access_scope):
        sidebar_filter_information = []
        for mapped_element in self.MAPPED_FILTERS:
            used_filter = self.FG.set_filter(mapped_element, access_scope)
            filter_parent = {
                "key": "",
                "label": "",
                "children": [],
            }
            filter_parent["key"] = (
                used_filter[mapped_element]["node"]
                + ">"
                + used_filter[mapped_element]["field"]
            )
            filter_parent["label"] = used_filter[mapped_element]["title"].capitalize()
            for facet_name in used_filter[mapped_element]["facets"]:
                filter_children = {
                    "facetPropPath": "",
                    "label": "",
                }
                filter_children["facetPropPath"] = filter_parent["key"]
                filter_children["label"] = facet_name
                filter_parent["children"].append(filter_children)
            sidebar_filter_information.append(filter_parent)
        return sidebar_filter_information

    def generate_filter_information(self, access_scope):
        filter_information = {
            "size": len(self.MAPPED_FILTERS),
            "titles": [],
            "nodes>fields": [],
            "elements": [],
        }
        for mapped_element in self.MAPPED_FILTERS:
            used_filter = self.FG.set_filter(mapped_element, access_scope)
            filter_information["titles"].append(
                used_filter[mapped_element]["title"].capitalize()
            )
            filter_information["nodes>fields"].append(
                used_filter[mapped_element]["node"]
                + ">"
                + used_filter[mapped_element]["field"]
            )
            filter_information["elements"].append(
                list(used_filter[mapped_element]["facets"].keys())
            )
        return filter_information
