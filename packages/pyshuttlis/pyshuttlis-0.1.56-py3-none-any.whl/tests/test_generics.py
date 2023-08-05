import pytest

from shuttlis.generics import Window


class TestWindow:
    def test_sorts_by_start_time(self):
        windows = [Window(5, 10), Window(10, 20), Window(6, 24)]
        assert [Window(5, 10), Window(6, 24), Window(10, 20)] == sorted(windows)

    def test_sorts_by_end_time_if_start_time_same(self):
        windows = [Window(5, 11), Window(10, 20), Window(5, 10)]
        assert [Window(5, 10), Window(5, 11), Window(10, 20)] == sorted(windows)

    def test_raises_error_if_start_greater_than_end(self):
        with pytest.raises(AssertionError):
            Window(11, 5)

    def test_works_if_start_is_equal_to_end(self):
        assert Window(5, 5)

    def test_works_if_start_is_same_as_end(self):
        assert Window(5, 6)
