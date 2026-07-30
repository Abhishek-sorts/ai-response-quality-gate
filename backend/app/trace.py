import time

class TraceTracker:
    def __init__(self):
        self.start_time = time.time()
        self.steps = []
        
    def add_step(self, step):
        self.steps.append(step)
        
    def get_total_latency(self) -> int:
        return int((time.time() - self.start_time) * 1000)
