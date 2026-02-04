# CADO Scheduler - Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# Step 1: Verify setup
python verify_setup.py

# Step 2: Test your workload
python schedule_workload.py workloads/yolov8_4k.json

# Step 3: Test all workloads
python batch_test.py workloads/
```

## 📝 Common Commands

### Test Single Workload

```bash
# Basic (uses defaults: 1000 MB/s, 2ms)
python schedule_workload.py your_workload.json

# Custom bandwidth/latency
python schedule_workload.py your_workload.json -b 500 -l 5

# Save results to file
python schedule_workload.py your_workload.json -o results.json

# Minimal output
python schedule_workload.py your_workload.json --quiet
```

### Test Multiple Workloads

```bash
# Test all JSON files in workloads/
python batch_test.py workloads/

# Test files in different directory
python batch_test.py /path/to/my/workloads/
```

### View Help

```bash
python schedule_workload.py --help
```

## 📊 Sample Workloads

| File | Description | Processors | Tasks |
|------|-------------|------------|-------|
| `workloads/yolov8_4k.json` | YOLOv8 4K inference | CPU, NPU | 5 |
| `workloads/image_processing.json` | Image pipeline | CPU, GPU | 6 |
| `workloads/multimodal_ai.json` | Audio+Video AI | CPU, GPU, DSP, NPU | 7 |

## 🎯 Your Workload JSON Template

```json
{
  "workload_id": "my_workload",
  "nodes": [
    {
      "id": "TASK_1",
      "costs": {"CPU": 100, "GPU": 20},
      "description": "Optional description"
    },
    {
      "id": "TASK_2",
      "costs": {"CPU": 50, "GPU": 10}
    }
  ],
  "edges": [
    {
      "from": "TASK_1",
      "to": "TASK_2",
      "data_size_MB": 5.0,
      "name": "Optional name"
    }
  ]
}
```

## 📈 Understanding Output

### Key Metrics

- **Makespan**: Total execution time (ms)
- **Throughput**: Operations per second
- **Speedup**: vs. best single processor
- **Utilization**: % each processor is busy
- **Comm Overhead**: Time spent on data transfers

### Example Output

```
✓ Total Makespan: 68.25 ms
✓ Throughput: 14.65 operations/second

Task-to-Processor Mapping:
TASK_A    CPU    0.00    10.00    10.00
TASK_B    NPU    12.00   20.00    8.00

Processor Utilization:
  CPU: 73.3% (50.00 ms / 68.25 ms)
  NPU: 19.0% (13.00 ms / 68.25 ms)

Speedup: 5.61x
Communication Overhead: 5.25 ms (7.7%)
```

## ⚙️ Bandwidth/Latency Guidelines

| System Type | Bandwidth | Latency | Use Case |
|-------------|-----------|---------|----------|
| PCIe 5.0 | 60000 MB/s | 0.1 ms | High-end GPU |
| PCIe 4.0 | 30000 MB/s | 0.2 ms | Gaming/Workstation |
| PCIe 3.0 | 15000 MB/s | 0.5 ms | Standard PC |
| 10 GbE | 1200 MB/s | 1-5 ms | Network accelerator |
| Shared Bus | 500 MB/s | 2-10 ms | Embedded system |
| Slow I2C/SPI | 10 MB/s | 5-20 ms | IoT devices |

## 🔧 Troubleshooting

### Import Error

```bash
# Make sure you're in the correct directory
cd /path/to/cado-scheduler/
python schedule_workload.py workloads/yolov8_4k.json
```

### Invalid JSON

```bash
# Validate your JSON first
python -m json.tool my_workload.json
```

### Missing tabulate

```bash
# Install for better batch_test.py output
pip install tabulate
```

## 📚 Documentation Files

- **CLI_USAGE_GUIDE.md** - Complete CLI documentation
- **YOLOV8_USAGE_GUIDE.md** - Integration guide
- **README.md** - HEFT algorithm details

## 🔬 Advanced Usage

### Python Integration

```python
import json
from test_yolov8 import YOLOv8Scheduler

with open('workload.json') as f:
    workload = json.load(f)

config = {
    "workload": workload,
    "system_config": {
        "processors": {p: {"performance_GFLOPS": 1.0} 
                      for p in ["CPU", "GPU"]},
        "bandwidth_MBps": 1000,
        "latency_ms": 2
    }
}

scheduler = YOLOv8Scheduler(json.dumps(config))
results = scheduler.optimize()

print(f"Makespan: {results['makespan_ms']} ms")
print(f"Mapping: {results['mapping']}")
```

### Sensitivity Analysis

```bash
# Test different bandwidths
for bw in 100 500 1000 2000; do
    echo "Bandwidth: $bw MB/s"
    python schedule_workload.py workload.json -b $bw -l 2 -q
done
```

## 📦 All Available Files

### Core Files
- `cado_scheduler.py` - HEFT algorithm implementation
- `test_yolov8.py` - Adapter for direct cost format
- `schedule_workload.py` - CLI tool
- `batch_test.py` - Batch testing
- `verify_setup.py` - Setup verification

### Examples
- `quickstart_yolov8.py` - Simple usage example
- `test_cado.py` - General tests

### Sample Workloads
- `workloads/yolov8_4k.json`
- `workloads/image_processing.json`
- `workloads/multimodal_ai.json`

### Documentation
- `README.md` - Algorithm documentation
- `YOLOV8_USAGE_GUIDE.md` - Integration guide
- `CLI_USAGE_GUIDE.md` - CLI documentation
- `QUICK_REFERENCE.md` - This file

## 💡 Tips

1. **Start simple**: Test with default settings first
2. **Measure real costs**: Profile your actual tasks
3. **Match your hardware**: Set accurate bandwidth/latency
4. **Compare scenarios**: Use batch_test.py for comparisons
5. **Validate results**: Check if processor assignments make sense

## ✅ Verification Checklist

- [ ] Run `python verify_setup.py` - all checks pass
- [ ] Test sample: `python schedule_workload.py workloads/yolov8_4k.json`
- [ ] Create your workload JSON file
- [ ] Test your workload with default settings
- [ ] Adjust bandwidth/latency to match your system
- [ ] Review processor assignments and timing
- [ ] Use results to configure your actual system

---

**Need Help?** Check the detailed guides:
- CLI_USAGE_GUIDE.md for complete CLI documentation
- YOLOV8_USAGE_GUIDE.md for integration examples
- README.md for algorithm theory
