
from collections import deque
import random
import threading
import time
from typing import Dict, List, Optional


# ============================================================
# CLASS 1: Server
# Represents a backend server that can handle client requests.
# ============================================================

class Server:

    def __init__(self, id: str, addr: str, weight: int = 1):
        # Unique identifier of the server, e.g., "s1"
        self.id = id

        # Server address, e.g., IP address or hostname
        self.addr = addr

        # Weight used by the Weighted Round Robin algorithm
        # A higher weight means the server gets selected more often
        self.weight = weight

        # Number of requests currently being processed
        self.active_conn = 0

        # Total number of requests assigned to this server
        self.total_requests = 0

        # Indicates whether the server is currently healthy
        self.healthy = True

        # Protects this server's shared state when multiple threads
        # access its counters or health status
        self.lock = threading.Lock()

    def acquire(self):
        """
        Called when a request is assigned to this server.

        Increments:
        1. active_conn: number of currently active requests
        2. total_requests: lifetime number of assigned requests
        """
        with self.lock:
            self.active_conn += 1
            self.total_requests += 1

    def release(self):
        """
        Called when a request finishes processing.

        Decreases the active connection count because one request
        is no longer being handled by this server.
        """
        with self.lock:
            if self.active_conn > 0:
                self.active_conn -= 1

    def mark_unhealthy(self):
        """Mark this server as unhealthy."""
        with self.lock:
            self.healthy = False

    def mark_healthy(self):
        """Mark this server as healthy again."""
        with self.lock:
            self.healthy = True

    def snapshot(self):
        """
        Return a dictionary containing the current server state.

        The lock ensures these fields are read together while
        protecting against concurrent updates.
        """
        with self.lock:
            return {
                "id": self.id,
                "addr": self.addr,
                "weight": self.weight,
                "active_conn": self.active_conn,
                "total_requests": self.total_requests,
                "healthy": self.healthy
            }


# ============================================================
# CLASS 2: LoadBalancer
# Manages backend servers and decides which server receives
# each incoming request.
# ============================================================

class LoadBalancer:

    def __init__(self, algorithm="round_robin"):
        # Dictionary of servers:
        # server ID -> Server object
        self.servers: Dict[str, Server] = {}

        # Protects shared load-balancer state
        self.lock = threading.Lock()

        # Current selection algorithm
        # Supported explicitly below:
        # round_robin, weighted_round_robin, least_connections
        self.algorithm = algorithm

        # Tracks the next server position for Round Robin
        self.rr_index = 0

        # Stores server IDs multiple times according to their weights.
        # Example: [s1, s2, s2, s2, s3, s3]
        self.weighted_queue = deque()

    def add_server(self, server: Server):
        """
        Add a backend server to the load balancer.

        Rebuild the weighted queue so that the new server is
        included in Weighted Round Robin selection.
        """
        with self.lock:
            self.servers[server.id] = server
            self._rebuild_weighted_queue()

    def remove_server(self, server_id: str):
        """
        Remove a server using its ID.

        Rebuild the weighted queue so that the removed server
        is no longer included in Weighted Round Robin selection.
        """
        with self.lock:
            if server_id in self.servers:
                del self.servers[server_id]
                self._rebuild_weighted_queue()

    def _rebuild_weighted_queue(self):
        """
        Reconstruct the queue used by Weighted Round Robin.

        Each healthy server ID is added according to its weight,
        capped at 10 repetitions.

        Example:
        s1 weight=1, s2 weight=3

        Queue: [s1, s2, s2, s2]
        """
        self.weighted_queue.clear()

        for server in self.servers.values():
            if server.healthy:
                # Limit the number of repetitions to 10
                cap = min(server.weight, 10)

                for _ in range(cap):
                    self.weighted_queue.append(server.id)

    def set_algorithm(self, algo: str):
        """
        Change the request-selection algorithm at runtime.

        Reset the Round Robin index when switching algorithms.
        """
        with self.lock:
            self.algorithm = algo
            self.rr_index = 0

    def _get_healthy_servers_list(self) -> List[Server]:
        """
        Return a list containing only healthy servers.

        This list is used by Round Robin, Least Connections,
        and the fallback selection algorithm.
        """
        with self.lock:
            return [
                server
                for server in self.servers.values()
                if server.healthy
            ]

    def select_server(self) -> Optional[Server]:
        """
        Select a backend server using the configured algorithm.

        Returns:
            A Server object if a server is selected.
            None if there are no eligible servers.
        """
        healthy = self._get_healthy_servers_list()

        # Cannot route a request if there are no healthy servers
        if not healthy:
            return None

        # ----------------------------------------------------
        # Algorithm 1: Round Robin
        # Select servers sequentially in a repeating cycle.
        # ----------------------------------------------------
        if self.algorithm == "round_robin":
            with self.lock:
                # Wrap the index around when it reaches the end
                idx = self.rr_index % len(healthy)

                # Move to the next position for the next request
                self.rr_index += 1

            return healthy[idx]

        # ----------------------------------------------------
        # Algorithm 2: Weighted Round Robin
        # Servers with larger weights appear more frequently
        # in the weighted queue.
        # ----------------------------------------------------
        elif self.algorithm == "weighted_round_robin":
            with self.lock:

                # Rebuild the queue if it is empty
                if not self.weighted_queue:
                    self._rebuild_weighted_queue()

                # Return None if the queue is still empty
                if not self.weighted_queue:
                    return None

                # Select the first server ID
                sid = self.weighted_queue.popleft()

                # Put it at the end to rotate the queue
                self.weighted_queue.append(sid)

            # Retrieve and return the corresponding server object
            return self.servers.get(sid)

        # ----------------------------------------------------
        # Algorithm 3: Least Connections
        # Select the healthy server with the fewest active
        # requests at the time of selection.
        # ----------------------------------------------------
        elif self.algorithm == "least_connections":
            chosen = min(
                healthy,
                key=lambda server: server.active_conn
            )
            return chosen

        # ----------------------------------------------------
        # Fallback algorithm
        # Randomly select one of the healthy servers when
        # an unrecognized algorithm name is configured.
        # ----------------------------------------------------
        else:
            return random.choice(healthy)

    def route_request(self, request_id, duration: Optional[float]):
        """
        Route a client request to a selected backend server.

        1. Select a server.
        2. Mark the request as active on that server.
        3. Start a separate thread to simulate request handling.
        """
        server = self.select_server()

        # Handle the case where no healthy server is available
        if not server:
            print(f"[LB] No healthy servers for request {request_id}")
            return False

        # Mark the request as active before starting its worker
        server.acquire()

        print(
            f"[LB] Routed req {request_id} -> server {server.id} "
            f"(active = {server.active_conn})"
        )

        # Simulate request handling in a separate thread
        t = threading.Thread(
            target=self._handle_request,
            args=(server, request_id, duration)
        )

        # Allow this thread to exit when the main program exits
        t.daemon = True
        t.start()

        return True

    def _handle_request(
        self,
        server: Server,
        request_id: int,
        duration: Optional[float]
    ):
        """
        Simulate the time a backend server spends handling
        a request, then release the active connection.

        If duration is None, choose a random processing time.
        """
        if duration is None:
            duration = random.uniform(0, 0.6)

        # Simulate request processing time
        time.sleep(duration)

        # Mark the request as completed
        server.release()

        print(
            f"[Server {server.id}] Completed req {request_id} "
            f"(active = {server.active_conn})"
        )

    def health_check_cycle(self):
        """
        Run simulated health checks continuously.

        Each cycle:
        1. Take a copy of the registered server list.
        2. Randomly mark servers unhealthy or healthy.
        3. Rebuild the weighted queue.
        4. Wait one second before the next cycle.
        """
        while True:
            # Copy the list while holding the load-balancer lock
            with self.lock:
                servers = list(self.servers.values())

            # Simulate health-check results for each server
            for server in servers:

                # Randomly mark a server unhealthy
                if random.random() < 0.2:
                    server.mark_unhealthy()
                    print(
                        f"[Health] Server {server.id} marked UNHEALTHY"
                    )

                # Give an unhealthy server a chance to recover
                elif (
                    not server.healthy
                    and random.random() < 0.3
                ):
                    server.mark_healthy()
                    print(
                        f"[Health] Server {server.id} marked HEALTHY"
                    )

            # Rebuild the queue to reflect current server health
            with self.lock:
                self._rebuild_weighted_queue()

            # Wait before running the next health-check cycle
            time.sleep(1.0)

    def snapshot(self):
        """
        Return the current state of all registered servers.

        The result maps each server ID to its status dictionary.
        """
        with self.lock:
            return {
                sid: server.snapshot()
                for sid, server in self.servers.items()
            }


# ============================================================
# DEMO FUNCTION
# Creates servers, starts health checks, simulates client
# requests, changes algorithms, and prints final statistics.
# ============================================================

def demo():

    # Create the load balancer using Round Robin initially
    lb = LoadBalancer(algorithm="round_robin")

    # Register three backend servers with different weights
    lb.add_server(Server("s1", "10.0.0.1", weight=1))
    lb.add_server(Server("s2", "10.0.0.2", weight=3))
    lb.add_server(Server("s3", "10.0.0.3", weight=2))

    # Start health checks in a background daemon thread
    hc = threading.Thread(
        target=lb.health_check_cycle,
        daemon=True
    )
    hc.start()

    # Track the next request ID
    req_id = 0

    def clients_sim():
        """
        Generate 25 simulated client requests.

        Switch from Round Robin to Weighted Round Robin
        at request 10, then to Least Connections at request 18.
        """
        nonlocal req_id

        while req_id < 25:

            # Switch algorithms while generating requests
            if req_id == 10:
                lb.set_algorithm("weighted_round_robin")
                print("\n--- Switched to Weighted Round Robin ---\n")

            if req_id == 18:
                lb.set_algorithm("least_connections")
                print("\n--- Switched to Least Connections ---\n")

            # Route the request and let a worker thread handle it
            lb.route_request(req_id, None)

            req_id += 1

            # Pause briefly before generating the next request
            time.sleep(0.08)

    # Run client simulation in its own thread
    client_thread = threading.Thread(target=clients_sim)
    client_thread.start()

    # Wait until the client simulation has submitted all requests
    client_thread.join()

    # Allow some time for request-processing threads to finish
    time.sleep(2)

    # Print the final server statistics
    print("\nFinal snapshot:")
    snap = lb.snapshot()

    for sid, info in snap.items():
        print(sid, info)


# Run the demo only when this file is executed directly
if __name__ == "__main__":
    demo()
