def sig_tokenize(hub, text: str, **kwargs) -> str:
    return text


def post_tokenize(hub, ctx):
    if not ctx.ret:
        raise ValueError("Tokenizer did not return text")
    return ctx.ret


# TODO We may also need a way to de-tokenize each plugin
# def sig_detokenize()
