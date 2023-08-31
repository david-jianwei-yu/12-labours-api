class FilterFormat(object):
    def __init__(self, fg):
        self.FG = fg
        self.FILTERS = fg.get_filters()

    def generate_sidebar_filter_information(self):
        sidebar_filter_information = []
        for mapped_element in self.FILTERS:
            filter_dict = self.FG.set_filter(mapped_element)
            filter_parent = {
                "key": "",
                "label": "",
                "children": [],
            }
            filter_parent["key"] = filter_dict[mapped_element]["node"] + \
                ">" + filter_dict[mapped_element]["field"]
            filter_parent["label"] = filter_dict[mapped_element]["title"].capitalize()
            for facet_name in filter_dict[mapped_element]["facets"]:
                filter_children = {
                    "facetPropPath": "",
                    "label": "",
                }
                filter_children["facetPropPath"] = filter_parent["key"]
                filter_children["label"] = facet_name
                filter_parent["children"].append(filter_children)
            sidebar_filter_information.append(filter_parent)
        return sidebar_filter_information

    def generate_filter_information(self):
        filter_information = {
            "size": len(self.FILTERS),
            "titles": [],
            "nodes>fields": [],
            "elements": []
        }
        for mapped_element in self.FILTERS:
            filter_dict = self.FG.set_filter(mapped_element)
            filter_information["titles"].append(
                filter_dict[mapped_element]["title"].capitalize())
            filter_information["nodes>fields"].append(
                filter_dict[mapped_element]["node"] + ">" + filter_dict[mapped_element]["field"])
            filter_information["elements"].append(
                list(filter_dict[mapped_element]["facets"].keys()))
        return filter_information
