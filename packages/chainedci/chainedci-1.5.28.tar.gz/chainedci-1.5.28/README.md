# Chained-ci-py

`chained-ci-py` is a project to manage CI/CD scenarios with gitlab and
trigger multi subproject pipelines, passing variables and artifacts from
one to the other.

⚠️ DOCUMENTATION is to be done ⚠️

Here is a few command line:

## How to use chainedci

Using python package:

```shell
pip install chainedci
```

Using Docker:

```shell
docker run --rm -ti \
  registry.gitlab.com/orange-opensource/lfn/ci_cd/chained-ci-py chainedci
```

## Generate .gitlab-ci.yml from scenario files

```shell
chainedci generate -i <scenario_folder>/inventory -p .vault
```

with `.vault` a local file containing your vault key that was used to cipher
projects tokens.
