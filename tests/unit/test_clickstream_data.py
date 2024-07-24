import pytest
from unittest.mock import patch
import random
import uuid
from datetime import datetime, timedelta
import sys
import os
import itertools

# Add the src directory to the system path to import the clickstream_simulation module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from clickstream_simulation import generate_random_timestamp, generate_random_event, simulate_clickstream_data

@pytest.fixture
def mock_datetime_now(monkeypatch):
    """Fixture to mock datetime.now() to return a fixed date."""
    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2023, 1, 2)

    # Patch the datetime class in the datetime module with our mock class
    monkeypatch.setattr('datetime.datetime', MockDatetime)

@pytest.fixture
def mock_uuid(monkeypatch):
    """Fixture to mock uuid.uuid4() to return a fixed UUID."""
    # Patch the uuid4 method in the uuid module to return a fixed UUID
    monkeypatch.setattr(uuid, 'uuid4', lambda: uuid.UUID('12345678123456781234567812345678'))

def test_generate_random_timestamp_normal_case():
    """Test the generate_random_timestamp function with normal case."""
    with patch('random.randint') as mock_randint:
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 2)
        mock_randint.return_value = 3600  # 1 hour in seconds
        result = generate_random_timestamp(start_date, end_date)
        expected_result = start_date + timedelta(seconds=3600)
        assert result == expected_result

def test_generate_random_timestamp_same_start_end():
    """Test the generate_random_timestamp function when start and end date are the same."""
    with patch('random.randint') as mock_randint:
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 1)
        mock_randint.return_value = 0
        result = generate_random_timestamp(start_date, end_date)
        assert result == start_date

def test_generate_random_timestamp_end_before_start():
    """Test the generate_random_timestamp function when end date is before start date."""
    start_date = datetime(2023, 1, 2)
    end_date = datetime(2023, 1, 1)
    with pytest.raises(ValueError):
        generate_random_timestamp(start_date, end_date)

def test_generate_random_event_structure():
    """Test the generate_random_event function structure."""
    with patch('random.choice') as mock_choice, patch('random.randint') as mock_randint:
        mock_choice.side_effect = itertools.cycle(["/home", "https://www.google.com", "page_view"])
        mock_randint.side_effect = itertools.cycle([5, 7, 43, 12])

        user_id = 1
        session_id = 'test-session-id'
        session_start = datetime(2023, 1, 1, 12, 0, 0)

        result = generate_random_event(user_id, session_id, session_start)
        assert result['page_url'] == "/home"
        assert result['referrer_url'] == "https://www.google.com"
        assert result['event_type'] == "page_view"
        assert 'timestamp' in result
        assert result['event_details']['scroll_depth'] == 43

def test_generate_random_event_values_cycle():
    """Test the generate_random_event function values cycle."""
    with patch('random.choice') as mock_choice, patch('random.randint') as mock_randint:
        mock_choice.side_effect = itertools.cycle(["/home", "https://www.google.com", "page_view"])
        mock_randint.side_effect = itertools.cycle([5, 7, 43, 12])

        user_id = 1
        session_id = 'test-session-id'
        session_start = datetime(2023, 1, 1, 12, 0, 0)

        generate_random_event(user_id, session_id, session_start)  # First event
        result = generate_random_event(user_id, session_id, session_start)  # Second event
        assert result['page_url'] == "/home"
        assert result['referrer_url'] == "https://www.google.com"
        assert result['event_type'] == "page_view"
        assert 'timestamp' in result
        assert result['event_details']['scroll_depth'] == 7

def test_simulate_clickstream_data_single_event(mock_datetime_now, mock_uuid):
    """Test the simulate_clickstream_data function with a single event."""
    with patch('random.choice') as mock_choice, patch('random.randint') as mock_randint:
        mock_choice.side_effect = itertools.cycle(["/home", "https://www.google.com", "page_view"])
        mock_randint.side_effect = itertools.cycle([10, 20, 30])

        data = simulate_clickstream_data(1, 1, 1)
        assert len(data) == 1
        assert data[0]['page_url'] == "/home"
        assert data[0]['referrer_url'] == "https://www.google.com"
        assert data[0]['event_type'] == "page_view"
        assert 'timestamp' in data[0]
        assert data[0]['event_details']['scroll_depth'] == 10

def test_simulate_clickstream_data_no_users(mock_datetime_now, mock_uuid):
    """Test the simulate_clickstream_data function with no users."""
    data = simulate_clickstream_data(0, 1, 1)
    assert len(data) == 0

def test_simulate_clickstream_data_no_sessions(mock_datetime_now, mock_uuid):
    """Test the simulate_clickstream_data function with no sessions per user."""
    data = simulate_clickstream_data(1, 0, 1)
    assert len(data) == 0

def test_simulate_clickstream_data_no_events(mock_datetime_now, mock_uuid):
    """Test the simulate_clickstream_data function with no events per session."""
    data = simulate_clickstream_data(1, 1, 0)
    assert len(data) == 0

def test_simulate_clickstream_data_large_dataset(mock_datetime_now, mock_uuid):
    """Test the simulate_clickstream_data function with a large dataset."""
    with patch('random.choice') as mock_choice, patch('random.randint') as mock_randint:
        mock_choice.side_effect = itertools.cycle(["/home", "https://www.google.com", "page_view"])
        mock_randint.side_effect = itertools.cycle([10, 20, 30])

        data = simulate_clickstream_data(20, 10, 5)
        assert len(data) == 1000  # 20 users * 10 sessions * 5 events
        assert data[5]['user_id'] == 1
        assert data[5]['session_id'] == str(uuid.UUID('12345678123456781234567812345678'))

