import numpy as np
import neurolab as nl
import pylab as pl
import pickle, math, random, operator
import pdb

# data from Oct 20, 2014, backwards, every hour
endTimeStamp= 1413763200

# get bitcoin price data	
execfile('dataFetcher.py')
priceData = pickle.load(open('../data/bitcoin_prices.pickle'))

class Window(list):

	def __init__(self, size):
		self.size = size

	def append(self, item):
		super(Window, self).append(item) 
		if len(self) > self.size:
			super(Window, self).pop(0)

	def isFull(self):
		return len(self) == self.size


class NeuralNetwork:

	def __init__(self, windowSize = 10, numFeatures = 100, numDataPoints = 1000, frequency = 3600):

		self.windowSize = windowSize
		self.numFeatures = numFeatures
		self.endTimeStamp = endTimeStamp
		self.numDataPoints = numDataPoints
		self.frequency = frequency
		self.priceData = aggregated_prices(priceData, self.endTimeStamp, self.numDataPoints, self.frequency)


	def toPercentChange(self):
		""" takes in an list of price data and returns a list of percentage change price data """
		percentChange = list()
		for i in range(1, len(self.priceData)):
			percentChange.append((self.priceData[i] - self.priceData[i - 1])/self.priceData[i - 1])
		return percentChange

	def simulate(self):
		# list holding all our predictions
		predictedPercentChanges = list() 

		# list holding all the actuall percentage changes
		actualPercentChanges = list()

		# list holding the predicted prices
		predictedPrices = list()

		percentChangePriceData = self.toPercentChange()
		inputVector = Window(self.numFeatures)
		targetVector = Window(self.numFeatures)
		featureVector = Window(self.windowSize)

		net = nl.net.newff([[-1, 1] for i in range(self.windowSize)], [self.windowSize, 1])

		# iterate over the price data to len(data) - 2 to avoid overflow because we predict step + 2 at each iteration
		for step in range(len(percentChangePriceData) - 2):

			featureVector.append(percentChangePriceData[step])
			if featureVector.isFull():
				inputVector.append(list(featureVector))
				targetVector.append(percentChangePriceData[step + 1])
				if inputVector.isFull() and targetVector.isFull():

					# we have enough input and target vectors to train the neural network 
					# create a 2 layer forward feed neural network
					
					inputs = np.array(inputVector).reshape(self.numFeatures, self.windowSize)
					targets = np.array(targetVector).reshape(self.numFeatures, 1)
					err = net.train(inputs, targets, goal = 0.01)
					
					# predict next time step
					testFeatureVector = featureVector[1:] + [percentChangePriceData[step + 1]]	
					out = net.sim([np.array(testFeatureVector)])
					predictedPercentChanges.append(out[0][0])
					predictedPrices.append((out[0][0] * self.priceData[step + 2]) + self.priceData[step + 2])
					actualPercentChanges.append(percentChangePriceData[step + 2])
					pdb.set_trace()
					print "Done with %f of the process" % (float(step)/len(percentChangePriceData) * 100)

		pl.figure(1)
		pl.title("Price Data")
		pl.subplot(211)
		pl.plot(range(len(predictedPrices)), self.priceData[len(self.priceData) - len(predictedPrices) :], 'b--')
		pl.subplot(212)
		pl.plot(range(len(predictedPrices)), predictedPrices, 'r--')

		def graphData(predictedPercentChanges, actualPercentChanges):

			def graphError(predictedPercentChanges, actualPercentChanges):
				# considering error and only considering it as error when the signs are different
				def computeSignedError(pred, actual):
					if (pred > 0 and actual > 0) or (pred < 0 and actual < 0):
						return 0
					else :
						return abs(pred - actual / actual) * 100

				signedError = map(lambda pred, actual: computeSignedError(pred, actual), predictedPercentChanges, actualPercentChanges)
				pl.figure(2)
				pl.title("Error")
				pl.subplot(211)
				pl.plot(signedError)
				pl.xlabel('Time step')
				pl.ylabel('Error (0 if signs are same and normal error if signs are different)')

				pl.figure(3)
				pl.title("Actual vs Predictions")
				pl.subplot(211)
				pl.plot(range(len(predictedPercentChanges)), predictedPercentChanges, 'r--', \
					range(len(actualPercentChanges)), actualPercentChanges, 'bs')

			def percentageCorrect(predictions, actuals):
				numCorrect = 0
				for i in range(len(predictions)):
					if (predictions[i] > 0 and actuals[i] > 0) or (predictions[i] < 0 and actuals[i] < 0):
						numCorrect = numCorrect + 1
				return numCorrect / float(len(predictions)) 

			print "The percentage correct is %f." % (percentageCorrect(predictedPercentChanges, actualPercentChanges))
			graphError(predictedPercentChanges, actualPercentChanges)		

		graphData(predictedPercentChanges, actualPercentChanges)
		pl.show()

		
def main():

	print "Starting Neural Network Simulations"
	# basicNeuralNetwork = NeuralNetwork()
	# basicNeuralNetwork.simulate()

	# # vary window size
	neuralNetwork1 = NeuralNetwork(20, 10, 500, 60)
	neuralNetwork1.simulate()

	# # larger window
	# neuralNetwork2 = NeuralNetwork(48, 10, 200)
	# neuralNetwork2.simulate()

	# # large window
	# neuralNetwork3 = NeuralNetwork(32, 10, 200)
	# neuralNetwork3.simulate()

	# # day sized window
	# neuralNetwork4 = NeuralNetwork(24, 10, 200)
	# neuralNetwork4.simulate()

	# half a day sized window
	# neuralNetwork5 = NeuralNetwork(12, 10, 200)
	# neuralNetwork5.simulate()

	# quarter of a day sized window
	#neuralNetwork6 = NeuralNetwork(6, 10, 200)
	#neuralNetwork6.simulate()


if __name__ == "__main__": 
	main()
