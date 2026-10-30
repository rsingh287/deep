def slug_generator(text: str = '') -> str:
    import re
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).lower().strip('-')
