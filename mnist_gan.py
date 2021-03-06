#encoding=utf-8
#time=18-11-9 上午11:53
__author__ = 'Ethan'
import time
import cv2
import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import gridspec
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets('./MNIST_data',one_hot=True)

#从正太分布输出随机值
def xavier_init(size):
    in_dim = size[0]
    xavier_stddev = 1./tf.sqrt(in_dim/2.)
    return  tf.random_normal(shape=size,stddev=xavier_stddev)

#生成模型的输入和参数初始化
#随机噪声
Z = tf.placeholder(tf.float32,shape=[None,100])
#权值
G_W1 = tf.Variable(xavier_init([100,128]))
#偏移量biaes
G_b1 = tf.Variable(tf.zeros(shape=[128]))
G_W2 = tf.Variable(xavier_init([128,784]))
G_b2 = tf.Variable(tf.zeros(shape=[784]))
theta_G = [G_W1,G_W2,G_b1,G_b2]

#判别模型的输入和参数初始化
#input data
X = tf.placeholder(tf.float32,shape=[None,784])
D_W1 = tf.Variable(xavier_init([784,128]))
D_b1 = tf.Variable(tf.zeros(shape=[128]))
D_W2 = tf.Variable(xavier_init([128,1]))
D_b2 = tf.Variable(tf.zeros(shape=[1]))
theta_D = [D_W1,D_W2,D_b1,D_b2]

#生成模型
def generator(z):
    G_h1 = tf.nn.relu(tf.matmul(z,G_W1)+G_b1)
    G_log_prob = tf.matmul(G_h1,G_W2)+G_b2
    G_prob = tf.nn.sigmoid(G_log_prob)
    return G_prob

#判别模型
def discriminator(x):
    D_h1 = tf.nn.relu(tf.matmul(x,D_W1)+D_b1)
    D_logit = tf.matmul(D_h1,D_W2)+D_b2
    D_prob = tf.nn.sigmoid(D_logit)

    return D_prob,D_logit

#随机噪声
def sample_Z(m,n):
    return  np.random.uniform(-1.,1.,size=[m,n])

# def sigmoid_cross_entropy_with_logits(_sentinel=None,labels=None,logits=None,name=None):
#     pass

def plot(samples):
    fig = plt.figure(figsize=(4,4))
    gs = gridspec.GridSpec(4,4)
    gs.update(wspace=0.05,hspace=0.05)

    for i,sample in enumerate(samples):
        # print('single sample type and shape:  ',type(sample),sample.shape)
        # sample = np.reshape(sample,(28,28))
        # cv2.imwrite('./output/'+str(i).zfill(6)+'_'+str(time)+'.png',sample)
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample.reshape(28,28),cmap='Greys_r')
    return fig

#feed data
G_sample = generator(Z)
D_real,D_logit_real = discriminator(X)
D_fake,D_logit_fake = discriminator(G_sample)

D_loss_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_real, labels=tf.ones_like(D_logit_real)))
D_loss_fake = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_fake, labels=tf.zeros_like(D_logit_fake)))
D_loss = D_loss_real+D_loss_fake

G_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_fake,labels=tf.ones_like(D_logit_fake)))

D_solver = tf.train.AdamOptimizer().minimize(D_loss,var_list=theta_D)
G_solver = tf.train.AdamOptimizer().minimize(G_loss,var_list=theta_G)

mb_size = 128
Z_dim = 100
sess = tf.Session()
sess.run(tf.global_variables_initializer())

if not os.path.exists('./output/'):
    os.makedirs('./output/')
i=0
for it in range(100000):
    if it %1000==0:
        samples = sess.run(G_sample,feed_dict={Z:sample_Z(16,Z_dim)})
        # print(type(samples),samples.shape)
        fig = plot(samples)
        plt.savefig('./output/{}.png'.format(str(i).zfill(3)),bbox_inches='tight')
        i+=1
        plt.close(fig)
    X_mb,_ = mnist.train.next_batch(mb_size)

    _,D_loss_curr = sess.run([D_solver, D_loss], feed_dict={X:X_mb,Z:sample_Z(mb_size,Z_dim)})
    _,G_loss_curr = sess.run([G_solver, G_loss], feed_dict={Z: sample_Z(mb_size, Z_dim)})
    # print(a,'adfasdfasdf',b)#均为None
    if it % 1000==0:
        print('iter:{}'.format(it))
        print('D loss:{!s:4}'.format(D_loss_curr))
        # print(type(D_loss_curr),D_loss_curr.shape)
        print('G loss:{!s:4}'.format(G_loss_curr))



