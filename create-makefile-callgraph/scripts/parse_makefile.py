#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import argparse
from enum import StrEnum
import re
from collections import defaultdict

class OutputFormat(StrEnum):
    DOT = 'dot'
    MERMAID = 'mermaid'
    BOTH = 'both'
    SUMMARY = 'summary'

def parse_makefile(filepath):
    """Parse a Makefile and extract targets with their dependencies."""
    targets = {}
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern to match target definitions: target: dependencies
    # This handles both phony and file targets
    target_pattern = r'^([a-zA-Z0-9_/.@-]+):\s*([^\n]*?)(?:\s*##.*)?$'
    
    for match in re.finditer(target_pattern, content, re.MULTILINE):
        target = match.group(1)
        deps_str = match.group(2).strip()
        
        # Parse dependencies (space-separated)
        deps = [d.strip() for d in deps_str.split() if d.strip()]
        
        targets[target] = deps
    
    # Also look for $(MAKE) calls within target recipes
    make_calls = defaultdict(list)
    current_target = None
    
    for line in content.split('\n'):
        # Check if this is a target line
        if re.match(r'^[a-zA-Z0-9_/.@-]+:', line):
            match = re.match(r'^([a-zA-Z0-9_/.@-]+):', line)
            if match:
                current_target = match.group(1)
        # Check for $(MAKE) calls in recipe lines (must start with tab)
        elif line.startswith('\t') and current_target:
            # Look for $(MAKE) target or $(MAKE) -C dir target
            make_match = re.search(r'\$\(MAKE\)(?:\s+-C\s+([^\s]+))?\s+([a-zA-Z0-9_/-]+)', line)
            if make_match:
                subdir = make_match.group(1)
                subtarget = make_match.group(2)
                if subdir:
                    make_calls[current_target].append(f"{subdir}/{subtarget}")
                else:
                    make_calls[current_target].append(subtarget)
    
    return targets, make_calls

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
    return parser.parse_args()

def main():
    arg_ns = parse_args()
    makefile_path = arg_ns.makefile_path
    
    targets, make_calls = parse_makefile(makefile_path)
    
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
    print()
    
    print("TARGETS AND DEPENDENCIES:")
    print("-" * 80)
    for target, deps in sorted(targets.items()):
        if deps:
            print(f"{target}: {' '.join(deps)}")
        else:
            print(f"{target}: (no dependencies)")
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
