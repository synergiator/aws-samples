# AWS Samples

# Quick start

* Clone this repository
* Create virtual environment (venv either virtualenvwrapper)
* Install dependencies 
  ```pip3 install -r requirements.txt ```
  ```pip3 install -r requirements.test.txt ```
* Configure AWS accounts to test
* Fill in missing values (```modules/constants.py```, test data in unit tests)
* Run tests
  ```python3 -m pytest -k "KEYWORD" -s tests/test_awssession.py ```


# Experiment 01

How to configure AWS in a way so that by assuming a role, our calling identity ARN fully matches it?

```
 python3 -m pytest -k "normal" -s tests/test_awssession.py # OK

 python3 -m pytest -k "experiment" -s tests/test_awssession.py # fails

```