import os
import typing as t
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest

from ts_sdk.task.__task_script_runner import Context
from ts_sdk.task.__util_config import (
    IDS,
    MISSING_ALLOWED_IDS,
    AllowedIDS,
    IDSInvalidWrite,
    IDSNotAllowed,
    IDSValidateWrongParams,
)


class LogMock:
    def log(self, data):
        print(data)


class ContextMethodsTest(TestCase):
    def setUp(self):
        os.environ["TASK_SCRIPTS_CONTAINERS_MODE"] = "ecs"
        os.environ["TS_SECRET_password"] = "secretvalue"

        self.datalake_mock = MagicMock()
        self.datalake_mock.get_file_name = MagicMock(return_value="filename")
        self.datalake_mock.get_presigned_url = MagicMock(return_value="presigned_url")

        self.ids_mock = {
            "get_ids": MagicMock(return_value={}),
            "validate_ids": MagicMock(return_value=True),
        }

        self.input_file = {
            "type": "s3",
            "bucket": "bucket",
            "fileKey": "some/fileKey",
            "fileId": "11111111-eeee-4444-bbbb-222222222222",
        }

        self.pipeline_config = {"ts_secret_name_password": "some/kms/path"}
        self.allowed_ids = AllowedIDS.from_allowedIds(
            {"namespace": "common", "slug": "example", "version": "v1.0.0"}
        )

        self.context_to_test = Context(
            {
                "inputFile": self.input_file,
                "pipelineConfig": self.pipeline_config,
                "orgSlug": "org_slug_from_context",
            },
            self.datalake_mock,
            self.ids_mock,
            MagicMock(),  # logger
            self.allowed_ids,
        )

    def tearDown(self):
        pass

    def test_read_file(self):
        """Make sure read_file with an input file dict calls the correct methods"""
        # Arrange
        self.context_to_test.search_eql = MagicMock(return_value=[])

        # Act
        self.context_to_test.read_file(self.input_file)

        # Assert
        self.datalake_mock.read_file.assert_called_once()
        self.context_to_test.search_eql.assert_not_called()

    def test_read_file_via_file_id_only(self):
        """Make sure that search_eql is called when reading a file using just a fileId"""
        # Arrange
        self.context_to_test.search_eql = MagicMock(return_value=[{}])

        # Act
        self.context_to_test.read_file(
            {"fileId": "11111111-eeee-4444-bbbb-222222222222"}
        )

        # Assert
        self.datalake_mock.read_file.assert_called_once()
        self.context_to_test.search_eql.assert_called_once()

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file(self, validate_file_labels_mock):
        """Make sure write_file calls the correct methods"""
        # Act
        self.context_to_test.write_file("content", "file_name", "RAW")

        # Assert
        self.datalake_mock.write_file.assert_called_once_with(
            content="content",
            context=self.context_to_test._obj,
            file_category="RAW",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            file_name="file_name",
            ids=None,
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            gzip_compress_level=5,
        )
        validate_file_labels_mock.assert_called_once_with(tuple())

    ### Allowed IDS test cases for write_file ###

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file_writing_ids_with_no_ids_parameter(
        self, validate_file_labels_mock
    ):
        """
        Make sure write_file calls the correct methods
        Even though allowedIds is missing and ids parameter passed to
        write_file is None, write_file should not raise any error
        """
        # Arrange
        self.context_to_test._allowed_ids = MISSING_ALLOWED_IDS

        # Act
        self.context_to_test.write_file("content", "file_name", "IDS", ids=None)

        # Assert
        self.datalake_mock.write_file.assert_called_once_with(
            content="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            file_name="file_name",
            ids=None,
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file_writing_ids_with_ids_parameter_when_allowed_ids_is_missing(
        self, validate_file_labels_mock
    ):
        """
        Make writing IDS file when allowedIds is not defined(missing)
        Even though allowedIds is missing and write_file should be called
        """
        # Arrange
        self.context_to_test._allowed_ids = MISSING_ALLOWED_IDS

        # Act
        self.context_to_test.write_file(
            "content", "file_name", "IDS", ids="common/my-ids:v1.0.0"
        )

        # Assert
        self.datalake_mock.write_file.assert_called_once_with(
            content="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            file_name="file_name",
            ids="common/my-ids:v1.0.0",
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file_writing_ids_with_not_allowed_ids(
        self, validate_file_labels_mock
    ):
        """Make Sure error is raised when writing a non-allowed IDS"""
        # Arrange
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        allowed_ids_list = [
            IDS(namespace="common", slug="my-ids", version="v1.0.0"),
            IDS(namespace="common", slug="my-ids", version="v1.1.0"),
        ]

        # Act and Assert
        # Simulate: allowedIds is a JSON object
        with pytest.raises(IDSNotAllowed):
            self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)
            self.context_to_test.write_file(
                "content", "file_name", "IDS", ids="common/my-ids:v2.0.0"
            )

        # Simulate: allowedIds is an array of Object
        with pytest.raises(IDSNotAllowed):
            self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids_list)
            self.context_to_test.write_file(
                "content", "file_name", "IDS", ids="common/my-ids:v2.0.0"
            )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file_writing_ids_when_allowed_ids_is_none(
        self, validate_file_labels_mock
    ):
        """
        Make Sure error is raised when trying to write ids but allowed ids is None.
        In this case task-script is not allowed to write IDS
        """
        # Arrange
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=None)

        # Act and Assert
        with pytest.raises(IDSInvalidWrite):
            self.context_to_test.write_file(
                "content", "file_name", "IDS", ids="common/my-ids:v2.0.0"
            )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file_writing_ids_with_no_ids_parameter_and_allowed_ids_is_a_dict(
        self, validate_file_labels_mock
    ):
        """
        In this case, since there is only one allowed IDS, it will be used to write the IDS file
        even if IDS parameter passed to write_file is None
        """
        # Arrange
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)

        # Act
        self.context_to_test.write_file("content", "file_name", "IDS", ids=None)

        # Assert
        self.datalake_mock.write_file.assert_called_once_with(
            content="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            file_name="file_name",
            ids="common/my-ids:v1.0.0",
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_file_writing_ids_with_no_ids_parameter_and_allowed_ids_is_a_list_with_single_entry(
        self, validate_file_labels_mock
    ):
        """
        In this case, since there is only one allowed IDS, it will be used to write the IDS file
        even if IDS parameter passed to write_file is None
        """
        # Arrange
        allowed_ids: IDS = [IDS(namespace="common", slug="my-ids", version="v1.0.0")]
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)

        # Act
        self.context_to_test.write_file("content", "file_name", "IDS", ids=None)

        # Assert
        self.datalake_mock.write_file.assert_called_once_with(
            content="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            file_name="file_name",
            ids="common/my-ids:v1.0.0",
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_invalid_write_file_writing_ids_with_no_ids_parameter_and_allowed_ids_is_a_list_with_multiple_entry(
        self, validate_file_labels_mock
    ):
        """
        In this case, since there is only one allowed IDS, it will be used to write the IDS file
        even if IDS parameter passed to write_file is None
        """
        # Arrange
        allowed_ids: IDS = [
            IDS(namespace="common", slug="my-ids", version="v1.0.0"),
            IDS(namespace="common", slug="my-ids", version="v2.0.0"),
        ]
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)

        # Act and Assert
        with pytest.raises(IDSInvalidWrite):
            self.context_to_test.write_file("content", "file_name", "IDS", ids=None)

    @pytest.mark.skip(
        "This test does not test anything and should be fixed.  Skipping to make coverage more accurate"
    )
    def test_get_ids(self):
        r = self.context_to_test.get_ids("namespace", "slug", "version")
        assert r == {}

    @pytest.mark.skip(
        "This test does not test anything and should be fixed.  Skipping to make coverage more accurate"
    )
    def test_validate_ids(self):
        r = self.context_to_test.validate_ids("data", "namespace", "slug", "version")
        assert r == True

    ### AllowedIDS test cases for validate ids ###
    def test_validate_ids_when_allowed_ids_is_missing(self):
        """
        Make sure missing allowed ids doest stop validate_ids from
        validating the IDS
        """
        self.context_to_test._allowed_ids = MISSING_ALLOWED_IDS

        self.context_to_test.validate_ids("data", "namespace", "slug", "version")
        self.ids_mock["validate_ids"].assert_called_once_with(
            "data", "namespace", "slug", "version"
        )

    def test_validate_ids_when_allowed_ids_is_none(self):
        """
        Since allowed_ids is explicitly set to None, This means task-script is not allowed to write
        IDS files.Hence, validate_ids will raise error stating the same
        """
        self.context_to_test._allowed_ids = AllowedIDS(None)

        with pytest.raises(IDSInvalidWrite):
            self.context_to_test.validate_ids("data", "namespace", "slug", "version")

    def test_validate_ids_when_ids_not_allowed(self):
        """
        Make sure error is raised when trying to validate
        IDS that is not allowed
        """
        # Arrange
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        allowed_ids_list = [
            IDS(namespace="common", slug="my-ids", version="v1.0.0"),
            IDS(namespace="common", slug="my-ids", version="v1.1.0"),
        ]

        # When allowed_ids is a dict
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)
        with pytest.raises(IDSNotAllowed):
            self.context_to_test.validate_ids("data", "namespace", "slug", "version")

        # When allowed_ids is a list
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids_list)
        with pytest.raises(IDSNotAllowed):
            self.context_to_test.validate_ids("data", "namespace", "slug", "version")

    def test_validate_ids_when_ids_is_allowed(self):
        """
        Validate an allowed IDS. Make sure function is called with proper arguments
        """
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids)

        self.context_to_test.validate_ids("data", "common", "my-ids", "v1.0.0")
        self.ids_mock["validate_ids"].assert_called_once_with(
            "data", "common", "my-ids", "v1.0.0"
        )

    def test_validate_ids_when_ns_slug_version_not_set(self):
        """
        Validate an allowed IDS. Make sure function is called with proper arguments
        """
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids)

        self.context_to_test.validate_ids("data")
        self.ids_mock["validate_ids"].assert_called_once_with(
            "data", "common", "my-ids", "v1.0.0"
        )

    def test_validate_ids_when_ns_slug_version_not_set_and_allowed_ids_is_list(self):
        """
        Validate an allowed IDS. Make sure function is called with proper arguments
        """
        allowed_ids: t.Iterable[IDS] = [
            IDS(namespace="common", slug="my-ids", version="v1.0.0"),
            IDS(namespace="common", slug="my-ids", version="v2.0.0"),
        ]
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids)

        with pytest.raises(IDSValidateWrongParams):
            self.context_to_test.validate_ids("data")

    def test_validate_ids_when_ns_slug_version_not_set_and_allowed_ids_is_missing(self):
        """
        Validate an allowed IDS. Make sure function is called with proper arguments
        """
        self.context_to_test._allowed_ids = MISSING_ALLOWED_IDS

        with pytest.raises(IDSValidateWrongParams):
            self.context_to_test.validate_ids("data")

    def test_validate_ids_when_one_of_param_is_not_set(self):
        """
        Validate an allowed IDS. Make sure function is called with proper arguments
        """
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids)

        with pytest.raises(IDSValidateWrongParams):
            self.context_to_test.validate_ids("data", "common", "my-ids")
        with pytest.raises(IDSValidateWrongParams):
            self.context_to_test.validate_ids("data", "common")
        with pytest.raises(IDSValidateWrongParams):
            self.context_to_test.validate_ids("data", version="v1.0.0")

    def test_validate_ids_when_ignore_allowed_ids_is_true(self):
        """
        Validate an allowed IDS. Make sure function is called with proper arguments
        """
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids)

        self.context_to_test.validate_ids(
            "data", "common", "my-ids", "v2.0.0", ignore_allowed_ids=True
        )
        self.ids_mock["validate_ids"].assert_called_once_with(
            "data", "common", "my-ids", "v2.0.0"
        )

    ##############################################

    def test_write_ids(self):
        """Test that write_ids calls the correct methods"""
        # Act
        self.context_to_test.write_ids("content", "file_suffix")

        # Assert
        self.datalake_mock.write_ids.assert_called_once()

    ### allowedIds test cases for write_ids ###
    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_ids_writing_ids_with_no_ids_parameter(
        self, validate_file_labels_mock
    ):
        """
        Make sure write_ids calls the correct methods
        Even though allowedIds is missing and ids parameter passed to
        write_ids is None, write_ids should not raise any error
        """
        # Arrange
        self.context_to_test._allowed_ids = MISSING_ALLOWED_IDS

        # Act
        self.context_to_test.write_ids("content", "file_suffix", ids=None)

        # Assert
        self.datalake_mock.write_ids.assert_called_once_with(
            content_obj="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            ids=None,
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            file_suffix="file_suffix",
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_ids_writing_ids_with_ids_parameter_when_allowed_ids_is_missing(
        self, validate_file_labels_mock
    ):
        """
        Make writing IDS file when allowedIds is not defined(missing)
        Even though allowedIds is missing and write_ids should be called
        """
        # Arrange
        self.context_to_test._allowed_ids = MISSING_ALLOWED_IDS

        # Act
        self.context_to_test.write_ids(
            "content", "file_suffix", ids="common/my-ids:v1.0.0"
        )

        # Assert
        self.datalake_mock.write_ids.assert_called_once_with(
            content_obj="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            ids="common/my-ids:v1.0.0",
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            file_suffix="file_suffix",
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_ids_writing_ids_with_not_allowed_ids(
        self, validate_file_labels_mock
    ):
        """Make Sure error is raised when writing a non-allowed IDS"""
        # Arrange
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        allowed_ids_list = [
            IDS(namespace="common", slug="my-ids", version="v1.0.0"),
            IDS(namespace="common", slug="my-ids", version="v1.1.0"),
        ]

        # Act and Assert
        # Simulate: allowedIds is a JSON object
        with pytest.raises(IDSNotAllowed):
            self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)
            self.context_to_test.write_ids(
                "content", "file_suffix", ids="common/my-ids:v2.0.0"
            )

        # Simulate: allowedIds is an array of Object
        with pytest.raises(IDSNotAllowed):
            self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids_list)
            self.context_to_test.write_ids(
                "content", "file_suffix", ids="common/my-ids:v2.0.0"
            )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_ids_writing_ids_when_allowed_ids_is_none(
        self, validate_file_labels_mock
    ):
        """
        Make Sure error is raised when trying to write ids but allowed ids is None.
        In this case task-script is not allowed to write IDS
        """
        # Arrange
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=None)

        # Act and Assert
        with pytest.raises(IDSInvalidWrite):
            self.context_to_test.write_ids(
                "content", "file_suffix", ids="common/my-ids:v2.0.0"
            )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_ids_writing_ids_with_no_ids_parameter_and_allowed_ids_is_a_dict(
        self, validate_file_labels_mock
    ):
        """
        In this case, since there is only one allowed IDS, it will be used to write the IDS file
        even if IDS parameter passed to write_ids is None
        """
        # Arrange
        allowed_ids: IDS = IDS(namespace="common", slug="my-ids", version="v1.0.0")
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)

        # Act
        self.context_to_test.write_ids("content", "file_suffix", ids=None)

        # Assert
        self.datalake_mock.write_ids.assert_called_once_with(
            content_obj="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            ids="common/my-ids:v1.0.0",
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            file_suffix="file_suffix",
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_write_ids_writing_ids_with_no_ids_parameter_and_allowed_ids_is_a_list_with_single_entry(
        self, validate_file_labels_mock
    ):
        """
        In this case, since there is only one allowed IDS, it will be used to write the IDS file
        even if IDS parameter passed to write_ids is None
        """
        # Arrange
        allowed_ids: IDS = [IDS(namespace="common", slug="my-ids", version="v1.0.0")]
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)

        # Act
        self.context_to_test.write_ids("content", "file_suffix", ids=None)

        # Assert
        self.datalake_mock.write_ids.assert_called_once_with(
            content_obj="content",
            context=self.context_to_test._obj,
            file_category="IDS",
            file_meta={
                "ts_integration_metadata": "",
                "ts_integration_tags": "",
                "ts_trace_id": "11111111-eeee-4444-bbbb-222222222222",
            },
            ids="common/my-ids:v1.0.0",
            labels=(),
            raw_file=self.input_file,
            source_type=None,
            file_suffix="file_suffix",
            gzip_compress_level=5,
        )

    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_invalid_write_ids_writing_ids_with_no_ids_parameter_and_allowed_ids_is_a_list_with_multiple_entry(
        self, validate_file_labels_mock
    ):
        """
        In this case, since there is only one allowed IDS, it will be used to write the IDS file
        even if IDS parameter passed to write_ids is None
        """
        # Arrange
        allowed_ids: IDS = [
            IDS(namespace="common", slug="my-ids", version="v1.0.0"),
            IDS(namespace="common", slug="my-ids", version="v2.0.0"),
        ]
        self.context_to_test._allowed_ids = AllowedIDS(allowed_ids=allowed_ids)

        # Act and Assert
        with pytest.raises(IDSInvalidWrite):
            self.context_to_test.write_ids("content", "file_suffix", ids=None)

    ###########################################

    def test_get_file_name(self):
        """Test that get_file_name calls the correct methods"""
        # Act
        self.context_to_test.get_file_name(self.input_file)

        # Assert
        self.datalake_mock.get_file_name.assert_called_with(self.input_file)

    def test_get_logger(self):
        """Test that the logger that is returned is the correct one from the context"""
        # Arrange
        log_mock = MagicMock()
        self.context_to_test._log = log_mock

        # Act
        logger = self.context_to_test.get_logger()

        # Assert
        assert logger is log_mock

    def test_get_secret_config_value(self):
        """Test that get_secret_config_value gets the secret from the environment"""
        r = self.context_to_test.get_secret_config_value("password")
        # TODO: Test the method that this method calls, and replace this test with a mock assert
        assert r == "secretvalue"

    def test_get_presigned_url(self):
        """Test that get_presigned_url gets the url from the datalake"""
        r = self.context_to_test.get_presigned_url(self.input_file)
        # TODO: Test the method that this method calls, and replace this test with a mock assert
        assert r == "presigned_url"

    @patch("ts_sdk.task.__task_script_runner.validate_file_tags")
    @patch("ts_sdk.task.__task_script_runner.validate_file_meta")
    def test_update_metadata_tags(
        self, validate_file_meta_mock, validate_file_tags_mock
    ):
        """Test that metadata and tags are correctly updated"""
        # Act
        self.context_to_test.update_metadata_tags(
            self.input_file, {"meta1": "v1"}, ["t1", "t2"]
        )
        self.datalake_mock.update_metadata_tags.assert_called_once_with(
            context=self.context_to_test._obj,
            custom_meta={"meta1": "v1"},
            custom_tags=["t1", "t2"],
            file=self.input_file,
            options={},
        )
        validate_file_meta_mock.assert_called_once_with({"meta1": "v1"})
        validate_file_tags_mock.assert_called_once_with(["t1", "t2"])

    @patch("ts_sdk.task.__task_script_runner.run_command")
    def test_run_command(self, run_command_mock):
        """Tests that the run_command method calls the correct methods"""
        # Act
        self.context_to_test.run_command(
            "org_slug", "target_id", "action", {"meta1": "v1"}, "payload"
        )
        # Assert
        run_command_mock.assert_called_once_with(
            self.context_to_test._obj,
            "org_slug",
            "target_id",
            "action",
            {"meta1": "v1"},
            "payload",
            300,
        )

    @patch("ts_sdk.task.__task_script_runner.run_command")
    def test_run_cmd(self, run_command_mock):
        """Tests that the run_cmd method calls the correct methods"""
        # Act
        self.context_to_test.run_cmd("target_id", "action", {"meta1": "v1"}, "payload")
        # Assert
        run_command_mock.assert_called_once_with(
            self.context_to_test._obj,
            "org_slug_from_context",
            "target_id",
            "action",
            {"meta1": "v1"},
            "payload",
            300,
        )

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_add_labels(self, validate_file_labels_mock, add_labels_mock):
        """Test that add_labels calls the correct function and correctly validates"""
        # Act
        self.context_to_test.add_labels(
            self.input_file, [{"name": "label1", "value": "label-value-1"}]
        )
        # Assert
        add_labels_mock.assert_called_once()
        validate_file_labels_mock.assert_called_once_with(
            [{"name": "label1", "value": "label-value-1"}]
        )

    @patch("ts_sdk.task.__task_script_runner.get_labels")
    def test_get_labels(self, get_labels_mock):
        """Test that get_labels calls the correct method"""
        # Act
        self.context_to_test.get_labels(self.input_file)

        # Assert
        get_labels_mock.assert_called_once()

    @patch("ts_sdk.task.__task_script_runner.delete_labels")
    def test_delete_labels(self, delete_labels_mock):
        """Test that delete_labels calls the correct method"""
        # Act
        self.context_to_test.delete_labels(self.input_file, [1, 2, 3])

        # Arrange
        delete_labels_mock.assert_called_once_with(
            self.context_to_test._obj, self.input_file["fileId"], [1, 2, 3]
        )

    @patch("ts_sdk.task.__task_script_runner.delete_labels")
    def test_delete_none_labels(self, delete_labels_mock):
        """
        Test that delete_labels calls the correct method and replaced None with an
        empty list
        """
        # Act
        self.context_to_test.delete_labels(self.input_file, None)

        # Arrange
        delete_labels_mock.assert_called_once_with(
            self.context_to_test._obj, self.input_file["fileId"], []
        )

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    def test_add_attributes_labels_only(
        self, validate_file_labels_mock, add_labels_mock
    ):
        """Test that add_attributes calls the correct methods when only tags are supplied"""

        # Act
        self.context_to_test.add_attributes(
            self.input_file, labels=[{"name": "label-name", "value": "label-value"}]
        )

        # Assert
        add_labels_mock.assert_called_once()
        self.datalake_mock.create_labels_file.assert_not_called()
        self.datalake_mock.update_metadata_tags.assert_not_called()

        validate_file_labels_mock.assert_called_once_with(
            [{"name": "label-name", "value": "label-value"}]
        )

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_meta")
    @patch("ts_sdk.task.__task_script_runner.validate_file_tags")
    def test_add_attributes_all_attrs(
        self,
        validate_file_tags_mock,
        validate_file_meta_mock,
        validate_file_labels_mock,
        add_labels_mock,
    ):
        """Test that add_attributes calls the correct methods when metadata, tags, and labels are specified"""

        # Act
        self.context_to_test.add_attributes(
            self.input_file,
            custom_meta={"m1": "v1"},
            custom_tags=["t1"],
            labels=[{"name": "label-name", "value": "label-value"}],
        )

        # Assert
        add_labels_mock.assert_not_called()
        self.datalake_mock.update_metadata_tags.assert_called_once()
        self.datalake_mock.create_labels_file.assert_called_once()
        create_labels_file_arg = self.datalake_mock.create_labels_file.call_args[1][
            "target_file"
        ]
        update_metadata_tags_options_arg = (
            self.datalake_mock.update_metadata_tags.call_args[1]["options"]
        )
        assert (
            create_labels_file_arg["fileId"]
            == update_metadata_tags_options_arg["new_file_id"]
        )

        validate_file_meta_mock.assert_called_once_with({"m1": "v1"})
        validate_file_tags_mock.assert_called_once_with(["t1"])
        validate_file_labels_mock.assert_called_once_with(
            [{"name": "label-name", "value": "label-value"}]
        )

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_tags")
    def test_add_attributes_tags_labels(
        self, validate_file_tags_mock, validate_file_labels_mock, add_labels_mock
    ):
        """Test that add_attributes calls the correct methods when only tags and labels are specified"""

        # Act
        self.context_to_test.add_attributes(
            self.input_file,
            custom_tags=["t1"],
            labels=[{"name": "label-name", "value": "label-value"}],
        )

        # Assert
        add_labels_mock.assert_not_called()
        self.datalake_mock.update_metadata_tags.assert_called_once()
        self.datalake_mock.create_labels_file.assert_called_once()
        create_labels_file_arg = self.datalake_mock.create_labels_file.call_args[1][
            "target_file"
        ]
        update_metadata_tags_options_arg = (
            self.datalake_mock.update_metadata_tags.call_args[1]["options"]
        )
        assert (
            create_labels_file_arg["fileId"]
            == update_metadata_tags_options_arg["new_file_id"]
        )

        validate_file_tags_mock.assert_called_once_with(["t1"])
        validate_file_labels_mock.assert_called_once_with(
            [{"name": "label-name", "value": "label-value"}]
        )

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_meta")
    def test_add_attributes_labels_meta_attrs(
        self, validate_file_meta_mock, validate_file_labels_mock, add_labels_mock
    ):
        """Test that add_attributes calls the correct methods when only metadata and labels are specified"""

        # Act
        self.context_to_test.add_attributes(
            self.input_file,
            custom_meta={"m1": "v1"},
            custom_tags=["t1"],
            labels=[{"name": "label-name", "value": "label-value"}],
        )

        # Assert
        add_labels_mock.assert_not_called()
        self.datalake_mock.update_metadata_tags.assert_called_once()
        self.datalake_mock.create_labels_file.assert_called_once()
        create_labels_file_arg = self.datalake_mock.create_labels_file.call_args[1][
            "target_file"
        ]
        update_metadata_tags_options_arg = (
            self.datalake_mock.update_metadata_tags.call_args[1]["options"]
        )
        assert (
            create_labels_file_arg["fileId"]
            == update_metadata_tags_options_arg["new_file_id"]
        )

        validate_file_meta_mock.assert_called_once_with({"m1": "v1"})
        validate_file_labels_mock.assert_called_once_with(
            [{"name": "label-name", "value": "label-value"}]
        )

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    @patch("ts_sdk.task.__task_script_runner.validate_file_meta")
    @patch("ts_sdk.task.__task_script_runner.validate_file_tags")
    def test_add_attributes_tags_metadata(
        self, validate_file_tags_mock, validate_file_meta_mock, add_labels_mock
    ):
        """Test that add_attributes calls the correct methods when only metadata and tags are specified"""

        # Act
        self.context_to_test.add_attributes(
            self.input_file,
            custom_meta={"m1": "v1"},
            custom_tags=["t1"],
        )

        # Assert
        add_labels_mock.add_labels.assert_not_called()
        self.datalake_mock.update_metadata_tags.assert_called_once()
        self.datalake_mock.create_labels_file.assert_not_called()

        update_metadata_tags_options_arg = (
            self.datalake_mock.update_metadata_tags.call_args[1]["options"]
        )

        validate_file_meta_mock.assert_called_once_with({"m1": "v1"})
        validate_file_tags_mock.assert_called_once_with(["t1"])

    @patch("ts_sdk.task.__task_script_runner.add_labels")
    def test_add_attributes_no_attrs(self, add_labels_mock):
        """Test that add_attributes does nothing when no attributes are provided"""

        # Act
        self.context_to_test.add_attributes(self.input_file)

        # Assert
        add_labels_mock.assert_not_called()
        self.datalake_mock.update_metadata_tags.assert_not_called()
        self.datalake_mock.create_labels_file.assert_not_called()
