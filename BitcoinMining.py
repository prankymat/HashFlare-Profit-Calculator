import math
import os, sys
from functools import reduce
from collections import defaultdict

class Simulator:
	def __init__(self):
		self.btcPrice = float(input('BTC Price now (5000 USD): ') or '5000')
		self.difficulty = int(input('Current Difficulty (1196792694099): ') or '1196792694099')
		self.reward = float(input('Current Reward (12.5): ') or '12.5')
		self.hashRate = defaultdict(int)
		self.hashRate[0] = float(input('Your hashrate now (1 TH/s): ') or '1')
		self.profitADay = float(0)
		self.capital = float(input('Balance in BTC (0 BTC): ') or '0')
		self.reinvest = (input('Reinvesting? (T/F): ') or 'F').lower()
		self.minReinvestRate = (0.01, self.USDToBTC(1.5))
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
		self.hashRate[self.time] += self.minReinvestRate[0] * quantity

	def hashRateCurrently(self):
		rates = [self.hashRate[i] for i in range(0, self.time+1)]
		return reduce(lambda x,y: x+y, rates)

	def updateProfitADay(self):
		self.profitADay = (self.hashRateCurrently()*math.pow(10,12)*86400*self.reward)/(math.pow(2,32)*self.difficulty)

	def payout(self):
		self.capital += self.profitADay

	def pruneExpiredContracts(self):
		if self.time-365 >= 0:
			for i in range(0, self.time-365):
				if self.hashRate[i] != 0:
					print('Expiring', '{0:.2f}'.format(self.hashRate[i])+'TH/s', 'which was bought at day', i)
					self.hashRate[i] = 0

	def tick(self, interval = 1, eachTick = None):
		for i in range(0, interval):
			self.pruneExpiredContracts()
			self.payout()
			if self.reinvest:
				if self.canReinvest:
					self.buyRate(self.capital/self.minReinvestRate[1])
					self.updateProfitADay()
			if eachTick is not None:
				eachTick()
			self.time += 1

	def printStats(self):
		print('Day', str(self.time) + ':')
		print('Total Investment:', '{0:.2f}'.format(self.totalInvestment))
		print('Hash Rate:', '{0:.2f}'.format(self.hashRateCurrently()))
		print('Balance:', '{0:.15f}'.format(self.capital), 'approx in USD:', '{0:.2f}'.format(self.BTCToUSD(self.capital)))
		print('Profit a day:', '{0:.15f}'.format(self.profitADay), 'approx in USD:', '{0:.2f}'.format(self.BTCToUSD(self.profitADay)))
		print('--------------------')

	def printBalance(self):
		print(self.time,'{0:.15f}'.format(self.capital),'', sep=',')

	def printPayoutPerDay(self):
		# print(self.time,'{0:.2f}'.format(self.BTCToUSD(self.profitADay)),'', sep=',')
		print(self.time,'{0:.15f}'.format(self.profitADay),'', sep=',')


def getAction(userInput):
	arguments = userInput.split(' ')
	if len(arguments) > 1:
		return arguments[0], arguments[1:]
	else:
		print('Syntax Error!')
		return None, None


simulator = Simulator()
print('--------------------')
while True:
	userInput = input('>>> ').lower()
	if userInput == '':
		simulator.tick(1, simulator.printStats)
		continue

	if userInput == 'restart' or userInput == 'r':
		if os.name == 'nt':
			os.system('cls')
		else:
			os.system('clear')
		os.execl(sys.executable, sys.executable, *sys.argv)

	(action,arguments) = getAction(userInput)
	if action == 'tick' or action == 't':
		simulator.tick(int(arguments[0]), simulator.printStats)

