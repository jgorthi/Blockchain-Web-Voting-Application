from hashlib import sha256
import time



def compute_hash(input):
    #print(sha256(input.encode()).hexdigest())
    return sha256(input.encode()).hexdigest()


def proof_of_work(input):
    # nonce is the extra we added to achieve our criteria
    nonce = 0
    start = time.time()
    input_v2 = input + str(nonce)
    computed_hash = compute_hash(input_v2)
    while not computed_hash.startswith('0' * 6):
        nonce += 1
        input_v2 = input + str(nonce)
        computed_hash = compute_hash(input_v2)
        # print(computed_hash)
    end = time.time()
    print(f"Total runtime of the program is {end - start}")
    # For less than 5 within a second
    # For 6 about 2 seconds to 1 minute
    # For 7 about more than 2 minutes

    print("Extra added is ",nonce)
    # print(computed_hash)
    return computed_hash


string = "170010025 Adam"
print("The input string is ",string)
output = compute_hash(string)
print("Hash of the input is ",output)
output = proof_of_work(string)
print("PoW hash is ",output)

print("------------------------------------------------")

