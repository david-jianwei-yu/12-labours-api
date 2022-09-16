import re
from app.filter_dictionary import MAPPED_MIME_TYPES, ANATOMY, SPECIES


class Filter:
    def generate_mimetypes_filter_data(self, data):
        result = {}
        others = []
        for ele in data["data"]:
            dataset_value = ele["experiments"][0]["submitter_id"]
            if "additional_types" in ele.keys():
                mimetype_key = ele["additional_types"].lower()
                if mimetype_key in MAPPED_MIME_TYPES:
                    # Convert the value name with more readable word
                    # *** Regex needs UPDATE if more mimetypes are used ***
                    ele["additional_types"] = re.sub(
                        '(_[A-Z]+)', '', MAPPED_MIME_TYPES[mimetype_key]).capitalize()
                    # Re-assign the value
                    mimetype_key = ele["additional_types"]
                    if mimetype_key not in result.keys():
                        result[mimetype_key] = [dataset_value]
                    else:
                        # Avoid duplicate value
                        if dataset_value not in result[mimetype_key]:
                            result[mimetype_key].append(dataset_value)
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

    def generate_anatomy_filter_data(self, data):
        result = {}
        others = []
        for ele in data["data"]:
            dataset_value = ele["experiments"][0]["submitter_id"]
            if "keywords" in ele.keys():
                keywords = re.findall('([a-zA-Z]+)', ele["keywords"])
                for kwd in keywords:
                    anatomy_key = kwd
                    if anatomy_key in ANATOMY:
                        anatomy_value = ANATOMY[anatomy_key].capitalize()
                        if anatomy_key not in result.keys():
                            result[anatomy_value] = [dataset_value]
                        else:
                            if dataset_value not in result[anatomy_value]:
                                result[anatomy_value].append(dataset_value)
                    else:
                        if dataset_value not in others:
                            others.append(dataset_value)
            else:
                if dataset_value not in others:
                    others.append(dataset_value)
        for ele in others:
            if not any(ele in val for val in result.values()):
                if "Others" not in result.keys():
                    result["Others"] = [ele]
                else:
                    result["Others"].append(ele)
        return result

    def generate_species_filter_data(self, data):
        result = {}
        others = []
        for ele in data["data"]:
            dataset_value = ele["experiments"][0]["submitter_id"]
            if "keywords" in ele.keys():
                keywords = re.findall('([a-zA-Z]+)', ele["keywords"])
                for kwd in keywords:
                    species_key = kwd
                    if species_key in SPECIES:
                        species_value = SPECIES[species_key].capitalize()
                        if species_key not in result.keys():
                            result[species_value] = [dataset_value]
                        else:
                            if dataset_value not in result[species_value]:
                                result[species_value].append(dataset_value)
                    else:
                        if dataset_value not in others:
                            others.append(dataset_value)
            else:
                if dataset_value not in others:
                    others.append(dataset_value)
        for ele in others:
            if not any(ele in val for val in result.values()):
                if "Others" not in result.keys():
                    result["Others"] = [ele]
                else:
                    result["Others"].append(ele)
        return result
