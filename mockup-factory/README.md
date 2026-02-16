# Mockup Factory

This guide explains how to use the **Mockup Factory** to generate consistent professional HTML mockups for laboratory information technology applications using AI assistance.

## Overview

The Mockup Factory helps you create:
- **Use Cases**: Define interactions between lab actors (LIS, instruments, staff, systems)
- **Mockup Descriptions**: Detailed specifications of user interface screens
- **HTML Mockups**: Working HTML prototypes based on mockup descriptions

Examples of mockup descriptions and generated mockups are available in the `samples/` folder.

## Why a Multi-Step Approach?

The structured workflow provides two key benefits:

1. **Leverage AI domain knowledge**: When defining use cases, the LLM can apply its broad knowledge of laboratory workflows, clinical processes, and best practices to suggest realistic interactions and edge cases you might not have considered.

2. **Finalize before implementation**: By completing the mockup description before generating HTML, you ensure the LLM creates exactly what you need. This prevents generating mockups that only remotely match your vision, saving time and iterations.

## Workflow

### Step 1: Load Context Files

Load the following prompt files into your AI assistant:
- `0.prompt - product brief.txt` - Product overview and application catalog
- `1.prompt - IDN description.txt` - Standard lab environment (sites, equipment, users)
- `2.prompt - Use Case guidelines.txt` - Use case structure and format
- `3.prompt - Mockup Description Guidelines.txt` - Mockup description template
- `4.prompt - Mockup Generation Guidelines.txt` - HTML generation rules (Bootstrap 5)

### Step 2 (Optional): Define Use Case

If your mockup requires understanding complex workflows, define a use case first:

**Example request:**
```
Can you create a use case for saline replacement on a lipemic hematology sample?
```

The AI will generate a structured use case showing:
- Title and problem statement
- User needs
- Step-by-step interactions between actors

Review and iterate as needed before proceeding to mockup description.

### Step 3: Generate Mockup Description

Ask the AI to create a mockup description.

**Example request:**
```
Can you generate a mockup description of a screen to audit configuration changes? 
I want to review changes associated with the sodium test. It should include:
- First area: Define which configuration element to audit (test "Sodium")
- Second area: List of configuration changes (unit, rule, range, LIS code) 
  with columns: who, when, configuration element, value before, value after
```

Review the mockup description and request changes as needed. Iterate until satisfied.

### Step 4: Generate HTML Mockup

Once the mockup description is finalized, ask the AI to generate the HTML:

**Example request:**
```
Can you generate the HTML mockup based on this description?
```

### Step 5: Test and Refine

1. Copy the generated HTML code
2. Save it as an `.html` file on your computer
3. Double-click the file to open it in your browser
4. Review the mockup
5. Request modifications from the AI if needed
6. Copy the updated HTML code and replace the content in your file

## Tips

- **Be specific**: Provide clear details about what you want to see on the screen
- **Iterate gradually**: Make incremental changes rather than requesting everything at once
- **Use standard elements**: Leverage the defined lab environment (sites, users, instruments) for consistency
- **Reference applications**: Refer to the 15 applications in the product brief for context

## File Structure

```
mockup-factory/
├── 0.prompt - product brief.txt          # Product & application overview
├── 1.prompt - IDN description.txt        # Lab environment setup
├── 2.prompt - Use Case guidelines.txt    # Use case template
├── 3.prompt - Mockup Description Guidelines.txt  # Mockup spec template
├── 4.prompt - Mockup Generation Guidelines.txt   # HTML generation rules
├── README.md                              # This file
└── samples/                               # Example mockups
    ├── app-launcher/
    │   ├── 01-mockup-description-app-launcher.txt
    │   └── 02-mockup-app-launcher.html
    └── saline-replacement/
        ├── 01-use-case-saline-replacement.txt
        ├── 02-mockup-description-saline-replacement.txt
        └── 03-mokcup-sample-review.html
```

## Notes

- All mockups use Bootstrap 5.3.2 for consistent styling
- The defined lab environment ensures realistic and consistent mockups
- Mockup descriptions are text-only; HTML is generated separately
