# TAVF Project Scope

## Project Title

A Task-Aware Validation Framework for LLM-Assisted Agile Software Development (TAVF)

## Project Objective

The project investigates whether task-specific validation and refinement can improve the quality of LLM-generated outputs in Agile software development tasks.

The study compares two methods:

1. Direct LLM Prompting
2. TAVF

Both methods will use the same LLM, the same task inputs, and the same evaluation procedure.

## Agile Tasks

The experiment covers three task types:

### 1. User Story Refinement

The LLM receives an existing user story and produces an improved version while preserving the original intent.

Dataset:
Dalpiaz User Story datasets.

Evaluation:
Task-specific quality rubric.

### 2. Bug Report Refinement

The LLM receives an existing bug report and produces a clearer and better-structured report while preserving the original technical information.

Dataset:
BugsRepo structured bug-report dataset.

Evaluation:
Task-specific bug-report quality rubric.

### 3. Test Case Generation

The LLM receives a programming-task description and its reference Python implementation and generates executable test cases.

Dataset:
TestEval.

Evaluation:
Execution success, correctness, line coverage, branch coverage, target coverage, and valid generated tests.

## TAVF Scope

TAVF follows the following general process:

Task Identification  
→ Task-Specific Prompting  
→ LLM Generation  
→ Task-Specific Validation  
→ Feedback / Refinement  
→ Human Review

The framework will use different validation rules depending on the task type.

## Baseline

The baseline method uses direct prompting.

The LLM receives the task input and generates one response without the TAVF validation and refinement process.

## Experimental Design

The experiment contains:

- 20 User Story Refinement tasks
- 20 Bug Report Refinement tasks
- 20 Test Case Generation tasks

Total:

60 tasks

Each task will be executed using:

- Direct LLM Prompting
- TAVF

This produces a controlled comparison between the two methods.

## Experimental Boundaries

The project focuses only on the three selected Agile software-development tasks.

The project does not include:

- model fine-tuning;
- training a new LLM;
- autonomous software development agents;
- full software-project generation;
- large-scale industrial deployment;
- additional Agile tasks outside the selected three.

The framework focuses on validating and refining LLM outputs rather than modifying the underlying LLM.

## Expected Comparison

The experiment will compare Direct Prompting and TAVF using:

- output quality;
- validation results;
- number of refinement iterations;
- response time;
- token usage and estimated cost when available;
- task-specific evaluation metrics;
- human evaluation scores.

The main independent variable is the generation method:

- Direct Prompting
- TAVF