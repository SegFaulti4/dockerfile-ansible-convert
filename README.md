# Containerfile to Ansible role translator

This repository contains a source code for Containerfile to Ansible role translator. 

## Dependencies

System packages:
* python3.7+
* python3-dev
* python3-setuptools

Python3 packages - listed in requirements.txt

## Getting started

After dependencies installation just clone this repository and run `python3 setup.py install` at the root of the project.

## Working with translator

To translate desired containerfile run `d2a *input-file*` or `d2a *input-file* -o *output-file*`.

## Translator components

### Shell parser

To parse shell scripts embedded in Containerfile translator uses [bashlex](https://github.com/idank/bashlex).

Currently, translator doesn't include support for many shell features, such as:

* command substitutions (`"$(nproc)"`)
* loops 
* if-else statements
* pipes
* redirects

Shell scripts that include any of these features will be translated as is.

### Containerfile parser

To parse Containerfile contents translator uses [this package](https://github.com/asottile/dockerfile).

Resulting AST of Containerfile contents after parsing are supplemented with AST of embedded shell.

### Ansible task matcher

After parsing of shell scripts translator uses its collection of command templates to match any given command with corresponding Ansible task.

Configurations of supported commands are stored [here](src/ansible_matcher/configs). For each supported command there is a JSON file with the following content:

* General template - any command that matches this template will be compared with examples from the same configuration file
* Examples - each example contains a command template and task template, if any given command matches command template it will be translated into corresponding task
* Options configuration - for each supported command option (i.e. `--help`) configuration file should include:
  * list of option aliases (i.e. `-h`, `--help`)
  * boolean value for the fact that option requires arguments
  * boolean value for the fact that option could be used multiple times in one command
* Option examples - after successful command example matching every non-matched command option will be compared with option examples, each option example contains a template for command options and template for additional task parameters, if any of remaining options matches with options template the generated task will be extended with additional parameters
