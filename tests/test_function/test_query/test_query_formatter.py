from tests.test_function.test_query.fixture import (
    dummy_filter_cache,
    dummy_filter_cache_private,
    dummy_query_data,
    qf_class,
)


def test_process_data_output_mode_data(qf_class, dummy_query_data):
    mode = "data"
    qf_class.set_query_mode(mode)
    qf_class.set_private_filter({})
    output = qf_class.process_data_output(dummy_query_data)
    assert output[mode] == dummy_query_data


def test_process_data_output_mode_detail(qf_class, dummy_query_data):
    mode = "detail"
    qf_class.set_query_mode(mode)
    qf_class.set_private_filter({})
    output = qf_class.process_data_output(dummy_query_data)
    assert output["detail"]["mris"] == [
        {
            "additional_metadata": None,
            "additional_types": None,
            "description": "NA",
            "file_type": ".nrrd",
            "filename": "primary/sub-dummy/sam-dummy/dummy_filename.nrrd",
            "id": "dummy id",
            "is_derived_from": None,
            "is_described_by": None,
            "is_source_of": None,
            "submitter_id": "dummy submitter",
            "supplemental_json_metadata": None,
            "timestamp": "dummy timestamp",
            "type": "manifest",
        },
        {
            "additional_metadata": None,
            "additional_types": None,
            "description": "NA",
            "file_type": ".nrrd",
            "filename": "primary/sub-dummy/sam-dummy/dummy_filename_extra.nrrd",
            "id": "dummy id",
            "is_derived_from": None,
            "is_described_by": None,
            "is_source_of": None,
            "submitter_id": "dummy submitter",
            "supplemental_json_metadata": None,
            "timestamp": "dummy timestamp",
            "type": "manifest",
        },
    ]
    assert output["detail"]["dicomImages"] == [
        {
            "additional_metadata": None,
            "additional_types": "application/dicom",
            "description": "NA",
            "file_type": ".dcm",
            "filename": "primary/sub-dummy/sam-dummy/1-01.dcm",
            "id": "dummy id",
            "is_derived_from": None,
            "is_described_by": None,
            "is_source_of": None,
            "submitter_id": "dummy submitter",
            "supplemental_json_metadata": None,
            "timestamp": "dummy timestamp",
            "type": "manifest",
        },
    ]
    assert output["facet"] == {
        "Data type": [
            "Scaffold",
            "Plot",
            "Dicom",
        ],
        "Age category": [
            "Dummy age category",
        ],
        "Sex": [
            "Male",
        ],
        "Species": [
            "Dummy species",
        ],
        "Anatomical structure": [
            "Dummy organ",
        ],
    }


def test_process_data_output_mode_detail_private(
    qf_class, dummy_filter_cache_private, dummy_query_data
):
    mode = "detail"
    qf_class.set_query_mode(mode)
    qf_class.set_private_filter(dummy_filter_cache_private)
    output = qf_class.process_data_output(dummy_query_data)
    assert output["facet"] == {
        "Data type": [
            "Scaffold",
            "Plot",
            "Dicom",
        ],
        "Age category": [
            "Dummy age category",
        ],
        "Sex": [
            "Male",
        ],
        "Species": [
            "Dummy species",
            "Dummy private species",
        ],
        "Anatomical structure": [
            "Dummy organ",
        ],
    }


def test_process_data_output_mode_facet(qf_class, dummy_query_data):
    mode = "facet"
    qf_class.set_query_mode(mode)
    qf_class.set_private_filter({})
    output = qf_class.process_data_output(dummy_query_data)
    assert output[mode] == [
        {
            "facet": "Scaffold",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Plot",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Dicom",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Dummy age category",
            "term": "Age category",
            "facetPropPath": "case_filter>age_category",
        },
        {
            "facet": "Male",
            "term": "Sex",
            "facetPropPath": "case_filter>sex",
        },
        {
            "facet": "Dummy species",
            "term": "Species",
            "facetPropPath": "case_filter>species",
        },
        {
            "facet": "Dummy organ",
            "term": "Anatomical structure",
            "facetPropPath": "dataset_description_filter>study_organ_system",
        },
    ]


def test_process_data_output_mode_facet_private(
    qf_class, dummy_filter_cache_private, dummy_query_data
):
    mode = "facet"
    qf_class.set_query_mode(mode)
    qf_class.set_private_filter(dummy_filter_cache_private)
    output = qf_class.process_data_output(dummy_query_data)
    assert output[mode] == [
        {
            "facet": "Scaffold",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Plot",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Dicom",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Dummy age category",
            "term": "Age category",
            "facetPropPath": "case_filter>age_category",
        },
        {
            "facet": "Male",
            "term": "Sex",
            "facetPropPath": "case_filter>sex",
        },
        {
            "facet": "Dummy species",
            "term": "Species",
            "facetPropPath": "case_filter>species",
        },
        {
            "facet": "Dummy private species",
            "term": "Species",
            "facetPropPath": "case_filter>species",
        },
        {
            "facet": "Dummy organ",
            "term": "Anatomical structure",
            "facetPropPath": "dataset_description_filter>study_organ_system",
        },
    ]


def test_process_data_output_mode_mri(qf_class, dummy_query_data):
    mode = "mri"
    qf_class.set_query_mode(mode)
    qf_class.set_private_filter({})
    output = qf_class.process_data_output(dummy_query_data)
    assert output[mode] == {
        "dummy_filename": [
            "primary/sub-dummy/sam-dummy/dummy_filename_c0.nrrd",
            "primary/sub-dummy/sam-dummy/dummy_filename_c1.nrrd",
            "primary/sub-dummy/sam-dummy/dummy_filename_c2.nrrd",
            "primary/sub-dummy/sam-dummy/dummy_filename_c3.nrrd",
            "primary/sub-dummy/sam-dummy/dummy_filename_c4.nrrd",
        ],
        "dummy_filename_extra": [
            "primary/sub-dummy/sam-dummy/dummy_filename_extra_c0.nrrd",
        ],
    }
