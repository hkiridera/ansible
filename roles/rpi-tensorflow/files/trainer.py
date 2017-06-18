#!/usr/bin/env python
#-*- encoding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
 
from __future__ import print_function
 
import tensorflow as tf
import sys
import time
 
from tensorflow.examples.tutorials.mnist import input_data
 
# Flags for defining the tf.train.ClusterSpec
tf.app.flags.DEFINE_string("ps_hosts", "",
                           "Comma-separated list of hostname:port pairs")
tf.app.flags.DEFINE_string("worker_hosts", "",
                           "Comma-separated list of hostname:port pairs")
 
# Flags for defining the tf.train.Server
tf.app.flags.DEFINE_string("job_name", "", "One of 'ps', 'worker'")
tf.app.flags.DEFINE_integer("task_index", 0, "Index of task within the job")
 
FLAGS = tf.app.flags.FLAGS
 
# config
batch_size = 100
learning_rate = 0.001
training_epochs = 10
# ホスト間で共有可能なディレクトリを指定します。
board_path = "/var/data/shared/board"
 
def main(_):
 
    ps_hosts = FLAGS.ps_hosts.split(",")
    worker_hosts = FLAGS.worker_hosts.split(",")
    worker_num = len(worker_hosts)
 
    # cluster を作成します。
    cluster = tf.train.ClusterSpec({"ps": ps_hosts, "worker": worker_hosts})
 
    # ローカル・タスクを実行するサーバを開始します。
    server = tf.train.Server(cluster,
                             job_name=FLAGS.job_name,
                             task_index=FLAGS.task_index)
 
    mnist    = input_data.read_data_sets("MNIST_data/", one_hot=True)
    is_chief = (FLAGS.task_index == 0)
 
    if FLAGS.job_name == "ps":
        server.join()
    elif FLAGS.job_name == "worker":
 
        # Between-graph replication
        with tf.device(tf.train.replica_device_setter(
             worker_device="/job:worker/task:%d" % FLAGS.task_index,
             cluster=cluster)):
 
            # 更新数のカウンター
            global_step = tf.get_variable('global_step', [],
                                          initializer = tf.constant_initializer(0),
                                          trainable = False)
 
 
            with tf.name_scope('input'):
                x = tf.placeholder(tf.float32, shape=[None, 784], name="x-input")  # mnist data image of shape 28*28=784
                y_ = tf.placeholder(tf.float32, shape=[None, 10], name="y-input")  # 0?9 10 classes
 
            with tf.name_scope("weights"):
                W = tf.Variable(tf.zeros([784, 10]))
 
            with tf.name_scope("biases"):
                b = tf.Variable(tf.zeros([10]))
 
            with tf.name_scope("softmax"):
                y = tf.nn.softmax(tf.matmul(x, W) + b)
 
            with tf.name_scope('cross_entropy'):
                #cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
                cross_entropy = -tf.reduce_sum(y_*tf.log(y))
 
            # optimizer
            with tf.name_scope('train'):
                grad_op = tf.train.GradientDescentOptimizer(learning_rate)
                # SyncReplicasOptimizerを使うと、同期的に勾配を集約してオプティマイザに渡すことができます。
                rep_op = tf.train.SyncReplicasOptimizer(grad_op,
                                                    replicas_to_aggregate=worker_num,
                                                    replica_id=FLAGS.task_index,
                                                    total_num_replicas=worker_num,
                                                    use_locking=True)
                train_op = rep_op.minimize(cross_entropy, global_step=global_step)
                #train_op = grad_op.minimize(cross_entropy, global_step=global_step)
 
            init_token_op      = rep_op.get_init_tokens_op()
            chief_queue_runner = rep_op.get_chief_queue_runner()
 
            with tf.name_scope('Accuracy'):
                # accuracy
                correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
                accuracy           = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
 
            tf.scalar_summary("cost", cross_entropy)
            tf.scalar_summary("accuracy", accuracy)
 
            #saver = tf.train.Saver()
            summary_op = tf.merge_all_summaries()
            init_op = tf.initialize_all_variables()
            print("Variables initialized ...")
 
        sv = tf.train.Supervisor(is_chief=(FLAGS.task_index == 0),
                                 global_step=global_step,
                                 init_op=init_op)
 
        begin_time = time.time()
        frequency = 100
        with sv.prepare_or_wait_for_session(server.target, config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)) as sess:
            # is chief
            if is_chief:
                sv.start_queue_runners(sess, [chief_queue_runner])
                sess.run(init_token_op)
 
            writer = tf.train.SummaryWriter(board_path, graph=tf.get_default_graph())
 
            start_time = time.time()
            for epoch in range(training_epochs):
 
                batch_count = int(mnist.train.num_examples/batch_size)
 
                count = 0
                for i in range(batch_count):
                    batch_x, batch_y = mnist.train.next_batch(batch_size)
 
                    if i % worker_num == FLAGS.task_index:
                        continue
 
                    _, cost, summary, step = sess.run(
                             [train_op, cross_entropy, summary_op, global_step],
                             feed_dict={x: batch_x, y_: batch_y})
                    writer.add_summary(summary, step)
 
                    count += 1
                    if count % frequency == 0 or i+1 == batch_count:
                        elapsed_time = time.time() - start_time
                        start_time   = time.time()
                        print("Step: %d,"           % (step+1),
                              " Epoch: %2d,"        % (epoch+1),
                              " Batch: %3d of %3d," % (i+1, batch_count),
                              " Cost: %.4f,"        % cost,
                              " AvgTime: %3.2fms"   % float(elapsed_time*1000/frequency))
                        count = 0
 
            print("Test-Accuracy: %2.2f" % sess.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}))
            print("Total Time: %3.2fs"   % float(time.time() - begin_time))
            print("Final Cost: %.4f"     % cost)
 
        #sv.stop()
        if is_chief:
            sv.request_stop()
        else:
            sv.stop()
        print("done")
 
if __name__ == "__main__":
    tf.app.run()
