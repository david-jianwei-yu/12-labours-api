"""
Functionality for processing query data output
- set_query_mode
- process_data_output
"""
import re


class QueryFormatter:
    """
    fg -> filter generator object is required
    """

    def __init__(self, fg):
        self._mapped_filter = fg.get_mapped_filter()
        self.__query_mode = None

    def set_query_mode(self, mode):
        """
        Handler for setting query_mode
        """
        self.__query_mode = mode

    def _handle_mri_path(self, data):
        """
        Handler for generating related mri paths
        """
        mri_paths = {}
        for _ in data:
            filepath = _["filename"]
            start = filepath.rindex("/") + 1
            end = filepath.rindex("_")
            filename = filepath[start:end]
            if filename not in mri_paths:
                mri_paths[filename] = [filepath]
            else:
                mri_paths[filename].append(filepath)
        return mri_paths

    def _update_facet_mode(self, related_facets, facet_name, content):
        """
        Handler for updating facet mode related facets
        """
        if facet_name not in related_facets:
            # Based on map integrated viewer map sidebar required filter format
            facet_format = {}
            facet_format["facet"] = facet_name
            facet_format["term"] = content["title"].capitalize()
            facet_format["facetPropPath"] = f"{content['node']}>{content['field']}"
            related_facets[facet_name] = facet_format

    def _update_detail_mode(self, related_facets, facet_name, content):
        """
        Handler for updating detail mode related facets
        """
        title = content["title"].capitalize()
        if title in related_facets:
            if facet_name not in related_facets[title]:
                related_facets[title].append(facet_name)
        else:
            related_facets[title] = [facet_name]

    def _handle_facet_check(self, facet_value, field_value):
        """
        Handler for checking whether facet exist
        """
        if isinstance(facet_value, str):
            # For study_organ_system
            # Array type field
            if isinstance(field_value, list) and facet_value in field_value:
                return True
            # For age_category/species
            # String type field
            elif field_value == facet_value:
                return True
        # For additional_types/sex
        elif isinstance(facet_value, list) and field_value in facet_value:
            return True
        return False

    def _update_related_facet(self, related_facets, field, data):
        """
        Handler for updating related facet
        """
        mapped_element = f"MAPPED_{field.upper()}"
        content = self._mapped_filter[mapped_element]
        for facet_name, facet_value in content["facets"].items():
            for _ in data:
                field_value = _[field]
                if self._handle_facet_check(facet_value, field_value):
                    if self.__query_mode == "detail":
                        self._update_detail_mode(related_facets, facet_name, content)
                    elif self.__query_mode == "facet":
                        self._update_facet_mode(related_facets, facet_name, content)

    def _handle_facet_source(self):
        """
        Handler for generating facet source
        """
        sources = []
        for mapped_element in self._mapped_filter:
            content = self._mapped_filter[mapped_element]
            node = re.sub("_filter", "s", content["node"])
            field = content["field"]
            if node == "experiments":
                pass
            elif node == "manifests":
                sources.append(f"scaffolds>{field}")
                sources.append(f"plots>{field}")
                sources.append(f"dicomImages>{field}")
            else:
                sources.append(f"{node}>{field}")
        return sources

    def _handle_related_facet(self, data):
        """
        Handler for generating related facets for corresponding dataset
        """
        related_facets = {}
        for _ in self._handle_facet_source():
            key = _.split(">")[0]
            field = _.split(">")[1]
            if key in data and data[key] != []:
                self._update_related_facet(related_facets, field, data[key])
        if self.__query_mode == "detail":
            return related_facets
        return list(related_facets.values())

    def _handle_mri(self, data):
        """
        Handler for updating mri data, keep one only
        """
        mris = []
        for _ in data:
            filepath = _["filename"]
            if "_c0" in filepath:
                _["filename"] = re.sub("_c0", "", _["filename"])
                mris.append(_)
        return mris

    def _handle_dicom_image(self, data):
        """
        Handler for updating dicom image data, keep one only
        """
        dicom_images = {}
        for _ in data:
            filepath = _["filename"]
            # Find the last "/" index in the file path
            index = filepath.rindex("/")
            folder_path = filepath[:index]
            # Keep only the first dicom data each folder
            if folder_path not in dicom_images:
                dicom_images[folder_path] = _
        return list(dicom_images.values())

    def _handle_detail_content(self, data):
        """
        Handler for updating detail content
        """
        # Combine multiple files within the dataset into one
        # Only need to display one in the portal
        if data["dicomImages"] != []:
            data["dicomImages"] = self._handle_dicom_image(data["dicomImages"])
        if data["mris"] != []:
            data["mris"] = self._handle_mri(data["mris"])
        return data

    def process_data_output(self, data):
        """
        Handler for processing data output to support portal services
        """
        result = {}
        if self.__query_mode == "data":
            result["data"] = data
        elif self.__query_mode == "detail":
            result["detail"] = self._handle_detail_content(data)
            # Filter format facet
            result["facet"] = self._handle_related_facet(data)
        elif self.__query_mode == "facet":
            # Sidebar format facet
            result["facet"] = self._handle_related_facet(data)
        elif self.__query_mode == "mri":
            # Combine 5 sub-file paths based on filename
            result["mri"] = self._handle_mri_path(data["mris"])
        return result
