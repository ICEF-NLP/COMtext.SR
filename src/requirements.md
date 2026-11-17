
# Requirements

The project uses two separate Python environments because Trankit has different dependency requirements from the rest of the project.

## Main Environment

The main environment is used for all project components except Trankit.

- **Python version:** 3.10.9
- **Requirements file:** `requirements_msd_lemma.txt`

Install the dependencies using:

```bash
pip install -r requirements_msd_lemma.txt
```

## Trankit Environment

Trankit is run in a separate environment due to its dependency and Python version requirements.

- **Python version:** 3.10.11
- **Requirements file:** `requirements_trankit.txt`

Install the dependencies using:

```bash
pip install -r requirements_trankit.txt
```

## Notes

Both requirements files are included in the repository. Make sure to use the appropriate Python version when creating each environment.
