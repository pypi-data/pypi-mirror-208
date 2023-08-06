from time import time
from typing import Any, Dict, Tuple

from loguru import logger


logger.level("Time", no=42, icon="⌛", color="<magenta>")


def timeit(function: object) -> callable:
    """
    Calculates the time taken by the function to run.

    Args:
        function: Object of the function whose running time is to calculated.

    Returns: Any object.

    """

    # Defined a wrapper function which acts as the dummy function when the actual function is called.
    def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        logger.info(f"Entering function {function.__name__}.")
        tic = time()
        results = function(*args, **kwargs)
        toc = time()
        elapsed_time = toc - tic
        logger.log(
            "Time", f"Function {function.__name__} ran for {elapsed_time} seconds.")
        logger.info(f"Exiting function {function.__name__}")
        return results

    return wrapper
