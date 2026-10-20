# Functional Requirenments
1) generate globally unique id's
2) id's should be sortable based on creation time
3) support concurrent id generation
4) demo with external db

# Non Functional Requirenments
1) high Thoughput and low latency
2) thread safe and collision free , in memory generation
3) minimal memory foorprint
4) easily testable and extendable

# Algorithm

1) simplified version of twitters snowflake algorithm
2) ID = Timestamp + machine_id + sequence_number
3) this ensures uniqueness and sortable ID's without external DB  
4) use threading.lock to ensure sequence increments are atomic
5) keep machine_id fixed for demo
6) sequence resets every miliseconds
7) datamodel :  id is 64 bit integer , timestampe(42) +  
machine_id(10) + sequence(12)