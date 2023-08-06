import xml.etree.ElementTree as ET
from importlib.resources import files

class SectorIndustryTickerParser():

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        fileContents = self.readFileContents()
        hierarchy = self.convertFileContentsToHierarchy(fileContents)
        return hierarchy

    def readFileContents(self):
        fileContents = files('stock_market_bytetheory.data').joinpath(self.filename).read_text()
        return ET.fromstring(fileContents)
    
    def convertFileContentsToHierarchy(self, fileContents):
        hierarchy = {}
        for ticker in fileContents:
            self.addTickerToHierarchy(ticker, hierarchy)
        return hierarchy

    def addTickerToHierarchy(self, ticker, hierarchy):
        # Note: Tickers cannot have more than one industry. Industries
        # may have more than one sector. Tickers are not repeated
        # in the file we're working with.

        tickerName = ticker.attrib["ticker"]
        tickerIndustry = ticker.attrib["industry"]
        tickerSector = ticker.attrib["sector"]

        if(
            self.sectorExistsInHierarchy(tickerSector, hierarchy) and
            self.industryExistsInHierarchy(tickerIndustry, tickerSector, hierarchy)
        ):
            hierarchy[tickerSector][tickerIndustry].append(tickerName)
        
        elif(
            self.sectorExistsInHierarchy(tickerSector, hierarchy) and
            not self.industryExistsInHierarchy(tickerIndustry, tickerSector, hierarchy)
        ):
            hierarchy[tickerSector][tickerIndustry] = [tickerName]

        else:
            hierarchy[tickerSector] = {tickerIndustry: [tickerName]}

    def sectorExistsInHierarchy(self, sector, hierarchy):
        if(hierarchy.get(sector, None) == None):
            return False
        return True
    
    def industryExistsInHierarchy(self, industry, sector, hierarchy):
        if(self.sectorExistsInHierarchy(sector, hierarchy)):
            industryExists = len(['match' for ind in hierarchy[sector].keys() if ind == industry])
            if(industryExists):
                return True
        return False

    


