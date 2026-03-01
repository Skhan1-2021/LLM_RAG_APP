import pytest

from app.text_utils import split_text


def test_split_text_makes_multiple_chunks() -> None:
    text = "abc " * 600
    chunks = split_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    assert all(chunks)


def test_split_text_validates_overlap() -> None:
    with pytest.raises(ValueError):
        split_text("hello", chunk_size=50, overlap=50)
