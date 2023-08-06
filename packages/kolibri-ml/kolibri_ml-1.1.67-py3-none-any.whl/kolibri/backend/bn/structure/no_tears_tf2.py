import tensorflow as tf
import numpy as np


class NoTearTF():

    def __init__(self, lamb=0.05, alpha_init=0.00, rho_init=1.0):
        self.alpha = alpha_init
        self.rho = rho_init
        self.lamb = lamb
        self.optimizer = tf.keras.optimizers.Adam(beta_1=0.9)

    def model_train(self, X, outer_iter=50, inner_iter=100, init_global_step=1e-2, h_tol=1e-8, eval_fun=None):

        h, h_new = np.inf, np.inf

        for _ in range(outer_iter):
            for t1 in range(inner_iter):
                self.opt_step = init_global_step / np.sqrt(1. + t1)
                self.train_step(X)

            h_ = self.loss_penalty(X, self.W)

            if h <= h_tol:
                break
            self.alpha += self.rho * h_
            self.rho *= 1.25
        return

    @tf.function
    def train_step(self, X):
        with tf.GradientTape() as tape:
            loss = self.compute_loss(X, self.W)
        grads = tape.gradient(loss, [self.W])
        self.optimizer.apply_gradients(zip(grads, [self.W]))

    def compute_loss(self, X, W):
        n, d = X.shape
        W = tf.linalg.set_diag(W, tf.zeros(d))
        d_xw = X - tf.matmul(X, W)
        loss_penalty = tf.linalg.trace(tf.linalg.expm(W ** 2)) - float(d)
        loss_xw = tf.reduce_sum(d_xw ** 2) / (float(n) * 2.0)
        loss_obj = loss_xw + (self.rho / 2.0) * (loss_penalty ** 2) + self.alpha * loss_penalty
        loss_obj = loss_obj + self.lamb * tf.reduce_sum(tf.abs(W))

        return loss_obj

    def loss_penalty(self, X, W):
        d = W.shape[0]
        W = tf.linalg.set_diag(W, tf.zeros(d))
        loss_penalty = tf.linalg.trace(tf.linalg.expm(W ** 2)) - float(d)
        return loss_penalty

    def construct_graph(self, X):
        ## X: nxd numpy array
        n, d = X.shape
        self.W = tf.Variable(tf.random.normal((d, d), dtype=tf.float32), trainable=True)
        return self.W
