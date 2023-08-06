---
################################################################################
#
# !! DO NOT EDIT MANUALLY !!
#
# {{ header }}
#
################################################################################

stages:
{%- for stage in stages %}
  - {{ stage }}
{%- endfor %}

variables:
  GIT_SUBMODULE_STRATEGY: recursive

################################################################################
# Shared parameters
################################################################################
.runner_tags: &runner_tags
  tags:
{%- for tag in runner.tags %}
    - {{ tag }}
{%- endfor %}

.runner_env: &runner_env
{%- for env in runner.env_vars %}
  {{ env }}: {{ runner.env_vars[env] }}
{%- endfor %}

################################################################################
# Linting
################################################################################

yaml_checking:
  only:
    - pushes
  stage: lint
  <<: *runner_tags
  variables:
    <<: *runner_env
  image: {{ yaml_image }}
  script:
    - >
      yamllint -d "line-length: {
      max: 80,
      allow-non-breakable-words: true,
      allow-non-breakable-inline-mappings: true}"
      .gitlab-ci.yml

{%- if disable_pages %}
################################################################################
# Pages
################################################################################

pages:
  image: {{ runner.images.ansible.image }}:{{ runner.images.ansible.tag }}
  stage: lint
  <<: *runner_tags
  variables:
    <<: *runner_env
  script:
    - ./chained-ci-vue/init.sh ./pod_inventory
  artifacts:
    paths:
      - public
  only:
    - master
  except:
    - triggers
    - api
    - external
    - pipelines
    - schedules
    - web
{% endif %}

################################################################################
# Scenarios
################################################################################

{%- if ci_vault_input == 'varfile' %}
.vault_mgmt:
  before_script:
    - echo ${{ ci_vault_file_var }} > ${PWD}/.vault
  after_script:
    - rm -f ${PWD}/.vault
{% set vault_file_param = '-p .vault' %}
{% elif ci_vault_input == 'file' %}
{% set vault_file_param = '-p $' + ci_vault_file_var %}
{% else %}
{% set vault_file_param = '' %}
{% endif -%}

{% if ci_mode == "dynamic" %}

.generate_filter: &generate_filter
  only:
    variables:
      - $POD
    refs:
      - web
      - schedules
      - triggers

generate-config:
{%- if ci_vault_input == 'varfile' %}
  extends: .vault_mgmt
{%- endif %}
  <<: *runner_tags
  <<: *generate_filter
  stage: prepareci
  image: {{ runner.images.chainedci.image }}:{{ runner.images.chainedci.tag }}
  script:
    - chainedci -i pod_inventory/inventory -s ${POD} {{ vault_file_param }} generate
  artifacts:
    paths:
      - scenario.yml

child-pipeline:
  <<: *generate_filter
  stage: rundynamicci
  trigger:
    include:
      - artifact: scenario.yml
        job: generate-config
    strategy: depend


{% elif ci_mode == "splitted" %}
include:
{%- for scenario in scenarios %}
  - '{{ ci_include_prefix }}{{ scenario }}.yml'
{%- endfor %}
{% else %}

.artifacts_root: &artifacts_root
  name: "$CI_JOB_NAME-$CI_COMMIT_REF_NAME"
  paths:
    - vars/
    - inventory/

.artifacts: &artifacts
  artifacts:
    <<: *artifacts_root
    expire_in: 15 days

.artifacts_longexpire: &artifacts_longexpire
  artifacts:
    <<: *artifacts_root
    expire_in: 1 yrs

.run_ci: &run_ci
  <<: *runner_tags
{%- if ci_vault_input == 'varfile' %}
  extends: .vault_mgmt
{%- endif %}
  image: {{ runner.images.chainedci.image }}:{{ runner.images.chainedci.tag }}
  script:
    - >
      chainedci -i pod_inventory/inventory
      -s ${pod} -j ${CI_JOB_NAME%:*} {{ vault_file_param }}

{% for scenario in scenarios %}
{% set scenario_name = scenario %}
{% set scenario_cfg = scenarios_cfg[scenario] %}
{% set header = "Scenario " + scenario %}
{% include 'scenario.yml.tpl' %}
{%- endfor %}
{% endif %}
