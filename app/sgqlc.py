import re

from fastapi import HTTPException

from app.data_schema import *
from sgqlc.operation import Operation
from app.sgqlc_schema import Query


class SimpleGraphQLClient:
    def add_count_field(self, item, query):
        # Add default count field to query
        count_field = f"total: _{item.node}_count"
        if item.filter != {}:
            # Manually modify and add count filed into graphql query
            filter_argument = re.sub(
                '\'([_a-z]+)\'', r'\1', re.sub(r'\{([^{].*[^}])\}', r'\1', f'{item.filter}'))
            count_field = re.sub(
                '\'', '\"', f'total: _{item.node}_count({filter_argument})')
        return query + count_field

    def update_manifests_information(self, query):
        query = re.sub(
            'manifests1', 'scaffolds: manifests(additional_types: ["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"])', query)
        query = re.sub(
            'manifests2', 'scaffoldViews: manifests(additional_types: ["application/x.vnd.abi.scaffold.view+json"])', query)
        query = re.sub(
            'manifests3', 'plots: manifests(additional_types: ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+Tab-separated-values", "text/vnd.abi.plot+csv"])', query)
        query = re.sub(
            'manifests4', 'thumbnails: manifests(file_type: [".jpg", ".png"])', query)
        return query

    def convert_query(self, item, query):
        # Convert camel case to snake case
        snake_case_query = re.sub(
            '_[A-Z]', lambda x:  x.group(0).lower(), re.sub('([a-z])([A-Z])', r'\1_\2', str(query)))
        # Remove all null filter arguments, this can simplify the generate_query function
        if "null" in snake_case_query:
            snake_case_query = re.sub(
                '[,]? [_a-z]+: null', '', snake_case_query)
        # Update the filter query node name
        if "filter" in item.node:  # query situation
            snake_case_query = re.sub('_filter', '', snake_case_query)
            item.node = re.sub('_filter', '', item.node)
        if type(item.search) == dict:  # pagination situation
            snake_case_query = self.update_manifests_information(
                snake_case_query)
            # Only pagination will need to add count field
            snake_case_query = self.add_count_field(item, snake_case_query)
        return "{" + snake_case_query + "}"

    # if the node name contains "_filter",
    # the query generator will only be used for /graphql/pagination API
    # else is for /graphql/query API,
    # this will fetch all the fields that Gen3 metadata has
    def generate_query(self, item):
        query = Operation(Query)
        if item.node == "experiment":
            return self.convert_query(
                item,
                query.experiment(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    submitter_id=item.filter["submitter_id"] if "submitter_id" in item.filter else None
                )
            )
        elif item.node == "dataset_description":
            return self.convert_query(
                item,
                query.datasetDescription(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    submitter_id=item.filter["submitter_id"] if "submitter_id" in item.filter else None
                )
            )
        elif item.node == "dataset_description_filter":
            return self.convert_query(
                item,
                query.datasetDescriptionFilter(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                )
            )
        elif item.node == "manifest":
            return self.convert_query(
                item,
                query.manifest(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    quick_search=item.search,
                    additional_types=item.filter["additional_types"] if "additional_types" in item.filter else None,
                    file_type=item.filter["file_type"] if "file_type" in item.filter else None
                )
            )
        elif item.node == "manifest_filter":
            return self.convert_query(
                item,
                query.manifestFilter(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    additional_types=item.filter["additional_types"] if "additional_types" in item.filter else None
                )
            )
        elif item.node == "case":
            return self.convert_query(
                item,
                query.case(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    quick_search=item.search,
                )
            )
        elif item.node == "case_filter":
            return self.convert_query(
                item,
                query.caseFilter(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    species=item.filter["species"] if "species" in item.filter else None,
                    sex=item.filter["sex"] if "sex" in item.filter else None,
                    age_category=item.filter["age_category"] if "age_category" in item.filter else None
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
            query_result = SUBMISSION.query(query)["data"]
        except Exception as e:
            raise HTTPException(status_code=NOT_FOUND, detail=str(e))

        if query_result[item.node] != []:
            return query_result
        else:
            raise HTTPException(status_code=NOT_FOUND,
                                detail="Data cannot be found in the node")
