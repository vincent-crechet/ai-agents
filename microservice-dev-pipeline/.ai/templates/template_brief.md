# [Agent Role] Brief: [Activity Name]

_Created: [Date]_
_Activity: [activity_id]_

## Objective

[One sentence describing what this activity accomplished and why]

## Summary

[2-3 sentences providing context about what was done. Focus on WHAT changed, not repeating the content of the artifacts.]

## Generated Artifacts

[Simple list of files created with one-line purpose statements. Do NOT summarize their contents.]

### [Category 1, e.g., "Service Definitions"]
- **File:** `path/to/artifact.md`
- **Purpose:** [One sentence describing what this file contains]

### [Category 2, e.g., "Requirements"]
- **File:** `path/to/artifact.md`
- **Purpose:** [One sentence describing what this file contains]

## Change Record

- **Trigger:** [What initiated this work — e.g., "Initial development", "DEFECT-042: description", "FEATURE-REQUEST: description"]
- **Artifacts created:** [List of new files created]
- **Artifacts modified:** [List of files changed, with version transition e.g., "v1.0 → v1.1" and one-line summary of change]
- **Artifacts reviewed, no change needed:** [List of files assessed but not modified — proves impact was evaluated]

## Key Decisions Made

[List ONLY major architectural or design decisions that affect downstream work. Maximum 3-5 bullet points.]

- **Decision:** [What was decided]
- **Rationale:** [Why this decision was made]

## Next Steps for [Next Agent Role]

[Clear, actionable steps for the next agent. Be specific about which files to read.]

1. **Read:** [specific file path] - [why this file is important]
2. **Analyze:** [what to look for or understand]
3. **Create:** [what outputs are expected]

## Questions to Resolve

[OPTIONAL - Only include if there are genuinely unresolved questions that need answers before proceeding. If everything is clear, omit this section entirely.]

- [Question 1]
- [Question 2]

## Sign-Off

**Status:** [✓ Complete / ⏳ In Progress / ⚠️ Blocked]
**Artifacts Created:** [number of files]
**Coverage:** [e.g., "All 3 use cases covered" or "2/2 services defined"]
**Ready for:** [next agent role or activity]

---

## GUIDELINES FOR WRITING BRIEFS

### DO:
- Keep the entire brief under 100 lines
- Focus on signposting and context, not content summary
- List artifacts with their PURPOSE, not their CONTENTS
- Reference files explicitly so agents know what to load
- Include only decisions that affect downstream activities

### DO NOT:
- Repeat or summarize the content of artifacts (agents will read them directly)
- Include detailed technical specifications (those belong in the artifacts)
- Copy acceptance criteria, workflows, or data contracts into the brief
- Create long explanations of what's already documented elsewhere
- List every single detail from the activity (be selective)

### REMEMBER:
A brief is a **work order and context document**, not a **comprehensive summary**.
Think of it as a cover letter that points to attachments, not a report that repeats them.
