# AI Agent Activity System

Activities transform business needs into working software through a pipeline. Each activity YAML defines inputs, outputs, instructions, and completion criteria.

## Change Model

Every change starts with a **design change file** in `design-changes/`. The file describes the business need, feature request, defect, or other trigger. The file name (without extension) becomes the **change_ref** used to namespace briefs and track progress.

- **Greenfield:** Start at activity 01 with a design-changes file (type: `new_product`)
- **Evolution:** Start at activity 00 (impact analysis) to classify the change and determine the required pipeline

All artifacts carry a **Change History** table (version, date, trigger, description, downstream impact). All briefs carry a **Change Record** (trigger, artifacts created/modified, artifacts reviewed but not changed). This ensures full traceability without relying on version control.

Progress is tracked in `design-changes/changelog.yml`.

## Activity Pipeline

```
design-changes/{change_ref}.txt
       │
       ▼
┌──────────────────────────────────────────────────┐
│ 00  Architect: Impact Analysis (non-greenfield)  │
│ Output: _brief/{change_ref}/brief_impact_*.md    │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│ 01  ProductOwner: Business Analysis              │
│ Output: product_definition.md, use_cases/*.md    │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│ 02  Architect: Service Decomposition             │
│ Output: services.yml, workflows/*.md             │
└──────────────────┬───────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌─────────────────┐   ┌──────────────────────────┐
│ 03a PO: Service │   │ 03b Architect: Service   │
│   Requirements  │   │   Interface Definition   │
│ Out: REQ_*.md   │   │ Out: contracts/*.py      │
└─────────────────┘   └──────────┬───────────────┘
  (parallel)                     ▼
                    ┌────────────────────────────────┐
                    │ 04  Architect: Use Case Tests  │
                    │ Out: test_*.py, harnesses/*    │
                    └────────────┬───────────────────┘
                                 ▼
                    ┌────────────────────────────────┐
                    │ 05  Developer: Service Impl    │
                    │ Out: services/<name>/*         │
                    └────────────┬───────────────────┘
                                 ▼
                    ┌────────────────────────────────┐
                    │ 06  Developer: Integration     │
                    │ Out: RealServiceHarness,       │
                    │      container fixtures        │
                    └────────────────────────────────┘
```

Not every change runs the full pipeline. Activity 00 determines which subset applies (see `change_types.yml`). 03a and 03b run in **parallel**. Activity 04 depends only on 03b. Activity 05 uses 03a + 03b + 04. Activity 06 uses 04 + 05.

All briefs for a given change are written under `architecture/_brief/{change_ref}/`, keeping the history of each evolution step.

## Directory Structure

```
design-changes/
├── *.txt                              ← Design change files (pipeline entry points)
└── changelog.yml                      ← Change tracking (status, pipeline, completed activities)

.ai/
├── *.yml                              ← Activity definitions (orchestration)
├── change_types.yml                   ← Change type → required pipeline mapping
├── templates/                         ← Content templates (structure, DO/DON'T, examples)
└── technical/                         ← Implementation patterns (referenced by activities)

```

## Output Artifacts

```
product/
├── product_definition.md              ← Activity 01
├── use_cases/use_case_*.md            ← Activity 01
└── <service>_service/REQ_*.md         ← Activity 03a

architecture/
├── services.yml                       ← Activity 02
├── workflows/workflow_*.md            ← Activity 02
├── contracts/*.py                     ← Activity 03b
└── _brief/{change_ref}/*.md           ← All activities (namespaced per change)

use_case_tests/
├── harnesses/                         ← Activities 04, 06
├── test_use_case_*.py                 ← Activity 04
├── conftest.py                        ← Activities 04, 06
└── docker-compose.yml                 ← Activity 06

services/<service-name>/
├── app/                               ← Activity 05
├── tests/                             ← Activity 05
└── Dockerfile                         ← Activity 05
```

## Key Principles

1. **Reference, Don't Repeat** — Each fact lives in ONE place. Activities reference templates and technical docs, never duplicate them.
2. **Briefs as Handoffs** — Each activity produces a brief (`template_brief.md`) that points to generated artifacts for the next agent. Briefs summarize, not duplicate.
3. **Two Perspectives** — Use cases define user-observable behavior (black-box). Service requirements define technical behavior (glass-box). Never mix them.
4. **Requirements Before Code** — No code change without an updated requirement. The pipeline enforces this by requiring upstream activities to complete before downstream ones start.
5. **Traceable Evolution** — Every change starts as a file in `design-changes/`, flows through the pipeline, and produces namespaced briefs. The changelog tracks progress.
