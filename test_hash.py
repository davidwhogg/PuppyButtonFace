import numpy as np

def get_wordlist():
    f = open("nounlist.txt", "r")
    s = f.read()
    f.close()
    return s.splitlines()

def hash(i, max):
    cycle = 2147483647    # MAGIC: 8th Mersenne Prime
    offset = 104729 ** 4  # MAGIC: 10,000th Prime
    return (i * cycle + offset) % max

def hashword(i, K, words):
    N = len(words)
    j = hash(i, N ** K)
    word = str(j) + " "
    for k in range(K):
        word += words[j % N]
        j /= N
    return word

def test_wordy():
    wordlist = get_wordlist()
    N = len(wordlist)
    K = 3
    for i in range(100):
        print hashword(i, K, wordlist)

def test_injectiveness():
    for Nwords in range(10000):
        count = np.zeros(Nwords)

        for i in range(Nwords):
            j = hash(i, Nwords)
            count[j] += 1

        if np.any(count != 1):
            print Nwords, "FAIL"
            print "min count", np.min(count)
            print "max count", np.max(count)
            return False
        else:
            print Nwords, "PASS"
    return True

if __name__ == "__main__":
    test_wordy()

