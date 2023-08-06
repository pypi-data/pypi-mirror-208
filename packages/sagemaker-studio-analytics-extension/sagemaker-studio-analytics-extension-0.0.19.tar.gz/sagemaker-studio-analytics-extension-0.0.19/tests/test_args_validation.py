import unittest
from unittest.mock import patch, MagicMock

from IPython.core.error import UsageError

from .resource_patch import *
from sagemaker_studio_analytics_extension.magics import (
    SagemakerAnalytics,
    _validate_emr_args,
)

from sagemaker_studio_analytics_extension.utils.exceptions import MissingParametersError


class DummyMissingAuthTypeArgs:
    auth_type = None
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"
    assumable_role_arn = None


class DummyMissingClusterId:
    auth_type = "Basic_Access"
    cluster_id = None
    language = "python"
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyInvalidAuthType:
    auth_type = "Something"
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyValidPySpark:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyMissingLanguageIPython:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    language = None
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyAssumableRoleArnValidation:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"

    def __init__(self, assumable_role_arn):
        self.assumable_role_arn = assumable_role_arn


class DummyEmrExecutionRoleArnValidation:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"
    assumable_role_arn = None

    def __init__(self, emr_execution_role_arn):
        self.emr_execution_role_arn = emr_execution_role_arn


class TestArgsValidation(unittest.TestCase):
    def test_invalid_service(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                "something connect --cluster-id j-3KMA44GZ4KWEJ --auth-type None"
            )
        self.assertEqual(
            str(e.exception),
            "Service 'something' not found. Please look at usage of %sm_analytics by "
            "executing `%sm_analytics?`.",
        )

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.ServiceFileLogger"
    )
    def test_invalid_operation(self, mock_logger):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                "emr disconnect --cluster-id j-3KMA44GZ4KWEJ --auth-type None"
            )
        self.assertEqual(
            str(e.exception),
            "Operation 'disconnect' not found. Please look at usage of %sm_analytics by executing `%sm_analytics?`.",
        )

    def test_missing_cluster_id(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr disconnect --cluster-id --auth-type None")
        self.assertEqual(
            str(e.exception),
            "argument --cluster-id: expected one argument",
        )

    def test_missing_auth(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr disconnect --cluster-id j-3KMA44GZ4KWEJ --auth-type")
        self.assertEqual(
            str(e.exception),
            "argument --auth-type: expected one argument",
        )

    def test_unsupported_auth(self):
        with self.assertRaises(Exception) as e:
            _validate_emr_args(DummyInvalidAuthType(), "something", "IPython")
        self.assertTrue(
            str(e.exception).__contains__("Invalid auth type, supported auth types are")
        )

    def test_empty_command(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("")
        self.assertEqual(
            str(e.exception),
            "Please provide service name and operation to perform. Please look at usage of %sm_analytics by executing "
            "`%sm_analytics?`.",
        )

    def test_blank_command(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(" ")
        self.assertEqual(
            str(e.exception),
            "Please provide service name and operation to perform. Please look at usage of %sm_analytics by executing "
            "`%sm_analytics?`.",
        )

    def test_more_than_needed(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr connect connect")
        self.assertEqual(
            str(e.exception),
            "Please provide service name and operation to perform. Please look at usage of %sm_analytics by executing "
            "`%sm_analytics?`.",
        )

    def test_unrecognized_argument_cluster_id_usage_error(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(UsageError) as e:
            sm.sm_analytics("emr connect --clusterid")
        self.assertEqual(
            str(e.exception),
            "unrecognized arguments: --clusterid",
        )

    def test_unrecognized_argument_auth_type_usage_error(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(UsageError) as e:
            sm.sm_analytics("emr connect --cluster-id xyz --authtype")
        self.assertEqual(
            str(e.exception),
            "unrecognized arguments: --authtype",
        )

    def test_unrecognized_argument_random_usage_error(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(UsageError) as e:
            sm.sm_analytics(
                "emr connect --cluster-id xyz --auth-type None --something_else"
            )
        self.assertEqual(
            str(e.exception),
            "unrecognized arguments: --something_else",
        )

    def test_invalid_language_none(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr connect --cluster-id xyz --auth-type None --language")
        self.assertEqual(
            str(e.exception),
            "argument --language: expected one argument",
        )

    def test_language_not_required_for_pyspark_kernel(self):
        _validate_emr_args(DummyValidPySpark(), "something", "PySpark")

    def test_language_required_for_ipython_kernel(self):
        with self.assertRaises(MissingParametersError) as e:
            _validate_emr_args(
                DummyMissingLanguageIPython(),
                usage="something",
                kernel_name="IPythonKernel",
            )
        self.assertEqual(
            "Missing required argument '--language' for IPython kernel. something",
            str(e.exception),
        )

    def test_missing_cluster_id_argument(self):
        with self.assertRaises(MissingParametersError) as e:
            _validate_emr_args(
                DummyMissingClusterId(), usage="something", kernel_name="IPython"
            )
        self.assertEqual(
            "Missing required argument '--cluster-id'. something",
            str(e.exception),
        )

    def test_missing_auth_type(self):
        with self.assertRaises(MissingParametersError) as e:
            _validate_emr_args(
                DummyMissingAuthTypeArgs(), usage="something", kernel_name="IPython"
            )
        self.assertEqual(
            "Missing required argument '--auth-type'. something",
            str(e.exception),
        )

    _incorrect_iam_role_arn_list = [
        (
            "foobar",
            "ARNs must be of the form arn:partition:service:region:accountId:resource",
        ),
        ("x:aws:iam::accid:role/roleId", "ARNs must start with `arn`"),
        ("arn::iam::accid:role/roleId", "Partition must be non-empty."),
        ("arn:aws:::accid:role/roleId", "Service must be non-empty."),
        ("arn:aws:iam::accid:", "Resource must be non-empty."),
        (
            "arn:aws:abc::accid:role/roleId",
            "Incorrect Role ARN. Provided service abc does not match expected service `iam`",
        ),
        (
            "arn:aws:iam::accid:foo/roleId",
            "Incorrect Role ARN. Provided resource foo/roleId does not correspond to expected resource `role`",
        ),
        (
            "arn:pqr:iam::accid:role/roleId",
            "Invalid partition: pqr",
        ),
        (
            "arn:aws:iam::accid:" + "x" * 2048,
            "ARN size must not exceed 2048 character limit.",
        ),
    ]

    def test_incorrect_assumable_arn(self):
        for command, expected_exception_string in self._incorrect_iam_role_arn_list:
            with self.subTest():
                with self.assertRaises(Exception) as e:
                    _validate_emr_args(
                        DummyAssumableRoleArnValidation(command),
                        usage="something",
                        kernel_name="IPython",
                    )
                self.assertEqual(expected_exception_string, str(e.exception))

    def test_incorrect_emr_execution_arn(self):
        for command, expected_exception_string in self._incorrect_iam_role_arn_list:
            with self.subTest():
                with self.assertRaises(Exception) as e:
                    _validate_emr_args(
                        DummyEmrExecutionRoleArnValidation(command),
                        usage="something",
                        kernel_name="IPython",
                    )
                self.assertEqual(expected_exception_string, str(e.exception))
