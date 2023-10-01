from tests.test_function.test_pagination.fixture import (
    dummy_filter_cache,
    dummy_pagination_data,
    pf_class,
)


def test_reconstruct_data_structure(pf_class, dummy_pagination_data):
    result = pf_class.reconstruct_data_structure(dummy_pagination_data)[0]
    assert (
        result["data_url_suffix"]
        == "/data/browser/dataset/dummy submitter?datasetTab=abstract"
    )
    assert result["source_url_middle"] == "/data/download/dummy submitter/"
    assert result["contributors"] == [
        {
            "name": "dummy contributor",
        },
        {
            "name": "extra dummy contributor",
        },
    ]
    assert result["keywords"] == [
        "dummy keyword",
    ]
    assert result["numberSamples"] == 12
    assert result["numberSubjects"] == 12
    assert result["name"] == "dummy title"
    assert result["datasetId"] == "dummy submitter"
    assert result["organs"] == [
        "dummy organ",
    ]
    assert result["species"] == [
        "Dummy species",
        "extra dummy species",
    ]
    assert result["plots"] == [
        {
            "image_url": "",
            "additional_mimetype": {
                "name": "text/vnd.abi.plot+csv",
            },
            "datacite": {
                "isDerivedFrom": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isDescribedBy": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isSourceOf": {
                    "path": [""],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "supplemental_json_metadata": {
                    "description": "",
                },
            },
            "dataset": {
                "identifier": "dummy id",
                "path": "dummy_filepath/dummy_filename.csv",
            },
            "file_type": {
                "name": ".csv",
            },
            "identifier": "dummy id",
            "name": "dummy_filename.csv",
        },
    ]
    assert result["scaffoldViews"] == [
        {
            "image_url": "/data/preview/dummy submitter/dummy_filepath/dummy_thumbnail.jpeg",
            "additional_mimetype": {
                "name": "application/x.vnd.abi.scaffold.view+json",
            },
            "datacite": {
                "isDerivedFrom": {
                    "path": [
                        "dummy_filepath/dummy_metadata.json",
                    ],
                    "relative": {
                        "path": [
                            "dummy_metadata.json",
                        ],
                    },
                },
                "isDescribedBy": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isSourceOf": {
                    "path": ["dummy_filepath/dummy_thumbnail.jpeg"],
                    "relative": {
                        "path": [
                            "dummy_thumbnail.jpeg",
                        ],
                    },
                },
                "supplemental_json_metadata": {
                    "description": "",
                },
            },
            "dataset": {
                "identifier": "dummy id",
                "path": "dummy_filepath/dummy_view.json",
            },
            "file_type": {
                "name": ".json",
            },
            "identifier": "dummy id",
            "name": "dummy_view.json",
        },
    ]
    assert result["scaffolds"] == [
        {
            "image_url": "",
            "additional_mimetype": {
                "name": "application/x.vnd.abi.scaffold.meta+json",
            },
            "datacite": {
                "isDerivedFrom": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isDescribedBy": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isSourceOf": {
                    "path": [
                        "dummy_filepath/dummy_view.json",
                    ],
                    "relative": {
                        "path": [
                            "dummy_view.json",
                        ],
                    },
                },
                "supplemental_json_metadata": {
                    "description": "",
                },
            },
            "dataset": {
                "identifier": "dummy id",
                "path": "dummy_filepath/dummy_metadata.json",
            },
            "file_type": {
                "name": ".json",
            },
            "identifier": "dummy id",
            "name": "dummy_metadata.json",
        },
    ]
    assert result["thumbnails"] == [
        {
            "image_url": "/data/preview/dummy submitter/dummy_filepath/dummy_filename.jpg",
            "additional_mimetype": {
                "name": "",
            },
            "datacite": {
                "isDerivedFrom": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isDescribedBy": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isSourceOf": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "supplemental_json_metadata": {
                    "description": "",
                },
            },
            "dataset": {
                "identifier": "dummy id",
                "path": "dummy_filepath/dummy_filename.jpg",
            },
            "file_type": {
                "name": ".jpg",
            },
            "identifier": "dummy id",
            "name": "dummy_filename.jpg",
        }
    ]
    assert result["mris"] == [
        {
            "image_url": "",
            "additional_mimetype": {
                "name": "",
            },
            "datacite": {
                "isDerivedFrom": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isDescribedBy": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isSourceOf": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "supplemental_json_metadata": {
                    "description": "",
                },
            },
            "dataset": {
                "identifier": "dummy id",
                "path": "dummy_filepath/sub-dummy/sam-dummy/dummy_filename.nrrd",
            },
            "file_type": {
                "name": ".nrrd",
            },
            "identifier": "dummy id",
            "name": "dummy_filename.nrrd",
        },
    ]
    assert result["dicomImages"] == [
        {
            "image_url": "",
            "additional_mimetype": {
                "name": "application/dicom",
            },
            "datacite": {
                "isDerivedFrom": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isDescribedBy": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "isSourceOf": {
                    "path": [
                        "",
                    ],
                    "relative": {
                        "path": [
                            "",
                        ],
                    },
                },
                "supplemental_json_metadata": {
                    "description": "",
                },
            },
            "dataset": {
                "identifier": "dummy id",
                "path": "dummy_filepath/sub-dummy/sam-dummy/dummy_filename.dcm",
            },
            "file_type": {
                "name": ".dcm",
            },
            "identifier": "dummy id",
            "name": "dummy_filename.dcm",
        },
    ]
    assert result["detailsReady"] == True
