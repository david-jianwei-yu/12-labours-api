import re
from app.mime_types import MAPPED_MIME_TYPES


class Filter:
    def generate_mimetypes_filter_data(self, data):
        result = {}
        others = []
        for ele in data["data"]:
            dataset_value = ele["experiments"][0]["submitter_id"]
            if "additional_types" in ele.keys():
                mime_type_key = ele["additional_types"]
                if mime_type_key in MAPPED_MIME_TYPES:
                    # Convert the value name with more readable word
                    ele["additional_types"] = re.sub(
                        '(_[A-Z]+)', '', MAPPED_MIME_TYPES[mime_type_key]).capitalize()
                    # Re-assign the value
                    mime_type_key = ele["additional_types"]
                    if mime_type_key not in result.keys():
                        result[mime_type_key] = [dataset_value]
                    else:
                        # Avoid duplicate value
                        if dataset_value not in result[mime_type_key]:
                            result[mime_type_key].append(dataset_value)
                else:
                    if dataset_value not in others:
                        others.append(dataset_value)
            else:
                if dataset_value not in others:
                    others.append(dataset_value)
        # Add items which not meet above condition
        for ele in others:
            if not any(ele in val for val in result.values()):
                if "Others" not in result.keys():
                    result["Others"] = [ele]
                else:
                    result["Others"].append(ele)
        return result
