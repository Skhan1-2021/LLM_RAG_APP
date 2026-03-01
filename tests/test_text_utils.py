from app.text_utils import chunk_id


def test_chunk_id_is_stable_and_unique_for_index() -> None:
    first = chunk_id(source="a", idx=0, chunk="hello")
    second = chunk_id(source="a", idx=0, chunk="hello")
    third = chunk_id(source="a", idx=1, chunk="hello")

    assert first == second
    assert first != third
