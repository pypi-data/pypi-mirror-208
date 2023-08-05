### Getting started 
The package can be found on pypi and can be installed using pip. 
```bash
pip install evalda-pub2
```

### Usage

**Create a bias detector instance for evaluating ner model:**

```python
>>> from evalda-pub2 import Evaluator
 
>>> ev = Evaluator()
```

**Generate ner output:** 

```python
>>> output = ev.eval_ner(n=5, model_name = "saattrupdan/nbailab-base-ner-scandi", outstyle="condensed", outformat="csv")
```
**Generate ner visualization:** (currently non existing:)

```python
>>> viz = ev.visualize(outformat="png")
```
