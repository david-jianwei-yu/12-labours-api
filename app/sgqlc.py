import re

from fastapi import HTTPException

from sgqlc.operation import Operation
from app.sgqlc_schema import Query

NOT_FOUND = 404


class SimpleGraphQLClient:
    def convert_query(self, item, query):
        # Convert camel case to snake case
        snake_case_query = re.sub(
            '_[A-Z]', lambda x:  x.group(0).lower(), re.sub('([a-z])([A-Z])', r'\1_\2', str(query)))
        # Add count field to query
        count_field = f"total: _{item.node}_count"
        if item.filter != {}:
            count_field = re.sub('\'', '\"', f"total: _{item.node}_count" + re.sub(
                '\'([_a-z]+)\'', r'\1', re.sub('\{([^{].*[^}])\}', r'(\1)', f"{item.filter}")))
        if item.node == "experiment":
            # Display all sub nodes records
            snake_case_query = re.sub(
                's {', 's(first: 0) {', snake_case_query) + count_field
        else:
            snake_case_query += count_field
        return "{" + snake_case_query + "}"

    def generate_query(self, item):
        query = Operation(Query)
        match item.node:
            case "experiment":
                if "submitter_id" in item.filter:
                    experiment_query = self.convert_query(item, query.experiment(
                        first=item.limit, offset=(item.page-1)*item.limit, submitter_id=item.filter["submitter_id"]))
                else:
                    experiment_query = self.convert_query(
                        item, query.experiment(first=item.limit, offset=(item.page-1)*item.limit))
                return experiment_query
            case "dataset_description":
                dataset_description_query = self.convert_query(
                    item, query.datasetDescription(first=item.limit, offset=(item.page-1)*item.limit))
                return dataset_description_query
            case "manifest":
                manifest_query = self.convert_query(
                    item, query.manifest(first=item.limit, offset=(item.page-1)*item.limit))
                return manifest_query
            case _:
                raise HTTPException(status_code=NOT_FOUND,
                                    detail="Query cannot be generated.")
