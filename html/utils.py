import re

def sanitize_string(content:str, extend_allowd_chars=False):
    """
    Remove all characters that are not whitelisted.

    Args:
        content (str): The string to sanitize.

    Returns:
        str: sanitized string.
    """
    pattern = r'a-zA-Z0-9_\-.' # RE pattern with whitelisted chars
    if extend_allowd_chars: pattern = r"a-zA-Z0-9_\-.\s"
    # Replace chars that aren't whitelisted
    sanitized_content = re.sub(f'[^{pattern}]', "", content)
    return sanitized_content