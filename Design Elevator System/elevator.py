# Design and implement a simple Elevator System simulation in Python that handles
# multiple floor requests, moves in real-time using the SCAN algorithm, and
# prints the elevator's current floor and direction -
# all within a single-file console demo (no database or GUI) 


import threading
import time


class Elevator:
    def __init__(self, floors = 10):
        self.current_floor = 0
        self.direction = "UP"
        self.requests = []
        self.total_floors = floors
        self.running = True

    def add_request(self,floor:int):

        if 0<= floor < self.total_floors:

            if floor not in self.requests:
                self.requests.append(floor)
                self.requests.sort()
                print(f"Request added for floor {floor}")
            else:
                print("Invalid floor request.")

    def move(self):

        while self.running or self.requests:
            if not self.requests:
                print("Waiting for requests")
                time.sleep(1)
                continue

            target_floor = self.requests[0]
            
            if self.current_floor < target_floor:
                self.direction = "UP"
                self.current_floor += 1
            elif self.current_floor > target_floor:
                self.direction = "DOWN"
                self.current_floor -= 1
            else:
                print(f"Reached floor {self.current_floor}. Doors opening...")
                self.requests.pop(0)
                time.sleep(1)
                print("Doors closing...")
                continue
            
            print(f"Moving {self.direction} | Current floor: {self.current_floor}")
            time.sleep(0.7)

    def run(self):
        self.thread = threading.Thread(target=self.move)
        self.thread.start()

if __name__ == "__main__":

    e = Elevator(10)
    e.run()

    e.add_request(5)
    e.add_request(2)
    e.add_request(9)


    # In the main program:
    # time.sleep(2)
    
    
    e.running = False
    e.thread.join()

    print("Simulation ended.")

