import logging
import os
import threading

import pytest

import picologging
from picologging import LogRecord


def test_logrecord_standard():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork bork bork", (), None
    )
    assert record.name == "hello"
    assert record.msg == "bork bork bork"
    assert record.levelno == logging.WARNING
    assert record.levelname == "WARNING"
    assert record.pathname == __file__
    assert record.module == "test_logrecord"
    assert record.filename == "test_logrecord.py"
    assert record.args == ()
    assert record.created


def test_logrecord_args():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork %s", ("boom"), None
    )
    assert record.name == "hello"
    assert record.msg == "bork %s"
    assert record.args == ("boom")
    assert record.message is None


def test_logrecord_getmessage_with_args():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork %s", ("boom"), None
    )
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"
    assert record.message == "bork boom"


def test_logrecord_getmessage_no_args():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork boom", (), None)
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"
    assert record.message == "bork boom"


def test_args_format_mismatch():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork boom %s %s", (0,), None
    )
    assert record.message is None
    with pytest.raises(TypeError):
        record.getMessage()


def test_args_len_mismatch():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork boom %s", (0, 1, 2), None
    )
    assert record.message is None
    with pytest.raises(TypeError):
        record.getMessage()


def test_no_args():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork boom", None, None)
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"


def test_no_args_and_format():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork %s", None, None)
    assert record.message is None
    assert record.getMessage() == "bork %s"
    assert record.message == "bork %s"


def test_logrecord_single_string_arg():
    record = LogRecord("", picologging.WARNING, "", 12, " %s", "\U000b6fb2", None)
    assert record.args == "\U000b6fb2"
    assert record.getMessage() == " \U000b6fb2"


def test_logrecord_single_empty_string_in_tuple_arg():
    record = LogRecord("", 0, "", 0, " %s", ("",), None)
    assert record.args == ("",)
    assert record.getMessage() == " "


def test_logrecord_single_dict_in_tuple_arg():
    record = LogRecord("", 0, "", 0, "%(key)s", ({"key": "val"},), None)
    assert record.args == {"key": "val"}
    assert record.getMessage() == "val"


def test_logrecord_nested_tuple_arg():
    record = LogRecord("", 0, "", 0, "%d %s", ((10, "bananas"),), None)
    assert record.args == ((10, "bananas"),)
    with pytest.raises(TypeError):
        record.getMessage()


def test_repr():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork %s", (0,), None)
    assert repr(record) == f"<LogRecord: hello, 30, {__file__}, 123, 'bork %s'>"


def test_mapping_dict():
    args = {
        "a": "b",
    }
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork %s", (args,), None
    )
    assert record.args == {"a": "b"}


def test_threading_info():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork", (), None)
    assert record.thread == threading.get_ident()
    assert record.threadName is None  # Not supported


def test_process_info():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork", (), None)
    assert record.process == os.getpid()
    assert record.processName is None  # Not supported


def test_logrecord_subclass():
    class DerivedLogRecord(LogRecord):
        pass

    record = DerivedLogRecord(
        "hello", logging.WARNING, __file__, 123, "bork boom", (), None
    )

    assert DerivedLogRecord.__base__ is LogRecord
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"
    assert record.message == "bork boom"

    handler = picologging.StreamHandler()
    handler.emit(record)
