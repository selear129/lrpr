from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cPickle

import os
import numpy
import sys
import timeit

import theano
from theano import function as fn
import theano.tensor as T

from model import model
from pretrain_model import pretrain_conv_autoencoder, pretrain_local_autoencoders

# remove if needed
from conv_layer import conv_pool_layer

#def usage():
#print 'Usage: python train_model.py img_h img_w'
#sys.exit(1)

#if len(sys.argv) < 3:
#	usage()

img_h = 64#int(sys.argv[1])
img_w = 64 #int(sys.argv[2])

train_dir = os.listdir('tiny-imagenet-200/train')
valid_dir = os.listdir('tiny-imagenet-200/val')
test_dir = os.listdir('tiny-imagenet-200/test')

train_data = ()
print '\n'
for i in range(len(train_dir)):
	print '\033[Floaded train data:', i*100./len(train_dir), '%'
	im= os.listdir('tiny-imagenet-200/train/'+train_dir[i]+'/images')
	for j in range(len(im)):
		img = Image.open('tiny-imagenet-200/train/'+train_dir[i]+'/images/'+im[j]).convert('RGB')
		img = np.array(img, dtype='float32').transpose(2, 0, 1)/256.
		img = img.reshape(1, 3, 64, 64)
		train_data +=(img, )
train_data = np.concatenate(train_data)
print train_data.shape
train_set = theano.shared(np.asarray(train_data, dtype=theano.config.floatX), borrow=True)
n_train_images = train_data.shape[0]

valid_data = ()
print '\n'

im= os.listdir('tiny-imagenet-200/val/images')
for j in range(len(im)):
	print '\033[Floaded valid data:', j*100./len(im), '%'
	img = Image.open('tiny-imagenet-200/val/images/'+im[j]).convert('RGB')
	img = np.array(img, dtype='float32').transpose(2, 0, 1)/256.
	img = img.reshape(1, 3, 64, 64)
	valid_data +=(img, )
valid_data = np.concatenate(valid_data)
print valid_data.shape
valid_set = theano.shared(np.asarray(valid_data, dtype=theano.config.floatX), borrow=True)
n_valid_images = valid_data.shape[0]

test_data = ()
print '\n'

im= os.listdir('tiny-imagenet-200/test/images')
for j in range(len(im)):
	print '\033[Floaded test data:', j*100./len(im), '%'
	img = Image.open('tiny-imagenet-200/test/images/'+im[j]).convert('RGB')
	img = np.array(img, dtype='float32').transpose(2, 0, 1)/256.
	img = img.reshape(1, 3, 64, 64)
	test_data +=(img, )
test_data = np.concatenate(test_data)
print test_data.shape
test_set = theano.shared(np.asarray(test_data, dtype=theano.config.floatX), borrow=True)
n_test_images = test_data.shape[0]

'''
image_files = []
for f in os.listdir('../data/scaled-0.25'):
	if f=='.DS_Store':
		continue
	image_files.append('../data/scaled-0.25/'+f)
image_files.sort()
n_images = len(image_files)
n_train_images = int(.6*n_images)
n_valid_images = int(.2*n_images)
n_test_images = n_images -(n_train_images + n_valid_images)

train_set = ()
valid_set = ()
test_set = ()
for f in image_files[:n_train_images]:
	print 'train', f
	img = Image.open(f).convert('L')
	img = np.array(img, dtype='float64') / 256.
	img = img.reshape(1, 1, img_h, img_w)
	train_set+=(img, )
train_set = numpy.concatenate(train_set, axis=0)
train_set = theano.shared(np.asarray(train_set, dtype=theano.config.floatX), borrow=True)

for f in image_files[n_train_images:n_train_images+n_valid_images]:
	print 'valid',f
	img = Image.open(f).convert('L')
	img = np.array(img, dtype='float64') / 256.
	img = img.reshape(1, 1, img_h, img_w)
	valid_set+=(img, )
valid_set = numpy.concatenate(valid_set, axis=0)
valid_set = theano.shared(np.asarray(valid_set, dtype=theano.config.floatX), borrow=True)

for f in image_files[n_train_images+n_valid_images:]:
	print 'test', f
	img = Image.open(f).convert('L')
	img = np.array(img, dtype='float64') / 256.
	img = img.reshape(1, 1, img_h, img_w)
	test_set+=(img, )
test_set = numpy.concatenate(test_set, axis=0)
test_set = theano.shared(np.asarray(test_set, dtype=theano.config.floatX), borrow=True)
'''

rng = np.random.RandomState(23455)
dummy_wt = theano.shared(numpy.asarray(rng.uniform(low=-1., high=-1., size=(1, 1)), dtype=theano.config.floatX), borrow=True)
params = ([dummy_wt, ]*2, )*12

def dump_params(params, save_file):
	W, b = params
	save_file = open(save_file, 'wb')
	cPickle.dump(W.get_value(borrow=True), save_file, -1)
	cPickle.dump(b.get_value(borrow=True), save_file, -1)
	save_file.close()
	print 'params dumped in', save_file 

'''
def pretrain_nnet(data_set, n_train_images=100, batch_size=5, learning_rate=0.1):
	print '\n', '#'*50
	print 'starting Greedy Layerwise Unsupervised Pretraining ...'
	layer0 = data_set
	
	layer1, params_1 = pretrain_conv_autoencoder(1, layer0, (batch_size, 1, 96, 336), (2, 1, 3, 3), 5, (1, 1), learning_rate)
	dump_params(layer1.params, 'pretrainparams1.pkl')
	dump_params(params_1, 'pretrainparams_1.pkl')
	print '\n'

	layer2, params_2 = pretrain_conv_autoencoder(2, layer1.output, (batch_size, 2, 96, 336), (3, 2, 3, 3), 5, (2, 2), learning_rate)
	dump_params(layer2.params, 'pretrainparams2.pkl')
	dump_params(params_2, 'pretrainparams_2.pkl')
	print '\n'

	layer3, params_3 = pretrain_conv_autoencoder(3, layer2.output, (batch_size, 3, 48, 168), (5, 3, 3, 3), 5, (1, 1), learning_rate)
	dump_params(layer3.params, 'pretrainparams3.pkl')
	dump_params(params_3, 'pretrainparams_3.pkl')
	print '\n'

	layer4, params_4 = pretrain_conv_autoencoder(4, layer3.output, (batch_size, 5, 48, 168), (8, 5, 3, 3), 5, (2, 2), learning_rate)
	dump_params(layer4.params, 'pretrainparams4.pkl')
	dump_params(params_4, 'pretrainparams_4.pkl')
	print '\n'

	layer5, params_5 = pretrain_conv_autoencoder(5, layer4.output, (batch_size, 8, 24, 84), (5, 8, 3, 3), 5, (2, 2), learning_rate)
	dump_params(layer5.params, 'pretrainparams5.pkl')
	dump_params(params_5, 'pretrainparams_5.pkl')
	print '\n'
	
	n_pretrained_layers = 5
	n_test = train_set.shape.eval()[0]
	img_shapes = [(n_test, 1, 96, 336), (n_test, 2, 96, 336), (n_test, 3, 48, 168), (n_test, 5, 48, 168), (n_test, 8, 24, 84)]
	k_shapes = [(2, 1, 3, 3), (3, 2, 3, 3), (5, 3, 3, 3), (8, 5, 3, 3), (5, 8, 3, 3)]
	p_shapes = [(1, 1), (2, 2), (1, 1), (2, 2), (2, 2)]
	for i in range(n_pretrained_layers):
		load_file = open('pretrainparams'+str(i+1)+'.pkl')
		W = theano.shared(cPickle.load(load_file), borrow=True)
		b = theano.shared(cPickle.load(load_file), borrow=True)
		layer0 = conv_pool_layer(rng, layer0, k_shapes[i], img_shapes[i], poolsize=p_shapes[i], read_file=True, W_input=W, b_input=b)
		layer5 = layer0
		layer0 = layer0.output
		load_file.close()

	layer6_input = T.reshape(layer5.output, (layer5.output.shape.eval()[0], 5, 504))
	layer6, params_6 = pretrain_local_autoencoders(6, layer6_input, 5, 504, 40, 5, learning_rate)
	dump_params(layer6.params, 'pretrainparams6.pkl')
	dump_params(params_6, 'pretrainparams_6.pkl')
	print '\n'

	layerwise_params = []
	for i in range(6):
		load_file = open('pretrainparams'+str(i+1)+'.pkl')
		W = theano.shared(cPickle.load(load_file), borrow=True)
		b = theano.shared(cPickle.load(load_file), borrow=True)
		layerwise_params.append([W, b])
		load_file.close()

	for i in range(6, 0, -1):
		load_file = open('pretrainparams_'+str(i)+'.pkl')
		W = theano.shared(cPickle.load(load_file), borrow=True)
		b = theano.shared(cPickle.load(load_file), borrow=True)
		layerwise_params.append([W, b])
		load_file.close()

	return layerwise_params
	#return layer1.params, layer2.params, layer3.params, layer4.params, layer5.params, layer6.params, params_6, params_5, params_4, params_3, params_2, params_1
'''

def train_nnet(rng, data_set, n_examples, batch_size=5, learning_rate=0.1, init=False, params=None):
	print '#'*50
	print 'Starting global fine tuning ...'
	x = T.tensor4('x')
	index = T.lscalar()

	model_ = model(rng, x, (img_h, img_w), batch_size=batch_size, init=init, params=params)

	cost = T.mean(T.sqr(model_.layer12.output-x))
	params = model_.layer1.params + model_.layer2.params + model_.layer3.params + model_.layer4.params + model_.layer5.params + model_.layer6.params + model_.layer7.params + model_.layer8.params + model_.layer9.params + model_.layer10.params + model_.layer11.params + model_.layer12.params

	l2 = 0.
	
	for i in range(len(params)):
		p = params[i].get_value(borrow=True)
		l2 = l2 + 0.01*T.sum(T.sqr(p))
	cost = cost + l2

	grads = T.grad(cost, params)
	updates = [
		(param_i, param_i - learning_rate*grad_i)
		for param_i, grad_i in zip(params, grads)
	]

	train_fn = fn([index], cost, updates=updates, givens ={
		x:data_set[0][index*batch_size: (index+1)*batch_size]
	})

	valid_fn = fn([index], cost, givens={
		x:data_set[1][index*batch_size: (index+1)*batch_size]
	})

	test_fn = fn([index], cost, givens={
		x:data_set[2][index*batch_size: (index+1)*batch_size]
	})

	n_train_batches = n_examples[0]/batch_size
	n_valid_batches = n_examples[1]/batch_size
	n_test_batches = n_examples[2]/batch_size

	epoch = 0
	n_epochs = 2000
	done_looping = False
	patience = 10000
	patience_increase = 2
	improve_threshold = 0.995
	validation_freq = min(n_train_batches, patience/2)
	best_validation_err = np.inf
	best_iter = 0
	test_err = 0
	start_time =timeit.default_timer()

	while((epoch < n_epochs) and (not done_looping)):
		epoch+=1
		for mini_batch_index in xrange(n_train_batches):
			iter = (epoch-1)*n_train_batches+mini_batch_index
			if iter%100 ==0:
				print 'training @ iter = ', iter
			cost_ij = train_fn(mini_batch_index)

			if (iter+1)%validation_freq==0:
				validation_losses=[valid_fn(i) for i in xrange(n_valid_batches)]
				this_validation_loss = np.mean(validation_losses)
				print ('epoch %i, minibatch %i/%i, mean validation reconstruction error: %f ' %(epoch, mini_batch_index+1, n_train_batches, this_validation_loss))

		if this_validation_loss<best_validation_err:
			if this_validation_loss<best_validation_err*improve_threshold:
				patience=max(patience, iter*patience_increase)

			best_validation_err=this_validation_loss
			best_iter=iter

			test_losses=[
				test_fn(i)
				for i in xrange(n_test_batches)
			]
			test_err=np.mean(test_losses)
			print '\tepoch %i, minibatch %i/%i, mean test reconstruction error: %f' %(epoch, mini_batch_index+1, n_train_batches, test_err)
			
			save_file = open('trained_params.pkl', 'wb')
			for i in range(len(params)):
				cPickle.dump(params[i].get_value(borrow=True), save_file, -1)
			save_file.close()
			print 'saved trained params @', save_file

		if patience<=iter:
			done_looping=True
			break

	# remove the following block made for visualisation
	# inp = T.tensor4()
	# train_ = model(rng, inp, (img_h, img_w), batch_size=batch_size, params=params)
	# f = fn([inp], train_.layer12.output)
	# f_img = f(data_set[0].eval())
	# plt.gray()
	# for i in range(1, 2):
	#	plt.subplot(1, 1, i); plt.axis('off'); plt.imshow(f_img[0, i-1, :, :])
	# plt.show()
	# block ends here
#params = pretrain_nnet(train_set, n_train_images)
train_nnet(rng, (train_set, valid_set, test_set), (n_train_images, n_valid_images, n_test_images), init=False, params=params)
