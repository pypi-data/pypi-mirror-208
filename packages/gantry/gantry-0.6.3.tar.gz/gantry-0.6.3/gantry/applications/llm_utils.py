import logging
import re
from typing import List

logger = logging.getLogger(__name__)


PROMPT_INPUT_REGEX = re.compile(r"\{\{([^\}\{]+)\}\}")


def _get_prompt_inputs(prompt: str) -> List[str]:
    return list(set(re.findall(PROMPT_INPUT_REGEX, prompt)))  # unique list


def fill_prompt(prompt: str, values: dict, strict: bool = False) -> str:
    """
    Fills a prompt with values, returning the completed prompt.

    Example usage:

    .. code-block:: python

        fill_prompt(
            "This is a prompt template. {{input1}} {{input2}}",
            {"input1": "foo", "input2": "bar"},
        )

    Example output:

    .. code-block:: python

        "This is a prompt template. foo bar"



    Args:
        prompt (str): The prompt template to use for this version. Denote variables
            like this: `{{variable}}`
        values (dict): A key-value mapping of variable names to values. The values will
            be used to fill the prompt template.
        strict (bool): If True, raises a ValueError if the prompt is not fully filled.
            Otherwise, logs a warning. False by default.

    Returns:
        str: The filled prompt.
    """
    unused_keys = []

    for key, value in values.items():
        prompt, num_replaced = re.subn("{{" + key + "}}", value, prompt)
        if num_replaced == 0:
            unused_keys.append(key)

    unfilled_keys = _get_prompt_inputs(prompt)

    if unused_keys or unfilled_keys:
        error_message = (
            f"Prompt {prompt!r} was not fully filled. "
            f"Unused keys: {unused_keys}. "
            f"Unfilled keys: {unfilled_keys}."
        )

        if strict:
            raise ValueError(error_message)
        else:
            logger.warning(error_message)

    return prompt
