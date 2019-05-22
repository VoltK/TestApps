# Чтобы использовать скрипт нужен свежий api key и чистый IP.
# Изначально используется новый API с ключем c лимитом в 250,000 bits, когда все bits использованы
# Идет переключение на старый API, с которого можно еще использовать 1,000,000 bits

# ИСПОЛЬЗОВАНИЕ:
# python random_million_generator.py <YOUR_KEY>
# ПЕРЕД ЭТИМ:
# pip install requests
# pip install beautifulsoup4

from bs4 import BeautifulSoup
import requests
import json
import sys


# static method
def handle_error(data):
    if "error" in data:
        error = data['error']
        code = error['code']
        msg = error['message']

        sys.exit(f"[-] API ERROR OCCURRED:\n\t1) status code: {code}\n\t2) message: {msg}")


class RandomMillionGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        # it uses both APIs
        # first it starts with new one
        self.new_api = "https://api.random.org/json-rpc/2/invoke"
        # after we used all bits available, it'll switch to old one, because that one allows 1,000,000 bit per day
        self.old_api = "https://www.random.org/integers/?num=10000&min=0&max=1&col=15&base=10&format=html&rnd=new"
        # there is a limit of max allowed numbers per each request equals to 10000
        # so I break 1000000 into 100 chunks.
        self.TOTAL_NUMBERS = 10000
        self.TOTAL_REQUESTS = 100
        # default daily amount of bits available
        self.bits_left = 250000
        self.data = []
        # main storage for results
        self.results = {
            "singles": {
                "0": 0,
                "1": 0
            },
            "doubles": {
                "00": 0,
                "01": 0,
                "10": 0,
                "11": 0
            },
            "triples": {
                "000": 0,
                "001": 0,
                "010": 0,
                "100": 0,
                "101": 0,
                "011": 0,
                "110": 0,
                "111": 0
            }
        }

    def new_api_get_integers(self):
            headers = {"Content-Type": "application/json"}
            params = {
                "jsonrpc": "2.0",
                "method": "generateIntegers",
                "params": {
                    "apiKey": self.api_key,
                    "n": self.TOTAL_NUMBERS,
                    "min": 0,
                    "max": 1,
                },
                "id": 32218
            }

            response = requests.post(self.new_api, data=json.dumps(params), headers=headers)
            data = response.json()
            handle_error(data)
            print(data)
            self.bits_left = data["result"]["bitsLeft"]
            self.data = data["result"]["random"]["data"]

    def old_api_get_integers(self):
        # for using old API, script parses html
        response = requests.get(self.old_api)
        soup = BeautifulSoup(response.text, 'lxml')
        # cleaning numbers from new lines
        numbers = soup.find("pre", class_="data").text.replace("\n", "\t")
        # split string into list and convert all elements into integers
        self.data = [int(number) for number in numbers.split("\t") if number != ""]

    def calculate_singles(self):
        for key in self.results["singles"]:
            self.results["singles"][key] += self.data.count(int(key))

    def calculate_doubles(self):
        # if a sublist equals to a sublist from key([0,1], [1,0] etc) ->
        # add 1 to a list -> calculate list's size -> modify key's value
        for key in self.results["doubles"]:
            # convert string key to a list
            key_sequence = [int(x) for x in key]
            self.results["doubles"][key] += len([1 for x in range(len(self.data) - 1)
                                            if [self.data[x], self.data[x + 1]] == key_sequence])

    # same as calculate_doubles
    def calculate_triples(self):
        for key in self.results["triples"]:
            key_sequence = [int(x) for x in key]
            self.results["triples"][key] += len([1 for x in range(len(self.data) - 2)
                                            if [self.data[x], self.data[x + 1], self.data[x + 2]] == key_sequence])

    def pick_function(self):
        if self.bits_left >= self.TOTAL_NUMBERS:
            self.new_api_get_integers()
        else:
            self.old_api_get_integers()

    def calculate_all(self):
        self.calculate_singles()
        self.calculate_doubles()
        self.calculate_triples()

    def print_results(self):
        print("\n[!] CALCULATING...\n[+] RESULTS:")
        for category, values in self.results.items():
            print(f"[*] {category}: ")
            total = sum(self.results[category].values())
            for sequence, count in values.items():
                percent = format(count * 100 / total if total != 0 else total, ".2f")
                print(f"\t{sequence}: {count} {percent}%")

    def make_all(self):
        print("[!] Start requesting random integers from RANDOM.ORG")
        for _ in range(self.TOTAL_REQUESTS):
            print("[*] MOVING TO THE NEXT CHUNK")
            # run either one api function
            self.pick_function()
            # do calculations
            self.calculate_all()

            print("[+] All results from this request were gathered")

        self.print_results()


if len(sys.argv) == 2:
    api_key = sys.argv[1]
    print("[!] Your API KEY is " + api_key)
else:
    sys.exit("[-] You didn't specify API KEY. Exiting...")

millions_info = RandomMillionGenerator(api_key)
millions_info.make_all()