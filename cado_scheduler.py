import json
from collections import defaultdict, deque

class CADOScheduler:
    def __init__(self, config_json):
        self.data = json.loads(config_json)
        self.nodes = {n['id']: n for n in self.data['workload']['nodes']}
        self.edges = self.data['workload']['edges']
        self.system = self.data['system_config']
        self.schedule = {}  # stores {node_id: (processor, start, end)}
        self.proc_ready_time = {}  # tracks when each processor is ready
        
    def get_comm_cost(self, parent_id, child_id, target_proc):
        """Calculate communication cost between parent and child nodes"""
        # If both are on same chip, cost is 0
        parent_proc, _, _ = self.schedule.get(parent_id, (None, 0, 0))
        if parent_proc == target_proc or parent_proc is None:
            return 0
        
        # Calculate data transfer overhead
        data_size = next(e['data_size_MB'] for e in self.edges 
                        if e['from'] == parent_id and e['to'] == child_id)
        return (data_size / self.system['bandwidth_MBps'] * 1000) + self.system['latency_ms']
    
    def get_computation_cost(self, node_id, processor):
        """Get computation time for a node on a specific processor"""
        node = self.nodes[node_id]
        proc_config = self.system['processors'][processor]
        
        # Calculate based on workload intensity and processor performance
        base_time = node['workload_intensity_GFLOPS'] / proc_config['performance_GFLOPS']
        return base_time * 1000  # Convert to ms
    
    def build_dependency_graph(self):
        """Build adjacency lists for dependencies"""
        predecessors = defaultdict(list)
        successors = defaultdict(list)
        
        for edge in self.edges:
            predecessors[edge['to']].append(edge['from'])
            successors[edge['from']].append(edge['to'])
        
        return predecessors, successors
    
    def topological_sort(self):
        """Perform topological sort to get task ordering"""
        predecessors, successors = self.build_dependency_graph()
        
        # Calculate in-degree
        in_degree = {node_id: len(predecessors[node_id]) for node_id in self.nodes}
        
        # Find all entry nodes (no predecessors)
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        topo_order = []
        
        while queue:
            node_id = queue.popleft()
            topo_order.append(node_id)
            
            for succ in successors[node_id]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)
        
        return topo_order, predecessors, successors
    
    def calculate_rank(self, node_id, successors, rank_cache):
        """Calculate upward rank for a node (used for prioritization)"""
        if node_id in rank_cache:
            return rank_cache[node_id]
        
        # Average computation cost across all processors
        avg_comp_cost = sum(self.get_computation_cost(node_id, proc) 
                           for proc in self.system['processors']) / len(self.system['processors'])
        
        if not successors[node_id]:
            # Exit node
            rank_cache[node_id] = avg_comp_cost
            return avg_comp_cost
        
        # Recursively calculate rank considering successors
        max_succ_rank = 0
        for succ in successors[node_id]:
            # Average communication cost
            avg_comm_cost = sum(self.get_comm_cost(node_id, succ, proc) 
                               for proc in self.system['processors']) / len(self.system['processors'])
            succ_rank = self.calculate_rank(succ, successors, rank_cache)
            max_succ_rank = max(max_succ_rank, avg_comm_cost + succ_rank)
        
        rank_cache[node_id] = avg_comp_cost + max_succ_rank
        return rank_cache[node_id]
    
    def get_earliest_start_time(self, node_id, processor, predecessors):
        """Calculate earliest start time for a node on a processor"""
        # When the processor is ready
        proc_ready = self.proc_ready_time.get(processor, 0)
        
        # When all data dependencies are satisfied
        data_ready = 0
        for pred_id in predecessors[node_id]:
            if pred_id in self.schedule:
                pred_proc, pred_start, pred_end = self.schedule[pred_id]
                comm_cost = self.get_comm_cost(pred_id, node_id, processor)
                data_ready = max(data_ready, pred_end + comm_cost)
        
        return max(proc_ready, data_ready)
    
    def optimize(self):
        """Main HEFT algorithm implementation"""
        # Phase 1: Task Prioritization (Ranking)
        topo_order, predecessors, successors = self.topological_sort()
        rank_cache = {}
        
        # Calculate ranks for all nodes
        for node_id in self.nodes:
            self.calculate_rank(node_id, successors, rank_cache)
        
        # Sort tasks by rank in decreasing order (higher rank = higher priority)
        sorted_tasks = sorted(self.nodes.keys(), key=lambda x: rank_cache[x], reverse=True)
        
        # Initialize processor ready times
        for proc in self.system['processors']:
            self.proc_ready_time[proc] = 0
        
        # Phase 2: Processor Selection
        for node_id in sorted_tasks:
            best_proc = None
            best_eft = float('inf')  # Earliest Finish Time
            best_est = 0  # Earliest Start Time
            
            # Try scheduling on each processor
            for proc in self.system['processors']:
                est = self.get_earliest_start_time(node_id, proc, predecessors)
                comp_cost = self.get_computation_cost(node_id, proc)
                eft = est + comp_cost
                
                # Select processor with minimum EFT
                if eft < best_eft:
                    best_eft = eft
                    best_est = est
                    best_proc = proc
            
            # Schedule the task on the best processor
            self.schedule[node_id] = (best_proc, best_est, best_eft)
            self.proc_ready_time[best_proc] = best_eft
        
        return self.get_results()
    
    def get_results(self):
        """Format and return the scheduling results"""
        # Calculate makespan (maximum finish time)
        makespan = max(end for _, _, end in self.schedule.values())
        
        # Create mapping dictionary
        mapping = {node_id: proc for node_id, (proc, _, _) in self.schedule.items()}
        
        # Create detailed schedule
        detailed_schedule = {
            node_id: {
                'processor': proc,
                'start_time_ms': start,
                'end_time_ms': end,
                'duration_ms': end - start
            }
            for node_id, (proc, start, end) in self.schedule.items()
        }
        
        return {
            'mapping': mapping,
            'makespan_ms': makespan,
            'detailed_schedule': detailed_schedule
        }


# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        "workload": {
            "nodes": [
                {"id": "A", "workload_intensity_GFLOPS": 10},
                {"id": "B", "workload_intensity_GFLOPS": 20},
                {"id": "C", "workload_intensity_GFLOPS": 15},
                {"id": "D", "workload_intensity_GFLOPS": 25}
            ],
            "edges": [
                {"from": "A", "to": "B", "data_size_MB": 50},
                {"from": "A", "to": "C", "data_size_MB": 30},
                {"from": "B", "to": "D", "data_size_MB": 40},
                {"from": "C", "to": "D", "data_size_MB": 20}
            ]
        },
        "system_config": {
            "processors": {
                "CPU": {"performance_GFLOPS": 100},
                "GPU": {"performance_GFLOPS": 500},
                "TPU": {"performance_GFLOPS": 300}
            },
            "bandwidth_MBps": 1000,
            "latency_ms": 5
        }
    }
    
    scheduler = CADOScheduler(json.dumps(config))
    results = scheduler.optimize()
    
    print("=" * 60)
    print("CADO SCHEDULER RESULTS (HEFT Algorithm)")
    print("=" * 60)
    print(f"\nTotal Makespan: {results['makespan_ms']:.2f} ms")
    print("\nNode-to-Processor Mapping:")
    print("-" * 40)
    for node_id, proc in sorted(results['mapping'].items()):
        print(f"  {node_id} -> {proc}")
    
    print("\nDetailed Schedule:")
    print("-" * 40)
    for node_id in sorted(results['detailed_schedule'].keys()):
        sched = results['detailed_schedule'][node_id]
        print(f"  {node_id}: {sched['processor']} "
              f"[{sched['start_time_ms']:.2f} - {sched['end_time_ms']:.2f}] "
              f"({sched['duration_ms']:.2f} ms)")
    print("=" * 60)
