import random 
import numpy as np 
import tensorflow 
import tensorflow.compat.v1 as tf
from .cfr_net import cfr_net
from causalforge.model import Model
from .utils import (
    convert_pd_to_np
)
           
tensorflow.compat.v1.disable_eager_execution()

class Params:
    
    def __init__(self,adict):
        for k in adict:
            setattr(self, k, adict[k])
NUM_ITERATIONS_PER_DECAY = 100

## ----------------------------------------------------------------------------
class CFR(Model):
    
    def build(self,user_params):
        ## ----------------------------------------------------------------------------            
        default_configs = {}
        default_configs['loss'] = 'l2' # """Which loss function to use (l1/l2/log)""")
        default_configs['n_in'] = 2   # """Number of representation layers. """)
        default_configs['n_out'] = 2  # """Number of regression layers. """)
        default_configs['p_alpha'] = 1e-4 #"""Imbalance regularization param. """)
        default_configs['p_lambda']= 0.0 #"""Weight decay regularization parameter. """)
        default_configs['rep_weight_decay'] = 1 #, """Whether to penalize representation layers with weight decay""")
        default_configs['dropout_in'] = 0.9 #, """Input layers dropout keep rate. """)
        default_configs['dropout_out'] = 0.9 #, """Output layers dropout keep rate. """)
        default_configs['nonlin'] = 'relu' #, """Kind of non-linearity. Default relu. """)
        default_configs['lrate'] = 0.05 #, """Learning rate. """)
        default_configs['decay'] = 0.5 #, """RMSProp decay. """)
        default_configs['batch_size'] = 100 #, """Batch size. """)
        default_configs['dim_in'] = 100 #, """Pre-representation layer dimensions. """)
        default_configs['dim_out'] = 100 #, """Post-representation layer dimensions. """)
        default_configs['batch_norm'] = 0 #, """Whether to use batch normalization. """)
        default_configs['normalization'] = 'none' #, """How to normalize representation (after batch norm). none/bn_fixed/divide/project """)
        default_configs['rbf_sigma'] = 0.1 #, """RBF MMD sigma """)
        default_configs['experiments'] = 1 #, """Number of experiments. """)
        default_configs['iterations'] = 2000 #, """Number of iterations. """)
        default_configs['weight_init'] = 0.01 #, """Weight initialization scale. """)
        default_configs['lrate_decay'] = 0.95 #, """Decay of learning rate every 100 iterations """)
        default_configs['wass_iterations'] = 20 #, """Number of iterations in Wasserstein computation. """)
        default_configs['wass_lambda'] = 1 #, """Wasserstein lambda. """)
        default_configs['wass_bpt'] = 0 #, """Backprop through T matrix? """)
        default_configs['varsel'] = 0 #, """Whether the first layer performs variable selection. """)
        default_configs['outdir'] = '../results/tfnet_topic/alpha_sweep_22_d100/' #, """Output directory. """)
        default_configs['datadir'] = '../data/topic/csv/' #, """Data directory. """)
        default_configs['dataform'] = 'topic_dmean_seed_%d.csv' #, """Training data filename form. """)
        default_configs['data_test'] = '' #, """Test data filename form. """)
        default_configs['sparse'] = 0 #, """Whether data is stored in sparse format (.x, .y). """)
        default_configs['seed'] = 1 #, """Seed. """)
        default_configs['repetitions'] = 1 #, """Repetitions with different seed.""")
        default_configs['use_p_correction'] = 1 #, """Whether to use population size p(t) in mmd/disc/wass.""")
        default_configs['optimizer'] = 'RMSProp' #, """Which optimizer to use. (RMSProp/Adagrad/GradientDescent/Adam)""")
        default_configs['imb_fun'] = 'mmd_lin' #, """Which imbalance penalty to use (mmd_lin/mmd_rbf/mmd2_lin/mmd2_rbf/lindisc/wass). """)
        default_configs['output_csv'] = 0 #,"""Whether to save a CSV file with the results""")
        default_configs['output_delay'] = 100 #, """Number of iterations between log/loss outputs. """)
        default_configs['pred_output_delay'] = -1 #, """Number of iterations between prediction outputs. (-1 gives no intermediate output). """)
        default_configs['debug'] = 0 #, """Debug mode. """)
        default_configs['save_rep'] =0 #, """Save representations after training. """)
        default_configs['val_part'] = 0 #, """Validation part. """)
        default_configs['split_output'] = 0 #, """Whether to split output layers between treated and control. """)
        default_configs['reweight_sample'] = 1 #, """Whether to reweight sample for prediction loss with average treatment probability. """)
        ## ----------------------------------------------------------------------------  
        
        params = default_configs.copy()
        for k in params:
            params[k] = user_params.get(k,params[k])
        self.params = params
        self.FLAGS = Params(self.params)
    
    def support_ite(self):
        return True 
    
    def predict_ite(self, X):
        X = convert_pd_to_np(X)
        pass 
    
    def predict_ate(self, X):
        return np.mean(self.predict_ite(X))
    
    
    def train_internal(CFR, sess, train_step, D, I_valid, D_test, logfile, i_exp):
        """ Trains a CFR model on supplied data """
    
        ''' Train/validation split '''
        n = D['x'].shape[0]
        I = range(n); I_train = list(set(I)-set(I_valid))
        n_train = len(I_train)
    
        ''' Compute treatment probability'''
        p_treated = np.mean(D['t'][I_train,:])
    
        ''' Set up loss feed_dicts'''
        dict_factual = {CFR.x: D['x'][I_train,:], CFR.t: D['t'][I_train,:], CFR.y_: D['yf'][I_train,:], \
          CFR.do_in: 1.0, CFR.do_out: 1.0, CFR.r_alpha: FLAGS.p_alpha, \
          CFR.r_lambda: FLAGS.p_lambda, CFR.p_t: p_treated}
    
        if FLAGS.val_part > 0:
            dict_valid = {CFR.x: D['x'][I_valid,:], CFR.t: D['t'][I_valid,:], CFR.y_: D['yf'][I_valid,:], \
              CFR.do_in: 1.0, CFR.do_out: 1.0, CFR.r_alpha: FLAGS.p_alpha, \
              CFR.r_lambda: FLAGS.p_lambda, CFR.p_t: p_treated}
    
        if D['HAVE_TRUTH']:
            dict_cfactual = {CFR.x: D['x'][I_train,:], CFR.t: 1-D['t'][I_train,:], CFR.y_: D['ycf'][I_train,:], \
              CFR.do_in: 1.0, CFR.do_out: 1.0}
    
        ''' Initialize TensorFlow variables '''
        sess.run(tf.global_variables_initializer())
    
        ''' Set up for storing predictions '''
        preds_train = []
        preds_test = []
    
        ''' Compute losses '''
        losses = []
        obj_loss, f_error, imb_err = sess.run([CFR.tot_loss, CFR.pred_loss, CFR.imb_dist],\
          feed_dict=dict_factual)
    
        cf_error = np.nan
        if D['HAVE_TRUTH']:
            cf_error = sess.run(CFR.pred_loss, feed_dict=dict_cfactual)
    
        valid_obj = np.nan; valid_imb = np.nan; valid_f_error = np.nan;
        if FLAGS.val_part > 0:
            valid_obj, valid_f_error, valid_imb = sess.run([CFR.tot_loss, CFR.pred_loss, CFR.imb_dist],\
              feed_dict=dict_valid)
    
        losses.append([obj_loss, f_error, cf_error, imb_err, valid_f_error, valid_imb, valid_obj])
    
        objnan = False
    
        reps = []
        reps_test = []
    
        ''' Train for multiple iterations '''
        for i in range(FLAGS.iterations):
    
            ''' Fetch sample '''
            I = random.sample(range(0, n_train), FLAGS.batch_size)
            x_batch = D['x'][I_train,:][I,:]
            t_batch = D['t'][I_train,:][I]
            y_batch = D['yf'][I_train,:][I]
    
            if __DEBUG__:
                M = sess.run(cfr.pop_dist(CFR.x, CFR.t), feed_dict={CFR.x: x_batch, CFR.t: t_batch})
                log(logfile, 'Median: %.4g, Mean: %.4f, Max: %.4f' % (np.median(M.tolist()), np.mean(M.tolist()), np.amax(M.tolist())))
    
            ''' Do one step of gradient descent '''
            if not objnan:
                sess.run(train_step, feed_dict={CFR.x: x_batch, CFR.t: t_batch, \
                    CFR.y_: y_batch, CFR.do_in: FLAGS.dropout_in, CFR.do_out: FLAGS.dropout_out, \
                    CFR.r_alpha: FLAGS.p_alpha, CFR.r_lambda: FLAGS.p_lambda, CFR.p_t: p_treated})
    
            ''' Project variable selection weights '''
            if FLAGS.varsel:
                wip = simplex_project(sess.run(CFR.weights_in[0]), 1)
                sess.run(CFR.projection, feed_dict={CFR.w_proj: wip})
    
            ''' Compute loss every N iterations '''
            if i % FLAGS.output_delay == 0 or i==FLAGS.iterations-1:
                obj_loss,f_error,imb_err = sess.run([CFR.tot_loss, CFR.pred_loss, CFR.imb_dist],
                    feed_dict=dict_factual)
    
                rep = sess.run(CFR.h_rep_norm, feed_dict={CFR.x: D['x'], CFR.do_in: 1.0})
                rep_norm = np.mean(np.sqrt(np.sum(np.square(rep), 1)))
    
                cf_error = np.nan
                if D['HAVE_TRUTH']:
                    cf_error = sess.run(CFR.pred_loss, feed_dict=dict_cfactual)
    
                valid_obj = np.nan; valid_imb = np.nan; valid_f_error = np.nan;
                if FLAGS.val_part > 0:
                    valid_obj, valid_f_error, valid_imb = sess.run([CFR.tot_loss, CFR.pred_loss, CFR.imb_dist], feed_dict=dict_valid)
    
                losses.append([obj_loss, f_error, cf_error, imb_err, valid_f_error, valid_imb, valid_obj])
                loss_str = str(i) + '\tObj: %.3f,\tF: %.3f,\tCf: %.3f,\tImb: %.2g,\tVal: %.3f,\tValImb: %.2g,\tValObj: %.2f' \
                            % (obj_loss, f_error, cf_error, imb_err, valid_f_error, valid_imb, valid_obj)
    
                if FLAGS.loss == 'log':
                    y_pred = sess.run(CFR.output, feed_dict={CFR.x: x_batch, \
                        CFR.t: t_batch, CFR.do_in: 1.0, CFR.do_out: 1.0})
                    y_pred = 1.0*(y_pred > 0.5)
                    acc = 100*(1 - np.mean(np.abs(y_batch - y_pred)))
                    loss_str += ',\tAcc: %.2f%%' % acc
    
                log(logfile, loss_str)
    
                if np.isnan(obj_loss):
                    log(logfile,'Experiment %d: Objective is NaN. Skipping.' % i_exp)
                    objnan = True
    
            ''' Compute predictions every M iterations '''
            if (FLAGS.pred_output_delay > 0 and i % FLAGS.pred_output_delay == 0) or i==FLAGS.iterations-1:
    
                y_pred_f = sess.run(CFR.output, feed_dict={CFR.x: D['x'], \
                    CFR.t: D['t'], CFR.do_in: 1.0, CFR.do_out: 1.0})
                y_pred_cf = sess.run(CFR.output, feed_dict={CFR.x: D['x'], \
                    CFR.t: 1-D['t'], CFR.do_in: 1.0, CFR.do_out: 1.0})
                preds_train.append(np.concatenate((y_pred_f, y_pred_cf),axis=1))
    
                if D_test is not None:
                    y_pred_f_test = sess.run(CFR.output, feed_dict={CFR.x: D_test['x'], \
                        CFR.t: D_test['t'], CFR.do_in: 1.0, CFR.do_out: 1.0})
                    y_pred_cf_test = sess.run(CFR.output, feed_dict={CFR.x: D_test['x'], \
                        CFR.t: 1-D_test['t'], CFR.do_in: 1.0, CFR.do_out: 1.0})
                    preds_test.append(np.concatenate((y_pred_f_test, y_pred_cf_test),axis=1))
    
                if FLAGS.save_rep and i_exp == 1:
                    reps_i = sess.run([CFR.h_rep], feed_dict={CFR.x: D['x'], \
                        CFR.do_in: 1.0, CFR.do_out: 0.0})
                    reps.append(reps_i)
    
                    if D_test is not None:
                        reps_test_i = sess.run([CFR.h_rep], feed_dict={CFR.x: D_test['x'], \
                            CFR.do_in: 1.0, CFR.do_out: 0.0})
                        reps_test.append(reps_test_i)
    
        return losses, preds_train, preds_test, reps, reps_test
    
    def fit(self, X, treatment, y):
        X, treatment, y = convert_pd_to_np(X, treatment, y)
        treatment = treatment.reshape(-1, 1)
        y = y.reshape(-1, 1)
        
        random.seed(self.FLAGS.seed)
        tensorflow.random.set_seed(self.FLAGS.seed)
        np.random.seed(self.FLAGS.seed)

        print('Training with hyperparameters: alpha=',self.FLAGS.p_alpha,
              ', lambda=', self.FLAGS.p_lambda )

        ''' Start Session '''
        sess = tf.Session()

        ''' Initialize input placeholders '''
        x  = tf.placeholder("float64", shape=[None,  X.shape[1]], name='x') # Features
        t  = tf.placeholder("float64", shape=[None, 1], name='t')   # Treatent
        y_ = tf.placeholder("float64", shape=[None, 1], name='y_')  # Outcome

        ''' Parameter placeholders '''
        r_alpha = tf.placeholder("float64", name='r_alpha')
        r_lambda = tf.placeholder("float64", name='r_lambda')
        do_in = tf.placeholder("float64", name='dropout_in')
        do_out = tf.placeholder("float64", name='dropout_out')
        p = tf.placeholder("float64", name='p_treated')

        ''' Define model graph '''
        dims = [X.shape[1], self.FLAGS.dim_in, self.FLAGS.dim_out]
        CFR = cfr_net(X, treatment, y, p, self.FLAGS, r_alpha, r_lambda, do_in, do_out, dims)
        
        
        
        
        
        
        ''' Set up optimizer '''
        global_step = tf.Variable(0, trainable=False)
        lr = tf.train.exponential_decay(self.FLAGS.lrate, global_step, 
                                        NUM_ITERATIONS_PER_DECAY, 
                                        self.FLAGS.lrate_decay, staircase=True)

        opt = None
        if self.FLAGS.optimizer == 'Adagrad':
            opt = tf.train.AdagradOptimizer(lr)
        elif self.FLAGS.optimizer == 'GradientDescent':
            opt = tf.train.GradientDescentOptimizer(lr)
        elif self.FLAGS.optimizer == 'Adam':
            opt = tf.train.AdamOptimizer(lr)
        else:
            opt = tf.train.RMSPropOptimizer(lr, self.FLAGS.decay)
    
        train_step = opt.minimize(CFR.tot_loss,global_step=global_step)
    
        ''' Set up for saving variables '''
        all_losses = []
        all_preds_train = []
        all_preds_test = []
        all_valid = []
        if self.FLAGS.varsel:
            all_weights = None
            all_beta = None
    
        all_preds_test = []

        ''' Handle repetitions '''
        n_experiments = self.FLAGS.experiments
        if self.FLAGS.repetitions>1:
            if self.FLAGS.experiments>1:
                raise Exception('ERROR: Use of both repetitions and multiple experiments is currently not supported.')
            n_experiments = self.FLAGS.repetitions

        ''' Run for all repeated experiments '''
        for i_exp in range(1,n_experiments+1):
    
            if self.FLAGS.repetitions>1:
                print('Training on repeated initialization ',i_exp,'/',self.FLAGS.repetitions,'...')
            else:
                print('Training on experiment ',i_exp,'/',self.FLAGS.repetitions,'...')
    
            ''' Load Data (if multiple repetitions, reuse first set)'''
    
            if i_exp==1 or self.FLAGS.experiments>1:
                D_exp_test = None
                if npz_input:
                    D_exp = {}
                    D_exp['x']  = D['x'][:,:,i_exp-1]
                    D_exp['t']  = D['t'][:,i_exp-1:i_exp]
                    D_exp['yf'] = D['yf'][:,i_exp-1:i_exp]
                    if D['HAVE_TRUTH']:
                        D_exp['ycf'] = D['ycf'][:,i_exp-1:i_exp]
                    else:
                        D_exp['ycf'] = None
    
                    if has_test:
                        D_exp_test = {}
                        D_exp_test['x']  = D_test['x'][:,:,i_exp-1]
                        D_exp_test['t']  = D_test['t'][:,i_exp-1:i_exp]
                        D_exp_test['yf'] = D_test['yf'][:,i_exp-1:i_exp]
                        if D_test['HAVE_TRUTH']:
                            D_exp_test['ycf'] = D_test['ycf'][:,i_exp-1:i_exp]
                        else:
                            D_exp_test['ycf'] = None
                else:
                    datapath = dataform % i_exp
                    D_exp = load_data(datapath)
                    if has_test:
                        datapath_test = dataform_test % i_exp
                        D_exp_test = load_data(datapath_test)
    
                D_exp['HAVE_TRUTH'] = D['HAVE_TRUTH']
                if has_test:
                    D_exp_test['HAVE_TRUTH'] = D_test['HAVE_TRUTH']
    
            ''' Split into training and validation sets '''
            I_train, I_valid = validation_split(D_exp, FLAGS.val_part)
    
            ''' Run training loop '''
            losses, preds_train, preds_test, reps, reps_test = \
                train(CFR, sess, train_step, D_exp, I_valid, \
                    D_exp_test, logfile, i_exp)
    
            ''' Collect all reps '''
            all_preds_train.append(preds_train)
            all_preds_test.append(preds_test)
            all_losses.append(losses)
    
            ''' Fix shape for output (n_units, dim, n_reps, n_outputs) '''
            out_preds_train = np.swapaxes(np.swapaxes(all_preds_train,1,3),0,2)
            if  has_test:
                out_preds_test = np.swapaxes(np.swapaxes(all_preds_test,1,3),0,2)
            out_losses = np.swapaxes(np.swapaxes(all_losses,0,2),0,1)