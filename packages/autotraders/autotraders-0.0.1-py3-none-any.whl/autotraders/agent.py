from sdk.contract import Contract
from sdk.ships import Ship, get_all_ships


class Agent:
    def __init__(self, session):
        self.session = session
        self.update()

    def update(self):
        r = self.session.get("https://api.spacetraders.io/v2/my/agent")
        j = r.json()
        if "error" in j:
            raise IOError(j["error"]["message"])
        self.account_id = j["data"]["accountId"]
        self.symbol = j["data"]["symbol"]
        self.headquarters = j["data"]["headquarters"]
        self.credits = j["data"]["credits"]
        self.ships = get_all_ships(self.session)
        r = self.session.get("https://api.spacetraders.io/v2/my/contracts")
        j = r.json()
        self.contracts = []
        for contract in j["data"]:
            c = Contract(contract["id"], self.session, False)
            c.update(contract)
            self.contracts.append(c)