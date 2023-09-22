"""
Functionality for editing the filer_template.json
- update_filter_cache
- cache_loader
"""
import json
import os


class FilterEditor:
    """
    Filter editor functionality
    """

    def __init__(self):
        self.__file_path = os.path.join(
            os.path.dirname(__file__), "./filter_template.json"
        )
        self.__filter_cache = self._template_loader()

    def update_filter_cache(self, mapped_filters):
        """
        Handler for uploading filter cache to self.__filter_cache
        """
        # with open(self.__file_path, "w", encoding="utf-8") as json_file:
        #     json.dump(mapped_filters, json_file, indent=4, sort_keys=True)
        self.__filter_cache = mapped_filters

    def cache_loader(self):
        """
        Handler for loading filter cache
        """
        return self.__filter_cache

    def _template_loader(self):
        """
        Handler for loading filter template
        """
        with open(self.__file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
