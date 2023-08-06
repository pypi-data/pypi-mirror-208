import os, sys
import numpy as np
from scipy.linalg import solve, det
import datetime as dt

from delta_converter import delta_converter

from biwcm_main import biwcm_main

import warnings
warnings.filterwarnings("ignore")

class biwcm_c(biwcm_main):
    
    def __init__(self, s_i, sigma_alpha, ic='random', tol=10**-8, max_iter=500, monitor=True, method='fixed-point', verbose=True):
        
        super().__init__(s_i, sigma_alpha, ic, tol, max_iter, monitor, method, verbose)
    
    def w_i_alpha(self, i, alpha):
        return 1/(self.x[i]+self.x[alpha+self.n_rows])
    
    def var_w_i_alpha(self, i, alpha):
        return self.w_i_alpha(i, alpha)**2
    
    # fixed-point        
     
    def fixed_point_fun(self):
        return self.e_strength/self.strength
        
    def fixed_point_x_update(self):
        self.x*=self.delta
            
    def fixed_point_jac(self):
        _jac=np.zeros((self.n_rows+self.n_cols, self.n_rows+self.n_cols))
        for i in range(self.n_rows):
            for a in range(self.n_cols):
                var_w_ia=self.var_w_i_alpha(i,a)
                # off-diagonal terms
                _jac[i,a+self.n_rows]=-self.x[i]/self.strength[i]*var_w_ia
                _jac[a+self.n_rows, i]=-self.x[a+self.n_rows]/self.strength[a+self.n_rows]*var_w_ia
                # terms on the diagonal
                _jac[i, i]+=-self.x[a+self.n_rows]/self.strength[i]*var_w_ia
                _jac[a+self.n_rows, a+self.n_rows]+=-self.x[i]/self.strength[a+self.n_rows]*var_w_ia
        return _jac
        
        
    # Newton
            
    def newton_fun(self):
        return -self.strength+self.e_strength
    
    # written in terms of the variance of w_i_alpha
    # the Newton's jacobian is the same for both the continuous and the discrete case