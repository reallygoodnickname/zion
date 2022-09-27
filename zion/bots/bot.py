from os.path import exists

# TODO: Add logging support, use logging instead of print


class Bot():
    def __init__(self, name):
        self.name = name
        self._checks = {}
        self._wordlists = {}

    # Check function wrapper
    # Adds function to checks list
    def check(self, *args, **kwargs):
        def inner(func):
            if "wordlists" not in kwargs:
                print("Wordlists not found!")
                exit(1)
            self._checks[func] = kwargs["wordlists"]
        return inner

    # Add wordlists to make use of them later
    def addWordlists(self, wordlists):
        for entry in wordlists:
            path = wordlists[entry]
            if exists(path):
                self._wordlists[entry] = self._unpack(path)
            else:
                print(f"File {path} does not exist, skipping!")

    # Get all words from wordlist in one array
    def _unpack(self, path):
        unpacked = []
        with open(path, 'r') as fd:
            for line in fd.readlines():
                unpacked.append(line.strip())
        return unpacked

    # Run all checks function and return
    # true if anything triggers
    def runChecks(self, msg):
        for func in self._checks:
            wordlists = self._checks[func]
            for wordlist in wordlists:
                if func(msg, self._wordlists[wordlist]):
                    return True
        return False
