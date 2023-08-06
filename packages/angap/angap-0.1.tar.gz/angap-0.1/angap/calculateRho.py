import scipy.integrate
import numpy as np

def calculateRho(lat,beta,i_mod180):
    a = max(lat-beta,-1*i_mod180)
    b = min(lat+beta,i_mod180)

    # numerically integrate
    rho = scipy.integrate.quad(lambda x: np.cos(x) * np.arccos((np.cos(beta/180.0*np.pi)-np.sin(x)*np.sin(lat/180.0*np.pi)) \
        /(np.cos(lat/180.0*np.pi)*np.cos(x))) \
        /(np.power(np.pi,2)*np.sqrt(np.power(np.sin(i_mod180/180.0*np.pi),2)-np.power(np.sin(x),2))), a/180.0*np.pi,b/180.0*np.pi,
        epsrel=1.00e-04)

    #rho = scipy.integrate.quad(lambda x: np.cos(x),a,b)

    return rho

def calculateRhoVector(lat_vec,beta,i_mod180):
    rho_vec = np.zeros(np.shape(lat_vec))
    for i in range(len(rho_vec)):
       rho_vec[i] = calculateRho(lat_vec[i],beta,i_mod180)