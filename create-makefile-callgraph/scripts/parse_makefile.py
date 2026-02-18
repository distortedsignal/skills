#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import argparse
from enum import StrEnum
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

class OutputFormat(StrEnum):
    DOT = 'dot'
    MERMAID = 'mermaid'
    BOTH = 'both'
    SUMMARY = 'summary'

def parse_makefile_with_make(makefile_path):
    """
    Parse a Makefile using 'make -pn' to get the expanded database.
    This handles variable expansion, implicit rules, and complex makefiles accurately.
    """
    makefile_path = Path(makefile_path).resolve()
    makefile_dir = makefile_path.parent
    makefile_name = makefile_path.name
    
    # Run make -pn to get the database
    # -p: print database
    # -n: dry run (don't execute)
    # -f: specify makefile
    try:
        cmd = ['make', '-pn', '-f', str(makefile_path)]
        result = subprocess.run(
            cmd,
            cwd=makefile_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
    except subprocess.TimeoutExpired:
        print(f"Error: make -pn timed out after 30 seconds", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running make -pn: {e}", file=sys.stderr)
        print(f"stdout: {e.stdout}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'make' command not found. Please ensure GNU Make is installed.", file=sys.stderr)
        sys.exit(1)
    
    return parse_make_database(output, makefile_dir)

def parse_make_database(make_output, makefile_dir):
    """
    Parse the output of 'make -pn' to extract targets and dependencies.
    """
    targets = {}
    make_calls = defaultdict(list)
    phony_targets = set()
    
    # Common make internal variables and targets to skip
    SKIP_TARGETS = {
        '.DEFAULT', '.SUFFIXES', '.INTERMEDIATE', '.SECONDARY', 
        '.PRECIOUS', '.IGNORE', '.SILENT', '.EXPORT_ALL_VARIABLES',
        '.NOTPARALLEL', '.ONESHELL', '.POSIX', 'Makefile',
        'GNUmakefile', 'makefile'
    }
    
    # Common make variables to skip
    SKIP_VARS = {
        'MAKEFILES', 'MAKEFILE_LIST', 'CURDIR', 'SHELL', 'MAKE',
        'MAKELEVEL', 'MAKEFLAGS', 'MFLAGS', 'MAKE_VERSION',
        'MAKE_COMMAND', '.DEFAULT_GOAL', '.VARIABLES', '.FEATURES',
        'VPATH', '.INCLUDE_DIRS', '.RECIPEPREFIX', 'MAKECMDGOALS'
    }
    
    lines = make_output.split('\n')
    i = 0
    current_target = None
    current_recipe = []
    in_database_section = False
    
    while i < len(lines):
        line = lines[i]
        
        # Detect when we enter the database section
        if line.startswith('# Files'):
            in_database_section = True
            i += 1
            continue
        
        # Skip lines before database section
        if not in_database_section:
            # Still look for .PHONY declarations in the early output
            if '.PHONY:' in line or line.startswith('.PHONY'):
                phony_match = re.search(r'\.PHONY:\s*(.+)', line)
                if phony_match:
                    phony_list = phony_match.group(1).strip().split()
                    phony_targets.update(phony_list)
            i += 1
            continue
        
        # Skip comment lines and empty lines in database section
        if line.startswith('#') or not line.strip():
            i += 1
            continue
        
        # Look for .PHONY declarations
        if '.PHONY:' in line or line.startswith('.PHONY'):
            phony_match = re.search(r'\.PHONY:\s*(.+)', line)
            if phony_match:
                phony_list = phony_match.group(1).strip().split()
                phony_targets.update(phony_list)
            i += 1
            continue
        
        # Match target lines: "target: dependencies"
        target_match = re.match(r'^([^#:\s][^:]*?):\s*(.*)$', line)
        
        if target_match:
            target = target_match.group(1).strip()
            deps_str = target_match.group(2).strip()
            
            # Skip if it's a variable assignment (contains =)
            if '=' in line and ':' in line:
                # Check if = comes before :
                eq_pos = line.index('=')
                colon_pos = line.index(':')
                if eq_pos < colon_pos:
                    i += 1
                    continue
            
            # Skip internal make targets
            if target in SKIP_TARGETS:
                i += 1
                continue
            
            # Skip internal make variables
            if target in SKIP_VARS:
                i += 1
                continue
            
            # Skip targets that look like variable assignments
            if target.isupper() and ' ' not in target:
                # Likely a variable like BLUE, GREEN, etc.
                i += 1
                continue
            
            # Skip targets that contain absolute paths from the make database
            if target.startswith('/'):
                i += 1
                continue
            
            # Skip pattern rules
            if '%' in target:
                i += 1
                continue
            
            # Skip internal targets (start with .)
            if target.startswith('.') and target not in ['.PHONY']:
                i += 1
                continue
            
            # Parse dependencies
            deps = []
            if deps_str:
                # Remove comments from dependency line
                deps_str = re.sub(r'#.*$', '', deps_str).strip()
                # Split on whitespace
                deps = [d.strip() for d in deps_str.split() if d.strip()]
            
            # Store target and dependencies
            if target not in targets:
                targets[target] = []
            targets[target].extend(deps)
            
            current_target = target
            current_recipe = []
            
            # Look ahead for recipe lines (start with # in dry-run output)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # Recipe lines in make -pn output start with #
                if next_line.startswith('#'):
                    recipe_line = next_line[1:].strip()
                    current_recipe.append(recipe_line)
                    j += 1
                elif next_line.strip() == '':
                    j += 1
                else:
                    break
            
            # Parse recipe for $(MAKE) calls
            for recipe_line in current_recipe:
                # Look for $(MAKE) or ${MAKE} calls
                make_match = re.search(r'\$[\({]MAKE[\)}](?:\s+-C\s+([^\s]+))?\s+([a-zA-Z0-9_/-]+)', recipe_line)
                if make_match:
                    subdir = make_match.group(1)
                    subtarget = make_match.group(2)
                    if subdir:
                        make_calls[current_target].append(f"{subdir}/{subtarget}")
                    else:
                        make_calls[current_target].append(subtarget)
            
            i = j
        else:
            i += 1
    
    # Remove duplicates from dependencies
    for target in targets:
        targets[target] = list(dict.fromkeys(targets[target]))
    
    return targets, make_calls, phony_targets

def parse_makefile(filepath):
    """
    Parse a Makefile and extract targets with their dependencies.
    This is the main entry point that uses make -pn for accurate parsing.
    """
    targets, make_calls, phony_targets = parse_makefile_with_make(filepath)
    return targets, make_calls, phony_targets

def find_cycles(graph):
    """Find all cycles in the dependency graph using DFS."""
    cycles = []
    visited = set()
    rec_stack = []
    
    def dfs(node, path):
        if node in rec_stack:
            # Found a cycle
            cycle_start = rec_stack.index(node)
            cycle = rec_stack[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.append(node)
        
        if node in graph:
            for dep in graph[node]:
                dfs(dep, path + [dep])
        
        rec_stack.pop()
    
    for node in graph:
        if node not in visited:
            dfs(node, [node])
    
    return cycles

def generate_dot(targets, make_calls, makefile_path):
    """Generate Graphviz DOT format."""
    dot = ['digraph MakefileCallGraph {']
    dot.append('  rankdir=LR;')
    dot.append('  node [shape=box, style=rounded];')
    dot.append('')
    
    # Add title
    dot.append(f'  labelloc="t";')
    dot.append(f'  label="Makefile Call Graph\\n{makefile_path}";')
    dot.append('')
    
    # Track all nodes
    all_nodes = set()
    
    # Add edges for direct dependencies
    for target, deps in targets.items():
        all_nodes.add(target)
        for dep in deps:
            all_nodes.add(dep)
            dot.append(f'  "{target}" -> "{dep}";')
    
    # Add edges for $(MAKE) calls
    for target, calls in make_calls.items():
        all_nodes.add(target)
        for call in calls:
            all_nodes.add(call)
            # Use different style for cross-makefile calls
            if '/' in call:
                dot.append(f'  "{target}" -> "{call}" [style=dashed, color=blue, label="make -C"];')
            else:
                dot.append(f'  "{target}" -> "{call}" [color=green, label="recursive make"];')
    
    dot.append('}')
    return '\n'.join(dot)

def generate_mermaid(targets, make_calls):
    """Generate Mermaid format."""
    mermaid = ['graph LR']
    
    # Add edges for direct dependencies
    for target, deps in targets.items():
        target_id = target.replace('.', '_').replace('/', '_')
        for dep in deps:
            dep_id = dep.replace('.', '_').replace('/', '_')
            mermaid.append(f'  {target_id}["{target}"] --> {dep_id}["{dep}"]')
    
    # Add edges for $(MAKE) calls
    for target, calls in make_calls.items():
        target_id = target.replace('.', '_').replace('/', '_')
        for call in calls:
            call_id = call.replace('.', '_').replace('/', '_')
            if '/' in call:
                mermaid.append(f'  {target_id}["{target}"] -.->|"make -C"| {call_id}["{call}"]')
            else:
                mermaid.append(f'  {target_id}["{target}"] ==>|"recursive"| {call_id}["{call}"]')
    
    return '\n'.join(mermaid)

def parse_args():
    parser = argparse.ArgumentParser(description="Parse a Makefile and generate call graph in DOT and Mermaid formats.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('makefile_path', help="Path to the Makefile to parse")
    parser.add_argument('--format', '-f', 
                        choices=[e.value for e in OutputFormat],
                        default=OutputFormat.BOTH.value,
                        help=f"Output format (default: {OutputFormat.BOTH.value})\n"+
                        "NOTE: 'summary' will only print the analysis summary without graph outputs")
    parser.add_argument('--phony-only', '-p',
                        action='store_true',
                        help="Only show PHONY targets (ignores file targets)")
    parser.add_argument('--no-src', action='store_true',
                        help="Do not show source file dependencies (only targets and their relationships)")
    return parser.parse_args()

def main():
    arg_ns = parse_args()
    makefile_path = arg_ns.makefile_path
    
    targets, make_calls, phony_targets = parse_makefile(makefile_path)
    
    # Filter to only phony targets if requested
    if arg_ns.phony_only:
        filtered_targets = {k: v for k, v in targets.items() if k in phony_targets}
        # Also filter dependencies to only include phony targets
        for target in filtered_targets:
            filtered_targets[target] = [d for d in filtered_targets[target] if d in phony_targets]
        targets = filtered_targets
        
        filtered_make_calls = {k: v for k, v in make_calls.items() if k in phony_targets}
        make_calls = filtered_make_calls
    
    # Filter out source file dependencies if requested
    if arg_ns.no_src:
        for target in targets:
            targets[target] = [d for d in targets[target] if not re.match(r'src.*$', d)]
    
    # Build complete graph for cycle detection
    graph = {}
    for target, deps in targets.items():
        graph[target] = deps.copy()
    for target, calls in make_calls.items():
        if target not in graph:
            graph[target] = []
        graph[target].extend(calls)
    
    # Find cycles
    cycles = find_cycles(graph)
    
    print("=" * 80)
    print("MAKEFILE CALL GRAPH ANALYSIS")
    print("=" * 80)
    print()
    
    print(f"Makefile: {makefile_path}")
    print(f"Total targets: {len(targets)}")
    print(f"Phony targets: {len(phony_targets)}")
    if arg_ns.phony_only:
        print("(Showing PHONY targets only)")
    print()
    
    print("TARGETS AND DEPENDENCIES:")
    print("-" * 80)
    for target, deps in sorted(targets.items()):
        phony_marker = " [PHONY]" if target in phony_targets else ""
        if deps:
            print(f"{target}{phony_marker}: {' '.join(deps)}")
        else:
            print(f"{target}{phony_marker}: (no dependencies)")
    print()
    
    if make_calls:
        print("RECURSIVE MAKE CALLS:")
        print("-" * 80)
        for target, calls in sorted(make_calls.items()):
            for call in calls:
                print(f"{target} -> {call}")
        print()
    
    if cycles:
        print("⚠️  CIRCULAR DEPENDENCIES DETECTED:")
        print("-" * 80)
        for i, cycle in enumerate(cycles, 1):
            print(f"Cycle {i}: {' -> '.join(cycle)}")
        print()
    else:
        print("✓ No circular dependencies detected")
        print()
    

    if (arg_ns.format == OutputFormat.DOT.value) or (arg_ns.format == OutputFormat.BOTH.value):
        dot_output = generate_dot(targets, make_calls, makefile_path)
        print("=" * 80)
        print("GRAPHVIZ DOT FORMAT")
        print("=" * 80)
        print(dot_output)
        print()
    
    if (arg_ns.format == OutputFormat.MERMAID.value) or (arg_ns.format == OutputFormat.BOTH.value):
        mermaid_output = generate_mermaid(targets, make_calls)
        print("=" * 80)
        print("MERMAID FORMAT")
        print("=" * 80)
        print(mermaid_output)
        print()

if __name__ == '__main__':
    main()
