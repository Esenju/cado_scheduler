# CADO Scheduler - Complete Package

## 🎯 Start Here

**New to CADO Scheduler?** Follow these steps:

1. ✅ Run verification: `python verify_setup.py`
2. ✅ Read: `QUICK_REFERENCE.md`
3. ✅ Test sample: `python schedule_workload.py workloads/yolov8_4k.json`
4. ✅ Create your workload JSON
5. ✅ Schedule it: `python schedule_workload.py your_workload.json`

## 📚 Documentation

### Quick Start Guides

| File | Description | When to Use |
|------|-------------|-------------|
| **QUICK_REFERENCE.md** | Cheat sheet with common commands | Daily reference |
| **CLI_USAGE_GUIDE.md** | Complete CLI documentation | Learning the tools |
| **YOLOV8_USAGE_GUIDE.md** | Integration and usage guide | Integrating into your project |
| **README.md** | HEFT algorithm theory | Understanding the algorithm |

### Choose Your Path

**Path 1: I just want to test my workload**
→ Read `QUICK_REFERENCE.md` → Run `schedule_workload.py`

**Path 2: I want to understand everything**
→ Read `README.md` → Read `CLI_USAGE_GUIDE.md` → Read `YOLOV8_USAGE_GUIDE.md`

**Path 3: I want to integrate this into my code**
→ Read `YOLOV8_USAGE_GUIDE.md` → Check `quickstart_yolov8.py` example

## 🛠️ Tools & Scripts

### Main Tools

| Script | Purpose | Usage |
|--------|---------|-------|
| **schedule_workload.py** | Test single workload | `python schedule_workload.py workload.json` |
| **batch_test.py** | Test multiple workloads | `python batch_test.py workloads/` |
| **verify_setup.py** | Verify installation | `python verify_setup.py` |

### Example Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **quickstart_yolov8.py** | Simple usage example | `python quickstart_yolov8.py` |
| **test_cado.py** | General CADO tests | `python test_cado.py` |

### Core Libraries

| File | Description |
|------|-------------|
| **cado_scheduler.py** | Core HEFT algorithm implementation |
| **test_yolov8.py** | Adapter for direct cost format (required by CLI tools) |

## 📊 Sample Workloads

Located in `workloads/` directory:

| File | Description | Processors | Tasks | Good For |
|------|-------------|------------|-------|----------|
| **yolov8_4k.json** | YOLOv8 4K inference | CPU, NPU | 5 | Computer vision |
| **image_processing.json** | Image pipeline | CPU, GPU | 6 | Graphics workloads |
| **multimodal_ai.json** | Audio+Video AI | CPU, GPU, DSP, NPU | 7 | Complex heterogeneous systems |

## 🚀 Quick Commands

```bash
# Verify everything is working
python verify_setup.py

# Test YOLOv8 workload (default: 1000 MB/s, 2ms)
python schedule_workload.py workloads/yolov8_4k.json

# Test with custom settings
python schedule_workload.py workloads/yolov8_4k.json -b 500 -l 5

# Save results
python schedule_workload.py workloads/yolov8_4k.json -o results.json

# Test all workloads
python batch_test.py workloads/

# Quick results only
python schedule_workload.py workloads/yolov8_4k.json --quiet
```

## 📝 Create Your Own Workload

### Template

Create a file `my_workload.json`:

```json
{
  "workload_id": "my_workload",
  "nodes": [
    {
      "id": "TASK_1",
      "costs": {"CPU": 100, "GPU": 20, "NPU": 15},
      "description": "First task"
    },
    {
      "id": "TASK_2",
      "costs": {"CPU": 50, "GPU": 10, "NPU": 8}
    }
  ],
  "edges": [
    {
      "from": "TASK_1",
      "to": "TASK_2",
      "data_size_MB": 5.0,
      "name": "Data transfer"
    }
  ]
}
```

### Test It

```bash
python schedule_workload.py my_workload.json
```

## 🎓 Understanding the Output

### What You Get

1. **Task-to-Processor Mapping** - Which processor runs each task
2. **Timing Information** - Start time, end time, duration for each task
3. **Makespan** - Total execution time
4. **Throughput** - Operations per second
5. **Speedup** - Improvement vs. single processor
6. **Processor Utilization** - How busy each processor is
7. **Communication Overhead** - Time spent on data transfers

### Example Output

```
✓ Total Makespan: 68.25 ms
✓ Throughput: 14.65 operations/second

Task-to-Processor Mapping:
CAM_CAPTURE     CPU       0.00     10.00     10.00
BACKBONE        NPU      28.20     36.20      8.00

Processor Utilization:
  CPU: 73.3% (50.00 ms / 68.25 ms)
  NPU: 19.0% (13.00 ms / 68.25 ms)

Speedup: 5.61x
```

## 🔧 Common Workflows

### Workflow 1: Optimize Your System Design

```bash
# 1. Create workload JSON with your tasks
# 2. Test with current system specs
python schedule_workload.py my_workload.json -b 1000 -l 2

# 3. Test with upgraded system
python schedule_workload.py my_workload.json -b 4000 -l 0.5

# 4. Compare results to justify upgrade
```

### Workflow 2: Find Bottlenecks

```bash
# 1. Run scheduler
python schedule_workload.py my_workload.json -o results.json

# 2. Check processor utilization
# 3. Identify underutilized processors
# 4. Adjust task costs or add tasks to balance load
```

### Workflow 3: Test Multiple Scenarios

```bash
# 1. Create multiple workload variants
# 2. Put them in a directory
# 3. Run batch test
python batch_test.py my_workloads/

# 4. Compare results
```

## 📦 File Organization

```
cado-scheduler/
├── Core Implementation
│   ├── cado_scheduler.py          # HEFT algorithm
│   └── test_yolov8.py             # Direct cost adapter
│
├── Command Line Tools
│   ├── schedule_workload.py       # Single workload CLI
│   ├── batch_test.py              # Batch testing CLI
│   └── verify_setup.py            # Setup verification
│
├── Examples
│   ├── quickstart_yolov8.py       # Simple example
│   └── test_cado.py               # General tests
│
├── Sample Workloads
│   └── workloads/
│       ├── yolov8_4k.json
│       ├── image_processing.json
│       └── multimodal_ai.json
│
└── Documentation
    ├── INDEX.md                    # This file
    ├── QUICK_REFERENCE.md          # Quick commands
    ├── CLI_USAGE_GUIDE.md          # CLI details
    ├── YOLOV8_USAGE_GUIDE.md       # Integration guide
    └── README.md                   # Algorithm theory
```

## 🔍 Troubleshooting

### Problem: Import errors

**Solution:**
```bash
# Make sure you're in the right directory
cd /path/to/cado-scheduler/
python verify_setup.py
```

### Problem: "File not found"

**Solution:**
```bash
# Check the file exists
ls workloads/yolov8_4k.json

# Use absolute path if needed
python schedule_workload.py /full/path/to/workload.json
```

### Problem: Invalid JSON

**Solution:**
```bash
# Validate your JSON
python -m json.tool my_workload.json
```

### Problem: Unexpected results

**Solution:**
1. Check task costs are accurate (profile real execution)
2. Verify bandwidth/latency match your hardware
3. Ensure edges reference correct node IDs
4. Check for circular dependencies

## 💡 Tips for Best Results

1. **Measure, Don't Guess**: Profile actual task execution times
2. **Set Realistic Bandwidth**: Match your actual hardware
3. **Start Simple**: Test with defaults, then adjust
4. **Validate Results**: Check if assignments make logical sense
5. **Use Batch Testing**: Compare multiple scenarios
6. **Check Utilization**: Look for imbalanced processor usage

## 🎯 Common Use Cases

### Use Case 1: Design New System

- Create workload JSON from requirements
- Test with different processor combinations
- Compare makespan and speedup
- Choose optimal configuration

### Use Case 2: Optimize Existing System

- Profile current task execution times
- Create workload JSON
- Run scheduler to find optimal assignment
- Reconfigure system based on results

### Use Case 3: Justify Hardware Upgrade

- Test current configuration
- Test with upgraded specs
- Calculate ROI based on speedup
- Present results to stakeholders

## 📈 Performance Expectations

### Typical Speedups

| System Complexity | Expected Speedup |
|------------------|------------------|
| 2 homogeneous processors | 1.5-2x |
| 2 heterogeneous processors | 2-6x |
| 4+ heterogeneous processors | 3-10x |

### Factors Affecting Performance

- **Task heterogeneity**: More varied tasks → better speedup
- **Processor diversity**: More processor types → more optimization potential
- **Communication overhead**: Lower bandwidth → reduced speedup
- **Dependency structure**: More parallelism → better speedup

## ✅ Quick Verification

Run this command to verify everything is working:

```bash
python verify_setup.py && \
python schedule_workload.py workloads/yolov8_4k.json --quiet
```

Expected output:
```
✅ ALL CHECKS PASSED - Setup is complete!
Makespan: 68.25 ms
Mapping: {'CAM_CAPTURE': 'CPU', ...}
```

## 🆘 Getting Help

1. **Quick answers**: Check `QUICK_REFERENCE.md`
2. **CLI help**: Run `python schedule_workload.py --help`
3. **Examples**: Look at `workloads/` directory
4. **Theory**: Read `README.md`
5. **Integration**: Check `YOLOV8_USAGE_GUIDE.md`

## 🎓 Learning Path

### Beginner

1. Run `verify_setup.py`
2. Read `QUICK_REFERENCE.md`
3. Test: `python schedule_workload.py workloads/yolov8_4k.json`
4. Create simple workload JSON
5. Test your workload

### Intermediate

1. Read `CLI_USAGE_GUIDE.md`
2. Understand output metrics
3. Test with different bandwidth/latency
4. Use batch testing
5. Analyze processor utilization

### Advanced

1. Read `README.md` (algorithm details)
2. Read `YOLOV8_USAGE_GUIDE.md`
3. Integrate into your code
4. Create custom workflows
5. Contribute improvements

## 📌 Key Takeaways

- ✅ **`test_yolov8.py` IS included** - it's the adapter that makes direct cost format work
- ✅ **3 sample workloads provided** - ready to test
- ✅ **Complete documentation** - from quick reference to deep theory
- ✅ **CLI tools ready** - schedule_workload.py and batch_test.py
- ✅ **Verification tool** - verify_setup.py checks everything
- ✅ **Multiple guides** - choose based on your needs

---

**Ready to start?** Run `python verify_setup.py` now!
