# TAVF

A Task-Aware Validation Framework for LLM-Assisted Agile Software Development.

## Project Overview

TAVF investigates whether task-specific validation and refinement can improve LLM-generated outputs compared with direct prompting.

The experiment covers three Agile software-development tasks:

- User Story Refinement
- Bug Report Refinement
- Test Case Generation

## Experimental Design

The study compares:

1. Direct LLM Prompting
2. TAVF

The same LLM and the same task inputs will be used for both methods.

The experimental dataset contains:

- 20 User Story Refinement tasks
- 20 Bug Report tasks
- 20 Test Case tasks

Total: 60 tasks.

## Datasets

- User Story Refinement: Dalpiaz User Story datasets
- Bug Reports: BugsRepo
- Test Cases: TestEval

UStAI is retained as a reference source for User Story quality criteria.

## Status

Week 1: Experimental setup and evaluation design.
