"""Unit tests for task/__util_datalake.py functions"""
import datetime
from unittest.mock import MagicMock

import pytest
import simplejson as json

from ts_sdk.task.__util_datalake import Datalake, InvalidPathException
from ts_sdk.task.__util_metadata import FIELDS


def test_datalake_update_metadata_tags():
    """Test update_metadata_tags with dummy data correctly calls S3 copy_object"""
    lake = Datalake("http://localhost:4569/")
    lake.s3.head_object = MagicMock(
        return_value={
            "Metadata": {
                FIELDS["FILE_ID"]: "file_id",
                FIELDS["CUSTOM_METADATA"]: "meta_k_1=meta_v_1&meta_k_2=meta_v_2",
                FIELDS["CUSTOM_TAGS"]: "tag1,tag2",
            },
            "LastModified": datetime.datetime(2021, 1, 1),
            "ContentType": "text/plain",
            "ContentLength": 100,
        }
    )
    lake.s3.copy_object = MagicMock(return_value={})
    file_metadata = {"bucket": "test-bucket", "fileKey": "test/file/key"}
    meta = {"meta_k_3": "meta_v_3", "meta_k_4": "meta_v_4", "meta_k_1": None}
    tags = ["tag3", "tag4", "tag4"]
    return_value = lake.update_metadata_tags({}, file_metadata, meta, tags)

    lake.s3.copy_object.assert_called_once()

    _, kwargs = lake.s3.copy_object.call_args
    assert kwargs["CopySource"] == "/test-bucket/test/file/key"
    assert (
        kwargs["Metadata"][FIELDS["CUSTOM_METADATA"]]
        == "meta_k_2=meta_v_2&meta_k_3=meta_v_3&meta_k_4=meta_v_4"
    )
    assert kwargs["Metadata"][FIELDS["CUSTOM_TAGS"]] == "tag1,tag2,tag3,tag4"
    assert kwargs["Metadata"][FIELDS["CONTENT_CREATED_FROM_FILE_ID"]] == "file_id"
    assert kwargs["Metadata"][FIELDS["DO_NOT_INHERIT_LABELS"]] == "true"
    assert kwargs["Metadata"][FIELDS["FILE_ID"]] is not None
    assert kwargs["Metadata"][FIELDS["FILE_ID"]] != "file_id"
    assert return_value["fileId"] == kwargs["Metadata"][FIELDS["FILE_ID"]]


def test_datalake_update_metadata_tags_if_empty():
    """Test update_metadata_tags correctly calls S3 copy_object with empty data"""
    lake = Datalake("http://localhost:4569/")
    lake.s3.head_object = MagicMock(
        return_value={
            "Metadata": {FIELDS["FILE_ID"]: "file_id"},
            "LastModified": datetime.datetime(2021, 1, 1),
            "ContentType": "text/plain",
            "ContentLength": 20,
        }
    )
    lake.s3.copy_object = MagicMock(return_value={})
    file_metadata = {"bucket": "test-bucket", "fileKey": "test/file/key"}
    meta = {
        "meta_k_3": "meta_v_3",
        "meta_k_4": "meta_v_4",
        "meta_k_1": None,
        "meta_bool": True,
        "meta_int": 123,
    }
    tags = ["tag3", "tag4", "tag4", 123]
    lake.update_metadata_tags({}, file_metadata, meta, tags)

    lake.s3.copy_object.assert_called_once()

    _, kwargs = lake.s3.copy_object.call_args
    assert kwargs["CopySource"] == "/test-bucket/test/file/key"
    assert (
        kwargs["Metadata"][FIELDS["CUSTOM_METADATA"]]
        == "meta_k_3=meta_v_3&meta_k_4=meta_v_4&meta_bool=True&meta_int=123"
    )
    assert kwargs["Metadata"][FIELDS["CUSTOM_TAGS"]] == "123,tag3,tag4"
    assert kwargs["Metadata"][FIELDS["FILE_ID"]] is not None
    assert kwargs["Metadata"][FIELDS["FILE_ID"]] != "file_id"


def test_datalake_update_metadata_tags_no_custom_data_provided():
    """Test update_metadata_tags doesn't call S3 when no custom data provided"""
    lake = Datalake("http://localhost:4569/")
    lake.s3.head_object = MagicMock(
        return_value={
            "Metadata": {
                FIELDS["FILE_ID"]: "file_id",
                FIELDS["CUSTOM_METADATA"]: "meta_k_1=meta_v_1&meta_k_2=meta_v_2",
                FIELDS["CUSTOM_TAGS"]: "tag1,tag2",
            },
            "LastModified": datetime.datetime(2021, 1, 1),
            "ContentType": "text/plain",
            "ContentLength": 100,
        }
    )
    lake.s3.copy_object = MagicMock(return_value={})
    file_metadata = {"bucket": "test-bucket", "fileKey": "test/file/key"}

    returned_file = lake.update_metadata_tags({}, file_metadata, {}, [])

    # make sure copy_object wasn't called since the method should log and return if no custom
    # metadata or tags were provided. We should also receive the original file
    lake.s3.copy_object.assert_not_called()
    assert returned_file == file_metadata


@pytest.mark.parametrize(
    "file_key,expected",
    [
        ("demo/abc/RAW/input.json", "demo/abc/TMP/input.json/fileId.labels"),
        ("demo/abc/RAW/RAW/input.json", "demo/abc/TMP/RAW/input.json/fileId.labels"),
        ("demo/abc/RAW_/RAW/input.json", "demo/abc/RAW_/TMP/input.json/fileId.labels"),
        ("demo/abc/_RAW/RAW/input.json", "demo/abc/_RAW/TMP/input.json/fileId.labels"),
        ("demo/abc/IDS/IDS/input.json", "demo/abc/TMP/IDS/input.json/fileId.labels"),
        (
            "demo/abc/PROCESSED/PROCESSED/input.json",
            "demo/abc/TMP/PROCESSED/input.json/fileId.labels",
        ),
    ],
)
def test_datalake_create_labels_file(file_key: str, expected: str):
    """Test create_labels_file correctly calls S3 put_object function"""
    lake = Datalake("http://localhost:4569/")
    lake.s3.put_object = MagicMock(return_value={})
    lake.s3.head_object = MagicMock(return_value={})
    lake.create_labels_file(
        target_file={
            "fileKey": file_key,
            "fileId": "fileId",
            "bucket": "labels-test-bucket",
        },
        labels=[{"name": "label1", "value": "label-value-1"}],
    )
    lake.s3.put_object.assert_called_once()
    _, kwargs = lake.s3.put_object.call_args
    assert kwargs["Key"] == expected


@pytest.mark.parametrize(
    "input_path, expected",
    [
        ("org/source/category/path/file_name", (True, "")),
        ("org/source/category/path/subpath/file_name", (True, "")),
        ("org/source/category/path/subpath/subsubpath/file_name", (True, "")),
        ("org/source/category/path/subpath/subsubpath/file_name.ext", (True, "")),
        ("org/source/category/path/subpath/subsubpath/file_name..ext", (True, "")),
        (
            "org/source/category/path/subpath/../file_name.ext",
            (False, 'Path cannot contain a directory ".."'),
        ),
        (
            "../org/source/category/path/subpath/file_name.ext",
            (False, 'Path cannot contain a directory ".."'),
        ),
        (
            "org/source/category/path/subpath/..",
            (False, 'Path cannot contain a directory ".."'),
        ),
    ],
)
def test_datalake_is_valid_filepath(input_path, expected):
    """Test private _is_file_path_valid correctly parses example filepaths"""
    actual = Datalake._is_file_path_valid(input_path)
    assert actual == expected


@pytest.mark.parametrize(
    "filename, file_category, file_key",
    [
        ("file_name", "PROCESSED", "../source/prepath/path"),
        ("file_name", "PROCESSED", "org/../prepath/path"),
        ("file_name", "PROCESSED", "org/source/prepath/.."),
        ("file_name.ext", "PROCESSED", "../source/prepath/path"),
        ("file_name.ext", "PROCESSED", "org/../prepath/path"),
        ("file_name.ext", "PROCESSED", "org/source/prepath/.."),
        ("file_name..ext", "PROCESSED", "../source/prepath/path"),
        ("file_name..ext", "PROCESSED", "org/../prepath/path"),
        ("file_name..ext", "PROCESSED", "org/source/prepath/.."),
        ("..", "PROCESSED", "../source/prepath/path"),
        ("..", "PROCESSED", "org/../prepath/path"),
        ("..", "PROCESSED", "org/source/prepath/.."),
        ("..", "PROCESSED", "org/source/prepath/path"),
    ],
)
def test_datalake_rejects_invalid_filepath(filename, file_category, file_key):
    """Test write_file raises InvalidPathException on invalid paths"""
    lake = Datalake("http://localhost:4569/")
    rawfile = {"bucket": None, "fileKey": file_key}

    with pytest.raises(InvalidPathException) as ex_info:
        lake.write_file(None, None, filename, file_category, rawfile, {})

    assert ex_info.value.reason == 'Path cannot contain a directory ".."'


def test_write_ids_raises_error_if_content_obj_is_not_dict():
    # Arrange
    lake = Datalake("http://localhost:4569/")
    test_data = json.dumps({"key": "value"})

    # Act and Assert
    with pytest.raises(
        TypeError, match="'content_obj' passed to 'write_ids' must be of type 'dict'."
    ):
        lake.write_ids(
            {},
            test_data,
            "1.json",
            None,
            {},
            "namespace/slug:0.0.0",
            None,
            "IDS",
            None,
        )


def test_write_ids_filename_prefix():
    # Arrange
    RAW_FILE = {
        "fileKey": "testorg/testsource/testfilecategory/testfilepath",
        "bucket": "test-bucket",
    }

    test_data_dict = {"key": "value"}

    lake = Datalake("http://localhost:4569/")
    lake.write_file = MagicMock()

    # Act
    lake.write_ids(
        {},
        test_data_dict,
        "1.json",
        RAW_FILE,
        {},
        "namespace/slug:0.0.0",
        None,
        "IDS",
        None,
    )

    # Assert
    call_args = lake.write_file.call_args[0]
    file_name = call_args[2]
    assert file_name == "namespace-slug-1.json"
