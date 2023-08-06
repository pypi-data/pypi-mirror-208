[![mir (Marine Inspection by Remote)](https://github.com/pockerman/mir/actions/workflows/python-app.yml/badge.svg)](https://github.com/pockerman/mir/actions/workflows/python-app.yml)

# mir-ml-engine

The ML engine for the mir (Marine Inspection by Remote) app.

## Dependencies

- PyTorch
- Numpy
- Pillow
- matplolib

- sphinx (if you want to build the documentation)

The project also gets benefited from <a href="https://pypi.org/project/easyfsl/">easyfsl</a> and
<a href="https://github.com/sicara/easy-few-shot-learning">easy-few-shot-learning</a>. However,
you don't need to install this as a fork is maintained within mir-engine

### Testing

There are additional dependencies if you want to run the tests

- pytest
- coverage
- flake8

In order to test locally, you can run the

```commandline
local_test_pipeline.sh
```

The script first runs ```flake8``` and then ```pytest``` with coverage. Finally, it produces
a report ```coverage_report.txt```.

## Installation 




