import math
import os, sys
class Simulator:
	def __init__(self):
		self.btcPrice = float(input('BTC Price now (5000 USD): ') or '5000')
		self.litePrice = float(input('Litecoin Price now (5000 USD): ') or '5000')
		self.hashRate = float(input('Your hashrate now (1 MH/s): ') or '1')
		self.profitADay = float(0)
		self.capital = float(input('Balance in BTC (0 BTC): ') or '0')
		self.reinvest = (input('Reinvesting? (T/F): ') or 'F').lower()
		self.minReinvestRate = (1, self.USDToBTC(7.5))
		self.time = 0
		self.totalInvestment = 0
		self.updateProfitADay()

		if self.reinvest == 'true' or self.reinvest == 't':
			self.reinvest = True
		else:
			self.reinvest = False

	def USDToBTC(self, usd):
		return usd / self.btcPrice

	def BTCToUSD(self, btc):
		return btc * self.btcPrice

	def canReinvest(self):
		return self.capital >= self.minReinvestRate[1]

	def buyRate(self, quantity):
		quantity = math.floor(quantity)
		price = self.minReinvestRate[1] * quantity
		self.totalInvestment += self.BTCToUSD(price)
		self.capital -= price
		self.hashRate += self.minReinvestRate[0] * quantity

	def updateProfitADay(self):
		self.profitADay = (self.hashRate*0.00000606)

	def payout(self):
		self.capital += self.profitADay

	def tick(self, interval = 1, eachTick = None):
		for i in range(0, interval):
			self.time += 1
			self.payout()
			if self.reinvest:
				if self.canReinvest:
					self.buyRate(self.capital/self.minReinvestRate[1])
					self.updateProfitADay()
			if eachTick is not None:
				eachTick()

	def printStats(self):
		print('Day', str(self.time) + ':')
		print('Total Investment:', '{0:.2f}'.format(self.totalInvestment))
		print('Hash Rate:', '{0:.2f}'.format(self.hashRate))
		print('Balance:', '{0:.15f}'.format(self.capital), 'approx in USD:', '{0:.2f}'.format(self.BTCToUSD(self.capital)))
		print('Profit a day:', '{0:.15f}'.format(self.profitADay), 'approx in USD:', '{0:.2f}'.format(self.BTCToUSD(self.profitADay)))
		print('--------------------')


def getAction(userInput):
	arguments = userInput.split(' ')
	if len(arguments) > 1:
		return arguments[0], arguments[1:]
	else:
		print('Syntax Error!')
		return None, None


simulator = Simulator()
print('--------------------')
simulator.printStats()
while True:
	userInput = input('>>> ').lower()
	if userInput == 'restart' or userInput == 'r':
		if os.name == 'nt':
			os.system('cls')
		else:
			os.system('clear')
		os.execl(sys.executable, sys.executable, *sys.argv)

	(action,arguments) = getAction(userInput)
	if action == 'tick' or action == 't':
		simulator.tick(int(arguments[0]), simulator.printStats)

