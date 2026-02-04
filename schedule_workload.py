#!/usr/bin/env python3
"""
CADO Scheduler - Command Line Tool
===================================

Usage:
    python schedule_workload.py <workload.json> [--bandwidth 1000] [--latency 2] [--output results.json]

Examples:
    python schedule_workload.py my_workload.json
    python schedule_workload.py my_workload.json --bandwidth 500 --latency 5
    python schedule_workload.py my_workload.json --output my_results.json
"""

import json
import sys
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test_yolov8 import YOLOv8Scheduler


def load_workload(filepath):
    """Load workload from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{filepath}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{filepath}'")
        print(f"   {str(e)}")
        sys.exit(1)


def create_config(workload, bandwidth, latency):
    """Convert workload to scheduler config"""
    # Extract processor types from first node
    if not workload.get('nodes'):
        print("❌ Error: Workload must have 'nodes' array")
        sys.exit(1)
    
    first_node = workload['nodes'][0]
    if 'costs' not in first_node:
        print("❌ Error: Nodes must have 'costs' dictionary")
        sys.exit(1)
    
    processor_types = list(first_node['costs'].keys())
    
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
    
    return config


def print_workload_info(workload):
    """Print workload summary"""
    print("\n" + "="*80)
    print("WORKLOAD SUMMARY")
    print("="*80)
    
    workload_id = workload.get('workload_id', 'Unknown')
    print(f"\nWorkload ID: {workload_id}")
    print(f"Number of Tasks: {len(workload.get('nodes', []))}")
    print(f"Number of Dependencies: {len(workload.get('edges', []))}")
    
    # Get processor types
    if workload.get('nodes'):
        processor_types = list(workload['nodes'][0]['costs'].keys())
        print(f"Processor Types: {', '.join(processor_types)}")
    
    print("\nTasks:")
    print("-"*80)
    for node in workload.get('nodes', []):
        node_id = node['id']
        costs = node.get('costs', {})
        desc = node.get('description', 'No description')
        
        print(f"\n  {node_id}")
        if desc:
            print(f"    Description: {desc}")
        print(f"    Costs: {', '.join([f'{proc}={cost}ms' for proc, cost in costs.items()])}")
    
    if workload.get('edges'):
        print("\nDependencies:")
        print("-"*80)
        for edge in workload['edges']:
            from_node = edge['from']
            to_node = edge['to']
            data_size = edge.get('data_size_MB', 0)
            name = edge.get('name', '')
            
            print(f"  {from_node} → {to_node}: {data_size:.2f} MB", end='')
            if name:
                print(f" ({name})", end='')
            print()


def print_results(results, workload, bandwidth, latency):
    """Print scheduling results"""
    print("\n" + "="*80)
    print("SCHEDULING RESULTS")
    print("="*80)
    
    print(f"\nSystem Configuration:")
    print(f"  Bandwidth: {bandwidth} MB/s")
    print(f"  Latency: {latency} ms")
    
    print(f"\n✓ Total Makespan: {results['makespan_ms']:.2f} ms")
    
    # Calculate FPS if this looks like a video/image workload
    fps = 1000 / results['makespan_ms']
    print(f"✓ Throughput: {fps:.2f} operations/second")
    
    print(f"\nTask-to-Processor Mapping:")
    print("-"*80)
    print(f"{'Task':<20} {'Processor':<12} {'Start (ms)':<12} {'End (ms)':<12} {'Duration (ms)'}")
    print("-"*80)
    
    for node in workload['nodes']:
        node_id = node['id']
        proc = results['mapping'][node_id]
        sched = results['detailed_schedule'][node_id]
        
        print(f"{node_id:<20} {proc:<12} {sched['start_time_ms']:>10.2f}  "
              f"{sched['end_time_ms']:>10.2f}  {sched['duration_ms']:>10.2f}")
    
    # Calculate processor utilization
    proc_utilization = {}
    makespan = results['makespan_ms']
    
    for node_id, sched in results['detailed_schedule'].items():
        proc = sched['processor']
        duration = sched['duration_ms']
        
        if proc not in proc_utilization:
            proc_utilization[proc] = 0
        proc_utilization[proc] += duration
    
    print(f"\nProcessor Utilization:")
    print("-"*80)
    for proc in sorted(proc_utilization.keys()):
        util_time = proc_utilization[proc]
        util_pct = (util_time / makespan) * 100
        print(f"  {proc}: {util_pct:5.1f}% ({util_time:.2f} ms / {makespan:.2f} ms)")
    
    # Calculate best single-processor time
    processor_types = list(workload['nodes'][0]['costs'].keys())
    single_proc_times = {}
    
    for proc in processor_types:
        total = sum(node['costs'].get(proc, float('inf')) for node in workload['nodes'])
        single_proc_times[proc] = total
    
    best_single_proc = min(single_proc_times, key=single_proc_times.get)
    best_single_time = single_proc_times[best_single_proc]
    
    speedup = best_single_time / makespan
    
    print(f"\nPerformance Comparison:")
    print("-"*80)
    print(f"  Best Single-Processor: {best_single_time:.2f} ms ({best_single_proc})")
    print(f"  Multi-Processor (HEFT): {makespan:.2f} ms")
    print(f"  Speedup: {speedup:.2f}x")
    
    # Calculate communication overhead
    total_compute = sum(sched['duration_ms'] for sched in results['detailed_schedule'].values())
    comm_overhead = makespan - total_compute
    
    if comm_overhead > 0:
        comm_pct = (comm_overhead / makespan) * 100
        print(f"\nCommunication Overhead:")
        print("-"*80)
        print(f"  Overhead: {comm_overhead:.2f} ms ({comm_pct:.1f}% of total time)")


def save_results(results, output_file):
    """Save results to JSON file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {output_file}")
    except Exception as e:
        print(f"\n❌ Error saving results: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Schedule workloads using the CADO HEFT algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s workload.json
  %(prog)s workload.json --bandwidth 500 --latency 5
  %(prog)s workload.json -b 2000 -l 1 -o results.json
  %(prog)s workload.json --quiet --output results.json

For workload JSON format, see YOLOV8_USAGE_GUIDE.md
        """
    )
    
    parser.add_argument('workload', 
                       help='Path to workload JSON file')
    parser.add_argument('-b', '--bandwidth', 
                       type=float, 
                       default=1000,
                       help='Inter-processor bandwidth in MB/s (default: 1000)')
    parser.add_argument('-l', '--latency', 
                       type=float, 
                       default=2,
                       help='Inter-processor latency in ms (default: 2)')
    parser.add_argument('-o', '--output', 
                       help='Save results to JSON file')
    parser.add_argument('-q', '--quiet', 
                       action='store_true',
                       help='Suppress detailed output, only show summary')
    
    args = parser.parse_args()
    
    # Load workload
    workload = load_workload(args.workload)
    
    # Print workload info unless quiet
    if not args.quiet:
        print_workload_info(workload)
    
    # Create config and run scheduler
    config = create_config(workload, args.bandwidth, args.latency)
    
    if not args.quiet:
        print("\n" + "="*80)
        print("RUNNING HEFT SCHEDULER...")
        print("="*80)
    
    scheduler = YOLOv8Scheduler(json.dumps(config))
    results = scheduler.optimize()
    
    # Print results
    if not args.quiet:
        print_results(results, workload, args.bandwidth, args.latency)
        print("="*80 + "\n")
    else:
        # Just print summary
        print(f"Makespan: {results['makespan_ms']:.2f} ms")
        print(f"Mapping: {results['mapping']}")
    
    # Save results if requested
    if args.output:
        save_results(results, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
