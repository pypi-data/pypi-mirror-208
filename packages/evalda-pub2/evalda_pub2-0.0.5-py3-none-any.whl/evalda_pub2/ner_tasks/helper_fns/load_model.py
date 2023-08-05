def load_mdl(model_name):
    import spacy, dacy
    if model_name in dacy.models() + ["chcaa/"+ i for i in dacy.models()]:
        print(f"Trying to load model {model_name} with Dacy.")
        model = dacy.load(model_name)
    elif model_name == "scandi-load-dacy":
        print(f"Trying to load model {model_name} with Dacy.")
        model = spacy.blank("da")
        model.add_pipe("dacy/ner")
    elif 'da_core_news' in model_name:
        print(f"Trying to load model {model_name} with Spacy.")
        model = spacy.load(model_name)
    elif '/' in model_name:
        print(f"Trying to load model {model_name} from Huggingface with spacy wrap.")
        try:
            import spacy_wrap
            model = spacy.blank("da")
            config = {  "model": {"name": model_name}, 
                        "predictions_to": ["ents"]} 

            model.add_pipe("token_classification_transformer", config=config)
        except OSError:
            print("Cannot find model on Hugginface. Please specify the full name of the model i.e. 'name/model-name' ")     
    else:
        print("Cannot find model on Hugginface. Please specify the full name of the model i.e. 'name/model-name' ")
    return model


