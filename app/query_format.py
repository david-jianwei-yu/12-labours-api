from fastapi import HTTPException, status


class QueryFormat(object):
    def __init__(self, fg, f):
        self.FILTERS = fg.get_filters()
        self.FIELDS = f.get_fields()

    def generate_related_mri(self, data):
        mri_path = {}
        for mri in data["mris"]:
            file_path = mri["filename"]
            start = file_path.rindex("/") + 1
            end = file_path.rindex("_")
            filename = file_path[start:end]
            if filename not in mri_path:
                mri_path[filename] = [file_path]
            else:
                mri_path[filename].append(file_path)
        return mri_path

    def handle_detail_mode(self, related_facet, filter_facet, mapped_element):
        title = self.FILTERS[mapped_element]["title"].capitalize()
        if title in related_facet and filter_facet not in related_facet[title]:
            related_facet[title].append(filter_facet)
        else:
            related_facet[title] = [filter_facet]

    def handle_facet_mode(self, related_facet, filter_facet, mapped_element):
        if filter_facet not in related_facet:
            # Based on mapintergratedvuer map sidebar required filter format
            facet_object = {}
            facet_object["facet"] = filter_facet
            facet_object["term"] = self.FILTERS[mapped_element]["title"].capitalize(
            )
            facet_object["facetPropPath"] = self.FILTERS[mapped_element]["node"] + \
                ">" + self.FILTERS[mapped_element]["field"]
            related_facet[filter_facet] = facet_object

    def handle_facet_structure(self, related_facet, filter_facet, mapped_element, mode):
        if mode == "detail":
            self.handle_detail_mode(
                related_facet, filter_facet, mapped_element)
        elif mode == "facet":
            self.handle_facet_mode(related_facet, filter_facet, mapped_element)

    def handle_facet_check(self, facet_value, field, field_value):
        if type(facet_value) == str:
            # For study_organ_system
            # Array type field
            if field in self.FIELDS and facet_value in field_value:
                return True
            # For age_category/sex/species
            # String type field
            elif field_value == facet_value:
                return True
        # For additional_types
        elif type(facet_value) == list and field_value in facet_value:
            return True
        return False

    def handle_facet(self, related_facet, field, field_value, mode):
        mapped_element = f"MAPPED_{field.upper()}"
        for filter_facet, facet_value in self.FILTERS[mapped_element]["facets"].items():
            if self.handle_facet_check(facet_value, field, field_value):
                self.handle_facet_structure(
                    related_facet, filter_facet, mapped_element, mode)

    def generate_related_facet(self, data, mode):
        related_facet = {}
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
                for ele in data[key]:
                    self.handle_facet(related_facet, field, ele[field], mode)
        if mode == "deatil":
            return related_facet
        elif mode == "facet":
            return list(related_facet.values())

    def update_mris(self, data):
        mris = []
        for mri in data:
            file_path = mri["filename"]
            if "c0" in file_path:
                mris.append(mri)
        return mris

    def update_dicom_images(self, data):
        dicom_images = {}
        for dicom in data:
            file_path = dicom["filename"]
            # Find the last "/" index in the file path
            index = file_path.rindex("/")
            folder_path = file_path[:index]
            # Keep only the first dicom data each folder
            if folder_path not in dicom_images:
                dicom_images[folder_path] = dicom
        return list(dicom_images.values())

    def modify_data_content(self, data):
        if data["dicomImages"] != []:
            dicom_images = self.update_dicom_images(data["dicomImages"])
            data["dicomImages"] = dicom_images
        if data["mris"] != []:
            mris = self.update_mris(data["mris"])
            data["mris"] = mris
        return data

    def process_data_output(self, data, mode):
        result = {}
        if mode == "data":
            result["data"] = data
        elif mode == "detail":
            result["data"] = self.modify_data_content(data)
            result["facet"] = self.generate_related_facet(data, mode)
        elif mode == "facet":
            result["facets"] = self.generate_related_facet(data, mode)
        elif mode == "mri":
            result["mris"] = self.generate_related_mri(data)
        else:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=f"Invalid query mode {mode}")
        return result
