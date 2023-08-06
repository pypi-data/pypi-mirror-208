# Hefesto

**Preprocessing datatable toolkit for CDE semantic model data source requirements**


## Install:
```bash
pip install Hefesto
```
## Usage:
**Requirements:**

- CSV datatable with your CDE data based on [CDE implementation glossary](https://github.com/ejp-rd-vp/CDE-semantic-model-implementations/blob/master/CDE_version_2.0.0/CSV_template_doc/glossary.md)

**Test:**

```py
from Hefesto.main import Hefesto
import yaml

test = Hefesto(datainput = "../data/input.csv") # Use your own path for your CSV input data
transform = test.transform_Fiab()
transform.to_csv ("../data/CDEresult_final.csv", index = False, header=True) # Change this path to the location where your resulting data should be located
```

