import re

from fastapi import HTTPException

from sgqlc.operation import Operation
from app.sgqlc_schema import Query

NOT_FOUND = 404


class SimpleGraphQLClient:
    def add_count_field(self, item, query):
        # Add count field to query
        count_field = f"total: _{item.node}_count(quick_search: \"{item.search}\")"
        if item.filter != {}:
            # Manually modify and add count filed into graphql query
            count_field = re.sub('\'', '\"', f"total: _{item.node}_count(quick_search: \"{item.search}\", " + re.sub(
                '\'([_a-z]+)\'', r'\1', re.sub('\{([^{].*[^}])\}', r'\1', f"{item.filter})")))
        if item.node == "experiment":
            # Display all sub nodes records
            query = re.sub(
                's {', 's(first: 0) {', query) + count_field
        else:
            query += count_field
        return query

    def convert_query(self, item, query):
        # Convert camel case to snake case
        snake_case_query = re.sub(
            '_[A-Z]', lambda x:  x.group(0).lower(), re.sub('([a-z])([A-Z])', r'\1_\2', str(query)))
        final_query = self.add_count_field(item, snake_case_query)
        return "{" + final_query + "}"

    def generate_query(self, item):
        query = Operation(Query)
        if item.node == "experiment":
            if "submitter_id" in item.filter:
                experiment_query = self.convert_query(item, query.experiment(
                    first=item.limit, offset=(item.page-1)*item.limit, quick_search=item.search, submitter_id=item.filter["submitter_id"]))
            else:
                experiment_query = self.convert_query(
                    item, query.experiment(first=item.limit, offset=(item.page-1)*item.limit, quick_search=item.search))
            return experiment_query
        elif item.node == "dataset_description":
            if "submitter_id" in item.filter:
                dataset_description_query = self.convert_query(item, query.datasetDescription(
                    first=item.limit, offset=(item.page-1)*item.limit, quick_search=item.search, submitter_id=item.filter["submitter_id"]))
            else:
                dataset_description_query = self.convert_query(
                    item, query.datasetDescription(first=item.limit, offset=(item.page-1)*item.limit, quick_search=item.search))
            return dataset_description_query
        elif item.node == "manifest":
            if "submitter_id" in item.filter:
                manifest_query = self.convert_query(item, query.manifest(
                    first=item.limit, offset=(item.page-1)*item.limit, quick_search=item.search, submitter_id=item.filter["submitter_id"]))
            elif "additional_types" in item.filter:
                manifest_query = self.convert_query(item, query.manifest(first=item.limit, offset=(
                    item.page-1)*item.limit, quick_search=item.search, additional_types=item.filter["additional_types"]))
            else:
                manifest_query = self.convert_query(item, query.manifest(
                    first=item.limit, offset=(item.page-1)*item.limit, quick_search=item.search))
            return manifest_query
        else:
            raise HTTPException(status_code=NOT_FOUND,
                                detail="Query cannot be generated.")
