from hypothesis import given
from hypothesis import strategies as st

from bharat_equity.infrastructure.storage import canonical_json, content_hash


@given(st.dictionaries(st.text(min_size=1, max_size=12), st.integers(), max_size=10))
def test_canonical_hash_is_deterministic_under_key_order(payload: dict[str, int]) -> None:
    reversed_payload = dict(reversed(list(payload.items())))
    assert canonical_json(payload) == canonical_json(reversed_payload)
    assert content_hash(payload) == content_hash(reversed_payload)
