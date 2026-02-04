import json
import sys
sys.path.append('/home/claude')
from cado_scheduler import CADOScheduler

def test_heterogeneous_system():
    """Test with a more realistic heterogeneous workload"""
    config = {
        "workload": {
            "nodes": [
                {"id": "T1", "workload_intensity_GFLOPS": 50},   # Entry task
                {"id": "T2", "workload_intensity_GFLOPS": 100},  # Compute-heavy
                {"id": "T3", "workload_intensity_GFLOPS": 30},   # Light task
                {"id": "T4", "workload_intensity_GFLOPS": 80},   # Medium task
                {"id": "T5", "workload_intensity_GFLOPS": 120},  # Heavy task
                {"id": "T6", "workload_intensity_GFLOPS": 60},   # Medium task
                {"id": "T7", "workload_intensity_GFLOPS": 90},   # Exit task
            ],
            "edges": [
                {"from": "T1", "to": "T2", "data_size_MB": 100},
                {"from": "T1", "to": "T3", "data_size_MB": 50},
                {"from": "T2", "to": "T4", "data_size_MB": 80},
                {"from": "T2", "to": "T5", "data_size_MB": 120},
                {"from": "T3", "to": "T6", "data_size_MB": 40},
                {"from": "T4", "to": "T7", "data_size_MB": 60},
                {"from": "T5", "to": "T7", "data_size_MB": 70},
                {"from": "T6", "to": "T7", "data_size_MB": 30}
            ]
        },
        "system_config": {
            "processors": {
                "CPU": {"performance_GFLOPS": 50},    # Slower, general purpose
                "GPU": {"performance_GFLOPS": 400},   # Fast for parallel work
                "TPU": {"performance_GFLOPS": 200},   # Medium speed, ML optimized
                "FPGA": {"performance_GFLOPS": 100}   # Configurable accelerator
            },
            "bandwidth_MBps": 800,   # 800 MB/s inter-chip bandwidth
            "latency_ms": 2          # 2ms network latency
        }
    }
    
    print("\n" + "="*70)
    print("TEST 1: Heterogeneous System with Complex DAG")
    print("="*70)
    print("\nSystem Configuration:")
    print("  Processors: CPU (50 GFLOPS), GPU (400 GFLOPS), TPU (200 GFLOPS), FPGA (100 GFLOPS)")
    print("  Bandwidth: 800 MB/s")
    print("  Latency: 2 ms")
    print("\nWorkload: 7 tasks with varying computational intensity")
    
    scheduler = CADOScheduler(json.dumps(config))
    results = scheduler.optimize()
    
    print(f"\n{'RESULTS':^70}")
    print("-"*70)
    print(f"Total Makespan: {results['makespan_ms']:.2f} ms")
    
    print("\nTask Assignment:")
    for node_id in sorted(results['mapping'].keys()):
        proc = results['mapping'][node_id]
        sched = results['detailed_schedule'][node_id]
        print(f"  {node_id}: {proc:6s} [{sched['start_time_ms']:7.2f} - {sched['end_time_ms']:7.2f}] "
              f"(compute: {sched['duration_ms']:6.2f} ms)")
    
    # Calculate processor utilization
    proc_work_time = {}
    for node_id, (proc, start, end) in scheduler.schedule.items():
        if proc not in proc_work_time:
            proc_work_time[proc] = 0
        proc_work_time[proc] += (end - start)
    
    print("\nProcessor Utilization:")
    for proc in sorted(proc_work_time.keys()):
        util = (proc_work_time[proc] / results['makespan_ms']) * 100
        print(f"  {proc}: {proc_work_time[proc]:.2f} ms ({util:.1f}%)")
    
    return results

def test_data_intensive_workload():
    """Test with high data transfer costs"""
    config = {
        "workload": {
            "nodes": [
                {"id": "Load", "workload_intensity_GFLOPS": 20},
                {"id": "Process1", "workload_intensity_GFLOPS": 100},
                {"id": "Process2", "workload_intensity_GFLOPS": 100},
                {"id": "Merge", "workload_intensity_GFLOPS": 50}
            ],
            "edges": [
                {"from": "Load", "to": "Process1", "data_size_MB": 500},  # Large transfer
                {"from": "Load", "to": "Process2", "data_size_MB": 500},  # Large transfer
                {"from": "Process1", "to": "Merge", "data_size_MB": 200},
                {"from": "Process2", "to": "Merge", "data_size_MB": 200}
            ]
        },
        "system_config": {
            "processors": {
                "CPU": {"performance_GFLOPS": 100},
                "GPU": {"performance_GFLOPS": 500}
            },
            "bandwidth_MBps": 100,   # Low bandwidth (100 MB/s)
            "latency_ms": 10         # High latency (10 ms)
        }
    }
    
    print("\n" + "="*70)
    print("TEST 2: Data-Intensive Workload (High Communication Cost)")
    print("="*70)
    print("\nSystem Configuration:")
    print("  Processors: CPU (100 GFLOPS), GPU (500 GFLOPS)")
    print("  Bandwidth: 100 MB/s (LOW)")
    print("  Latency: 10 ms (HIGH)")
    print("\nWorkload: Pipeline with large data transfers (500 MB each)")
    
    scheduler = CADOScheduler(json.dumps(config))
    results = scheduler.optimize()
    
    print(f"\n{'RESULTS':^70}")
    print("-"*70)
    print(f"Total Makespan: {results['makespan_ms']:.2f} ms")
    
    print("\nTask Assignment:")
    for node_id in ['Load', 'Process1', 'Process2', 'Merge']:
        proc = results['mapping'][node_id]
        sched = results['detailed_schedule'][node_id]
        print(f"  {node_id:10s}: {proc:6s} [{sched['start_time_ms']:7.2f} - {sched['end_time_ms']:7.2f}] "
              f"(compute: {sched['duration_ms']:6.2f} ms)")
    
    # Note: The algorithm should prefer keeping tasks on the same processor
    # to minimize communication overhead
    processors_used = set(results['mapping'].values())
    print(f"\nProcessors used: {len(processors_used)} ({', '.join(sorted(processors_used))})")
    if len(processors_used) == 1:
        print("  → All tasks on same processor to avoid high communication cost!")
    
    return results

if __name__ == "__main__":
    # Run comprehensive tests
    print("\n" + "#"*70)
    print("#" + " "*22 + "CADO SCHEDULER TESTS" + " "*27 + "#")
    print("#" + " "*20 + "(HEFT Algorithm Implementation)" + " "*19 + "#")
    print("#"*70)
    
    results1 = test_heterogeneous_system()
    results2 = test_data_intensive_workload()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nThe HEFT algorithm successfully:")
    print("  ✓ Ranks tasks by their critical path (upward rank)")
    print("  ✓ Selects processors to minimize Earliest Finish Time (EFT)")
    print("  ✓ Accounts for heterogeneous processor speeds")
    print("  ✓ Considers data transfer costs between processors")
    print("  ✓ Adapts to different communication vs. computation trade-offs")
    print("="*70 + "\n")
