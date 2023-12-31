import smartpy as sp

STEWARDSHIP_ARTIFACT_URI = "ipfs://QmX41L5CLVj4XYBW6ZzDhF4o7Z8Lkr2b3WpDAGLCgUa6RR"
STEWARDSHIP_DISPLAY_URI = "ipfs://QmeDtCRJhEJkm67MuXPkJQoR5Ui3fPpimb4WeAp9n2JLkk"
STEWARDSHIP_THUMBNAIL_URI = "ipfs://QmYjYprrgBpMtVZQwJPuqjqwwr7CSmEg7ja8eGyVGQTiY6"
STEWARDSHIP_TOKEN_SYMBOL = "STETK"

EVENT_ARTIFACT_URI = "ipfs://QmXziC8i7FhmRpk6FnRvrkUZHZRj6dwsijmcdA5fxgtzjt"
EVENT_DISPLAY_URI = "ipfs://Qmak5iJZB9s9FWFfTv6M36nkSQTKRcfH5Nu5Wyhb8GF5GM"
EVENT_THUMBNAIL_URI = "ipfs://QmQbT6ssZCZecaMLHUTn32VfG1c6iRu2zFz6DaEigNBzca"
EVENT_TOKEN_SYMBOL = "EVETK"

MetadataUrl = "ipfs://bafkreifzcdut2wzhwimkqby7qutbyg5zsjqf7qfm5iq7ashpbxwerdyzae"

class TokenMetadataGenerator(sp.Contract):
    def __init__(self, addr_data, orders, stewardship_token, event_token, metadata):
        self.init(
            addresses = addr_data,
            orders = orders,
            stewardship_token = stewardship_token,
            event_token = event_token,
            metadata = metadata
        )

    def is_admin(self):
        sp.verify(sp.sender == self.data.addresses["admin"], "NOT_ADMIN")

    @sp.entry_point
    def default(self):
        sp.send(sp.sender, sp.amount)

    @sp.entry_point
    def update_metadata(self, k, v):
        self.is_admin()
        self.data.metadata[k] = v
    
    @sp.entry_point
    def update_address(self, name, address):
        self.is_admin()
        self.data.addresses[name] = address
        
    @sp.entry_point
    def update_stewardship_token(self, key, value):
        self.is_admin()
        self.data.stewardship_token[key] = value
        
    @sp.entry_point
    def update_event_token(self, key, value):
        self.is_admin()
        self.data.event_token[key] = value
        
    @sp.entry_point
    def update_orders(self, key, value):
        self.is_admin()
        self.data.orders[key] = value

    @sp.onchain_view()
    def gen_stewardship_token(self, params):
        sp.set_type(params, sp.TRecord(multisig_name = sp.TBytes, multisig_description = sp.TBytes, generation = sp.TNat, creator = sp.TAddress))
        result = sp.local("result", self.data.stewardship_token)
        result.value["name"] = sp.utils.bytes_of_string("[STEWARDSHIP TOKEN GEN-") + self.data.orders[params.generation] + sp.utils.bytes_of_string("] ") +     params.multisig_name
        result.value["description"] = params.multisig_description
        result.value["creators"] = sp.pack(params.creator)
        sp.result(result.value)

    @sp.onchain_view()
    def gen_event_token(self, params):
        sp.set_type(params, sp.TRecord(event_name = sp.TBytes, event_description = sp.TBytes, multisig_name = sp.TBytes,generation = sp.TNat, creator = sp.TAddress))
        result = sp.local("result", self.data.event_token)
        result.value["name"] = sp.utils.bytes_of_string("[") + params.multisig_name + sp.utils.bytes_of_string(" GEN-") + self.data.orders[params.generation] + sp.utils.bytes_of_string(" EVENT TOKEN] ") + params.event_name
        
        result.value["description"] = params.event_description
        result.value["creators"] = sp.pack(params.creator)
        sp.result(result.value)
        


        
    
@sp.add_test(name = "DID token Metadata Generator")
def test():
    scenario = sp.test_scenario()
    scenario.h1("DID token Metadata Generator") 
    
    addrData = {}
    addrData["admin"] = sp.address("tz1UikAq5Po4wefKL4WkzAHqmCDVnUC1AKAS")

    addr_data = sp.big_map(
        tkey = sp.TString,
        tvalue = sp.TAddress,
        l = addrData
    )

    orderData = {}
    for i in range(1, 101):
        orderData[i] = sp.utils.bytes_of_string(str(i))

    orders = sp.big_map(
        tkey = sp.TNat,
        tvalue = sp.TBytes,
        l = orderData
    )
    
    url = MetadataUrl
    metadata = sp.big_map({"":sp.utils.bytes_of_string(url)})

    stewardship_token = sp.map(
        tkey = sp.TString,
        tvalue = sp.TBytes,
        l = {
            sp.string("symbol"): sp.utils.bytes_of_string(STEWARDSHIP_TOKEN_SYMBOL),
            sp.string("artifactUri"): sp.utils.bytes_of_string(STEWARDSHIP_ARTIFACT_URI),
            sp.string("displayUri"): sp.utils.bytes_of_string(STEWARDSHIP_DISPLAY_URI),
            sp.string("thumbnailUri"): sp.utils.bytes_of_string(STEWARDSHIP_THUMBNAIL_URI)
        }
    )

    event_token = sp.map(
        tkey = sp.TString,
        tvalue = sp.TBytes,
        l = {
            sp.string("symbol"): sp.utils.bytes_of_string(EVENT_TOKEN_SYMBOL),
            sp.string("artifactUri"): sp.utils.bytes_of_string(EVENT_ARTIFACT_URI),
            sp.string("displayUri"): sp.utils.bytes_of_string(EVENT_DISPLAY_URI),
            sp.string("thumbnailUri"): sp.utils.bytes_of_string(EVENT_THUMBNAIL_URI)
        }
    )

    c = TokenMetadataGenerator(addr_data, orders, stewardship_token, event_token, metadata)
    
    scenario += c