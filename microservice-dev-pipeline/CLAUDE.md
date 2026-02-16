# Project Guide

This project uses an AI activity pipeline to develop a backend application. All activity definitions, templates, and technical docs are in `.ai/`. See `.ai/README.md` for the full pipeline diagram, directory structure, and key principles.

## Running an Activity

When asked to run an activity (e.g., "run activity 03a for url-management service"):

1. Read the activity YAML in `.ai/` (e.g., `.ai/03a_PO_service_requirements.yml`)
2. Read all declared inputs (load every file listed in the `inputs:` section)
3. For each output that references a template, read the template
4. For each output that references a technical doc, read the technical doc
5. Follow the instructions step by step, starting at step 0 (trigger and upstream context)
6. Generate all declared outputs
7. Validate all completion criteria are met
8. Generate the brief with Change Record section

## Processing a Design Change

When asked to process a design change (e.g., "process design-changes/02-add-observability.txt"):

1. Read the design change file to understand the trigger
2. Derive the **change_ref** from the file name without extension (e.g., `02-add-observability`)
3. If the change type is `new_product` (greenfield), start at activity 01
4. Otherwise, start at activity 00 (`.ai/00_Architect_impact_analysis.yml`) for impact analysis
5. Activity 00 classifies the change type and determines the required pipeline (see `.ai/change_types.yml`)
6. Execute each required activity in the pipeline sequence
7. For parallel activities (03a and 03b), complete both before proceeding to 04
8. All briefs are written under `architecture/_brief/{change_ref}/`
9. Update `design-changes/changelog.yml` at pipeline start (in_progress) and end (completed)

## Greenfield Development

When asked to build a new product from scratch:

1. Create a design change file in `design-changes/` with `type: new_product`
2. Start at activity 01 with the design change file as input
3. Execute the full pipeline: 01 → 02 → 03a/03b (parallel) → 04 → 05 → 06
4. Activity 05 runs once per service defined in `architecture/services.yml`

## Key Rules

- **Requirements before code**: Never skip to implementation (activity 05) without updating requirements (activity 03a) first
- **Change History**: When modifying an existing artifact, add a new row to its Change History table
- **Change Record in briefs**: Every brief must document trigger, artifacts created/modified, and artifacts reviewed but not changed
- **Read before write**: Always read existing artifacts before modifying them in update mode
- **Design changes as entry point**: Every pipeline execution starts from a file in `design-changes/`
- **Namespaced briefs**: All briefs for a change go under `architecture/_brief/{change_ref}/`
