from typing import Iterator

import pytest

from toolforge_weld.utils import peek


@pytest.fixture
def iterator_with_data() -> Iterator[str]:
    def iterator():
        yield "first"
        yield "second"
        yield "third"

    return iterator()


def test_peek_data(iterator_with_data):
    first, all = peek(iterator_with_data)
    assert first == "first"
    assert list(all) == ["first", "second", "third"]
