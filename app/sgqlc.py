import re

from fastapi import HTTPException
from sgqlc.operation import Operation

from app.data_schema import *
from app.sgqlc_schema import Query


class SimpleGraphQLClient:
    def add_count_field(self, item, query):
        # Add default count field to query
        count_field = f"total: _{item.node}_count"
        if item.filter != {}:
            # Manually modify and add count field into graphql query
            filter_argument = re.sub(
                '\'([_a-z]+)\'', r'\1', re.sub(r'\{([^{].*[^}])\}', r'\1', f'{item.filter}'))
            count_field = re.sub(
                '\'', '\"', f'total: _{item.node}_count({filter_argument})')
        return query + count_field

    def update_manifests_information(self, query):
        data = {
            'manifests1': ['scaffolds', 'additional_types', '["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"]'],
            'manifests2': ['scaffoldViews', 'additional_types', '["application/x.vnd.abi.scaffold.view+json"]'],
            'manifests3': ['plots', 'additional_types', '["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+Tab-separated-values", "text/vnd.abi.plot+csv"]'],
            'manifests4': ['thumbnails', 'file_type', '[".jpg", ".png"]']
        }
        for key in data.keys():
            query = re.sub(
                key, f'{data[key][0]}: manifests({data[key][1]}: {data[key][2]})', query)
        return query

    def remove_node_suffix(self, node, query):
        suffix = ""
        if "filter" in node:
            suffix = "_filter"
        elif "query" in node:
            suffix = "_query"
        elif "pagination" in node:
            suffix = "_pagination"
        query = re.sub(suffix, '', query)
        node = re.sub(suffix, '', node)
        return query, node

    def convert_query(self, item, query):
        # Convert camel case to snake case
        snake_case_query = re.sub(
            '_[A-Z]', lambda x:  x.group(0).lower(), re.sub('([a-z])([A-Z])', r'\1_\2', str(query)))
        # Remove all null filter arguments, this can simplify the generate_query function
        if "null" in snake_case_query:
            snake_case_query = re.sub(
                '[,]? [_a-z]+: null', '', snake_case_query)
        # Either pagination or experiment node query
        if "experiment" in item.node:
            snake_case_query = self.update_manifests_information(
                snake_case_query)
            # Only pagination will need count field
            if type(item.search) == dict:
                snake_case_query = self.add_count_field(item, snake_case_query)
        snake_case_query, item.node = self.remove_node_suffix(
            item.node, snake_case_query)
        return "{" + snake_case_query + "}"

    # generated query will fetch all the fields that Gen3 metadata has
    def generate_query(self, item):
        query = Operation(Query)
        # FILTER
        # if the node name contains "_filter",
        # the query generator will be used for /filter/ and /graphql/pagination API
        if item.node == "dataset_description_filter":
            return self.convert_query(
                item,
                query.datasetDescriptionFilter(
                    first=0,
                    offset=0,
                    # study_organ_system=item.filter["study_organ_system"] if "study_organ_system" in item.filter else None
                )
            )
        elif item.node == "manifest_filter":
            return self.convert_query(
                item,
                query.manifestFilter(
                    first=0,
                    offset=0,
                    additional_types=item.filter["additional_types"] if "additional_types" in item.filter else None
                )
            )
        elif item.node == "case_filter":
            return self.convert_query(
                item,
                query.caseFilter(
                    first=0,
                    offset=0,
                    species=item.filter["species"] if "species" in item.filter else None,
                    sex=item.filter["sex"] if "sex" in item.filter else None,
                    age_category=item.filter["age_category"] if "age_category" in item.filter else None
                )
            )
        # QUERY
        # if the node name contains "_query",
        # the query generator will only be used for /graphql/query API
        elif item.node == "experiment_query":
            if type(item.search) == str and item.search != "":
                raise HTTPException(status_code=METHOD_NOT_ALLOWED,
                                    detail="Search function does not support while querying in experiment node")
            return self.convert_query(
                item,
                query.experimentQuery(
                    first=0,
                    offset=0,
                    submitter_id=item.filter["submitter_id"] if "submitter_id" in item.filter else None
                )
            )
        elif item.node == "dataset_description_query":
            return self.convert_query(
                item,
                query.datasetDescriptionQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                )
            )
        elif item.node == "manifest_query":
            return self.convert_query(
                item,
                query.manifestQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                )
            )
        elif item.node == "case_query":
            return self.convert_query(
                item,
                query.caseQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                )
            )
        # PAGINATION
        # if the node name contains "_pagination",
        # the query generator will only be used for /graphql/pagination API
        elif item.node == "experiment_pagination":
            return self.convert_query(
                item,
                query.experimentPagination(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    submitter_id=item.filter["submitter_id"] if "submitter_id" in item.filter else None
                )
            )
        else:
            raise HTTPException(status_code=NOT_FOUND,
                                detail="GraphQL query cannot be generated by sgqlc")

    def get_queried_result(self, item, SUBMISSION):
        if item.node == None:
            raise HTTPException(status_code=BAD_REQUEST,
                                detail="Missing one or more fields in the request body")

        query = self.generate_query(item)
        try:
            return SUBMISSION.query(query)["data"]
        except Exception as e:
            raise HTTPException(status_code=NOT_FOUND, detail=str(e))
