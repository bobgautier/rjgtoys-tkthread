"""
Tests for EventGenerator.
"""

import pytest
from unittest.mock import Mock, patch, call

from rjgtoys.tkthread import EventGenerator

from helpers import get_open_files, widget

def test_eg_puts():

    generator = iter(('item1', 'item2'))

    handler = Mock()

    mock_queue = Mock()

    mock_event_queue = Mock(return_value=mock_queue)

    with patch('rjgtoys.tkthread.EventQueue', mock_event_queue):
        g = EventGenerator(widget='mock_widget', handler=handler, generator=generator)

    # While we're here, check the name
    assert g.name.startswith('EventGenerator-')

    # Did the queue get built as expected?

    mock_event_queue.assert_called_once_with(widget='mock_widget', handler=handler, maxsize=0)

    # Did the events get sent to the queue?

    mock_queue.put.assert_has_calls(
        [
            call('item1'),
            call('item2')
        ]
    )


def test_eg_does_not_leak_pipes(widget):

    generator = iter(('item1', 'item2'))

    def handler(e):
        raise Exception("Should never be called")

    before = get_open_files()

    with EventGenerator(widget=widget, generator=generator, handler=handler) as q:
        pass

    after = get_open_files()

    assert before == after
