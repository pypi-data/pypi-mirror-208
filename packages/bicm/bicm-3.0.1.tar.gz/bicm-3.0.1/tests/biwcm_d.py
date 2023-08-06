import os, sys
import numpy as np
from scipy.linalg import solve, det
import datetime as dt

from delta_converter import delta_converter

from biwcm_main import biwcm_main

class biwcm_d(biwcm_main):
    
    def __init__(self, s_i, sigma_alpha, ic='random', tol=10**-8, max_iter=500, monitor=True, method='fixed-point', verbose=True):
        
        super().__init__(s_i, sigma_alpha, ic, tol, max_iter, monitor, method, verbose)
    
    def w_i_alpha(self, i, alpha):
        num=np.exp(-(self.x[i]+self.x[alpha+self.n_rows]))
        return num/(1-num)
    
    def var_w_i_alpha(self, i, alpha):
        num=np.exp(-(self.x[i]+self.x[alpha+self.n_rows]))
        return num/(1-num)**2
    
    # fixed-point        
    def fixed_point_fun(self):
        return np.log(self.e_strength/self.strength)
    
    def fixed_point_x_update(self):
        self.x+=self.delta
    
    def anderson_alpha(self, alpha):
        delta=self.x+self.delta
        min_delta=np.min(delta)
        # actually, the limitation is stricter than necessary
        if min_delta<=0:
            w_min=np.where(delta==min_delta)[0]
            exp_alpha=np.ceil(-np.log10(np.abs(self.x[w_min]/min_delta)))[0]
            if self.verbose:
                print('\nAnderson! alpha=10^{:d}\n'.format(-exp_alpha))
            return 10**-exp_alpha
        return 1
            
        
            
    def fixed_point_jac(self):
        _jac_diag=np.ones(self.n_rows+self.n_cols)
        # the ones on the diagonal
        _jac=np.diag(_jac_diag)
        for i in range(self.n_rows):
            for a in range(self.n_cols):
                var_w_ia=self.var_w_i_alpha(i, a)
                # off-diagonal terms
                _jac[i,a+self.n_rows]=-var_w_ia/self.e_strength[i]
                _jac[a+self.n_rows, i]=-var_w_ia/self.e_strength[a+self.n_rows]
                # terms on the diagonal
                _jac[i, i]+=-var_w_ia/self.e_strength[i]
                _jac[a+self.n_rows, a+self.n_rows]+=-var_w_ia/self.e_strength[a+self.n_rows]
        return _jac
        
        
    # Newton
    
    def newton_fun(self):
        return -self.strength+self.e_strength
        #return -np.log(self.strength)+np.log(self.e_strength)
    
    # written in terms of the variance of w_i_alpha
    # the Newton's jacobian is the same for both the continuous and the discrete case         
    