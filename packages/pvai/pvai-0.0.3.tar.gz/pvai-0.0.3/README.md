# PVAI

PVAI is a Python library for data processing and analysis.

Build by [ParkView AI](https://parkviewai.com/).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pvai.

```bash
pip install pvai
```

## list of importable sections

- cleaning 
  - cat_clean_dict
  - num_clean_dist
- analysis
  - POD

## Usage

```python
from pvai.analysis import POD
import pvai.categorical as pcat

# get POD object
test_obj = POD()

# clean categorical samples
cat_dict,unwanted_samples = pcat.cat_clean_num(...)

```
## Dependencies
- numpy
- pandas
- matplotlib

## Contributing

Coming in the future.

## License

[MIT](https://choosealicense.com/licenses/mit/)