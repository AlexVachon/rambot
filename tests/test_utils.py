# tests/test_utils.py
import pytest
from botasaurus.utils import read_json_file

def test_read_json_file():
    with pytest.mock.open() as m_open:
        m_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
        data = read_json_file("test.json")
        assert data == {"test": "data"}