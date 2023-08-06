import logging

import pytest

from gantry.applications.llm_utils import _get_prompt_inputs, fill_prompt


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("no vars", []),
        ("{{test}} variable", ["test"]),
        ("{{two}} {{vars}}", ["two", "vars"]),
        ("{not} a {variable}", []),
        ("{{test}} {{test}}", ["test"]),
    ],
)
def test_get_prompt_inputs(prompt, expected):
    assert set(_get_prompt_inputs(prompt)) == set(expected)


@pytest.mark.parametrize(
    ("prompt", "values", "expected"),
    [
        ("no vars", {}, "no vars"),
        ("{{test}} variable", {"test": "filled"}, "filled variable"),
        ("{{two}} {{vars}}", {"two": "2", "vars": "variables"}, "2 variables"),
        ("{{unfilled}} var", {}, "{{unfilled}} var"),
        ("{{test}} {{test}}", {"test": "filled"}, "filled filled"),
        ("{{extra}} fields", {"extra": "filled", "unused": "unused"}, "filled fields"),
    ],
)
def test_fill_prompt(prompt, values, expected):
    assert fill_prompt(prompt, values) == expected


@pytest.mark.parametrize(
    ("prompt", "values", "strict", "expected_error"),
    [
        ("{{test}} variable", {}, False, "warn"),
        ("{{test}} variable", {}, True, "error"),
        ("test variable", {"test": "foo"}, False, "warn"),
        ("test variable", {"test": "foo"}, True, "error"),
        ("{{test}} variable", {"test": "foo"}, True, None),
        ("{{test}} variable", {"test": "foo"}, False, None),
    ],
)
def test_fill_prompt_errors_or_warnings(prompt, values, strict, expected_error, caplog):
    if expected_error is None:
        with caplog.at_level(logging.WARNING):
            fill_prompt(prompt, values, strict=strict)
        assert not caplog.text
    elif expected_error == "warn":
        with caplog.at_level(logging.WARNING):
            fill_prompt(prompt, values, strict=strict)
        assert "was not fully filled" in caplog.text
    elif expected_error == "error":
        with pytest.raises(ValueError):
            fill_prompt(prompt, values, strict=strict)


@pytest.mark.parametrize(
    ("prompt", "values", "message"),
    [
        (
            "{{a}} b",
            {},
            "Prompt '{{a}} b' was not fully filled. Unused keys: []. Unfilled keys: ['a'].",
        ),
        (
            "a",
            {"a": "b"},
            "Prompt 'a' was not fully filled. Unused keys: ['a']. Unfilled keys: [].",
        ),
    ],
)
def test_fill_prompt_correct_error_message(prompt, values, message, caplog):
    with caplog.at_level(logging.WARNING):
        fill_prompt(prompt, values)
    assert message in caplog.text
