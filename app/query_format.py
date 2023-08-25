import re


class QueryFormat(object):
    def __init__(self, fg, f):
        self.FILTERS = fg.get_filters()
        self.FIELDS = f.get_fields()

    def generate_facet_object(self, filter_facet, mapped_element):
        # Based on mapintergratedvuer map sidebar required filter format
        facet_object = {}
        facet_object["facet"] = filter_facet
        facet_object["term"] = self.FILTERS[mapped_element]["title"].capitalize()
        facet_object["facetPropPath"] = self.FILTERS[mapped_element]["node"] + \
            ">" + self.FILTERS[mapped_element]["field"]
        return facet_object

    def check_facet(self, facet_value, field, field_value):
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

    def handle_matched_facet(self, related_facet, field, field_value):
        mapped_element = f"MAPPED_{field.upper()}"
        for filter_facet, facet_value in self.FILTERS[mapped_element]["facets"].items():
            is_match = self.check_facet(facet_value, field, field_value)
            if is_match and filter_facet not in related_facet.keys():
                related_facet[filter_facet] = self.generate_facet_object(
                    filter_facet, mapped_element)

    def generate_related_facet(self, data):
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
            if key in data.keys() and data[key] != []:
                for ele in data[key]:
                    self.handle_matched_facet(related_facet, field, ele[field])
        return list(related_facet.values())

    def update_mris(self, data):
        mris = []
        mri_path = {}
        for mri in data:
            filename = mri["filename"]
            if "c0" in filename:
                mris.append(mri)
            start = filename.rindex("/") + 1
            end = filename.rindex("_")
            instance = filename[start:end]
            if instance not in mri_path:
                mri_path[instance] = [filename]
            else:
                mri_path[instance].append(filename)
        return mris, mri_path

    def update_dicom_images(self, data):
        dicom_images = []
        dicom_path = {}
        for dicom in data:
            filename = dicom["filename"].split("/")
            study = re.sub('sub-', '', filename[1])
            series = re.sub('sam-', '', filename[2])
            instance = filename[3]
            path = f"{study}/{series}"
            if path not in dicom_path:
                dicom_path[path] = instance
                dicom_images.append(dicom)
        return dicom_images, dicom_path

    def modify_data_structure(self, data):
        if data["dicomImages"] != []:
            dicom_images, dicom_path = self.update_dicom_images(
                data["dicomImages"])
            data["dicomImages"] = dicom_images
        if data["mris"] != []:
            mris, mri_path = self.update_mris(data["mris"])
            data["mris"] = mris
        return data
