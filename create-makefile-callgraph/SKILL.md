---
name: create-makefile-callgraph
description: Create a call graph of all the makefile targets in the current directory and in any subdirectories
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
---

## What I do

- Start at the current directory and search through all subdirectories for Makefiles
    - `find . -name "Makefile" -type "f"`
- The script in `scripts/parse_makefile.py` will parse each Makefile and...
    - Make a list of the targets in each makefile
    - Make a call graph of the targets in each makefile
        - If a target calls another target, draw an edge from the calling target to the called target
        - If a target calls a target in another makefile, draw an edge from the calling target to the called target
            - Include the path to the called target in the edge label
    - Output the call graph in a format that can be visualized with a graph visualization tool, such as Graphviz or Mermaid
        - For Graphviz, output the call graph in DOT format
        - For Mermaid, output the call graph in Mermaid syntax
    - If there are circular dependencies between targets, report those circular dependencies
    - It is recommended to run the script with the `--no-src` flag to ignore source file dependencies and only show target-to-target relationships, as this will make the call graph easier to read and understand
    - It is recommended to run the script with the `--format mermaid` flag to output the call graph in Mermaid syntax, as this will allow you to easily visualize the call graph in a Markdown file or in a Mermaid live editor
- When the script is complete...
    - Show the user a summary of the analysis, including the number of makefiles parsed, the number of targets found, and any circular dependencies detected
    - Display the call graph in the specified output format (DOT or Mermaid)

## When to use me

After making many batch changes to one makefile or many makefiles
Before pushing a branch with changes to one makefile or many makefiles
When researching a project for the first time
If a developer is unfamiliar with a project
