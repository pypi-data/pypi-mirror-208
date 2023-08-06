import math
import numpy as np
from calculateRho import *

def findMaxGapTime(latitude_range,inc_deg,alt,elev_deg,constants):
    lam_prime = latitude_range
    E_CON = constants
    h = alt
    i = inc_deg
    T_s = 2.0*math.pi*((E_CON.r_e+h)**1.5)/(E_CON.GM_e**0.5) #s
    V_s = 2.0*math.pi*(E_CON.r_e+h)/T_s #km/s
    A_s = 1000.0*(V_s**2.0)/(E_CON.r_e+h) #m/s^2
    Orbits_per_sol = E_CON.T_sr_e/T_s
    L_s = T_s/E_CON.T_sr_e*360.0 #deg
    epsil = elev_deg
    phi = i-90.0
    #phi_m = -1.0*(i-90.0)
    i_mod180 = 180-i if i>90 else i
    tau = 30 #s

    r = E_CON.r_e*np.sqrt( (np.power(np.cos(lam_prime/180.0*math.pi),2.0) + ((1.0-(E_CON.ecc_e**2.0))**2.0)*(np.power(np.sin(lam_prime/180.0*math.pi),2.0)))
                           /(1.0-(E_CON.ecc_e**2.0)*np.power(np.sin(lam_prime/180.0*math.pi),2.0)) )

    #beta = 90.0-epsil-np.arcsin( np.multiply(r,np.cos(epsil/180*math.pi))/(E_CON.r_e+h) )/math.pi*180.0
    beta_long = 90.0-epsil-np.arcsin( np.clip(np.multiply(r,np.cos(epsil/180*math.pi))/(E_CON.r_e+h),-1,1) )/math.pi*180.0
    #beta=beta_long
    #beta = np.arcsin(np.sqrt(np.power(np.sin(beta_long/180.0*math.pi),2)-4*np.power(np.sin(2*math.pi*tau/T_s),2)))*180.0/math.pi
    beta = np.arcsin(np.clip(np.sin(beta_long/180.0*math.pi) * np.cos( np.arcsin(np.clip(np.sin(math.pi*tau/T_s)/np.sin(beta_long/180.0*math.pi),-1,1)) + 2*math.pi*tau/E_CON.T_sr_e*np.sin(i/180*math.pi)),-1,1))*180.0/math.pi
    beta = np.sqrt(np.power(beta,2) - np.power(tau*360.0/2*(1/T_s + np.cos(i/180.0*math.pi)/E_CON.T_sr_e),2))

    #print(beta_long-beta)

    lam1_prime_min = np.zeros(lam_prime.shape)
    for ii in range(len(lam1_prime_min)):
        ## ORIGINAL 1 ##
        lam1_prime_min[ii] = i+beta[ii]-180.0 if i+beta[ii]-180.0>0.0 else 0.0
        ## CHANGE 1 ##
        if(0.0<i+beta[ii]-180.0<=90.0):
            lam1_prime_min[ii] = i+beta[ii]-180.0
        else:
            lam1_prime_min[ii] = 0.0

    lam1_prime_max = np.zeros(lam_prime.shape)
    for ii in range(len(lam1_prime_max)):
        ## ORIGINAL 2 ##
        lam1_prime_max[ii] = 0.0 if i-beta[ii]<0.0 else (i-beta[ii] if i-beta[ii]<90.0 else 180-(i-beta[ii]))
        ## CHANGE 2 ##
        if(0.0 < i-beta[ii] <= 90.0):
            lam1_prime_max[ii] = i-beta[ii]
        elif(90.0 < i-beta[ii] < 180.0):
            lam1_prime_max[ii] = 180.0-(i-beta[ii])
        else:
            lam1_prime_max[ii] = 0.0

    lam2_prime_min = np.zeros(lam_prime.shape)
    for ii in range(len(lam2_prime_min)):
        ## ORIGINAL 3 ##
        lam2_prime_min[ii] = beta[ii]-i if beta[ii]-i>0.0 else 0.0
        ## CHANGE 3 ##
        if(0.0 < beta[ii]-i < 90.0):
            lam2_prime_min[ii] = beta[ii] - i
        else:
            lam2_prime_min[ii] = 0.0

    lam2_prime_max = np.zeros(lam_prime.shape)
    for ii in range(len(lam2_prime_min)):
        ## ORIGINAL 4 ##
        lam2_prime_max[ii] = 0.0 if (i+beta[ii]<0.0 or i+beta[ii]>180.0) else (i+beta[ii] if i+beta[ii]<90.0 else 180-(i+beta[ii]))
        ## CHANGE 4 ##
        if(0.0 < i+beta[ii] <= 90.0):
            lam2_prime_max[ii] = i+beta[ii]
        elif(90.0 < i+beta[ii] < 180.0):
            lam2_prime_max[ii] = 180.0 - (i+beta[ii])
        else:
            lam2_prime_max[ii] = 0.0


    ## ORIGINAL 5 ##
    #lam1 = np.arcsin( (np.sin(lam_prime/180.0*math.pi)-np.sin(beta/180.0*math.pi)*np.sin(phi_p/180.0*math.pi)) / np.cos(phi_p/180.0*math.pi))*180.0/math.pi
    ## CHANGE 5 ##
    lam1 = np.arcsin( np.clip((np.sin(lam_prime/180.0*math.pi)-np.sin(beta/180.0*math.pi)*np.sin(phi/180.0*math.pi)) / np.cos(phi/180.0*math.pi),-1,1))*180.0/math.pi

    ## ORIGINAL 6 ##
    L1 = np.arcsin( np.clip(np.sqrt(np.divide(np.power(np.cos(beta/180.0*math.pi),2)-np.power(np.sin(lam1/180.0*math.pi),2),np.power(np.cos(lam1/180.0*math.pi),2))),-1,1))*180.0/math.pi
    ## CHANGE 6 ##
    L1 = np.arccos(np.clip(np.divide(np.sin(beta/180.0*math.pi),np.cos(lam1/180.0*math.pi)),-1,1))*180.0/math.pi

    ## ORIGINAL 7 ##
    #L1_prime = np.arctan2(np.multiply(np.sin(L1/180.0*math.pi),np.cos(lam1/180.0*math.pi)),
    #           np.multiply(np.cos(L1/180.0*math.pi),np.cos(lam1/180.0*math.pi))*np.cos(phi_p/180.0*math.pi) - np.sin(lam1/180.0*math.pi)*np.sin(phi_p/180.0*math.pi))*180.0/math.pi
    ## CHANGE 7 ##
    L1_prime = np.arctan2(np.multiply(np.sin(L1/180.0*math.pi),np.cos(lam1/180.0*math.pi)),
               np.multiply(np.cos(L1/180.0*math.pi),np.cos(lam1/180.0*math.pi))*np.cos(phi/180.0*math.pi) - np.sin(lam1/180.0*math.pi)*np.sin(phi/180.0*math.pi))*180.0/math.pi

    A12_1 = np.zeros(lam_prime.shape)
    for ii in range(len(A12_1)):
        if(i<90):
            #A12_1[ii] = (360.0-2.0*(90.0-np.divide(lam1[ii],np.cos(beta[ii]/180.0*math.pi))))
            ## ORIGINAL 8 ##
            A12_1[ii] = (360.0 - 2.0 * (90.0 - np.divide(lam1[ii], np.cos(beta_long[ii] / 180.0 * math.pi))))
            ## CHANGE 8 ##
            A12_1[ii] = (360.0 - 2.0 * (90.0 - np.arcsin(np.clip(np.divide(np.sin(lam1[ii]/180.0*math.pi),np.cos(beta_long[ii]/180.0*math.pi)),-1,1))*180.0/math.pi))
            #A12_1[ii] = (360-2.0*(90.0-lam1[ii]))
        else:
            #A12_1[ii] = (2.0*(90.0-np.divide(lam1[ii],np.cos(beta[ii]/180.0*math.pi))))
            ## ORIGINAL 9 ##
            A12_1[ii] = (2.0*(90.0-np.divide(lam1[ii],np.cos(beta_long[ii]/180.0*math.pi))))
            ## CHANGE 9 ##
            A12_1[ii] = (2.0*(90.0-np.arcsin(np.clip(np.divide(np.sin(lam1[ii]/180.0*math.pi), np.cos(beta_long[ii]/180.0*math.pi)),-1,1))*180.0/math.pi))
            #A12_1[ii] = (2.0*(90.0-lam1[ii]))

    ## ORIGINAL 10 ##
    #lam2 = np.arcsin( (np.sin(lam_prime/180.0*math.pi)-np.sin(beta/180.0*math.pi)*np.sin(phi_m/180.0*math.pi)) / np.cos(phi_m/180.0*math.pi))*180.0/math.pi
    ## CHANGE 10 ##
    lam2 = np.arcsin( np.clip((np.sin(lam_prime/180.0*math.pi)+np.sin(beta/180.0*math.pi)*np.sin(phi/180.0*math.pi)) / np.cos(phi/180.0*math.pi),-1,1))*180.0/math.pi

    ## ORIGINAL 11 ##
    L2 = np.arcsin( np.clip(np.sqrt(np.divide(np.power(np.cos(beta/180.0*math.pi),2)-np.power(np.sin(lam2/180.0*math.pi),2),np.power(np.cos(lam2/180.0*math.pi),2))),-1,1))*180.0/math.pi
    ## CHANGE 11 ##
    L2 = np.arccos(np.clip(np.divide(np.sin(beta/180.0*math.pi),np.cos(lam2/180.0*math.pi)),-1,1))*180.0/math.pi

    ## ORIGINAL 12 ##
    #L2_prime = np.arctan2(np.multiply(np.sin(L2/180.0*math.pi),np.cos(lam2/180.0*math.pi)),
    #           np.multiply(np.cos(L2/180.0*math.pi),np.cos(lam2/180.0*math.pi))*np.cos(phi_m/180.0*math.pi) - np.sin(lam2/180.0*math.pi)*np.sin(phi_m/180.0*math.pi))*180.0/math.pi
    ## CHANGE 12 ##
    L2_prime = np.arctan2(np.multiply(np.sin(L2/180.0*math.pi),np.cos(lam2/180.0*math.pi)),
                          np.multiply(np.cos(L2/180.0*math.pi),np.cos(lam2/180.0*math.pi))*np.cos(phi/180.0*math.pi)+np.sin(lam2/180.0*math.pi)*np.sin(phi/180.0*math.pi))*180.0/math.pi

    A12_2 = np.zeros(lam_prime.shape)
    for ii in range(len(A12_2)):
        if(i<90):
            #A12_2[ii] = (360.0-2.0*(90.0-np.divide(lam2[ii],np.cos(beta[ii]/180.0*math.pi))))
            ## ORIGINAL 13 ##
            A12_2[ii] = (360.0-2.0*(90.0-np.divide(lam2[ii],np.cos(beta_long[ii]/180.0*math.pi))))
            ## CHANGE 13 ##
            A12_2[ii] = (360.0-2.0*(90.0-np.arcsin(np.clip(np.divide(np.sin(lam2[ii]/180.0*math.pi), np.cos(beta_long[ii]/180.0*math.pi)),-1,1))*180.0/math.pi))
            #A12_2[ii] = (360.0 - 2.0 * (90.0 - lam2[ii]))
        else:
            #A12_2[ii] = (2.0*(90.0-np.divide(lam2[ii],np.cos(beta[ii]/180.0*math.pi))))
            ## ORIGINAL 14 ##
            A12_2[ii] = (2.0*(90.0-np.divide(lam2[ii],np.cos(beta_long[ii]/180.0*math.pi))))
            ## CHANGE 14 ##
            A12_2[ii] = (2.0*(90.0-np.arcsin(np.clip(np.divide(np.sin(lam2[ii]/180.0*math.pi), np.cos(beta_long[ii]/180.0*math.pi)),-1,1))*180.0/math.pi))
            #A12_2[ii] = (2.0 * (90.0 - lam2[ii]))

    ## CHANGE 15 ##
    d_out_1 = np.zeros(lam_prime.shape)
    for ii in range(len(d_out_1)):
        d_out_1[ii] = np.arccos(np.clip(np.divide(np.cos(beta_long[ii]/180.0*math.pi),np.cos((L_s-beta_long[ii])/180.0*math.pi)),-1,1))*180.0/math.pi

    ## CHANGE 16 ##
    d_in_1 = np.zeros(lam_prime.shape)
    for ii in range(len(d_in_1)):
        a = np.ceil(2.0*L1_prime[ii]/L_s-A12_1[ii]/360.0)+A12_1[ii]/360.0
        d_in_1[ii] = np.arccos(np.clip(np.cos(beta_long[ii]/180.0*math.pi)/np.cos((a-beta_long[ii])/180.0*math.pi),-1,1))*180.0/math.pi

    T_gap1 = np.zeros(lam_prime.shape)
    for ii in range(len(T_gap1)):
        if(lam_prime[ii]<lam1_prime_min[ii] or ((lam_prime[ii]<i_mod180+beta[ii] and lam_prime[ii]>lam1_prime_max[ii]) and lam1_prime_max[ii]>lam1_prime_min[ii])):
            #T_gap1[ii] = T_s*(1.0-2.0*beta[ii]/360.0)*(1.0+T_s*np.cos(i/180.0*math.pi)/E_CON.T_sr_e)
            #T_gap1[ii] = T_s * (1.0 - 2.0 * beta_long[ii] / 360.0) * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e)
            if(lam_prime[ii]<lam1_prime_min[ii]):
                #T_gap1[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*(((-1.0/lam1_prime_min[ii])*lam_prime[ii]+1.0)*1.0)/360.0)
                ## ORIGINAL 17 ##
                T_gap1[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*((np.sqrt(1.0-np.power((lam_prime[ii])/lam1_prime_min[ii],2)))*1.0)/360.0)
                ## CHANGE 17 ##
                T_gap1[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*np.arccos(np.clip(np.cos(beta_long[ii]/180.0*math.pi)/np.cos(i_mod180/180.0*math.pi+lam_prime[ii]/180.0*math.pi),-1,1))*180.0/math.pi/360.0)
            else:
                ## ORIGINAL 18 ##
                T_gap1[ii] = T_s * (1 - 2*beta_long[ii]*((np.sqrt(1.0-np.power((lam_prime[ii]-lam1_prime_max[ii]-(180-i_mod180-lam1_prime_max[ii]))/(180.0-i_mod180-lam1_prime_max[ii]),2)))*1.0)/360.0)
                ## CHANGE 18 ##
                T_gap1[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*(np.arccos(np.clip(np.divide(np.cos(beta_long[ii]/180.0*math.pi),np.cos(180.0/180.0*math.pi-i_mod180/180.0*math.pi-lam_prime[ii]/180.0*math.pi)),-1,1)))*180.0/math.pi/360.0)
                #T_gap1[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*(((1.0/(90.0-lam1_prime_max[ii]))*lam_prime[ii]-lam1_prime_max[ii]/(90.0-lam1_prime_max[ii]))*1.0)/360.0)
                #T_gap1[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*(((1.0/beta_long[ii])*lam_prime[ii]-(min(90.0,i_mod180+beta_long[ii])-beta_long[ii])/beta_long[ii])*1.0)/360.0)
        elif(lam_prime[ii]<=lam1_prime_max[ii] and lam_prime[ii]>=lam1_prime_min[ii]):
            #T_gap1[ii] = T_s * (np.ceil(1.0+2.0*L1_prime[ii]/L_s-A12_1[ii]/360.0)+A12_1[ii]/360.0-2.0*beta[ii]/360)
            ## ORIGINAL 19 ##
            T_gap1[ii] = T_s * (np.ceil(1.0+2.0*L1_prime[ii]/L_s-A12_1[ii]/360.0)+A12_1[ii]/360.0-2.0*beta_long[ii]/360)
            ## CHANGE 19 ##
            #T_gap1[ii] = T_s * (np.ceil(1.0+2.0*L1_prime[ii]/L_s-A12_1[ii]/360.0)+A12_1[ii]/360.0-(d_in_1[ii]+d_out_1[ii])/360.0)
            T_gap1[ii] = T_s * (np.ceil(1.0+2.0*L1_prime[ii]/L_s-A12_1[ii]/360.0)+A12_1[ii]/360.0-(d_in_1[ii]+d_out_1[ii])/360.0)
        else:
            T_gap1[ii] = float('inf')

    ## CHANGE 20 ##
    d_out_2 = np.zeros(lam_prime.shape)
    for ii in range(len(d_out_2)):
        d_out_2[ii] = np.arccos(np.clip(np.divide(np.cos(beta_long[ii]/180.0*math.pi),np.cos((L_s-beta_long[ii])/180.0*math.pi)),-1,1))*180.0/math.pi

    ## CHANGE 21 ##
    d_in_2 = np.zeros(lam_prime.shape)
    for ii in range(len(d_in_2)):
        a = np.ceil(2.0 * L2_prime[ii] / L_s - A12_2[ii] / 360.0) + A12_2[ii] / 360.0
        d_in_2[ii] = np.arccos(np.clip(np.cos(beta_long[ii]/180.0*math.pi) / np.cos((a - beta_long[ii])/180.0*math.pi),-1,1)) * 180.0 / math.pi

    T_gap2 = np.zeros(lam_prime.shape)
    for ii in range(len(T_gap1)):
        if(lam_prime[ii]<lam2_prime_min[ii] or ((lam_prime[ii]<i_mod180+beta[ii] and lam_prime[ii]>lam2_prime_max[ii]) and lam2_prime_max[ii]>lam2_prime_min[ii])):
            #T_gap2[ii] = T_s*(1.0-2.0*beta[ii]/360.0)*(1.0+T_s*np.cos(i/180.0*math.pi)/E_CON.T_sr_e)
            #T_gap2[ii] = T_s * (1.0 - 2.0 * beta_long[ii] / 360.0) * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e)
            if(lam_prime[ii]<lam2_prime_min[ii]):
                #T_gap2[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*(((-1.0/lam2_prime_min[ii])*lam_prime[ii]+1.0)*1.0)/360.0)
                ## ORIGINAL 22 ##
                T_gap2[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*((np.sqrt(1.0-np.power((lam_prime[ii])/lam2_prime_min[ii],2)))*1.0)/360.0)
                ## CHANGE 22 ##
                T_gap2[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*np.arccos(np.clip(np.cos(beta_long[ii]/180.0*math.pi)/np.cos(i_mod180/180.0*math.pi+lam_prime[ii]/180.0*math.pi),-1,1))*180.0/math.pi/360.0)

            else:
                #T_gap2[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*(((1.0/beta_long[ii])*lam_prime[ii]-(min(90.0,i_mod180+beta_long[ii])-beta_long[ii])/beta_long[ii])*1.0)/360.0)
                #T_gap2[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*beta_long[ii]*(((1.0/(90.0-lam2_prime_max[ii]))*lam_prime[ii]-lam2_prime_max[ii]/(90.0-lam2_prime_max[ii]))*1.0)/360.0)
                ## ORIGINAL 23 ##
                T_gap2[ii] = T_s * (1 - 2*beta_long[ii]*((np.sqrt(1.0-np.power((lam_prime[ii]-lam2_prime_max[ii]-(180-i_mod180-lam2_prime_max[ii]))/(180.0-i_mod180-lam2_prime_max[ii]),2)))*1.0)/360.0)
                ## CHANGE 23 ##
                T_gap2[ii] = T_s * (1.0 + T_s * np.cos(i / 180.0 * math.pi) / E_CON.T_sr_e) * (1 - 2*(np.arccos(np.clip(np.divide(np.cos(beta_long[ii]/180.0*math.pi),np.cos(180.0/180.0*math.pi-i_mod180/180.0*math.pi-lam_prime[ii]/180.0*math.pi)),-1,1)))*180.0/math.pi/360.0)
        elif(lam_prime[ii]<=lam2_prime_max[ii] and lam_prime[ii]>=lam2_prime_min[ii]):
            #T_gap2[ii] = T_s * (np.ceil(1.0+2.0*L2_prime[ii]/L_s-A12_2[ii]/360.0)+A12_2[ii]/360.0-2.0*beta[ii]/360)
            ## ORIGINAL 24 ##
            T_gap2[ii] = T_s * (np.ceil(1.0+2.0*L2_prime[ii]/L_s-A12_2[ii]/360.0)+A12_2[ii]/360.0-2.0*beta_long[ii]/360)
            ## CHANGE 24 ##
            #T_gap2[ii] = T_s * (np.ceil(1.0+2.0*L2_prime[ii]/L_s-A12_2[ii]/360.0)+A12_2[ii]/360.0-(d_in_2[ii]+d_out_2[ii])/360)
            T_gap2[ii] = T_s * (np.ceil(1.0 + 2.0 * L2_prime[ii] / L_s - A12_2[ii] / 360.0) + A12_2[ii] / 360.0
                    -(d_in_2[ii] + d_out_2[ii]) / 360.0)
        else:
            T_gap2[ii] = float('inf')

    T_maxgap = np.zeros(lam_prime.shape)
    swath_width=np.zeros(lam_prime.shape)
    for ii in range(len(T_maxgap)):
        if  ((T_gap1[ii]!=float('inf') and not math.isnan(T_gap1[ii])) and (T_gap2[ii]!=float('inf') and not math.isnan(T_gap2[ii]))):
            T_maxgap[ii] = np.maximum(T_gap1[ii],T_gap2[ii])
        elif((T_gap1[ii]==float('inf') or math.isnan(T_gap1[ii])) and (T_gap2[ii]!=float('inf') and not math.isnan(T_gap2[ii]))):
            T_maxgap[ii] = T_gap2[ii]
        elif((T_gap1[ii]!=float('inf') and not math.isnan(T_gap1[ii])) and (T_gap2[ii]==float('inf') or math.isnan(T_gap2[ii]))):
            T_maxgap[ii] = T_gap1[ii]
        else:
            T_maxgap[ii] = float('inf')
            swath_width[ii] = 0.0

    swath_width=np.zeros(lam_prime.shape)
    overlap_swath = np.zeros(lam_prime.shape)
    for ii in range(len(swath_width)):
        if  (not(math.isnan(L1_prime[ii])) and not(math.isnan(L2_prime[ii])) ):
            swath_width[ii] = (360.0-2.0*L1_prime[ii]-2.0*L2_prime[ii])/2.0
        elif(math.isnan(L1_prime[ii]) and not(math.isnan(L2_prime[ii])) ):
            swath_width[ii] = (360.0-2.0*L2_prime[ii])
        elif(not(math.isnan(L1_prime[ii])) and math.isnan(L2_prime[ii])):
            swath_width[ii] = (360.0-2.0*L1_prime[ii])
        elif(math.isnan(L1_prime[ii]) and math.isnan(L2_prime[ii]) and lam_prime[ii] < i_mod180+beta[ii]):
            swath_width[ii] = 360.0
        else:
            swath_width[ii] = float('inf')

        overlap_swath[ii] = swath_width[ii]>L_s

    total_swath=np.zeros(lam_prime.shape)
    for ii in range(len(swath_width)):
        if  (not(math.isnan(L1_prime[ii])) and not(math.isnan(L2_prime[ii])) ):
            total_swath[ii] = 360.0-2.0*L1_prime[ii]-2.0*L2_prime[ii]
        elif(math.isnan(L1_prime[ii]) and not(math.isnan(L2_prime[ii])) ):
            total_swath[ii] = (360.0-2.0*L2_prime[ii])
        elif(not(math.isnan(L1_prime[ii])) and math.isnan(L2_prime[ii])):
            total_swath[ii] = (360.0-2.0*L1_prime[ii])
        elif(math.isnan(L1_prime[ii]) and math.isnan(L2_prime[ii]) and lam_prime[ii] < i_mod180+beta[ii]):
            total_swath[ii] = 360.0
        else:
            total_swath[ii] = float('inf')

    ppd=np.zeros(lam_prime.shape)
    for ii in range(len(ppd)):
        f_i_l=0.0
        if(i <= 90):
            f_i_l = np.minimum(np.abs(np.cos(i/180.0*math.pi)),np.abs(np.cos(lam_prime[ii]/180.0*math.pi)))
            #f_i_l = np.cos(i/180.0*math.pi)
        else:
            f_i_l = -1*np.minimum(np.abs(np.cos(i/180.0*math.pi)),np.abs(np.cos(lam_prime[ii]/180.0*math.pi)))
            #f_i_l = np.cos(i/180.0*math.pi)

        ppd[ii] = total_swath[ii]/360.0 * (E_CON.T_s_e/T_s - f_i_l)

    mpt=np.zeros(lam_prime.shape)
    for ii in range(len(mpt)):
        result = calculateRho(lam_prime[ii],beta[ii],i_mod180)
        #result=[0,0]
        mpt[ii] = (result[0] * E_CON.T_s_e/ppd[ii])

    return T_maxgap,overlap_swath,ppd,mpt

class ConstantsStruct:
    def __init__(self):
        # earth definitions
        self.r_e = 6378.145 #km
        self.circ_e = 2.0*math.pi*(self.r_e) #km
        self.area_e = 4.0*math.pi*(self.r_e**2.0) # km^2
        self.T_sr_e = 86163.45 #s
        self.T_s_e = 86400.00 #s
        self.c = 3.00*(10.0**5.0) # km/s
        self.G = 6.67*(10.0**-20.0) # km^3/(kg s)^2
        self.M_e = 5.98*(10.0**24.0) # kg
        self.GM_e = self.G*self.M_e
        self.ecc_e = 0#8.18*(10.0**-2.0)
