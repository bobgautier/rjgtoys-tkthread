"""
Tests for the EventQueue

"""

import os
from unittest.mock import Mock, patch, call

import tkinter as tk

import pytest

from rjgtoys.tkthread import EventQueue

from helpers import get_open_files, widget

PIPE_R = 'pipe_r'   # NB: deliberately not even an integer
PIPE_W = 'pipe_w'

@pytest.fixture
def mock_pipe():
    with patch('rjgtoys.tkthread.os.pipe', return_value=(PIPE_R, PIPE_W)) as p:
        yield p

@pytest.fixture
def mock_close():
    with patch('rjgtoys.tkthread.os.close', return_value=0) as p:
        yield p

@pytest.fixture
def mock_close_failing():
    with patch('rjgtoys.tkthread.os.close', side_effect=OSError('os.close fails')) as p:
        yield p

@pytest.fixture
def mock_read():

    def _os_read(fd, nb):
        assert fd == PIPE_R
        assert nb == 1

    with patch('rjgtoys.tkthread.os.read', _os_read) as p:
        yield p

@pytest.fixture
def mock_write():

    def _os_write(fd, buff):
        assert fd == PIPE_W

    with patch('rjgtoys.tkthread.os.write', _os_write) as p:
        yield p

def assert_widget_has_handler(widget, handler):

    widget.tk.createfilehandler.assert_called_once_with(PIPE_R, tk.READABLE, handler)

def test_eq_delivers(widget, mock_pipe, mock_write, mock_read):

    handled = []

    def handle_event(event):
        handled.append(event)

    q = EventQueue(widget, handle_event)

    assert_widget_has_handler(widget, q._readable)

    q.put('event1')
    q.put_nowait('event2')  # Other entry point, just for coverage

    assert q.qsize() == 2

    # Each 'handler' activation should eat one event

    q._readable(None, None)

    assert q.qsize() == 1

    q._readable(None, None)

    assert q.qsize() == 0

    # Calling the handler with an empty queue is not a problem

    q._readable(None, None)

    assert handled == ['event1', 'event2']


def test_eq_delivers_when_handler_raises(widget, mock_pipe, mock_write, mock_read):

    handled = []

    def handle_event(event):
        handled.append(event)
        raise Exception("Could not handle %s" % (event))

    q = EventQueue(widget, handle_event)

    assert_widget_has_handler(widget, q._readable)

    q.put('event1')
    q.put_nowait('event2')  # Other entry point, just for coverage

    assert q.qsize() == 2

    # Each 'handler' activation should eat one event

    q._readable(None, None)

    assert q.qsize() == 1

    q._readable(None, None)

    assert q.qsize() == 0

    # Calling the handler with an empty queue is not a problem

    q._readable(None, None)

    assert handled == ['event1', 'event2']



def test_eq_shutdown_does_not_leak_pipes(widget):

    def handler(e):
        raise Exception("Should never be called")

    before = get_open_files()

    q = EventQueue(widget, handler)

    q.drain()

    after = get_open_files()

    assert before == after


def test_eq_context_does_not_leak_pipes(widget):

    def handler(e):
        raise Exception("Should never be called")

    before = get_open_files()

    with EventQueue(widget, handler) as q:
        pass

    after = get_open_files()

    assert before == after

def test_eq_drain_handles_exception(widget, mock_close_failing):

    # Test the fixture

    with pytest.raises(Exception):
        mock_close_failing('foo')

    def handler(e):
        raise Exception("Should never be called")

    with EventQueue(widget, handler) as q:
        pass

    # Ensure that both calls were made, despite the exception

    mock_close_failing.assert_has_calls(
        [
            call(q._pipe_r),
            call(q._pipe_w)
        ]
    )
