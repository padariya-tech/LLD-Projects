# functional requirenments
Requirement	What it means in our logger
Multiple log levels	Support DEBUG, INFO, WARNING, ERROR, CRITICAL.
Configurable format	Choose fields such as timestamp, level, thread name, and message.
Configurable handlers	Enable console, file, or both.
Size-based rotation	Move the current log file aside when it reaches a configured size and start a new one.
Asynchronous logging	Application threads enqueue records instead of performing file I/O themselves.
Concurrent requests	Multiple threads can submit log records simultaneously.
Thread safety	Concurrent queue operations don't corrupt records or queue state.
Graceful shutdown	Stop accepting new records, drain queued records, flush sinks, and stop the worker.

# non functional Requirenments

high thoughput with low latency for callers
low memeory usage
durability for file output( atomic writes / flush on rotation)
fault tolerance
observability
configurability

# Algorithm Choice Discussion
## Async Queue + Worker Thread
-> chose to duplicate application threads from i/o latency , callers push minimal objects to a bounded queue. worker pops and writes to sinks in batches. this yields high throughput and back pressure handling

## Concurrency

1) Queue from queue module used - safe threads
2) worker safely updates rotation metadata, rotation must pause writes momentarily but ramins inside worker thread
3) graceful shutdown. set a sentinel, join worker , flush remaining logs


# Limitation

1) single process only
2) No structured log output (json) by default
3) no sync remote transport
4) rotation by size only
5) No compression of rotated files
6) limited metrics
7) slow handlers
8) no dynamic re-configuration at runtime
