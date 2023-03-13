import re

from app.data_schema import GraphQLQueryItem
from app.sgqlc import SimpleGraphQLClient
from app.filter import Filter, FIELDS
from app.search import Search

sgqlc = SimpleGraphQLClient()
f = Filter()
s = Search()


class Pagination:
    def update_pagination_item(self, item, input, SUBMISSION, SESSION):
        if item.filter != {}:
            query_item = GraphQLQueryItem()
            filter_dict = {"submitter_id": []}
            temp_node_dict = {}
            for element in item.filter.values():
                query_item.node, query_item.filter = element["node"], element["filter"]
                filter_node = re.sub('_filter', '', query_item.node)
                filter_field = list(query_item.filter.keys())[0]
                # Only do fetch when there is no related temp data stored in temp_node_dict
                # or the node field type is "String"
                if filter_node not in temp_node_dict.keys() or filter_field not in FIELDS:
                    query_result = sgqlc.get_queried_result(
                        query_item, SUBMISSION)
                    # The data will be stored when the field type is an "Array"
                    # The default filter relation of the Gen3 "Array" type field is "AND"
                    # We need "OR", therefore entire node data will go through a self-written filter function
                    if filter_field in FIELDS:
                        temp_node_dict[filter_node] = query_result[filter_node]
                elif filter_node in temp_node_dict.keys() and filter_field in FIELDS:
                    query_result = temp_node_dict
                filter_dict["submitter_id"].append(f.get_filtered_datasets(
                    query_item.filter, query_result[filter_node]))
            item.filter = filter_dict
            f.filter_relation(item)

        if input != "":
            # If input does not match any content in the database, item.search will be empty dictionary
            item.search["submitter_id"] = s.get_searched_datasets(
                input, SESSION)
            if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
                s.search_filter_relation(item)

    def update_pagination_output(self, result):
        items = []
        for ele in result:
            item = {
                # "cases": ele["cases"],
                "contributors": ele["dataset_descriptions"][0]["contributor_name"],
                "keywords": ele["dataset_descriptions"][0]["keywords"],
                "numberSamples": int(ele["dataset_descriptions"][0]["number_of_samples"][0]),
                "numberSubjects": int(ele["dataset_descriptions"][0]["number_of_subjects"][0]),
                "name": ele["dataset_descriptions"][0]["title"][0],
                "datasetId": ele["submitter_id"],
                "organs": ele["dataset_descriptions"][0]["study_organ_system"],
                "species": [],
                "plots": ele["plots"],
                "scaffoldViews": ele["scaffoldViews"],
                "scaffolds": ele["scaffolds"],
                "thumbnails": ele["thumbnails"],
            }
            items.append(item)
        return items
