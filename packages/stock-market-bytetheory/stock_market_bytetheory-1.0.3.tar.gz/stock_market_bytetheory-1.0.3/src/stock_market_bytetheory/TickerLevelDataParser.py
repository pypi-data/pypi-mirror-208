from importlib.resources import files
import csv
import datetime as dt

class TickerLevelDataParser():

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        fileContents = self.readFileContents()
        cleanedFileContents = self.cleanFileContents(fileContents)
        dataOrganizedByTicker = self.organizeFileContentsByTicker(cleanedFileContents)
        return dataOrganizedByTicker

    def readFileContents(self):
        fin = files("stock_market_bytetheory.data").joinpath(self.filename)
        csvin = csv.reader(open(fin))
        rows = [row for row in csvin]
        del rows[0]
        return rows

    def cleanFileContents(self, fileContents):
        cleanedContents = []
        for row in fileContents:
            cleanedRow = self.cleanRow(row)
            cleanedContents.append(cleanedRow)
        return cleanedContents

    def cleanRow(self, row):
        rowWithDateReformatted = self.reformatDate(row)
        rowWithNumbersCastedToFloats = self.castNumbersToFloats(rowWithDateReformatted)
        return rowWithNumbersCastedToFloats
    
    def reformatDate(self, row):
        date = dt.datetime.strptime(row[0], "%Y%m%d")
        row[0] = date
        return row
    
    def castNumbersToFloats(self, row):
        for i, val in enumerate(row):
            try:
                row[i] = float(val)
            except:
                continue
        return row

    def organizeFileContentsByTicker(self, fileContents):
        dataOrganizedByTicker = {}
        for row in fileContents:
            dataOrganizedByTicker = self.addOrganizedRow(row, dataOrganizedByTicker)
        return dataOrganizedByTicker               

    def addOrganizedRow(self, row, organizedData):
        ticker = row[1]
        if(self.tickerHasBeenOrganized(ticker, organizedData)):
            organizedData[ticker].append(self.everythingButTicker(row))
        else:
            organizedData.update({ticker: [ self.everythingButTicker(row) ]})
        return organizedData

    def tickerHasBeenOrganized(self, ticker, organizedData):
        if(organizedData.get(ticker, None) == None):
            return False
        return True

    def everythingButTicker(self, row):
        return [ row[0] ] + row[2:]
        