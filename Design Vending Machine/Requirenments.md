# Functional Requirenments

1) add product 
2) browse product list
3) insert money (support coins/notes )
4) select product to purchase
5) dispense product of enough money & inventory
6) return change using greedy coin selection


# Non Functional Requirenments

1) deterministic behaviour
2) threadsafe for concurrent product attemps

# Algorithm for Coins

1) greedy algo with canonical coin set(100,50,20,10,5,1)

# Concurrency

1) all operations that mutate inventory or cashbox acquire the same lock to preserve atomicity

2) Read only operations do not acquire the lock