from hashlib import sha256
import json
import time
import datetime

class Block:

    def __init__(self, index, votes, timestamp, previous_hash):

        self.index = index
        self.votes = votes
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    # Computes the hash of the block
    # Also used when proof of work is needed
    # Input for hash function is all the votes in the current block and hash of the previous block
    def compute_hash(self,nonce=0):

        block_string = ""

        for x in self.votes:
            block_string = block_string + str(x)

        block_string = block_string + str(self.previous_hash) + str(nonce)
        return sha256(block_string.encode()).hexdigest()

    # This proof of work example is taken form examples in IBM website of how to create a blockchain
    # Computes the proof of work for the block
    # Here in proof of work we specify that every block should start with some no.of zeros
    # The only method to achieve proof of work is brute force
    def proof_of_work(self):

        # nonce is the extra we added to achieve our criteria
        nonce = 0

        computed_hash = self.compute_hash(nonce)
        while not computed_hash.startswith('0' * 3):
            nonce += 1
            computed_hash = self.compute_hash(nonce)
            #print(computed_hash)

        # for less than 5 within a second
        # for 6 about 20 seconds
        # for 7 about 160 seconds

        # print(nonce)
        self.nonce = nonce
        return computed_hash


# Testing
if __name__ == '__main__':

    test_block = Block(0,["170010025 to CAD 1 ","170010026 to CAD 2"], datetime.datetime.now(),0)
    print(test_block.votes)
    hash = test_block.compute_hash()
    print(hash)

    start = datetime.datetime.now()
    #start_time = time.time()
    hard_hash = test_block.proof_of_work()
    stop = datetime.datetime.now()
    #stop_time = time.time()
    print(stop - start)
    #print(stop_time - start_time)
    print(hard_hash)