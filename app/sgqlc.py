import re

from fastapi import HTTPException

from sgqlc.operation import Operation
from app.sgqlc_schema import Query

NOT_FOUND = 404


class Generator:
    def convert_query(self, query):
        new_query = re.sub(r'_[A-Z]', lambda x:  x.group(0).lower(),
                           re.sub('([a-z])([A-Z])', r'\1_\2', query))
        return new_query

    def generate_query(self, item):
        query = Operation(Query)
        match item.node:
            case "case":
                if "sex" in item.filter or "species" in item.filter:
                    case_query = "{" + self.convert_query(str(query.case(
                        sex=item.filter["sex"], species=item.filter["species"]))) + "}"
                    return case_query
                else:
                    raise HTTPException(status_code=NOT_FOUND,
                                        detail="The filter does not exist.")
            case "dataset_description":
                if "study_organ_system" in item.filter:
                    dataset_description_query = "{" + self.convert_query(str(query.datasetDescription(
                        study_organ_system=item.filter["study_organ_system"]))) + "}"
                    return dataset_description_query
                else:
                    raise HTTPException(status_code=NOT_FOUND,
                                        detail="The filter does not exist.")
            case "slide":
                if "file_type" in item.filter:
                    slide_query = "{" + self.convert_query(str(query.slide(
                        file_type=item.filter["file_type"]))) + "}"
                    return slide_query
                else:
                    raise HTTPException(status_code=NOT_FOUND,
                                        detail="The filter does not exist.")
            case _:
                raise HTTPException(status_code=NOT_FOUND,
                                    detail="Query cannot be generated.")
