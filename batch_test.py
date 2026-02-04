#!/usr/bin/env python3
"""
Batch Workload Tester
=====================

Tests multiple workload JSON files with different system configurations
and generates a comparison report.

Usage:
    python batch_test.py [workload_directory]
    python batch_test.py workloads/
"""

import json
import sys
import os
from pathlib import Path
from tabulate import tabulate

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from test_yolov8 import YOLOv8Scheduler


def find_json_files(directory):
    """Find all JSON files in directory"""
    path = Path(directory)
    if not path.exists():
        print(f"❌ Directory '{directory}' not found")
        sys.exit(1)
    
    json_files = list(path.glob('*.json'))
    if not json_files:
        print(f"❌ No JSON files found in '{directory}'")
        sys.exit(1)
    
    return json_files


def load_workload(filepath):
    """Load workload from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Warning: Could not load {filepath}: {str(e)}")
        return None


def schedule_workload(workload, bandwidth, latency):
    """Schedule a workload with given parameters"""
    try:
        # Get processor types
        processor_types = list(workload['nodes'][0]['costs'].keys())
        
        config = {
            "workload": {
                "nodes": workload['nodes'],
                "edges": workload.get('edges', [])
            },
            "system_config": {
                "processors": {proc: {"performance_GFLOPS": 1.0} for proc in processor_types},
                "bandwidth_MBps": bandwidth,
                "latency_ms": latency
            }
        }
        
        scheduler = YOLOv8Scheduler(json.dumps(config))
        return scheduler.optimize()
    except Exception as e:
        print(f"⚠️  Warning: Scheduling failed: {str(e)}")
        return None


def main():
    # Determine directory to scan
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = 'workloads'
    
    print("="*80)
    print("BATCH WORKLOAD TESTING")
    print("="*80)
    print(f"\nScanning directory: {directory}")
    
    # Find all JSON files
    json_files = find_json_files(directory)
    print(f"Found {len(json_files)} workload file(s)\n")
    
    # Test configurations
    configs = [
        ("High-Speed", 2000, 1),
        ("Medium", 1000, 2),
        ("Low-Speed", 500, 5)
    ]
    
    # Store results
    all_results = []
    
    # Process each workload
    for json_file in sorted(json_files):
        workload = load_workload(json_file)
        if workload is None:
            continue
        
        workload_id = workload.get('workload_id', json_file.stem)
        num_tasks = len(workload.get('nodes', []))
        num_edges = len(workload.get('edges', []))
        
        print(f"\n{'='*80}")
        print(f"Workload: {workload_id}")
        print(f"  File: {json_file.name}")
        print(f"  Tasks: {num_tasks}, Dependencies: {num_edges}")
        print(f"{'='*80}\n")
        
        # Get processor types
        if workload.get('nodes'):
            proc_types = ', '.join(workload['nodes'][0]['costs'].keys())
            print(f"  Processors: {proc_types}")
        
        # Test with different configurations
        workload_results = []
        
        for config_name, bandwidth, latency in configs:
            results = schedule_workload(workload, bandwidth, latency)
            
            if results:
                makespan = results['makespan_ms']
                fps = 1000 / makespan
                
                # Calculate speedup vs best single processor
                processor_types = list(workload['nodes'][0]['costs'].keys())
                single_proc_times = {
                    proc: sum(node['costs'].get(proc, float('inf')) for node in workload['nodes'])
                    for proc in processor_types
                }
                best_single = min(single_proc_times.values())
                speedup = best_single / makespan
                
                workload_results.append([
                    config_name,
                    f"{bandwidth} MB/s",
                    f"{latency} ms",
                    f"{makespan:.2f} ms",
                    f"{fps:.2f} ops/s",
                    f"{speedup:.2f}x"
                ])
                
                # Store for summary
                all_results.append({
                    'workload': workload_id,
                    'file': json_file.name,
                    'config': config_name,
                    'makespan': makespan,
                    'fps': fps,
                    'speedup': speedup,
                    'mapping': results['mapping']
                })
        
        if workload_results:
            headers = ["Configuration", "Bandwidth", "Latency", "Makespan", "Throughput", "Speedup"]
            print(f"\n{tabulate(workload_results, headers=headers, tablefmt='grid')}\n")
    
    # Generate summary comparison
    if all_results:
        print(f"\n{'='*80}")
        print("SUMMARY: ALL WORKLOADS COMPARISON")
        print(f"{'='*80}\n")
        
        # Group by configuration
        for config_name, _, _ in configs:
            config_results = [r for r in all_results if r['config'] == config_name]
            
            if config_results:
                print(f"\n{config_name} Configuration:")
                print("-"*80)
                
                summary_data = [
                    [
                        r['workload'][:30],  # Truncate long names
                        f"{r['makespan']:.2f} ms",
                        f"{r['fps']:.2f} ops/s",
                        f"{r['speedup']:.2f}x"
                    ]
                    for r in config_results
                ]
                
                headers = ["Workload", "Makespan", "Throughput", "Speedup"]
                print(tabulate(summary_data, headers=headers, tablefmt='grid'))
        
        # Save detailed results
        output_file = 'batch_test_results.json'
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✓ Detailed results saved to: {output_file}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        from tabulate import tabulate
    except ImportError:
        print("❌ Error: 'tabulate' package required")
        print("   Install with: pip install tabulate")
        sys.exit(1)
    
    main()
