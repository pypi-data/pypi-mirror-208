import functools
import inspect
import os
from _pytest._code.code import ExceptionInfo
import pytest
from helpers.driver_manager import logger

__all__ = [
    "mcmp_check",
    "equal",
    "not_equal",
    "is_",
    "is_not",
    "is_true",
    "is_false",
    "is_none",
    "is_not_none",
    "is_in",
    "is_not_in",
    "is_instance",
    "is_not_instance",
    "almost_equal",
    "not_almost_equal",
    "greater",
    "greater_equal",
    "less",
    "less_equal",
    "check_func",
]


_stop_on_fail = False
_failures = []
_msg = "Actual: {} | Expected: {}"
_aux_msg = ''


def clear_failures():
    global _failures
    _failures = []


def get_failures():
    return _failures


def set_log_message(actual, expected, field):
    global _aux_msg
    _aux_msg = ''
    if field:
        _aux_msg = f"{field} -> "
    _aux_msg = f"{_aux_msg}{_msg}"
    _aux_msg = _aux_msg.format(actual, expected)
    return _aux_msg


def set_stop_on_fail(stop_on_fail):
    global _stop_on_fail
    _stop_on_fail = stop_on_fail


def check_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        __tracebackhide__ = True
        try:
            func(*args, **kwds)
            logger.info(_aux_msg)
            return True
        except AssertionError as e:
            logger.error(_aux_msg)
            log_failure(e)
            if _stop_on_fail:
                raise e
            return False

    return wrapper


class AssertCheck():
    @check_func
    def equal(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a == b, _aux_msg


    @check_func
    def not_equal(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a != b, _aux_msg


    @check_func
    def is_(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a is b, _aux_msg


    @check_func
    def is_not(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a is not b, _aux_msg


    @check_func
    def is_true(self, x, field='', stop_on_fail=False):
        set_log_message(x, str(True),field)
        set_stop_on_fail(stop_on_fail)
        assert bool(x), _aux_msg


    @check_func
    def is_false(self, x, field='', stop_on_fail=False):
        set_log_message(x, str(False), field)
        set_stop_on_fail(stop_on_fail)
        assert not bool(x), _aux_msg


    @check_func
    def is_none(self, x, field='', stop_on_fail=False):
        set_log_message(x, 'None', field)
        set_stop_on_fail(stop_on_fail)
        assert x is None, _aux_msg

    @check_func
    def is_not_none(self, x, field='', stop_on_fail=False):
        set_log_message(x, 'not None', field)
        set_stop_on_fail(stop_on_fail)
        assert x is not None, _aux_msg


    @check_func
    def is_in(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a in b or b in a, _aux_msg
        

    @check_func
    def is_not_in(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a not in b, _aux_msg


    @check_func
    def is_instance(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert isinstance(a, b), _aux_msg


    @check_func
    def is_not_instance(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert not isinstance(a, b), _aux_msg


    @check_func
    def almost_equal(self, a, b, rel=None, abs=None, field='', stop_on_fail=False):
        """
        for rel and abs tolerance, see:
        See https://docs.pytest.org/en/latest/builtin.html#pytest.approx
        """
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a == pytest.approx(b, rel, abs), _aux_msg


    @check_func
    def not_almost_equal(self, a, b, rel=None, abs=None, field='', stop_on_fail=False):
        """
        for rel and abs tolerance, see:
        See https://docs.pytest.org/en/latest/builtin.html#pytest.approx
        """
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a != pytest.approx(b, rel, abs), _aux_msg


    @check_func
    def greater(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a > b, _aux_msg


    @check_func
    def greater_equal(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a >= b, _aux_msg


    @check_func
    def less(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a < b, _aux_msg


    @check_func
    def less_equal(self, a, b, field='', stop_on_fail=False):
        set_log_message(a, b, field)
        set_stop_on_fail(stop_on_fail)
        assert a <= b, _aux_msg


mcmp_check = AssertCheck()

def get_full_context(level):
    (_, filename, line, funcname, contextlist) = inspect.stack()[level][0:5]
    filename = os.path.relpath(filename)
    context = contextlist[0].strip()
    return (filename, line, funcname, context)


def log_failure(msg):
    __tracebackhide__ = True
    level = 3
    pseudo_trace = []
    func = ""
    while "test_" not in func:
        (file, line, func, context) = get_full_context(level)
        if "site-packages" in file:
            break
        line = "{}:{} in {}() -> {}".format(file, line, func, context)
        pseudo_trace.append(line)
        level += 1
    pseudo_trace_str = "\n".join(reversed(pseudo_trace))
    entry = "FAILURE: {}\n{}".format(msg if msg else "", pseudo_trace_str)
    _failures.append(entry)


def soft_assert_failures_report(report, call):
    failures = get_failures()
    clear_failures()

    if failures:
        summary = "Failed Checks: {}".format(len(failures))
        longrepr = ["\n".join(failures)]
        longrepr.append("-" * 60)
        longrepr.append(summary)

        if report.longrepr:
            longrepr.append("-" * 60)
            longrepr.append(report.longreprtext)
            report.longrepr = "\n".join(longrepr)
        else:
            report.longrepr = "\n".join(longrepr)
        report.outcome = "failed"
        try:
            raise AssertionError(report.longrepr)
        except AssertionError:
             excinfo = ExceptionInfo.from_current()
        call.excinfo = excinfo

    
