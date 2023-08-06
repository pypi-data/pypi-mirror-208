


class Classification:
    def __init__(self, data:dict):
        self.nameAcount = data["nameAcount"]
        self.identifier = data["identifier"]
        self.number = data["number"]
        self.date = data["date"]
        self.totalExcludingPackage = data["totalExcludingPackage"]
        
        self.local = Local(data["local"])
        self.roaming = Roaming(data["roaming"])
        

    

class Local:
    
    def __init__(self, data:dict):
        self.internet = Internet(data["internet"], True)
        self.call = Appel(data["call"])
        self.sms = SMS(data["SMS"])
        self.mms = MMS(data["MMS"])
        
    
class Roaming:
    
    def __init__(self, data:dict):
        self.internet = Internet(data["internet"], False)
        self.call = Appel(data["call"])
        self.sms = SMS(data["SMS"])
        self.mms = MMS(data["MMS"])

class Internet:
    
    def __init__(self, data:dict, carbonFootprint:bool):
        self.conso = data["conso"]
        self.total = data["consoMax"]
        self.remaining = data["remaining"]
        self.excludingPackage = data["excludingPackage"]
        
        if carbonFootprint: self.carbonFootprint = data["carbonFootprint"]

class Appel:
    
    def __init__(self, data:dict):
        self.conso = data["conso"]
        self.total = data["consoMax"]
        self.callToMyCountry = data["callToMyCountry"]
        self.callToInternational = data["callToInternational"]
        self.excludingPackage = data["excludingPackage"]

class SMS:
    
    def __init__(self, data:dict):
        self.conso = data["conso"]
        self.total = data["consoMax"]
        self.maxNbSMS = data["maxNbSMS"]
        self.nbSMS = data["nbSMS"]
        self.excludingPackage = data["excludingPackage"]
        
        
class MMS:
    
    def __init__(self, data:dict):
        self.conso = data["conso"]
        self.total = data["consoMax"]
        self.maxNbMMS = data["maxNbMMS"]
        self.nbMMS = data["nbMMS"]
        self.excludingPackage = data["excludingPackage"]