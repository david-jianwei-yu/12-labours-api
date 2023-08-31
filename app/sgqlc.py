import re

from fastapi import HTTPException, status
from sgqlc.operation import Operation

from app.sgqlc_schema import Query


class SimpleGraphQLClient(object):
    def __init__(self, submission):
        self.SUBMISSION = submission

    def handle_node_suffix(self, node, snake_case_query):
        gen3_node = ""
        if "experiment" in node:
            gen3_node = "experiment"
        elif "dataset_description" in node:
            gen3_node = "dataset_description"
        elif "manifest" in node:
            gen3_node = "manifest"
        elif "case" in node:
            gen3_node = "case"
        valid_query = re.sub(node, gen3_node, snake_case_query)
        valid_node = re.sub(node, gen3_node, node)
        return valid_query, valid_node

    def handle_classification(self, item, snake_case_query):
        access_scope = re.sub('\'', '\"', f"{item.access}")
        data = {
            # Choose the number of data to display, 0 here means display everything
            'manifests1': ['scaffolds', 'additional_types', '["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"]'],
            'manifests2': ['scaffoldViews', 'additional_types', '["application/x.vnd.abi.scaffold.view+json"]'],
            'manifests3': ['plots', 'additional_types', '["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+Tab-separated-values", "text/vnd.abi.plot+csv"]'],
            'manifests4': ['thumbnails', 'file_type', '[".jpg", ".png"]'],
            'manifests5': ['mris', 'file_type', '[".nrrd"]'],
            'manifests6': ['dicomImages', 'file_type', '[".dcm"]']
        }

        for key in data:
            snake_case_query = re.sub(
                key,
                f'{data[key][0]}: manifests(first:0, offset:0, {data[key][1]}: {data[key][2]}, project_id: {access_scope}, order_by_asc:"submitter_id")',
                snake_case_query
            )
        return snake_case_query

    def handle_null_argument(self, snake_case_query):
        if "null" in snake_case_query:
            snake_case_query = re.sub(
                '[,]? [_a-z]+: null',
                '',
                snake_case_query
            )
        return snake_case_query

    def handle_snake_case(self, query):
        snake_case_query = re.sub(
            '_[A-Z]',
            lambda x:  x.group(0).lower(),
            re.sub(
                '([a-z])([A-Z])',
                r'\1_\2',
                str(query)
            )
        )
        return snake_case_query

    def convert_query(self, item, query):
        # Convert camel case to snake case
        snake_case_query = self.handle_snake_case(query)
        # Remove all null filter arguments, this can simplify the generate_query function
        snake_case_query = self.handle_null_argument(snake_case_query)
        # Either pagination or experiment node query
        if "experiment" in item.node and "count" not in item.node:
            snake_case_query = self.handle_classification(
                item, snake_case_query)
        snake_case_query, item.node = self.handle_node_suffix(
            item.node, snake_case_query)
        return "{" + snake_case_query + "}"

    # generated query will fetch all the fields that Gen3 metadata has
    def generate_query(self, item):
        query = Operation(Query)
        # FILTER
        # if the node name contains "_filter",
        # the query generator will be used for /filter/ and /graphql/pagination API
        if item.node == "experiment_filter":
            return self.convert_query(
                item,
                query.experimentFilter(
                    first=0,
                    offset=0,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                )
            )
        elif item.node == "dataset_description_filter":
            return self.convert_query(
                item,
                query.datasetDescriptionFilter(
                    first=0,
                    offset=0,
                    # study_organ_system=item.filter.get("study_organ_system", None),
                    project_id=item.access,
                )
            )
        elif item.node == "manifest_filter":
            return self.convert_query(
                item,
                query.manifestFilter(
                    first=0,
                    offset=0,
                    additional_types=item.filter.get("additional_types", None),
                    project_id=item.access,
                )
            )
        elif item.node == "case_filter":
            return self.convert_query(
                item,
                query.caseFilter(
                    first=0,
                    offset=0,
                    species=item.filter.get("species", None),
                    sex=item.filter.get("sex", None),
                    age_category=item.filter.get("age_category", None),
                    project_id=item.access,
                )
            )
        # QUERY
        # if the node name contains "_query",
        # the query generator will only be used for /graphql/query API
        elif item.node == "experiment_query":
            if type(item.search) == str and item.search != "":
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="Search function does not support while querying in experiment node")
            return self.convert_query(
                item,
                query.experimentQuery(
                    first=0,
                    offset=0,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                )
            )
        elif item.node == "dataset_description_query":
            return self.convert_query(
                item,
                query.datasetDescriptionQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                    project_id=item.access,
                )
            )
        elif item.node == "manifest_query":
            return self.convert_query(
                item,
                query.manifestQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                    project_id=item.access,
                )
            )
        elif item.node == "case_query":
            return self.convert_query(
                item,
                query.caseQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                    project_id=item.access,
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
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                    order_by_asc=item.asc,
                    order_by_desc=item.desc,
                )
            )
        elif item.node == "experiment_pagination_count":
            return self.convert_query(
                item,
                query.experimentPaginationCount(
                    first=0,
                    offset=0,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                )
            )
        # SUPPORT FOR PAGINATION ORDER
        elif item.node == "pagination_order_by_dataset_description":
            return self.convert_query(
                item,
                query.paginationOrderByDatasetDescription(
                    first=item.limit,
                    offset=(item.page-1)*item.limit,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                    order_by_asc=item.asc,
                    order_by_desc=item.desc,
                )
            )
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="GraphQL query cannot be generated by sgqlc")

    def get_queried_result(self, item, key=None, queue=None):
        if item.node == None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Missing one or more fields in the request body")

        query = self.generate_query(item)
        try:
            result = self.SUBMISSION.query(query)["data"][item.node]
            if key != None and queue != None:
                queue.put({key: result})
            return result
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=str(e))
