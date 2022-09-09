import re

from fastapi import HTTPException

from sgqlc.operation import Operation
from app.sgqlc_schema import Query

NOT_FOUND = 404


class Generator:
    def convert_query(self, query):
        new_query = re.sub(r'_[A-Z]', lambda x:  x.group(0).lower(),
                           re.sub('([a-z])([A-Z])', r'\1_\2', str(query)))
        return "{" + new_query + "}"

    def generate_query(self, item):
        query = Operation(Query)
        match item.node:
            case "dataset_description":
                if "study_organ_system" in item.filter:
                    dataset_description_query = self.convert_query(query.datasetDescription(
                        first=0, study_organ_system=item.filter["study_organ_system"]))
                    return dataset_description_query
                else:
                    dataset_description_query = self.convert_query(
                        query.datasetDescription(first=0))
                    return dataset_description_query
            case "manifest":
                if "additional_types" in item.filter:
                    manifest_query = self.convert_query(query.manifest(
                        first=0, additional_types=item.filter["additional_types"]))
                    return manifest_query
                else:
                    manifest_query = self.convert_query(
                        query.manifest(first=0))
                    return manifest_query
            case _:
                raise HTTPException(status_code=NOT_FOUND,
                                    detail="Query cannot be generated.")
