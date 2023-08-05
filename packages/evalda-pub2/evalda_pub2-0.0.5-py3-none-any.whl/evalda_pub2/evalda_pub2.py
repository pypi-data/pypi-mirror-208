from transformers import logging
logging.set_verbosity_error()
import warnings
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", FutureWarning)

class Evaluator:
    def __init__(self, model_name):
        self.model_name = model_name
        print(f'You can test {self.model_name} by running Evaluator.evalute_<model type>()')
    
    def evaluate_ner(self, n):
        from .ner_tasks.helper_fns.load_model import load_mdl
        from .ner_tasks.helper_fns.performance import eval_model_augmentation
        from .ner_tasks.helper_fns.augmentation import f_aug, m_aug, muslim_f_aug, muslim_m_aug
        from dacy.datasets import dane
        testdata = dane(splits=["test"], redownload=True, open_unverified_connected=True)

        model = load_mdl(self.model_name)
        if n <= 1:
            print(f"Please choose a value for n larger than 1 to ensure robustness, got: {n}.")
        else:
            print(f"Running model with {n} repetitions")
        
        # define augmenters 
        augmenters = [
            (f_aug, "Female names", n),
            (m_aug, "Male names", n),
            (muslim_f_aug, "Muslim female names", n),
            (muslim_m_aug, "Muslim male names", n)]

        # run model 
        output = eval_model_augmentation(model, self.model_name, str(n), augmenters, testdata)
        return output
    
    def evaluate_pretrained(self, task, mask_token=None, start_token = None, sep_token=None):
        import pandas as pd
        from .base_tasks.abc_lm_utilities import load_abc, run_abc, get_output
        from .base_tasks.load_model import load_mdl
        from transformers import pipeline
        from .base_tasks.wino_fillmask_utilities import run_winobias, evaluate_lm_winobias
        import spacy
        
        ### RUN ABC
        # load data 
        if task == "abc":
            print("Running the coreference model on the ABC dataset. First on the female-stereotypical sentences, and secondly on the male-stereotypical sentences.")
            refl_sents_m, refl_sents_f = load_abc()
            # load tokenizer and model
            model, tokenizer = load_mdl(self.model_name)
            
            # create results df 
            out_df_f = run_abc(refl_sents_f, "female", tokenizer, model, start_token, sep_token)
            out_df_m = run_abc(refl_sents_m, "male", tokenizer, model, start_token, sep_token)


            # evaluate abc
            results = get_output(out_df_f, out_df_m, model_name = self.model_name)

        elif task == "dawinobias":
            print("Running the pre-trained model on the ABC dataset. First on the anti-stereotypical sentences, and secondly on the pro-stereotypical sentences.")
            ### RUN WINO 
            #tokenizer = spacy.load("da_core_news_sm")
            #load model used for tokenization
            try:
                tokenizer = spacy.load("da_core_news_sm")
            except OSError: 
                print("da_core_news_sm spaCy model missing, installing it now")
                from spacy.cli.download import download
                download("da_core_news_sm")
                tokenizer = spacy.load("da_core_news_sm")
            
            # initiate pipeline
            nlp =  pipeline(task = "fill-mask", model = self.model_name) 

            # run wino
            clf_rep_anti, clf_rep_pro= run_winobias(tokenizer, nlp, mask_token = mask_token, model_name = self.model_name)
            
            results = evaluate_lm_winobias(clf_rep_anti, clf_rep_pro, model_name = self.model_name)
                    
        else: 
            raise ValueError("Not a valid task. Choose between 'abc' and 'dawinobias'")
        return results 
        
    def evaluate_coref(self, task, model):
        #from danlp.models import load_xlmr_coref_model
        from sklearn.metrics import classification_report, f1_score
        import numpy as np
        import sys, os, spacy, random, torch, json
        from pathlib import Path
        import numpy as np
        import pandas as pd
        import nltk #only wino
        import progressbar

        # load the coreference model
        #if model_name == "xlm-r_coref": 
            #print("Loading the XLM-R coreference model")
            #model = load_xlmr_coref_model() 

        if task == "dawinobias":
            import nltk
            from .coref_tasks.coref_utils import run_winobias_coref, evaluate_coref_winobias
            nltk.download('omw-1.4') #only wino
            #load model used for tokenization
            try:
                nlp = spacy.load("da_core_news_sm")
            except OSError: 
                print("da_core_news_sm spaCy model missing, installing it now")
                from spacy.cli.download import download
                download("da_core_news_sm")
                nlp = spacy.load("da_core_news_sm")

            print("Running the coreference model on the DaWinoBias dataset. First on the anti-stereotypical sentences, and secondly on the pro-stereotypical sentences.")
            anti_res, pro_res =run_winobias_coref(model, nlp)
            results = evaluate_coref_winobias(anti_res, pro_res, model_name = self.model_name)
            
        elif task == "abc":
            import pandas as pd
            from .coref_tasks.coref_utils import run_abc_coref, evaluate_coref_abc, eval_results
            print("Running the coreference model on the ABC dataset. First on the female-stereotypical sentences, and secondly on the male-stereotypical sentences.")
            fem_preds, male_preds = run_abc_coref(model)
            #two dicts of f1 scores
            df_fem, df_male, all_sents = evaluate_coref_abc(fem_preds= fem_preds, male_preds= male_preds)

            results = eval_results(df_fem, df_male, all_sents, model_name=self.model_name)
        else:
            raise ValueError("Not a valid task. Choose between 'abc' and 'dawinobias'")

        return results 

class Visualizer:
    """Class for visualizing the results of the evaluation"""
    def __init__(self):
        import seaborn as sns
        sns.set_style("whitegrid", rc={"lines.linewidth": 1})
        sns.set_context("notebook", font_scale=1.2)

        self.palette = sns.color_palette("pastel",n_colors=15).reverse()
    
    def vizualize_results(self, detailed_output, framework, model_name, task=None):
        import seaborn as sns
        import pandas as pd
        import matplotlib.pyplot as plt

        sns.set_style("whitegrid", rc={"lines.linewidth": 10})
        
        df = pd.DataFrame()

        if framework == "abc":
            df["Stereotypical Occupations"] = ["Female","Male", "Overall"] *2
            df["Anti-reflexive Pronoun"] = ["Female"] *3 + ["Male"] *3
            markers = ["o", "o", "o"]
            x = "Anti-reflexive Pronoun"
            nuance = "Stereotypical Occupations"

            if task == "coref":
                try:
                    mean_fem = list(detailed_output.loc["Mean Rate of Detected Clusters"])[1]
                    mean_male = list(detailed_output.loc["Mean Rate of Detected Clusters"])[3]
                    fpr_fem_pron_fem_occ = list(detailed_output.loc["Rate of Detected Clusters"])[0]
                    fpr_fem_pron_male_occ = list(detailed_output.loc["Rate of Detected Clusters"])[1]
                    fpr_male_pron_fem_occ = list(detailed_output.loc["Rate of Detected Clusters"])[2]
                    fpr_male_pron_male_occ = list(detailed_output.loc["Rate of Detected Clusters"])[3]
                except:
                    mean_fem = float(detailed_output.iloc[2,2])
                    mean_male = float(detailed_output.iloc[2,4])
                    fpr_fem_pron_fem_occ = float(detailed_output.iloc[4,1])
                    fpr_fem_pron_male_occ = float(detailed_output.iloc[4,2])
                    fpr_male_pron_fem_occ = float(detailed_output.iloc[4,3])
                    fpr_male_pron_male_occ = float(detailed_output.iloc[4,4])
                
                points = [  fpr_fem_pron_fem_occ,
                            fpr_fem_pron_male_occ,
                            mean_fem,
                            fpr_male_pron_fem_occ,
                            fpr_male_pron_male_occ,
                            mean_male] 

                df["False Positive Rates"] = points
                y = "False Positive Rates"
                title = f"Coreference Resolution on the ABC dataset. {model_name}"
            
            elif task == "lm":
                try:
                    points = [float(detailed_output.iloc[4,1].split(" ")[0]), 
                        float(detailed_output.iloc[4,2].split(" ")[0]),
                        float(detailed_output.iloc[2,1].split(" ")[0]),
                        float(detailed_output.iloc[4,3].split(" ")[0]), 
                        float(detailed_output.iloc[4,4].split(" ")[0]),
                        float(detailed_output.iloc[2,3].split(" ")[0])]
                except:
                    points = [float(detailed_output.iloc[4,0].split(" ")[0]), 
                        float(detailed_output.iloc[4,1].split(" ")[0]),
                        float(detailed_output.iloc[2,0].split(" ")[0]),
                        float(detailed_output.iloc[4,2].split(" ")[0]), 
                        float(detailed_output.iloc[4,3].split(" ")[0]),
                        float(detailed_output.iloc[2,2].split(" ")[0])]
                df["Median Perplexity"] = points
                y = "Median Perplexity"
                title = f"Perplexities of the ABC dataset. {model_name}"
        
        elif framework == "dawinobias":


            df["Pronoun"] = ["Female F1","Male F1", "Accuracy"]*2
            if task == "coref":
                try:
                    points = [float(detailed_output.iloc[5,1]), 
                        float(detailed_output.iloc[5,2]), 
                        float(detailed_output.iloc[3,1]), 
                        float(detailed_output.iloc[5,3]), 
                        float(detailed_output.iloc[5,4]), 
                        float(detailed_output.iloc[3,3])]
                except:
                    points =  [detailed_output.loc["F1"][0],
                        detailed_output.loc["F1"][1],
                        detailed_output.loc["Accuracy"][0],
                        detailed_output.loc["F1"][2],
                        detailed_output.loc["F1"][3],
                        detailed_output.loc["Accuracy"][2]]
                title = f"Coreference Performance, DaWinoBias: {model_name}"
            elif task == "fillmask":
                try: #if loaded
                    points = [
                        float(detailed_output.iloc[4,1]),
                        float(detailed_output.iloc[4,2]),
                        float(detailed_output.iloc[2,1]),
                        float(detailed_output.iloc[4,3]),
                        float(detailed_output.iloc[4,4]),
                        float(detailed_output.iloc[2,3])
                    ]
                except: # if 
                    points =  [detailed_output.loc["F1"][0],
                        detailed_output.loc["F1"][1],
                        detailed_output.loc["Accuracy"][0],
                        detailed_output.loc["F1"][2],
                        detailed_output.loc["F1"][3],
                        detailed_output.loc["Accuracy"][2]]
                title = f"Fill-Mask Task Performance, DaWinoBias: {model_name}"

            df["Performance"] = points
            df["Condition"] = ["Anti-stereotypical"]*3 + ["Pro-stereotypical"]*3
            x = "Condition"
            y = "Performance"
            nuance = "Pronoun"
            markers = ["o", "o", "o"]
            title = title

        elif framework == "ner":
            df["Protected Group"] = ["Majority F1", "Minority F1"]*2
            try:    
                points = [float(detailed_output.iloc[2,1].split(" ")[0]), 
                    float(detailed_output.iloc[4,2].split(" ")[0]), 
                    float(detailed_output.iloc[2,3].split(" ")[0]), 
                    float(detailed_output.iloc[4,4].split(" ")[0])]
            except:
                points = [float(detailed_output.iloc[4,0].split(" ")[0]),
                        float(detailed_output.iloc[4,1].split(" ")[0]), 
                        float(detailed_output.iloc[4,2].split(" ")[0]), 
                        float(detailed_output.iloc[4,3].split(" ")[0])]

            df["Performance"] = points
            df["Augmentation"] = ["Female Names"] *2 + ["Male Names"]*2
            x = "Augmentation"
            y = "Performance"
            nuance = "Protected Group"
            markers = ["o", "o"]
            title = f"Performance of NER on Augmented DaNe. {model_name}"

        sns.pointplot(data=df, 
                    x=x,
                    y=y, 
                    hue= nuance,  
                    dodge=False, 
                    join=True, 
                    markers= markers, 
                    scale=1.2, 
                    linestyles=[':', ':', '-'],
                    palette=["sandybrown", "mediumpurple", "darkgrey"]).set_title(title)
        
        plt.minorticks_on()

        return plt