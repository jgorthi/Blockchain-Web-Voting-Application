from hashlib import sha256
import time
import datetime
from Block import Block
import threading

class Blockchain:

    def __init__(self):

        self.new_votes = []
        self.chain = []
        self.set_genesis_block()


    # The first block in blockchain is called Genesis Block and it will contain no votes.
    def set_genesis_block(self):

        genesis_block = Block(1, ["This is Genesis Block"], datetime.datetime.now(), 0)
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)


    def last_block(self):

        return self.chain[-1]


    # Append a new block when mining is done, checking for proof of work and previous hash
    def append_block(self, block, proof):

        previous_hash = self.last_block().hash

        if previous_hash != block.previous_hash:
            print("Previous hash is not same as hash in last block")
            return False

        if not self.is_valid_proof(block, proof):
            print("Proof of work in invalid")
            return False

        block.hash = proof
        self.chain.append(block)
        return True


    # Check for proof of work and compute hash to verify the given hash is acutally the proof of work hash
    def is_valid_proof(self, block, block_hash):

        return (block_hash.startswith('0' * 3) and
                block_hash == block.compute_hash(block.nonce))


    # Add's a new vote, to be mined later
    def add_new_vote(self, vote):

        self.new_votes.append(vote)


    # Mines a the no.of votes present in unadded votes and creates a new block and append its
    def mine(self):

        if not self.new_votes:
            print("No new Votes")
            return False

        last_block = self.last_block()

        new_block = Block(last_block.index + 1,
                          self.new_votes[0:3],
                          datetime.datetime.now(),
                          last_block.hash)

        print(new_block.__dict__)
        proof = new_block.proof_of_work()
        self.append_block(new_block, proof)
        if len(self.new_votes) > 3:
            self.new_votes = self.new_votes[3:]
        else:
            self.new_votes = []
    # All ...._timer() functions execute continuously from time to time

    # Verifies Blockchain hashes every 5 Seconds
    # old
    def verify_timer(self):

        check = threading.Timer(5.0, self.verify_timer).start()
        check = True;

        for block in self.chain:
            if block.index > 1:
                check = check and self.is_valid_proof(block, block.hash)

        if check:
            print("Good")

        return check


    # Check all blocks in blockchain for proof of hash and
    # Collect votes for votes blockchain and check no.of votes with accounts blockchain
    def verify_timer_v2(self, accounts_b):

        check = True;
        # Create a list to load vote count from blockchain, later compare to that of account blockchain
        count = []
        if len(accounts_b.chain[-1][0].votes) >=0 :
            for cad in accounts_b.chain[-1][0].votes:
                # Creating and entry for each candidate and setting their intial vote count to 0
                count.append([cad[0], 0])
        else:
            return "No candidates"


        for block in self.chain:
            if block.index > 1:
                # Check for proof of work
                check = check and self.is_valid_proof(block, block.hash)
                # If not valid print hacked
                if not check: return "Hacked"
                # Now iterate through all votes and count no.of votes for each candidate
                for vote in block.votes:
                    # Split the vote string to
                    spilted_Vote = vote.split()
                    for cad in count:
                        # Check if the voter has voted or not
                        # if not voted our chain has been hacked
                        _group = accounts_b.which_group(spilted_Vote[0])
                        _year = accounts_b.which_year(spilted_Vote[0])
                        if accounts_b.is_valid_roll(_group, _year, spilted_Vote[0]):
                            return "Hacked"
                        if spilted_Vote[-1] == cad[0]:
                            cad[1] = cad[1] + 1


        # Check for no.of votes for each candidate in votes blockchain and accounts blockchain
        i = 0
        for cad_info in accounts_b.chain[-1][0].votes:
            if cad_info[1] != count[i][1]:
                print("Vote count hacked")
                check = False
                return check
            else:
                print("Votes are correct for ",cad_info[0])
            i = i + 1

        if check:
            print("Good")

        return check

    #Check for no.of new votes every 5 seconds and mine when sufficient no.of new votes are present
    def mine_timer(self):

        threading.Timer(5.0, self.mine_timer).start()
        if len(self.new_votes) >= 3:
            self.mine()
            print("Mined")
