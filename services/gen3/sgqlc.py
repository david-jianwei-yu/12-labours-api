"""
Functionality for generating query code and fetching data
- handle_graphql_query_code
"""
import re

from sgqlc.operation import Operation

from services.gen3.sgqlc_schema import Query


class SimpleGraphQLClient:
    """
    Generate graphql query code functionality
    """

    def _handle_suffix(self, node, snake_case):
        """
        Handler for removing node suffix
        """
        node_type = ""
        if "experiment" in node:
            node_type = "experiment"
        elif "dataset_description" in node:
            node_type = "dataset_description"
        elif "manifest" in node:
            node_type = "manifest"
        elif "case" in node:
            node_type = "case"
        updated_query = re.sub(node, node_type, snake_case)
        updated_node = re.sub(node, node_type, node)
        return updated_query, updated_node

    def _handle_classification(self, item, snake_case):
        """
        Handler for processing manifest classification
        """
        access_scope = re.sub("'", '"', f"{item.access}")
        data = {
            # Choose the number of data to display, 0 here means display everything
            "manifests1": [
                "scaffolds",
                "additional_types",
                '["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"]',
            ],
            "manifests2": [
                "scaffoldViews",
                "additional_types",
                '["application/x.vnd.abi.scaffold.view+json"]',
            ],
            "manifests3": [
                "plots",
                "additional_types",
                '["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"]',
            ],
            "manifests4": ["thumbnails", "file_type", '[".jpg", ".png"]'],
            "manifests5": ["mris", "file_type", '[".nrrd"]'],
            "manifests6": ["dicomImages", "file_type", '[".dcm"]'],
        }
        for key, value in data.items():
            snake_case = re.sub(
                key,
                f"{value[0]}: manifests(first:0,"
                + "offset:0,"
                + f"{value[1]}: {value[2]},"
                + f"project_id: {access_scope},"
                + 'order_by_asc:"submitter_id")',
                snake_case,
            )
        return snake_case

    def _handle_null_argument(self, snake_case):
        """
        Handler for removing null from snake case
        """
        if "null" in snake_case:
            snake_case = re.sub("[,]? [_a-z]+: null", "", snake_case)
        return snake_case

    def _handle_snake_case(self, query_code):
        """
        Handler for converting query code from camel case to snake case
        """
        snake_case = re.sub(
            "_[A-Z]",
            lambda x: x.group(0).lower(),
            re.sub("([a-z])([A-Z])", r"\1_\2", str(query_code)),
        )
        return snake_case

    def _handle_query_code_format(self, item, query_code):
        """
        Handler for converting query code
        """
        # Convert camel case to snake case
        snake_case = self._handle_snake_case(query_code)
        # Remove all null filter arguments, simplify the _handle_graphql_query_code function
        snake_case = self._handle_null_argument(snake_case)
        # Either pagination or experiment node query
        if "experiment" in item.node and "count" not in item.node:
            snake_case = self._handle_classification(item, snake_case)
        snake_case, item.node = self._handle_suffix(item.node, snake_case)
        return "{" + snake_case + "}"

    # generated query will fetch all the fields that Gen3 metadata has
    def handle_graphql_query_code(self, item):
        """
        Handler for creating graphql query code
        """
        query = Operation(Query)
        # FILTER
        # if the node name contains "_filter",
        # the query generator will be used for /filter/ and /graphql/pagination API
        if item.node == "experiment_filter":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.experimentFilter(
                    first=0,
                    offset=0,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                ),
            )
        elif item.node == "dataset_description_filter":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.datasetDescriptionFilter(
                    first=0,
                    offset=0,
                    # study_organ_system=item.filter.get("study_organ_system", None),
                    project_id=item.access,
                ),
            )
        elif item.node == "manifest_filter":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.manifestFilter(
                    first=0,
                    offset=0,
                    additional_types=item.filter.get("additional_types", None),
                    project_id=item.access,
                ),
            )
        elif item.node == "case_filter":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.caseFilter(
                    first=0,
                    offset=0,
                    species=item.filter.get("species", None),
                    sex=item.filter.get("sex", None),
                    age_category=item.filter.get("age_category", None),
                    project_id=item.access,
                ),
            )
        # QUERY
        # if the node name contains "_query",
        # the query generator will only be used for /graphql/query API
        elif item.node == "experiment_query":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.experimentQuery(
                    first=0,
                    offset=0,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                ),
            )
        elif item.node == "dataset_description_query":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.datasetDescriptionQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                    project_id=item.access,
                ),
            )
        elif item.node == "manifest_query":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.manifestQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                    project_id=item.access,
                ),
            )
        elif item.node == "case_query":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.caseQuery(
                    first=0,
                    offset=0,
                    quick_search=item.search,
                    project_id=item.access,
                ),
            )
        # PAGINATION
        # if the node name contains "_pagination",
        # the query generator will only be used for /graphql/pagination API
        elif item.node == "experiment_pagination":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.experimentPagination(
                    first=item.limit,
                    offset=(item.page - 1) * item.limit,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                    order_by_asc=item.asc,
                    order_by_desc=item.desc,
                ),
            )
        elif item.node == "experiment_pagination_count":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.experimentPaginationCount(
                    first=0,
                    offset=0,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                ),
            )
        # SUPPORT FOR PAGINATION ORDER
        elif item.node == "pagination_order_by_dataset_description":
            graphql_query_code = self._handle_query_code_format(
                item,
                query.paginationOrderByDatasetDescription(
                    first=item.limit,
                    offset=(item.page - 1) * item.limit,
                    submitter_id=item.filter.get("submitter_id", None),
                    project_id=item.access,
                    order_by_asc=item.asc,
                    order_by_desc=item.desc,
                ),
            )
        return graphql_query_code
