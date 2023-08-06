import functools
import pprint as pp

from stock_market_bytetheory import SectorIndustryTickerParser, TickerLevelDataParser


class SP500History:
    def __init__(self):
        self.sectorIndustryTickerHierarchy = SectorIndustryTickerParser(
            "SP_500.xml"
        ).parse()
        self.tickerLevelData = TickerLevelDataParser("SP500_ind.csv").parse()

    def getTickersForIndustry(self, industry, sector):
        tickers = self.sectorIndustryTickerHierarchy[sector][industry]
        return tickers

    def getAllSectorsAndIndustries(self):
        return {
            sector: self.getIndustriesForSector(sector)
            for sector in self.sectorIndustryTickerHierarchy.keys()
        }

    def getIndustriesForSector(self, sector):
        return [
            industry for industry in self.sectorIndustryTickerHierarchy[sector].keys()
        ]

    def getPricingMetricsForIndustry(self, industry, sector):
        metrics = []
        tickers = self.sectorIndustryTickerHierarchy[sector][industry]
        for ticker in tickers:
            try:
                metrics.append(self.getAllMetricsForTicker(ticker))
            except Exception as e:
                print(e)
        return metrics

    def getAllMetricsForTicker(self, ticker):
        return {
            "ticker": ticker,
            "vwap": self.getVolumeWeightedAveragePrice(ticker),
            "avgOpen": self.getAverageOpenPrice(ticker),
        }

    def getVolumeWeightedAveragePrice(self, ticker):
        # Return the volume weighted average price of the stock.  In order to do this,
        # first find the average price of the stock on each day.  Then, multiply that price with the
        # volume on that day.  Take the sum of these values. Finally, divide that value by the sum of all the volumes.
        # (note: average price for each day = (high + low + close)/3)
        sumOfWeightedDailyPrices = 0
        sumOfDailyVolume = 0
        for dayOfPriceData in self.tickerLevelData[ticker]:
            [
                date,
                openPrice,
                highPrice,
                lowPrice,
                closePrice,
                volumeForDay,
            ] = dayOfPriceData
            averagePrice = self.computeAveragePriceForDay(
                highPrice, lowPrice, closePrice
            )
            sumOfWeightedDailyPrices += self.computeWeightedPriceForDay(
                averagePrice, volumeForDay
            )
            sumOfDailyVolume += volumeForDay
        return float(sumOfWeightedDailyPrices / sumOfDailyVolume)

    def computeAveragePriceForDay(self, high, low, close):
        return (high + low + close) / 3

    def computeWeightedPriceForDay(self, averagePrice, volume):
        return averagePrice * volume

    def getAverageOpenPrice(self, ticker):
        return self.sumOfAllOpenPrices(ticker) / self.numberOfOpenPrices(ticker)

    def sumOfAllOpenPrices(self, ticker):
        def addOpenPrices(runningSum, dayPrice):
            openPrice = dayPrice[2]
            return runningSum + openPrice

        return functools.reduce(addOpenPrices, self.tickerLevelData[ticker], 0)

    def numberOfOpenPrices(self, ticker):
        return len(self.tickerLevelData[ticker])

    def findReturn(self, ticker, start, end):
        # Uses the opening price on the starting date, and the closing price on the ending date.
        openPriceOnStartDate = self.findOpenPriceOnStartDate(ticker, start)
        closePriceOnEndDate = self.findClosePriceOnEndDate(ticker, end)
        return float(
            (closePriceOnEndDate - openPriceOnStartDate) / openPriceOnStartDate
        )

    def findOpenPriceOnStartDate(self, ticker, startDatetime):
        for dayOfPriceData in self.tickerLevelData[ticker]:
            openPrice = dayOfPriceData[1]
            priceDay = dayOfPriceData[0].day
            priceMonth = dayOfPriceData[0].month
            priceYear = dayOfPriceData[0].year
            startDay = startDatetime[1]
            startMonth = startDatetime[0]
            startYear = startDatetime[2]
            if (
                priceDay == startDay
                and priceMonth == startMonth
                and priceYear == startYear
            ):
                return openPrice
        else:
            message = startDatetime.strftime(
                "No data exists for this ticker on the start date of %d, %b %Y"
            )
            raise Exception(message)

    def findClosePriceOnEndDate(self, ticker, closeDatetime):
        for dayOfPriceData in self.tickerLevelData[ticker]:
            closePrice = dayOfPriceData[4]
            priceDay = dayOfPriceData[0].day
            priceMonth = dayOfPriceData[0].month
            priceYear = dayOfPriceData[0].year
            endDay = closeDatetime[1]
            endMonth = closeDatetime[0]
            endYear = closeDatetime[2]
            if priceDay == endDay and priceMonth == endMonth and priceYear == endYear:
                return closePrice
        else:
            message = closeDatetime.strftime(
                "No data exists for this ticker on the end date of %d, %b %Y"
            )
            raise Exception(message)
