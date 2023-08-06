import os, sys
import numpy as np
from scipy.linalg import solve, det
import datetime as dt

from delta_converter import delta_converter

class biwcm_main:
    
    def __init__(self, s_i, sigma_alpha, ic='random', tol=10**-8, max_iter=500, monitor=True, method='fixed-point', verbose=True):
        self.n_rows=len(s_i)
        self.n_cols=len(sigma_alpha)
        self.strength=np.concatenate((s_i, sigma_alpha))

        self.tol=tol
        self.max_iter=max_iter

        self.monitor=monitor
        self.method=method
        self.verbose=verbose
        
        # get initial conditions
        if type(ic)==str:
            # flat
            if ic=='flat':
                self.x=np.ones(self.n_rows+self.n_cols)
            # still flat
            elif ic=='galaxy':
                self.x=42*np.ones(self.n_rows+self.n_cols)
            # random
            elif ic=='random':
                self.x=np.random.random(size=self.n_rows+self.n_cols)
                # positive, but distributed over a longer interval
                self.x=-np.log(self.x)
            elif ic=='zero':
                self.x=tol*np.ones(self.n_rows+self.n_cols)
            elif ic=='cla' or ic=='rca':
                self.w=np.sum(s_i)
                self.x=-np.log(self.strength/np.sqrt(self.w))
            else:
                print('the IC has not been implemented yet, turning to random IC')
                self.x=np.random.random(size=self.n_rows+self.n_cols)
                # positive, but distributed over a longer interval
                self.x=-np.log(self.x)
        elif type(ic)==np.ndarray:
            self.x=ic
        
        # saving the initial condition for further analysis
        self.ic=self.x.copy()
        
        # calculate how far I am from results from the very beginning
        self.get_e_strength()
        self.max_err()
        
        if self.monitor:
            # taking trace of what happened step by step
            self.monitor_d={}
            self.monitor_d['x']=[self.x.copy()]
            self.monitor_d['mrse']=[self.mrse]
            self.monitor_d['mase']=[self.mase]
            self.monitor_d['s_n']=[self.e_strength.copy()]
            
            if self.method=='fixed-point':
                _jac=self.fixed_point_jac()
            elif self.method=='newton':
                _jac=self.newton_jac()
            det_j=det(_jac)
            self.monitor_d['det_J']=[det_j]
        
        self.counter=0
        
    def get_theta_eta(self):
        self.start=dt.datetime.now()
        if self.method=='fixed-point':
            self.get_theta_eta_fixed_point()
        elif self.method=='newton':
            self.get_theta_eta_newton()
        else:
            print('method not implemented (yet?). Proceeding with Newton...')
            self.get_theta_eta_newton()
            
        self.has_converged()
            
    # fixed-point        
            
    def get_theta_eta_fixed_point(self):  
        if self.verbose:
            print('{:} MRSE={:.4e} MASE={:.4e}'.format(self.counter, self.mrse, self.mase), end='\r')
        while self.mrse>self.tol and self.max_iter>self.counter:
            self.counter+=1
            self.fixed_point_iter()
            if self.verbose:
                print('{:} MRSE={:.4e} MASE={:.4e}'.format(self.counter, self.mrse, self.mase), end='\r')
        
        
    def fixed_point_iter(self):
        self.delta=self.fixed_point_fun()
        #alpha=self.anderson_alpha(1)
        #self.x+=alpha*self.delta
        self.fixed_point_x_update()
        # check the result
        self.get_e_strength()
        self.max_err()
        if self.monitor:
            self.monitor_d['x'].append(self.x.copy())
            self.monitor_d['mrse'].append(self.mrse)
            self.monitor_d['mase'].append(self.mase)
            self.monitor_d['s_n'].append(self.e_strength.copy())
            _jac=self.fixed_point_jac()
            det_j=det(_jac)
            self.monitor_d['det_J'].append(det_j)

    # Newton
    
    def get_theta_eta_newton(self):  
        if self.verbose:
            print('{:} MRSE={:.4e} MASE={:.4e}'.format(self.counter, self.mrse, self.mase), end='\r')
        while self.mrse>self.tol and self.max_iter>self.counter:
            self.counter+=1
            self.newton_iter()
            if self.verbose:
                print('{:} MRSE={:.4e} MASE={:.4e}'.format(self.counter, self.mrse, self.mase), end='\r')
                
    def newton_iter(self):
        self._matrix=self.newton_jac()
        self._f=self.newton_fun()
        self.delta=solve(self._matrix, self._f, assume_a='sym')
        self.x+=self.delta
        # check the result
        self.get_e_strength()
        self.max_err()
        if self.monitor:
            self.monitor_d['x'].append(self.x.copy())
            self.monitor_d['mrse'].append(self.mrse)
            self.monitor_d['mase'].append(self.mase)
            self.monitor_d['s_n'].append(self.e_strength.copy())
            _jac=self.newton_jac()
            det_j=det(_jac)
            self.monitor_d['det_J'].append(det_j)
        
    # written in terms of the variance of w_i_alpha
    # the Newton's jacobian, it is the same for both the continuous and the discrete case
    

    
    def newton_jac(self):
        # actually it is -J, i.e. the quantity that enters in the Newton step
        _jac=np.zeros((self.n_rows+self.n_cols, self.n_rows+self.n_cols))
        for i in range(self.n_rows):
            for a in range(self.n_cols):
                var_w_ia=self.var_w_i_alpha(i,a)
                # off-diagonal terms
                _jac[i,a+self.n_rows]=var_w_ia
                _jac[a+self.n_rows, i]=var_w_ia
                # terms on the diagonal
                _jac[i, i]+=var_w_ia
                _jac[a+self.n_rows, a+self.n_rows]+=var_w_ia
        return _jac
               
        
        
    # auxiliary functions
    
    def max_err(self):
        self.mrse=np.abs(self.strength-self.e_strength)/self.strength
        self.mrse=np.max(self.mrse)
    
        self.mase=np.abs(self.strength-self.e_strength)
        self.mase=np.max(self.mase)
        
    def has_converged(self):
        if self.mrse<=self.tol:
            self.converged=True
        else:
            self.converged=False
        
        if self.verbose:
            if self.converged:
                final_result=' converged '
            else:
                final_result=' did not converge '
            
            delta=dt.datetime.now()-self.start
            
            sentence='Algorithm'+final_result+'after {:} steps in {:}. MRSE={:.4e} MASE={:.4e}'.format(self.counter, delta_converter(delta), self.mrse, self.mase)
            print(sentence)
    
    
    # written in terms of the expected value of w_i_alpha get_e_strength, it is the same for both the continuous and the discrete case
    
    def get_e_strength(self):
        self.e_strength=np.zeros(self.n_rows+self.n_cols)
        for i in range(self.n_rows):
            for a in range(self.n_cols):
                wia=self.w_i_alpha(i,a)
                self.e_strength[i]+=wia
                self.e_strength[a+self.n_rows]+=wia    
                
                
