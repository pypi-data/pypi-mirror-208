# coding: utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.special import erf, erfcinv

# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# SUPY_SIGNSYS.PY    - TOOLBOX FOR SIGNAL AND SYSTEMS
# ----------------------------------------------------
# Version 16/04/2023, Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany
# EXPERIMENTAL SOFTWARE: NO WARRANTIES! REGULARLY BACKUP YOUR DATA!
# former name: signal.py  (renamed on 14/5/2023) 
#
# CONTENTS:
# -------------------------
# Part I) Linear Algebra and Optimization Operations
#  - def inv3(A,eps=1e-12)
#  - def inv3_arr(A)
#  - def inv3sym(A,eps=1e-12)
#  - def inv3sym_arr(A)
#  - def mult3sym_arr(A,v)
#  
# Part I) Signal Detection with Truncated Gaussians
#  - def getDerivatives4TruncatedGaussiansError(mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu=1.0,lmbda_sig2=1.0,lmbda_N=1.0, flagOnlyE=1)
#  - def getDerivatives4TruncatedGaussiansError_arr(mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu=1.0,lmbda_sig2=1.0,lmbda_N=1.0, flagOnlyE=1)
#  - def estimateGaussParametersFromTruncatedGaussians(mu_est, sig2_est, N_est, a, b, mu__bar, sig2__bar, N__bar, lmbda_mu=1.0, lmbda_sig2=1.0, lmbda_N=1.0, tau_max=50,
#                                                      mumin=None,mumax=None, sig2min=None,sig2max=None, Nmin=None,Nmax=None,
#                                                      epsNablaE=1e-8,E_ok=3,tau_ok=3)
#  - def getModeOfDensity(x,binsize=10,p_cutoff=0,x_sorted=None)
#  - def detectSignalFromTruncatedGaussians(x,
#                                           fac_p_decision=1.0,
#                                           nEstimates = 10, sigEstimates = 10.0, 
#                                           tau_max=100, epsNablaE=1e-8, E_ok=3, tau_ok=3,
#                                           list_ptrunc_a=[0.0001,0.0001,0.0001,0.0001,0.0001,0.0001, 0.0001],
#                                           list_ptrunc_b=[0.05  ,0.1   ,0.2   ,0.3   ,0.4   ,0.5   , 0.6   ],
#                                           lmbda_mu=1/3, lmbda_sig2=1/3, lmbda_N=1/3,
#                                           p_binsize=0.01,max_binsize=200,
#                                           p_cutoff_mode=0.2)
#
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************


# ***************************************************************************************
# ***************************************************************************************
# Part I) Linear Algebra and Optimization Operations 
# ***************************************************************************************
# ***************************************************************************************

def inv3(A,eps=1e-12): 
    """
    invert 3x3 matrix using the explicit inversion formula (e.g., see Mathe1, Satz 8.26, pp205)
    :param A: 3x3 matrix to be inverted
    :param eps: if |det(A)|<eps then return -1 to indicate that matrix A is (nearly) singular
    :returns: either -1 (if singular) or inverse of matrix A
    """
    assert A.shape==(3,3),"supy.signal.inv3(A): A must be 3x3 matrix, but A="+str(A) 
    a,b,c,d,e,f,g,h,i=A[0,0],A[0,1],A[0,2],A[1,0],A[1,1],A[1,2],A[2,0],A[2,1],A[2,2]   # get components of matrix
    detA=a*e*i+b*f*g+c*d*h-g*e*c-h*f*a-i*d*b   # determinant of A
    if abs(detA)<eps: return -1
    Am1=np.array([[e*i-f*h, c*h-b*i, b*f-c*e],\
                  [f*g-d*i, a*i-c*g, c*d-a*f],\
                  [d*h-e*g, b*g-a*h, a*e-b*d]],dtype=A.dtype)
    return Am1/detA

def inv3_arr(A):
    """
    invert array of 3x3 matrices using the explicit inversion formula (e.g., see Mathe1, Satz 8.26, pp205)
    :param A: 3x3xN matrixes to be inverted (that is, A[:,:,n] is the n-th matrix to be inverted
    :returns Am1,detA: inverse Matrix and corresponding determinant (to identify singular components) 
    """
    a,b,c,d,e,f,g,h,i=A[0,0],A[0,1],A[0,2],A[1,0],A[1,1],A[1,2],A[2,0],A[2,1],A[2,2]   # get components of matrix
    detA=np.multiply(a,np.multiply(e,i))+np.multiply(b,np.multiply(f,g))+np.multiply(c,np.multiply(d,h))-np.multiply(g,np.multiply(e,c))-np.multiply(h,np.multiply(f,a))-np.multiply(i,np.multiply(d,b))
    Am1=np.zeros(A.shape)
    Am1[0,0]=np.multiply(e,i)-np.multiply(f,h)
    Am1[0,1]=np.multiply(c,h)-np.multiply(b,i)
    Am1[0,2]=np.multiply(b,f)-np.multiply(c,e)
    Am1[1,0]=np.multiply(f,g)-np.multiply(d,i)
    Am1[1,1]=np.multiply(a,i)-np.multiply(c,g)
    Am1[1,2]=np.multiply(c,d)-np.multiply(a,f)
    Am1[2,0]=np.multiply(d,h)-np.multiply(e,g)
    Am1[2,1]=np.multiply(b,g)-np.multiply(a,h)
    Am1[2,2]=np.multiply(a,e)-np.multiply(b,d)
    return np.divide(Am1,detA),detA


def inv3sym(A,eps=1e-12): 
    """
    invert symmetric 3x3 matrix using the explicit inversion formula (see AB5/pp6; cf. Mathe1, Satz 8.26, pp205) 
    :param A: 3x3 matrix to be inverted; either represented as 1D array of length 6  containing the upper triangle a=A11, e=A22, i=A33, b=A12, c=A13, f=A23, or conventionally, as 2D array of size 3x3 
    :param eps: if |det(A)|<eps then return -1 to indicate that matrix A is (nearly) singular
    :returns: either -1 (if singular) or inverse of matrix A (in same format as A)
    """
    if A.shape==(6,):
        a,e,i,b,c,f=A[0],A[1],A[2],A[3],A[4],A[5]
    else:
        assert A.shape==(3,3,),"supy.signal.inv3sym(A): A must be either 3x3 matrix or A=[a,e,i,b,c,f] containing only the upper triangle of matrix A, but A.shape="+str(A.shape)
        a,e,i,b,c,f=A[0,0],A[1,1],A[2,2],A[0,1],A[0,2],A[1,2]   # get relevant components of matrix
    alpha,beta,gamma,delta=e*i-f*f,b*f,e*c,i*b
    detA=a*alpha+c*(2*beta-gamma)-delta*b
    if abs(detA)<eps: return -1
    Am1=np.array([alpha,a*i-c*c,a*e-b*b,c*f-delta,beta-gamma,b*c-a*f])
    if A.shape!=(6,): Am1=np.array([[Am1[0],Am1[3],Am1[4]],\
                                    [Am1[3],Am1[1],Am1[5]],\
                                    [Am1[4],Am1[5],Am1[2]]])
    return Am1/detA

def inv3sym_arr(A):    
    """
    invert array of symmetric 3x3 matrices using the explicit inversion formula (see AB5/pp6; cf. Mathe1, Satz 8.26, pp205)  
    :param A: either 3x3xN or 6xN array representing the symmetric matrixes to be inverted 
              if A is 3x3xN then A[:,:,n] is the n-th matrix to be inverted
              if A is 6xN then A[:,n] is the n-th matrix to be inverted, interpreted as 1D array of length 6  containing the upper triangle a=A11, e=A22, i=A33, b=A12, c=A13, f=A23
    :returns Am1,detA: inverse Matrix (same format as A) and corresponding determinant (to identify singular components) 
    """
    if len(A.shape)==2 and A.shape[0]==6:
        flag6=1
        a,e,i,b,c,f=A[0],A[1],A[2],A[3],A[4],A[5]
    else:
        flag6=0
        assert len(A.shape)==3 and A.shape[0]==3 and A.shape[1]==3,"supy.signal.inv3sym_arr(A): Symmetric A must be either 3x3xN or 6xN array A=[a,e,i,b,c,f] containing only the 6 upper triangle entries, "+\
            "but A.shape="+str(A.shape)
        a,e,i,b,c,f=A[0,0],A[1,1],A[2,2],A[0,1],A[0,2],A[1,2]   # get relevant components of matrix
    Am1=np.empty((6,A.shape[-1]))         # allocate space for inverse matrix (represented as 1D array of length 6)
    Am1[0,:],beta,gamma,delta=np.multiply(e,i)-np.multiply(f,f),np.multiply(b,f),np.multiply(e,c),np.multiply(i,b)    # Am1[0,:] corresponds to alpha (see AB5/p7/Satz2)
    detA=np.multiply(a,Am1[0,:])+np.multiply(c,2*beta-gamma)-np.multiply(delta,b)
    Am1[1,:]=np.multiply(a,i)-np.multiply(c,c)
    Am1[2,:]=np.multiply(a,e)-np.multiply(b,b)
    Am1[3,:]=np.multiply(c,f)-delta
    Am1[4,:]=beta-gamma
    Am1[5,:]=np.multiply(b,c)-np.multiply(a,f)
    if flag6<=0: Am1=np.array([[Am1[0],Am1[3],Am1[4]],\
                               [Am1[3],Am1[1],Am1[5]],\
                               [Am1[4],Am1[5],Am1[2]]])
    return np.divide(Am1,detA),detA

def mult3sym_arr(A,v):    
    """
    matrix-vector-multiplications w=A*v, more specifically,
    multiply array of 3x3 symmetric matrixes A with 3dim vectors v (see AB5/p8/19.4.2023)
    :param A: 6xN array representing the N symmetric 3x3 matrixes to be multiplied
    :param v: 3xN array representing the N 3-dim column vectors v to be multiplied to A (from right)
    :returns w: 3xN array representing the N resulting 3D-Vectors from the matrix-vector multiplications  
    """
    if len(A.shape)==2 and A.shape[0]==6:
        flag6=1
        a,e,i,b,c,f=A[0],A[1],A[2],A[3],A[4],A[5]
    else:
        flag6=0
        assert len(A.shape)==3 and A.shape[0]==3 and A.shape[1]==3,"supy.signal.inv3sym_arr(A): Symmetric A must be either 3x3xN or 6xN array A=[a,e,i,b,c,f] containing only the 6 upper triangle entries, "+\
            "but A.shape="+str(A.shape)
        a,e,i,b,c,f=A[0,0],A[1,1],A[2,2],A[0,1],A[0,2],A[1,2]   # get relevant components of matrix
    w=np.empty((3,A.shape[-1]))         # allocate space for N results of matrix-vector-multipliations (represented as 1D array of length 3)
    w[0]=np.multiply(a,v[0])+np.multiply(b,v[1])+np.multiply(c,v[2])   # see AB5/p8/19.4.2023
    w[1]=np.multiply(b,v[0])+np.multiply(e,v[1])+np.multiply(f,v[2])   # see AB5/p8/19.4.2023
    w[2]=np.multiply(c,v[0])+np.multiply(f,v[1])+np.multiply(i,v[2])   # see AB5/p8/19.4.2023
    return w


# ***************************************************************************************
# ***************************************************************************************
# Part II) Signal Detection with Truncated Gaussians
# ***************************************************************************************
# ***************************************************************************************
def getDerivatives4TruncatedGaussiansError(mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu=1.0,lmbda_sig2=1.0,lmbda_N=1.0, flagOnlyE=1):
    """
    compute Gradient and Hessian of Truncated Gaussian Error Function (for Details see NB36)
    copy (or slightly more efficient variant) of the implementation from ~/hs-albsig/02-research/Borst_Fledermaeuse/python/checkParameterEstimationNB36.py
    only difference: per default (flagOnlyE>0) return only E,D_E,DD_E (i.e., loss,gradient,hessian)
    :param mu  : expectation of original (non-truncated) Gaussian distribution (here used as model parameter to be optimized, see NB36/p1)
    :param sig2: variance of original (non-truncated) Gaussian distribution (here used as model parameter to be optimized, see NB36/p1)
    :param N   : sample number of original (non-truncated) Gaussian distribution (here used as model parameter to be optimized, see NB36/p1)
    :param a: lower bound of truncation interval (here used as model input, see NB36/p1)
    :param b: upper bound of truncation interval (here used as model input, see NB36/p1)
    :param mu__bar  : mean estimator of truncated Gaussian distribution as measured from data (here used as target value, see NB36/p1)
    :param sig2__bar: variance estimator of truncated Gaussian distribution as measured from data (here used as target value, see NB36/p1)
    :param N__bar   : number of samples original Gaussian distribution lying in the [a,b] interval as measured from data (here used as target value, see NB36/p1)
    :param lmbda_mu  : weight of the loss term w.r.t. model parameter mu
    :param lmbda_sig2: weight of the loss term w.r.t. model parameter sig2
    :param lmbda_N   : weight of the loss term w.r.t. model parameter N
    :param flagOnlyE: if >=0 then return only E,D_E,DD_E (i.e. error function, gradient, and hessian); otherwise return dict of all intermediary results
    """
    # ***************************************************************************************************************************************************************************
    # (PART I): Compute moments and their derivatives according to NB34   (copied from checkTruncatedGaussiansNB34.py, def getDerivatives_NB34_pp12(mu,sig,a,b,n,filter=None))
    # ***************************************************************************************************************************************************************************
    #assert N__bar>2,"N__bar="+str(N__bar)+"is too small!!!!!"
    n=4                # we need raw moments up to order n=4 (for variance estimation NB35/p3/Satz3/(20); see also NB36/p3/(32),(36) 
    sig=np.sqrt(sig2)  # the formulas of NB34 are based on sig rather than sig2
    
    # (I.i) auxiliary values (applying definitions from Satz 1 (p2) and Section 4 (p5) and Section 6 (p12)
    sqrt2,sqrt2pi=np.sqrt(2),np.sqrt(2.0*np.pi)
    alpha, beta = (a-mu)/sig, (b-mu)/sig                                                   # NB34, p2, Satz 1
    Z = 0.5*(erf(beta/sqrt2)-erf(alpha/sqrt2))                                             # NB34, p2, Satz 1
    phi_alpha, phi_beta = np.exp(-0.5*alpha*alpha)/sqrt2pi, np.exp(-0.5*beta*beta)/sqrt2pi # NB34, p2, Satz 1
    #sig2=sig*sig   # sig^2     # not required as sig2 is given as parameter here (NB36)
    sig3=sig2*sig   # sig^3
    Z2=Z*Z         # Z^2
    Z3=Z2*Z        # Z^3
    sigi=np.ones(n+1)                                # initialize sigi[0]=sig^0=1
    for i in range(1,n+1): sigi[i]=sigi[i-1]*sig     # sigi[i]=sig^i
    mui=np.ones(n+1)                                 # initialize mui[0]=mu^0=1
    for i in range(1,n+1): mui[i]=mui[i-1]*mu        # sigi[i]=sig^i
    
    # (I.ii) compute the fj(alpha,beta):=beta^j*phi(beta)-alpha^j*phi(alpha) from NB34, p12, (6.25)
    f=np.zeros(n+5)
    for j in range(max(n+5,7)):                       # for derivatives we need f[j] upto j=n+4 (see (6.32)) and a minimum of j=6 (see (6.45))
        if j==0: alphaj,betaj=1.0,1.0                 # initialize alpha^j, beta^j
        else: alphaj,betaj=alphaj*alpha,betaj*beta    # update alpha^j, beta^j
        f[j]=betaj*phi_beta-alphaj*phi_alpha          # NB34, p12, (6.25)

    # (I.iii) compute the derivatives of the fj(alpha,beta) from NB34, p12, (6.28)-(6.32)
    d_f_DIV_d_mu  = np.zeros(n+1)
    d_f_DIV_d_sig = np.zeros(n+1)
    d2_f_DIV_d_mu_d_mu   = np.zeros(n+1)
    d2_f_DIV_d_sig_d_sig = np.zeros(n+1)
    d2_f_DIV_d_mu_d_sig  = np.zeros(n+1)
    for j in range(max(n+1,3)):              # for derivatives of gamma we need at least j=2 (see NB34, p13/(6.45))
        d_f_DIV_d_mu        [j]=(f[j+1]-j*f[max(j-1,0)])/sig   # NB34, p15/(6.63), p12/(6.28)
        d_f_DIV_d_sig       [j]=(f[j+2]-j*f[j])/sig            # NB34, p15/(6.64), p12/(6.29)
        d2_f_DIV_d_mu_d_mu  [j]=(f[j+2]-(2*j+1)*f[j]+j*(j-1)*f[max(j-2,0)])/sig2 # NB34, p15/(6.65), p12/(6.30)
        d2_f_DIV_d_sig_d_sig[j]=(f[j+4]-(2*j+3)*f[j+2]+j*(j+1)*f[j])/sig2        # NB34, p15/(6.66), p12/(6.31)
        d2_f_DIV_d_mu_d_sig [j]=(f[j+3]-(2*j+2)*f[j+1]+j*j*f[max(j-1,0)])/sig2   # NB34, p15/(6.67), p12/(6.32)

    # (I.iv) compute gamma and the derivatives of Z and gamma (see NB34, p2/Satz 1, p10/(6.14), p8, p13
    gamma=f[0]/Z             # NB34, p13/(6.42), p10/(6.14)
    gamma2=gamma*gamma
    gammai=np.ones(n+1)                                # initialize gammai[0]=gamma^0=1
    for i in range(1,n+1): gammai[i]=gammai[i-1]*gamma # gammai[i]=gamma^i
    d_Z_DIV_d_mu =-f[0]/sig  # NB34, p13/(6.35), p8/(4.41)
    d_Z_DIV_d_sig=-f[1]/sig  # NB34, p13/(6.36), p8/(4.42)
    d2_Z_DIV_d_mu_d_mu   = -f[1]/sig2         # NB34, p13/(6.37), p8/(4.43)
    d2_Z_DIV_d_sig_d_sig = (2*f[1]-f[3])/sig2 # NB34, p13/(6.38), p8/(4.44)
    d2_Z_DIV_d_mu_d_sig  = (f[0]-f[2])/sig2   # NB34, p13/(6.39), p8/(4.45)
    d_gamma_DIV_d_mu =(f[1]/Z+gamma2)/sig          # NB34, p13/(6.40)
    d_gamma_DIV_d_sig=(f[2]+gamma*f[1])/(sig*Z)    # NB34, p13/(6.41)
    d2_gamma_DIV_d_mu_d_mu  =(d_f_DIV_d_mu[1]+f[1]*gamma/sig+2*f[0]*d_gamma_DIV_d_mu)/(sig*Z)                             # NB34, p13/(6.43)
    d2_gamma_DIV_d_sig_d_sig=(d_f_DIV_d_sig[2]+gamma*d_f_DIV_d_sig[1]+d_gamma_DIV_d_sig*(2*f[1]-Z))/(sig*Z)               # NB34, p13/(6.44)
    d2_gamma_DIV_d_mu_d_sig =(f[0]*d_gamma_DIV_d_sig+d_f_DIV_d_mu[2]+f[1]*d_gamma_DIV_d_mu+gamma*d_f_DIV_d_mu[1])/(sig*Z) # NB34, p13/(6.45)

    # (I.v) compute double factorials for Sn and other variables
    doubfac=np.ones(n+1,dtype='int')  # initialize doubfac[0]=1, doubfac[1]=1
    for i in range(2,n+1): doubfac[i]=doubfac[i-2]*i    # n!!:=n*(n-2)!! = n*(n-2)*(n-4)*...*1
    
    # (I.vi) compute Sn and their derivatives (NB34, p12, p13)
    S=np.zeros(n+1)
    d_S_DIV_d_mu=np.zeros(n+1)
    d_S_DIV_d_sig=np.zeros(n+1)
    d2_S_DIV_d_mu_d_mu=np.zeros(n+1)
    d2_S_DIV_d_sig_d_sig=np.zeros(n+1)
    d2_S_DIV_d_mu_d_sig=np.zeros(n+1)
    for ni in range(n+1):
        if ni%2==0:        # ni even ...
            for k in range(ni//2):
                k2p1=2*k+1
                fac=doubfac[max(0,ni-1)]//doubfac[k2p1]                # fac := (ni-1)!! / (2k+1)!!
                S[ni] -= fac*f[2*k+1]                                  # NB34, p12/(6.24)
                d_S_DIV_d_mu [ni] -= fac*d_f_DIV_d_mu[k2p1]                # NB34, p13/(6.34)
                d_S_DIV_d_sig[ni] -= fac*d_f_DIV_d_sig[k2p1]               # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_mu  [ni] -= fac*d2_f_DIV_d_mu_d_mu[k2p1]   # NB34, p13/(6.34)
                d2_S_DIV_d_sig_d_sig[ni] -= fac*d2_f_DIV_d_sig_d_sig[k2p1] # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_sig [ni] -= fac*d2_f_DIV_d_mu_d_sig[k2p1]  # NB34, p13/(6.34)
            S[ni]+=doubfac[max(0,ni-1)]*Z                              # NB34, p12/(6.24)
            d_S_DIV_d_mu [ni]+=doubfac[max(0,ni-1)]*d_Z_DIV_d_mu       # NB34, p13/(6.34)
            d_S_DIV_d_sig[ni]+=doubfac[max(0,ni-1)]*d_Z_DIV_d_sig      # NB34, p13/(6.34)
            d2_S_DIV_d_mu_d_mu  [ni]+=doubfac[max(0,ni-1)]*d2_Z_DIV_d_mu_d_mu   # NB34, p13/(6.34)
            d2_S_DIV_d_sig_d_sig[ni]+=doubfac[max(0,ni-1)]*d2_Z_DIV_d_sig_d_sig # NB34, p13/(6.34)
            d2_S_DIV_d_mu_d_sig [ni]+=doubfac[max(0,ni-1)]*d2_Z_DIV_d_mu_d_sig  # NB34, p13/(6.34)
        else:              # ni odd ...
            for k in range((ni-1)//2+1):
                k2=2*k
                fac=doubfac[max(0,ni-1)]//doubfac[k2]      # fac := (ni-1)!! / (2k)!!
                S[ni] -= fac*f[k2]                         # NB34, p12/(6.24)
                d_S_DIV_d_mu [ni] -= fac*d_f_DIV_d_mu[k2]        # NB34, p13/(6.34)
                d_S_DIV_d_sig[ni] -= fac*d_f_DIV_d_sig[k2]       # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_mu  [ni] -= fac*d2_f_DIV_d_mu_d_mu[k2]   # NB34, p13/(6.34)
                d2_S_DIV_d_sig_d_sig[ni] -= fac*d2_f_DIV_d_sig_d_sig[k2] # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_sig [ni] -= fac*d2_f_DIV_d_mu_d_sig[k2]  # NB34, p13/(6.34)

    # (I.vii) compute Fij and Gi and their derivatives (NB34, p14)
    F=np.nan*np.ones((n+1,n+1)) # allocate memory for F(i,j):=gamma^i*S_j, see NB34,p14/(6.46) (only needed for i+j<=n; mark remaining fields with NaN to recognized errors)
    d_F_DIV_d_mu,d_F_DIV_d_sig                                 =np.nan*np.ones((n+1,n+1)),np.nan*np.ones((n+1,n+1)) 
    d2_F_DIV_d_mu_d_mu,d2_F_DIV_d_sig_d_sig,d2_F_DIV_d_mu_d_sig=np.zeros((n+1,n+1)),np.zeros((n+1,n+1)),np.zeros((n+1,n+1))
    G,d_G_DIV_d_mu,d_G_DIV_d_mu,d_G_DIV_d_sig                  =np.zeros(n+1),np.zeros(n+1),np.zeros(n+1),np.zeros(n+1)  # allocate memory for G(i):=sigma^i / Z, see NB34,p14/(6.47)
    d2_G_DIV_d_mu_d_mu,d2_G_DIV_d_sig_d_sig,d2_G_DIV_d_mu_d_sig=np.zeros(n+1),np.zeros(n+1),np.zeros(n+1)
    for i in range(n+1):
        G[i]=sigi[i]/Z            # NB34,p14/(6.47)
        d_G_DIV_d_mu [i]=-sigi[i]/Z2*d_Z_DIV_d_mu                          # NB34,p14/(6.53)
        d_G_DIV_d_sig[i]=-sigi[i]/Z2*d_Z_DIV_d_sig + i*sigi[max(i-1,0)]/Z  # NB34,p14/(6.54)
        d2_G_DIV_d_mu_d_mu  [i]=2*sigi[i]/Z3*d_Z_DIV_d_mu*d_Z_DIV_d_mu - sigi[i]/Z2*d2_Z_DIV_d_mu_d_mu                                                             # NB34,p14/(6.55)
        d2_G_DIV_d_sig_d_sig[i]=sigi[i]/Z2*(2/Z*d_Z_DIV_d_sig*d_Z_DIV_d_sig-d2_Z_DIV_d_sig_d_sig)-2*i*sigi[max(i-1,0)]/Z2*d_Z_DIV_d_sig+i*(i-1)*sigi[max(i-2,0)]/Z # NB34,p14/(6.56)
        d2_G_DIV_d_mu_d_sig [i]=sigi[i]/Z2*(2/Z*d_Z_DIV_d_mu*d_Z_DIV_d_sig-d2_Z_DIV_d_mu_d_sig)-i*sigi[max(i-1,0)]/Z2*d_Z_DIV_d_mu                                 # NB34,p14/(6.57)
        for j in range(n+1):
            if i+j<=n:
                F[i,j]=gammai[i]*S[j]      # NB34,p14/(6.46)
                d_F_DIV_d_mu [i,j]=i*gammai[max(0,i-1)]*d_gamma_DIV_d_mu *S[j] + gammai[i]*d_S_DIV_d_mu [j]  # NB34,p14/(6.48)
                d_F_DIV_d_sig[i,j]=i*gammai[max(0,i-1)]*d_gamma_DIV_d_sig*S[j] + gammai[i]*d_S_DIV_d_sig[j]  # NB34,p14/(6.49)
                d2_F_DIV_d_mu_d_mu  [i,j]=i*(i-1)*gammai[max(0,i-2)]*d_gamma_DIV_d_mu*d_gamma_DIV_d_mu*S[j] \
                                           + i*gammai[max(0,i-1)]*(d2_gamma_DIV_d_mu_d_mu*S[j]+2*d_gamma_DIV_d_mu*d_S_DIV_d_mu[j]) \
                                           + gammai[i]*d2_S_DIV_d_mu_d_mu[j]                                   # NB34,p14/(6.50)
                d2_F_DIV_d_sig_d_sig[i,j]=i*(i-1)*gammai[max(0,i-2)]*d_gamma_DIV_d_sig*d_gamma_DIV_d_sig*S[j] \
                                           + i*gammai[max(0,i-1)]*(d2_gamma_DIV_d_sig_d_sig*S[j]+2*d_gamma_DIV_d_sig*d_S_DIV_d_sig[j]) \
                                           + gammai[i]*d2_S_DIV_d_sig_d_sig[j]                                 # NB34,p14/(6.51)
                d2_F_DIV_d_mu_d_sig [i,j]=i*(i-1)*gammai[max(0,i-2)]*d_gamma_DIV_d_mu*d_gamma_DIV_d_sig*S[j] \
                                           + i*gammai[max(0,i-1)]*(d2_gamma_DIV_d_mu_d_sig*S[j]+d_gamma_DIV_d_mu*d_S_DIV_d_sig[j]+d_gamma_DIV_d_sig*d_S_DIV_d_mu[j]) \
                                           + gammai[i]*d2_S_DIV_d_mu_d_sig[j]                                  # NB34,p14/(6.52)

    # (I.viii) compute central moments mu_n' and their derivatives (NB34, p12/(6.26), p15/(6.58a)
    n_fac=np.ones((n+1),'int')                          # initialize n_fac[0]=0!=1
    for ni in range(1,n+1): n_fac[ni]=ni*n_fac[ni-1]    # n_fac[ni]=ni!=ni*(ni-1)!=ni*n_fac[ni-1]
    n_choose_k = np.nan*np.ones((n+1,n+1),'int')        # initialize (n k) with nan (to recognize errors)
    for ni in range(n+1):
        for k in range(ni+1): n_choose_k[ni,k]=n_fac[ni]/(n_fac[k]*n_fac[ni-k])  # (ni k) := ni!/((ni-k)!*k!)
    mu_n_=np.zeros((n+1))  # allocate memory for n-th central moment mu_n' of truncated Gaussian  (NB34, p12/(6.26), p15/(6.58a)
    d_mu_n__DIV_d_mu =np.zeros((n+1))  # allocate memory 
    d_mu_n__DIV_d_sig=np.zeros((n+1))  # allocate memory 
    d2_mu_n__DIV_d_mu_d_mu  =np.zeros((n+1))  # allocate memory 
    d2_mu_n__DIV_d_sig_d_sig=np.zeros((n+1))  # allocate memory 
    d2_mu_n__DIV_d_mu_d_sig =np.zeros((n+1))  # allocate memory 
    for ni in range(n+1):
        mu_n_[ni] = G[ni]*np.sum([n_choose_k[ni,k]*F[ni-k,k] for k in range(ni+1)])    # NB34,p15/(6.58a)
        d_mu_n__DIV_d_mu [ni]= np.sum([n_choose_k[ni,k]*(d_G_DIV_d_mu [ni]*F[ni-k,k]+G[ni]*d_F_DIV_d_mu [ni-k,k]) for k in range(ni+1)]) # NB34,p15/(6.58)
        d_mu_n__DIV_d_sig[ni]= np.sum([n_choose_k[ni,k]*(d_G_DIV_d_sig[ni]*F[ni-k,k]+G[ni]*d_F_DIV_d_sig[ni-k,k]) for k in range(ni+1)]) # NB34,p15/(6.59)
        d2_mu_n__DIV_d_mu_d_mu  [ni]=np.sum([n_choose_k[ni,k]*(d2_G_DIV_d_mu_d_mu[ni]*F[ni-k,k]+2*d_G_DIV_d_mu[ni]*d_F_DIV_d_mu[ni-k,k]+G[ni]*d2_F_DIV_d_mu_d_mu[ni-k,k]) \
                                             for k in range(ni+1)]) # NB34,p15/(6.60)
        d2_mu_n__DIV_d_sig_d_sig[ni]=np.sum([n_choose_k[ni,k]*(d2_G_DIV_d_sig_d_sig[ni]*F[ni-k,k]+2*d_G_DIV_d_sig[ni]*d_F_DIV_d_sig[ni-k,k]+G[ni]*d2_F_DIV_d_sig_d_sig[ni-k,k]) \
                                             for k in range(ni+1)]) # NB34,p15/(6.61)
        d2_mu_n__DIV_d_mu_d_sig [ni]=np.sum([n_choose_k[ni,k]*(d2_G_DIV_d_mu_d_sig[ni]*F[ni-k,k]+d_G_DIV_d_mu[ni]*d_F_DIV_d_sig[ni-k,k]\
                                                               +d_G_DIV_d_sig[ni]*d_F_DIV_d_mu[ni-k,k]+G[ni]*d2_F_DIV_d_mu_d_sig[ni-k,k]) for k in range(ni+1)]) # NB34,p15/(6.61)
    # (I.ix) compute Fij_tilde and their derivatives (NB34, p15)
    Ft=np.nan*np.ones((n+1,n+1)) # allocate memory for Ft(i,j):=F_tilde(i,j):=mu^i*sig^j*S_j, see NB34,p15/(6.68) (only needed for i+j<=n; mark remaining fields with NaN to recognized errors)
    d_Ft_DIV_d_mu,d_Ft_DIV_d_sig                                  =np.nan*np.ones((n+1,n+1)),np.nan*np.ones((n+1,n+1)) 
    d2_Ft_DIV_d_mu_d_mu,d2_Ft_DIV_d_sig_d_sig,d2_Ft_DIV_d_mu_d_sig=np.zeros((n+1,n+1)),np.zeros((n+1,n+1)),np.zeros((n+1,n+1))
    for i in range(n+1):
        for j in range(n+1):
            if i+j<=n:
                Ft[i,j]=mui[i]*sigi[j]*S[j]      # NB34,p15/(6.68)
                d_Ft_DIV_d_mu [i,j]=sigi[j]*(i*mui [max(0,i-1)]*S[j]+mui [i]*d_S_DIV_d_mu [j])  # NB34,p15/(6.69)
                d_Ft_DIV_d_sig[i,j]=mui [i]*(j*sigi[max(0,j-1)]*S[j]+sigi[j]*d_S_DIV_d_sig[j])  # NB34,p15/(6.70)
                d2_Ft_DIV_d_mu_d_mu  [i,j]=sigi[j]*(i*(i-1)*mui[max(0,i-2)]*S[j]+2*i*mui[max(0,i-1)]*d_S_DIV_d_mu[j]+mui[i]*d2_S_DIV_d_mu_d_mu[j])      # NB34,p15/(6.71)
                d2_Ft_DIV_d_sig_d_sig[i,j]=mui[i]*(j*(j-1)*sigi[max(0,j-2)]*S[j]+2*j*sigi[max(0,j-1)]*d_S_DIV_d_sig[j]+sigi[j]*d2_S_DIV_d_sig_d_sig[j]) # NB34,p15/(6.72)
                d2_Ft_DIV_d_mu_d_sig [i,j]=j*sigi[max(0,j-1)]*(i*mui[max(0,i-1)]*S[j]+mui[i]*d_S_DIV_d_mu[j]) \
                                            + sigi[j]*(i*mui [max(0,i-1)]*d_S_DIV_d_sig[j]+mui[i]*d2_S_DIV_d_mu_d_sig[j])                               # NB34,p15/(6.73)

    # (I.x) compute raw moments M_n' and their derivatives (NB34, p12/(6.27), p15/(6.69), p16/(6.74)
    M_n_=np.zeros((n+1))  # allocate memory for n-th raw moment M_n' of truncated Gaussian  (NB34, p12/(6.27), p15/(6.69), p16/(6.74)
    d_M_n__DIV_d_mu =np.zeros((n+1))  # allocate memory 
    d_M_n__DIV_d_sig=np.zeros((n+1))  # allocate memory 
    d2_M_n__DIV_d_mu_d_mu  =np.zeros((n+1))  # allocate memory 
    d2_M_n__DIV_d_sig_d_sig=np.zeros((n+1))  # allocate memory 
    d2_M_n__DIV_d_mu_d_sig =np.zeros((n+1))  # allocate memory 
    for ni in range(n+1):
        M_n_[ni] = G[0]*np.sum([n_choose_k[ni,k]*Ft[ni-k,k] for k in range(ni+1)])    # NB34,p16/(6.74a)
        d_M_n__DIV_d_mu [ni]= np.sum([n_choose_k[ni,k]*(d_G_DIV_d_mu [0]*Ft[ni-k,k]+G[0]*d_Ft_DIV_d_mu [ni-k,k]) for k in range(ni+1)]) # NB34,p16/(6.75)
        d_M_n__DIV_d_sig[ni]= np.sum([n_choose_k[ni,k]*(d_G_DIV_d_sig[0]*Ft[ni-k,k]+G[0]*d_Ft_DIV_d_sig[ni-k,k]) for k in range(ni+1)]) # NB34,p16/(6.76)
        d2_M_n__DIV_d_mu_d_mu  [ni]=np.sum([n_choose_k[ni,k]*(d2_G_DIV_d_mu_d_mu[0]*Ft[ni-k,k]+2*d_G_DIV_d_mu[0]*d_Ft_DIV_d_mu[ni-k,k]+G[0]*d2_Ft_DIV_d_mu_d_mu[ni-k,k]) \
                                            for k in range(ni+1)]) # NB34,p16/(6.77)
        d2_M_n__DIV_d_sig_d_sig[ni]=np.sum([n_choose_k[ni,k]*(d2_G_DIV_d_sig_d_sig[0]*Ft[ni-k,k]+2*d_G_DIV_d_sig[0]*d_Ft_DIV_d_sig[ni-k,k]+G[0]*d2_Ft_DIV_d_sig_d_sig[ni-k,k]) \
                                            for k in range(ni+1)]) # NB34,p16/(6.78)
        d2_M_n__DIV_d_mu_d_sig [ni]=np.sum([n_choose_k[ni,k]*(d2_G_DIV_d_mu_d_sig[0]*Ft[ni-k,k]+d_G_DIV_d_mu[0]*d_Ft_DIV_d_sig[ni-k,k]\
                                                              +d_G_DIV_d_sig[0]*d_Ft_DIV_d_mu[ni-k,k]+G[0]*d2_Ft_DIV_d_mu_d_sig[ni-k,k]) for k in range(ni+1)]) # NB34,p16/(6.79)

    # ***************************************************************************************************************************************************************************
    # (PART II): Include additional variables and derivatives for Error Function of Parameter Estimation (NB36) 
    # ***************************************************************************************************************************************************************************
    # (II.i) define indexes for variables and derivatives
    ix_mu,ix_sig2,ix_N = 0,1,2                                                                        # indexes of variables and 1st derivatives
    ix_dd_mu_mu, ix_dd_sig2_sig2, ix_dd_N_N, ix_dd_mu_sig2, ix_dd_mu_N, ix_dd_sig2_N = 0,1,2,3,4,5    # index of 2nd derivatives

    # (II.ii) compute derivatives of functions of raw moments (NB36/p3/(37-40))
    D_M1_ = np.array([d_M_n__DIV_d_mu[1], d_M_n__DIV_d_sig[1]/(2*sig), 0.0])    # first derivatives of M1_ (for derivatives w.r.t. sig2 use NB36/(14)
    D_M2_ = np.array([d_M_n__DIV_d_mu[2], d_M_n__DIV_d_sig[2]/(2*sig), 0.0])    # first derivatives of M2_ (for derivatives w.r.t. sig2 use NB36/(14)
    D_M3_ = np.array([d_M_n__DIV_d_mu[3], d_M_n__DIV_d_sig[3]/(2*sig), 0.0])    # first derivatives of M3_ (for derivatives w.r.t. sig2 use NB36/(14)
    D_M4_ = np.array([d_M_n__DIV_d_mu[4], d_M_n__DIV_d_sig[4]/(2*sig), 0.0])    # first derivatives of M4_ (for derivatives w.r.t. sig2 use NB36/(14)
    DD_M1_ = np.array([d2_M_n__DIV_d_mu_d_mu[1], d2_M_n__DIV_d_sig_d_sig[1]/(4*sig2)-d_M_n__DIV_d_sig[1]/(4*sig3), 0.0, d2_M_n__DIV_d_mu_d_sig[1]/(2*sig), 0.0, 0.0]) # 2nd deriv. of M1_; deriv. w.r.t. sig2 use NB36/(18),(14)
    DD_M2_ = np.array([d2_M_n__DIV_d_mu_d_mu[2], d2_M_n__DIV_d_sig_d_sig[2]/(4*sig2)-d_M_n__DIV_d_sig[2]/(4*sig3), 0.0, d2_M_n__DIV_d_mu_d_sig[2]/(2*sig), 0.0, 0.0]) # 2nd deriv. of M2_; deriv. w.r.t. sig2 use NB36/(18),(14)
    DD_M3_ = np.array([d2_M_n__DIV_d_mu_d_mu[3], d2_M_n__DIV_d_sig_d_sig[3]/(4*sig2)-d_M_n__DIV_d_sig[3]/(4*sig3), 0.0, d2_M_n__DIV_d_mu_d_sig[3]/(2*sig), 0.0, 0.0]) # 2nd deriv. of M3_; deriv. w.r.t. sig2 use NB36/(18),(14)
    DD_M4_ = np.array([d2_M_n__DIV_d_mu_d_mu[4], d2_M_n__DIV_d_sig_d_sig[4]/(4*sig2)-d_M_n__DIV_d_sig[4]/(4*sig3), 0.0, d2_M_n__DIV_d_mu_d_sig[4]/(2*sig), 0.0, 0.0]) # 2nd deriv. of M4_; deriv. w.r.t. sig2 use NB36/(18),(14)
    D_M2_2     = 2*M_n_[2]*D_M2_                                # NB36/(37)
    D_M1__M3_  = M_n_[3]*D_M1_+M_n_[1]*D_M3_                    # NB36/(38)
    D_M1_2_M2_ = 2*M_n_[1]*M_n_[2]*D_M1_+M_n_[1]*M_n_[1]*D_M2_  # NB36/(39)
    D_M1_4     = 4*M_n_[1]*M_n_[1]*M_n_[1]*D_M1_                # NB36/(40)
    D_M2_D_M2_  = np.array([D_M2_[0]*D_M2_[0], D_M2_[1]*D_M2_[1], D_M2_[2]*D_M2_[2], \
                            D_M2_[0]*D_M2_[1], D_M2_[0]*D_M2_[2], D_M2_[1]*D_M2_[2]])  # product d_M2_/du*d_M2_/dw for NB36/p3/(41), term 1  
    D_M1_D_M3_  = np.array([D_M1_[0]*D_M3_[0], D_M1_[1]*D_M3_[1], D_M1_[2]*D_M3_[2], \
                            D_M1_[0]*D_M3_[1], D_M1_[0]*D_M3_[2], D_M1_[1]*D_M3_[2]])  # product d_M1_/du*d_M3_/dw for NB36/p3/(42), term 2  
    D_M3_D_M1_  = np.array([D_M3_[0]*D_M1_[0], D_M3_[1]*D_M1_[1], D_M3_[2]*D_M1_[2], \
                            D_M3_[0]*D_M1_[1], D_M3_[0]*D_M1_[2], D_M3_[1]*D_M1_[2]])  # product d_M3_/du*d_M1_/dw for NB36/p3/(42), term 3  
    D_M1_D_M1_  = np.array([D_M1_[0]*D_M1_[0], D_M1_[1]*D_M1_[1], D_M1_[2]*D_M1_[2], \
                            D_M1_[0]*D_M1_[1], D_M1_[0]*D_M1_[2], D_M1_[1]*D_M1_[2]])  # product d_M1_/du*d_M1_/dw for NB36/p3/(43), term 1 and NB36/p3/(44), term 1  
    D_M1_D_M2_  = np.array([D_M1_[0]*D_M2_[0], D_M1_[1]*D_M2_[1], D_M1_[2]*D_M2_[2], \
                            D_M1_[0]*D_M2_[1], D_M1_[0]*D_M2_[2], D_M1_[1]*D_M2_[2]])  # product d_M1_/du*d_M2_/dw for NB36/p3/(43), term 3  
    D_M2_D_M1_  = np.array([D_M2_[0]*D_M1_[0], D_M2_[1]*D_M1_[1], D_M2_[2]*D_M1_[2], \
                            D_M2_[0]*D_M1_[1], D_M2_[0]*D_M1_[2], D_M2_[1]*D_M1_[2]])  # product d_M2_/du*d_M1_/dw for NB36/p3/(43), term 4  
    DD_M2_2     = 2*D_M2_D_M2_+2*M_n_[2]*DD_M2_                                                                  # NB36/(41)
    DD_M1__M3_  = M_n_[3]*DD_M1_+D_M1_D_M3_+D_M3_D_M1_+M_n_[1]*DD_M3_                                            # NB36/(42)
    DD_M1_2_M2_ = 2*M_n_[2]*(D_M1_D_M1_+M_n_[1]*DD_M1_)+2*M_n_[1]*(D_M1_D_M2_+D_M2_D_M1_)+M_n_[1]*M_n_[1]*DD_M2_ # NB36/(43)
    DD_M1_4     = 12*M_n_[1]*M_n_[1]*D_M1_D_M1_+4*M_n_[1]*M_n_[1]*M_n_[1]*DD_M1_                                 # NB36/(44)
    
    # (II.iii) compute model predictions and their derivatives (NB36/p2/(12-25))
    mu_ = M_n_[1]            # expectation of truncated distribution corresponds to first raw moment
    sig2_ = mu_n_[2]         # variance of truncated distribution corresponds to second central moment
    N_=N*Z                   # expected number of samples that are in interval [a,b]
    D_mu_   = np.array([d_M_n__DIV_d_mu [1], d_M_n__DIV_d_sig [1]/(2*sig), 0.0])  # mu_ is 1st raw moment M_n_[1]; see also NB36/(21),(12),(14)
    D_sig2_ = np.array([d_mu_n__DIV_d_mu[2], d_mu_n__DIV_d_sig[2]/(2*sig), 0.0])  # sig2_ is 2nd central moment mu_n_[2]; see also NB36/(23),(12),(14),(18)
    D_N_    = np.array([N*d_Z_DIV_d_mu, N*d_Z_DIV_d_sig/(2*sig), Z])              # see NB36/(13),(15),(16)
    DD_mu_  = np.array([d2_M_n__DIV_d_mu_d_mu [1], d2_M_n__DIV_d_sig_d_sig [1]/(4*sig2)-d_M_n__DIV_d_sig [1]/(4*sig3), 0.0, d2_M_n__DIV_d_mu_d_sig [1]/(2*sig), 0.0, 0.0])  # mu_=M_n_[1]; see also NB36/(22),(12),(14),(18)
    DD_sig2_= np.array([d2_mu_n__DIV_d_mu_d_mu[2], d2_mu_n__DIV_d_sig_d_sig[2]/(4*sig2)-d_mu_n__DIV_d_sig[2]/(4*sig3), 0.0, d2_mu_n__DIV_d_mu_d_sig[2]/(2*sig), 0.0, 0.0])  # mu_=mu_n_[2]; see also NB36/(24),(12),(14),(18)
    DD_N_   = np.array([N*d2_Z_DIV_d_mu_d_mu, N/(4*sig2)*d2_Z_DIV_d_sig_d_sig-N/(4*sig3)*d_Z_DIV_d_sig, 0.0, N/(2*sig)*d2_Z_DIV_d_mu_d_sig, d_Z_DIV_d_mu, d_Z_DIV_d_sig/(2*sig)]) # see NB36/(17),(19),(20),(25abc)
    
    # (II.iv) compute variances and their derivatives (NB36/p3/(26-40))
    var_mu__bar  =sig2_/N__bar       # NB36/(26a)
    var_N__bar   =N*Z*(1-Z)          # NB36/(27a)
    var_sig2__bar=M_n_[4]/N__bar - (N__bar-3)/(N__bar*(N__bar-1))*M_n_[2]*M_n_[2] \
                   - 4/N__bar*M_n_[1]*M_n_[3] + 4*(2*N__bar-3)/(N__bar*(N__bar-1))*M_n_[1]*M_n_[1]*M_n_[2] \
                   - 2*(2*N__bar-3)/(N__bar*(N__bar-1))*M_n_[1]**4 # NB36/(32); cf. NB35, p3, Satz 3; copied from checkVarianceNB35.py, def getVar4EVarEst_NB35_Satz3(n,M1,M2,M3,M4)
    D_var_mu__bar = D_sig2_/N__bar       # NB36/(26)
    DD_var_mu__bar = DD_sig2_/N__bar     # NB36/(26)
    D_var_N__bar = np.array([N*(1-2*Z)*d_Z_DIV_d_mu, N*(1-2*Z)*d_Z_DIV_d_sig/(2*sig), Z*(1-Z)])  # NB36/(27),(14),(29)  
    DD_var_N__bar = np.array([N*((1-2*Z)*d2_Z_DIV_d_mu_d_mu-2*d_Z_DIV_d_mu*d_Z_DIV_d_mu), \
                              N*(1-2*Z)*(d2_Z_DIV_d_sig_d_sig/(4*sig2)-d_Z_DIV_d_sig/(4*sig3))-N*2*d_Z_DIV_d_sig*d_Z_DIV_d_sig/(4*sig2), \
                              0.0,\
                              N*(1-2*Z)*d2_Z_DIV_d_mu_d_sig/(2*sig)-N*2*d_Z_DIV_d_mu*d_Z_DIV_d_sig/(2*sig),\
                              (1-2*Z)*d_Z_DIV_d_mu,\
                              (1-2*Z)*d_Z_DIV_d_sig/(2*sig)])  # NB36/(28),(31),(30),(14),(18)
    D_var_sig2__bar=D_M4_/N__bar - (N__bar-3)/(N__bar*(N__bar-1))*D_M2_2 \
                     - 4/N__bar*D_M1__M3_ + 4*(2*N__bar-3)/(N__bar*(N__bar-1))*D_M1_2_M2_ \
                     - 2*(2*N__bar-3)/(N__bar*(N__bar-1))*D_M1_4 # NB36/(35)
    DD_var_sig2__bar=DD_M4_/N__bar - (N__bar-3)/(N__bar*(N__bar-1))*DD_M2_2 \
                      - 4/N__bar*DD_M1__M3_ + 4*(2*N__bar-3)/(N__bar*(N__bar-1))*DD_M1_2_M2_ \
                      - 2*(2*N__bar-3)/(N__bar*(N__bar-1))*DD_M1_4 # NB36/(35)

    # (II.v) compute error function and its derivatives (NB36/p1-2/(1)-(11)
    eps_mu   = mu_-mu__bar       # difference error of mu_ 
    eps_sig2 = sig2_-sig2__bar   # difference error of sig2_
    eps_N    = N_-N__bar         # difference error of N_
    E = lmbda_mu*eps_mu*eps_mu/var_mu__bar + lmbda_sig2*eps_sig2*eps_sig2/var_sig2__bar + lmbda_N*eps_N*eps_N/var_N__bar   # loss function according to NB36/p1/(2)
    Q_mu   = eps_mu/var_mu__bar      # Qv from NB36/p2/(8) for v=mu
    Q_sig2 = eps_sig2/var_sig2__bar  # Qv from NB36/p2/(8) for v=sig2
    Q_N    = eps_N/var_N__bar        # Qv from NB36/p2/(8) for v=N
    #D_Q_mu   = (D_mu_  *var_mu__bar  -eps_mu  *D_var_mu__bar  )/(var_mu__bar  *var_mu__bar  )  # NB36/p2/(11)
    #D_Q_sig2 = (D_sig2_*var_sig2__bar-eps_sig2*D_var_sig2__bar)/(var_sig2__bar*var_sig2__bar)  # NB36/p2/(11)
    #D_Q_N    = (D_N_   *var_N__bar   -eps_N   *D_var_N__bar   )/(var_N__bar   *var_N__bar   )  # NB36/p2/(11)
    D_Q_mu   = (D_mu_  -Q_mu  *D_var_mu__bar  )/var_mu__bar    # NB36/p2/(11), improved
    D_Q_sig2 = (D_sig2_-Q_sig2*D_var_sig2__bar)/var_sig2__bar  # NB36/p2/(11), improved
    D_Q_N    = (D_N_   -Q_N   *D_var_N__bar   )/var_N__bar     # NB36/p2/(11), improved
    D_E = lmbda_mu*Q_mu*(2*D_mu_-Q_mu*D_var_mu__bar) + lmbda_sig2*Q_sig2*(2*D_sig2_-Q_sig2*D_var_sig2__bar) + lmbda_N*Q_N*(2*D_N_-Q_N*D_var_N__bar) # NB36/p2/(9)
    Dv__DQv_mu   = np.array([D_mu_  [0]  *D_Q_mu[0], D_mu_  [1]*D_Q_mu  [1], D_mu_  [2]*D_Q_mu  [2], \
                             D_mu_  [0]  *D_Q_mu[1], D_mu_  [0]*D_Q_mu  [2], D_mu_  [1]*D_Q_mu  [2]])  # d_v_/du*d_Qv/dw for v=mu, see NB36/p2/(10), term 1 in sum 
    Dv__DQv_sig2 = np.array([D_sig2_[0]*D_Q_sig2[0], D_sig2_[1]*D_Q_sig2[1], D_sig2_[2]*D_Q_sig2[2], \
                             D_sig2_[0]*D_Q_sig2[1], D_sig2_[0]*D_Q_sig2[2], D_sig2_[1]*D_Q_sig2[2]])  # d_v_/du*d_Qv/dw for v=sig2, see NB36/p2/(10), term 1 in sum 
    Dv__DQv_N    = np.array([D_N_   [0]*D_Q_N   [0], D_N_   [1]*D_Q_N   [1], D_N_   [2]*D_Q_N   [2], \
                             D_N_   [0]*D_Q_N   [1], D_N_   [0]*D_Q_N   [2], D_N_   [1]*D_Q_N   [2]])  # d_v_/du*d_Qv/dw for v=N, see NB36/p2/(10), term 1 in sum 
    Dvarv_DQv_mu   = np.array([D_var_mu__bar  [0]  *D_Q_mu[0], D_var_mu__bar  [1]*D_Q_mu  [1], D_var_mu__bar  [2]*D_Q_mu  [2], \
                               D_var_mu__bar  [0]  *D_Q_mu[1], D_var_mu__bar  [0]*D_Q_mu  [2], D_var_mu__bar  [1]*D_Q_mu  [2]])  # d_var_v__bar/du*d_Qv/dw for v=mu, see NB36/p2/(10), term 3 in sum 
    Dvarv_DQv_sig2 = np.array([D_var_sig2__bar[0]*D_Q_sig2[0], D_var_sig2__bar[1]*D_Q_sig2[1], D_var_sig2__bar[2]*D_Q_sig2[2], \
                               D_var_sig2__bar[0]*D_Q_sig2[1], D_var_sig2__bar[0]*D_Q_sig2[2], D_var_sig2__bar[1]*D_Q_sig2[2]])  # d_var_v__bar/du*d_Qv/dw for v=sig2, see NB36/p2/(10), term 3 in sum 
    Dvarv_DQv_N    = np.array([D_var_N__bar   [0]*D_Q_N   [0], D_var_N__bar   [1]*D_Q_N   [1], D_var_N__bar   [2]*D_Q_N   [2], \
                               D_var_N__bar   [0]*D_Q_N   [1], D_var_N__bar   [0]*D_Q_N   [2], D_var_N__bar   [1]*D_Q_N   [2]])  # d_var_v__bar/du*d_Qv/dw for v=N, see NB36/p2/(10), term 3 in sum 
    DD_E = 2*lmbda_mu  *(Dv__DQv_mu   + Q_mu  *(DD_mu_  -Dvarv_DQv_mu  ) - Q_mu  *Q_mu  /2*DD_var_mu__bar  ) + \
           2*lmbda_sig2*(Dv__DQv_sig2 + Q_sig2*(DD_sig2_-Dvarv_DQv_sig2) - Q_sig2*Q_sig2/2*DD_var_sig2__bar) + \
           2*lmbda_N   *(Dv__DQv_N    + Q_N   *(DD_N_   -Dvarv_DQv_N   ) - Q_N   *Q_N   /2*DD_var_N__bar   )      # NB36/p2/(10)

    if flagOnlyE>0: return E,D_E,DD_E   # return error function E, gradient of E, and Hessian (compressed) of E 
    
    # ***************************************************************************************************************************************************************************
    # (PART III): store results in data dict dd  
    # ***************************************************************************************************************************************************************************
    # (III.i) store results of PART I (NB34) in data dict dd
    dd={}
    dd['alpha'],dd['beta'],dd['phi_alpha'],dd['phi_beta'] = alpha,beta,phi_alpha,phi_beta
    dd['f'],dd['d_f_DIV_d_mu'],dd['d_f_DIV_d_sig']                                = f,d_f_DIV_d_mu,d_f_DIV_d_sig
    dd['d2_f_DIV_d_mu_d_mu'],dd['d2_f_DIV_d_sig_d_sig'],dd['d2_f_DIV_d_mu_d_sig'] = d2_f_DIV_d_mu_d_mu,d2_f_DIV_d_sig_d_sig,d2_f_DIV_d_mu_d_sig
    dd['Z'],dd['d_Z_DIV_d_mu'],dd['d_Z_DIV_d_sig']                                = Z,d_Z_DIV_d_mu,d_Z_DIV_d_sig
    dd['d2_Z_DIV_d_mu_d_mu'],dd['d2_Z_DIV_d_sig_d_sig'],dd['d2_Z_DIV_d_mu_d_sig'] = d2_Z_DIV_d_mu_d_mu,d2_Z_DIV_d_sig_d_sig,d2_Z_DIV_d_mu_d_sig
    dd['gamma'],dd['d_gamma_DIV_d_mu'],dd['d_gamma_DIV_d_sig']                                = gamma,d_gamma_DIV_d_mu,d_gamma_DIV_d_sig
    dd['d2_gamma_DIV_d_mu_d_mu'],dd['d2_gamma_DIV_d_sig_d_sig'],dd['d2_gamma_DIV_d_mu_d_sig'] = d2_gamma_DIV_d_mu_d_mu,d2_gamma_DIV_d_sig_d_sig,d2_gamma_DIV_d_mu_d_sig
    dd['S'],dd['d_S_DIV_d_mu'],dd['d_S_DIV_d_sig']                                = S,d_S_DIV_d_mu,d_S_DIV_d_sig
    dd['d2_S_DIV_d_mu_d_mu'],dd['d2_S_DIV_d_sig_d_sig'],dd['d2_S_DIV_d_mu_d_sig'] = d2_S_DIV_d_mu_d_mu,d2_S_DIV_d_sig_d_sig,d2_S_DIV_d_mu_d_sig
    dd['F'],dd['d_F_DIV_d_mu'],dd['d_F_DIV_d_sig']                                = F,d_F_DIV_d_mu,d_F_DIV_d_sig
    dd['d2_F_DIV_d_mu_d_mu'],dd['d2_F_DIV_d_sig_d_sig'],dd['d2_F_DIV_d_mu_d_sig'] = d2_F_DIV_d_mu_d_mu,d2_F_DIV_d_sig_d_sig,d2_F_DIV_d_mu_d_sig
    dd['G'],dd['d_G_DIV_d_mu'],dd['d_G_DIV_d_sig']                                = G,d_G_DIV_d_mu,d_G_DIV_d_sig
    dd['d2_G_DIV_d_mu_d_mu'],dd['d2_G_DIV_d_sig_d_sig'],dd['d2_G_DIV_d_mu_d_sig'] = d2_G_DIV_d_mu_d_mu,d2_G_DIV_d_sig_d_sig,d2_G_DIV_d_mu_d_sig
    dd['mu_n_'],dd['d_mu_n__DIV_d_mu'],dd['d_mu_n__DIV_d_sig']                                = mu_n_,d_mu_n__DIV_d_mu,d_mu_n__DIV_d_sig
    dd['d2_mu_n__DIV_d_mu_d_mu'],dd['d2_mu_n__DIV_d_sig_d_sig'],dd['d2_mu_n__DIV_d_mu_d_sig'] = d2_mu_n__DIV_d_mu_d_mu,d2_mu_n__DIV_d_sig_d_sig,d2_mu_n__DIV_d_mu_d_sig
    dd['Ft'],dd['d_Ft_DIV_d_mu'],dd['d_Ft_DIV_d_sig']                                = Ft,d_Ft_DIV_d_mu,d_Ft_DIV_d_sig
    dd['d2_Ft_DIV_d_mu_d_mu'],dd['d2_Ft_DIV_d_sig_d_sig'],dd['d2_Ft_DIV_d_mu_d_sig'] = d2_Ft_DIV_d_mu_d_mu,d2_Ft_DIV_d_sig_d_sig,d2_Ft_DIV_d_mu_d_sig
    dd['M_n_'],dd['d_M_n__DIV_d_mu'],dd['d_M_n__DIV_d_sig']                                = M_n_,d_M_n__DIV_d_mu,d_M_n__DIV_d_sig
    dd['d2_M_n__DIV_d_mu_d_mu'],dd['d2_M_n__DIV_d_sig_d_sig'],dd['d2_M_n__DIV_d_mu_d_sig'] = d2_M_n__DIV_d_mu_d_mu,d2_M_n__DIV_d_sig_d_sig,d2_M_n__DIV_d_mu_d_sig

    # (III.ii) store results of PART II (NB36) in data dict dd
    dd['ix_mu'],dd['ix_sig2'],dd['ix_N']=ix_mu,ix_sig2,ix_N
    dd['ix_dd_mu_mu'],dd['ix_dd_sig2_sig2'],dd['ix_dd_N_N'],dd['ix_dd_mu_sig2'],dd['ix_dd_mu_N'],dd['ix_dd_sig2_N']=ix_dd_mu_mu,ix_dd_sig2_sig2,ix_dd_N_N,ix_dd_mu_sig2,ix_dd_mu_N,ix_dd_sig2_N
    dd['D_M1_'],dd['D_M2_'],dd['D_M3_'],dd['D_M4_'],dd['DD_M1_'],dd['DD_M2_'],dd['DD_M3_'],dd['DD_M4_']=D_M1_,D_M2_,D_M3_,D_M4_,DD_M1_,DD_M2_,DD_M3_,DD_M4_
    dd['D_M2_2'],dd['D_M1__M3_'],dd['D_M1_2_M2_'],dd['D_M1_4'],dd['DD_M2_2'],dd['DD_M1__M3_'],dd['DD_M1_2_M2_'],dd['DD_M1_4']=D_M2_2,D_M1__M3_,D_M1_2_M2_,D_M1_4,DD_M2_2,DD_M1__M3_,DD_M1_2_M2_,DD_M1_4
    dd['mu_'],dd['sig2_'],dd['N_'],dd['D_mu_'],dd['D_sig2_'],dd['D_N_'],dd['DD_mu_'],dd['DD_sig2_'],dd['DD_N_']=mu_,sig2_,N_,D_mu_,D_sig2_,D_N_,DD_mu_,DD_sig2_,DD_N_
    dd['var_mu__bar'],dd['var_N__bar'],dd['var_sig2__bar'],dd['D_var_mu__bar'],dd['DD_var_mu__bar']=var_mu__bar,var_N__bar,var_sig2__bar,D_var_mu__bar,DD_var_mu__bar
    dd['D_var_N__bar'],dd['DD_var_N__bar'],dd['D_var_sig2__bar'],dd['DD_var_sig2__bar']=D_var_N__bar,DD_var_N__bar,D_var_sig2__bar,DD_var_sig2__bar
    dd['eps_mu'],dd['eps_sig2'],dd['eps_N'],dd['E']=eps_mu,eps_sig2,eps_N,E
    dd['Q_mu'],dd['Q_sig2'],dd['Q_N'],dd['D_Q_mu'],dd['D_Q_sig2'],dd['D_Q_N'],dd['D_E']=Q_mu,Q_sig2,Q_N,D_Q_mu,D_Q_sig2,D_Q_N,D_E
    dd['Dv__DQv_mu'],dd['Dv__DQv_sig2'],dd['Dv__DQv_N']=Dv__DQv_mu,Dv__DQv_sig2,Dv__DQv_N
    dd['Dvarv_DQv_mu'],dd['Dvarv_DQv_sig2'],dd['Dvarv_DQv_N'],dd['DD_E']=Dvarv_DQv_mu,Dvarv_DQv_sig2,Dvarv_DQv_N,DD_E
    return dd

def getDerivatives4TruncatedGaussiansError_arr(mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu=1.0,lmbda_sig2=1.0,lmbda_N=1.0, flagOnlyE=1):
    """
    compute Gradient and Hessian of Truncated Gaussian Error Function (for Details see NB36)
    similar to previous function getDerivatives4TruncatedGaussiansError(.), but parameters mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar are assumed to be arrays of length NPAR,
    such that NPAR evaluations are computed at once  
    see also implementation from ~/hs-albsig/02-research/Borst_Fledermaeuse/python/checkParameterEstimationNB36.py
    :param mu  : array of expectations of original (non-truncated) Gaussian distribution (here used as model parameters to be optimized, see NB36/p1)
    :param sig2: array of variances of original (non-truncated) Gaussian distribution (here used as model parameters to be optimized, see NB36/p1)
    :param N   : array of sample numbers of original (non-truncated) Gaussian distributions (here used as model parameters to be optimized, see NB36/p1)
    :param a: array of lower bounds of truncation intervals (here used as model inputs, see NB36/p1)
    :param b: array of upper bounds of truncation intervals (here used as model inputs, see NB36/p1)
    :param mu__bar  : array of mean estimators of truncated Gaussian distributions as measured from data (here used as target values, see NB36/p1)
    :param sig2__bar: array of variance estimators of truncated Gaussian distributions as measured from data (here used as target values, see NB36/p1)
    :param N__bar   : array of numbers of samples of the original Gaussian distributions lying in the [a,b] interval as measured from data (here used as target values, see NB36/p1)
    :param lmbda_mu  : weight of the loss term w.r.t. model parameter mu
    :param lmbda_sig2: weight of the loss term w.r.t. model parameter sig2
    :param lmbda_N   : weight of the loss term w.r.t. model parameter N
    :param flagOnlyE: if >=0 then return only E,D_E,DD_E (i.e. error function, gradient, and hessian); otherwise return dict of all intermediary results
    """
    # ***************************************************************************************************************************************************************************
    # (PART I): Compute moments and their derivatives according to NB34   (copied from checkTruncatedGaussiansNB34.py, def getDerivatives_NB34_pp12(mu,sig,a,b,n,filter=None))
    # ***************************************************************************************************************************************************************************
    #assert N__bar>2,"N__bar="+str(N__bar)+"is too small!!!!!"
    NPAR=max([len(mu),len(sig2),len(N),len(a),len(b),len(mu__bar),len(sig2__bar),len(N__bar)])   # parameter number; assumes one dimensional arrays
    n=4                # we need raw moments up to order n=4 (for variance estimation NB35/p3/Satz3/(20); see also NB36/p3/(32),(36) 
    sig=np.sqrt(sig2)  # the formulas of NB34 are based on sig rather than sig2
    sig_inv=np.divide(1.0,sig)   # 1/sig
    sig2_inv=np.divide(1.0,sig2) # 1/sig^2
    
    # (I.i) auxiliary values (applying definitions from Satz 1 (p2) and Section 4 (p5) and Section 6 (p12)
    sqrt2_inv,sqrt2pi_inv=1.0/np.sqrt(2),1.0/np.sqrt(2.0*np.pi)
    alpha, beta = np.multiply(a-mu,sig_inv), np.multiply(b-mu,sig_inv)                     # NB34, p2, Satz 1
    Z = 0.5*(erf(beta*sqrt2_inv)-erf(alpha*sqrt2_inv))                                     # NB34, p2, Satz 1
    phi_alpha, phi_beta = np.exp(-0.5*np.multiply(alpha,alpha))*sqrt2pi_inv, np.exp(-0.5*np.multiply(beta,beta))*sqrt2pi_inv # NB34, p2, Satz 1
    #sig2=sig*sig   # sig^2     # not required as sig2 is given as parameter here (NB36)
    sig3_inv=np.multiply(sig2_inv,sig_inv)   # 1/sig^3
    Z_inv=np.divide(1.0,Z)           # 1/Z
    Z2_inv=np.multiply(Z_inv,Z_inv)  # 1/Z^2
    Z3_inv=np.multiply(Z2_inv,Z_inv) # 1/Z^3
    sigZ_inv=np.multiply(sig_inv,Z_inv) # 1/(sig*Z)
    sigi=np.ones((n+1,NPAR))                         # initialize sigi[0]=sig^0=1
    for i in range(1,n+1): sigi[i]=np.multiply(sigi[i-1],sig) # sigi[i]=sig^i
    mui=np.ones((n+1,NPAR))                          # initialize mui[0]=mu^0=1
    for i in range(1,n+1): mui[i]=np.multiply(mui[i-1],mu)    # sigi[i]=sig^i
    
    # (I.ii) compute the fj(alpha,beta):=beta^j*phi(beta)-alpha^j*phi(alpha) from NB34, p12, (6.25)
    f=np.zeros((n+5,NPAR))
    for j in range(max(n+5,7)):                       # for derivatives we need f[j] upto j=n+4 (see (6.32)) and a minimum of j=6 (see (6.45))
        if j==0: alphaj,betaj=np.ones(NPAR),np.ones(NPAR) # initialize alpha^j, beta^j
        else: alphaj,betaj=np.multiply(alphaj,alpha),np.multiply(betaj,beta)  # update alpha^j, beta^j
        f[j]=np.multiply(betaj,phi_beta)-np.multiply(alphaj,phi_alpha)        # NB34, p12, (6.25)

    # (I.iii) compute the derivatives of the fj(alpha,beta) from NB34, p12, (6.28)-(6.32)
    d_f_DIV_d_mu  = np.zeros((n+1,NPAR))
    d_f_DIV_d_sig = np.zeros((n+1,NPAR))
    d2_f_DIV_d_mu_d_mu   = np.zeros((n+1,NPAR))
    d2_f_DIV_d_sig_d_sig = np.zeros((n+1,NPAR))
    d2_f_DIV_d_mu_d_sig  = np.zeros((n+1,NPAR))
    for j in range(max(n+1,3)):              # for derivatives of gamma we need at least j=2 (see NB34, p13/(6.45))
        d_f_DIV_d_mu        [j]=np.multiply(f[j+1]-j*f[max(j-1,0)],sig_inv)   # NB34, p15/(6.63), p12/(6.28)
        d_f_DIV_d_sig       [j]=np.multiply(f[j+2]-j*f[j],sig_inv)            # NB34, p15/(6.64), p12/(6.29)
        d2_f_DIV_d_mu_d_mu  [j]=np.multiply(f[j+2]-(2*j+1)*f[j]+j*(j-1)*f[max(j-2,0)],sig2_inv) # NB34, p15/(6.65), p12/(6.30)
        d2_f_DIV_d_sig_d_sig[j]=np.multiply(f[j+4]-(2*j+3)*f[j+2]+j*(j+1)*f[j],sig2_inv)        # NB34, p15/(6.66), p12/(6.31)
        d2_f_DIV_d_mu_d_sig [j]=np.multiply(f[j+3]-(2*j+2)*f[j+1]+j*j*f[max(j-1,0)],sig2_inv)   # NB34, p15/(6.67), p12/(6.32)

    # (I.iv) compute gamma and the derivatives of Z and gamma (see NB34, p2/Satz 1, p10/(6.14), p8, p13
    gamma=np.multiply(f[0],Z_inv)           # NB34, p13/(6.42), p10/(6.14)
    gamma2=np.multiply(gamma,gamma)
    gammai=np.ones((n+1,NPAR))              # initialize gammai[0]=gamma^0=1
    for i in range(1,n+1): gammai[i]=np.multiply(gammai[i-1],gamma) # gammai[i]=gamma^i
    d_Z_DIV_d_mu =-np.multiply(f[0],sig_inv)  # NB34, p13/(6.35), p8/(4.41)
    d_Z_DIV_d_sig=-np.multiply(f[1],sig_inv)  # NB34, p13/(6.36), p8/(4.42)
    d2_Z_DIV_d_mu_d_mu   = -np.multiply(f[1],sig2_inv)         # NB34, p13/(6.37), p8/(4.43)
    d2_Z_DIV_d_sig_d_sig = np.multiply(2*f[1]-f[3],sig2_inv) # NB34, p13/(6.38), p8/(4.44)
    d2_Z_DIV_d_mu_d_sig  = np.multiply(f[0]-f[2],sig2_inv)   # NB34, p13/(6.39), p8/(4.45)
    d_gamma_DIV_d_mu =np.multiply(np.multiply(f[1],Z_inv)+gamma2,sig_inv)  # NB34, p13/(6.40)
    d_gamma_DIV_d_sig=np.multiply(f[2]+np.multiply(gamma,f[1]),sigZ_inv)   # NB34, p13/(6.41)
    d2_gamma_DIV_d_mu_d_mu  =np.multiply(d_f_DIV_d_mu[1]+np.multiply(f[1],np.multiply(gamma,sig_inv))+2*np.multiply(f[0],d_gamma_DIV_d_mu),sigZ_inv)                         # NB34, p13/(6.43)
    d2_gamma_DIV_d_sig_d_sig=np.multiply(d_f_DIV_d_sig[2]+np.multiply(gamma,d_f_DIV_d_sig[1])+np.multiply(d_gamma_DIV_d_sig,2*f[1]-Z),sigZ_inv)                              # NB34, p13/(6.44)
    d2_gamma_DIV_d_mu_d_sig =np.multiply(np.multiply(f[0],d_gamma_DIV_d_sig)+d_f_DIV_d_mu[2]+np.multiply(f[1],d_gamma_DIV_d_mu)+np.multiply(gamma,d_f_DIV_d_mu[1]),sigZ_inv) # NB34, p13/(6.45)

    # (I.v) compute double factorials for Sn and other variables
    doubfac=np.ones(n+1,dtype='int')  # initialize doubfac[0]=1, doubfac[1]=1
    for i in range(2,n+1): doubfac[i]=doubfac[i-2]*i    # n!!:=n*(n-2)!! = n*(n-2)*(n-4)*...*1
    
    # (I.vi) compute Sn and their derivatives (NB34, p12, p13)
    S=np.zeros((n+1,NPAR))
    d_S_DIV_d_mu=np.zeros((n+1,NPAR))
    d_S_DIV_d_sig=np.zeros((n+1,NPAR))
    d2_S_DIV_d_mu_d_mu=np.zeros((n+1,NPAR))
    d2_S_DIV_d_sig_d_sig=np.zeros((n+1,NPAR))
    d2_S_DIV_d_mu_d_sig=np.zeros((n+1,NPAR))
    for ni in range(n+1):
        if ni%2==0:        # ni even ...
            for k in range(ni//2):
                k2p1=2*k+1
                fac=doubfac[max(0,ni-1)]//doubfac[k2p1]                # fac := (ni-1)!! / (2k+1)!!
                S[ni] -= fac*f[2*k+1]                                  # NB34, p12/(6.24)
                d_S_DIV_d_mu [ni] -= fac*d_f_DIV_d_mu[k2p1]                # NB34, p13/(6.34)
                d_S_DIV_d_sig[ni] -= fac*d_f_DIV_d_sig[k2p1]               # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_mu  [ni] -= fac*d2_f_DIV_d_mu_d_mu[k2p1]   # NB34, p13/(6.34)
                d2_S_DIV_d_sig_d_sig[ni] -= fac*d2_f_DIV_d_sig_d_sig[k2p1] # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_sig [ni] -= fac*d2_f_DIV_d_mu_d_sig[k2p1]  # NB34, p13/(6.34)
            S[ni]+=doubfac[max(0,ni-1)]*Z                              # NB34, p12/(6.24)
            d_S_DIV_d_mu [ni]+=doubfac[max(0,ni-1)]*d_Z_DIV_d_mu       # NB34, p13/(6.34)
            d_S_DIV_d_sig[ni]+=doubfac[max(0,ni-1)]*d_Z_DIV_d_sig      # NB34, p13/(6.34)
            d2_S_DIV_d_mu_d_mu  [ni]+=doubfac[max(0,ni-1)]*d2_Z_DIV_d_mu_d_mu   # NB34, p13/(6.34)
            d2_S_DIV_d_sig_d_sig[ni]+=doubfac[max(0,ni-1)]*d2_Z_DIV_d_sig_d_sig # NB34, p13/(6.34)
            d2_S_DIV_d_mu_d_sig [ni]+=doubfac[max(0,ni-1)]*d2_Z_DIV_d_mu_d_sig  # NB34, p13/(6.34)
        else:              # ni odd ...
            for k in range((ni-1)//2+1):
                k2=2*k
                fac=doubfac[max(0,ni-1)]//doubfac[k2]      # fac := (ni-1)!! / (2k)!!
                S[ni] -= fac*f[k2]                         # NB34, p12/(6.24)
                d_S_DIV_d_mu [ni] -= fac*d_f_DIV_d_mu[k2]        # NB34, p13/(6.34)
                d_S_DIV_d_sig[ni] -= fac*d_f_DIV_d_sig[k2]       # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_mu  [ni] -= fac*d2_f_DIV_d_mu_d_mu[k2]   # NB34, p13/(6.34)
                d2_S_DIV_d_sig_d_sig[ni] -= fac*d2_f_DIV_d_sig_d_sig[k2] # NB34, p13/(6.34)
                d2_S_DIV_d_mu_d_sig [ni] -= fac*d2_f_DIV_d_mu_d_sig[k2]  # NB34, p13/(6.34)

    # (I.vii) compute Fij and Gi and their derivatives (NB34, p14)
    F=np.nan*np.ones((n+1,n+1,NPAR)) # allocate memory for F(i,j):=gamma^i*S_j, see NB34,p14/(6.46) (only needed for i+j<=n; mark remaining fields with NaN to recognized errors)
    d_F_DIV_d_mu,d_F_DIV_d_sig                                 =np.nan*np.ones((n+1,n+1,NPAR)),np.nan*np.ones((n+1,n+1,NPAR)) 
    d2_F_DIV_d_mu_d_mu,d2_F_DIV_d_sig_d_sig,d2_F_DIV_d_mu_d_sig=np.zeros((n+1,n+1,NPAR)),np.zeros((n+1,n+1,NPAR)),np.zeros((n+1,n+1,NPAR))
    G,d_G_DIV_d_mu,d_G_DIV_d_mu,d_G_DIV_d_sig                  =np.zeros((n+1,NPAR)),np.zeros((n+1,NPAR)),np.zeros((n+1,NPAR)),np.zeros((n+1,NPAR))  # allocate memory for G(i):=sigma^i / Z, see NB34,p14/(6.47)
    d2_G_DIV_d_mu_d_mu,d2_G_DIV_d_sig_d_sig,d2_G_DIV_d_mu_d_sig=np.zeros((n+1,NPAR)),np.zeros((n+1,NPAR)),np.zeros((n+1,NPAR))
    for i in range(n+1):
        G[i]=np.multiply(sigi[i],Z_inv)            # NB34,p14/(6.47)
        d_G_DIV_d_mu [i]=-np.multiply(np.multiply(sigi[i],Z2_inv),d_Z_DIV_d_mu)                          # NB34,p14/(6.53)
        d_G_DIV_d_sig[i]=-np.multiply(np.multiply(sigi[i],Z2_inv),d_Z_DIV_d_sig) + i*np.multiply(sigi[max(i-1,0)],Z_inv)  # NB34,p14/(6.54)
        d2_G_DIV_d_mu_d_mu  [i]=2*np.multiply(np.multiply(np.multiply(sigi[i],Z3_inv),d_Z_DIV_d_mu),d_Z_DIV_d_mu) - np.multiply(np.multiply(sigi[i],Z2_inv),d2_Z_DIV_d_mu_d_mu) # NB34,p14/(6.55)
        d2_G_DIV_d_sig_d_sig[i]=np.multiply(np.multiply(sigi[i],Z2_inv), 2*np.multiply(np.multiply(Z_inv,d_Z_DIV_d_sig),d_Z_DIV_d_sig)-d2_Z_DIV_d_sig_d_sig)\
                                 -2*i*np.multiply(np.multiply(sigi[max(i-1,0)],Z2_inv),d_Z_DIV_d_sig)\
                                 +i*(i-1)*np.multiply(sigi[max(i-2,0)],Z_inv)                                                                                      # NB34,p14/(6.56)
        d2_G_DIV_d_mu_d_sig [i]=np.multiply(np.multiply(sigi[i],Z2_inv), 2*np.multiply(np.multiply(Z_inv,d_Z_DIV_d_mu),d_Z_DIV_d_sig)-d2_Z_DIV_d_mu_d_sig)\
                                 -i*np.multiply(np.multiply(sigi[max(i-1,0)],Z2_inv),d_Z_DIV_d_mu)                                                                 # NB34,p14/(6.57)
        for j in range(n+1):
            if i+j<=n:
                F[i,j]=np.multiply(gammai[i],S[j])      # NB34,p14/(6.46)
                d_F_DIV_d_mu [i,j]=i*np.multiply(np.multiply(gammai[max(0,i-1)],d_gamma_DIV_d_mu ),S[j]) + np.multiply(gammai[i],d_S_DIV_d_mu [j])  # NB34,p14/(6.48)
                d_F_DIV_d_sig[i,j]=i*np.multiply(np.multiply(gammai[max(0,i-1)],d_gamma_DIV_d_sig),S[j]) + np.multiply(gammai[i],d_S_DIV_d_sig[j])  # NB34,p14/(6.49)
                d2_F_DIV_d_mu_d_mu  [i,j]=i*(i-1)*np.multiply(np.multiply(gammai[max(0,i-2)],d_gamma_DIV_d_mu),d_gamma_DIV_d_mu*S[j]) \
                                           + i*np.multiply(gammai[max(0,i-1)], np.multiply(d2_gamma_DIV_d_mu_d_mu,S[j])+2*np.multiply(d_gamma_DIV_d_mu,d_S_DIV_d_mu[j])) \
                                           + np.multiply(gammai[i],d2_S_DIV_d_mu_d_mu[j])                      # NB34,p14/(6.50)
                d2_F_DIV_d_sig_d_sig[i,j]=i*(i-1)*np.multiply(np.multiply(gammai[max(0,i-2)],d_gamma_DIV_d_sig),d_gamma_DIV_d_sig*S[j]) \
                                           + i*np.multiply(gammai[max(0,i-1)], np.multiply(d2_gamma_DIV_d_sig_d_sig,S[j])+2*np.multiply(d_gamma_DIV_d_sig,d_S_DIV_d_sig[j])) \
                                           + np.multiply(gammai[i],d2_S_DIV_d_sig_d_sig[j])                    # NB34,p14/(6.51)
                d2_F_DIV_d_mu_d_sig [i,j]=i*(i-1)*np.multiply(np.multiply(gammai[max(0,i-2)],d_gamma_DIV_d_mu ),d_gamma_DIV_d_sig*S[j]) \
                                           + i*np.multiply(gammai[max(0,i-1)], np.multiply(d2_gamma_DIV_d_mu_d_sig,S[j])+np.multiply(d_gamma_DIV_d_mu,d_S_DIV_d_sig[j])+np.multiply(d_gamma_DIV_d_sig,d_S_DIV_d_mu[j])) \
                                           + np.multiply(gammai[i],d2_S_DIV_d_mu_d_sig[j])                     # NB34,p14/(6.52)

    # (I.viii) compute central moments mu_n' and their derivatives (NB34, p12/(6.26), p15/(6.58a)
    n_fac=np.ones((n+1),'int')                          # initialize n_fac[0]=0!=1
    for ni in range(1,n+1): n_fac[ni]=ni*n_fac[ni-1]    # n_fac[ni]=ni!=ni*(ni-1)!=ni*n_fac[ni-1]
    n_choose_k = np.nan*np.ones((n+1,n+1),'int')        # initialize (n k) with nan (to recognize errors)
    for ni in range(n+1):
        for k in range(ni+1): n_choose_k[ni,k]=n_fac[ni]/(n_fac[k]*n_fac[ni-k])  # (ni k) := ni!/((ni-k)!*k!)
    mu_n_=np.zeros((n+1,NPAR))  # allocate memory for n-th central moment mu_n' of truncated Gaussian  (NB34, p12/(6.26), p15/(6.58a)
    d_mu_n__DIV_d_mu =np.zeros((n+1,NPAR))  # allocate memory 
    d_mu_n__DIV_d_sig=np.zeros((n+1,NPAR))  # allocate memory 
    d2_mu_n__DIV_d_mu_d_mu  =np.zeros((n+1,NPAR))  # allocate memory 
    d2_mu_n__DIV_d_sig_d_sig=np.zeros((n+1,NPAR))  # allocate memory 
    d2_mu_n__DIV_d_mu_d_sig =np.zeros((n+1,NPAR))  # allocate memory 
    for ni in range(n+1):
        for k in range(ni+1):
            d_mu_n__DIV_d_mu [ni] += n_choose_k[ni,k]*(np.multiply(d_G_DIV_d_mu [ni],F[ni-k,k])+np.multiply(G[ni],d_F_DIV_d_mu [ni-k,k]))     # NB34,p15/(6.58)
            d_mu_n__DIV_d_sig[ni] += n_choose_k[ni,k]*(np.multiply(d_G_DIV_d_sig[ni],F[ni-k,k])+np.multiply(G[ni],d_F_DIV_d_sig[ni-k,k]))     # NB34,p15/(6.59)            
            d2_mu_n__DIV_d_mu_d_mu  [ni] += n_choose_k[ni,k]*(np.multiply(d2_G_DIV_d_mu_d_mu[ni],F[ni-k,k])+2*np.multiply(d_G_DIV_d_mu[ni],d_F_DIV_d_mu[ni-k,k])\
                                                              +np.multiply(G[ni],d2_F_DIV_d_mu_d_mu[ni-k,k])) # NB34,p15/(6.60)
            d2_mu_n__DIV_d_sig_d_sig[ni] += n_choose_k[ni,k]*(np.multiply(d2_G_DIV_d_sig_d_sig[ni],F[ni-k,k])+2*np.multiply(d_G_DIV_d_sig[ni],d_F_DIV_d_sig[ni-k,k])\
                                                              +np.multiply(G[ni],d2_F_DIV_d_sig_d_sig[ni-k,k])) # NB34,p15/(6.61)
            d2_mu_n__DIV_d_mu_d_sig [ni] += n_choose_k[ni,k]*(np.multiply(d2_G_DIV_d_mu_d_sig[ni],F[ni-k,k])+np.multiply(d_G_DIV_d_mu[ni],d_F_DIV_d_sig[ni-k,k])\
                                                              +np.multiply(d_G_DIV_d_sig[ni],d_F_DIV_d_mu[ni-k,k])+np.multiply(G[ni],d2_F_DIV_d_mu_d_sig[ni-k,k])) # NB34,p15/(6.61)
            mu_n_[ni]+=n_choose_k[ni,k]*F[ni-k,k] # NB34,p15/(6.58a)
        mu_n_[ni]*=G[ni]                          # NB34,p15/(6.58a)
    
    # (I.ix) compute Fij_tilde and their derivatives (NB34, p15)
    Ft=np.nan*np.ones((n+1,n+1,NPAR)) # allocate memory for Ft(i,j):=F_tilde(i,j):=mu^i*sig^j*S_j, see NB34,p15/(6.68) (only needed for i+j<=n; mark remaining fields with NaN to recognized errors)
    d_Ft_DIV_d_mu,d_Ft_DIV_d_sig                                  =np.nan*np.ones((n+1,n+1,NPAR)),np.nan*np.ones((n+1,n+1,NPAR)) 
    d2_Ft_DIV_d_mu_d_mu,d2_Ft_DIV_d_sig_d_sig,d2_Ft_DIV_d_mu_d_sig=np.zeros((n+1,n+1,NPAR)),np.zeros((n+1,n+1,NPAR)),np.zeros((n+1,n+1,NPAR))
    for i in range(n+1):
        for j in range(n+1):
            if i+j<=n:
                Ft[i,j]=np.multiply(np.multiply(mui[i],sigi[j]),S[j])      # NB34,p15/(6.68)
                d_Ft_DIV_d_mu [i,j]=np.multiply(sigi[j], i*np.multiply(mui [max(0,i-1)],S[j])+np.multiply(mui [i],d_S_DIV_d_mu [j]))  # NB34,p15/(6.69)
                d_Ft_DIV_d_sig[i,j]=np.multiply(mui [i], j*np.multiply(sigi[max(0,j-1)],S[j])+np.multiply(sigi[j],d_S_DIV_d_sig[j]))  # NB34,p15/(6.70)
                d2_Ft_DIV_d_mu_d_mu  [i,j]=np.multiply(sigi[j], i*(i-1)*np.multiply(mui [max(0,i-2)],S[j])+2*i*np.multiply(mui [max(0,i-1)],d_S_DIV_d_mu [j])+np.multiply(mui [i],d2_S_DIV_d_mu_d_mu  [j])) # NB34,p15/(6.71)
                d2_Ft_DIV_d_sig_d_sig[i,j]=np.multiply(mui [i], j*(j-1)*np.multiply(sigi[max(0,j-2)],S[j])+2*j*np.multiply(sigi[max(0,j-1)],d_S_DIV_d_sig[j])+np.multiply(sigi[j],d2_S_DIV_d_sig_d_sig[j])) # NB34,p15/(6.72)
                d2_Ft_DIV_d_mu_d_sig [i,j]=j*np.multiply(sigi[max(0,j-1)], i*np.multiply(mui[max(0,i-1)],S[j])+np.multiply(mui[i],d_S_DIV_d_mu[j])) \
                                            + np.multiply(sigi[j], i*np.multiply(mui [max(0,i-1)],d_S_DIV_d_sig[j])+np.multiply(mui[i],d2_S_DIV_d_mu_d_sig[j]))  # NB34,p15/(6.73)

    # (I.x) compute raw moments M_n' and their derivatives (NB34, p12/(6.27), p15/(6.69), p16/(6.74)
    M_n_=np.zeros((n+1,NPAR))  # allocate memory for n-th raw moment M_n' of truncated Gaussian  (NB34, p12/(6.27), p15/(6.69), p16/(6.74)
    d_M_n__DIV_d_mu =np.zeros((n+1,NPAR))  # allocate memory 
    d_M_n__DIV_d_sig=np.zeros((n+1,NPAR))  # allocate memory 
    d2_M_n__DIV_d_mu_d_mu  =np.zeros((n+1,NPAR))  # allocate memory 
    d2_M_n__DIV_d_sig_d_sig=np.zeros((n+1,NPAR))  # allocate memory 
    d2_M_n__DIV_d_mu_d_sig =np.zeros((n+1,NPAR))  # allocate memory 
    for ni in range(n+1):
        for k in range(ni+1):
            d_M_n__DIV_d_mu [ni] += n_choose_k[ni,k]*(np.multiply(d_G_DIV_d_mu [0],Ft[ni-k,k])+np.multiply(G[0],d_Ft_DIV_d_mu [ni-k,k])) # NB34,p16/(6.75)
            d_M_n__DIV_d_sig[ni] += n_choose_k[ni,k]*(np.multiply(d_G_DIV_d_sig[0],Ft[ni-k,k])+np.multiply(G[0],d_Ft_DIV_d_sig[ni-k,k])) # NB34,p16/(6.76)
            d2_M_n__DIV_d_mu_d_mu  [ni] += n_choose_k[ni,k]*(np.multiply(d2_G_DIV_d_mu_d_mu[0],Ft[ni-k,k])+2*np.multiply(d_G_DIV_d_mu[0],d_Ft_DIV_d_mu[ni-k,k])+\
                                                             np.multiply(G[0],d2_Ft_DIV_d_mu_d_mu[ni-k,k]))                                                      # NB34,p16/(6.77)
            d2_M_n__DIV_d_sig_d_sig[ni] += n_choose_k[ni,k]*(np.multiply(d2_G_DIV_d_sig_d_sig[0],Ft[ni-k,k])+2*np.multiply(d_G_DIV_d_sig[0],d_Ft_DIV_d_sig[ni-k,k])+\
                                                             np.multiply(G[0],d2_Ft_DIV_d_sig_d_sig[ni-k,k]))                                                    # NB34,p16/(6.78)
            d2_M_n__DIV_d_mu_d_sig [ni] += n_choose_k[ni,k]*(np.multiply(d2_G_DIV_d_mu_d_sig[0],Ft[ni-k,k])+np.multiply(d_G_DIV_d_mu[0],d_Ft_DIV_d_sig[ni-k,k])+\
                                                             np.multiply(d_G_DIV_d_sig[0],d_Ft_DIV_d_mu[ni-k,k])+np.multiply(G[0],d2_Ft_DIV_d_mu_d_sig[ni-k,k])) # NB34,p16/(6.79)
            M_n_[ni] += n_choose_k[ni,k]*Ft[ni-k,k]          # NB34,p16/(6.74a)
        M_n_[ni]*=G[0]                                       # NB34,p16/(6.74a)

    # ***************************************************************************************************************************************************************************
    # (PART II): Include additional variables and derivatives for Error Function of Parameter Estimation (NB36) 
    # ***************************************************************************************************************************************************************************
    # (II.i) define indexes for variables and derivatives
    ix_mu,ix_sig2,ix_N = 0,1,2                                                                        # indexes of variables and 1st derivatives
    ix_dd_mu_mu, ix_dd_sig2_sig2, ix_dd_N_N, ix_dd_mu_sig2, ix_dd_mu_N, ix_dd_sig2_N = 0,1,2,3,4,5    # index of 2nd derivatives

    # (II.ii) compute derivatives of functions of raw moments (NB36/p3/(37-40))
    D_M1_ = np.array([d_M_n__DIV_d_mu[1], np.multiply(d_M_n__DIV_d_sig[1],0.5*sig_inv), np.zeros(NPAR)])  # first derivatives of M1_ (for derivatives w.r.t. sig2 use NB36/(14)
    D_M2_ = np.array([d_M_n__DIV_d_mu[2], np.multiply(d_M_n__DIV_d_sig[2],0.5*sig_inv), np.zeros(NPAR)])  # first derivatives of M2_ (for derivatives w.r.t. sig2 use NB36/(14)
    D_M3_ = np.array([d_M_n__DIV_d_mu[3], np.multiply(d_M_n__DIV_d_sig[3],0.5*sig_inv), np.zeros(NPAR)])  # first derivatives of M3_ (for derivatives w.r.t. sig2 use NB36/(14)
    D_M4_ = np.array([d_M_n__DIV_d_mu[4], np.multiply(d_M_n__DIV_d_sig[4],0.5*sig_inv), np.zeros(NPAR)])  # first derivatives of M4_ (for derivatives w.r.t. sig2 use NB36/(14)
    DD_M1_ = np.array([d2_M_n__DIV_d_mu_d_mu[1], np.multiply(d2_M_n__DIV_d_sig_d_sig[1],0.25*sig2_inv)-np.multiply(d_M_n__DIV_d_sig[1],0.25*sig3_inv), np.zeros(NPAR), \
                       np.multiply(d2_M_n__DIV_d_mu_d_sig[1],0.5*sig_inv), np.zeros(NPAR), np.zeros(NPAR)]) # 2nd deriv. of M1_; deriv. w.r.t. sig2 use NB36/(18),(14)
    DD_M2_ = np.array([d2_M_n__DIV_d_mu_d_mu[2], np.multiply(d2_M_n__DIV_d_sig_d_sig[2],0.25*sig2_inv)-np.multiply(d_M_n__DIV_d_sig[2],0.25*sig3_inv), np.zeros(NPAR), \
                       np.multiply(d2_M_n__DIV_d_mu_d_sig[2],0.5*sig_inv), np.zeros(NPAR), np.zeros(NPAR)]) # 2nd deriv. of M2_; deriv. w.r.t. sig2 use NB36/(18),(14)
    DD_M3_ = np.array([d2_M_n__DIV_d_mu_d_mu[3], np.multiply(d2_M_n__DIV_d_sig_d_sig[3],0.25*sig2_inv)-np.multiply(d_M_n__DIV_d_sig[3],0.25*sig3_inv), np.zeros(NPAR), \
                       np.multiply(d2_M_n__DIV_d_mu_d_sig[3],0.5*sig_inv), np.zeros(NPAR), np.zeros(NPAR)]) # 2nd deriv. of M3_; deriv. w.r.t. sig2 use NB36/(18),(14)
    DD_M4_ = np.array([d2_M_n__DIV_d_mu_d_mu[4], np.multiply(d2_M_n__DIV_d_sig_d_sig[4],0.25*sig2_inv)-np.multiply(d_M_n__DIV_d_sig[4],0.25*sig3_inv), np.zeros(NPAR), \
                       np.multiply(d2_M_n__DIV_d_mu_d_sig[4],0.5*sig_inv), np.zeros(NPAR), np.zeros(NPAR)]) # 2nd deriv. of M4_; deriv. w.r.t. sig2 use NB36/(18),(14)
    D_M2_2     = 2*np.multiply(M_n_[2],D_M2_)                                # NB36/(37)
    D_M1__M3_  = np.multiply(M_n_[3],D_M1_)+np.multiply(M_n_[1],D_M3_)       # NB36/(38)
    D_M1_2_M2_ = 2*np.multiply(np.multiply(M_n_[1],M_n_[2]),D_M1_) + np.multiply(np.multiply(M_n_[1],M_n_[1]),D_M2_)  # NB36/(39)
    D_M1_4     = 4*np.multiply(np.multiply(np.multiply(M_n_[1],M_n_[1]),M_n_[1]),D_M1_)                               # NB36/(40)
    D_M2_D_M2_  = np.array([np.multiply(D_M2_[0],D_M2_[0]), np.multiply(D_M2_[1],D_M2_[1]), np.multiply(D_M2_[2],D_M2_[2]), \
                            np.multiply(D_M2_[0],D_M2_[1]), np.multiply(D_M2_[0],D_M2_[2]), np.multiply(D_M2_[1],D_M2_[2])])  # product d_M2_/du*d_M2_/dw for NB36/p3/(41), term 1  
    D_M1_D_M3_  = np.array([np.multiply(D_M1_[0],D_M3_[0]), np.multiply(D_M1_[1],D_M3_[1]), np.multiply(D_M1_[2],D_M3_[2]), \
                            np.multiply(D_M1_[0],D_M3_[1]), np.multiply(D_M1_[0],D_M3_[2]), np.multiply(D_M1_[1],D_M3_[2])])  # product d_M1_/du*d_M3_/dw for NB36/p3/(42), term 2  
    D_M3_D_M1_  = np.array([np.multiply(D_M3_[0],D_M1_[0]), np.multiply(D_M3_[1],D_M1_[1]), np.multiply(D_M3_[2],D_M1_[2]), \
                            np.multiply(D_M3_[0],D_M1_[1]), np.multiply(D_M3_[0],D_M1_[2]), np.multiply(D_M3_[1],D_M1_[2])])  # product d_M3_/du*d_M1_/dw for NB36/p3/(42), term 3  
    D_M1_D_M1_  = np.array([np.multiply(D_M1_[0],D_M1_[0]), np.multiply(D_M1_[1],D_M1_[1]), np.multiply(D_M1_[2],D_M1_[2]), \
                            np.multiply(D_M1_[0],D_M1_[1]), np.multiply(D_M1_[0],D_M1_[2]), np.multiply(D_M1_[1],D_M1_[2])])  # product d_M1_/du*d_M1_/dw for NB36/p3/(43), term 1 and NB36/p3/(44), term 1  
    D_M1_D_M2_  = np.array([np.multiply(D_M1_[0],D_M2_[0]), np.multiply(D_M1_[1],D_M2_[1]), np.multiply(D_M1_[2],D_M2_[2]), \
                            np.multiply(D_M1_[0],D_M2_[1]), np.multiply(D_M1_[0],D_M2_[2]), np.multiply(D_M1_[1],D_M2_[2])])  # product d_M1_/du*d_M2_/dw for NB36/p3/(43), term 3  
    D_M2_D_M1_  = np.array([np.multiply(D_M2_[0],D_M1_[0]), np.multiply(D_M2_[1],D_M1_[1]), np.multiply(D_M2_[2],D_M1_[2]), \
                            np.multiply(D_M2_[0],D_M1_[1]), np.multiply(D_M2_[0],D_M1_[2]), np.multiply(D_M2_[1],D_M1_[2])])  # product d_M2_/du*d_M1_/dw for NB36/p3/(43), term 4  
    DD_M2_2     = 2*D_M2_D_M2_+2*np.multiply(M_n_[2],DD_M2_)                                                     # NB36/(41)
    DD_M1__M3_  = np.multiply(M_n_[3],DD_M1_)+D_M1_D_M3_+D_M3_D_M1_+np.multiply(M_n_[1],DD_M3_)                  # NB36/(42)
    DD_M1_2_M2_ = 2*np.multiply(M_n_[2], D_M1_D_M1_+np.multiply(M_n_[1],DD_M1_)) +2*np.multiply(M_n_[1],D_M1_D_M2_+D_M2_D_M1_) + np.multiply(np.multiply(M_n_[1],M_n_[1]),DD_M2_) # NB36/(43)
    DD_M1_4     = 12*np.multiply(np.multiply(M_n_[1],M_n_[1]),D_M1_D_M1_)+4*np.multiply(np.multiply(np.multiply(M_n_[1],M_n_[1]),M_n_[1]),DD_M1_)                                 # NB36/(44)
    
    # (II.iii) compute model predictions and their derivatives (NB36/p2/(12-25))
    mu_ = M_n_[1]            # expectation of truncated distribution corresponds to first raw moment
    sig2_ = mu_n_[2]         # variance of truncated distribution corresponds to second central moment
    N_=np.multiply(N,Z)      # expected number of samples that are in interval [a,b]
    D_mu_   = np.array([d_M_n__DIV_d_mu [1], np.multiply(d_M_n__DIV_d_sig [1],0.5*sig_inv), np.zeros(NPAR)])  # mu_ is 1st raw moment M_n_[1]; see also NB36/(21),(12),(14)
    D_sig2_ = np.array([d_mu_n__DIV_d_mu[2], np.multiply(d_mu_n__DIV_d_sig[2],0.5*sig_inv), np.zeros(NPAR)])  # sig2_ is 2nd central moment mu_n_[2]; see also NB36/(23),(12),(14),(18)
    D_N_    = np.array([np.multiply(N,d_Z_DIV_d_mu), np.multiply(np.multiply(N,d_Z_DIV_d_sig),0.5*sig_inv), Z])              # see NB36/(13),(15),(16)
    DD_mu_  = np.array([d2_M_n__DIV_d_mu_d_mu [1], np.multiply(d2_M_n__DIV_d_sig_d_sig [1],0.25*sig2_inv)-np.multiply(d_M_n__DIV_d_sig [1],0.25*sig3_inv), \
                        np.zeros(NPAR), np.multiply(d2_M_n__DIV_d_mu_d_sig [1],0.5*sig_inv), np.zeros(NPAR), np.zeros(NPAR)])  # mu_=M_n_[1]; see also NB36/(22),(12),(14),(18)
    DD_sig2_= np.array([d2_mu_n__DIV_d_mu_d_mu[2], np.multiply(d2_mu_n__DIV_d_sig_d_sig[2],0.25*sig2_inv)-np.multiply(d_mu_n__DIV_d_sig[2],0.25*sig3_inv), \
                        np.zeros(NPAR), np.multiply(d2_mu_n__DIV_d_mu_d_sig[2],0.5*sig_inv), np.zeros(NPAR), np.zeros(NPAR)])  # mu_=mu_n_[2]; see also NB36/(24),(12),(14),(18)
    DD_N_   = np.array([N*d2_Z_DIV_d_mu_d_mu, np.multiply(np.multiply(N,0.25*sig2_inv),d2_Z_DIV_d_sig_d_sig)-np.multiply(np.multiply(N,0.25*sig3_inv),d_Z_DIV_d_sig), \
                        np.zeros(NPAR), np.multiply(np.multiply(N,0.5*sig_inv),d2_Z_DIV_d_mu_d_sig), d_Z_DIV_d_mu, np.multiply(d_Z_DIV_d_sig,0.5*sig_inv)]) # see NB36/(17),(19),(20),(25abc)
    
    # (II.iv) compute variances and their derivatives (NB36/p3/(26-40))
    N__bar_inv=np.divide(1.0,N__bar)            # 1/N__bar
    N__bar_m1_inv=np.divide(1.0,N__bar-1)       # 1/(N__bar-1)
    var_mu__bar  =np.multiply(sig2_,N__bar_inv)       # NB36/(26a)
    var_N__bar   =np.multiply(np.multiply(N,Z),1-Z)   # NB36/(27a)
    var_sig2__bar=np.multiply(M_n_[4],N__bar_inv) - np.multiply(np.multiply(np.multiply(np.multiply(N__bar-3,N__bar_inv),N__bar_m1_inv),M_n_[2]),M_n_[2]) \
                   - 4*np.multiply(np.multiply(N__bar_inv,M_n_[1]),M_n_[3]) + 4*np.multiply(np.multiply(np.multiply(np.multiply(np.multiply(2*N__bar-3,N__bar_inv),N__bar_m1_inv),M_n_[1]),M_n_[1]),M_n_[2]) \
                   - 2*np.multiply(np.multiply(np.multiply(2*N__bar-3,N__bar_inv),N__bar_m1_inv),M_n_[1]**4) # NB36/(32); cf. NB35, p3, Satz 3; copied from checkVarianceNB35.py, def getVar4EVarEst_NB35_Satz3(n,M1,M2,M3,M4)
    D_var_mu__bar = np.multiply(D_sig2_,N__bar_inv)       # NB36/(26)
    DD_var_mu__bar = np.multiply(DD_sig2_,N__bar_inv)     # NB36/(26)
    D_var_N__bar = np.array([np.multiply(np.multiply(N,1-2*Z),d_Z_DIV_d_mu), np.multiply(np.multiply(np.multiply(N,1-2*Z),d_Z_DIV_d_sig),0.5*sig_inv), np.multiply(Z,1-Z)])  # NB36/(27),(14),(29)  
    DD_var_N__bar = np.array([np.multiply(N,np.multiply(1-2*Z,d2_Z_DIV_d_mu_d_mu)-2*np.multiply(d_Z_DIV_d_mu,d_Z_DIV_d_mu)), \
                              np.multiply(np.multiply(N,1-2*Z),np.multiply(d2_Z_DIV_d_sig_d_sig,0.25*sig2_inv)-np.multiply(d_Z_DIV_d_sig,0.25*sig3_inv))
                              -np.multiply(np.multiply(np.multiply(N*2,d_Z_DIV_d_sig),d_Z_DIV_d_sig),0.25*sig2_inv), \
                              np.zeros(NPAR),\
                              np.multiply(np.multiply(np.multiply(N,1-2*Z),d2_Z_DIV_d_mu_d_sig),0.5*sig_inv)-np.multiply(np.multiply(np.multiply(N*2,d_Z_DIV_d_mu),d_Z_DIV_d_sig),0.5*sig_inv),\
                              np.multiply(1-2*Z,d_Z_DIV_d_mu),\
                              np.multiply(np.multiply(1-2*Z,d_Z_DIV_d_sig),0.5*sig_inv)])  # NB36/(28),(31),(30),(14),(18)
    D_var_sig2__bar=np.multiply(D_M4_,N__bar_inv) - np.multiply(np.multiply(np.multiply(N__bar-3,N__bar_inv),N__bar_m1_inv),D_M2_2) \
                     - 4*np.multiply(N__bar_inv,D_M1__M3_) + 4*np.multiply(np.multiply(np.multiply(2*N__bar-3,N__bar_inv),N__bar_m1_inv),D_M1_2_M2_) \
                     - 2*np.multiply(np.multiply(np.multiply(2*N__bar-3,N__bar_inv),N__bar_m1_inv),D_M1_4)   # NB36/(35)
    DD_var_sig2__bar=np.multiply(DD_M4_,N__bar_inv) - np.multiply(np.multiply(np.multiply(N__bar-3,N__bar_inv),N__bar_m1_inv),DD_M2_2) \
                      - 4*np.multiply(N__bar_inv,DD_M1__M3_) + 4*np.multiply(np.multiply(np.multiply(2*N__bar-3,N__bar_inv),N__bar_m1_inv),DD_M1_2_M2_) \
                      - 2*np.multiply(np.multiply(np.multiply(2*N__bar-3,N__bar_inv),N__bar_m1_inv),DD_M1_4) # NB36/(35)

    # (II.v) compute error function and its derivatives (NB36/p1-2/(1)-(11)
    eps_mu   = mu_-mu__bar       # difference error of mu_ 
    eps_sig2 = sig2_-sig2__bar   # difference error of sig2_
    eps_N    = N_-N__bar         # difference error of N_
    var_mu__bar_inv  =np.divide(1.0,var_mu__bar)
    var_sig2__bar_inv=np.divide(1.0,var_sig2__bar)
    var_N__bar_inv   =np.divide(1.0,var_N__bar)
    E = lmbda_mu  *np.multiply(np.multiply(eps_mu  ,eps_mu  ),var_mu__bar_inv  ) + \
        lmbda_sig2*np.multiply(np.multiply(eps_sig2,eps_sig2),var_sig2__bar_inv) + \
        lmbda_N   *np.multiply(np.multiply(eps_N   ,eps_N   ),var_N__bar_inv   )   # loss function according to NB36/p1/(2)
    Q_mu   = np.multiply(eps_mu  ,var_mu__bar_inv)      # Qv from NB36/p2/(8) for v=mu
    Q_sig2 = np.multiply(eps_sig2,var_sig2__bar_inv)    # Qv from NB36/p2/(8) for v=sig2
    Q_N    = np.multiply(eps_N   ,var_N__bar_inv)       # Qv from NB36/p2/(8) for v=N
    #D_Q_mu   = (D_mu_  *var_mu__bar  -eps_mu  *D_var_mu__bar  )/(var_mu__bar  *var_mu__bar  )  # NB36/p2/(11)
    #D_Q_sig2 = (D_sig2_*var_sig2__bar-eps_sig2*D_var_sig2__bar)/(var_sig2__bar*var_sig2__bar)  # NB36/p2/(11)
    #D_Q_N    = (D_N_   *var_N__bar   -eps_N   *D_var_N__bar   )/(var_N__bar   *var_N__bar   )  # NB36/p2/(11)
    D_Q_mu   = np.multiply(D_mu_  -np.multiply(Q_mu,  D_var_mu__bar  ),var_mu__bar_inv)    # NB36/p2/(11), improved
    D_Q_sig2 = np.multiply(D_sig2_-np.multiply(Q_sig2,D_var_sig2__bar),var_sig2__bar_inv)  # NB36/p2/(11), improved
    D_Q_N    = np.multiply(D_N_   -np.multiply(Q_N,   D_var_N__bar   ),var_N__bar_inv)     # NB36/p2/(11), improved
    D_E = lmbda_mu   *np.multiply(Q_mu ,2*D_mu_  -np.multiply(Q_mu,D_var_mu__bar)) +\
          lmbda_sig2*np.multiply(Q_sig2,2*D_sig2_-np.multiply(Q_sig2,D_var_sig2__bar)) +\
          lmbda_N   *np.multiply(Q_N   ,2*D_N_   -np.multiply(Q_N   ,D_var_N__bar)) # NB36/p2/(9)
    Dv__DQv_mu   = np.array([np.multiply(D_mu_  [0],D_Q_mu  [0]), np.multiply(D_mu_  [1],D_Q_mu  [1]), np.multiply(D_mu_  [2],D_Q_mu  [2]), \
                             np.multiply(D_mu_  [0],D_Q_mu  [1]), np.multiply(D_mu_  [0],D_Q_mu  [2]), np.multiply(D_mu_  [1],D_Q_mu  [2])])  # d_v_/du*d_Qv/dw for v=mu, see NB36/p2/(10), term 1 in sum 
    Dv__DQv_sig2 = np.array([np.multiply(D_sig2_[0],D_Q_sig2[0]), np.multiply(D_sig2_[1],D_Q_sig2[1]), np.multiply(D_sig2_[2],D_Q_sig2[2]), \
                             np.multiply(D_sig2_[0],D_Q_sig2[1]), np.multiply(D_sig2_[0],D_Q_sig2[2]), np.multiply(D_sig2_[1],D_Q_sig2[2])])  # d_v_/du*d_Qv/dw for v=sig2, see NB36/p2/(10), term 1 in sum 
    Dv__DQv_N    = np.array([np.multiply(D_N_   [0],D_Q_N   [0]), np.multiply(D_N_   [1],D_Q_N   [1]), np.multiply(D_N_   [2],D_Q_N   [2]), \
                             np.multiply(D_N_   [0],D_Q_N   [1]), np.multiply(D_N_   [0],D_Q_N   [2]), np.multiply(D_N_   [1],D_Q_N   [2])])  # d_v_/du*d_Qv/dw for v=N, see NB36/p2/(10), term 1 in sum 
    Dvarv_DQv_mu   = np.array([np.multiply(D_var_mu__bar  [0],D_Q_mu  [0]), np.multiply(D_var_mu__bar  [1],D_Q_mu  [1]), \
                               np.multiply(D_var_mu__bar  [2],D_Q_mu  [2]), np.multiply(D_var_mu__bar  [0],D_Q_mu  [1]), \
                               np.multiply(D_var_mu__bar  [0],D_Q_mu  [2]), np.multiply(D_var_mu__bar  [1],D_Q_mu  [2])])  # d_var_v__bar/du*d_Qv/dw for v=mu, see NB36/p2/(10), term 3 in sum 
    Dvarv_DQv_sig2 = np.array([np.multiply(D_var_sig2__bar[0],D_Q_sig2[0]), np.multiply(D_var_sig2__bar[1],D_Q_sig2[1]), \
                               np.multiply(D_var_sig2__bar[2],D_Q_sig2[2]), np.multiply(D_var_sig2__bar[0],D_Q_sig2[1]), \
                               np.multiply(D_var_sig2__bar[0],D_Q_sig2[2]), np.multiply(D_var_sig2__bar[1],D_Q_sig2[2])])  # d_var_v__bar/du*d_Qv/dw for v=sig2, see NB36/p2/(10), term 3 in sum 
    Dvarv_DQv_N    = np.array([np.multiply(D_var_N__bar   [0],D_Q_N   [0]), np.multiply(D_var_N__bar   [1],D_Q_N   [1]), \
                               np.multiply(D_var_N__bar   [2],D_Q_N   [2]), np.multiply(D_var_N__bar   [0],D_Q_N   [1]), \
                               np.multiply(D_var_N__bar   [0],D_Q_N   [2]), np.multiply(D_var_N__bar   [1],D_Q_N   [2])])  # d_var_v__bar/du*d_Qv/dw for v=N, see NB36/p2/(10), term 3 in sum 
    DD_E = 2*lmbda_mu  *(Dv__DQv_mu   + np.multiply(Q_mu  ,DD_mu_  -Dvarv_DQv_mu  ) - 0.5*np.multiply(np.multiply(Q_mu  ,Q_mu  ),DD_var_mu__bar  )) + \
           2*lmbda_sig2*(Dv__DQv_sig2 + np.multiply(Q_sig2,DD_sig2_-Dvarv_DQv_sig2) - 0.5*np.multiply(np.multiply(Q_sig2,Q_sig2),DD_var_sig2__bar)) + \
           2*lmbda_N   *(Dv__DQv_N    + np.multiply(Q_N   ,DD_N_   -Dvarv_DQv_N   ) - 0.5*np.multiply(np.multiply(Q_N   ,Q_N   ),DD_var_N__bar   ))      # NB36/p2/(10)

    if flagOnlyE>0: return E,D_E,DD_E   # return error function E, gradient of E, and Hessian (compressed) of E 
    
    # ***************************************************************************************************************************************************************************
    # (PART III): store results in data dict dd  
    # ***************************************************************************************************************************************************************************
    # (III.i) store results of PART I (NB34) in data dict dd
    dd={}
    dd['alpha'],dd['beta'],dd['phi_alpha'],dd['phi_beta'] = alpha,beta,phi_alpha,phi_beta
    dd['f'],dd['d_f_DIV_d_mu'],dd['d_f_DIV_d_sig']                                = f,d_f_DIV_d_mu,d_f_DIV_d_sig
    dd['d2_f_DIV_d_mu_d_mu'],dd['d2_f_DIV_d_sig_d_sig'],dd['d2_f_DIV_d_mu_d_sig'] = d2_f_DIV_d_mu_d_mu,d2_f_DIV_d_sig_d_sig,d2_f_DIV_d_mu_d_sig
    dd['Z'],dd['d_Z_DIV_d_mu'],dd['d_Z_DIV_d_sig']                                = Z,d_Z_DIV_d_mu,d_Z_DIV_d_sig
    dd['d2_Z_DIV_d_mu_d_mu'],dd['d2_Z_DIV_d_sig_d_sig'],dd['d2_Z_DIV_d_mu_d_sig'] = d2_Z_DIV_d_mu_d_mu,d2_Z_DIV_d_sig_d_sig,d2_Z_DIV_d_mu_d_sig
    dd['gamma'],dd['d_gamma_DIV_d_mu'],dd['d_gamma_DIV_d_sig']                                = gamma,d_gamma_DIV_d_mu,d_gamma_DIV_d_sig
    dd['d2_gamma_DIV_d_mu_d_mu'],dd['d2_gamma_DIV_d_sig_d_sig'],dd['d2_gamma_DIV_d_mu_d_sig'] = d2_gamma_DIV_d_mu_d_mu,d2_gamma_DIV_d_sig_d_sig,d2_gamma_DIV_d_mu_d_sig
    dd['S'],dd['d_S_DIV_d_mu'],dd['d_S_DIV_d_sig']                                = S,d_S_DIV_d_mu,d_S_DIV_d_sig
    dd['d2_S_DIV_d_mu_d_mu'],dd['d2_S_DIV_d_sig_d_sig'],dd['d2_S_DIV_d_mu_d_sig'] = d2_S_DIV_d_mu_d_mu,d2_S_DIV_d_sig_d_sig,d2_S_DIV_d_mu_d_sig
    dd['F'],dd['d_F_DIV_d_mu'],dd['d_F_DIV_d_sig']                                = F,d_F_DIV_d_mu,d_F_DIV_d_sig
    dd['d2_F_DIV_d_mu_d_mu'],dd['d2_F_DIV_d_sig_d_sig'],dd['d2_F_DIV_d_mu_d_sig'] = d2_F_DIV_d_mu_d_mu,d2_F_DIV_d_sig_d_sig,d2_F_DIV_d_mu_d_sig
    dd['G'],dd['d_G_DIV_d_mu'],dd['d_G_DIV_d_sig']                                = G,d_G_DIV_d_mu,d_G_DIV_d_sig
    dd['d2_G_DIV_d_mu_d_mu'],dd['d2_G_DIV_d_sig_d_sig'],dd['d2_G_DIV_d_mu_d_sig'] = d2_G_DIV_d_mu_d_mu,d2_G_DIV_d_sig_d_sig,d2_G_DIV_d_mu_d_sig
    dd['mu_n_'],dd['d_mu_n__DIV_d_mu'],dd['d_mu_n__DIV_d_sig']                                = mu_n_,d_mu_n__DIV_d_mu,d_mu_n__DIV_d_sig
    dd['d2_mu_n__DIV_d_mu_d_mu'],dd['d2_mu_n__DIV_d_sig_d_sig'],dd['d2_mu_n__DIV_d_mu_d_sig'] = d2_mu_n__DIV_d_mu_d_mu,d2_mu_n__DIV_d_sig_d_sig,d2_mu_n__DIV_d_mu_d_sig
    dd['Ft'],dd['d_Ft_DIV_d_mu'],dd['d_Ft_DIV_d_sig']                                = Ft,d_Ft_DIV_d_mu,d_Ft_DIV_d_sig
    dd['d2_Ft_DIV_d_mu_d_mu'],dd['d2_Ft_DIV_d_sig_d_sig'],dd['d2_Ft_DIV_d_mu_d_sig'] = d2_Ft_DIV_d_mu_d_mu,d2_Ft_DIV_d_sig_d_sig,d2_Ft_DIV_d_mu_d_sig
    dd['M_n_'],dd['d_M_n__DIV_d_mu'],dd['d_M_n__DIV_d_sig']                                = M_n_,d_M_n__DIV_d_mu,d_M_n__DIV_d_sig
    dd['d2_M_n__DIV_d_mu_d_mu'],dd['d2_M_n__DIV_d_sig_d_sig'],dd['d2_M_n__DIV_d_mu_d_sig'] = d2_M_n__DIV_d_mu_d_mu,d2_M_n__DIV_d_sig_d_sig,d2_M_n__DIV_d_mu_d_sig

    # (III.ii) store results of PART II (NB36) in data dict dd
    dd['ix_mu'],dd['ix_sig2'],dd['ix_N']=ix_mu,ix_sig2,ix_N
    dd['ix_dd_mu_mu'],dd['ix_dd_sig2_sig2'],dd['ix_dd_N_N'],dd['ix_dd_mu_sig2'],dd['ix_dd_mu_N'],dd['ix_dd_sig2_N']=ix_dd_mu_mu,ix_dd_sig2_sig2,ix_dd_N_N,ix_dd_mu_sig2,ix_dd_mu_N,ix_dd_sig2_N
    dd['D_M1_'],dd['D_M2_'],dd['D_M3_'],dd['D_M4_'],dd['DD_M1_'],dd['DD_M2_'],dd['DD_M3_'],dd['DD_M4_']=D_M1_,D_M2_,D_M3_,D_M4_,DD_M1_,DD_M2_,DD_M3_,DD_M4_
    dd['D_M2_2'],dd['D_M1__M3_'],dd['D_M1_2_M2_'],dd['D_M1_4'],dd['DD_M2_2'],dd['DD_M1__M3_'],dd['DD_M1_2_M2_'],dd['DD_M1_4']=D_M2_2,D_M1__M3_,D_M1_2_M2_,D_M1_4,DD_M2_2,DD_M1__M3_,DD_M1_2_M2_,DD_M1_4
    dd['mu_'],dd['sig2_'],dd['N_'],dd['D_mu_'],dd['D_sig2_'],dd['D_N_'],dd['DD_mu_'],dd['DD_sig2_'],dd['DD_N_']=mu_,sig2_,N_,D_mu_,D_sig2_,D_N_,DD_mu_,DD_sig2_,DD_N_
    dd['var_mu__bar'],dd['var_N__bar'],dd['var_sig2__bar'],dd['D_var_mu__bar'],dd['DD_var_mu__bar']=var_mu__bar,var_N__bar,var_sig2__bar,D_var_mu__bar,DD_var_mu__bar
    dd['D_var_N__bar'],dd['DD_var_N__bar'],dd['D_var_sig2__bar'],dd['DD_var_sig2__bar']=D_var_N__bar,DD_var_N__bar,D_var_sig2__bar,DD_var_sig2__bar
    dd['eps_mu'],dd['eps_sig2'],dd['eps_N'],dd['E']=eps_mu,eps_sig2,eps_N,E
    dd['Q_mu'],dd['Q_sig2'],dd['Q_N'],dd['D_Q_mu'],dd['D_Q_sig2'],dd['D_Q_N'],dd['D_E']=Q_mu,Q_sig2,Q_N,D_Q_mu,D_Q_sig2,D_Q_N,D_E
    dd['Dv__DQv_mu'],dd['Dv__DQv_sig2'],dd['Dv__DQv_N']=Dv__DQv_mu,Dv__DQv_sig2,Dv__DQv_N
    dd['Dvarv_DQv_mu'],dd['Dvarv_DQv_sig2'],dd['Dvarv_DQv_N'],dd['DD_E']=Dvarv_DQv_mu,Dvarv_DQv_sig2,Dvarv_DQv_N,DD_E
    return dd

def estimateGaussParametersFromTruncatedGaussians(mu_est, sig2_est, N_est, a, b, mu__bar, sig2__bar, N__bar, lmbda_mu=1.0, lmbda_sig2=1.0, lmbda_N=1.0, tau_max=50,
                                                  mumin=None,mumax=None, sig2min=None,sig2max=None, Nmin=None,Nmax=None,
                                                  epsNablaE=1e-8,E_ok=3,tau_ok=3):
    """
    Estimate Gaussian Parameters From Truncated Gaussian Data Distribution
    Works parallel on multiple estimates, that is, mu_est,sig2_est,N_est are arrays of length len_est
    For each estimation i in range(len_est), error function E is defined as sum of n_ab terms, i.e., a,b,mu__bar,sig2__bar,N__bar are arrays of length n_ab
    :param mu_est    : 1D array (size len_est) of initial estimations of mean value of Gaussian (e.g., initialize with mode of data distribution)
    :param sig2_est  : 1D array (size len_est) of initial estimations of variance of Gaussian (e.g., initialize from complete data distribution; or from mode)
    :param N_est     : 1D array (size len_est) of initial estimations of data number (e.g., use total data number)
    :param a         : 1D array (size n_ab) of left bounds of truncation interval
    :param b         : 1D array (size n_ab) of right bounds of truncation interval
    :param mu__bar   : 1D array (size n_ab) of empirical truncated means        (estimated from truncated data distribution) 
    :param sig2__bar : 1D array (size n_ab) of empirical truncated variances    (estimated from truncated data distribution) 
    :param N__bar    : 1D array (size n_ab) of empirical truncated data numbers (estimated from truncated data distribution) 
    :param lmbda_mu  : weight of the loss term w.r.t. model parameter mu
    :param lmbda_sig2: weight of the loss term w.r.t. model parameter sig2
    :param lmbda_N   : weight of the loss term w.r.t. model parameter N
    :param mumin     : lower bound for mean (default: min(mu_est-3*sig_est))
    :param maxmax    : upper bound for mean (default: min(mu_est+3*sig_est)) 
    :param sig2min   : lower bound for variance (default: largest measured truncated variance sig2__bar)
    :param sig2max   : upper bound for variance (default: max. initialization value of sig2_est, assuming that this is total data variance)
    :param Nmin      : lower bound for noise data number (default: minimum of N__bar) 
    :param Nmax      : upper bound for noise data number (default: N_est, assuming that N_est is initialized with total data number) 
    :param epsNablaE : if maximum of nablaE is below epsNablaE, then terminate optimization (as optimum is reached)
    :param E_ok      : break optimization loop if E<=E_ok is reached
    :param tau_ok    : if E<=E_ok is reached but NablaE is not yet below epsNablaE (not yet converged) then add additional tau_ok optimization steps (to hope for further convergence)
    """

    # (i) set valid intervals for truncated Gaussian parameters mu, sig2, N to be estimated
    if mumin is None: mumin=np.min(mu_est-3*np.sqrt(sig2_est))
    if mumax is None: mumax=np.max(mu_est+3*np.sqrt(sig2_est))
    if sig2min is None: sig2min=np.min(sig2__bar)
    if sig2max is None: sig2max=np.max(sig2_est)
    if Nmin is None: Nmin=np.min(N__bar)
    if Nmax is None: Nmax=np.max(N_est)

    # (ii) check if parameters have valid shapes, and allocate auxiliary arrays (for layout of arrays, see AB5/p9/25.4.2023)
    assert np.min(N__bar)>2,"Values of N__bar must be >2, but N__bar="+str(N__bar)
    len_est,n_ab=mu_est.shape[0],a.shape[0]    # length of 1D arrays
    n_ab_inv=1.0/n_ab                          # inverse of n_ab
    assert len(mu_est.shape)==1 and len(sig2_est.shape)==1 and len(N_est.shape)==1 and sig2_est.shape[0]==len_est and N_est.shape[0]==len_est, "mu_est, sig2_est, and N_est must be 1D arrays of same length "+\
        "len_est="+str(len_est)+", but mu_est.shape="+str(mu_est.shape)+", sig2_est.shape="+str(sig2_est.shape)+", N_est.shape="+str(N_est.shape) 
    assert len(a.shape)==1 and len(b.shape)==1 and len(mu__bar.shape)==1 and len(sig2__bar.shape)==1 and len(N__bar.shape)==1 and b.shape[0]==n_ab and mu__bar.shape[0]==n_ab and sig2__bar.shape[0]==n_ab, "a, b, "+\
        "mu__bar, sig2__bar, and N__bar must be 1D arrays of same length n_ab="+str(n_ab)+", but "+\
        "a.shape="+str(a.shape)+", b.shape="+str(b.shape)+", mu__bar.shape="+str(mu__bar.shape)+", sig2__bar.shape="+str(sig2__bar.shape)+", N__bar.shape="+str(N__bar.shape)
    sum_lmbda_v_inv = 1.0/(lmbda_mu+lmbda_sig2+lmbda_N)     # factor for normalizing lmbda_mu/sig2/N such that sum of weights lmbda_v is 1  (such that E becomes interpretable as mean errors normalized to s.d.)
    lmbda_mu  *=sum_lmbda_v_inv    # normalize 
    lmbda_sig2*=sum_lmbda_v_inv    # normalize 
    lmbda_N   *=sum_lmbda_v_inv    # normalize 
    len_all    =len_est*n_ab     # total 1D-array length (used for calling getDerivatives4TruncatedGaussiansError_arr(.)) 
    shape_all  =(len_est,n_ab)   # total 2D-array shape (each row correponds to a separate parameter estimation set; correpsonding to the summands of the error function corresponding to differenct [a,b] intervals)
    shape_all_T=(n_ab,len_est)   # transposed shape_all
    mu_est, sig2_est, N_est      = (np.ones(shape_all_T)*mu_est).T, (np.ones(shape_all_T)*sig2_est).T, (np.ones(shape_all_T)*N_est).T   # expand to 2D arrays, where mu_est, sig2_est, N_est are placed in columns
    a,b,mu__bar,sig2__bar,N__bar = np.ones(shape_all)*a, np.ones(shape_all)*b, np.ones(shape_all)*mu__bar, np.ones(shape_all)*sig2__bar, np.ones(shape_all)*N__bar # expand to 2D arrays, where a,b,*__bar are placed in rows
    E_best =1e50*np.ones((len_est))       # E_best       [i] is smallest error value for i-th parameter setting (minimized over time step tau); init with very large value
    DE_best=1e50*np.ones((3,len_est))     # DE_best      [:,i] is gradient for smallest error value E_best[i] for i-th parameter setting (optimized over time step tau); init with very large value
    DDE_best=-np.ones((6,len_est))        # DDE_best     [:,i] is hessian  for smallest error value E_best[i] for i-th parameter setting (optimized over time step tau)
    mu_est_best  =np.zeros((len_est))     # mu_est_best  [i] is mu_est   for smallest error value E_best[i] for i-th parameter setting (optimized over time step tau)
    sig2_est_best=np.zeros((len_est))     # sig2_est_best[i] is sig2_est for smallest error value E_best[i] for i-th parameter setting (optimized over time step tau)
    N_est_best   =np.zeros((len_est))     # N_est_best   [i] is N_est    for smallest error value E_best[i] for i-th parameter setting (optimized over time step tau)
    tau_best     =np.zeros((len_est),'int') # tau_best   [i] is time step tau where minimal error E_best[i] has occured ; init with zero
    idx_ok_bool=np.array(len_est*[True])    # idx_ok[i]==True means that parameter set i should be further optimized in while-loop; init all indexes with True/ok
    idx_ok = np.array(range(len_est),'int') # integer indexes corresponding to idx_ok_bool
    tau_E_ok=tau_max                      # first time where E<=E_ok has been reached (init with -1 means E<=E_ok has not yet been reached)
    
    # (iii) main Newton optimization loop 
    tau=0
    while tau<tau_max and tau<tau_E_ok+tau_ok:
        tau=tau+1         # increment optimization step counter

        # (iii.a) get indexes idx_ok of parameter settings that still have to be optimized
        len_est_ok=len(idx_ok)            # how many indexes are ok (or how many parameter settings still have to be optimized?)
        if len_est_ok==0: break           # if no indexes are ok then break while loop, and optimization has finished
        len_all_ok=len_est_ok*n_ab
        shape_all_ok=(len_est_ok,n_ab)

        # (iii.b) compute error and derivatives for given parameter settings
        E,DE,DDE = getDerivatives4TruncatedGaussiansError_arr(mu_est[idx_ok].reshape(len_all_ok),sig2_est[idx_ok].reshape(len_all_ok),N_est[idx_ok].reshape(len_all_ok),\
                                                              a[idx_ok].reshape(len_all_ok),b[idx_ok].reshape(len_all_ok),\
                                                              mu__bar[idx_ok].reshape(len_all_ok),sig2__bar[idx_ok].reshape(len_all_ok),N__bar[idx_ok].reshape(len_all_ok),\
                                                              lmbda_mu,lmbda_sig2,lmbda_N)  # compute error terms and derivatives
        E  =np.sum(E  .reshape(shape_all_ok),axis=1)*n_ab_inv       # mean over the error terms corresponding to differenct [a,b] intervals; result will be 1D array of size len_est 
        DE =np.sum(DE .reshape((3,)+shape_all_ok),axis=2)*n_ab_inv  # gradient of E (sum over the error terms corresponding to differenct [a,b] intervals; result is 2D array of size 3 x len_est)
        DDE=np.sum(DDE.reshape((6,)+shape_all_ok),axis=2)*n_ab_inv  # Hessian of E (over the error terms corresponding to different [a,b] intervals; result is 2D array of size 6 x len_est)
         
        # (iii.c) update best error and parameter settings
        idx_resbetter = np.logical_and(np.isfinite(E),E<E_best[idx_ok])  # selected (within scope of idx_ok) parameter settings whre new error E is still finite and is an improvement over previous E
        idx_better = idx_ok[idx_resbetter]                          # indexes in parameter setting arrays where improvement has happened
        E_best    [idx_better]=E[idx_resbetter]                     # update E_best (error terms)
        DE_best [:,idx_better]=DE [:,idx_resbetter]                 # update DE_best (gradients)
        DDE_best[:,idx_better]=DDE[:,idx_resbetter]                 # update DDE_best (hessians)
        mu_est_best  [idx_better]=mu_est  [idx_better,0]            # take over improved parameter mu_est   (remember: parameters mu_est   has values in columns)
        sig2_est_best[idx_better]=sig2_est[idx_better,0]            # take over improved parameter sig2_est (remember: parameters sig2_est has values in columns)
        N_est_best   [idx_better]=N_est   [idx_better,0]            # take over improved parameter N_est    (remember: parameters N_est    has values in columns)
        tau_best[idx_better]=tau
        
        # (iii.d) check for early convergence to break while loop
        idx_best=np.argmin(E_best)              # index of (currently) best parameter setting
        if E_best[idx_best]<=E_ok:              # below required error bound?
            if tau<tau_E_ok: tau_E_ok=tau       # start final additional optimization steps, if not yet happened (tau_E_ok is first time step where E<=E_ok holds)
            if np.max(np.abs(DE_best[:,idx_best]))<=epsNablaE: break   # if nablaE of best parameter setting is below bound (i.e., has converged) then break while-loop immediately
        
        # (iii.e) make Newton update step of parameters
        DDE_inv,det_DDE = inv3sym_arr(DDE)
        dpar = -mult3sym_arr(DDE_inv,DE)

        mu_est  [idx_ok]+=dpar[0].reshape((len_est_ok,1))
        sig2_est[idx_ok]+=dpar[1].reshape((len_est_ok,1))
        N_est   [idx_ok]+=dpar[2].reshape((len_est_ok,1))
        mu_est  [idx_ok]=np.maximum(np.minimum(mu_est  [idx_ok],mumax  ),mumin  )
        sig2_est[idx_ok]=np.maximum(np.minimum(sig2_est[idx_ok],sig2max),sig2min)
        N_est   [idx_ok]=np.maximum(np.minimum(N_est   [idx_ok],Nmax   ),Nmin   )

        # (iii.f) update indexes that correspond to parameters that are ok (not diverged/NAN and non converged)
        idx_ok_bool[idx_ok] = np.logical_and( np.logical_and( np.isfinite(mu_est[idx_ok,0]), np.isfinite(sig2_est[idx_ok,0])), np.isfinite(N_est[idx_ok,0])) # indexes (from 0...len_est) where all parameters are ok
        idx_ok_bool[idx_ok] = np.logical_and( np.logical_and( idx_ok_bool[idx_ok], np.isfinite(E_best[idx_ok])), \
                                              np.sum(np.isfinite(DE_best[:,idx_ok]),axis=0)==3, np.sum(np.isfinite(DDE_best[:,idx_ok]),axis=0)==6) # require additionally that all derivatives are ok
        idx_ok_bool[idx_ok] = np.logical_and( idx_ok_bool[idx_ok], np.max(np.abs(DE_best[:,idx_ok]),axis=0)>epsNablaE) # require also that optimization has not yet converged
        idx_ok=idx_ok[idx_ok_bool[idx_ok]]    # update idx_ok
        

    # (iv) finalize results
    idx_best=np.argmin(E_best)              # index of best parameter setting
    res={}                                  # dict of results
    res['mu_est_best'  ]=mu_est_best
    res['sig2_est_best']=sig2_est_best
    res['N_est_best'   ]=N_est_best
    res['E_best'       ]=E_best
    res['DE_best'      ]=DE_best
    res['DDE_best'     ]=DDE_best
    res['tau_best'     ]=tau_best
    res['idx_best'     ]=idx_best
    res['tau'          ]=tau
    return res # return results  

def getModeOfDensity(x,binsize=10,p_cutoff=0,x_sorted=None):
    """
    get mode of data x (i.e. location of maximal density):
    - data x is sorted
    - data mass p of minimal / maximal values is cut off symmetrically (to get rid of outliers)
    - data is divided into bins of equal element numbers 
    - for each bin density is computed (#elements/(max-min))
    - central location of bin having maximal density is returned
    python code taken from ~/hs-albsig/02-research/Borst_Fledermaeuse/python/ivisit_testSignalDetNB36.py, 15/4/2023
    :param x: 1D data array 
    :param binsize: number of elements per bin
    :param p_cutoff: initially, cut off fraction of minimal/maximal values from x; e.g., p_cutoff=0.5 cuts off 25% of largest and 25% of smallest data
    :param x_sorted: sorted x (if available; if None, x will be sorted)
    :return mode,p_mode: location (center of bin) and value of maximal density
    :return bin_centers,bin_density,bin_widths: bin centers, corresponding probability density, and corresponding bin widths
    """
    if x_sorted is None: x_sorted=np.sort(x)  # work on sorted data array
    n=len(x_sorted)                           # length of data array
    if p_cutoff>0:
        idx1=int(np.floor(n*0.5*p_cutoff))
        idx2=int(np.ceil(n*(1.0-0.5*p_cutoff)))
        x_sorted=x_sorted[idx1:idx2]          # crop central portion of data array x having probability mass (1-p_cutoff)
        n=len(x_sorted)
    assert n>0,"getModeOfDensity: n="+str(n)+" must be positive!"
    idx1=(n%binsize)//2
    bin_borders=x_sorted[range(idx1,n,binsize)]
    bin_widths=bin_borders[1:]-bin_borders[0:-1]
    bin_density=np.divide(binsize/float(n),bin_widths)
    bin_centers=0.5*(bin_borders[1:]+bin_borders[0:-1])
    imax=np.argmax(bin_density)
    mode=bin_centers[imax] 
    p_mode=bin_density[imax]
    return mode,p_mode,bin_centers,bin_density,bin_widths

def detectSignalFromTruncatedGaussians(x,
                                       fac_p_decision=1.0,
                                       nEstimates = 10, sigEstimates = 10.0, 
                                       tau_max=100, epsNablaE=1e-8, E_ok=3, tau_ok=3,
                                       list_ptrunc_a=[0.0001,0.0001,0.0001,0.0001,0.0001,0.0001, 0.0001],
                                       list_ptrunc_b=[0.05  ,0.1   ,0.2   ,0.3   ,0.4   ,0.5   , 0.6   ],
                                       lmbda_mu=1/3, lmbda_sig2=1/3, lmbda_N=1/3,
                                       p_binsize=0.01,max_binsize=200,
                                       p_cutoff_mode=0.2):
    """
    Unsupervised Signal Detection Algorithm employing Truncated Gaussian Moments to estimate background noise and set optimal threshold for extracting the signal (see NB36/17.4.2023 and cf., AB4/pp299-301, AB5/pp1-5)
    For earlier implementation of the algorithm see also: ~/hs-albsig/02-research/Borst_Fledermaeuse/python/OLD_ARCHIVE/ivisit_spekview_v1_3_20230427.py  
                                                          --> in step(), line 182, (iv) Unsupervised Signal Detection with Truncated Gaussians
                                                          --> to be started with: python ivisit_spekview_v1_3_20230427.py ivisit_spekview_v1_3_20230427.db
    :param x: the raw signal where the signal detection algorithm should be applied to (1D array); 
              it is assumed that x is composed of the signal plus additive stationary Gaussian noise (with some mean mu0_est, variance sig02_est and noise data number N0_est)
    :param fac_p_decision: parameter determining threshold for signal detection; either float or list of floats (in the latter case resulting theta will also be a list)
                           set decision threshold to the smallest bin (see parameters p_binsize and max_binsize) larger than the mean and satisfying p(signal)>=fac_p_decision*p(noise)
                           e.g., fac_p_decision=1 corresponds to a maximum accuracy decision setting the threshold to the first bin where p(signal)>=p(noise) holds
                           e.g., fac_p_decision=5 corresponds to a larger threshold where p(signal)>=5*p(noise), where p(.) corresponds to estimated probability density within the bins of the data histogram
                           where it is assumed that signal is larger than noise on average (see also parameters list_ptrunc_a/b)
    :param nEstimates: number of parallel estimations of noise distribution parameters (mu0_est,sig02_est), each using different initialization parameters; 
                       as the convergence of the Newton algorithm depends on initial parameters, doing only a single estimation may give bad estimates or even diverge (to NaN);
                       therefore it is recommended using nEstimates>1, e.g., nEstimates=10
                       As the algorithm breaks as soon as being below a desired error limit, larger nEstimates may even accelerate the algorithm, since the chance of fast convergence increases
    :param sigEstimates: standard deviation of noise component of initial estimation of parameters; currently noise is added only to the initial estimate of the variance parameter sig02_est
                         (this seems to be sufficient to get different convergence behaviors, even for small sigEstimates)
    :param tau_max: Maximum number of time steps (or iterations) for Newton optimization 
    :param epsNablaE: Break Newton optimization loop for one of the nEstimates parallel estimations as soon as the first derivative NablaE of the error function E(mu0_est,sig02_est,N0_est) is below epsNablaE
    :param E_ok: If one of the nEstimates parallel estimations has an error E below E_ok then begin early stopping procedure (of additional tau_ok optimization steps, see parameter tau_ok)
                 The error value is relative to the standard deviation of the estimators mu0_est,sig02_est,N0_est (see NB36), so values below E<3 correspond to plausible estimates
                 as the probability that the estimates are more than 3 standard deviations away from the actual values is low
                 Moreover, it is a typical behavior that if E is already small then a few more optimization steps lead to final convergence
    :param tau_ok: Length of early stopping procedure (see param E_ok): As soon as E<E_ok begin early stopping procedure comprising tau_ok additional Newton optimization steps
    :param list_ptrunc_a: list coresponding to the left interval bounds a[i] of the i-th truncated Gaussians; length of list_ptrunc_a determines number of truncated Gaussians (see NB36)
                          The error E(mu0_est,sig02_est,N0_est) to be minimized by the Newton algorithm is the average over all truncated Gaussians
                          Instead of directly giving interval bounds [a[i],b[i]] the list is given by the percentiles p(i) of the (total) data distribution (comprising both noise and signal)
                          e.g., list_ptrunc_a[i]=0.01 correspond to the data value a[i] where 0.01 (1 percent) of the total data has values below a[i]
    :param list_ptrunc_b: list corrpesonding to the right interval bounds b[i] of the i-th truncated Gaussians (see NB36); length of list_ptrunc_b must be same as length of list_ptrunc_a
    :param lmbda_mu  : weight of the error term in E corresponding to the estimates mu_[i] of the truncted Gaussians (see NB36)
    :param lmbda_sig2: weight of the error term in E corresponding to the estimates sig2_[i] of the truncted Gaussians (see NB36)
    :param lmbda_N   : weight of the error term in E corresponding to the estimates N_[i] of the truncted Gaussians (see NB36)
    :param p_binsize:   determines binsize=max(1,len(x)*p_binsize) (in data number per bin) of the histograms used for estimating the mode of the data distribution (as initial estimate for the noise mean mu0_est) 
                        and to determine the decision threshold (see parameter fac_p_decision); each bin of the histogram contains binsize data values (except possibly the last one)
                        The binsize should be much smaller than the data number len(x), e.g., binsize<len(x)/100 to have enough "resolution" to obtain mode estimate and decision threshold with sufficient precision
    :param max_binsize: Bound binsize to values smaller than max_binsize, that is, binsize=max(1,min(max_binsize,len(x)*p_binsize))
    :param p_cutoff_mode: for determining mode of data distribution, cut of fraction p_cutoff_mode/2 from both below and above to avoide extreme values of densities (which may occur, e.g., if the data range is bounded)
                          As the mode for Gaussian background noise and sparse signal data should be close to the median, we can safely cut off, for example,
                          10% from below and 10% from above (corresponding to default value p_cutoff_mode=0.2) 
    """

    # (i) prepare data and compute mode and histograms 
    binsize=max(1,min(max_binsize,int(len(x)*p_binsize)))                                                     # determine bin size for histogram analysis
    binsize=max_binsize #200 #!!!!
    x_sorted=np.sort(x)                                                                                       # sort data values for estimation of mode and density of data distribution from histograms
    mode,p_mode,dummy1,dummy2,dummy3 = getModeOfDensity(x,binsize=binsize,p_cutoff=p_cutoff_mode,x_sorted=x_sorted)       # get mode of data distribution (most frequent value of histogram values) 
    dummy1,dummy2,bin_centers,bin_density,bin_widths = getModeOfDensity(x,binsize=binsize,p_cutoff=0,x_sorted=x_sorted)   # get density of data distribution (without cropping extreme values) 
    sig2max=np.var(x)                                                                                         # upper bound on noise variance (from complete distribution)

    # (ii) initial estimates of noise distribution parameters
    mu0_est_init   = mode                                       # use mode of data distribution as initial estimate mu0_est for the mean mu0 of the Gaussian noise distribution
    sig02_est_init = 1.0/(2*np.pi*p_mode*p_mode)                # estimate variance from density at mode assuming Gaussian distribution (see AB5/p8 from 23.4.2023); possible alternative would be using sig2max
    N0_est_init    = len(x)                                     # initialize estimated number of noise data points with total data number 
    mu0_est, sig02_est, N0_est = mu0_est_init, sig02_est_init, N0_est_init   # set current estimates using initial values
    
    # (iii) prepare parameters for truncated Gaussians
    n_ab=len(list_ptrunc_a)                                # number of truncated Gaussians to be considered
    assert n_ab==len(list_ptrunc_b),"parameters list_ptrunc_a and list_ptrunc_b must have same length, but list_ptrunc_a="+str(list_ptrunc_a)+", list_ptrunc_b="+str(list_ptrunc_b)
    list_a=x_sorted[[int(ai*N0_est) for ai in list_ptrunc_a]]  # transform list_ptrunc_a to list of actual lower bounds a[i] of the i-th truncated Gaussians
    list_b=x_sorted[[int(bi*N0_est) for bi in list_ptrunc_b]]  # transform list_ptrunc_b to list of actual upper bounds b[i] of the i-th truncated Gaussians
    list_x_trunc = [x[np.logical_and(x>=list_a[i],x<=list_b[i])] for i in range(n_ab)] # list of n_ab boolean numpy arrays each selecting the data points x[j] in [a[i],b[i]] belonging to the i-th Truncated Gaussian
    list_mu0__bar   = [np.mean(x_trunci) for x_trunci in list_x_trunc]  # list of empirical means mu0__bar[i] for each Truncated Gaussian truncating the interval [a[i],b[i]]  
    list_sig02__bar = [np.var (x_trunci) for x_trunci in list_x_trunc]  # list of empirical variances sig02__bar[i] for each Truncated Gaussian truncating the interval [a[i],b[i]]  
    list_N0__bar    = [len    (x_trunci) for x_trunci in list_x_trunc]  # list of empirical data number N0__bar[i] for each Truncated Gaussian truncating the interval [a[i],b[i]]  
    sig2min=np.max(list_sig02__bar)   # lower bound on noise variance (assuming that the truncated distributions contain no signals, the noise variance must be larger than each truncated variance)
    mumin=np.min(list_mu0__bar)                # we can assume that mu0 is at least the minimal truncated mean (as we are mainly sampling from the lower percentiles) 
    mumax=np.mean(x[x>np.max(list_mu0__bar)])  # we can assume that mu0 is at most the mean above the largest truncated mean (as we are skipping some of the lower percentiles) 
    assert np.min(list_N0__bar)>=3,"Not enough data points found: list_N0__bar="+str(list_N0__bar)+" should all be at least 3! Either increase data number len(x) or increase truncation interval sizes [a[i];b[i]]!" 

    # (iv) call to Newton optimization of noise distribution parameters mu0_est, sig02_est, N0_est
    tau,E,nablaE,H_E,res = 0,'undef','undef','undef',None  # initialize time steps tau, error E, gradient nablaE, and Hessian H_E with dummy values (in case tau_max is set 0, then return just the initializations from (ii))
    if tau_max>0:
        old_err_settings = np.seterr(all='ignore')  #ignore warnings; catch NAN warnings by hand
        res=estimateGaussParametersFromTruncatedGaussians(mu0_est  *(1.0+sigEstimates*0.01*np.random.randn(nEstimates)),\
                                                          sig02_est*(1.0+sigEstimates*0.01*np.random.randn(nEstimates)),\
                                                          N0_est   *(1.0+sigEstimates*0.01*np.random.randn(nEstimates)),\
                                                          np.array(list_a),np.array(list_b),np.array(list_mu0__bar),np.array(list_sig02__bar),np.array(list_N0__bar),\
                                                          lmbda_mu,lmbda_sig2,lmbda_N,tau_max,
                                                          mumin,mumax,sig2min,sig2max,3,len(x))
        idx_best  = res['idx_best']
        mu0_est   = res['mu_est_best'  ][idx_best]
        sig02_est = res['sig2_est_best'][idx_best]
        N0_est    = res['N_est_best'   ][idx_best]
        E         = res['E_best'       ][idx_best]
        nablaE    = res['DE_best'      ][:,idx_best]
        H_E       = res['DDE_best'     ][:,idx_best]
        tau       = res['tau'          ]
        np.seterr(**old_err_settings)               # reactivate warnings (set to previous state) 

    # (v) determine decision threshold
    minhist,maxhist=np.min(x),np.max(x)     # minimal and maximal data value
    yy0 = N0_est/np.sqrt(2*np.pi*sig02_est)*np.exp(-0.5*np.multiply(bin_centers-mu0_est,bin_centers-mu0_est)/sig02_est)   # theoretical class 0 histogram density (# expected data points per length) at histogram centers
    yy01_x=len(x)*bin_density                                                                                          # empirical histogram density for both class 0 and class 1
    yy1=yy01_x-yy0                          # histogram density of class 1  (whereas yy0 is estimated histogram density of class 0)
    min_theta=np.max(list_b)                # upper interval bounds b are assumed to belong to class 0
    fac_p_dec_list=fac_p_decision                                              # list of decision factors
    if not isinstance(fac_p_dec_list, list): fac_p_dec_list=[fac_p_dec_list]   # enforce list
    theta,idx_theta=[],[]
    for i in range(len(fac_p_dec_list)):    # iterate over all decision factors to compute a corresponding decision threshold
        idx_theta+=[np.argmax(np.logical_and(yy1>fac_p_dec_list[i]*yy0,\
                                             bin_centers>min_theta))] # get index of lowest threshold (beyond min_theta), where class1 has a larger density (times fac_p_decision) than class 0 to maximize classif. accuracy
        if idx_theta[i]==0:                 # no values available where class 1 has larger density than class 0 
            #theta=maxhist*1.01             # previous choice: --> then set theta above maximum of histogram values
            theta+=[mu0_est+np.sqrt(2*sig02_est)*erfcinv(2.0/(fac_p_dec_list[i]*len(x)))]   # maybe better choice: set threshold such that 1/fac_p_decision false class 1 sample occurs on average (see AB5/pp8-9/24.4.2023)
        else:
            theta+=[bin_centers[idx_theta[i]]] # decision threshold
    if not isinstance(fac_p_decision, list): theta,idx_theta=theta[0],idx_theta[0]  # enforce type for theta being same as for fac_p_decision

    # (vi) return results as data dict
    dd={}
    dd['res']=res
    dd['idx_best']=idx_best
    dd['mu0_est']=mu0_est
    dd['sig02_est']=sig02_est
    dd['N0_est']=N0_est
    dd['E']=E
    dd['nablaE']=nablaE
    dd['H_E']=H_E
    dd['tau']=tau
    dd['theta']=theta
    dd['idx_theta']=idx_theta
    dd['mu0_est_init']=mu0_est_init
    dd['sig02_est_init']=sig02_est_init
    dd['N0_est_init']=N0_est_init
    dd['n_ab']=n_ab
    dd['list_a']=list_a
    dd['list_b']=list_b
    dd['mode']=mode
    dd['p_mode']=p_mode
    dd['binsize']=binsize
    dd['bin_centers']=bin_centers
    dd['bin_density']=bin_density
    dd['bin_widths' ]=bin_widths
    dd['yy0']=yy0
    dd['yy01_x']=yy01_x
    dd['yy1']=yy1
    dd['min_theta']=min_theta
    return dd

##################################################################################################################################################################
##################################################################################################################################################################
##################################################################################################################################################################
# Part XX: Module test
##################################################################################################################################################################
##################################################################################################################################################################
##################################################################################################################################################################
if __name__ == '__main__':
    from time import time as clock

    select_tests={
        "inv3"                       :0,
        "deriv_trunc_gauss"          :0,
        "deriv_trunc_gauss_arr"      :0,
        "estim_Gauss_from_TruncGauss":1
    }

    if select_tests["inv3"]>0:
        ##################################################################################################################################################################
        print("\nModule test of supylib module supy.signal.py:")
        print("------------------------------------------------")
        print("\nPart (i): Test of inv3(.) and their variants:")
        print("-----------------------------------------------")
        ##################################################################################################################################################################
        n_trials=30
        #n_trials=3
        list_maxerr=[]
        print("\n(a) Prove correctness of inv3(.) for n_trials=",n_trials)
        for i in range(n_trials):
            A=np.random.rand(3,3)
            #print("A=",A)
            Ainv_np=np.linalg.inv(A)
            Ainv=inv3(A)
            list_maxerr.append(np.max(np.abs(Ainv_np-Ainv)))
        #print("list_maxerr=",list_maxerr)
        print("maxerr=",np.max(list_maxerr))

        print("\n(b) Measure efficiency of inv3(.) for n_trials=",n_trials)
        A=np.random.rand(n_trials,3,3)
        t1=clock()
        for i in range(n_trials): Ainv_np=np.linalg.inv(A[i])
        t2=clock()
        print("Numpy: dt=",t2-t1)
        t1=clock()
        for i in range(n_trials): Ainv=inv3(A[i])
        t2=clock()
        print("Supy.Signal: dt=",t2-t1)
        
        print("\n(c) Prove correctness and efficiency of inv3_arr(.) for n_trials=",n_trials)
        A=np.random.rand(3,3,n_trials)
        Ainv_np=np.zeros(A.shape)
        t1=clock()
        for i in range(n_trials): Ainv_np[:,:,i]=np.linalg.inv(A[:,:,i])    
        t2=clock()
        print("Numpy (for-loop): dt=",t2-t1)
        A_np_ar=np.zeros((n_trials,3,3))
        for i in range(n_trials): A_np_ar[i,:,:]=A[:,:,i]  # bring in format for numpy
        t1=clock()
        Ainv_np_=np.linalg.inv(A_np_ar)    
        t2=clock()
        print("Numpy (at once): dt=",t2-t1)
        Ainv_np__=np.zeros(A.shape)
        for i in range(n_trials): Ainv_np__[:,:,i]=Ainv_np_[i,:,:]  # bring back to format of A (for later comparison)
        t1=clock()
        Ainv,detA=inv3_arr(A)
        t2=clock()
        print("Supy.Signal: dt=",t2-t1)
        print("maxerr=",np.max(np.abs(Ainv-Ainv_np))) 
        print("maxerr=",np.max(np.abs(Ainv-Ainv_np__))) 

        print("\n(d) Prove correctness and efficiency of inv3sym(.) for n_trials=",n_trials)
        A=np.random.rand(n_trials,3,3)
        A[:,1,0],A[:,2,0],A[:,2,1]=A[:,0,1],A[:,0,2],A[:,1,2]   # enforce symmetry
        A_cmpr=np.array([A[:,0,0],A[:,1,1],A[:,2,2],A[:,0,1],A[:,0,2],A[:,1,2]])
        print("A[:,0,0].shape=",A[:,0,0].shape)
        print("A_cmpr.shape=",A_cmpr.shape)
        list_maxerr=[]
        list_maxerr_cmpr=[]
        for i in range(n_trials):
            Ainv_np=np.linalg.inv(A[i])     # numpy
            Ainv=inv3sym(A[i])              # supy.signal uncompressed 
            Ainv_cmpr=inv3sym(A_cmpr[:,i])  # supy.signal compressed
            Ainv_cmpr_=np.array([[Ainv_cmpr[0],Ainv_cmpr[3],Ainv_cmpr[4]],\
                                 [Ainv_cmpr[3],Ainv_cmpr[1],Ainv_cmpr[5]],\
                                 [Ainv_cmpr[4],Ainv_cmpr[5],Ainv_cmpr[2]]])  # de-compress for comparison
            list_maxerr     .append(np.max(np.abs(Ainv_np-Ainv      )))
            list_maxerr_cmpr.append(np.max(np.abs(Ainv_np-Ainv_cmpr_)))
        print("maxerr     =",np.max(list_maxerr))
        print("maxerr_cmpr=",np.max(list_maxerr_cmpr))
        t1=clock()
        for i in range(n_trials): Ainv_np=np.linalg.inv(A[i])     # numpy
        t2=clock()
        print("Numpy: dt=",t2-t1)
        t1=clock()
        for i in range(n_trials): Ainv=inv3sym(A[i])              # supy.signal uncompressed      
        t2=clock()
        print("Supy.Signal uncompressed: dt=",t2-t1)
        t1=clock()
        for i in range(n_trials): Ainv=inv3sym(A_cmpr[:,i])       # supy.signal compressed      
        t2=clock()
        print("Supy.Signal compressed: dt=",t2-t1)

        print("\n(e) Prove correctness and efficiency of inv3sym_arr(.) for n_trials=",n_trials)
        A=np.random.rand(3,3,n_trials)
        A[1,0,:],A[2,0,:],A[2,1,:]=A[0,1,:],A[0,2,:],A[1,2,:]   # enforce symmetry
        Ainv_np=np.zeros(A.shape)
        t1=clock()
        for i in range(n_trials): Ainv_np[:,:,i]=np.linalg.inv(A[:,:,i])     # *** numpy (for loop)    
        t2=clock()
        dt_numpy_loop=t2-t1
        print("Numpy (for-loop): dt=",t2-t1)
        A_np_ar=np.zeros((n_trials,3,3))
        for i in range(n_trials): A_np_ar[i,:,:]=A[:,:,i]  # bring in format for numpy
        t1=clock()
        Ainv_np_=np.linalg.inv(A_np_ar)                                      # *** numpy (at once)
        t2=clock()
        dt_numpy_once=t2-t1
        print("Numpy (at once): dt=",t2-t1)
        Ainv_np__=np.zeros(A.shape)
        for i in range(n_trials): Ainv_np__[:,:,i]=Ainv_np_[i,:,:]  # bring back to format of A (for later comparison)
        t1=clock()
        Ainv,detA=inv3sym_arr(A)                                              # *** supy.signal compressed
        t2=clock()
        print("Supy.Signal uncompressed: dt=",t2-t1)
        A_cmpr=np.array([A[0,0,:],A[1,1,:],A[2,2,:],A[0,1,:],A[0,2,:],A[1,2,:]])
        t1=clock()
        Ainv_cmpr,detA_cmpr=inv3sym_arr(A_cmpr)                               # *** supy.signal compressed
        t2=clock()
        dt_supy_cmpr=t2-t1
        print("Supy.Signal compressed: dt=",t2-t1)
        Ainv_cmpr_=np.array([[Ainv_cmpr[0],Ainv_cmpr[3],Ainv_cmpr[4]],\
                             [Ainv_cmpr[3],Ainv_cmpr[1],Ainv_cmpr[5]],\
                             [Ainv_cmpr[4],Ainv_cmpr[5],Ainv_cmpr[2]]]) # bring back in format 3x3xN for comparison
        print("np-loop vs. uncompressed: maxerr=",np.max(np.abs(Ainv-Ainv_np))) 
        print("np-once vs. uncompressed: maxerr=",np.max(np.abs(Ainv-Ainv_np__))) 
        print("np-loop vs. compressed: maxerr=",np.max(np.abs(Ainv_cmpr_-Ainv_np))) 
        print("np-once vs. compressed: maxerr=",np.max(np.abs(Ainv_cmpr_-Ainv_np__))) 
        print("gain np-loop vs. compressed:",dt_numpy_loop/dt_supy_cmpr)
        print("gain np-once vs. compressed:",dt_numpy_once/dt_supy_cmpr)
 
    if select_tests["deriv_trunc_gauss"]>0 or select_tests["deriv_trunc_gauss_arr"]>0:
        ##################################################################################################################################################################
        print("\nModule test of supylib module supy.signal.py:")
        print("------------------------------------------------")
        print("\nPart (ii): Test of getDerivatives4TruncatedGaussiansError(.) and getDerivatives4TruncatedGaussiansError_arr(.):")
        print("-----------------------------------------------")
        ##################################################################################################################################################################
        flagRand=0    # 1=random, 2=random, gentle
        criticalCase=1
        
        #mu,sig,  a,b  =   3.1, 1.2,    2.5, 2.9
        mu,sig,  a,b, N  =   3.1, 1.2,    1.5, 2.9,  10.5
        mu__bar,sig__bar,N__bar = 2.7,0.9,4
        lmbda_mu,lmbda_sig2,lmbda_N=0.85,0.95,1.15
        
        if flagRand==1:
            mu,sig,N = 3*np.random.randn(1)[0], abs(2*np.random.randn(1))[0], abs(20+2*np.random.randn(1))[0]
            a,b = mu-3*sig+np.random.rand()*6*sig, mu-3*sig+np.random.rand()*6*sig
            a,b = min(a,b),max(a,b)
            mu__bar,sig__bar,N__bar = min(a,b)+np.random.rand()*abs(b-a), 0.5*np.random.rand()*abs(b-a), abs(20+2*np.random.randn(1)[0])
            lmbda_mu,lmbda_sig2,lmbda_N=1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand()
    
        if flagRand==2:
            mu,sig,N = 3*np.random.randn(1)[0], abs(2*np.random.randn(1))[0], abs(20+2*np.random.randn(1))[0]
            a,b = mu-2*sig+np.random.rand()*2*sig, mu-2*sig+np.random.rand()*2*sig
            a,b = min(a,b),max(a,b)
            mu__bar,sig__bar,N__bar = min(a,b)+np.random.rand()*abs(b-a), 0.5*(0.2+np.random.rand())*abs(b-a), abs(20+2*np.random.randn(1)[0])
            lmbda_mu,lmbda_sig2,lmbda_N=1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand()

        if criticalCase==1:   # as obtained from random with large numerical error
            mu,sig,N = -2.5058248508468988, 0.6987712033650018, 18.387389380774177
            a,b,     = -3.602869340484787, -3.152404152726297
            mu__bar,sig__bar,N__bar = -3.2580722516217926, 0.17731485094149554, 17.50877240410078
            lmbda_mu,lmbda_sig2,lmbda_N = 1.245738798006679, 1.0088250185926841, 1.2333476146119249
            eps=1e-7
        
        eps=1e-7
        sig2=sig*sig
        sig2__bar=sig__bar*sig__bar
        eps_sig=np.sqrt(sig2+eps)-sig    # for computing numerical derivatives w.r.t. sig: sig+eps = sqrt(sig2+eps)
        
        print("mu=",mu,"sig=",sig,"a=",a,"b=",b,"N=",N,"mu__bar=",mu__bar,"sig__bar=",sig__bar,"N__bar=",N__bar)
        print("lmbda_mu=",lmbda_mu,"lmbda_sig2=",lmbda_sig2,"lmbda_N=",lmbda_N)
        print("eps=",eps,"eps_sig=",eps_sig)
        print("alpha=",(a-mu)/sig,"beta=",(b-mu)/sig)
        
        print("\nComputing results for Part I (NB34) and Part II (NB36)...")
        list_rel_err_NB34,list_rel_err_NB36=[],[]                 # lists of relative errors
        list_rel_err_NB34_vals,list_rel_err_NB36_vals=[],[]       # lists of corresponding absolute values
        dd=getDerivatives4TruncatedGaussiansError(mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=0)
        dd_epsmu  =getDerivatives4TruncatedGaussiansError(mu+eps,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=0)
        dd_epssig2=getDerivatives4TruncatedGaussiansError(mu,sig2+eps,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=0)
        dd_epsN   =getDerivatives4TruncatedGaussiansError(mu,sig2,N+eps,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=0)
        dd_arr=getDerivatives4TruncatedGaussiansError_arr(np.array([mu]),np.array([sig2]),np.array([N]),np.array([a]),np.array([b]),np.array([mu__bar]),np.array([sig2__bar]),np.array([N__bar]),lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=0)
        if select_tests["deriv_trunc_gauss"]>0:
            print("\nI) Verify results Part I (NB34, pp12-pp15):")
            print("-------------------------------------------------")
            
            print("\nI.a) Test: Z,gamma and derivatives (only compare derivatives of Z and gamma against numerical values)")
            print("Z                   =",dd['Z'])
            print("d_Z_DIV_d_mu        =",dd['d_Z_DIV_d_mu'])
            print("d_Z_DIV_d_sig       =",dd['d_Z_DIV_d_sig'])
            print("d2_Z_DIV_d_mu_d_mu  =",dd['d2_Z_DIV_d_mu_d_mu'])
            print("d2_Z_DIV_d_sig_d_sig=",dd['d2_Z_DIV_d_sig_d_sig'])
            print("d2_Z_DIV_d_mu_d_sig =",dd['d2_Z_DIV_d_mu_d_sig'])
            rel_err_d_Z_DIV_d_mu        =np.divide(dd['d_Z_DIV_d_mu'        ]-(dd_epsmu  ['Z'            ]-dd['Z'            ])/eps    ,abs(dd['d_Z_DIV_d_mu'        ])); print("rel_err_d_Z_DIV_d_mu        =",rel_err_d_Z_DIV_d_mu)
            rel_err_d_Z_DIV_d_sig       =np.divide(dd['d_Z_DIV_d_sig'       ]-(dd_epssig2['Z'            ]-dd['Z'            ])/eps_sig,abs(dd['d_Z_DIV_d_sig'       ])); print("rel_err_d_Z_DIV_d_sig       =",rel_err_d_Z_DIV_d_sig)
            rel_err_d2_Z_DIV_d_mu_d_mu  =np.divide(dd['d2_Z_DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_Z_DIV_d_mu' ]-dd['d_Z_DIV_d_mu' ])/eps    ,abs(dd['d2_Z_DIV_d_mu_d_mu'  ])); print("rel_err_d2_Z_DIV_d_mu_d_mu  =",rel_err_d2_Z_DIV_d_mu_d_mu)
            rel_err_d2_Z_DIV_d_sig_d_sig=np.divide(dd['d2_Z_DIV_d_sig_d_sig']-(dd_epssig2['d_Z_DIV_d_sig']-dd['d_Z_DIV_d_sig'])/eps_sig,abs(dd['d2_Z_DIV_d_sig_d_sig'])); print("rel_err_d2_Z_DIV_d_sig_d_sig=",rel_err_d2_Z_DIV_d_sig_d_sig)
            rel_err_d2_Z_DIV_d_mu_d_sig =np.divide(dd['d2_Z_DIV_d_mu_d_sig' ]-(dd_epssig2['d_Z_DIV_d_mu' ]-dd['d_Z_DIV_d_mu' ])/eps_sig,abs(dd['d2_Z_DIV_d_mu_d_sig' ])); print("rel_err_d2_Z_DIV_d_mu_d_sig =",rel_err_d2_Z_DIV_d_mu_d_sig)
            list_rel_err_NB34     +=[rel_err_d_Z_DIV_d_mu,rel_err_d_Z_DIV_d_sig,rel_err_d2_Z_DIV_d_mu_d_mu,rel_err_d2_Z_DIV_d_sig_d_sig,rel_err_d2_Z_DIV_d_mu_d_sig] 
            list_rel_err_NB34_vals+=[    dd['d_Z_DIV_d_mu'],  dd['d_Z_DIV_d_sig'],  dd['d2_Z_DIV_d_mu_d_mu'],  dd['d2_Z_DIV_d_sig_d_sig'],  dd['d2_Z_DIV_d_mu_d_sig']] 
            print("gamma                   =",dd['gamma'])
            print("d_gamma_DIV_d_mu        =",dd['d_gamma_DIV_d_mu'])
            print("d_gamma_DIV_d_sig       =",dd['d_gamma_DIV_d_sig'])
            print("d2_gamma_DIV_d_mu_d_mu  =",dd['d2_gamma_DIV_d_mu_d_mu'])
            print("d2_gamma_DIV_d_sig_d_sig=",dd['d2_gamma_DIV_d_sig_d_sig'])
            print("d2_gamma_DIV_d_mu_d_sig =",dd['d2_gamma_DIV_d_mu_d_sig'])
            rel_err_d_gamma_DIV_d_mu        =np.divide(dd['d_gamma_DIV_d_mu'        ]-(dd_epsmu  ['gamma'            ]-dd['gamma'            ])/eps    ,abs(dd['d_gamma_DIV_d_mu'        ])); print("rel_err_d_gamma_DIV_d_mu        =",rel_err_d_gamma_DIV_d_mu)
            rel_err_d_gamma_DIV_d_sig       =np.divide(dd['d_gamma_DIV_d_sig'       ]-(dd_epssig2['gamma'            ]-dd['gamma'            ])/eps_sig,abs(dd['d_gamma_DIV_d_sig'       ])); print("rel_err_d_gamma_DIV_d_sig       =",rel_err_d_gamma_DIV_d_sig)
            rel_err_d2_gamma_DIV_d_mu_d_mu  =np.divide(dd['d2_gamma_DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_gamma_DIV_d_mu' ]-dd['d_gamma_DIV_d_mu' ])/eps    ,abs(dd['d2_gamma_DIV_d_mu_d_mu'  ])); print("rel_err_d2_gamma_DIV_d_mu_d_mu  =",rel_err_d2_gamma_DIV_d_mu_d_mu)
            rel_err_d2_gamma_DIV_d_sig_d_sig=np.divide(dd['d2_gamma_DIV_d_sig_d_sig']-(dd_epssig2['d_gamma_DIV_d_sig']-dd['d_gamma_DIV_d_sig'])/eps_sig,abs(dd['d2_gamma_DIV_d_sig_d_sig'])); print("rel_err_d2_gamma_DIV_d_sig_d_sig=",rel_err_d2_gamma_DIV_d_sig_d_sig)
            rel_err_d2_gamma_DIV_d_mu_d_sig =np.divide(dd['d2_gamma_DIV_d_mu_d_sig' ]-(dd_epssig2['d_gamma_DIV_d_mu' ]-dd['d_gamma_DIV_d_mu' ])/eps_sig,abs(dd['d2_gamma_DIV_d_mu_d_sig' ])); print("rel_err_d2_gamma_DIV_d_mu_d_sig =",rel_err_d2_gamma_DIV_d_mu_d_sig)
            list_rel_err_NB34     +=[rel_err_d_gamma_DIV_d_mu,rel_err_d_gamma_DIV_d_sig,rel_err_d2_gamma_DIV_d_mu_d_mu,rel_err_d2_gamma_DIV_d_sig_d_sig,rel_err_d2_gamma_DIV_d_mu_d_sig] 
            list_rel_err_NB34_vals+=[    dd['d_gamma_DIV_d_mu'],  dd['d_gamma_DIV_d_sig'],  dd['d2_gamma_DIV_d_mu_d_mu'],  dd['d2_gamma_DIV_d_sig_d_sig'],  dd['d2_gamma_DIV_d_mu_d_sig']]
            
            print("\nI.b) Test: Sn and derivatives (derivatives are compared against numerical approximations")
            print("S                   =",dd['S'])
            print("d_S_DIV_d_mu        =",dd['d_S_DIV_d_mu'])
            print("d_S_DIV_d_sig       =",dd['d_S_DIV_d_sig'])
            print("d2_S_DIV_d_mu_d_mu  =",dd['d2_S_DIV_d_mu_d_mu'])
            print("d2_S_DIV_d_sig_d_sig=",dd['d2_S_DIV_d_sig_d_sig'])
            print("d2_S_DIV_d_mu_d_sig =",dd['d2_S_DIV_d_mu_d_sig'])
            rel_err_d_S_DIV_d_mu        =np.divide(dd['d_S_DIV_d_mu'        ]-(dd_epsmu  ['S'            ]-dd['S'            ])/eps    , abs(dd['d_S_DIV_d_mu'        ]));print("rel_err_d_S_DIV_d_mu        =",rel_err_d_S_DIV_d_mu)
            rel_err_d_S_DIV_d_sig       =np.divide(dd['d_S_DIV_d_sig'       ]-(dd_epssig2['S'            ]-dd['S'            ])/eps_sig, abs(dd['d_S_DIV_d_sig'       ]));print("rel_err_d_S_DIV_d_sig       =",rel_err_d_S_DIV_d_sig)
            rel_err_d2_S_DIV_d_mu_d_mu  =np.divide(dd['d2_S_DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_S_DIV_d_mu' ]-dd['d_S_DIV_d_mu' ])/eps    , abs(dd['d2_S_DIV_d_mu_d_mu'  ]));print("rel_err_d2_S_DIV_d_mu_d_mu  =",rel_err_d2_S_DIV_d_mu_d_mu)
            rel_err_d2_S_DIV_d_sig_d_sig=np.divide(dd['d2_S_DIV_d_sig_d_sig']-(dd_epssig2['d_S_DIV_d_sig']-dd['d_S_DIV_d_sig'])/eps_sig, abs(dd['d2_S_DIV_d_sig_d_sig']));print("rel_err_d2_S_DIV_d_sig_d_sig=",rel_err_d2_S_DIV_d_sig_d_sig)
            rel_err_d2_S_DIV_d_mu_d_sig =np.divide(dd['d2_S_DIV_d_mu_d_sig' ]-(dd_epssig2['d_S_DIV_d_mu' ]-dd['d_S_DIV_d_mu' ])/eps_sig, abs(dd['d2_S_DIV_d_mu_d_sig' ]));print("rel_err_d2_S_DIV_d_mu_d_sig =",rel_err_d2_S_DIV_d_mu_d_sig)
            list_rel_err_NB34     +=list(rel_err_d_S_DIV_d_mu)+list(rel_err_d_S_DIV_d_sig)+list(rel_err_d2_S_DIV_d_mu_d_mu)+list(rel_err_d2_S_DIV_d_sig_d_sig)+list(rel_err_d2_S_DIV_d_mu_d_sig) 
            list_rel_err_NB34_vals+=list(    dd['d_S_DIV_d_mu'])+list(  dd['d_S_DIV_d_sig'])+list(  dd['d2_S_DIV_d_mu_d_mu'])+list(  dd['d2_S_DIV_d_sig_d_sig'])+list(  dd['d2_S_DIV_d_mu_d_sig'])
            print("max(list_rel_err_NB34)=",np.max(np.abs(list_rel_err_NB34)))
            
            print("\nI.c) Test: F, G and derivatives (only derivatives are compared against numerical approximations")
            print("F                   =",dd['F'])
            print("d_F_DIV_d_mu        =",dd['d_F_DIV_d_mu'])
            print("d_F_DIV_d_sig       =",dd['d_F_DIV_d_sig'])
            print("d2_F_DIV_d_mu_d_mu  =",dd['d2_F_DIV_d_mu_d_mu'])
            print("d2_F_DIV_d_sig_d_sig=",dd['d2_F_DIV_d_sig_d_sig'])
            print("d2_F_DIV_d_mu_d_sig =",dd['d2_F_DIV_d_mu_d_sig'])
            rel_err_d_F_DIV_d_mu        =np.divide(dd['d_F_DIV_d_mu'        ]-(dd_epsmu  ['F']            -dd['F']            )/eps    , abs(dd['d_F_DIV_d_mu'        ]));print("rel_err_d_F_DIV_d_mu        =",rel_err_d_F_DIV_d_mu)
            rel_err_d_F_DIV_d_sig       =np.divide(dd['d_F_DIV_d_sig'       ]-(dd_epssig2['F']            -dd['F']            )/eps_sig, abs(dd['d_F_DIV_d_sig'       ]));print("rel_err_d_F_DIV_d_sig       =",rel_err_d_F_DIV_d_sig)
            rel_err_d2_F_DIV_d_mu_d_mu  =np.divide(dd['d2_F_DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_F_DIV_d_mu' ]-dd['d_F_DIV_d_mu' ])/eps    , abs(dd['d2_F_DIV_d_mu_d_mu'  ]));print("rel_err_d2_F_DIV_d_mu_d_mu  =",rel_err_d2_F_DIV_d_mu_d_mu)
            rel_err_d2_F_DIV_d_sig_d_sig=np.divide(dd['d2_F_DIV_d_sig_d_sig']-(dd_epssig2['d_F_DIV_d_sig']-dd['d_F_DIV_d_sig'])/eps_sig, abs(dd['d2_F_DIV_d_sig_d_sig']));print("rel_err_d2_F_DIV_d_sig_d_sig=",rel_err_d2_F_DIV_d_sig_d_sig)
            rel_err_d2_F_DIV_d_mu_d_sig =np.divide(dd['d2_F_DIV_d_mu_d_sig' ]-(dd_epssig2['d_F_DIV_d_mu' ]-dd['d_F_DIV_d_mu' ])/eps_sig, abs(dd['d2_F_DIV_d_mu_d_sig' ]));print("rel_err_d2_F_DIV_d_mu_d_sig =",rel_err_d2_F_DIV_d_mu_d_sig)
            ixOK=np.logical_not(np.isnan(dd['F']))   # kick out nan in list of relative errors
            list_rel_err_NB34     +=list(rel_err_d_F_DIV_d_mu[ixOK].flat)+list(rel_err_d_F_DIV_d_sig[ixOK].flat)+list(rel_err_d2_F_DIV_d_mu_d_mu[ixOK].flat)+list(rel_err_d2_F_DIV_d_sig_d_sig[ixOK].flat)+list(rel_err_d2_F_DIV_d_mu_d_sig[ixOK].flat)
            list_rel_err_NB34_vals+=list(    dd['d_F_DIV_d_mu'][ixOK].flat)+list(  dd['d_F_DIV_d_sig'][ixOK].flat)+list(  dd['d2_F_DIV_d_mu_d_mu'][ixOK].flat)+list(  dd['d2_F_DIV_d_sig_d_sig'][ixOK].flat)+list(  dd['d2_F_DIV_d_mu_d_sig'][ixOK].flat)
            print("max(list_rel_err_NB34)=",np.max(np.abs(list_rel_err_NB34)))
            print("\nG                   =",dd['G'])
            print("d_G_DIV_d_mu        =",dd['d_G_DIV_d_mu'])
            print("d_G_DIV_d_sig       =",dd['d_G_DIV_d_sig'])
            print("d2_G_DIV_d_mu_d_mu  =",dd['d2_G_DIV_d_mu_d_mu'])
            print("d2_G_DIV_d_sig_d_sig=",dd['d2_G_DIV_d_sig_d_sig'])
            print("d2_G_DIV_d_mu_d_sig =",dd['d2_G_DIV_d_mu_d_sig'])
            rel_err_d_G_DIV_d_mu        =np.divide(dd['d_G_DIV_d_mu'        ]-(dd_epsmu  ['G']            -dd['G'            ])/eps    , abs(dd['d_G_DIV_d_mu'        ]));print("rel_err_d_G_DIV_d_mu        =",rel_err_d_G_DIV_d_mu)
            rel_err_d_G_DIV_d_sig       =np.divide(dd['d_G_DIV_d_sig'       ]-(dd_epssig2['G']            -dd['G'            ])/eps_sig, abs(dd['d_G_DIV_d_sig'       ]));print("rel_err_d_G_DIV_d_sig       =",rel_err_d_G_DIV_d_sig)
            rel_err_d2_G_DIV_d_mu_d_mu  =np.divide(dd['d2_G_DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_G_DIV_d_mu' ]-dd['d_G_DIV_d_mu' ])/eps    , abs(dd['d2_G_DIV_d_mu_d_mu'  ]));print("rel_err_d2_G_DIV_d_mu_d_mu  =",rel_err_d2_G_DIV_d_mu_d_mu)
            rel_err_d2_G_DIV_d_sig_d_sig=np.divide(dd['d2_G_DIV_d_sig_d_sig']-(dd_epssig2['d_G_DIV_d_sig']-dd['d_G_DIV_d_sig'])/eps_sig, abs(dd['d2_G_DIV_d_sig_d_sig']));print("rel_err_d2_G_DIV_d_sig_d_sig=",rel_err_d2_G_DIV_d_sig_d_sig)
            rel_err_d2_G_DIV_d_mu_d_sig =np.divide(dd['d2_G_DIV_d_mu_d_sig' ]-(dd_epssig2['d_G_DIV_d_mu' ]-dd['d_G_DIV_d_mu' ])/eps_sig, abs(dd['d2_G_DIV_d_mu_d_sig' ]));print("rel_err_d2_G_DIV_d_mu_d_sig =",rel_err_d2_G_DIV_d_mu_d_sig)
            list_rel_err_NB34     +=list(rel_err_d_G_DIV_d_mu)+list(rel_err_d_G_DIV_d_sig)+list(rel_err_d2_G_DIV_d_mu_d_mu)+list(rel_err_d2_G_DIV_d_sig_d_sig)+list(rel_err_d2_G_DIV_d_mu_d_sig) 
            list_rel_err_NB34_vals+=list(    dd['d_G_DIV_d_mu'])+list(  dd['d_G_DIV_d_sig'])+list(  dd['d2_G_DIV_d_mu_d_mu'])+list(  dd['d2_G_DIV_d_sig_d_sig'])+list(  dd['d2_G_DIV_d_mu_d_sig']) 
            print("max(list_rel_err_NB34)=",np.max(np.abs(list_rel_err_NB34)))
            
            print("\nI.d) Test: mu_n_ and derivatives (mu_n_ is compared against previous computation, and derivatives are compared against numerical approximations")
            print("mu_n_                   =",dd['mu_n_'])
            print("d_mu_n__DIV_d_mu        =",dd['d_mu_n__DIV_d_mu'])
            print("d_mu_n__DIV_d_sig       =",dd['d_mu_n__DIV_d_sig'])
            print("d2_mu_n__DIV_d_mu_d_mu  =",dd['d2_mu_n__DIV_d_mu_d_mu'])
            print("d2_mu_n__DIV_d_sig_d_sig=",dd['d2_mu_n__DIV_d_sig_d_sig'])
            print("d2_mu_n__DIV_d_mu_d_sig =",dd['d2_mu_n__DIV_d_mu_d_sig'])
            rel_err_d_mu_n__DIV_d_mu        =np.divide(dd['d_mu_n__DIV_d_mu'        ]-(dd_epsmu  ['mu_n_'            ]-dd['mu_n_'            ])/eps    ,abs(dd['d_mu_n__DIV_d_mu'        ]));print("rel_err_d_mu_n__DIV_d_mu        =",rel_err_d_mu_n__DIV_d_mu)
            rel_err_d_mu_n__DIV_d_sig       =np.divide(dd['d_mu_n__DIV_d_sig'       ]-(dd_epssig2['mu_n_'            ]-dd['mu_n_'            ])/eps_sig,abs(dd['d_mu_n__DIV_d_sig'       ]));print("rel_err_d_mu_n__DIV_d_sig       =",rel_err_d_mu_n__DIV_d_sig)
            rel_err_d2_mu_n__DIV_d_mu_d_mu  =np.divide(dd['d2_mu_n__DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_mu_n__DIV_d_mu' ]-dd['d_mu_n__DIV_d_mu' ])/eps    ,abs(dd['d2_mu_n__DIV_d_mu_d_mu'  ]));print("rel_err_d2_mu_n__DIV_d_mu_d_mu  =",rel_err_d2_mu_n__DIV_d_mu_d_mu)
            rel_err_d2_mu_n__DIV_d_sig_d_sig=np.divide(dd['d2_mu_n__DIV_d_sig_d_sig']-(dd_epssig2['d_mu_n__DIV_d_sig']-dd['d_mu_n__DIV_d_sig'])/eps_sig,abs(dd['d2_mu_n__DIV_d_sig_d_sig']));print("rel_err_d2_mu_n__DIV_d_sig_d_sig=",rel_err_d2_mu_n__DIV_d_sig_d_sig)
            rel_err_d2_mu_n__DIV_d_mu_d_sig =np.divide(dd['d2_mu_n__DIV_d_mu_d_sig' ]-(dd_epssig2['d_mu_n__DIV_d_mu' ]-dd['d_mu_n__DIV_d_mu' ])/eps_sig,abs(dd['d2_mu_n__DIV_d_mu_d_sig' ]));print("rel_err_d2_mu_n__DIV_d_mu_d_sig =",rel_err_d2_mu_n__DIV_d_mu_d_sig)
            list_rel_err_NB34     +=list(rel_err_d_mu_n__DIV_d_mu[2:])+list(rel_err_d_mu_n__DIV_d_sig[2:])+list(rel_err_d2_mu_n__DIV_d_mu_d_mu[2:])+list(rel_err_d2_mu_n__DIV_d_sig_d_sig[2:])+list(rel_err_d2_mu_n__DIV_d_mu_d_sig[2:]) # for derivatives ignore first two central moments n=0,1 (as they are constant 1 or 0 such that the derivatives will be zero)
            list_rel_err_NB34_vals+=list(    dd['d_mu_n__DIV_d_mu'][2:])+list(  dd['d_mu_n__DIV_d_sig'][2:])+list(  dd['d2_mu_n__DIV_d_mu_d_mu'][2:])+list(  dd['d2_mu_n__DIV_d_sig_d_sig'][2:])+list(  dd['d2_mu_n__DIV_d_mu_d_sig'][2:])
            print("max(list_rel_err_NB34)=",np.max(np.abs(list_rel_err_NB34)),"check list lengths:",len(list_rel_err_NB34),len(list_rel_err_NB34_vals))
            
            print("\nI.e) Test: F_tilde and derivatives (only derivatives are compared against numerical approximations")
            print("Ft                   =",dd['Ft'])
            print("d_Ft_DIV_d_mu        =",dd['d_Ft_DIV_d_mu'])
            print("d_Ft_DIV_d_sig       =",dd['d_Ft_DIV_d_sig'])
            print("d2_Ft_DIV_d_mu_d_mu  =",dd['d2_Ft_DIV_d_mu_d_mu'])
            print("d2_Ft_DIV_d_sig_d_sig=",dd['d2_Ft_DIV_d_sig_d_sig'])
            print("d2_Ft_DIV_d_mu_d_sig =",dd['d2_Ft_DIV_d_mu_d_sig'])
            rel_err_d_Ft_DIV_d_mu        =np.divide(dd['d_Ft_DIV_d_mu'        ]-(dd_epsmu  ['Ft'            ]-dd['Ft'            ])/eps    ,abs(dd['d_Ft_DIV_d_mu'        ]));print("rel_err_d_Ft_DIV_d_mu        =",rel_err_d_Ft_DIV_d_mu)
            rel_err_d_Ft_DIV_d_sig       =np.divide(dd['d_Ft_DIV_d_sig'       ]-(dd_epssig2['Ft'            ]-dd['Ft'            ])/eps_sig,abs(dd['d_Ft_DIV_d_sig'       ]));print("rel_err_d_Ft_DIV_d_sig       =",rel_err_d_Ft_DIV_d_sig)
            rel_err_d2_Ft_DIV_d_mu_d_mu  =np.divide(dd['d2_Ft_DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_Ft_DIV_d_mu' ]-dd['d_Ft_DIV_d_mu' ])/eps    ,abs(dd['d2_Ft_DIV_d_mu_d_mu'  ]));print("rel_err_d2_Ft_DIV_d_mu_d_mu  =",rel_err_d2_Ft_DIV_d_mu_d_mu)
            rel_err_d2_Ft_DIV_d_sig_d_sig=np.divide(dd['d2_Ft_DIV_d_sig_d_sig']-(dd_epssig2['d_Ft_DIV_d_sig']-dd['d_Ft_DIV_d_sig'])/eps_sig,abs(dd['d2_Ft_DIV_d_sig_d_sig']));print("rel_err_d2_Ft_DIV_d_sig_d_sig=",rel_err_d2_Ft_DIV_d_sig_d_sig)
            rel_err_d2_Ft_DIV_d_mu_d_sig =np.divide(dd['d2_Ft_DIV_d_mu_d_sig' ]-(dd_epssig2['d_Ft_DIV_d_mu' ]-dd['d_Ft_DIV_d_mu' ])/eps_sig,abs(dd['d2_Ft_DIV_d_mu_d_sig' ]));print("rel_err_d2_Ft_DIV_d_mu_d_sig =",rel_err_d2_Ft_DIV_d_mu_d_sig)
            ixOK=np.logical_not(np.isnan(dd['F']))   # kick out nan in list of relative errors
            list_rel_err_NB34     +=list(rel_err_d_Ft_DIV_d_mu[ixOK].flat)+list(rel_err_d_Ft_DIV_d_sig[ixOK].flat)+list(rel_err_d2_Ft_DIV_d_mu_d_mu[ixOK].flat)+list(rel_err_d2_Ft_DIV_d_sig_d_sig[ixOK].flat)+list(rel_err_d2_Ft_DIV_d_mu_d_sig[ixOK].flat)
            list_rel_err_NB34_vals+=list(    dd['d_Ft_DIV_d_mu'][ixOK].flat)+list(  dd['d_Ft_DIV_d_sig'][ixOK].flat)+list(  dd['d2_Ft_DIV_d_mu_d_mu'][ixOK].flat)+list(  dd['d2_Ft_DIV_d_sig_d_sig'][ixOK].flat)+list(  dd['d2_Ft_DIV_d_mu_d_sig'][ixOK].flat)
            print("max(list_rel_err_NB34)=",np.max(np.abs(list_rel_err_NB34)),"check list lengths:",len(list_rel_err_NB34),len(list_rel_err_NB34_vals))
            
            print("\nI.f) Test: M_n_ and derivatives (M_n_ is compared against previous computation, and derivatives are compared against numerical approximations")
            print("M_n_                   =",dd['M_n_'])
            print("d_M_n__DIV_d_mu        =",dd['d_M_n__DIV_d_mu'])
            print("d_M_n__DIV_d_sig       =",dd['d_M_n__DIV_d_sig'])
            print("d2_M_n__DIV_d_mu_d_mu  =",dd['d2_M_n__DIV_d_mu_d_mu'])
            print("d2_M_n__DIV_d_sig_d_sig=",dd['d2_M_n__DIV_d_sig_d_sig'])
            print("d2_M_n__DIV_d_mu_d_sig =",dd['d2_M_n__DIV_d_mu_d_sig'])
            rel_err_d_M_n__DIV_d_mu        =np.divide(dd['d_M_n__DIV_d_mu'        ]-(dd_epsmu  ['M_n_'            ]-dd['M_n_'            ])/eps    , abs(dd['d_M_n__DIV_d_mu'        ]));print("rel_err_d_M_n__DIV_d_mu        =",rel_err_d_M_n__DIV_d_mu)
            rel_err_d_M_n__DIV_d_sig       =np.divide(dd['d_M_n__DIV_d_sig'       ]-(dd_epssig2['M_n_'            ]-dd['M_n_'            ])/eps_sig, abs(dd['d_M_n__DIV_d_sig'       ]));print("rel_err_d_M_n__DIV_d_sig       =",rel_err_d_M_n__DIV_d_sig)
            rel_err_d2_M_n__DIV_d_mu_d_mu  =np.divide(dd['d2_M_n__DIV_d_mu_d_mu'  ]-(dd_epsmu  ['d_M_n__DIV_d_mu' ]-dd['d_M_n__DIV_d_mu' ])/eps    , abs(dd['d2_M_n__DIV_d_mu_d_mu'  ]));print("rel_err_d2_M_n__DIV_d_mu_d_mu  =",rel_err_d2_M_n__DIV_d_mu_d_mu)
            rel_err_d2_M_n__DIV_d_sig_d_sig=np.divide(dd['d2_M_n__DIV_d_sig_d_sig']-(dd_epssig2['d_M_n__DIV_d_sig']-dd['d_M_n__DIV_d_sig'])/eps_sig, abs(dd['d2_M_n__DIV_d_sig_d_sig']));print("rel_err_d2_M_n__DIV_d_sig_d_sig=",rel_err_d2_M_n__DIV_d_sig_d_sig)
            rel_err_d2_M_n__DIV_d_mu_d_sig =np.divide(dd['d2_M_n__DIV_d_mu_d_sig' ]-(dd_epssig2['d_M_n__DIV_d_mu' ]-dd['d_M_n__DIV_d_mu' ])/eps_sig, abs(dd['d2_M_n__DIV_d_mu_d_sig' ]));print("rel_err_d2_M_n__DIV_d_mu_d_sig =",rel_err_d2_M_n__DIV_d_mu_d_sig)
            list_rel_err_NB34     +=list(rel_err_d_M_n__DIV_d_mu[1:])+list(rel_err_d_M_n__DIV_d_sig[1:])+list(rel_err_d2_M_n__DIV_d_mu_d_mu[1:])+list(rel_err_d2_M_n__DIV_d_sig_d_sig[1:])+list(rel_err_d2_M_n__DIV_d_mu_d_sig[1:]) # for derivatives ignore first two central moments n=0,1 (as they are constant 1 or 0 such that the derivatives will be zero)
            list_rel_err_NB34_vals+=list(    dd['d_M_n__DIV_d_mu'][1:])+list(  dd['d_M_n__DIV_d_sig'][1:])+list(  dd['d2_M_n__DIV_d_mu_d_mu'][1:])+list(  dd['d2_M_n__DIV_d_sig_d_sig'][1:])+list(  dd['d2_M_n__DIV_d_mu_d_sig'][1:]) 
            print("max(list_rel_err_NB34)=",np.max(np.abs(list_rel_err_NB34)),"check list lengths:",len(list_rel_err_NB34),len(list_rel_err_NB34_vals))
            
            print("\nII) Verify results Part II (NB36):")
            print("-------------------------------------------------")
            eps_D         = np.array([eps,eps,eps])                # for division for numerical 1st derivatives 
            eps_DD        = np.array([eps,eps,eps,eps,eps,eps])    # for division for numerical 2nd derivatives
            eps_D_epssig  = np.array([eps,eps_sig,eps])            # as eps_D, but if 
            eps_DD_epssig = np.array([eps,eps_sig,eps,eps,eps,eps])
            ddeD =[dd_epsmu,dd_epssig2,dd_epsN]                             # data using for 1st numerical derivatives  (corresponding to denominator of derivatives)
            ddeDD =[dd_epsmu,dd_epssig2,dd_epsN,dd_epssig2,dd_epsN,dd_epsN] # data using for 2nd numerical derivatives (corresponding to denominator of derivatives)
            ddeDDi=[0,1,2,0,0,1]                                            # index using for 2nd numerical derivative (corresponding to index of numerator derivatives)
            
            print("\nII.a) Test: derivatives of functions of raw moments (NB36/p3/(37-40))")
            print("D_M1_=",dd['D_M1_'])
            print("D_M2_=",dd['D_M2_'])
            print("D_M3_=",dd['D_M3_'])
            print("D_M4_=",dd['D_M4_'])
            D_M1_num = np.array([(dde['M_n_'][1]-dd['M_n_'][1])/eps for dde in ddeD]) # numeric derivatives of M1_
            D_M2_num = np.array([(dde['M_n_'][2]-dd['M_n_'][2])/eps for dde in ddeD]) # numeric derivatives of M2_
            D_M3_num = np.array([(dde['M_n_'][3]-dd['M_n_'][3])/eps for dde in ddeD]) # numeric derivatives of M3_
            D_M4_num = np.array([(dde['M_n_'][4]-dd['M_n_'][4])/eps for dde in ddeD]) # numeric derivatives of M4_
            rel_err_D_M1_=np.divide(dd['D_M1_']-D_M1_num,np.maximum(1e-12,np.abs(dd['D_M1_']))); print("rel_err_D_M1_=",rel_err_D_M1_)
            rel_err_D_M2_=np.divide(dd['D_M2_']-D_M2_num,np.maximum(1e-12,np.abs(dd['D_M2_']))); print("rel_err_D_M2_=",rel_err_D_M2_)
            rel_err_D_M3_=np.divide(dd['D_M3_']-D_M3_num,np.maximum(1e-12,np.abs(dd['D_M3_']))); print("rel_err_D_M3_=",rel_err_D_M3_)
            rel_err_D_M4_=np.divide(dd['D_M4_']-D_M4_num,np.maximum(1e-12,np.abs(dd['D_M4_']))); print("rel_err_D_M4_=",rel_err_D_M4_)
            list_rel_err_NB36     +=list(rel_err_D_M1_)+list(rel_err_D_M2_)+list(rel_err_D_M3_)+list(rel_err_D_M4_)
            list_rel_err_NB36_vals+=list(    dd['D_M1_'])+list(  dd['D_M2_'])+list(  dd['D_M3_'])+list(  dd['D_M4_'])
            print("DD_M1_=",dd['DD_M1_'])
            print("DD_M2_=",dd['DD_M2_'])
            print("DD_M3_=",dd['DD_M3_'])
            print("DD_M4_=",dd['DD_M4_'])
            DD_M1_num = np.array([(ddeDD[i]['D_M1_'][ddeDDi[i]]-dd['D_M1_'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M1_
            DD_M2_num = np.array([(ddeDD[i]['D_M2_'][ddeDDi[i]]-dd['D_M2_'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M2_
            DD_M3_num = np.array([(ddeDD[i]['D_M3_'][ddeDDi[i]]-dd['D_M3_'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M3_
            DD_M4_num = np.array([(ddeDD[i]['D_M4_'][ddeDDi[i]]-dd['D_M4_'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M4_
            rel_err_DD_M1_=np.divide(dd['DD_M1_']-DD_M1_num,np.maximum(1e-12,np.abs(dd['DD_M1_']))); print("rel_err_DD_M1_        =",rel_err_DD_M1_) 
            rel_err_DD_M2_=np.divide(dd['DD_M2_']-DD_M2_num,np.maximum(1e-12,np.abs(dd['DD_M2_']))); print("rel_err_DD_M2_        =",rel_err_DD_M2_)
            rel_err_DD_M3_=np.divide(dd['DD_M3_']-DD_M3_num,np.maximum(1e-12,np.abs(dd['DD_M3_']))); print("rel_err_DD_M3_        =",rel_err_DD_M3_)
            rel_err_DD_M4_=np.divide(dd['DD_M4_']-DD_M4_num,np.maximum(1e-12,np.abs(dd['DD_M4_']))); print("rel_err_DD_M4_        =",rel_err_DD_M4_)
            list_rel_err_NB36     +=list(rel_err_DD_M1_)+list(rel_err_DD_M2_)+list(rel_err_DD_M3_)+list(rel_err_DD_M4_)
            list_rel_err_NB36_vals+=list(    dd['DD_M1_'])+list(  dd['DD_M2_'])+list(  dd['DD_M3_'])+list(  dd['DD_M4_'])
            print("D_M2_2    =",dd['D_M2_2'])
            print("D_M1__M3_ =",dd['D_M1__M3_'])
            print("D_M1_2_M2_=",dd['D_M1_2_M2_'])
            print("D_M1_4    =",dd['D_M1_4'])
            D_M2_2_num    = np.array([(dde['M_n_'][2]**2               -dd['M_n_'][2]**2              )/eps for dde in ddeD])
            D_M1__M3_num  = np.array([(dde['M_n_'][1]*dde['M_n_'][3]   -dd['M_n_'][1]*dd['M_n_'][3]   )/eps for dde in ddeD])
            D_M1_2_M2_num = np.array([(dde['M_n_'][1]**2*dde['M_n_'][2]-dd['M_n_'][1]**2*dd['M_n_'][2])/eps for dde in ddeD])
            D_M1_4_num    = np.array([(dde['M_n_'][1]**4               -dd['M_n_'][1]**4              )/eps for dde in ddeD])
            rel_err_D_M2_2    =np.divide(dd['D_M2_2'    ]-D_M2_2_num   ,np.maximum(1e-12,np.abs(dd['D_M2_2'    ]))); print("rel_err_D_M2_2    =",rel_err_D_M2_2)
            rel_err_D_M1__M3_ =np.divide(dd['D_M1__M3_' ]-D_M1__M3_num ,np.maximum(1e-12,np.abs(dd['D_M1__M3_' ]))); print("rel_err_D_M1__M3_ =",rel_err_D_M1__M3_)
            rel_err_D_M1_2_M2_=np.divide(dd['D_M1_2_M2_']-D_M1_2_M2_num,np.maximum(1e-12,np.abs(dd['D_M1_2_M2_']))); print("rel_err_D_M1_2_M2_=",rel_err_D_M1_2_M2_)
            rel_err_D_M1_4    =np.divide(dd['D_M1_4'    ]-D_M1_4_num   ,np.maximum(1e-12,np.abs(dd['D_M1_4'    ]))); print("rel_err_D_M1_4    =",rel_err_D_M1_4)
            list_rel_err_NB36     +=list(rel_err_D_M2_2)+list(rel_err_D_M1__M3_)+list(rel_err_D_M1_2_M2_)+list(rel_err_D_M1_4)
            list_rel_err_NB36_vals+=list(    dd['D_M2_2'])+list(  dd['D_M1__M3_'])+list(  dd['D_M1_2_M2_'])+list(  dd['D_M1_4'])
            print("DD_M2_2    =",dd['DD_M2_2'])
            print("DD_M1__M3_ =",dd['DD_M1__M3_'])
            print("DD_M1_2_M2_=",dd['DD_M1_2_M2_'])
            print("DD_M1_4    =",dd['DD_M1_4'])
            DD_M2_2_num    = np.array([(ddeDD[i]['D_M2_2'    ][ddeDDi[i]]-dd['D_M2_2'    ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M2_2
            DD_M1__M3_num  = np.array([(ddeDD[i]['D_M1__M3_' ][ddeDDi[i]]-dd['D_M1__M3_' ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M1__M3_
            DD_M1_2_M2_num = np.array([(ddeDD[i]['D_M1_2_M2_'][ddeDDi[i]]-dd['D_M1_2_M2_'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M1_2_M2_
            DD_M1_4_num    = np.array([(ddeDD[i]['D_M1_4'    ][ddeDDi[i]]-dd['D_M1_4'    ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of M1_4
            rel_err_DD_M2_2    =np.divide(dd['DD_M2_2'    ]-DD_M2_2_num   ,np.maximum(1e-12,np.abs(dd['DD_M2_2'    ]))); print("rel_err_DD_M2_2    =",rel_err_DD_M2_2) 
            rel_err_DD_M1__M3_ =np.divide(dd['DD_M1__M3_' ]-DD_M1__M3_num ,np.maximum(1e-12,np.abs(dd['DD_M1__M3_' ]))); print("rel_err_DD_M1__M3_ =",rel_err_DD_M1__M3_) 
            rel_err_DD_M1_2_M2_=np.divide(dd['DD_M1_2_M2_']-DD_M1_2_M2_num,np.maximum(1e-12,np.abs(dd['DD_M1_2_M2_']))); print("rel_err_DD_M1_2_M2_=",rel_err_DD_M1_2_M2_) 
            rel_err_DD_M1_4    =np.divide(dd['DD_M1_4'    ]-DD_M1_4_num   ,np.maximum(1e-12,np.abs(dd['DD_M1_4'    ]))); print("rel_err_DD_M1_4    =",rel_err_DD_M1_4) 
            list_rel_err_NB36     +=list(rel_err_DD_M2_2)+list(rel_err_DD_M1__M3_)+list(rel_err_DD_M1_2_M2_)+list(rel_err_DD_M1_4)
            list_rel_err_NB36_vals+=list(    dd['DD_M2_2'])+list(  dd['DD_M1__M3_'])+list(  dd['DD_M1_2_M2_'])+list(  dd['DD_M1_4'])
            print("max(list_rel_err_NB36)=",np.max(np.abs(list_rel_err_NB36)),"check list lengths:",len(list_rel_err_NB36),len(list_rel_err_NB36_vals))
            
            print("\nII.b) Test: model predictions and their derivatives (NB36/p2/(12-25))")
            print("mu_  =",dd['mu_'])
            print("sig2_=",dd['sig2_'])
            print("N_   =",dd['N_'])
            print("D_mu_  =",dd['D_mu_'])
            print("D_sig2_=",dd['D_sig2_'])
            print("D_N_   =",dd['D_N_'])
            print("DD_mu_  =",dd['DD_mu_'])
            print("DD_sig2_=",dd['DD_sig2_'])
            print("DD_N_   =",dd['DD_N_'])
            D_mu_num   = np.array([(dde['mu_'  ]-dd['mu_'  ])/eps for dde in ddeD]) # numeric derivatives of mu_
            D_sig2_num = np.array([(dde['sig2_']-dd['sig2_'])/eps for dde in ddeD]) # numeric derivatives of sig2_
            D_N_num    = np.array([(dde['N_'   ]-dd['N_'   ])/eps for dde in ddeD]) # numeric derivatives of N_
            DD_mu_num   = np.array([(ddeDD[i]['D_mu_'  ][ddeDDi[i]]-dd['D_mu_'  ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of mu_
            DD_sig2_num = np.array([(ddeDD[i]['D_sig2_'][ddeDDi[i]]-dd['D_sig2_'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of sig2_
            DD_N_num    = np.array([(ddeDD[i]['D_N_'   ][ddeDDi[i]]-dd['D_N_'   ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of N_
            rel_err_D_mu_  =np.divide(dd['D_mu_'  ]-D_mu_num  ,np.maximum(1e-12,np.abs(dd['D_mu_'  ]))); print("rel_err_D_mu_  =",rel_err_D_mu_)
            rel_err_D_sig2_=np.divide(dd['D_sig2_']-D_sig2_num,np.maximum(1e-12,np.abs(dd['D_sig2_']))); print("rel_err_D_sig2_=",rel_err_D_sig2_)
            rel_err_D_N_   =np.divide(dd['D_N_'   ]-D_N_num   ,np.maximum(1e-12,np.abs(dd['D_N_'   ]))); print("rel_err_D_N_   =",rel_err_D_N_)
            rel_err_DD_mu_  =np.divide(dd['DD_mu_'  ]-DD_mu_num  ,np.maximum(1e-12,np.abs(dd['DD_mu_'  ]))); print("rel_err_DD_mu_  =",rel_err_DD_mu_)
            rel_err_DD_sig2_=np.divide(dd['DD_sig2_']-DD_sig2_num,np.maximum(1e-12,np.abs(dd['DD_sig2_']))); print("rel_err_DD_sig2_=",rel_err_DD_sig2_)
            rel_err_DD_N_   =np.divide(dd['DD_N_'   ]-DD_N_num   ,np.maximum(1e-12,np.abs(dd['DD_N_'   ]))); print("rel_err_DD_N_   =",rel_err_DD_N_)
            list_rel_err_NB36     +=list(rel_err_D_mu_)+list(rel_err_D_sig2_)+list(rel_err_D_N_)+list(rel_err_DD_mu_)+list(rel_err_DD_sig2_)+list(rel_err_DD_N_)
            list_rel_err_NB36_vals+=list(    dd['D_mu_'])+list(  dd['D_sig2_'])+list(  dd['D_N_'])+list(  dd['DD_mu_'])+list(  dd['DD_sig2_'])+list(dd['DD_N_'])
            print("max(list_rel_err_NB36)=",np.max(np.abs(list_rel_err_NB36)),"check list lengths:",len(list_rel_err_NB36),len(list_rel_err_NB36_vals))
            
            print("\nII.c) Test: variances and their derivatives (NB36/p3/(26-40))")
            print("var_mu__bar  =",dd['var_mu__bar'])
            print("var_sig2__bar=",dd['var_sig2__bar'])
            print("var_N__bar   =",dd['var_N__bar'])
            print("D_var_mu__bar  =",dd['D_var_mu__bar'])
            print("D_var_sig2__bar=",dd['D_var_sig2__bar'])
            print("D_var_N__bar   =",dd['D_var_N__bar'])
            print("DD_var_mu__bar  =",dd['DD_var_mu__bar'])
            print("DD_var_sig2__bar=",dd['DD_var_sig2__bar'])
            print("DD_var_N__bar   =",dd['DD_var_N__bar'])
            D_var_mu__bar_num   = np.array([(dde['var_mu__bar'  ]-dd['var_mu__bar'  ])/eps for dde in ddeD]) # numeric derivatives of var_mu__bar
            D_var_sig2__bar_num = np.array([(dde['var_sig2__bar']-dd['var_sig2__bar'])/eps for dde in ddeD]) # numeric derivatives of var_sig2__bar
            D_var_N__bar_num    = np.array([(dde['var_N__bar'   ]-dd['var_N__bar'   ])/eps for dde in ddeD]) # numeric derivatives of var_N__bar
            DD_var_mu__bar_num   = np.array([(ddeDD[i]['D_var_mu__bar'  ][ddeDDi[i]]-dd['D_var_mu__bar'  ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of var_mu__bar
            DD_var_sig2__bar_num = np.array([(ddeDD[i]['D_var_sig2__bar'][ddeDDi[i]]-dd['D_var_sig2__bar'][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of var_sig2__bar
            DD_var_N__bar_num    = np.array([(ddeDD[i]['D_var_N__bar'   ][ddeDDi[i]]-dd['D_var_N__bar'   ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of var_N__bar
            rel_err_D_var_mu__bar  =np.divide(dd['D_var_mu__bar'  ]-D_var_mu__bar_num  ,np.maximum(1e-12,np.abs(dd['D_var_mu__bar'  ]))); print("rel_err_D_var_mu__bar  =",rel_err_D_var_mu__bar)
            rel_err_D_var_sig2__bar=np.divide(dd['D_var_sig2__bar']-D_var_sig2__bar_num,np.maximum(1e-12,np.abs(dd['D_var_sig2__bar']))); print("rel_err_D_var_sig2__bar=",rel_err_D_var_sig2__bar)
            rel_err_D_var_N__bar   =np.divide(dd['D_var_N__bar'   ]-D_var_N__bar_num   ,np.maximum(1e-12,np.abs(dd['D_var_N__bar'   ]))); print("rel_err_D_var_N__bar   =",rel_err_D_var_N__bar)
            rel_err_DD_var_mu__bar  =np.divide(dd['DD_var_mu__bar'  ]-DD_var_mu__bar_num  ,np.maximum(1e-12,np.abs(dd['DD_var_mu__bar'  ]))); print("rel_err_DD_var_mu__bar  =",rel_err_DD_var_mu__bar)
            rel_err_DD_var_sig2__bar=np.divide(dd['DD_var_sig2__bar']-DD_var_sig2__bar_num,np.maximum(1e-12,np.abs(dd['DD_var_sig2__bar']))); print("rel_err_DD_var_sig2__bar=",rel_err_DD_var_sig2__bar)
            rel_err_DD_var_N__bar   =np.divide(dd['DD_var_N__bar'   ]-DD_var_N__bar_num   ,np.maximum(1e-12,np.abs(dd['DD_var_N__bar'   ]))); print("rel_err_DD_var_N__bar   =",rel_err_DD_var_N__bar)
            list_rel_err_NB36     +=list(rel_err_D_var_mu__bar)+list(rel_err_D_var_sig2__bar)+list(rel_err_D_var_N__bar)+list(rel_err_DD_var_mu__bar)+list(rel_err_DD_var_sig2__bar)+list(rel_err_DD_var_N__bar)   
            list_rel_err_NB36_vals+=list(    dd['D_var_mu__bar'])+list(  dd['D_var_sig2__bar'])+list(  dd['D_var_N__bar'])+list(  dd['DD_var_mu__bar'])+list(  dd['DD_var_sig2__bar'])+list(  dd['DD_var_N__bar'])   
            print("max(list_rel_err_NB36)=",np.max(np.abs(list_rel_err_NB36)),"check list lengths:",len(list_rel_err_NB36),len(list_rel_err_NB36_vals))
            
            print("\nII.d) Test: error function and its derivatives (NB36/p1-2/(1)-(11)")
            print("Q_mu   =",dd['Q_mu'])
            print("Q_sig2   =",dd['Q_sig2'])
            print("Q_N   =",dd['Q_N'])
            print("D_Q_mu   =",dd['D_Q_mu'])
            print("D_Q_sig2   =",dd['D_Q_sig2'])
            print("D_Q_N   =",dd['D_Q_N'])
            print("E   =",dd['E'])
            print("D_E =",dd['D_E'])
            print("DD_E=",dd['DD_E'])
            D_Q_mu_num   =np.array([(dde['Q_mu'  ]-dd['Q_mu'  ])/eps for dde in ddeD]) # numeric derivatives of Q_mu
            D_Q_sig2_num =np.array([(dde['Q_sig2']-dd['Q_sig2'])/eps for dde in ddeD]) # numeric derivatives of Q_sig2
            D_Q_N_num    =np.array([(dde['Q_N'   ]-dd['Q_N'   ])/eps for dde in ddeD]) # numeric derivatives of Q_N
            D_E_num =np.array([(dde['E']-dd['E'])/eps for dde in ddeD]) # numeric derivatives of E
            DD_E_num=np.array([(ddeDD[i]['D_E'   ][ddeDDi[i]]-dd['D_E'   ][ddeDDi[i]])/eps for i in range(len(ddeDD))]) # 2nd numeric derivatives of E
            rel_err_D_Q_mu  =np.divide(dd['D_Q_mu'  ]-D_Q_mu_num  ,np.maximum(1e-12,np.abs(dd['D_Q_mu'  ]))); print("rel_err_D_Q_mu  =",rel_err_D_Q_mu)
            rel_err_D_Q_sig2=np.divide(dd['D_Q_sig2']-D_Q_sig2_num,np.maximum(1e-12,np.abs(dd['D_Q_sig2']))); print("rel_err_D_Q_sig2=",rel_err_D_Q_sig2)
            rel_err_D_Q_N   =np.divide(dd['D_Q_N'   ]-D_Q_N_num   ,np.maximum(1e-12,np.abs(dd['D_Q_N'   ]))); print("rel_err_D_Q_N   =",rel_err_D_Q_N)
            rel_err_D_E =np.divide(dd['D_E' ]-D_E_num ,np.maximum(1e-12,np.abs(dd['D_E' ]))); print("rel_err_D_E =",rel_err_D_E)
            rel_err_DD_E=np.divide(dd['DD_E']-DD_E_num,np.maximum(1e-12,np.abs(dd['DD_E']))); print("rel_err_DD_E=",rel_err_DD_E)
            list_rel_err_NB36     +=list(rel_err_D_Q_mu)+list(rel_err_D_Q_sig2)+list(rel_err_D_Q_N)+list(rel_err_D_E)+list(rel_err_DD_E)
            list_rel_err_NB36_vals+=list(    dd['D_Q_mu'])+list(  dd['D_Q_sig2'])+list(  dd['D_Q_N'])+list(  dd['D_E'])+list(  dd['DD_E'])
            print("max(list_rel_err_NB36)=",np.max(np.abs(list_rel_err_NB36)),"check list lengths:",len(list_rel_err_NB36),len(list_rel_err_NB36_vals))
            
            print("\nIII)FinalOverview of relativ errors:")
            print("---------------------------------------")
            print("mu=",mu,"sig=",sig,"a=",a,"b=",b,"N=",N,"mu__bar=",mu__bar,"sig__bar=",sig__bar,"N__bar=",N__bar)
            print("lmbda_mu=",lmbda_mu,"lmbda_sig2=",lmbda_sig2,"lmbda_N=",lmbda_N)
            print("eps=",eps,"eps_sig=",eps_sig)
            print("alpha=",(a-mu)/sig,"beta=",(b-mu)/sig)
            list_rel_err_abs_NB34=np.abs(list_rel_err_NB34)
            list_rel_err_abs_NB36=np.abs(list_rel_err_NB36)
            print("max(list_rel_err_NB34)=",np.max(list_rel_err_abs_NB34))
            print("max(list_rel_err_NB36)=",np.max(list_rel_err_abs_NB36))
            th=1e-3
            print("Threshold rel_err>",th)
            ix_bad_NB34=list_rel_err_abs_NB34>th
            ix_bad_NB36=list_rel_err_abs_NB36>th
            n_bad_NB34=len(np.array(list_rel_err_NB34)>th)
            print("n_bad_NB34=",np.sum(ix_bad_NB34), "n_bad_NB36=",np.sum(ix_bad_NB36))
            print("bad rel err NB34=",np.array(list_rel_err_NB34)     [ix_bad_NB34])
            print("bad val     NB34=",np.array(list_rel_err_NB34_vals)[ix_bad_NB34])
            print("bad rel err NB36=",np.array(list_rel_err_NB36)     [ix_bad_NB36])
            print("bad val     NB36=",np.array(list_rel_err_NB36_vals)[ix_bad_NB36])

        if select_tests["deriv_trunc_gauss_arr"]>0: 
            print("\nIV)Comparison of getDerivatives4TruncatedGaussiansError(.) vs. getDerivatives4TruncatedGaussiansError_arr(.):")
            print("-------------------------------------------------------------------------------------------------------------------")
            print("a) for array size 1 (same values as before)")
            print("---------------------------------------------")
            print("\ndd['alpha']=",dd['alpha']);print("dd_arr['alpha']=",dd_arr['alpha'])
            print("\ndd['f']=",dd['f']);print("dd_arr['f']=",dd_arr['f'])
            print("\ndd['gamma']=",dd['gamma']);print("dd_arr['gamma']=",dd_arr['gamma'])
            print("\ndd['S']=",dd['S']);print("dd_arr['S']=",dd_arr['S'])
            print("\ndd['F']=",dd['F']);print("dd_arr['F']=",dd_arr['F'])
            print("\ndd['G']=",dd['G']);print("dd_arr['G']=",dd_arr['G'])
            print("\ndd['mu_n_']=",dd['mu_n_']);print("dd_arr['mu_n_']=",dd_arr['mu_n_'])
            print("\ndd['Ft']=",dd['Ft']);print("dd_arr['Ft']=",dd_arr['Ft'])
            print("\ndd['M_n_']=",dd['M_n_']);print("dd_arr['M_n_']=",dd_arr['M_n_'])
            print("\ndd['mu_']=",dd['mu_']);print("dd_arr['mu_']=",dd_arr['mu_'])
            print("\ndd['sig2_']=",dd['sig2_']);print("dd_arr['sig2_']=",dd_arr['sig2_'])
            print("\ndd['N_']=",dd['N_']);print("dd_arr['N_']=",dd_arr['N_'])
            print("\ndd['var_mu__bar']=",dd['var_mu__bar']);print("dd_arr['var_mu__bar']=",dd_arr['var_mu__bar'])
            print("\ndd['var_sig2__bar']=",dd['var_sig2__bar']);print("dd_arr['var_sig2__bar']=",dd_arr['var_sig2__bar'])
            print("\ndd['var_N__bar']=",dd['var_N__bar']);print("dd_arr['var_N__bar']=",dd_arr['var_N__bar'])
            
            print("\ndd['D_mu_']=",dd['D_mu_']);print("dd_arr['D_mu_']=",dd_arr['D_mu_'])
            print("\ndd['D_sig2_']=",dd['D_sig2_']);print("dd_arr['D_sig2_']=",dd_arr['D_sig2_'])
            print("\ndd['D_N_']=",dd['D_N_']);print("dd_arr['D_N_']=",dd_arr['D_N_'])
            print("\ndd['D_var_mu__bar']=",dd['D_var_mu__bar']);print("dd_arr['D_var_mu__bar']=",dd_arr['D_var_mu__bar'])
            print("\ndd['D_var_sig2__bar']=",dd['D_var_sig2__bar']);print("dd_arr['D_var_sig2__bar']=",dd_arr['D_var_sig2__bar'])
            print("\ndd['D_var_N__bar']=",dd['D_var_N__bar']);print("dd_arr['D_var_N__bar']=",dd_arr['D_var_N__bar'])
            
            print("\ndd['DD_mu_']=",dd['DD_mu_']);print("dd_arr['DD_mu_']=",dd_arr['DD_mu_'])
            print("\ndd['DD_sig2_']=",dd['DD_sig2_']);print("dd_arr['DD_sig2_']=",dd_arr['DD_sig2_'])
            print("\ndd['DD_N_']=",dd['DD_N_']);print("dd_arr['DD_N_']=",dd_arr['DD_N_'])
            print("\ndd['DD_var_mu__bar']=",dd['DD_var_mu__bar']);print("dd_arr['DD_var_mu__bar']=",dd_arr['DD_var_mu__bar'])
            print("\ndd['DD_var_sig2__bar']=",dd['DD_var_sig2__bar']);print("dd_arr['DD_var_sig2__bar']=",dd_arr['DD_var_sig2__bar'])
            print("\ndd['DD_var_N__bar']=",dd['DD_var_N__bar']);print("dd_arr['DD_var_N__bar']=",dd_arr['DD_var_N__bar'])
            
        
            print("\ndd['E']=",dd['E']);print("dd_arr['E']=",dd_arr['E'])
            print("\ndd['D_E']=",dd['D_E']); print("dd_arr['D_E']=",dd_arr['D_E'])
            print("\ndd['DD_E']=",dd['DD_E']);print("dd_arr['DD_E']=",dd_arr['DD_E'])
            
            
            print("\nb) for many iterations")
            # Performance Test
            n_iter=30
            flagRand=1
            if flagRand==1:
                mu,sig,N = 3*np.random.randn(n_iter), abs(2*np.random.randn(n_iter)), abs(20+2*np.random.randn(n_iter))
                a,b = mu-3*sig+np.random.rand(n_iter)*6*sig, mu-3*sig+np.random.rand(n_iter)*6*sig
                a,b = np.minimum(a,b),np.maximum(a,b)
                mu__bar,sig__bar,N__bar = a+np.random.rand(n_iter)*(b-a), 0.5*np.random.rand(n_iter)*(b-a), abs(20+2*np.random.randn(n_iter))
                lmbda_mu,lmbda_sig2,lmbda_N=1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand()   # keep fixed
                
            if flagRand==2:
                mu,sig,N = 3*np.random.randn(n_iter), abs(2*np.random.randn(n_iter)), abs(20+2*np.random.randn(n_iter))
                a,b = mu-2*sig+np.random.rand(n_iter)*2*sig, mu-2*sig+np.random.rand(n_iter)*2*sig
                a,b = np.minimum(a,b),np.maximum(a,b)
                mu__bar,sig__bar,N__bar = a+np.random.rand(n_iter)*(b-a), 0.5*(0.2+np.random.rand(n_iter))*(b-a), abs(20+2*np.random.randn(n_iter))
                lmbda_mu,lmbda_sig2,lmbda_N=1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand()
            
            sig2=np.multiply(sig,sig)
            sig2__bar=np.multiply(sig__bar,sig__bar)
            print("mu=",mu)
            print("sig=",sig)
            print("N=",N)
            print("a=",a)
            print("b=",b)
            print("mu__bar=",mu__bar)
            print("sig__bar=",sig__bar)
            print("N__bar=",N__bar)
            print("\nTest getDerivatives4TruncatedGaussiansError(.) for n_iter=",n_iter)
            E_seq=np.empty(n_iter)
            DE_seq=np.empty((3,n_iter))
            DDE_seq=np.empty((6,n_iter))
            t1=clock()
            for i in range(n_iter):
                E_seq[i],DE_seq[:,i],DDE_seq[:,i]=getDerivatives4TruncatedGaussiansError(mu[i],sig2[i],N[i],a[i],b[i],mu__bar[i],sig2__bar[i],N__bar[i],lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=1)
            t2=clock()
            dt_seq=t2-t1    # time for sequential processing
            print("dt_seq=",dt_seq)
            print("\nTest getDerivatives4TruncatedGaussiansError_arr(.) for n_iter=",n_iter)
            t1=clock()
            E_arr,DE_arr,DDE_arr=getDerivatives4TruncatedGaussiansError_arr(mu,sig2,N,a,b,mu__bar,sig2__bar,N__bar,lmbda_mu,lmbda_sig2,lmbda_N,flagOnlyE=1)
            t2=clock()
            dt_arr=t2-t1    # time for processing at once within arrays
            print("dt_arr=",dt_arr)
            print("max Delta E=",np.max(np.abs(np.divide(E_seq-E_arr,E_seq))))
            print("max Delta DE=",np.max(np.abs(np.divide(DE_seq-DE_arr,DE_seq))))
            print("max Delta DDE=",np.max(np.abs(np.divide(DDE_seq-DDE_arr,DDE_seq))))
            
    if select_tests["estim_Gauss_from_TruncGauss"]>0: 
        ##################################################################################################################################################################
        print("\nModule test of supylib module supy.signal.py:")
        print("------------------------------------------------")
        print("\nPart (ii.B): Test of estimateGaussParametersFromTruncatedGaussians(.):")
        print("-----------------------------------------------")
        ##################################################################################################################################################################

        # input data
        flag_critical_case=1

        mu_est  = 3.1
        sig_est = [1.0, 1.1, 1.2]
        N_est   = 200.5
        a        = [1.3 ,1.4 ,1.5 ,1.6 ]
        b        = [2.7 ,2.8 ,2.9 ,3.0 ]
        mu__bar  = [2.3 ,2.4 ,2.5 ,2.6 ]
        sig__bar = [0.7 ,0.8 ,0.9 ,1.0 ]
        N__bar   = [10.1,20.2,30.3,40.4]
        lmbda_mu,lmbda_sig2,lmbda_N=0.85,0.95,1.15

        if flag_critical_case==1:      # critical case from bat data set (leads to NaN)
            pass
        
        # prepare call
        mu_est   = np.array(len(sig_est)*[mu_est]) # mu_est must have same length as sig_est
        N_est    = np.array(len(sig_est)*[N_est])  # N_est must have same length as sig_est
        sig2_est = np.multiply(sig_est,sig_est)    # call requires sig2_est rather than sig_est
        a = np.array(a)
        b = np.array(b)
        mu__bar=np.array(mu__bar)
        sig2__bar = np.multiply(sig__bar,sig__bar) # call requires sig2__bar rather than sig__bar
        N__bar=np.array(N__bar)
        
        # do call
        estimateGaussParametersFromTruncatedGaussians(mu_est, sig2_est, N_est, a, b, mu__bar, sig2__bar, N__bar, lmbda_mu=1.0, lmbda_sig2=1.0, lmbda_N=1.0, tau_max=50)
        
        
        exit(0)
        
        #mu,sig,  a,b  =   3.1, 1.2,    2.5, 2.9
        mu,sig,  a,b, N  =   3.1, 1.2,    1.5, 2.9,  10.5
        mu__bar,sig__bar,N__bar = 2.7,0.9,4
        lmbda_mu,lmbda_sig2,lmbda_N=0.85,0.95,1.15


        if flagRand==1:
            mu,sig,N = 3*np.random.randn(n_iter), abs(2*np.random.randn(n_iter)), abs(20+2*np.random.randn(n_iter))
            a,b = mu-3*sig+np.random.rand(n_iter)*6*sig, mu-3*sig+np.random.rand(n_iter)*6*sig
            a,b = np.minimum(a,b),np.maximum(a,b)
            mu__bar,sig__bar,N__bar = a+np.random.rand(n_iter)*(b-a), 0.5*np.random.rand(n_iter)*(b-a), abs(20+2*np.random.randn(n_iter))
            lmbda_mu,lmbda_sig2,lmbda_N=1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand(),1.0+0.5*np.random.rand()   # keep fixed
            

        
        
        print("\nIV)Comparison of getDerivatives4TruncatedGaussiansError(.) vs. getDerivatives4TruncatedGaussiansError_arr(.):")
        print("-------------------------------------------------------------------------------------------------------------------")
        print("a) for array size 1 (same values as before)")
        print("---------------------------------------------")
        print("\ndd['alpha']=",dd['alpha']);print("dd_arr['alpha']=",dd_arr['alpha'])
    exit(0)

