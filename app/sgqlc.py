import re

from fastapi import HTTPException

from sgqlc.operation import Operation
from app.sgqlc_schema import Query

NOT_FOUND = 404


class SimpleGraphQLClient:
    def convert_query(self, node, query):
        new_query = re.sub(r'_[A-Z]', lambda x:  x.group(0).lower(),
                           re.sub('([a-z])([A-Z])', r'\1_\2', str(query)))
        if node == "experiment":
            new_query = re.sub('s {', 's(first: 0) {', new_query)
        return "{" + new_query + "}"

    def generate_query(self, item):
        query = Operation(Query)
        node = item.node
        filter = item.filter
        match node:
            case "experiment":
                if "submitter_id" in filter:
                    experiment_query = self.convert_query(node, query.experiment(
                        first=0, submitter_id=filter["submitter_id"]))
                else:
                    experiment_query = self.convert_query(
                        node, query.experiment(first=0, ))
                return experiment_query
            case "dataset_description":
                if "study_organ_system" in filter:
                    dataset_description_query = self.convert_query(node, query.datasetDescription(
                        first=0, study_organ_system=filter["study_organ_system"]))
                else:
                    dataset_description_query = self.convert_query(
                        node, query.datasetDescription(first=0, ))
                return dataset_description_query
            case "manifest":
                if "additional_types" in filter:
                    manifest_query = self.convert_query(node, query.manifest(
                        first=0, additional_types=filter["additional_types"]))
                else:
                    manifest_query = self.convert_query(
                        node, query.manifest(first=0, ))
                return manifest_query
            case _:
                raise HTTPException(status_code=NOT_FOUND,
                                    detail="Query cannot be generated.")
