from MintLottery import MintTx

if "Test no outs":
    mintTx = MintTx()
    mintTx.vin=[["i1", 1], ["i2", 2]]
    mintTx.calcResults()
    assert len(mintTx.results) == 2
    assert mintTx.results["i1"] == 1
    assert mintTx.results["i2"] == 2

if "Test one out":
    mintTx = MintTx()
    mintTx.vin=[["i1", 10], ["i2", 20]]
    mintTx.vout = [["o1", 6]]
    mintTx.calcResults()
    assert len(mintTx.results) == 2
    assert mintTx.results["i1"] == 8
    assert mintTx.results["i2"] == 16

if "Test one out is change":
    mintTx = MintTx()
    mintTx.vin=[["i1", 10], ["i2", 20]]
    mintTx.vout = [["i1", 6]]
    mintTx.calcResults()
    assert len(mintTx.results) == 2
    assert mintTx.results["i1"] == 8
    assert mintTx.results["i2"] == 16

if "Test change receives more":
    mintTx = MintTx()
    mintTx.vin=[["i1", 10], ["i2", 20]]
    mintTx.vout = [["i1", 15]]
    mintTx.calcResults()
    assert len(mintTx.results) == 2
    assert mintTx.results["i1"] == 5
    assert mintTx.results["i2"] == 10


if "Test zeros":
    mintTx = MintTx()
    mintTx.vin = [["i1", 0], ["i2", 10]]
    mintTx.vout = [["i1", 0], ["o1", 0]]
    mintTx.calcResults()
    assert len(mintTx.results) == 2
    assert mintTx.results["i1"] == 0
    assert mintTx.results["i2"] == 10

if "Mixed test":
    mintTx = MintTx()
    mintTx.vin=[["i1", 10], ["i2", 20], ["i3", 10], ["i4", 10]]
    mintTx.vout = [["i1", 5], ["i4", 20], ["o1", 5]]
    mintTx.calcResults()
    assert len(mintTx.results) == 4
    assert mintTx.results["i1"] == 4
    assert mintTx.results["i2"] == 8
    assert mintTx.results["i3"] == 4
    assert mintTx.results["i4"] == 4
