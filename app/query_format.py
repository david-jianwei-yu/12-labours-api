import re


class QueryFormat(object):
    def __init__(self, fg):
        self.FILTER_MAP = fg.get_filter_map()
        self.mode = None

    def set_mode(self, mode):
        self.mode = mode

    def generate_related_mri(self, data):
        mri_paths = {}
        for mri in data["mris"]:
            filepath = mri["filename"]
            start = filepath.rindex("/") + 1
            end = filepath.rindex("_")
            filename = filepath[start:end]
            if filename not in mri_paths:
                mri_paths[filename] = [filepath]
            else:
                mri_paths[filename].append(filepath)
        return mri_paths

    def handle_facet_mode(self, related_facet, filter_facet, mapped_element):
        if filter_facet not in related_facet:
            # Based on mapintergratedvuer map sidebar required filter format
            facet_object = {}
            facet_object["facet"] = filter_facet
            facet_object["term"] = self.FILTER_MAP[mapped_element]["title"].capitalize(
            )
            facet_object["facetPropPath"] = self.FILTER_MAP[mapped_element]["node"] + \
                ">" + self.FILTER_MAP[mapped_element]["field"]
            related_facet[filter_facet] = facet_object

    def handle_detail_mode(self, related_facet, filter_facet, mapped_element):
        title = self.FILTER_MAP[mapped_element]["title"].capitalize()
        if title in related_facet and filter_facet not in related_facet[title]:
            related_facet[title].append(filter_facet)
        else:
            related_facet[title] = [filter_facet]

    def handle_facet_check(self, facet_value, field_value):
        if type(facet_value) == str:
            # For study_organ_system
            # Array type field
            if type(field_value) == list and facet_value in field_value:
                return True
            # For age_category/sex/species
            # String type field
            elif field_value == facet_value:
                return True
        # For additional_types
        elif type(facet_value) == list and field_value in facet_value:
            return True
        return False

    def handle_facet_structure(self, related_facet, field, data):
        mapped_element = f"MAPPED_{field.upper()}"
        for filter_facet, facet_value in self.FILTER_MAP[mapped_element]["facets"].items():
            for ele in data:
                field_value = ele[field]
                if self.handle_facet_check(facet_value, field_value):
                    if self.mode == "detail":
                        self.handle_detail_mode(
                            related_facet, filter_facet, mapped_element)
                    elif self.mode == "facet":
                        self.handle_facet_mode(
                            related_facet, filter_facet, mapped_element)

    def generate_related_facet(self, data):
        related_facets = {}
        facet_source = [
            "dataset_descriptions>study_organ_system",
            "scaffolds>additional_types",
            "plots>additional_types",
            "cases>age_category",
            "cases>sex",
            "cases>species"
        ]
        for info in facet_source:
            key = info.split(">")[0]
            field = info.split(">")[1]
            if key in data and data[key] != []:
                self.handle_facet_structure(related_facets, field, data[key])
        if self.mode == "detail":
            return related_facets
        elif self.mode == "facet":
            return list(related_facets.values())

    def update_mri(self, data):
        mris = []
        for mri in data:
            filepath = mri["filename"]
            if "_c0" in filepath:
                mri["filename"] = re.sub('_c0', '', mri["filename"])
                mris.append(mri)
        return mris

    def update_dicom_image(self, data):
        dicom_images = {}
        for dicom in data:
            filepath = dicom["filename"]
            # Find the last "/" index in the file path
            index = filepath.rindex("/")
            folder_path = filepath[:index]
            # Keep only the first dicom data each folder
            if folder_path not in dicom_images:
                dicom_images[folder_path] = dicom
        return list(dicom_images.values())

    def update_detail_content(self, data):
        # Combine multiple files within the dataset into one
        # Only need to display one in the portal
        if data["dicomImages"] != []:
            data["dicomImages"] = self.update_dicom_image(data["dicomImages"])
        if data["mris"] != []:
            data["mris"] = self.update_mri(data["mris"])
        return data

    def process_data_output(self, data):
        result = {}
        if self.mode == "data":
            result["data"] = data
        elif self.mode == "detail":
            result["detail"] = self.update_detail_content(data)
            # Filter format facet
            result["facet"] = self.generate_related_facet(data)
        elif self.mode == "facet":
            # Sidebar format facet
            result["facet"] = self.generate_related_facet(data)
        elif self.mode == "mri":
            # Combine 5 sub-file paths based on filename
            result["mri"] = self.generate_related_mri(data)
        return result
