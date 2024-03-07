import json
class Deal:
    messageReceived=''
    dealId=''
    separatedText=''
    store=''
    dealType=''
    storeUrl=''
    productTitle=''
    imageUrl=''
    storerating=-0.1
    brand=''
    dealPrice=0
    mrp=1.1
    finalMessage=''
    category=''
    dealTime=''
    channel=''
    dealPercent=0
    aiMessage=''
    shortURL=''
    
    aff_url=''
    
    first_url=''
    
    
    
    
    
    

    ##TEMP PARAMETERS
    finalRedirectURL=''
    originalURL=''

    messageType=''

    

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            deal_dict = json.loads(json_data)
        elif isinstance(json_data, dict):
            deal_dict = json_data
        else:
            raise ValueError("Invalid JSON data provided")

        deal = cls()
        deal.__dict__ = deal_dict
        return deal
    



    #@classmethod
    #def from_json(cls, json_str):
    #    deal = cls()
    #    deal_dict = json.loads(json_str)
    #    deal.__dict__.update(deal_dict)
    #    return deal