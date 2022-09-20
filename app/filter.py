import re
from app.filter_dictionary import MAPPED_MIME_TYPES, ANATOMY, SPECIES


class Filter:
    def get_filter_data(self, filter, data):
        if filter == "DATA TYPES":
            filter_result = self.generate_mimetypes_filter_data(data)
        elif filter == "ANATOMICAL STRUCTURE":
            filter_result = self.generate_anatomy_filter_data(data)
        elif filter == "SPECIES":
            filter_result = self.generate_species_filter_data(data)
        return filter_result

    def add_main_dict(self, key, value, result):
        if key not in result.keys():
            result[key] = [value]
        else:
            # Avoid duplicate value
            if value not in result[key]:
                result[key].append(value)

    def append_others_list(self, value, list):
        # Avoid duplicate value
        if value not in list:
            list.append(value)

    def add_others_dict(self, result, others):
        for ele in others:
            if not any(ele in val for val in result.values()):
                if "Others" not in result.keys():
                    result["Others"] = [ele]
                else:
                    result["Others"].append(ele)

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
                    self.add_main_dict(mimetype_key, dataset_value, result)
                else:
                    self.append_others_list(dataset_value, others)
            else:
                self.append_others_list(dataset_value, others)
        # Add items which not meet above condition
        self.add_others_dict(result, others)
        return result

    def generate_anatomy_filter_data(self, data):
        result = {}
        others = []
        for ele in data["data"]:
            dataset_value = ele["experiments"][0]["submitter_id"]
            if "keywords" in ele.keys():
                keywords = re.findall('([a-zA-Z]+)', ele["keywords"])
                for kwd in keywords:
                    if kwd in ANATOMY:
                        anatomy_key = ANATOMY[kwd].capitalize()
                        self.add_main_dict(anatomy_key, dataset_value, result)
                    else:
                        self.append_others_list(dataset_value, others)
            else:
                self.append_others_list(dataset_value, others)
        self.add_others_dict(result, others)
        return result

    def generate_species_filter_data(self, data):
        result = {}
        others = []
        for ele in data["data"]:
            dataset_value = ele["experiments"][0]["submitter_id"]
            if "keywords" in ele.keys():
                keywords = re.findall('([a-zA-Z]+)', ele["keywords"])
                for kwd in keywords:
                    if kwd in SPECIES:
                        species_key = SPECIES[kwd].capitalize()
                        self.add_main_dict(species_key, dataset_value, result)
                    else:
                        self.append_others_list(dataset_value, others)
            else:
                self.append_others_list(dataset_value, others)
        self.add_others_dict(result, others)
        return result
