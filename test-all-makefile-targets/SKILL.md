---
name: test-all-makefile-targets
description: Test all the makefile targets in the current directory and in any subdirectories
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
---

## What I do

- Start at the current directory and search through all subdirectories for Makefiles
    - `find . -name "Makefile" -type "f"`
- Make a list of the targets in each makefile that only affect the user's host
- Only test one Makefile at a time
    - Start with the Makefile closest to the root directory and work further from the root directory
- Run each target in dry-run mode
    - If the result of the dry-run of the target is non-zero, report that result as a failure
    - If the result of the dry-run of the target is zero, report that result as a success
- For the targets that only affect the user's host, run each target
    - If the result of the target is non-zero, report that result as a failure
    - If the result of the target is zero, report that result as a success
    - If there are targets that build docker images, ask how long the user would like to wait for the docker build to complete and use that as a timeout for any make targets that invoke a docker build
- When a target fails, continue testing the remaining targets

## When to use me

After making many batch changes to one makefile or many makefiles
Before pushing a branch with changes to one makefile or many makefiles
When researching a project for the first time
If a developer is unfamiliar with a project
