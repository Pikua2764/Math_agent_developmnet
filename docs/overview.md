# Modules Overview

This section organizes the main modules of the Django-based Math Agent project into **Backend** and **Frontend** components, with clear subcategories and concise descriptions of each module's purpose, key functions/classes, interactions, and dependencies.

---

## Backend

### 1. Utility Modules

#### [`system_messages.py`](../math_agent/utils/system_messages.py)
**Purpose:**  
Defines reusable system prompt templates for LLMs in various roles (problem generation, hinting, checking, target answering, judging).

**Key Elements:**  
- `GENERATOR_MESSAGE`: Prompt for generating challenging, self-contained math problems and answers in JSON.
- `HINT_ONLY_MESSAGE`: Prompt for generating a step-by-step dictionary of hints for a given problem and answer, as JSON.
- `CHECKER_MESSAGE`: Prompt for validating the logical soundness of answers and hints, and for providing corrections, as JSON.
- `TARGET_MESSAGE`: Prompt for simulating a student's answer, requiring only the final answer in JSON.
- `JUDGE_MESSAGE`: Prompt for comparing a model's answer to the true answer, focusing on mathematical equivalence, as JSON.

**Interactions:**  
Imported by all LLM utility modules.

**Dependencies:**  
None.

---

#### [`call_llm_clients.py`](../math_agent/utils/call_llm_clients.py)
**Purpose:**  
Provides a unified interface for calling different LLM providers (OpenAI, Gemini, etc.).

**Key Elements:**  
- `call_llm(pipeline_config, messages)`: Unified function to call either OpenAI or Google Gemini models, handling message formatting, temperature, and API keys.
- `safe_json_parse(raw_text)`: Cleans and parses model output into valid JSON, handling code block markers and LaTeX escapes.
- Provider-specific logic for OpenAI (using `openai.OpenAI`) and Google Gemini (using `google.generativeai`).
- Error handling for unsupported providers and malformed responses.

**Interactions:**  
Used by all LLM-related utilities.

**Dependencies:**  
- External: `openai`, `google-generativeai`, `os`, `json`, `re`

---

#### [`generator.py`](../math_agent/utils/generator.py)
**Purpose:**  
Generates new math problems using LLMs.

**Key Elements:**  
- `generate_problem(pipeline_config, taxonomy=None)`:  
  - Builds a prompt using the system message and taxonomy (subject/topic).
  - Calls the LLM via `call_llm`.
  - Extracts and returns the generated question and answer from the model's JSON response.
  - Handles missing or malformed responses.

**Interactions:**  
Used by views and batch generation logic.

**Dependencies:**  
- Internal: `system_messages.py`, `call_llm_clients.py`
- External: `json`, `django.conf.settings`

---

#### [`hinter.py`](../math_agent/utils/hinter.py)
**Purpose:**  
Generates hints for math problems using LLMs.

**Key Elements:**  
- `generate_hints(question, answer, pipeline_config)`:  
  - Builds a prompt with the problem and answer.
  - Calls the LLM via `call_llm`.
  - Parses and sanitizes the returned hints (ensuring a dictionary format).
  - Retries up to 3 times if hints are empty or malformed.
- `dictify_hints(hints)`: Converts a list of hints to a dictionary if needed.

**Interactions:**  
Used by views and batch generation logic.

**Dependencies:**  
- Internal: `system_messages.py`, `call_llm_clients.py`
- External: `json`, `django.conf.settings`

---

#### [`checker.py`](../math_agent/utils/checker.py)
**Purpose:**  
Validates the logical soundness and correctness of generated problems and hints.

**Key Elements:**  
- `check_problem(question, answer, hints, pipeline_config)`:  
  - Builds a prompt with the problem, answer, and hints.
  - Calls the LLM via `call_llm`.
  - Extracts validation result (`valid`), rejection reason, and any corrected hints from the model's JSON response.

**Interactions:**  
Used by views and batch generation logic.

**Dependencies:**  
- Internal: `system_messages.py`, `call_llm_clients.py`
- External: `json`, `django.conf.settings`

---

#### [`target.py`](../math_agent/utils/target.py)
**Purpose:**  
Tests how a target LLM would answer a given math problem.

**Key Elements:**  
- `test_with_target(question, pipeline_config)`:  
  - Builds a prompt with the problem.
  - Calls the LLM via `call_llm`.
  - Extracts and returns the model's answer from the JSON response.

**Interactions:**  
Used by views and batch generation logic.

**Dependencies:**  
- Internal: `system_messages.py`, `call_llm_clients.py`
- External: `json`, `django.conf.settings`

---

#### [`judge.py`](../math_agent/utils/judge.py)
**Purpose:**  
Evaluates the quality or correctness of a solution using LLMs.

**Key Elements:**  
- `judge_solution(target_solution, true_answer, pipeline_config)`:  
  - Builds a prompt with the true answer and the model's answer.
  - Calls the LLM via `call_llm`.
  - Extracts and returns the validation result (`valid`) and prints the reason if provided.

**Interactions:**  
Used by views and batch generation logic.

**Dependencies:**  
- Internal: `system_messages.py`, `call_llm_clients.py`
- External: `json`, `django.conf.settings`

---

### 2. Database Modules

#### [`models.py`](../math_agent/models.py)
**Purpose:**  
Defines the database schema for problems, batches, and their relationships.

**Key Elements:**  
- `Batch` model:  
  - Fields: `name`, `taxonomy_json`, `pipeline` (JSON), `number_of_valid_needed`, `created_at`, `updated_at`.
  - Represents a batch of generated problems and its configuration.
- `Problem` model:  
  - Fields: `subject`, `topic`, `question`, `answer`, `hints` (JSON), `rejection_reason`, `status` (choices: discarded, solved, valid), `batch` (ForeignKey), `created_at`, `updated_at`.
  - Represents an individual math problem, its hints, status, and batch association.

**Interactions:**  
Used by Django ORM, views, and admin.

**Dependencies:**  
- External: `django.db.models`, `django.core.validators`

---

### 3. View & Routing Modules

#### [`views.py`](../math_agent/views.py)
**Purpose:**  
Implements the main web views for generating problems, listing batches, viewing batch details, and filtering problems.

**Key Elements:**  
- `GenerateView`: Handles GET (form display) and POST (problem generation pipeline, batch creation, LLM calls, and saving results).
- `BatchListView`: Lists all batches with statistics on problem statuses.
- `BatchDetailView`: Shows details and statistics for a specific batch.
- `ProblemDetailView`: Shows details for a specific problem.
- `ProblemListView`: Lists problems for a batch, with optional status filtering.
- `AllProblemsView`: Lists all problems, with optional status filtering.

**Interactions:**  
Uses models, utility functions, and templates.

**Dependencies:**  
- Internal: `models.py`, `utils/`
- External: `django.shortcuts`, `django.views`, `django.http`, `json`, `random`

---

#### [`urls.py`](../math_agent/urls.py)
**Purpose:**  
Defines URL patterns for routing requests to the appropriate views.

**Key Elements:**  
- URL patterns for:
  - Batch list (`/`)
  - Problem generation (`/generate/`)
  - Batch detail (`/batch/<int:pk>/`)
  - Problems in a batch (`/batch/<int:batch_id>/problems/`)
  - Problem detail (`/problem/<int:pk>/`)
  - All problems (`/problems/`)

**Interactions:**  
Maps URLs to views.

**Dependencies:**  
- Internal: `views.py`
- External: `django.urls`

---

## Frontend

### 1. Page Template Modules

#### `generate.html`
**Purpose:**  
Frontend for generating new math problems and selecting LLM models.

**Key Elements:**  
- Form for specifying number of problems, uploading taxonomy, and configuring the LLM pipeline.
- Dynamic dropdowns for provider/model selection, populated from `models.json`.
- Loading overlay for user feedback during generation.
- JavaScript to fetch and update model options based on provider selection.

**Interactions:**  
Interacts with the generate problem view.

---

#### `batches.html`
**Purpose:**  
Displays a list of all problem batches.

**Key Elements:**  
- Table or list displaying all batches.
- Links to batch details and statistics for each batch.

**Interactions:**  
Interacts with the batch list view.

---

#### `batch_detail.html`
**Purpose:**  
Shows details for a specific batch, including its problems.

**Key Elements:**  
- Displays batch metadata (name, creation date, etc.).
- Lists all problems in the batch, grouped by status (solved, valid, discarded).
- Links to individual problem details.

**Interactions:**  
Interacts with the batch detail view.

---

#### `problems.html`
**Purpose:**  
Displays a list of problems, with filtering options.

**Key Elements:**  
- Table or list of problems for a specific batch.
- Filter controls for problem status.
- Links to individual problem details.

**Interactions:**  
Interacts with the problem list view.

---

#### `all_problems.html`
**Purpose:**  
Displays a list of all problems across batches.

**Key Elements:**  
- Table or list of all problems across batches.
- Filter controls for problem status.
- Links to individual problem details.

**Interactions:**  
Interacts with the all problems view.

---

#### `problem_detail.html`
**Purpose:**  
Displays full details for a single problem: question, answer, hints, status, and batch association.

**Key Elements:**  
- Shows question, answer, hints, status, and batch association for a problem.
- May include navigation to previous/next problems or back to batch.

**Interactions:**  
Interacts with the problem detail view.

---

### 2. Data Schema Module

#### [`models.json`](../math_agent/static/math_agent/models.json)
**Purpose:**  
Defines the available LLM providers and models for selection in the frontend when generating problems.

**Key Elements:**  
- JSON object mapping provider names (`openai`, `google`) to lists of supported model names.
- Used by the frontend (especially `generate.html`) to populate provider/model dropdowns for each pipeline component (generator, hinter, checker, target, judge).
- Example structure:
  ```json
  {
      "openai": ["o3-mini", "o1", "gpt-4", "gpt-3.5-turbo"],
      "google": ["gemini-2.5-pro-preview-06-05", "gemini-1.5-pro"]
  }
  ```

**Interactions:**  
Loaded by the frontend (e.g., in `generate.html`) to populate provider/model selection options for users.

--- 