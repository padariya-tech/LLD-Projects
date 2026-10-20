import threading
import time


class UniqueIDGenerator:
    def __init__(self, machine_id=1, rollback_timeout=2.0):
        if not 0 <= machine_id <= 1023:
            raise ValueError("machine_id must be between 0 and 1023")

        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()
        self.rollback_timeout = rollback_timeout

    def _current_millis(self): # returns the current time in milliseconds
        return int(round(time.time() * 1000))

    # Problem it solves: What happens if one machine generates 
    # more IDs in a single millisecond than its sequence field can represent?
    def _wait_next_millis(self, last_timestamp): # wait when we run out of sequence numbers
        ts = self._current_millis()

        while ts <= last_timestamp:
            print("Waiting for the next millisecond" )
            ts = self._current_millis()

        return ts

    def generate_unique_id(self):
        with self.lock:
            ts = self._current_millis()

            if ts < self.last_timestamp:
                raise RuntimeError("System clock moved backward")

            if ts == self.last_timestamp:
                # increment sequence
                self.sequence = (self.sequence + 1) & 0xFFF # 12 bits

                if self.sequence == 0: # sequence overflow
                    print("Sequence overflow, waiting for the next millisecond")
                    ts = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = ts # update last timestamp

            return ( # 64 bits unique ID
                (ts << 22)
                | (self.machine_id << 12)
                | self.sequence
            )
        
generator = UniqueIDGenerator(machine_id=1)

for _ in range(50):
    print(generator.generate_unique_id())