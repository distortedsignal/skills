---
name: document-code-in-readme-files
description: Find all README.md files and comprehensively document the code structure, intent, data structures, and design patterns
license: MIT
compatibility: opencode
metadata:
  audience: developers, maintainers
---

# What I do

This skill performs a comprehensive documentation workflow for all README.md files in a project:

## Phase 1: Discovery
- Find all README.md files in the current directory and subdirectories using glob pattern `**/README.md`
- Create a task list tracking each README file to be updated
- Set up todo tracking for the entire documentation process

## Phase 2: Analysis
- Use the Task tool with the `explore` subagent to perform a thorough codebase analysis
- For each directory containing a README, analyze:
  - **Main purpose/intent**: What problem does this component solve?
  - **Directory structure**: How is the code organized?
  - **Critical data structures**: Key classes, interfaces, types, models, schemas
  - **Design patterns**: Architectural patterns being used (e.g., Repository Pattern, Service Layer, Microservices)
  - **Key architectural decisions**: Important technology and design choices
  - **Technology stack**: Frameworks, libraries, and tools used

## Phase 3: Documentation
For each README.md file, update or create comprehensive documentation including:

### Required Sections
1. **Title and Overview**: Clear, concise description of the component
2. **Intent**: What this component aims to accomplish and why it exists
3. **Architecture & Structure**: 
   - Visual architecture diagrams (ASCII art)
   - Directory structure with file descriptions
   - Component relationships and data flow
4. **Critical Data Structures**:
   - Database schemas (if applicable)
   - Key models/classes with field descriptions
   - API request/response structures
   - Configuration objects
5. **Design Patterns**:
   - Patterns used (e.g., Repository, Service Layer, Factory, Singleton)
   - Rationale for each pattern
   - Code examples showing pattern implementation
6. **Technology Stack**: Table of technologies with purposes
7. **Getting Started**: Prerequisites, installation, and setup instructions
8. **Development**: Development workflow and commands
9. **API Documentation**: Endpoints and usage examples (if applicable)
10. **Troubleshooting**: Common issues and solutions

### Documentation Quality Standards
- Use clear, professional language
- Include code examples where helpful
- Add ASCII diagrams for architecture visualization
- Provide specific file paths with line numbers when referencing code
- Document the "why" behind design decisions, not just the "what"
- Keep content up-to-date with actual codebase structure
- Preserve existing useful content while enhancing it

## Phase 4: Verification
- Mark each README as completed in the todo list as it's updated
- Track progress throughout the entire process
- Provide a summary of all changes made

# When to use me

Use this skill when:
- Starting work on a new project with poor or missing documentation
- After major architectural changes that need to be documented
- Preparing a project for handoff to new team members
- During code reviews when documentation is found lacking
- Creating documentation for open-source projects
- When onboarding developers need comprehensive project understanding
- Before major releases to ensure documentation is current

# Best practices

## Before Running
- Ensure the codebase is in a stable state (committed changes)
- Have a clear understanding of the project's high-level architecture
- Identify any existing documentation standards in the project

## During Execution
- Review the analysis output before documentation to ensure accuracy
- Let the skill complete the analysis phase fully before documentation begins
- Check that generated documentation matches actual codebase structure
- Verify that design patterns identified are accurate

## After Running
- Review all updated README files for accuracy
- Check that code examples compile/run
- Ensure architecture diagrams accurately reflect the system
- Verify that all file paths and references are correct
- Commit the updated documentation with a clear commit message

# Output format

The skill updates README.md files in place with the following structure:

```markdown
# Component Name

Brief description

## Overview
Comprehensive overview paragraph(s)

## Intent
Purpose and goals of this component

## Architecture & Structure
### Architecture Diagram
[ASCII diagram]

### Directory Structure
[Tree structure with descriptions]

## Critical Data Structures
### Structure Name
Description and code example

## Design Patterns
### Pattern Name
Explanation and rationale

## Technology Stack
| Component | Technology | Purpose |
|-----------|-----------|---------|

## Getting Started
Prerequisites and setup steps

## Development
Development workflow

## API Documentation (if applicable)
Endpoints and examples

## Troubleshooting
Common issues and solutions

## License
License information
```

# Examples

## Example 1: Monorepo with Multiple Services
```
project/
├── README.md                    # Root overview
├── frontend/
│   └── README.md               # UI documentation
├── backend/
│   ├── README.md               # Backend overview
│   ├── api-service/
│   │   └── README.md           # API service details
│   └── data-service/
│       └── README.md           # Data service details
└── infrastructure/
    └── README.md               # Deployment docs
```

The skill will:
1. Find all 6 README files
2. Analyze each directory's codebase
3. Update each README with comprehensive documentation
4. Ensure consistency across all READMEs

## Example 2: Single Service Project
```
my-service/
├── README.md                   # Main documentation
└── src/
    └── [source files]
```

The skill will:
1. Find the root README
2. Analyze the entire codebase structure
3. Document architecture, patterns, and data structures
4. Add setup and development instructions

# Technical implementation notes

## Analysis Approach
- Uses the `explore` subagent for codebase analysis to handle large projects efficiently
- Analyzes code context rather than just file names
- Identifies patterns by examining actual code structure
- Extracts data structures by reading model/schema definitions

## Documentation Strategy
- Preserves existing useful content (like setup instructions)
- Enhances rather than replaces when READMEs already exist
- Uses consistent formatting across all READMEs
- Includes both high-level (architecture) and low-level (code) details

## Quality Assurance
- Tracks progress with todo list to ensure no README is missed
- Marks items complete immediately after updating
- Provides summary of all work done
- Validates that documentation matches actual code structure

# Limitations

- Does not automatically update documentation when code changes (requires re-running)
- May need manual review for highly specialized or domain-specific patterns
- ASCII diagrams have limited visual complexity
- Generated documentation reflects current state, not historical context
- Requires sufficient context about the codebase to generate accurate documentation

# Related skills

- **test-all-makefile-targets**: Document build system alongside code structure
- **create-makefile-callgraph**: Visualize build dependencies to include in architecture docs
