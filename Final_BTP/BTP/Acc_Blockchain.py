from hashlib import sha256
import time
import datetime
from Block import Block
from Blockchain import Blockchain
import threading
import requests
from urllib.parse import urlparse
import json


class Acc_Block(Block):

    def __init__(self, index, votes, timestamp, previous_hash = 0):
        self.index = index
        self.votes = votes
        self.timestamp = timestamp
        self.previous_hash = previous_hash


class Acc_Blockchain(Blockchain):

    def __init__(self):

        self.chain = []
        self.new_acc = []
        self.new_votes_cad = []
        self.nodes = []
        self.set_genesis_block()
        self.overide_genesis_to_root()
        self.set_tree(["B.Tech","M.Tech","CAD"],[4, 2, 0])
        self.new_roll_no = None
        self.otp = None


    # Here our block chain should have a root block not genesis block
    def overide_genesis_to_root(self):

        genesis = self.chain[0]
        root_block = Acc_Block("Root","",datetime.datetime.now(),[])
        self.chain[0] = root_block
        self.chain[0].hash = 0


    # Sets the tree in blockchain
    def set_tree(self,groups,years):

        i = 1
        for group in groups:
            new_ls = []
            root_group_block = Acc_Block(group, [], datetime.datetime.now(), [])
            new_ls.append(root_group_block)

            # Creating blocks for each group
            for year in range(0,years[i-1]):
                group_block = Acc_Block(group + " " + str(year+1) , [], datetime.datetime.now(), [])
                new_ls.append(group_block)
            self.chain.append(new_ls)
            i = i + 1
        # Update the hash as the tree is complete
        # self.update_hash()
        self.compute_groups_hash_pow()
        self.compute_root_hash()


    # Print the group blocks and there accounts
    def print_chain(self):

        for block in self.chain:

            if type(block) is list:
                for sub_block in block:
                    print(sub_block.index," contains ",sub_block.votes, " and has hash", sub_block.hash)

            else:
                print(block.index)


    # Function of add new account in the respective tree branch, called after mining
    def add_account(self,roll_no): # roll_no has both roll no and cad

        year = int(self.which_year(roll_no))
        group =  self.which_group(roll_no)

        for block in self.chain[1:]:
            if block[0].index == group:
                block[year].votes.append(roll_no)
                #print(block[0].index,block[int(year)].votes)

        return True

    # Add accounts in buffer
    def add_tem_acc(self, group, year, roll_no, cad=0):

        year = int(year)

        if not self.is_valid_roll(group, year, roll_no):
            return False

        self.new_acc.append(roll_no + " " + cad)
        return True

    # The code assumes the following pattern for roll numbers, where x if from 1 to 3 and yz from 01 to 30
    # 1600x00yz belongs to B.Tech 1st Year
    # 1700x00yz belongs to B.Tech 2nd Year
    # 1800x00yz belongs to B.Tech 3rd Year
    # 1900x00yz belongs to B.Tech 4th Year
    # 2600x00yz belongs to M.Tech 1st Year
    # 2700x00yz belongs to M.Tech 2nd Year

    # Returns which group the roll number belongs to
    def which_group(self,_roll):

        _roll = str(_roll)
        _roll = _roll.split()[0]
        if _roll.startswith("1"):
            _year = int(_roll[1]) - 5
            if _year > 4 or _year <= 0:
                return "Invalid"
            _group = "B.Tech"

        elif _roll.startswith("2"):
            _group = "M.Tech"
            _year = int(_roll[1]) - 5
            if _year > 2:
                return "Invalid"

        return _group


    # Returns which year the roll number belongs to
    def which_year(self,_roll):

        _roll = str(_roll)
        _roll = _roll.split()[0]
        if _roll.startswith("1"):
            _year = int(_roll[1]) - 5

        elif _roll.startswith("2"):
            _year = int(_roll[1]) - 5
            if _year > 2:
                return "Invalid"

        return _year


    # Checks if the voter has already voted
    def is_valid_roll(self, group, year, roll_no):

        # Check in buffer
        for new_acc in self.new_acc:
            if new_acc.split()[0] == roll_no:
                print("In buffer already")
                return False

        # Check in actual account blokchain
        for block in self.chain[1:]:
            if block[0].index == group:
                if any(roll_no in accounts.split()[0] for accounts in block[year].votes):
                    return False

        return True


    # Fuction to update the hash of all nodes in the tree
    # old
    def update_hash(self, nonce = 0):

        for block in reversed(self.chain):
            if type(block) is list:
                # Update hash's of groups
                block[0].hash = self.compute_group_hash(block[0].index)
            else:
                # Update hash of root
                block.hash = self.compute_root_hash()


    # Function to update hash the tree branches
    # old
    def compute_group_hash(self, group):

        for block in self.chain[1:]:
            if block[0].index == group:
                block_string = ""

                for sub_block in reversed(block):
                    sub_block.hash = sub_block.compute_hash() # updates the leaf's hash
                    block_string = block_string + " " + str(sub_block.hash)

                hash = sha256(block_string.encode()).hexdigest()
                return hash


    # Function to do PoW and update hash the tree branches, called in mining after new accounts are added
    def compute_groups_hash_pow(self):

        # Updates hash's for all group sub-tress
        for group_node in self.chain[1:-1]:
            block_string = ""

            for sub_block in group_node[1:]:
                # Updates the leaf's hash
                sub_block.hash = sub_block.proof_of_work()
                #print(sub_block.hash)
                block_string = block_string + " " + str(sub_block.hash)

            mix_hash = sha256(block_string.encode()).hexdigest()
            # Update the parents hash
            group_node[0].hash = mix_hash
            #print(group_node[0].hash)

        # Update hash for candidate sub-tree
        self.chain[-1][0].hash = self.chain[-1][0].proof_of_work()


    # Function to update the hash of root of the tree
    def compute_root_hash(self, nonce = 0):

        block_string = ""
        for group_block in self.chain[1:]:
            block_string = block_string + str(group_block[0].hash)
        self.chain[0].hash = sha256(block_string.encode()).hexdigest()


    # Function to add the candidate to accounts
    def add_cad(self,candidate):

        #print(type(self.chain[-1][0]))
        self.chain[-1][0].votes.append([candidate, 0])
        #self.update_hash()
        self.compute_groups_hash_pow()
        self.compute_root_hash()



    # Funtion to increase the vote count for the candidate, stored in buffer
    # Will be added when mined accordingly
    def vote_to_cad_buffer(self,cad):

        for cad_pair in self.chain[-1][0].votes:
            if cad_pair[0] == cad:
                self.new_votes_cad.append(cad)
                return True

        return False


    # Funtion to increase the vote count for the candidate
    # called when mining
    def vote_to_cad(self, cad):

        for cad_pair in self.chain[-1][0].votes:
            if cad_pair[0] == cad:
                cad_pair[1] = cad_pair[1] + 1
                return True

        return False


    # Results the votes of all candidates
    def cad_results(self):

        return self.chain[-1][0].votes


    # Function to mine the Merkle Tree blockchain
    # Right now will mining synchronously with basic blockchain which stores votes to avoid errors
    def mine_Acc(self):

        if not self.new_acc:
            return False

        if len(self.new_acc) < 3:
            return False

        # Register accounts
        for account in self.new_acc[0:3]:
            self.add_account(account)

        # Increase count for candidates
        for account in self.new_votes_cad[0:3]:
            self.vote_to_cad(account)

        # Decrease the buffer
        self.new_acc = self.new_acc[3:]
        self.new_votes_cad = self.new_votes_cad[3:0]

        # compute hash for group nodes
        self.compute_groups_hash_pow()


        # compute hash for root node
        self.compute_root_hash()
        self.print_chain()
        return True

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.append(parsed_url.netloc)
        print(address," has been added in connections")

    # Alert Function
    def alert_network(self, roll_no, cad):
        network = self.nodes
        if len(network) == 0:
            print("No connected Nodes")
            return True
        info_json = {'roll_no': roll_no, 'cad': cad}
        for node in network:
            response = requests.post(f'http://{node}/has_vote', json = info_json)
            if response.status_code == 201:
                requests.post(f'http://{node}/add_vote', json = info_json)
        return

    def has_vote(self, roll_no, cad):

        vote_string = roll_no + " " + cad

        for block in self.chain:

            if type(block) is list:
                for sub_block in block:
                    if vote_string in sub_block.votes or vote_string in self.new_acc:
                        return True

        return False


    def alert_network_mine(self):
        network = self.nodes
        if len(network) == 0:
            print("No connected Nodes")
            return True
        for node in network:
            response = requests.get(f'http://{node}/no_of_votes')
            if response.status_code == 200:
                requests.get(f'http://{node}/mine_block')
            else:
                return False

    def validation(self):
        check = True
        # Create a list to load vote count from blockchain, later compare to that of account blockchain
        candidates = []
        count = []
        if len(self.chain[-1][0].votes) >= 0:
            for cad in self.chain[-1][0].votes:
                # Creating and entry for each candidate and setting their intial vote count to 0
                candidates.append(cad[0])
                count.append(0)
        else:
            return False

        for block in self.chain[:-1]:
            if type(block) is list:
                for sub_block in block:
                    if len(sub_block.votes) > 0:
                        check = check and self.is_valid_proof(sub_block, sub_block.hash)
                    for vote in sub_block.votes:
                        spilted_Vote = vote.split()
                        _group = self.which_group(spilted_Vote[0])
                        _year = self.which_year(spilted_Vote[0])
                        if self.is_valid_roll(_group, _year, spilted_Vote[0]):
                            return False
                        index = candidates.index(spilted_Vote[1])
                        count[index] = count[index] + 1

        if len(self.chain[-1][0].votes) >= 0 :
            i = 0
            for cad in self.chain[-1][0].votes:
                # Compare vote count
                if cad[1] != count[i]:
                    return False
                print("Candidate", cad[0], "has votes recorded ", count[i], "and count in end is ", cad[1])
                i = i + 1

        print("check is ",check)
        return check


    def valid_v2(self):
        network = self.nodes
        json_info = self.to_json()
        if len(network) == 0:
            print("No connected Nodes")
            return True
        for node in network:
            response = requests.post(f'http://{node}/check_blockchain', json=json_info)
            if response.status_code == 201:
                print(node, "same as ours")
            else:
                print(node, "not same as ours")
                return False
        return True


    def to_json(self):
        dt = {}
        key = 0

        for block in self.chain[:-1]:
            if type(block) is list:
                for sub_block in block:
                    if len(sub_block.votes) > 0:
                        for vote in sub_block.votes:
                            dt[key] = vote
                            key = key + 1
                        dt[key] = sub_block.hash
                        key = key + 1

        for cad in self.chain[-1][0].votes:
            dt[key] = str(cad[0]) + " " + str(cad[1])
            key = key + 1

        dt[key] = self.chain[-1][0].hash

        j = json.dumps(dt)
        #print(j)
        return j




# Testing
if __name__ == '__main__':

    test_block = Acc_Blockchain()
    #print(test_block.__dict__)
    #test_block.print_chain()
    print(test_block.new_acc)
    test_block.add_tem_acc(test_block.which_group(160010024), test_block.which_year(160010024), 160010024)
    test_block.add_tem_acc("B.Tech", 1, 160010025)
    test_block.add_tem_acc("B.Tech", 1, 160010026)
    print(test_block.new_acc)
    t1 = threading.Thread(target=test_block.mine_Acc())
    t1.start()
    t1.join()
    print(test_block.new_acc)
    #test_block.print_chain()
    for block in test_block.chain[1:]:
        for sub_block in block:
            print(sub_block.index,sub_block.votes,sub_block.hash)

    print("Root Hash is")
    print(test_block.chain[0].hash)


    #test_block.add_account("B.Tech", 3, 190010024)
    #print("B.tech Hash is")
    #print(test_block.compute_group_hash("B.Tech"))
    #print("M.tech Hash is")
    #print(test_block.compute_group_hash("M.Tech"))
    ##test_block.print_chain()
    #print("Root Hash is")
    #print(test_block.chain[0].hash)