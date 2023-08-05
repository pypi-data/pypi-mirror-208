"""
Token plugins can be used to handle specific edge
"""


def tokenize(hub, text: str, **kwargs) -> str:
    # iterate over "token" plugins and handle each unique edge case
    for plugin in hub.token._loaded:
        if plugin == "init":
            continue
        hub.log.debug(f"Passing text through tokenizer plugin {plugin}")
        text = hub.token[plugin].tokenize(text, **kwargs)

    return text
