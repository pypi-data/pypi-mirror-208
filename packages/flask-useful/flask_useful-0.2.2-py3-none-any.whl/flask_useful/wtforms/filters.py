def trim(s, chars=None):
    """
    To remove other characters when used as a filter for form fields, you can use `functools.partial`.

    Example:
        from functools import partial

        StringField(filters=[partial(trim, chars='/')])
    """
    return s.strip(chars) if isinstance(s, str) else None
