---
name: Bug Report
about: Template to help gather minimal debugging/reproducing info
labels: bug
---

<!--
Common problems to check:
- old virtualenv
    Especially if any dependencies have changed or if you've installed additional packages, you might try creating a fresh virtualenv
      python -m venv ~/.virtualenvs/dql-new
      source ~/.virtualenvs/dql-new/bin/activate
      pip install -U pip
      pip install -e '.[dev]'

- re-install dql needed
    If using a PyPI release, try
      pip install -U dql-alpha

    If installing from a repo, try
      pip install -e '.[dev]'

- remove .dql if using a new dql version
    rm -rf .dql
-->

## Version info

```sh
dql -V; python -V
```
The command above prints:
```

```
<!--
Please share the dql and python version above between the backticks (```).
The output might look like this:

  0.19.1.dev1+g350df47.d20230503
  Python 3.8.12

-->


## Description

<!--
A clear and concise description of what the bug is.

If possible, reproduce CLI bugs with the verbose option:
  dql command -v
-->

### Reproduce

<!--
Step list of how to reproduce the bug

Example:
```
dql ls s3://bkt/dir1 s3://bkt/dir2
dql cp s3://bkt/dir3 ./abc
...
```
-->
