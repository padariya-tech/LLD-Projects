# Functional Requirenments
 
1) short the long URL into Short URL Alias
2) Redirect Short URL to original Long URL
3) Handle Collision in URL Generation
4) Track number of hits

# Non Functional Requirenments

1) Short url should be unique and minimal length
2) system should be fast for lookup and insertion
3) should be memeory efficient for small scale demo
4) easy to extend to persistent db later

# Algorithm choices

1) use base64 encoding of a unique ID to generate URL's
2) Maintain a dectionary (Hash Map) for fast mapping of short -> long URL's and vice-versa
3) this ensures o(1) insertion and retrival for demo scale

# concurrency and data model discussion

url_db : {} 
reverse_db = {}
counter : 1 

## concurrency:

1) for a single - threaded python demo , no complex , no complex locks needed