from scipy import stats
from scipy.stats import linregress
from scipy.signal import argrelextrema
import numpy as np
import pandas as pd
import math
import statsmodels
from pandas import Series
import random

def divergence(indicator_vals,highs,lows,order):
    
    i_vals,h_vals,l_vals = list(indicator_vals),list(highs),list(lows)
    i_vals_np,h_vals_np,l_vals_np = np.array(indicator_vals),np.array(highs),np.array(lows)
    
    # Record peaks/troughs for price and indicator 
    
    i_trough_indices = argrelextrema(i_vals_np, np.less, order = order)
    i_peak_indices = argrelextrema(i_vals_np, np.greater, order = order)    
    h_peak_indices = argrelextrema(h_vals_np, np.greater, order = order)       
    l_trough_indices = argrelextrema(l_vals_np, np.less, order = order)   
    
    i_trough_vals = list(i_vals_np[i_trough_indices])
    i_peak_vals = list(i_vals_np[i_peak_indices])   
    h_peak_vals = list(h_vals_np[h_peak_indices])
    l_trough_vals = list(l_vals_np[l_trough_indices])
    
    # Calculate HL prices' slopes
    
    h_peak_indx = []
    for item in h_peak_vals:
        h_peak_indx.append(h_vals.index(item))
    h_peak_slope = stats.linregress(h_peak_indx[-2:],h_peak_vals[-2:]).slope

    l_trough_indx = []
    for item in l_trough_vals:
        l_trough_indx.append(l_vals.index(item))
    l_trough_slope = stats.linregress(l_trough_indx[-2:],l_trough_vals[-2:]).slope
    
    # Confirm price action
    
    price_action = None
    
    if h_peak_slope >= 0.01:
        price_action = "higher_highs"
    elif l_trough_slope <= -0.01:
        price_action = "lower_lows"
    
    # Record price action start/end dates         
    
    p_indx_start, price_action_start_date, p_indx_end, price_action_end_date = None,None,None,None
    
    if price_action == "higher_highs":     
        p_indx_start = h_vals.index(h_peak_vals[-2])
        try:
            price_action_start_date = highs.index[p_indx_start]
        except:
            price_action_start_date = None
        
    elif price_action == "lower_lows":       
        p_indx_start = l_vals.index(l_trough_vals[-2])
        try:
            price_action_start_date = lows.index[p_indx_start]
        except:
            price_action_start_date = None
        
    # Identify indicator's corresponding start date (index)

    i_peak_indx = []
    for item in i_peak_vals:
        i_peak_indx.append(i_vals.index(item))
    
    i_trough_indx = []
    for item in i_trough_vals:
        i_trough_indx.append(i_vals.index(item))    

    i_peak_find_backw,i_peak_find_forw,i_trough_find_backw,i_trough_find_forw = 0,0,0,0
    
    try:
        if price_action == "higher_highs":
            i_peak_find_backw = [i for i in i_peak_indx if i <= p_indx_start][-1]
            i_peak_find_forw = [i for i in i_peak_indx if i > p_indx_start][0]     

        elif price_action == "lower_lows":
            i_trough_find_backw = [i for i in i_trough_indx if i <= p_indx_start][-1]
            i_trough_find_forw = [i for i in i_trough_indx if i > p_indx_start][0]
            
        i_indx_start__ = np.asarray([i_peak_find_backw,i_peak_find_forw,i_trough_find_backw,i_trough_find_forw])
        i_indx_start_ = (np.abs(i_indx_start__-p_indx_start)).argmin()
        i_indx_start = i_indx_start__[i_indx_start_]
        
    except:
        i_indx_start__,i_indx_start_,i_indx_start = None,None,p_indx_start
    
    # Calculate indicator slope

    x1 = i_indx_start
    
    try:
        if price_action == "higher_highs":
            x2 = i_vals.index(i_peak_vals[-1])  

        elif price_action == "lower_lows":
            x2 = i_vals.index(i_trough_vals[-1])
        
    except:
        
        p_indx_end, price_action_end_date = None,None

        if price_action == "higher_highs":     
            p_indx_end = h_vals.index(h_peak_vals[-1])
            price_action_end_date = highs.index[p_indx_end]

        elif price_action == "lower_lows":       
            p_indx_end = l_vals.index(l_trough_vals[-1])
            price_action_end_date = lows.index[p_indx_end]
        
        x2 = p_indx_end
    
    try:
        y1,y2 = i_vals[x1], i_vals[x2]
        x,y = [x1,x2], [y1,y2]
        i_slope = stats.linregress(x,y).slope
        
    except:
        i_slope = 0
    
    # Confirm divergence
    
    divergence = None
    
    if price_action == "higher_highs" and i_slope < 0:
        divergence = "bearish_divergence" 
        
    elif price_action == "lower_lows" and i_slope > 0:
        divergence = "bullish_divergence"   
    
    # Identify indicator divergence top/bottom
    
    i_divergence_max,i_divergence_min = 0,0
    
    if price_action_start_date != None:        
        i_divergence_vals = i_vals[i_indx_start:x2]
        try:
            i_divergence_max = max(i_divergence_vals)
        except:
            i_divergence_max = 0
        try:
            i_divergence_min = min(i_divergence_vals)
        except:
            i_divergence_min = 0
    
    return price_action,divergence,price_action_start_date,i_divergence_max,i_divergence_min