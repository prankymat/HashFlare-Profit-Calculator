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
		self.reinvest = (input('Reinvesting? (on/off): ') or 'off').lower()
		self.minReinvestRate = (0.01, self.USDToBTC(1.5))
		self.maintenance = self.USDToBTC(0.35)
		self.time = 0
		self.totalInvestment = 0
		self.updateProfitADay()

		if self.reinvest in ['on', 'true', 't']:
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

	def chargeMaintenance(self):
		self.capital -= self.maintenance * self.hashRateCurrently()

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
			self.chargeMaintenance()
			if self.reinvest:
				if self.canReinvest:
					self.buyRate(self.capital/self.minReinvestRate[1])
			self.updateProfitADay()
			if eachTick is not None:
				eachTick()
			self.time += 1

	def printStats(self):
		print('Day', str(self.time) + ':')
		print('Reinvesting is', 'on' if self.reinvest else 'off')
		print('Total Investment:', '{0:.2f}'.format(self.totalInvestment))
		print('Hash Rate:', '{0:.2f}'.format(self.hashRateCurrently()))
		print('Payout a day:', '{0:.15f}'.format(self.profitADay), 'approx in USD:', '{0:.2f}'.format(self.BTCToUSD(self.profitADay)))
		print('Maintenance fee:', '{0:.15f}'.format(self.maintenance * self.hashRateCurrently()))
		print('Balance:', '{0:.15f}'.format(self.capital), 'approx in USD:', '{0:.2f}'.format(self.BTCToUSD(self.capital)))
		print('--------------------')

	def printBalance(self):
		print(self.time,'{0:.15f}'.format(self.capital),'', sep=',')

	def printPayoutPerDay(self):
		print(self.time,'{0:.15f}'.format(self.profitADay),'', sep=',')


def getAction(userInput):
	arguments = userInput.split(' ')
	try:
		if arguments[0] == '':
			return 'tick', [1]
		elif arguments[0] == 'tick' or arguments[0] == 't':
			return 'tick', arguments[1:]
		elif arguments[0] == 'change' or arguments[0] == 'c':
			return 'change', arguments[1:]
	except IndexError:
		print('Syntax Error!')
		return None, None


simulator = Simulator()
print('--------------------')
while True:
	userInput = input('>>> ').lower()
	(action,arguments) = getAction(userInput)

	if action == 'tick':
		interval = 1
		if len(arguments) == 1:
			interval = int(arguments[0])
		simulator.tick(interval, simulator.printStats)

	elif action == 'change':
		try:
			arg = arguments[0]
			if arg == 'all':
				print("Resetting the simulation...")
				simulator = Simulator()  # reinit the Simulator
				print("Simulation has been reset!")
			elif arg == 'capital':
				simulator.capital = float(arguments[1])
			elif arg == 'reinvest':
				shouldReinvest = True if arguments[1] in ['on', 'true', 't'] else False
				if shouldReinvest:
					print("Reinvesting is now on")
				else:
					print("Reinvesting is now off")
				simulator.reinvest = shouldReinvest
		except IndexError:
			print('\nPossible arguments after "change" are:\n'
				  '\tall\n'
				  '\tcapital [amount]\n'
				  '\treinvest [on/off]\n'
				 )

