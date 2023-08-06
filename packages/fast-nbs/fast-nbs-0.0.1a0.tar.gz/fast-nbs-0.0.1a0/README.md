# Fast-nbs

Import jupyter notebooks fast

## Example

Supposing we have a module directory like:
```
- nbpackage
--  nbs
       other.ipynb
--  mynotebook.ipynb

```

then we can import the ipynb codes into current Python files like:

```python
import os
import fastnbs.vis as nbvis

# call root notebook
from nbpackage import mynotebook
mynotebook.show_name("Chen")

# call sub directory notebook
from nbpackage.nbs import other
other.say_hi('hi')
# show notebook codes
nbvis.show_notebook(os.path.join("nbpackage", "nbs", "other.ipynb"))
```