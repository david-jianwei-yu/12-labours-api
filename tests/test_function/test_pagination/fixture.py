from app.function.pagination.pagination_formatter import PaginationFormatter
from app.function.filter.filter_editor import FilterEditor
import pytest


@pytest.fixture
def pf_class(dummy_filter_cache):
    fe = FilterEditor()
    fe.update_filter_cache(dummy_filter_cache)
    return PaginationFormatter(fe)


@pytest.fixture
def dummy_filter_cache():
    return {
        "MAPPED_SPECIES": {
            "title": "species",
            "node": "case_filter",
            "field": "species",
            "facets": {
                "Dummy species": "dummy species",
            },
        },
    }


@pytest.fixture
def dummy_pagination_data():
    return [
        {
            "cases": [
                {
                    "id": "dummy id",
                    "species": "dummy species",
                },
                {
                    "id": "dummy id",
                    "species": "extra dummy species",
                },
            ],
            "dataset_descriptions": [
                {
                    "contributor_name": [
                        "dummy contributor",
                        "extra dummy contributor",
                    ],
                    "id": "dummy id",
                    "keywords": [
                        "dummy keyword",
                    ],
                    "number_of_samples": [
                        "12",
                    ],
                    "number_of_subjects": [
                        "12",
                    ],
                    "study_organ_system": [
                        "dummy organ",
                    ],
                    "title": [
                        "dummy title",
                    ],
                },
            ],
            "dicomImages": [
                {
                    "additional_metadata": None,
                    "additional_types": "application/dicom",
                    "file_type": ".dcm",
                    "filename": "dummy_filepath/sub-dummy/sam-dummy/dummy_filename.dcm",
                    "id": "dummy id",
                    "is_derived_from": None,
                    "is_described_by": None,
                    "is_source_of": None,
                    "supplemental_json_metadata": None,
                },
            ],
            "id": "dummy id",
            "mris": [
                {
                    "additional_metadata": None,
                    "additional_types": None,
                    "file_type": ".nrrd",
                    "filename": "dummy_filepath/sub-dummy/sam-dummy/dummy_filename.nrrd",
                    "id": "dummy id",
                    "is_derived_from": None,
                    "is_described_by": None,
                    "is_source_of": None,
                    "supplemental_json_metadata": None,
                },
            ],
            "plots": [
                {
                    "additional_metadata": None,
                    "additional_types": "text/vnd.abi.plot+csv",
                    "file_type": ".csv",
                    "filename": "dummy_filepath/dummy_filename.csv",
                    "id": "dummy id",
                    "is_derived_from": None,
                    "is_described_by": None,
                    "is_source_of": None,
                    "supplemental_json_metadata": None,
                },
            ],
            "scaffoldViews": [
                {
                    "additional_metadata": None,
                    "additional_types": "application/x.vnd.abi.scaffold.view+json",
                    "file_type": ".json",
                    "filename": "dummy_filepath/dummy_view.json",
                    "id": "dummy id",
                    "is_derived_from": "dummy_metadata.json",
                    "is_described_by": None,
                    "is_source_of": "dummy_thumbnail.jpeg",
                    "supplemental_json_metadata": None,
                },
            ],
            "scaffolds": [
                {
                    "additional_metadata": None,
                    "additional_types": "application/x.vnd.abi.scaffold.meta+json",
                    "file_type": ".json",
                    "filename": "dummy_filepath/dummy_metadata.json",
                    "id": "dummy id",
                    "is_derived_from": None,
                    "is_described_by": None,
                    "is_source_of": "dummy_view.json",
                    "supplemental_json_metadata": None,
                },
                {
                    "additional_metadata": None,
                    "additional_types": "application/x.vnd.abi.scaffold.meta+json",
                    "file_type": ".json",
                    "filename": "dummy_filepath/dummy_metadata.json",
                    "id": "dummy id",
                    "is_derived_from": None,
                    "is_described_by": None,
                    "is_source_of": "['dummy_view1.json', 'dummy_view2.json', 'dummy_view3.json', 'dummy_view4.json']",
                    "supplemental_json_metadata": None,
                },
            ],
            "submitter_id": "dummy submitter",
            "thumbnails": [
                {
                    "additional_metadata": None,
                    "additional_types": None,
                    "file_type": ".jpg",
                    "filename": "dummy_filepath/dummy_filename.jpg",
                    "id": "dummy id",
                    "is_derived_from": None,
                    "is_described_by": None,
                    "is_source_of": None,
                    "supplemental_json_metadata": None,
                },
            ],
        }
    ]
