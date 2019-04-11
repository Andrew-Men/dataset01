#!/usr/local/anaconda3/envs/kaggle/bin python
import os
import glob
import numpy as np
import imageio
import keras
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D, Flatten, Activation, BatchNormalization, Dropout

# FIX CRASH #
import matplotlib
matplotlib.use("TkAgg")
# --------- #
from matplotlib import pyplot as plt



def preProcessData():
	imdata = []
	labels = []

	# read image.png file and store in a np.array
	dataRootPath = os.path.join('..' ,'dataset01')
	dataDirs = os.listdir(dataRootPath)

	for subpath in os.listdir(dataRootPath):
		imagePathList = glob.glob(os.path.join(dataRootPath, subpath, '*.png'))
		for imagePath in imagePathList:
			tempImage = imageio.imread(imagePath, as_gray=True).reshape(50,50,1)
			imdata.append(tempImage)
			labels.append(int(subpath))

	datamean = np.mean(imdata, axis=0)
	imdata = np.array(imdata) - datamean
	labels = np.array(labels)

	# save data to a .npz file
	np.savez('data', imdata=imdata, labels=labels)

def loadData():
	if not os.path.exists('data.npz'):
		preProcessData()
	data = np.load('data.npz')
	return (data['imdata'], data['labels'])

class LossHistory(keras.callbacks.Callback):
	def on_train_begin(self, logs={}):
		self.losses = {'batch':[], 'epoch':[]}
		self.accuracy = {'batch':[], 'epoch':[]}
		self.val_loss = {'batch':[], 'epoch':[]}
		self.val_acc = {'batch':[], 'epoch':[]}

	def on_batch_end(self, batch, logs={}):
		self.losses['batch'].append(logs.get('loss'))
		self.accuracy['batch'].append(logs.get('acc'))
		self.val_loss['batch'].append(logs.get('val_loss'))
		self.val_acc['batch'].append(logs.get('val_acc'))

	def on_epoch_end(self, batch, logs={}):
		self.losses['epoch'].append(logs.get('loss'))
		self.accuracy['epoch'].append(logs.get('acc'))
		self.val_loss['epoch'].append(logs.get('val_loss'))
		self.val_acc['epoch'].append(logs.get('val_acc'))

	def loss_plot(self):
		loss_type = 'epoch'
		iters = range(len(self.losses[loss_type]))
		plt.figure()
		# acc
		plt.subplot(2,1,1)
		plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
		plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
		plt.xlabel('epoch')
		plt.ylabel('acc-rate')
		plt.grid(True)
		plt.legend(loc="upper right")

		# loss
		plt.subplot(2,1,2)
		plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
		plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
		plt.xlabel('epoch')
		plt.ylabel('loss')
		plt.grid(True)
		plt.legend(loc="upper right")

		plt.show()

data, labels = loadData()
x_train = data
y_train = labels
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train,test_size=0.2, random_state=10101)


model = Sequential()

model.add(Conv2D(10, (5, 5), strides=1, padding='valid', input_shape=(50,50,1)))
model.add(Activation('relu'))
model.add(Dropout(0.4))
model.add(MaxPool2D((2, 2)))
model.add(Activation('relu'))
# model.add(Conv2D(10, (3, 3), strides=1, padding='valid'))
# model.add(Activation('relu'))
# model.add(MaxPool2D((2, 2)))
# model.add(Activation('relu'))
model.add(Flatten())
model.add(Dense(8))
model.add(Activation('relu'))
model.add(Dense(output_dim=1 , activation='sigmoid'))

adam = keras.optimizers.Adam(lr=0.00001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
sgd = keras.optimizers.SGD(lr=0.00001, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='binary_crossentropy', optimizer=sgd, metrics=['accuracy'])

# datagen = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True)
# datagen.fit(x_train)

history = LossHistory()

model.fit(x_train, y_train, steps_per_epoch=10, epochs=40, validation_data=(x_val,y_val), validation_steps=10, callbacks=[history])

history.loss_plot()

# imageio.help('PNG')