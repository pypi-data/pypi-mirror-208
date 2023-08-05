def __init__(hub):
    # Perform python imports for the whole project
    hub.pop.sub.add(dyne_name="lib")
    hub.pop.sub.add(python_import="transformers", sub=hub.lib)
    hub.pop.sub.add(python_import="dict_tools.data", sub=hub.lib, subname="dtd")

    # Add subsystems that are used by pop_ml
    hub.pop.sub.add(dyne_name="config")
    hub.pop.sub.add(dyne_name="token")

    # Ensure that pop_ml is always loaded onto the config
    hub.config.LOAD.append("pop_ml")


def cli(hub):
    hub.pop.config.load(hub.config.LOAD, cli="pop_ml")

    hub.pop.loop.create()

    hub.ml.init.run()


def run(hub):
    """
    This is the entrypoint for the pop-ml cli tool called "pop-translate"
    """
    # Initialize the tokenizer from config options
    hub.ml.tokenizer.init(
        model_name=hub.OPT.pop_ml.model_name,
        dest_lang=hub.OPT.pop_ml.dest_lang,
        source_lang=hub.OPT.pop_ml.source_lang,
        pretrained_model=hub.OPT.pop_ml.pretrained_model_class,
        pretrained_tokenizer=hub.OPT.pop_ml.pretrained_tokenizer_class,
    )
    # Split the input text based on newlines
    source = hub.OPT.pop_ml.input_text.split("\n")
    # Translate each line and return the output
    output = hub.ml.tokenizer.translate(source)
    # Print the output
    print("\n".join(output))
