"""This module contains the implementation of CodeGrade's pytest reporter plugin
for use in AutoTest v2.

The plugin is automatically enabled, but can be disabled by running pytest with
the following command line flags:

    pytest -p no:cg-pytest-reporter
"""
import json
import typing as t
import logging
import dataclasses

import pytest
import _pytest.nodes
from _pytest.junitxml import mangle_test_address

logger = logging.getLogger('cg_pytest_reporter')


def json_dumps(obj: object) -> str:
    """Dump an object to JSON without any extra formatting.
    """
    # Make sure only ASCII characters are used so that the string length as
    # python's `len` function reports it is equal to the string's byte length.
    # Do not insert spaces after each separator.
    return json.dumps(obj, ensure_ascii=True, separators=(',', ':'))


class MessageTooLargeException(Exception):
    """This exception is raised when the required fields of the message combined
    are too large.
    """


# The actual limit is 256KB (TODO: Is it?) so set it a bit lower to make sure
# there is enough space left for the wrapping message.
MESSAGE_SIZE_LIMIT = 250_000

PyTestCaseStatus = t.Literal['passed', 'failed', 'skipped']
CgTestCaseStatus = t.Literal['success', 'failure', 'skipped']

# Mapping from the status used by pytest to the status used by CodeGrade.
STATUS_NAME_MAP: t.Mapping[PyTestCaseStatus, CgTestCaseStatus] = {
    'passed': 'success',
    'failed': 'failure',
    'skipped': 'skipped',
}


class _TestCaseResultReq(t.TypedDict):
    """The required properties of a test case result.
    """
    #: The name of the test case.
    name: str
    #: The result of the test case.
    status: CgTestCaseStatus


class TestCaseResult(_TestCaseResultReq, total=False):
    """The optional properties of a test case result.
    """
    #: The description of the test case.
    description: str
    #: The weight of the test case.
    weight: float
    #: The reason the test case failed or was skipped.
    reason: str
    #: The stdout produced by the test case.
    stdout: str
    #: The stderr produced by the test case.
    stderr: str


class _TestSuiteResultReq(t.TypedDict):
    """The required properties of a test suite result.
    """
    #: The id of this suite. Test cases within the same file
    #: are in the same suite.
    id: str
    #: The file name of the test that was run.
    name: str
    #: The results of the test cases in this suite.
    testCases: t.List[TestCaseResult]


class TestSuiteResult(_TestSuiteResultReq, total=False):
    """The optional properties of a test suite result.
    """
    #: The weight of the test suite.
    weight: float


class UnitTestMessage(t.TypedDict):
    """The message to be sent for each test case.
    """
    #: Message tag.
    tag: t.Literal['unit-test']
    #: The test results.
    results: t.List[TestSuiteResult]


@dataclasses.dataclass
class CgMarks:
    """Marks set on each test case by the `cg-pytest-reporter` plugin used when
    generating the report.
    """
    #: The name of the test suite.
    suite_name: str | None
    #: The weight of the test suite.
    suite_weight: int | float | None

    #: The name of the test case.
    name: str | None
    #: The description of the test case.
    description: str | None
    #: The weight of the test case.
    weight: int | float | None
    #: The reason the test failed.
    reason: str | None
    #: The stdout produced while running the test.
    hide_stdout: bool
    #: The stderr produced while running the test.
    hide_stderr: bool

    @classmethod
    def from_item(cls, item: pytest.Item) -> 'CgMarks':
        """Get the CodeGrade marks from the given item.

        :param item: The item to get the marks from.
        :returns: A new `CgMarks` instance.
        """
        return CgMarks(
            suite_name=cls._as_str(
                cls._get_suite_mark_value(item, 'cg_suite_name')
            ),
            suite_weight=cls._as_num(
                cls._get_suite_mark_value(item, 'cg_suite_weight')
            ),
            name=cls._as_str(cls._get_mark_value(item, 'cg_name')),
            description=cls._as_str(
                cls._get_mark_value(item, 'cg_description')
            ),
            weight=cls._as_num(cls._get_mark_value(item, 'cg_weight')),
            reason=cls._as_str(cls._get_mark_value(item, 'cg_reason')),
            hide_stdout=item.get_closest_marker('cg_hide_stdout') is not None,
            hide_stderr=item.get_closest_marker('cg_hide_stderr') is not None,
        )

    @classmethod
    def _get_suite_mark_value(
        cls,
        item: pytest.Item,
        name: str,
    ) -> object | None:
        # It is not possible to add marks on the module level because you cannot
        # call a decorator on a module. So on the module level we allow a custom
        # name and weight by setting the `__cg_suite_{name,weight}__` variables
        # at the top level of the module.
        if isinstance(item.parent, pytest.Module):
            # Pytest offers no way to get the module object from a `Module` node.
            # pylint: disable=protected-access
            return getattr(item.parent._obj, f'__{name}__', None)
        else:
            return cls._get_mark_value(item.parent, name)

    @classmethod
    def _get_mark_value(
        cls,
        item: _pytest.nodes.Node | None,
        name: str,
    ) -> object | None:
        if item is None:
            return None
        mark: pytest.Mark | None = item.get_closest_marker(name)
        if mark is None or not mark.args:
            return None
        return mark.args[0]

    @staticmethod
    def _as_str(obj: object) -> str | None:
        if isinstance(obj, str):
            return obj
        return None

    @staticmethod
    def _as_num(obj: object) -> float | int | None:
        if isinstance(obj, (int, float)):
            return obj
        return None


class CGPytestReporterPlugin:
    """Implementation of the reporter plugin.

    This uses the file descriptor set with the `--cg-pytest-fd` command line
    flag to open it as a writable stream.

    This intercepts the `pytest_runtest_makereport` hook to get all the marks
    that were set on a test item, which is necessary because the value of those
    marks is no longer retrievable in the `pytest_runtest_logreport` call.

    This also has a `pytest_runtest_logreport` hook that will actually write the
    report to the given file descriptor.
    """

    _config: pytest.Config
    _fd: int
    _file: t.BinaryIO

    def __init__(self, config: pytest.Config) -> None:
        self._config = config

        fd = config.getoption('--cg-pytest-fd', default=None)
        if fd is None:
            self._fd = 1
        else:
            assert isinstance(fd, int)
            self._fd = fd

        # NOTE: This "file" is never closed, as that will close the underlying
        # file descriptor, preventing it to be used for other purposes in this
        # process.
        # We cannot use `with open(...)` here because the opened file needs to
        # remain open after this function.
        # pylint: disable=consider-using-with
        self._file = open(self._fd, 'wb', buffering=0)

    @staticmethod
    def pytest_runtest_makereport(
        item: pytest.Item,
        call: pytest.CallInfo[None],
    ) -> pytest.TestReport:
        """Create the report for logging.

        This hook must return a `pytest.TestReport`, but that class is marked
        `@final` so we are not allowed to subclass it.

        :param item: The item to generate a report for.
        :param call: The result of the test function invocation.
        :returns: A report for the test that was run, including an extra
            `_cg_marks` attribute to make it possible to retrieve the mark
            values in the `pytest_runtest_logreport` hook.
        """
        report = pytest.TestReport.from_item_and_call(item, call)
        # `TestReport` has no property `_cg_marks`...
        # pylint: disable=protected-access
        report._cg_marks = CgMarks.from_item(item)  # type: ignore
        return report

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Write the report to the given file descriptor.

        :param report: The report to write.
        :returns: Nothing.
        """
        # This hook is called multiple times for each test. For tests that are
        # not skipped the report contains the information we need during the
        # "call" phase.
        if report.when == 'call':
            self._send_message(report)

        # Because a skipped test is never ran, we never get a message for it
        # during the "call" phase but we do get a message for it during the
        # "setup" phase.
        if report.when == 'setup' and report.outcome == 'skipped':
            self._send_message(report)

    def _send_message(self, report: pytest.TestReport) -> None:
        message: UnitTestMessage = {
            'tag': 'unit-test',
            'results': [self._mk_test_suite(report)],
        }

        data = json_dumps(message) + '\n'
        if len(data) > MESSAGE_SIZE_LIMIT:
            self._limit_message_size(message)
            data = json_dumps(message) + '\n'

        self._file.write(data.encode('utf8'))

    def _mk_test_suite(self, report: pytest.TestReport) -> TestSuiteResult:
        *suite_name_parts, case_name = mangle_test_address(report.nodeid)
        suite_name = '.'.join(suite_name_parts)

        test_suite: TestSuiteResult = {
            'id': suite_name,
            'name': suite_name,
            'testCases': [self._mk_test_case(case_name, report)],
        }

        # pylint: disable=protected-access
        marks = t.cast(CgMarks, report._cg_marks)

        if marks.suite_name is not None:
            test_suite['id'] = test_suite['name'] = marks.suite_name
        if marks.suite_weight is not None:
            test_suite['weight'] = float(marks.suite_weight)

        return test_suite

    @staticmethod
    def _mk_test_case(name: str, report: pytest.TestReport) -> TestCaseResult:
        status = STATUS_NAME_MAP[report.outcome]

        test_case: TestCaseResult = {
            'name': name,
            'status': status,
        }

        # pylint: disable=protected-access
        marks = t.cast(CgMarks, report._cg_marks)

        if marks.name is not None:
            test_case['name'] = marks.name
        if marks.description is not None:
            test_case['description'] = marks.description
        if marks.weight is not None:
            test_case['weight'] = float(marks.weight)

        if marks.reason is not None:
            test_case['reason'] = marks.reason
        elif report.longrepr is None:
            pass
        else:
            longrepr = report.longrepr
            # Long repr is an annoyingly big `t.Union`...
            if isinstance(longrepr, tuple):
                # If it is a tuple it has 3 elements: a path, a line number, and
                # the actual reason.
                reason = longrepr[2]
            else:
                reason = report.longreprtext
            test_case['reason'] = reason

        # if status == 'failure':
        if report.capstdout and not marks.hide_stdout:
            test_case['stdout'] = report.capstdout
        if report.capstderr and not marks.hide_stderr:
            test_case['stderr'] = report.capstderr

        return test_case

    @staticmethod
    def _limit_message_size(message: UnitTestMessage) -> None:
        """Edits the message in place to ensure it will not be dropped.

        If all of the following fields do not fit, an exception is raised. All
        of these fields, except for case status which is already very limited in
        the size it needs, are directly controlled by the teacher.

        - Suite id, name, and weight
        - Case name, status, description, and weight

        The other fields (case reason, stdout, and stderr) are trimmed down to
        fit. First the reason is tried, as that is most likely to contain
        information useful for the student to figure out what went wrong. After
        that the smaller one of stdout and stderr is included, and finally the
        other one as well.
        """
        def jsonlen(obj: object) -> int:
            return len(json_dumps(obj))

        def field_length(
            dct: t.Mapping[str, object], field: str
        ) -> int | None:
            val = dct.get(field)
            if val is None:
                return None

            length = len(f'"{field}":')
            if isinstance(val, str):
                # Add 2 for the quotes.
                length += 2
            length += jsonlen(val)
            return length

        def trim(string: str, maxlen: int) -> str:
            nbytes = maxlen
            while jsonlen(trimmed := f'{string[:nbytes - 1]}…') > maxlen:
                nbytes = int(0.95 * nbytes)
            return trimmed

        test_suite = message['results'][0]
        test_case = test_suite['testCases'][0]

        limit = MESSAGE_SIZE_LIMIT
        # Length of a comma.
        comma = 1

        # First reduce the limit by the amount of space needed for required
        # fields, starting with the top level message.
        limit -= len('{"tag":"unit-test","results":[]}')

        # Then also the required fields of a suite.
        limit -= len('{"id":"","name":"","testCases":[]}')
        # The id and name fields are the same so don't dump them twice.
        limit -= 2 * jsonlen(test_suite['name'])
        if (length := field_length(test_suite, 'weight')) is not None:
            limit -= length + comma

        # Here we remove
        limit -= sum(
            length for length in [
                len('{}'),
                field_length(test_case, 'name'),
                comma,
                field_length(test_case, 'status'),
            ] if length is not None
        )
        if (length := field_length(test_case, 'weight')) is not None:
            limit -= length + comma
        if (length := field_length(test_case, 'description')) is not None:
            limit -= length + comma

        # All fields so far are the same for each test run and can be directly
        # configured by the teacher, so just crash if they do not fit.
        if limit < 0:
            raise MessageTooLargeException(
                'cg_pytest_reporter: message too large, it is larger than'
                f' {MESSAGE_SIZE_LIMIT} bytes. Please adjust your test'
                ' configuration.'
            )

        # Always try to include the reason first. Then do stdout and stderr in
        # order of size (smaller first), to increase the likelihood that both
        # will be included.
        optional_fields: t.List[t.Literal['reason', 'stdout', 'stderr']]
        optional_fields = ['reason']
        if len(test_case.get('stdout', '')) > len(test_case.get('stderr', '')):
            optional_fields.extend(['stderr', 'stdout'])
        else:
            optional_fields.extend(['stdout', 'stderr'])

        for field in optional_fields:
            length = field_length(test_case, field)
            if length is None:
                continue
            if length > limit:
                logger.warning('Field %s too large', field)
                test_case[field] = trim(test_case[field], limit - comma)
                return
            limit -= length

        # This should not happen, but let's warn users if it does.
        if limit < 0:
            logger.warning(
                (
                    'Message might be too large and not be sent, please contact'
                    ' CodeGrade support.\n%s'
                ),
                json.dumps(message, indent=2),
            )


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the --cg-pytest-fd command line option.
    """
    group = parser.getgroup("terminal reporting", "report-log plugin options")
    group.addoption(
        "--cg-pytest-fd",
        type=int,
        action="store",
        metavar="file descriptor",
        default=None,
        help="File descriptor to write the results to.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Initialize the plugin.

    1. Register the plugin with Pytest's plugin manager.
    2. Configure the markers that are used by the plugin to prevent warnings
       being printed for them.
    """
    plugin = CGPytestReporterPlugin(config)
    config.pluginmanager.register(plugin, name='cg-pytest-reporter')

    config.addinivalue_line(
        'markers', 'cg_suite_name(str): Name of a test suite'
    )
    config.addinivalue_line(
        'markers', 'cg_suite_weight(float): Weight of a test suite'
    )

    config.addinivalue_line('markers', 'cg_name(str): Name of a test case')
    config.addinivalue_line(
        'markers', 'cg_description(str): Description of a test case'
    )
    config.addinivalue_line(
        'markers', 'cg_weight(float): Weight of a test case'
    )
    config.addinivalue_line(
        'markers', 'cg_reason(str): The reason a test case failed'
    )
    config.addinivalue_line(
        'markers',
        'cg_hide_stdout: Hide the stdout written while running this test'
    )
    config.addinivalue_line(
        'markers',
        'cg_hide_stderr: Hide the stderr written while running this test'
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    """Deregister the plugin.
    """
    config.pluginmanager.unregister(name='cg-pytest-reporter')
