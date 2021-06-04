import subprocess, os, collections, time
from hashlib import sha256
import random
from decimal import Decimal
import json

class MintTx:
    def __init__(self):
        self.vin=[]
        self.vout=[]
        self.results= collections.OrderedDict()
        self.results.setdefault(0)
    def calcResults(self):
        vinAmount = Decimal(0)
        voutAmount = Decimal(0)
        self.results = {}
        for input in self.vin:
            vinAmount = vinAmount + input[1]
            self.results[input[0]] = self.results.get(input[0], Decimal(0)) + input[1]
        for output in self.vout:
            voutAmount = voutAmount + output[1]
        if voutAmount != 0 and vinAmount != 0:
            for ra, rv in self.results.items():
                if rv != 0:
                    rv = rv - voutAmount * rv / vinAmount
                    self.results[ra] = rv

########################################################################################################################

def Log(message:str):
    print(message)

def Run(params):
    result = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception("Execution error: {}".format(result.stderr))
    return result.stdout.rstrip().decode('ascii')

def ParseTx(tx:str):
    return json.loads(tx, parse_float=Decimal)

def ParseBlock(block:str):
    return json.loads(block)

########################################################################################################################

class MintLottery:
    def run(self, startHeight:int, endHeight:int, winnerNum:int):
        height = startHeight
        results = []
        digest = sha256()
        mintNum = 0
        while height <= endHeight:
            Log("Handling height {}".format(height))
            block = self.getBlock(height)
            txs = self.getTxs(block)
            for tx in txs:
                mintTx = MintTx()
                mintTx.vin = tx["vin"]
                mintTx.vout = tx["vout"]
                mintTx.calcResults()
                for addr, val in mintTx.results.items():
                    if addr not in self.usedAddrs:
                        results.append([addr, val])
                        self.usedAddrs.add(addr)
                        digest.update("{}:{} ".format(addr, val).encode("utf-8"))
                        Log("Registering mint {} {}:{}".format(mintNum, addr, val))
                        mintNum += 1
            height += 1

        random.seed(digest.hexdigest(), version = 2)
        winners = []
        for i in range(0, winnerNum):
            winNum = random.randint(0, len(results)-1)
            Log("The winner index is: {}".format(winNum))
            winners.append(results[winNum])

        winners.sort(reverse=True, key=lambda x: (x[1], x[0]))
        i = 0
        for addr, val in winners:
            print("{}. The winner is {} with amount {}".format(i, addr, val))
            i += 1
        Log("Total mints: {}".format(self.txs))

    def __init__(self, firoCliPath:str):
        self.mintStats = {}
        self.firoCli = os.path.join(firoCliPath, "firo-cli")
        self.txs = 0
# The following addresses are excluded because of their involvement in the recent ValueDeFi hack        
        self.usedAddrs = {
            "aDFpcLgCavmY4H27xxKHw7AwEq5PoNTk3Z",
            "aHifKFgNh6Z3cPUznZu8zm15esXDquGrTo",
            "aAXjaB6BpvyDuBxK9P4JL8M5L7cibXP4tE",
            "aGvzV7ErzTuNS7Zna37mvSwxphHQDw4igZ",
            "aBqQVPf5iBAjH2xWCCY9Bo1uDWr6hbKr3H",
            "aBVVgGQEV3ckxYgD3Xyk7rPKTm5jroNYbY",
            "a6qnPx1CYsKnW4bywhWnrgCBRez6QNWvJQ",
            "aJfhthNWXQg16C8AZMkF2rwBcxGMbCRwsu",
            "aHoD3xg5FenrtiwFW82tSF8gmV5LyZjVYh",
            "a6cFMBD823WG67gn6WhN1Tw2uaSzYiDCwb"
        }

    def getBlock(self, height:int):
        hash = ""
        received = False
        while not received:
             try:
                 hash = Run([self.firoCli, "getblockhash", "{}".format(height)])
                 received = True
             except:
                 Log("Cannot get block {}, waiting".format(height))
                 time.sleep(60)
        return ParseBlock(Run([self.firoCli, "getblock", "{}".format(hash)]))

    def getTxs(self, block):
        txIds = block["tx"]
        txs = []
        for txNum in range(0, len(txIds)):
            rawTx = ""
            received = False
            while not received:
                try:
                    rawTx = Run([self.firoCli, "getrawtransaction", "{}".format(txIds[txNum]), "1"])
                    received = True
                except:
                    Log("Cannot get tx {}, waiting".format(txIds[txNum]))
                    time.sleep(60)
            if rawTx.find("OP_LELANTUSMINT") == -1:
                continue
            jsonTx = ParseTx(rawTx)
            self.txs += 1
            tx = {}
            newVin = []
            vinTotal = 0
            noVin = True
            for input in jsonTx["vin"]:
                vinTotal += input["value"]
                if input["value"] >= 1:
                    newVin.append([input["address"], input["value"]])
                    noVin = False
            if noVin:
                continue
            tx["vin"] = newVin
            newVout = []
            voutTotal = 0
            for output in jsonTx["vout"]:
                voutTotal += output["value"]
                if output["scriptPubKey"]["hex"].find("c5") != 0:
                    newVout.append([output["scriptPubKey"]["addresses"], output["value"]])
            newVout.append(["fee", vinTotal - voutTotal])
            tx["vout"] = newVout
            txs.append(tx)
        return txs

if __name__ == "__main__":
    mintStats = MintLottery("/usr/local/bin/")
    mintStats.run(369000, 377630 , 25)
