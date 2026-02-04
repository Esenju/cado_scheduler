#!/usr/bin/env python3
"""
CADO Scheduler - Setup Verification
====================================

Run this script to verify all files are in place and working correctly.
"""

import sys
import os
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_import(module_name, from_file=None):
    """Check if a module can be imported"""
    try:
        if from_file:
            exec(f"from {from_file} import {module_name}")
        else:
            exec(f"import {module_name}")
        print(f"✓ Can import: {module_name}")
        return True
    except ImportError as e:
        print(f"✗ Cannot import {module_name}: {str(e)}")
        return False

def main():
    print("="*70)
    print("CADO SCHEDULER - SETUP VERIFICATION")
    print("="*70)
    
    all_ok = True
    
    # Check core files
    print("\n📁 Checking Core Files:")
    print("-"*70)
    all_ok &= check_file("cado_scheduler.py", "Core scheduler")
    all_ok &= check_file("test_yolov8.py", "YOLOv8 adapter")
    all_ok &= check_file("schedule_workload.py", "CLI tool")
    all_ok &= check_file("batch_test.py", "Batch tester")
    
    # Check example files
    print("\n📁 Checking Example Files:")
    print("-"*70)
    all_ok &= check_file("quickstart_yolov8.py", "Quick start example")
    all_ok &= check_file("test_cado.py", "General tests")
    
    # Check workload files
    print("\n📁 Checking Sample Workloads:")
    print("-"*70)
    all_ok &= check_file("workloads/yolov8_4k.json", "YOLOv8 workload")
    all_ok &= check_file("workloads/image_processing.json", "Image processing")
    all_ok &= check_file("workloads/multimodal_ai.json", "Multimodal AI")
    
    # Check documentation
    print("\n📁 Checking Documentation:")
    print("-"*70)
    all_ok &= check_file("README.md", "General README")
    all_ok &= check_file("YOLOV8_USAGE_GUIDE.md", "YOLOv8 guide")
    all_ok &= check_file("CLI_USAGE_GUIDE.md", "CLI guide")
    
    # Check imports
    print("\n🐍 Checking Python Imports:")
    print("-"*70)
    all_ok &= check_import("json")
    all_ok &= check_import("CADOScheduler", "cado_scheduler")
    all_ok &= check_import("YOLOv8Scheduler", "test_yolov8")
    
    # Check optional dependencies
    print("\n📦 Checking Optional Dependencies:")
    print("-"*70)
    has_tabulate = check_import("tabulate")
    if not has_tabulate:
        print("   Note: Install with 'pip install tabulate' for better batch_test.py output")
    
    # Test a simple workload
    print("\n🧪 Running Simple Test:")
    print("-"*70)
    try:
        import json
        from test_yolov8 import YOLOv8Scheduler
        
        # Minimal test workload
        test_config = {
            "workload": {
                "nodes": [
                    {"id": "A", "costs": {"CPU": 10}},
                    {"id": "B", "costs": {"CPU": 20}}
                ],
                "edges": [{"from": "A", "to": "B", "data_size_MB": 1.0}]
            },
            "system_config": {
                "processors": {"CPU": {"performance_GFLOPS": 1.0}},
                "bandwidth_MBps": 1000,
                "latency_ms": 2
            }
        }
        
        scheduler = YOLOv8Scheduler(json.dumps(test_config))
        results = scheduler.optimize()
        
        if results and 'makespan_ms' in results:
            print(f"✓ Scheduler test passed (makespan: {results['makespan_ms']:.2f} ms)")
        else:
            print("✗ Scheduler test failed: Invalid results")
            all_ok = False
            
    except Exception as e:
        print(f"✗ Scheduler test failed: {str(e)}")
        all_ok = False
    
    # Final result
    print("\n" + "="*70)
    if all_ok and has_tabulate:
        print("✅ ALL CHECKS PASSED - Setup is complete!")
        print("\nYou can now run:")
        print("  python schedule_workload.py workloads/yolov8_4k.json")
        print("  python batch_test.py workloads/")
    elif all_ok:
        print("✅ CORE CHECKS PASSED - Setup is functional!")
        print("\n⚠️  Optional: Install tabulate for better output")
        print("   pip install tabulate")
        print("\nYou can now run:")
        print("  python schedule_workload.py workloads/yolov8_4k.json")
    else:
        print("❌ SOME CHECKS FAILED - Please ensure all files are present")
        print("\nMissing files should be in the same directory as this script.")
    print("="*70 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
