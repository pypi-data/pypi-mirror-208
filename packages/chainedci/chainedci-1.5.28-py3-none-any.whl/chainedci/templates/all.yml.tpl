---
disable_pages: true
protected_pods: []
stages:
  - lint
  - config
  - prepare
  - build
  - apps
  - test
runner:
  tags: []

  env_vars:
    chainedci_project: {{ project_long_name }}
  docker_proxy:
  images:
    ansible:
      image: registry.gitlab.com/orange-opensource/lfn/ci_cd/docker_ansible
      tag: 2.9-alpine
    chainedci:
      image: registry.gitlab.com/orange-opensource/lfn/ci_cd/chained-ci-py
      tag: {{ current_chained_ci_version }}

gitlab:
  pipeline:
    delay: 15
  base_url: https://{{ gitlab_server }}
  api_url: https://{{ gitlab_server }}/api/v4

  git_projects:
    {{ config_step }}:
      stage: config
      path: {{ config_path }}

    {{ trigger_step }}:
      stage: apps
      trigger_token: {{ trigger_token }}
      branch: {% raw %}"{{ lookup('env','CI_BUILD_REF_NAME')|default('master', true) }}"{% endraw %}

    project_A:
      stage: build
      url: https://{{ gitlab_server }}/{{ example_project }}
      trigger_token: this token must be set
      branch: master
      pull_artifacts: "name_of_job_to_pull"
      parameters:
        ansible_verbose: {% raw %}"{{ lookup('env','ansible_verbose') }}"{% endraw %}