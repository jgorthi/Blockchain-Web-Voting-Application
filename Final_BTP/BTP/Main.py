from Blockchain import Blockchain
from Acc_Blockchain import Acc_Blockchain
from flask import Flask, redirect, url_for, render_template, request, session
import re
import threading

if __name__ == '__main__':

    test_blockchain = Blockchain() # Intialize basic blockchain which stores vote strings
    acc_blockchain = Acc_Blockchain() # Intialize Merkle tree blockchain to contain accounts of voted students
    state = 0 # State variable to keep track of whether the blockchains are mining or verifying

    #print(test_blockchain.chain[0].__dict__)
    #
    #test_blockchain.add_new_vote("170010001 vote to Jaswanth")
    #test_blockchain.add_new_vote("180010002 vote to Adam")
    #print(test_blockchain.new_votes)
    #test_blockchain.mine()
    #try :print(test_blockchain.chain[1].__dict__)
    #except(IndexError):
    #    print("Not added")


    app = Flask(__name__)
    app.secret_key = "Simple"


    # Page for voter registration
    @app.route("/", methods=["POST", "GET"])
    def create_Acc():

        if request.method == "POST":
            _roll = request.form["Roll_no"]
            # Check if the roll number is valid
            _valid = re.match("[1-2][6-9][0][0][1-3][0][0][0-3][0-9]", _roll)

            if not bool(_valid):
                return "Invalid"

            # Figure out which year and group from roll number
            _group = acc_blockchain.which_group(_roll)
            _year = acc_blockchain.which_year(_roll)

            if not acc_blockchain.is_valid_roll(_group,_year, _roll):
                return "Invalid"

            session["_roll"] = _roll
            session["_group"] = _group
            session["_year"] = _year
            #acc_blockchain.print_chain()
            return redirect(url_for("vote"))

        else:
            return render_template("create_Acc.html")


    # Page for voting to prefered candidate. We will add vote in buffer of both blockchains
    @app.route("/vote", methods=["POST", "GET"])
    def vote():

        if request.method == "POST":
            if "_roll" in session:
                _voter = session["_roll"]
                _group = session["_group"]
                _year  = session["_year"] 
            else:
                return "Login"

            _cad = request.form["CAD"]
            vote_string = _voter + " " + _cad

            # Check whether candidate name is valid
            if not any(_cad in cad_accounts for cad_accounts in acc_blockchain.chain[-1][0].votes):
                return "No such Candidate"

            # Add account to buffer
            if not acc_blockchain.add_tem_acc(_group, _year, _voter, _cad):
                return "Invalid"

            test_blockchain.add_new_vote(vote_string)
            acc_blockchain.vote_to_cad_buffer(_cad)
            #print(test_blockchain.new_votes)
            #if len(test_blockchain.new_votes) == 3:
                #test_blockchain.mine()
                #print(test_blockchain.last_block().__dict__)
            #acc_blockchain.print_chain()
            return render_template("Success.html")

        else:
            return render_template("API.html")


    # Page to add candidate
    @app.route("/add_cad", methods=["POST", "GET"])
    def add_candidate():

        if request.method == "POST":
            _cad = request.form["name"]
            acc_blockchain.add_cad(_cad)
            #acc_blockchain.print_chain()
            return render_template("Success.html")

        else:
            return render_template("add_Candidate.html")


    # Page to print results, will shows all candidates and their vote count
    @app.route("/results", methods=["POST", "GET"])
    def print_res():

        results = acc_blockchain.cad_results()
        result_string = ""

        for cad_res in results:
            result_string = result_string  + cad_res[0] + " has " + str(cad_res[1]) + " votes <br>"

        return f"{result_string}"


    # Shows the basic blockchain. Prints each block and its contents
    @app.route("/see_blockchain", methods=["POST", "GET"])
    def print_blockchain():

        votes = ""

        if request.method == "GET":

            for block in test_blockchain.chain:
                votes = votes + "The block with index " +str(block.index) + " <br> has "
                votes = votes + str(block.votes) + " list of votes " + "<br>"
                votes = votes + " and has hash " + str(block.hash)  + "<br>" + " and previous hash " + str(block.previous_hash) + "<br>"
                votes = votes + "<br>"
            return f"{votes}"

        else:
            return "None"


    # Shows the Merkle tree blockchain. Prints each block and its contents
    @app.route("/see_accounts", methods=["POST", "GET"])
    def print_acc_blockchain():

        accounts = ""

        if request.method == "GET":

            # Adding the root node
            accounts = accounts + acc_blockchain.chain[0].index + " has hash " + str(acc_blockchain.chain[0].hash) + "<br>"
            accounts = accounts + "<br>"

            for block in acc_blockchain.chain[1:-1]:

                # Adding the parent node of leaf nodes
                accounts = accounts + block[0].index + " contains sub-tress " + "<br>"
                accounts = accounts + "<br>"

                for sub_block in block[1:]:
                    # Adding the leaf nodes
                    accounts = accounts + " ------- Children " + sub_block.index + " Which contains accounts " + str(sub_block.votes) + "<br>" + "and has hash "+ str(sub_block.hash) + "<br>"
                    accounts = accounts + "<br>"

                accounts = accounts + " and " + block[0].index + " has hash " + str(block[0].hash) + "<br>"
                accounts = accounts + "<br>"

            # Adding the candidate node
            accounts = accounts + acc_blockchain.chain[-1][0].index + " Which contains accounts " + str(acc_blockchain.chain[-1][0].votes) + "<br>" + " has hash " + str(acc_blockchain.chain[-1][0].hash) + "<br>"
            accounts = accounts + "<br>"


            return accounts

        else:
            return "None"


    # Function to verify whether the blockchain is compromsied or not
    @app.route("/verify_blockchain", methods=["POST", "GET"])
    def verify_blockchain():

        if request.method == "GET":
            check = test_blockchain.verify()
            if check:
                return "The Blockchain is Good"
            else:
                return "Chain is Hacked"

        else:
            return "None"


    # Shows all the votes in buffer
    @app.route("/see_new_votes", methods=["POST", "GET"])
    def new_votes_print():

        if request.method == "GET":
            string = ""

            for new_vote in test_blockchain.new_votes:
                string = string + " " + new_vote;

            if string:
                return string
            else:
                return "No new votes"

        else:
            return "None"


    # Can be used to intialize mining process of merkle tree blockchain
    # old
    @app.route("/mine_Accounts", methods=["POST", "GET"])
    def acc_mine_test():

        if request.method == "GET":
            acc_blockchain.mine_Acc()
            return "Done"

        else:
            return "None"


    # Miner function which uses multithreading to mine both blockchains at the same time
    # returns when both blockchains mining is completed
    def final_miner():
        vote_blockchain = threading.Thread(target=test_blockchain.mine)
        account_blockchain = threading.Thread(target=acc_blockchain.mine_Acc)
        # Start the mining thread for basic blockchian
        vote_blockchain.start()
        # Start the mining thread for merkle tree blockchain
        account_blockchain.start()
        # Wait for both mining threads to complete, then return
        vote_blockchain.join()
        account_blockchain.join()
        return True


    # Initialing the State

    state = 0

    # State = 0 Free
    # State = 1 In Mining
    # State = 2 Minig Done
    # State = 3 Verifying
    # State = 4 Verifying done
    # State = 5 Hacked


    # Function to excetute the mining and verifying threads one after the another
    # After a specific interval of time
    def M_and_V_threads(state):

        # Start Mining after Free State or Verifying Completed Successfully
        if state == 0 or state == 4:

            print("Checking for mining")

            if len(test_blockchain.new_votes) >= 3 and len(test_blockchain.new_votes) == len(acc_blockchain.new_acc):
                mine_thread = threading.Thread(target = final_miner)
                state = 1
                # Start the mining of both blockchains
                mine_thread.start()
                # Wait for it to complete, then change state to mining done and ready to be verified
                mine_thread.join()
                state = 2
            else:
                print("Not enough to mine")
                state = 2

        # Start Verifying after Mining is completed
        if state == 2:

            print("Verifying")

            verify_thread = threading.Thread(target = test_blockchain.verify_timer_v2, args = [acc_blockchain])
            state = 3
            verify_thread.start()
            verify_thread.join()
            state = 4

        # Timer function to excetute the function every n seconds
        threading.Timer(5.0, M_and_V_threads, [state]).start()
        return None



    # Starting the Program Execution
    # Start the timer for mining and verifying threads
    M_and_V_threads(state)

    #test_blockchain.mine_timer()
    #test_blockchain.verify_timer_v2(acc_blockchain)

    app.run()



