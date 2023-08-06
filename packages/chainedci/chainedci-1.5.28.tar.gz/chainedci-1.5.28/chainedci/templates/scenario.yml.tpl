---
##############################################################################
# {{ header }}
##############################################################################

{% if ci_mode == "dynamic" %}
stages:
{%- for stage in stages %}
  - {{ stage }}
{%- endfor %}
{%- if ci_vault_input == 'varfile' %}
.vault_mgmt:
  before_script:
    - echo ${{ ci_vault_file_var }} > ${PWD}/.vault
  after_script:
    - rm -f ${PWD}/.vault
{% endif %}
{%- endif %}
{%- if ci_vault_input == 'varfile' %}
{% set vault_file_param = '-p .vault' %}
{% elif ci_vault_input == 'file' %}
{% set vault_file_param = '-p $' + ci_vault_file_var %}
{% else %}
{% set vault_file_param = '' %}
{% endif -%}

.{{ scenario_name }}_global: &{{ scenario_name }}_global
  variables:
    pod: {{ scenario_name }}
{%- for env in runner.env_vars %}
    {{ env }}: {{ runner.env_vars[env] }}
{%- endfor %}
{% if scenario.environment is defined %}
  environment:
    name: {{ scenario.environment }}
{%- endif %}
{% if ci_mode != "dynamic" %}
  only:
    variables:
      - $POD == "{{ scenario_name }}"
    refs:
      - web
      - schedules
      - triggers
{%- endif %}

{% if ci_mode == "splitted" or ci_mode == "dynamic" %}
.{{ scenario_name }}_runci: &{{ scenario_name }}_runci
  tags:
{%- for tag in runner.tags %}
    - {{ tag }}
{%- endfor %}
{%- if ci_vault_input == 'varfile' %}
  extends: .vault_mgmt
{%- endif %}
  image: {{ runner.images.chainedci.image }}:{{ runner.images.chainedci.tag }}
  script:
    - >
      chainedci -i pod_inventory/inventory
      -s ${pod} -j ${CI_JOB_NAME%:*} {{ vault_file_param }} run

.{{ scenario_name }}_artifacts: &{{ scenario_name }}_artifacts
  artifacts:
    expire_in: 15 days
    name: "$CI_JOB_NAME-$CI_COMMIT_REF_NAME"
    paths:
      - vars/
      - inventory/
{%- endif %}

{% for step in scenario.scenario_steps %}
{{ step }}:{{ scenario_name }}:
  stage: {{ scenario.scenario_steps[step].stage }}
{%- if ci_mode == "splitted" or ci_mode == "dynamic" %}
  <<: *{{ scenario_name }}_global
  <<: *{{ scenario_name }}_runci
{%- if scenario.scenario_steps[step].pull_artifacts or
      git_projects[scenario.scenario_steps[step].project].pull_artifacts or
      step == 'config' %}
  <<: *{{ scenario_name }}_artifacts
{%- endif %}
{% else %}
  <<: *{{ scenario_name }}_global
  <<: *run_ci
{%- if scenario.scenario_steps[step].pull_artifacts or
      git_projects[scenario.scenario_steps[step].project].pull_artifacts or
      step == 'config' %}
  <<: *artifacts
{%- endif %}
{%- endif %}
{%- endfor %}
