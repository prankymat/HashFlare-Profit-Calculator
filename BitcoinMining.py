import math

class Simulator:
	def __init__(self):
		self.btcPrice = float(input("BTC Price now (5000 USD): ") or "5000")
		self.difficulty = int(input("Current Difficulty (1196792694099): ") or "1196792694099")
		self.reward = float(input("Current Reward (12.5): ") or "12.5")
		self.hashRate = float(input("Your hashrate now (1 TH/s): ") or "1")
		self.profitADay = float(0)
		self.capital = float(input("Balance in BTC (0 BTC): ") or "0")
		self.reinvest = (input("Reinvesting? (T/F): ") or "F").lower()
		self.minReinvestRate = (0.01, self.USDToBTC(1.5))
		self.time = 0
		self.totalInvestment = 0
		self.updateProfitADay()

		if self.reinvest == "true" or self.reinvest == "t":
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
		self.profitADay = (self.hashRate*math.pow(10,12)*86400*self.reward)/(math.pow(2,32)*self.difficulty)

	def payout(self):
		self.capital += self.profitADay

	def tick(self):
		self.time += 1
		self.payout()
		if self.reinvest:
			if self.canReinvest:
				self.buyRate(self.capital/self.minReinvestRate[1])
				self.updateProfitADay()

	def printStats(self):
		print("Day", str(self.time) + ":")
		print("Total Investment:", '{0:.2f}'.format(self.totalInvestment))
		print("Hash Rate:", '{0:.2f}'.format(self.hashRate))
		print("Balance:", '{0:.15f}'.format(self.capital), "approx in USD:", '{0:.2f}'.format(self.BTCToUSD(self.capital)))
		print("Profit a day:", '{0:.15f}'.format(self.profitADay), "approx in USD:", '{0:.2f}'.format(self.BTCToUSD(self.profitADay)))


simulator = Simulator()
print('--------------------')
while True:
	simulator.printStats()
	print('--------------------')
	simulator.tick()
	input()
