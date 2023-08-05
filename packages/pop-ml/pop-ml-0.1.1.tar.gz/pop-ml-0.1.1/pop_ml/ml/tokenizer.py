from typing import List

import transformers


def __init__(hub):
    hub.ml.MODEL_NAME = None
    hub.ml.MODEL = None
    hub.ml.TOKENIZER = None


def init(
    hub,
    model_name: str = None,
    dest_lang: str = None,
    source_lang: str = None,
    pretrained_model: str = None,
    pretrained_tokenizer: str = None,
):
    """
    Idempotently initialize the global model and tokenizer
    """
    if hub.ml.MODEL_NAME and hub.ml.MODEL and hub.ml.TOKENIZER:
        # Global initialization is already complete
        return

    ret = hub.ml.tokenizer.get(
        model_name=model_name,
        source_lang=source_lang,
        dest_lang=dest_lang,
        pretrained_model=pretrained_model,
        pretrained_tokenizer=pretrained_tokenizer,
    )

    if hub.ml.MODEL_NAME is None:
        hub.ml.MODEL_NAME = ret.model_name

    if hub.ml.MODEL is None:
        hub.ml.MODEL = ret.model

    if hub.ml.TOKENIZER is None:
        hub.ml.TOKENIZER = ret.tokenizer


def get(
    hub,
    model_name: str = None,
    dest_lang: str = None,
    source_lang: str = None,
    pretrained_model: str = None,
    pretrained_tokenizer: str = None,
):
    """
    Get a tokenizer based on the given parameters and return it
    """
    if model_name is None and not (source_lang and dest_lang):
        # Use the global model name
        model_name = hub.ml.MODEL_NAME
    elif not (source_lang and dest_lang):
        raise ValueError(f"Both a source_lang and dest_lang must be specified")
    else:
        # Use the default Hugging Face translation model using the given source and dest languages
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{dest_lang}"

    hub.log.debug(f"Using model: {model_name}")

    model = getattr(hub.lib.transformers, pretrained_model).from_pretrained(model_name)
    hub.log.debug(f"Initialized pretrained model: {model}")

    tokenizer = getattr(hub.lib.transformers, pretrained_tokenizer)

    hub.log.debug(f"Initialized pretrained tokenizer: {tokenizer}")

    # Wrap the given tokenizer class with our own class that will use plugins to handle custom cases
    class POPMLTokenizer(tokenizer):
        def tokenize(self, text, **kwargs):
            # Pass the text through the tokenizing plugins
            text: str = hub.token.init.tokenize(text, **kwargs)

            # Lastly, use the main tokenizer class
            hub.log.debug(f"Passing text through the primary tokenizer {tokenizer}")
            text: List[str] = super().tokenize(text, **kwargs)
            return text

    custom_tokenizer = POPMLTokenizer.from_pretrained(model_name)

    return hub.lib.dtd.NamespaceDict(
        model=model,
        model_name=model_name,
        tokenizer=custom_tokenizer,
    )


def translate(
    hub,
    texts: List[str],
    model: transformers.PreTrainedModel = None,
    tokenizer: transformers.PreTrainedTokenizerBase = None,
) -> List[str]:
    """
    Translate the list of strings and return the result
    """
    if tokenizer is None:
        tokenizer = hub.ml.TOKENIZER

    if tokenizer is None:
        raise RuntimeError(
            "Tokenizer has not been initialized, please call hub.ml.tokenizer.init(<source_lang>, <dest_lang>)"
        )

    hub.log.debug(f"Generating tokens using {tokenizer.__class__.__name__}")
    tokens = tokenizer(list(texts), return_tensors="pt", padding=True)

    if model is None:
        model = hub.ml.MODEL

    if model is None:
        raise RuntimeError(
            "Model has not been initialized, please call hub.ml.tokenizer.init(<source_lang>, <dest_lang>)"
        )

    hub.log.debug(f"Generating translation tokens using {model.__class__.__name__}")
    translate_tokens = hub.ml.MODEL.generate(**tokens)

    # TODO Can we pass in more special tokens?
    result = [tokenizer.decode(t, skip_special_tokens=True) for t in translate_tokens]

    return result
