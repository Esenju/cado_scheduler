# CADO Scheduler - Command Line Interface Guide

## Quick Start - Testing Your JSON Workload

### Single Workload Test

```bash
# Basic usage with default settings (1000 MB/s, 2ms latency)
python schedule_workload.py your_workload.json

# Custom bandwidth and latency
python schedule_workload.py your_workload.json --bandwidth 500 --latency 5

# Short form
python schedule_workload.py your_workload.json -b 2000 -l 1

# Save results to file
python schedule_workload.py your_workload.json -o results.json

# Quiet mode (minimal output)
python schedule_workload.py your_workload.json --quiet
```

### Batch Testing (Multiple Workloads)

```bash
# Test all JSON files in a directory
python batch_test.py workloads/

# Automatically tests with 3 different configurations:
# - High-Speed: 2000 MB/s, 1ms latency
# - Medium: 1000 MB/s, 2ms latency  
# - Low-Speed: 500 MB/s, 5ms latency
```

## Examples

### Example 1: YOLOv8 Inference

```bash
python schedule_workload.py workloads/yolov8_4k.json
```

**Output:**
```
✓ Total Makespan: 68.25 ms
✓ Throughput: 14.65 operations/second

Task-to-Processor Mapping:
CAM_CAPTURE          CPU            0.00       10.00       10.00
PRE_PROC             CPU           10.00       25.00       15.00
BACKBONE             NPU           28.20       36.20        8.00
NECK_HEAD            NPU           36.20       41.20        5.00
POST_NMS             CPU           43.25       68.25       25.00

Speedup: 5.61x
```

### Example 2: Different Bandwidth Settings

```bash
# Fast interconnect (PCIe 4.0)
python schedule_workload.py workloads/yolov8_4k.json -b 2000 -l 1

# Result: 65.62 ms (5.84x speedup)

# Slow interconnect (shared bus)
python schedule_workload.py workloads/yolov8_4k.json -b 200 -l 10

# Result: 89.25 ms (4.29x speedup)
```

### Example 3: Save and Analyze Results

```bash
# Run scheduler and save results
python schedule_workload.py workloads/yolov8_4k.json -o my_results.json

# Results file contains:
{
  "mapping": {
    "CAM_CAPTURE": "CPU",
    "PRE_PROC": "CPU",
    "BACKBONE": "NPU",
    ...
  },
  "makespan_ms": 68.25,
  "detailed_schedule": {
    "CAM_CAPTURE": {
      "processor": "CPU",
      "start_time_ms": 0.0,
      "end_time_ms": 10.0,
      "duration_ms": 10.0
    },
    ...
  }
}
```

## JSON Workload Format

Your workload JSON must have this structure:

```json
{
  "workload_id": "my_workload",
  "nodes": [
    {
      "id": "TASK_NAME",
      "costs": {
        "CPU": 100,
        "GPU": 20,
        "NPU": 15
      },
      "description": "Optional description"
    }
  ],
  "edges": [
    {
      "from": "TASK_A",
      "to": "TASK_B",
      "data_size_MB": 10.0,
      "name": "Optional edge name"
    }
  ]
}
```

### Required Fields

- **workload_id**: Any string identifier
- **nodes**: Array of tasks
  - **id**: Unique task identifier
  - **costs**: Dictionary of {processor_type: execution_time_ms}
- **edges**: Array of dependencies
  - **from**: Source task ID
  - **to**: Destination task ID
  - **data_size_MB**: Data transfer size

### Optional Fields

- **nodes[].description**: Human-readable task description
- **edges[].name**: Human-readable edge description

## Command Line Options

### schedule_workload.py

```
positional arguments:
  workload              Path to workload JSON file

optional arguments:
  -h, --help            Show help message
  -b, --bandwidth BANDWIDTH
                        Inter-processor bandwidth in MB/s (default: 1000)
  -l, --latency LATENCY
                        Inter-processor latency in ms (default: 2)
  -o, --output OUTPUT   Save results to JSON file
  -q, --quiet           Suppress detailed output, only show summary
```

### batch_test.py

```
usage: batch_test.py [workload_directory]

positional arguments:
  workload_directory    Directory containing JSON workload files (default: workloads/)
```

## Understanding the Output

### Main Metrics

1. **Makespan**: Total execution time from start to finish
2. **Throughput**: Operations per second (1000 / makespan)
3. **Speedup**: Improvement over best single-processor execution

### Task-to-Processor Mapping

Shows which processor runs each task:
```
Task                 Processor    Start (ms)   End (ms)     Duration (ms)
CAM_CAPTURE          CPU                0.00       10.00       10.00
BACKBONE             NPU               28.20       36.20        8.00
```

### Processor Utilization

Shows how busy each processor is:
```
Processor Utilization:
  CPU:  73.3% (50.00 ms / 68.25 ms)
  NPU:  19.0% (13.00 ms / 68.25 ms)
```

### Communication Overhead

Shows time spent transferring data:
```
Communication Overhead:
  Overhead: 5.25 ms (7.7% of total time)
```

## Sample Workloads Included

### 1. yolov8_4k.json
- **Type**: Computer vision inference
- **Processors**: CPU, NPU
- **Tasks**: 5 (camera, preprocessing, backbone, neck/head, NMS)
- **Best for**: Testing vision AI pipelines

### 2. image_processing.json
- **Type**: Image processing pipeline
- **Processors**: CPU, GPU
- **Tasks**: 6 (load, denoise, color correct, sharpen, resize, compress)
- **Best for**: Testing graphics workloads

### 3. multimodal_ai.json
- **Type**: Multi-modal AI (audio + video)
- **Processors**: CPU, GPU, DSP, NPU
- **Tasks**: 7 (capture, encode, feature extraction, recognition, fusion)
- **Best for**: Testing complex heterogeneous systems

## Common Use Cases

### 1. Find Optimal Processor Assignment

```bash
python schedule_workload.py my_workload.json
```

Use the "Task-to-Processor Mapping" to configure your actual system.

### 2. Compare Different Hardware Configurations

```bash
# Test your current system
python schedule_workload.py my_workload.json -b 1000 -l 2

# Test upgraded system with faster interconnect
python schedule_workload.py my_workload.json -b 4000 -l 0.5

# Compare results to justify hardware upgrade
```

### 3. Identify Bottlenecks

Look at:
- **Processor Utilization**: Underutilized processors indicate imbalance
- **Communication Overhead**: High % indicates slow interconnect
- **Critical Path**: Tasks on the critical path determine total time

### 4. Batch Testing for System Design

```bash
python batch_test.py workloads/

# Compare multiple workloads to design a balanced system
```

## Tips for Accurate Results

### 1. Measure Real Execution Times

Don't guess! Profile your actual tasks:

```python
# Example: Measure BACKBONE execution on NPU
import time

start = time.time()
run_backbone_on_npu()
end = time.time()

execution_time_ms = (end - start) * 1000
# Use this value in your JSON
```

### 2. Set Realistic Bandwidth/Latency

Common values:

| Connection Type | Bandwidth | Latency |
|----------------|-----------|---------|
| PCIe 5.0 x16 | 60000 MB/s | 0.1 ms |
| PCIe 4.0 x16 | 30000 MB/s | 0.2 ms |
| PCIe 3.0 x16 | 15000 MB/s | 0.5 ms |
| 10 GbE Network | 1200 MB/s | 1-5 ms |
| Shared System Bus | 500 MB/s | 2-10 ms |
| Slow I2C/SPI | 10 MB/s | 5-20 ms |

### 3. Include All Data Transfers

Make sure your edges include ALL data that needs to move between processors.

### 4. Account for Non-Compute Time

If a task includes I/O, memory transfers, or synchronization, include that in the cost.

## Troubleshooting

### Error: "File not found"
```bash
# Make sure path is correct
ls my_workload.json

# Use absolute path if needed
python schedule_workload.py /full/path/to/workload.json
```

### Error: "Invalid JSON"
```bash
# Validate your JSON
python -m json.tool my_workload.json

# Common issues:
# - Missing commas
# - Trailing commas in arrays/objects
# - Unquoted keys
```

### Error: "Nodes must have 'costs' dictionary"
Make sure every node has a `costs` field with at least one processor.

### Warning: "Scheduling failed"
- Check that all edge references (`from`, `to`) match actual node IDs
- Verify no circular dependencies in the task graph
- Ensure all costs are positive numbers

## Integration with Your Code

### Python Integration

```python
import json
from test_yolov8 import YOLOv8Scheduler

# Load your workload
with open('my_workload.json') as f:
    workload = json.load(f)

# Create config
config = {
    "workload": workload,
    "system_config": {
        "processors": {proc: {"performance_GFLOPS": 1.0} 
                      for proc in ["CPU", "GPU"]},
        "bandwidth_MBps": 1000,
        "latency_ms": 2
    }
}

# Schedule
scheduler = YOLOv8Scheduler(json.dumps(config))
results = scheduler.optimize()

# Use results to configure your system
for task, processor in results['mapping'].items():
    assign_task_to_processor(task, processor)
```

### Continuous Integration

```bash
#!/bin/bash
# test_performance.sh

# Run scheduler on your workload
python schedule_workload.py workload.json -o results.json

# Extract makespan
makespan=$(python -c "import json; print(json.load(open('results.json'))['makespan_ms'])")

# Fail if performance degrades
if (( $(echo "$makespan > 100" | bc -l) )); then
    echo "Performance regression: ${makespan}ms > 100ms threshold"
    exit 1
fi
```

## Advanced Usage

### Custom System Configurations

Test specific hardware setups:

```bash
# High-end workstation (PCIe 4.0)
python schedule_workload.py workload.json -b 30000 -l 0.2

# Embedded system (slow shared bus)  
python schedule_workload.py workload.json -b 100 -l 10

# Cloud instance (network attached accelerator)
python schedule_workload.py workload.json -b 1200 -l 5
```

### Sensitivity Analysis

```bash
# Create a script to test multiple configurations
for bw in 100 500 1000 2000 5000; do
    echo "Testing bandwidth: ${bw} MB/s"
    python schedule_workload.py workload.json -b $bw -l 2 -q
done
```

## Files and Directories

```
├── schedule_workload.py      # Main CLI tool
├── batch_test.py             # Batch testing tool
├── cado_scheduler.py         # Core HEFT algorithm
├── test_yolov8.py            # YOLOv8 scheduler adapter
├── workloads/                # Sample workloads
│   ├── yolov8_4k.json
│   ├── image_processing.json
│   └── multimodal_ai.json
└── README.md                 # General documentation
```

## Next Steps

1. ✅ Create your workload JSON file
2. ✅ Run `python schedule_workload.py your_workload.json`
3. ✅ Analyze the processor assignments and timing
4. ✅ Adjust bandwidth/latency to match your hardware
5. ✅ Use the mapping to configure your actual system
6. ✅ Profile actual execution and update costs if needed

## Support

For detailed algorithm information, see:
- `README.md` - HEFT algorithm theory
- `YOLOV8_USAGE_GUIDE.md` - Integration guide
- `cado_scheduler.py` - Implementation details (well commented)
