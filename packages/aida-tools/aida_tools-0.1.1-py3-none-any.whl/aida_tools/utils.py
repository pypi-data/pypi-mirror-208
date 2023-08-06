from typing import Any, Dict, Union
import uuid

def safe_replace(item: Any, obj: Dict) -> Union[Any, None]:
    """Replaces a values with the one in the dictionary

    It is a shortcut for the following code:

    .. code-block:: python

        return_value = x if item == y else None

    Parameters
    ----------
    item : Any
        The item to replace
    obj : Dict
        The dictionary to use
    
    Returns
    -------
    Union[Any, None]
        The replaced value or None if not found

    Examples
    --------
    >>> safe_replace("a", {"a": "b"})
    "b"
    >>> safe_replace("c", {"a": "b"})
    None

    """
    return obj.get(item, None)

def generate_id() -> str:
    return str(uuid.uuid4()).split('-')[0]