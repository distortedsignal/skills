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
- Make a list of the targets in each makefile
- Make a call graph of the targets in each makefile
    - If a target calls another target, draw an edge from the calling target to the called target
    - If a target calls a target in another makefile, draw an edge from the calling target to the called target
        - Include the path to the called target in the edge label
- Output the call graph in a format that can be visualized with a graph visualization tool, such as Graphviz or Mermaid
    - For Graphviz, output the call graph in DOT format
    - For Mermaid, output the call graph in Mermaid syntax
- If there are circular dependencies between targets, report those circular dependencies

## When to use me

After making many batch changes to one makefile or many makefiles
Before pushing a branch with changes to one makefile or many makefiles
When researching a project for the first time
If a developer is unfamiliar with a project
