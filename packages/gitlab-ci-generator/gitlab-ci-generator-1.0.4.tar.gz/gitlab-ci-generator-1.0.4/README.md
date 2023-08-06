# gitlab-ci-generator
This project builds a dynamic gitlab ci file that is intended to be used for monorepos.  The concept is to simplify the amount of work that is needed to manage the monorepo.

## Installation
You can download and run directly with python or install using:
```
pip install gitlab-ci-generator
```
This installs like an executable and you can simply run: 
```
gitlab-ci-generator
```

## Usage
The project takes the following parameters:
|Name|Parameter|Description|Required|
|-----|--------|-----------|--------|
|Input File|--inputfile/-f|The yaml file that will be used to render the gitlab ci file.|Yes|
|Output File|--outputfile/-o|The yaml file that is rendered using the jinja2 template with data from the input yaml file.|No|
|Template File|--templatefile/-t|A jinja2 file that can be used to override default templating|No|
|Help|-h|Displays help info|No|

This program will load the input yaml file into two distinct dictionaries that are available to the template:
* pipeline_info
* jobs

To run without specifying an output file you can write stdout to a redirect file like so: 
```
gitlab-ci-generator --inputfile ./job-dependency.yml 1> /tmp/test.out
```

### pipeline_info
This section is gets loaded as is into a dictionary so you can easily extend it for your needs.  The built-in template uses the following:
```
pipeline_info:
  shared_includes: <<-- Used by the template to build the include: section of the gitlab ci file.
    - name: rules <<-- List of includes and can be of type local or project.  The rules example here is used in the template in concert with the share_reference_rules: section to define dynamic rules for jobs.
      local: "example/example-config/rules.yml" 
  shared_reference_rules: <<-- Used by the template to build the rules: section of the gitlab ci under each job.
    - rule_name: standard-rule-if <- The rule_source and rule_name will create a !reference[rule_source, rule_name] value under the rules section of each job.
      rule_source: .job_changes_rules
      only_changes: true
  final_job: <<-- Optional section that can be used to specify a final trigger job to run at the end of your pipeline.
    name: <<-- The name of the final job.
    stage: <<-- The stage that you want the final job to run in.
    trigger_job_info: <<-- Info around the final job.
      project: <<-- gitlab project location for final job.
      ref: <<-- Final job branch reference
      file: <<-- Path to the yml file to be triggered.
    rules: <<-- Custom rules for the final job.
      - rule_name: <<-- The rule_source and rule_name will create a !reference[rule_source, rule_name] value under the rules section of each job.
      - rule_source: <<-- Points the rule_name in the !reference
      only_changes: true <<-- True will run this job only if changes occur.
```

### jobs
This section is used to define the hierarchy for the gitlab jobs.  This section is not extensible and should be structured as follows:
```
jobs: <<-- List of jobs and dependencies that will build the appropriate changes/needs logic in the generated gitlab ci file.
  - name: example-1 <<-- name: will be the job name in the generated gitlab file and is required. 
    folder: example/example-folder-1 <<-- folder: The subfolder in the gitlab repo that will be monitored for changes and contains the sub-repo in the monorepo.
    gitlab_yml_file: .gitlab-example.yml <<--  gitlab_yml_file: is the pipeline file that will be triggered in the folder: that is specified
    dependent_jobs: <<-- dependent_jobs: is a list of dependent jobs and can have dependent_jobs on its jobs.  In other words, this can go multiple levels deep with dependencies.  
      - name: example-2
        folder: example/example-folder-2
        gitlab_yml_file: .gitlab-example.yml
```

## Sample Input yaml File
This sample can also be found in the gitlab repo for this project at the location [example/example-config/job-dependency.yml](https://gitlab.com/gary.schaetz/public/gitlab-ci-generator/-/blob/main/example/example-config/job-dependency.yml)
```
---
pipeline_info:
  shared_includes:
    - name: rules
      local: "example/example-config/rules.yml"
  shared_reference_rules:
    - rule_name: standard-rule-if
      rule_source: .job_changes_rules
      only_changes: true
    - rule_name:  manual-rule-if
      rule_source: .job_changes_rules
      when: manual
      only_changes: true
    - rule_name: schedule-rule-if
      rule_source: .job_changes_rules
      only_changes: false
  final_job:
    name: cut-tag
    stage: post-deploy
    trigger_job_info:
      project: gary.schaetz/private/pipelines
      ref: main
      file: /path/to/child-pipeline.yml
    rules:
      - rule_name: standard-rule-if
        rule_source: .job_changes_rules
        only_changes: true
jobs:
  - name: example-1
    folder: example/example-folder-1
    gitlab_yml_file: .gitlab-example.yml
    dependent_jobs:
      - name: example-2
        folder: example/example-folder-2
        gitlab_yml_file: .gitlab-example.yml
```

### Sample Output
Using the jinja template [here](https://gitlab.com/gary.schaetz/public/gitlab-ci-generator/-/blob/main/src/gitlab_ci_generator_package/templates/gitlab-template.jinja) and the data from [example/example-config/job-dependency.yml](https://gitlab.com/gary.schaetz/public/gitlab-ci-generator/-/blob/main/example/example-config/job-dependency.yml)
```
include:
    - local: 'example/example-config/rules.yml'

stages:
  - build
  - post-deploy

example-1:
  stage: build
  variables:
    PROJECT_SUBDIR: example/example-folder-1
  rules:
    - if: !reference [.job_changes_rules,standard-rule-if]
      changes:
        - example/example-folder-1/**/*
    - if: !reference [.job_changes_rules,manual-rule-if]
      when: manual
      changes:
        - example/example-folder-1/**/*
    - if: !reference [.job_changes_rules,schedule-rule-if]
  trigger:
    include: example/example-folder-1/.gitlab-example.yml    
    strategy: depend
 
example-2:
  stage: build
  variables:
    PROJECT_SUBDIR: example/example-folder-2
  rules:
    - if: !reference [.job_changes_rules,standard-rule-if]
      changes:
        - example/example-folder-2/**/*
        - example/example-folder-1/**/*
    - if: !reference [.job_changes_rules,manual-rule-if]
      when: manual
      changes:
        - example/example-folder-2/**/*
        - example/example-folder-1/**/*
    - if: !reference [.job_changes_rules,schedule-rule-if]
  needs: 
    - job: example-1
      optional: true 
  trigger:
    include: example/example-folder-2/.gitlab-example.yml    
    strategy: depend
 
cut-tag:
  stage: post-deploy
  rules:
    - if: !reference [.job_changes_rules,standard-rule-if]
      changes:
        - example/example-folder-1/**/*
        - example/example-folder-2/**/*
  trigger:
    include: 
      - project: 'gary.schaetz/private/pipelines'
        ref: 'main'
        file: '/path/to/child-pipeline.yml' 
    strategy: depend
```

## How to use in your pipeline
A variable is passed into your pipeline that you can see in the previous section called PROJECT_SUBDIR.  Use this in before scripts to cd into the active project.  

Here is an example of a pipeline that will use this program in one job to generate the ci file and then trigger it in the next job.  Notice how we set PARENT_PIPELINE_SOURCE variable so that you can use this in your downstream rules as a trigger overrides the original CI_PIPELINE_SOURCE.
```
include: 
  - project: "gary.schaetz/private/pipelines"
    ref: main
    file: 'templates/rules/rules.yml'

stages:
  - build_config
  - run

generate-pipeline:
  image: gschaetz/base-alpine:latest
  stage: build_config
  tags: 
    - docker 
    - self-managed 
    - ubuntu-worker
  rules:
    - !reference [.job_rules, standard-rule]  
  before_script:
    - pip install gitlab-ci-generator
  script:
    - gitlab-ci-generator -f job-dependency.yml -o generated-ci.yml
  artifacts:
    paths:
      - generated-ci.yml

trigger-child-pipeline:
  stage: run
  rules:
    - if: !reference [.job_changes_rules,standard-rule-if]
      changes:
        - "*/**/*"
  trigger:
    include:
      - artifact: generated-ci.yml
        job: generate-pipeline
    strategy: depend
  variables:
    PARENT_PIPELINE_ID: $CI_PIPELINE_ID
    PARENT_PIPELINE_SOURCE: $CI_PIPELINE_SOURCE
```

## License
MIT License