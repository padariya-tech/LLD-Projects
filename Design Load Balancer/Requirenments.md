
# Functional Requirenments
1) Accept incoming client requests and forward them to backend servers
2) support multiple load balancing algorithm
3) maintain server health status
4) dynamic server management
5) collect basic metrics
6) provide an api to query server pod status and metrics


# Non Functional Requirenments

1) High throughput and low latency for routing decisions
2) fault tolerance
3) scalability
4) observability
5) concurrency safe

# Algorithm Selection

1) ##Round Robin :- simple, fair when servers are identical . o(1) per 
    requests. good defsult
2) ##Weighted Round Robin :- extends round robin to account for capacity differences using weights. slightly more stale/complexity.

3) ##Least Connectiosn :- forward to servers with least conenctions


# Concurrency Model

1) Use fine grained locking per server for active connections increments/decrements reduce contention

2) Use an atomic pointer/index for RR selection
3) health checks run in background worker threads and update healthy-flag under lock.
4) Ensure request routing and metrics update are consistent


