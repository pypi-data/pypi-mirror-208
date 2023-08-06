#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:40:24 2019

FADO plotting routine in Python

@author: Jean Gomes
"""

import matplotlib.pyplot as plt
from pylab import *
import seaborn as sns
from cycler import cycler

class PlotFADO(object):
    """ @author: Jean Gomes 
 @date  : Mon Apr 29 14:40:24 2019
 Resume : FADO plotting class in Python """
    
    g_listvalEL = [0980.00,
                   1030.00,
                   1216.00,
                   1240.00,
                   1397.00,
                   1549.00,
                   1909.00,
                   2799.00,
                   3425.50,
                   #3726.03,
                   #3728.82,
                   3727.42,
                   3868.71,
                   3888.65,
                   3967.41,
                   3970.07,
                   4101.76,
                   4340.47,
                   4363.21,
                   4861.33,
                   4958.92,
                   5006.84,
                   5754.64,
                   5875.67,
                   #5889.95,
                   #5895.92,
                   6300.30,
                   6548.03,
                   6562.80,
                   6583.41,
                   6678.15,
                   6716.47,
                   6730.85,
                   7065.20,
                   7135.80,
                   7319.50,
                   7330.20,
                   7751.10,
                   8617.00,
                   8375.11,
                   8393.04,
                   8413.96,
                   8438.60,
                   8467.90,
                   8503.13,
                   8546.03,
                   8599.05,
                   8665.68,
                   8751.14,
                   8863.46,
                   9015.60,
                   9229.72]
        
    g_list_pref = [1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   0,
                   0,
                   0,
                   0,
                   1,
                   1,
                   0,
                   1,
                   0,
                   1,
                   0,
                   0,
                   1,
                   0,
                   1,
                   0,
                   0,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   1,
                   0,
                   1,
                   0,
                   1,
                   0,
                   0]
    
    g_listnamEL = [r'$\mathrm{CII+NIII}$',
                   r'$\mathrm{OIV+Ly}\beta$',
                   r'$\mathrm{Ly}\alpha$',
                   r'$\mathrm{NV}$',
                   r'$\mathrm{SiIV+OIV]}$',
                   r'$\mathrm{CIV}$',
                   r'$\mathrm{CIII]}$',
                   r'$\mathrm{MgII}$',
                   r'$\mathrm{[NeV]}$',
                   r'$\mathrm{[OII]}$ 3726,3729',
                   r'$\mathrm{[NeIII]}$',
                   r'$\mathrm{HeI}$',
                   r'$\mathrm{[NeIII]}$',
                   r'$\mathrm{[NeIII],CaII,H_{\epsilon}}$',
                   r'$\mathrm{H}{\delta}$',
                   r'$\mathrm{H}{\gamma}$',
                   r'$\mathrm{[OIII]}$ 4363',
                   r'$\mathrm{H}{\beta}$',
                   r'$\mathrm{[OIII]}$ 4959',
                   r'$\mathrm{[OIII]}$ 5007',
                   r'$\mathrm{[NII]}$ 5755',
                   r'$\mathrm{HeI}$',
                   #r'$\mathrm{NaI}$',
                   #r'$\mathrm{HeI,NaI}$',
                   r'$\mathrm{[OI]}$ 6300',
                   r'$\mathrm{[NII]}$ 6548',
                   r'$\mathrm{H}_{\alpha}$',
                   #r'$\mathrm{[NII]}$ 6583',
                   r'$\mathrm{[NII],H{\alpha}}$',
                   r'$\mathrm{HeI}$',
                   r'$\mathrm{[SII]}$ 6717',
                   r'$\mathrm{[SII]}$ 6731',
                   r'$\mathrm{HeI}$',
                   r'$\mathrm{[ArIII]}$',
                   r'$\mathrm{[OII]}$',
                   r'$\mathrm{[OII]}$',
                   r'$\mathrm{[ArIII]}$',
                   r'$\mathrm{[FeII]}$',
                   r'$\mathrm{HP21}$',
                   r'$\mathrm{HP20}$',
                   r'$\mathrm{HP19}$',
                   r'$\mathrm{HP18}$',
                   r'$\mathrm{HP17}$',
                   r'$\mathrm{HP16}$',
                   r'$\mathrm{HP15}$',
                   r'$\mathrm{HP14}$',
                   r'$\mathrm{HP13}$',
                   r'$\mathrm{HP12}$',
                   r'$\mathrm{HP11}$',
                   r'$\mathrm{HP10}$',
                   r'$\mathrm{HP09}$']

        # Initialization of class PlotFADO ################################################################################################
    def __init__( self, object, xmin=3000.0 , xmax=9300.0, ymin=0.0, ymax=1.5, ymin_residual=-999.0, ymax_residual=-999.0 ):
        self.spectrum = object.spectrum
        self.fluxunit = object.fluxunit
        self.galsnorm = object.galsnorm
        self.lambda_0 = object.lambda_0
        
        self.num_base = object.num_base
        
        self.light_fractions     = object.light_fractions
        self.mass_fractions      = object.mass_fractions
        self.met_stellar_pop     = object.met_stellar_pop
        self.log_age_stellar_pop = object.log_age_stellar_pop
        self.age_stellar_pop     = object.age_stellar_pop
        
        # Extinction parameters
        self.reddening_law       = object.reddening_law
        self.AV_extinction       = object.AV_extinction                                  
        self.AV_extinction_error = object.AV_extinction_error
        
        #print( self.fluxunit, self.galsnorm, self.lambda_0 )
        
        # Parameters for the main fitting window
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        
        # Parameters for the residual window
        self.ymin_residual = ymin_residual
        self.ymax_residual = ymax_residual
        
        self.listvalEL = self.g_listvalEL
        self.listnamEL = self.g_listnamEL
        self.list_pref = self.g_list_pref
        
        self.PlotFit( xmin=self.xmin, xmax=self.xmax, ymin=self.ymin, ymax=self.ymax, ymin_residual=self.ymin_residual, ymax_residual=self.ymax_residual )
        # Initialization of class PlotFADO ################################################################################################


        # Define function for string formatting of scientific notation ####################################################################
    def sci_notation( self, num, decimal_digits=1, precision=None, exponent=None ):
        """ ============================================================
 @author: Jean Gomes 
 @date  : Mon Apr 29 14:40:24 2019
 License: pyFADO module  is freely available under the General Public License (GPL).
 Resume : Returns a string representation of the scientific notation of the given number formatted for use with LaTeX or Mathtext, with specified number of significant decimal digits and precision (number of decimal digits to show). The exponent to be used can also be specified explicitly. 
 ============================================================ """
        coeff = 0
        
        if not exponent:
            exponent = int(floor(np.log10(np.abs(num))))
            
        #print( type(exponent), type(num) )
        coeff = round( num / float(10**exponent), decimal_digits )
            
        if not precision:
            precision = decimal_digits

        return "{0:.{2}f}\cdot10^{{{1:d}}}".format(coeff, exponent, precision)
        # Define function for string formatting of scientific notation ####################################################################

        
        # Plot Fit FADO ###################################################################################################################
        #Figure = plt.figure(figsize=(1.8 * 22, 2.4 * 28),dpi=80,facecolor='w',edgecolor='w')
    def PlotFit( self, xmin=3000.0, xmax=9300.0, ymin=0.0, ymax=1.5, ymin_residual=-999.0, ymax_residual=-999.0 ):
        
        l = self.spectrum[:,0]
        f = self.spectrum[:,1]
        e = self.spectrum[:,2]
        m = self.spectrum[:,3]
        b = self.spectrum[:,4]
        s = self.spectrum[:,5]
        n = self.spectrum[:,6]
        r = self.spectrum[:,7]
        
        ## Axis limits
        #xmin=np.min(l) ; xmax=np.max(l)
        #ymin=np.min(b) ; ymax=np.max(b)
        
        xwidth  = xmax - xmin
        yheight = ymax - ymin
        ylimmin = ymin #- 0.2*yheight
        ylimmax = ymax #+ 0.3*yheight
        
        #print(xmin,xmax,ymin,ymax)
        
        Figure = plt.figure( figsize=(15,12),dpi=120,facecolor='w',edgecolor='w' )
        plt.subplots_adjust(bottom=.02, left=.06, right=.95, top=.98, wspace=0.0, hspace=0.0) 
        
        ax = plt.subplot(111)
        
        ###--------------------------------------------------------------------------------------------------------------------------------
        ##  1st Top Plot: Lines
        ###--------------------------------------------------------------------------------------------------------------------------------
        ax1_top = subplot2grid( (22,28), (0,0), colspan=20, rowspan=2 )       #sets the position and size of the panel for Plot #01
        ax1_top.axis('off')
        
        ax1_top.set_xlim( xmin,xmax )
        ax1_top.set_ylim( ylimmin,ylimmax)
        
        self.EmissionLines( xmin, xmax, ymin, ymax, xwidth, yheight, self.listvalEL, self.listnamEL, self.list_pref )
        
        ###--------------------------------------------------------------------------------------------------------------------------------
        ##  1st Plot: Observed and Synthethic Spectra
        ###--------------------------------------------------------------------------------------------------------------------------------
        ax1 = subplot2grid( (22,28), (2,0), colspan=20, rowspan=10 )          #sets the position and size of the panel for Plot #01
        ax1.grid()
        
        #print(xmin,xmax,ymin,ymax)
        
        ax1.set_xlim( xmin,xmax )
        ax1.set_ylim( ylimmin,ylimmax)
        
        Ny = 8
        Nx = 12
        ax1.xaxis.set_major_locator(plt.MaxNLocator(Nx))
        ax1.xaxis.set_minor_locator(plt.MaxNLocator(Nx*2))
        ax1.yaxis.set_major_locator(plt.MaxNLocator(Ny))
        ax1.yaxis.set_minor_locator(plt.MaxNLocator(Ny*2))
        
        ## Plotting spectra
        Plot_1a, = plt.plot(l, f,'#EF7E00',linewidth=1.8, label='Observed')   # input: Orange # Observed spectrum
        Plot_1b, = plt.plot(l, b,'#3498db',linewidth=1.2, label='Best-fit')   # output: Blue  # Best-fit spectrum
                            
        Plot_1c, = plt.plot(l, s,'#4C534B',linewidth=1.2, label='Stellar')    # output: Verde #  Stellar spectrum
        Plot_1d, = plt.plot(l, n,'#870403',linewidth=1.2, label='Nebular')    # output:  Rosa #  Nebular spectrum
    
        ax1.fill_between(l, 0, s, color='lightgreen')
        ax1.fill_between(l, 0, n, color='pink')
    
        #AbsorptionLines(ymin,ymax,xwidth,yheight)
    
        ax1.legend(loc='upper left', frameon=False)
    
        normalization = self.fluxunit * self.galsnorm
        SciNum        = normalization
        SciNum_10     = self.sci_notation( SciNum, 3 )
        
        ylabel_txt = r'$\mathrm{F}_{\lambda} \  / \ \mathrm{F}_{%d\ \AA}\ \times {%s}$' % (self.lambda_0,SciNum_10)
        ylabel(ylabel_txt,family='serif',fontsize=16)

        #ylabel('$\mathrm{F}_{\lambda} \  / \ \mathrm{F}_{4020\ \AA}$',family='serif',fontsize=18)
        #ax1.axes.get_xaxis().set_ticks([])                                         #removes the ticks from the x axis
        #yticks = ax1.yaxis.get_major_ticks()
        #yticks[-1].label1.set_visible(False)
    
        ###--------------------------------------------------------------------------------------------------------------------------------
        ##  2nd Plot: Observed and Synthethic Spectra difference
        ###--------------------------------------------------------------------------------------------------------------------------------
        ax2 = subplot2grid( (22,28), (13,0), colspan=20,rowspan=5 )       #sets the position and size of the panel for Plot #02
        ax2.grid()
        
        ## Axis limits
        if ymin_residual == ymax_residual or (ymin_residual == -999.0 and ymax_residual == -999.0):
            ymin_residual=np.min(-e)-0.1*(np.max(e)-np.min(e)) 
            ymax_residual=np.max(+e)+0.1*(np.max(e)-np.min(e))
            
        #print( ymin_residual,ymax_residual )
            
        ax2.set_xlim( xmin,xmax )
        ax2.set_ylim( ymin_residual,ymax_residual )
          
        Ny = 8
        Nx = 12
        ax2.xaxis.set_major_locator(plt.MaxNLocator(Nx))
        ax2.xaxis.set_minor_locator(plt.MaxNLocator(Nx*2))
        ax2.yaxis.set_major_locator(plt.MaxNLocator(Ny))
        ax2.yaxis.set_minor_locator(plt.MaxNLocator(Ny*2))
        
        rr = np.where( m == 0, r, 0.0 )
        rl = np.where( m == 5, r, 0.0 )
        ra = 0.0 * rr
        
        ## Mask shadding
        #for i in range(len(l)):
        #    if m[i] == 1:
        #        Shading_X=[l[i],l[i]]
        #        Shading_Y=[ylimmin,ylimmax]
        #        plt.plot(Shading_X,Shading_Y,'BLUE',linewidth=1 )
        #indx = np.arange(0,len(l),1)
        #mask = (m == 1.0)
        
        min1ll = min( l[np.size(l)-1], xmin )
        max1ll = l[np.size(l)-1]
        
        min2ll = l[0]
        max2ll = max( l[0],xmax )
        
        max1ll_ = max1ll
        min2ll_ = min2ll
        for counter, value in enumerate(l):
            #print(counter, value)
            if m[counter] == 0 and r[counter] > 0.0 and max1ll_ > l[counter]:
                max1ll_ = l[counter]
            if m[counter] == 5 and r[counter] > 0.0 and max1ll  > l[counter]:
                max1ll  = l[counter]
            if m[counter] == 0 and r[counter] > 0.0 and min2ll_ < l[counter]:    
                min2ll_ = l[counter]
            if m[counter] == 5 and r[counter] > 0.0 and min2ll  < l[counter]:    
                min2ll  = l[counter]
                
        #print( max1ll,max1ll_ )
                
        max1ll = min( max1ll,max1ll_ )
        min2ll = max( min2ll,min2ll_ )
        #print(min_ll,max_ll)
        
        #print(mask,subset_indx)
        #ll = np.where( (m == 1) & (l < 4000.), l, 9.0e30 )
        #mask = [ (m != 1 ) & (f <= 0.0) ]
        #ll = np.array(l)
        #eps  = 1.0e-5
        #a     = list(m)
        #min_f = min(i for i in m if i==1)
        #max_f = max(i for i in m if i==1)
        #ind_1 = a.index(min_f)
        #ind_2 = a.index(max_f)
        #if ind_1 > 1:
        #    ind_1 -= 1
        #print(min_f,max_f,l[ind_1],l[ind_2])
        
        #ll[mask]
        #print(ll)
        #min_ll = 0.0
        #max_ll = l[ind_1]
        #ax2.fill([min1ll,min1ll,max1ll,max1ll], [ymin,ymax,ymax,ymin], fill=False, hatch='\\',color='#A0A0A1')
        ax2.fill([min1ll,min1ll,max1ll,max1ll], [ymin,ymax,ymax,ymin], fill=False, hatch='\\',color='#FF4343')
        ax2.fill([min2ll,min2ll,max2ll,max2ll], [ymin,ymax,ymax,ymin], fill=False, hatch='\\',color='#FF4343')
        
        ## Plotting Residuals    
        Plot_4a = plt.plot( l, ra, color='#EF7E00', linewidth=1.5 )
        Plot_4a = plt.plot( l, rl, color='#66181E', linewidth=1.2 )        
        Plot_4a = plt.plot( l, rr, color='#5989AD', linewidth=1.2 ) 
    
        #ax2.fill_between( l, rl, rl*0, where=rl >= 0.0, facecolor='#66181E', interpolate=True )
        ax2.fill_between( l, rl, rl*0, where=rl >= 0.0, facecolor='red', interpolate=True )
    
        ## Axis labeling
        xlabel('$\lambda \, (\AA)$',family='serif',fontsize=16)
        ylabel('$\Delta_{\lambda}$',family='serif',fontsize=16)
        
        #yticks = ax2.yaxis.get_major_ticks()
        #yticks[0].label1.set_visible(False)
        #yticks[-1].label1.set_visible(False)
    
        ###--------------------------------------------------------------------------------------------------------------------------------
        ##  3rd Plot: SSP Light Percentage
        ###--------------------------------------------------------------------------------------------------------------------------------
        ax3 = subplot2grid( (22,28), (2,22), colspan=22, rowspan=5 )        #sets the position and size of the panel for Plot #03
        ax3.axis("on")
        #ax3.axes.get_xaxis().set_ticks([])
        #ax3.axes.get_yaxis().set_ticks([])
                
        ## Defining variables
        minimum_age = np.min( self.log_age_stellar_pop[0:self.num_base] )
        maximum_age = np.max( self.log_age_stellar_pop[0:self.num_base] )
        maxmindif_age = maximum_age - minimum_age
        
        sorted_met    = np.sort( self.met_stellar_pop[0:self.num_base] )
        minmindif_met = sorted_met[1:self.num_base] - sorted_met[0:self.num_base-1]
        index_dif_met = np.arange(0,len(minmindif_met),1)
        index_dif_met = index_dif_met[ minmindif_met > 0.0 ]
        minmindif_met = minmindif_met[ minmindif_met > 0.0 ]
        
        #print(minmindif_met,np.size(minmindif_met))
        N_Zs = np.size(minmindif_met) + 1
        N_ts = np.empty(0)
        
        # Se for igual a zero ou temos uma única metalicidade ou algo errado (assume-se o primeiro)
        if np.size(minmindif_met) > 1:
            Z_grid = sorted_met[0]
            Z_grid = np.append( Z_grid, sorted_met[ index_dif_met+1 ] )
            
        z = np.empty(0)
        for a in enumerate(Z_grid):
            x = self.age_stellar_pop[ (self.age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            z = np.concatenate( (x,z) )
            N_ts = np.append( N_ts,np.size(x) ) # Number of ages per metallicity
            
        #z = np.unique(z)
        #print(z)
        
        TOL = 1.0e3 # years
        b = z.copy()
        b.sort()
        d = np.append(True, np.diff(b))
        #print(d.shape,d[0],d[1],d[4])
        #print(d)
        #d[0] = d[N_Zs]
        result = b[d>TOL]
        result = np.append(z[0],result)
        xx = np.log10(result)
        
        #print('Old ages: ',TOL,z)
        #print('New ages: ',TOL,result)
        
        #N_ts_str = np.array( N_ts, dtype='int' )
        
        print( "Metallicities: {} and Number of metallicities: {}".format(Z_grid,np.size(Z_grid)) )
        print( "Ages per metallicity: {}".format(N_ts,np.size(N_ts)) )
        
        #print(self.log_age_stellar_pop[0:self.num_base])
        #print(self.met_stellar_pop[0:self.num_base])
        #print(minimum_age,maximum_age,maxmindif_age)
        
        ## Plotting Stacked Bars
        barheight = 0
        # Width of the bars
        # Take the minimum between ages
        
        minmindif_age = np.max( np.log10( np.abs(result[1:len(result)]) ) - np.log10( np.abs(result[0:len(result)-1]) ) )
        bar_width = min( minmindif_age, 0.05 )
        #print('bar_width ==',bar_width,minmindif_age)
        
        #cmap = sns.cubehelix_palette(light=1, as_cmap=True)
        # Sequential palette of colors
        #csns = sns.color_palette("cubehelix", 25)
        #csns = sns.cubehelix_palette( N_Zs, start=0.5, rot=0, dark=0, light=.75, reverse=True )
        csns = sns.color_palette("colorblind", N_Zs)
        ax3.set_prop_cycle( cycler('color', csns) )
        Z_colour  = ['DarkOrchid','SlateBlue','RoyalBlue','SeaGreen','GoldenRod','Tomato']
        #Z_colour = csns
        
        colour_index = np.arange(0,len(Z_colour),1) 
        
        Luminosity_sum = self.light_fractions[0:self.num_base].sum()
        #print(Luminosity_sum)
        
        #print("")
        sum_yy = 0.0
        result_light_fraction = np.zeros( np.size(result) )
        for a in enumerate(Z_grid):
            #print(a[0],a[1])
            
            x = self.log_age_stellar_pop[ (self.log_age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            y = self.light_fractions[ (self.log_age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            
            # Re-map x_ and y into result and yy
            x_ = self.age_stellar_pop[ (self.age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            
            yy = np.zeros( np.size(result) )
            for i in enumerate(result):
                #x_ = 10.0**(x)
                w = (x_ >= ( i[1] - TOL )) & (x_ <= ( i[1] + TOL ))
                
                #if i[0] == 0:
                #    print(w,i[1],i[1]-TOL,i[1]+TOL,x_[0]-TOL,x_[0]+TOL)
                
                y_ = y[ (x_ >= ( i[1] - TOL )) & (x_ <= ( i[1] + TOL )) ]
                #print(np.size(y_),y_)
                if np.size(y_) > 0:
                    yy[i[0]] = np.sum(y_)
                else:
                    yy[i[0]] = 0.0
                
                result_light_fraction[i[0]] += yy[i[0]]/Luminosity_sum
                
            sum_yy += sum(yy)
            #print( a[0],sum_yy,Luminosity_sum,sum_yy/Luminosity_sum  )
            
            # This is the old
            #y = y / Luminosity_sum * 100.0
            #bar( x, y, width=bar_width, color=Z_colour[colour_index[a[0]]], edgecolor='none', align='center' )
            
            yy = yy / Luminosity_sum * 100.0
            bar( xx, yy, width=bar_width, color=Z_colour[colour_index[a[0]]], bottom=barheight, edgecolor='none', align='center' )
            
            if a[0] == 0:
                barheight = yy
            if a[0]  > 0:
                # Stacking remaning Bars
                barheight += yy
        
        #print( result_light_fraction, sum(result_light_fraction) )        
        # Density Plot and Histogram of all arrival delays
        #sns.distplot( flights['arr_delay'], hist=True, kde=True, bins=int(180/5), color = 'darkblue', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 4})
        #import seaborn as sns
        #import pandas as pd
        
        #df = pd.DataFrame(dict(x=result,y=result_light_fraction))
        ##print(df)
        #sns.distplot( df['x'], hist=False, kde=True, bins=df['y'], color = 'darkblue', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 4})
        
        #from scipy.stats import multivariate_normal
        
        #from scipy.stats.distributions import norm
        x_d_min = np.log10(result[0])
        x_d_max = np.log10(result[-1])
        
        sigma   = 0.2
        if (x_d_min - 4.0*sigma) > 0.0:
            x_d_min = x_d_min - 4.0*sigma
        else:
            x_d_min = 0.0
        
        x_d = np.linspace(x_d_min, x_d_max, 1000)
        #density = norm(np.log10(result[0])).pdf(x_d)
        #density = result_light_fraction[xi[0]] * norm(xi[1]).pdf(x_d)

        #density /= sum(density) / 100.0
        #print(x_d, density, sum(density))
        density = 0.
        for i in enumerate(result):
            mu = np.log10(result[i[0]])
            density += result_light_fraction[i[0]] * 1.0/(sigma * np.sqrt(2.0 * np.pi)) * np.exp( - (x_d - mu)**2 / (2.0 * sigma**2) )
            
        density /= np.max(density) / np.max(result_light_fraction) / 100.0
        
        ax3.fill_between( x_d, density, alpha=0.2 )
        ax3.plot( x_d, density, -0.1, '|k', markeredgewidth=1, alpha=0.4 )

        # Mean stellar age weighted by Light and base elements
        max_barheight = np.max(barheight)
        max_yvalue    = max_barheight + 0.105 * max_barheight
        #ax3.arrow( logt_L, maxyvalue, 0.0, -0.05*maxyvalue, fc="Gray", ec="Gray",head_width=0.1, head_length=1 )
        
        #for ages in range(len(log_age_Z[0,:])):
        #    Base_x = np.array([log_age_Z[0,ages],log_age_Z[0,ages]])
        #    Base_y = np.array([0.96*maxyvalue, maxyvalue])
        #    plt.plot(Base_x, Base_y,color='Black',linewidth=1)

        ax3.set_xlim( x_d_min,x_d_max )

        Ny = 10
        Nx = 10
        ax3.xaxis.set_major_locator(plt.MaxNLocator(Nx))
        ax3.xaxis.set_minor_locator(plt.MaxNLocator(Nx*2))
        ax3.yaxis.set_major_locator(plt.MaxNLocator(Ny))
        ax3.yaxis.set_minor_locator(plt.MaxNLocator(Ny*2))

        ## Axis labeling
        ylabel_txt = r'L $_{%d}$ (${%s}$)' % (self.lambda_0,'\%')
        #xlabel('log age [years]',family='serif',fontsize=16)
        ylabel(ylabel_txt,family='serif',fontsize=16)

        ###--------------------------------------------------------------------------------------------------------------------------------
        ##  4th Plot: SSP Mass Percentage         (uses internal variables from the 3rd Plot)
        ###--------------------------------------------------------------------------------------------------------------------------------
        #ax3 = subplot2grid( (22,28), (2,22), colspan=22, rowspan=5 )        #sets the position and size of the panel for Plot #03
        #ax3.axis("on")
        ax4 = subplot2grid((22,28), (8,22), colspan=22,rowspan=5)        #sets the position and size of the panel for Plot #04

        Mass_sum = self.mass_fractions[0:self.num_base].sum()

        ## Defining variables
        barheight = 0        
        
        ## Plotting Stacked Bars
        sum_yy = 0
        result_mass_fraction = np.zeros( np.size(result) )
        for a in enumerate(Z_grid):
            
            x = self.log_age_stellar_pop[ (self.log_age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            y = self.mass_fractions[ (self.log_age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            
            # Re-map x_ and y into result and yy
            x_ = self.age_stellar_pop[ (self.age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            
            yy = np.zeros( np.size(result) )
            for i in enumerate(result):
                #x_ = 10.0**(x)
                w = (x_ >= ( i[1] - TOL )) & (x_ <= ( i[1] + TOL ))
                
                #if i[0] == 0:
                #    print(w,i[1],i[1]-TOL,i[1]+TOL,x_[0]-TOL,x_[0]+TOL)
                
                y_ = y[ (x_ >= ( i[1] - TOL )) & (x_ <= ( i[1] + TOL )) ]
                #print(np.size(y_),y_)
                if np.size(y_) > 0:
                    yy[i[0]] = np.sum(y_)
                else:
                    yy[i[0]] = 0.0
                
                result_mass_fraction[i[0]] += yy[i[0]]/Mass_sum
                
            sum_yy += sum(yy)
            #print( a[0],sum_yy,Mass_sum,sum_yy/Mass_sum  )
            
            # This is the old
            #y = y / Mass_sum * 100.0
            #bar( x, y, width=bar_width, color=Z_colour[colour_index[a[0]]], edgecolor='none', align='center' )
            
            yy = yy / Mass_sum * 100.0
            bar( xx, yy, width=bar_width, color=Z_colour[colour_index[a[0]]], bottom=barheight, edgecolor='none', align='center' )
            
            if a[0] == 0:
                barheight = yy
            if a[0]  > 0:
                # Stacking remaning Bars
                barheight += yy
            
        #from scipy.stats.distributions import norm
        x_d_min = np.log10(result[0])
        x_d_max = np.log10(result[-1])
        
        sigma   = 0.2
        if (x_d_min - 4.0*sigma) > 0.0:
            x_d_min = x_d_min - 4.0*sigma
        else:
            x_d_min = 0.0
        
        x_d = np.linspace(x_d_min, x_d_max, 1000)
        #density = norm(np.log10(result[0])).pdf(x_d)
        #density = result_light_fraction[xi[0]] * norm(xi[1]).pdf(x_d)

        #density /= sum(density) / 100.0
        #print(x_d, density, sum(density))
        density = 0.
        for i in enumerate(result):
            mu = np.log10(result[i[0]])
            density += result_mass_fraction[i[0]] * 1.0/(sigma * np.sqrt(2.0 * np.pi)) * np.exp( - (x_d - mu)**2 / (2.0 * sigma**2) )
            
        density /= np.max(density) / np.max(result_mass_fraction) / 100.0
        
        # F8E8CD
        #ax4.fill_between( x_d, density, alpha=0.2, color='#F8E8CD' )
        ax4.fill_between( x_d, density, alpha=0.2 )
        ax4.plot( x_d, density, -0.1, '|k', markeredgewidth=1, alpha=0.4 )

        # Mean stellar age weighted by Light and base elements
        max_barheight = np.max(barheight)
        max_yvalue    = max_barheight + 0.105 * max_barheight

        ax4.set_xlim( x_d_min,x_d_max )

        Ny = 10
        Nx = 10
        ax4.xaxis.set_major_locator(plt.MaxNLocator(Nx))
        ax4.xaxis.set_minor_locator(plt.MaxNLocator(Nx*2))
        ax4.yaxis.set_major_locator(plt.MaxNLocator(Ny))
        ax4.yaxis.set_minor_locator(plt.MaxNLocator(Ny*2))

        ## Axis labeling
        ylabel_txt = r'M (${%s}$)' % ('\%')
        xlabel('log age [years]',family='serif',fontsize=16)
        ylabel(ylabel_txt,family='serif',fontsize=16)
            
        ###--------------------------------------------------------------------------------------------------------------------------------
        ##  Legend for 3th and 4th PLots
        ###--------------------------------------------------------------------------------------------------------------------------------
        #ax5 = subplot2grid((22,28), (12,22), colspan=6,rowspan=6)       #sets the position and size of the panel for Plot #02
        ax5 = subplot2grid((22,28), (1,22), colspan=6,rowspan=1)
        
        ind   = 0
        ind_i = 0
        ind_j = 0
        for a in enumerate(Z_grid): 
            #colour_index.append( int(Z_grid.index(Z_list[a])) )    #so that the colors always match the same Z
            #annotate(r'$\mathtt{Z \ = \ %s}$'%Z_list[a],size=14,color=Z_colour[colour_index[a]],xy=(0.50, 0.60-0.08*a),horizontalalignment='center',verticalalignment='center',xycoords='axes fraction')
            #value_Z = r'$\mathtt{Z \ = \ {:8.3f}}$'.format(Z_grid[a[0]])
            value_Z = r'$\mathtt{Z \ = \ %8.3f}$' % Z_grid[a[0]]
            #annotate( value_Z, size=8.2, color=Z_colour[a[0]], xy=(0.10 + 0.20*col, 1.1-0.3*a[0]), horizontalalignment='center', verticalalignment='center', xycoords='axes fraction')
            annotate( value_Z, size=8.2, color=Z_colour[a[0]], xy=(0.10 + 0.30*ind_i, 1.1-0.3*ind_j), horizontalalignment='center', verticalalignment='center', xycoords='axes fraction')
        
            ind   += 1
            ind_j += 1
        
            if ind == 4:
                ind_i += 1
                ind_j  = 0                
                ind    = 0
                
        ax5.axis('off') 





        #axes2.show()
        #plt.show()
        #plt.savefig('test1.png')
        # Plot Fit FADO ###################################################################################################################


        # Emission-Lines to be showed #####################################################################################################
    def EmissionLines( self, xmin, xmax, ymin, ymax, xwidth, yheight, listvalEL, listnamEL, list_pref ):
    
        N_Elines = len(listvalEL)
        print("Number of ELs: {}".format(N_Elines))
        
        printELs = np.zeros(N_Elines)
        printELs += 1
        #print(printELs)
        print(len(listvalEL),len(listnamEL),len(list_pref))
        
        #print(xwidth,xwidth/24.)
        visual_resolution = xwidth/24.
        
        # Subsample of lists for the preference ones
        ind_list_pref = np.array(list_pref, dtype=int)        
        sub_listindex = np.arange(0,len(ind_list_pref),1)
        sub_listvalEL = np.array(listvalEL)
        sub_listnamEL = np.array(listnamEL)
        
        sub_listindex = sub_listindex[ ind_list_pref==1 ]
        sub_listvalEL = sub_listvalEL[ ind_list_pref==1 ]
        sub_listnamEL = sub_listnamEL[ ind_list_pref==1 ]
        
        #print( sub_listvalEL,sub_listnamEL,sub_listindex )
        
        # First loop over the preference list subsample of emission-lines
        for counter in enumerate(sub_listvalEL):
            ind = sub_listindex[ counter[0] ]
            #print( 'AGORA: ',counter[0],listvalEL[ind],printELs[ind], ind, ind+N_Elines-ind )
            
            if listvalEL[ind] > xmin and listvalEL[ind] < xmax and printELs[ind] == 1:
                x1 = np.array(listvalEL[ind])
                x  = np.array([x1,x1])
                y  = np.array([ymin-0.1*yheight,ymin+0.025*yheight])
    
                #print( x, y )
                for i in range(N_Elines-ind): 
                    
                    if ind+i < N_Elines:
                        #print(ind+i,listvalEL[ind+i])
                        if np.abs( listvalEL[ind+i] - listvalEL[ind] ) <= visual_resolution:
                            printELs[ind+i] = 0
    
                plt.plot( x, y, color='black', linestyle='-', linewidth=0.5)
                plt.annotate( listnamEL[ind], color='black', xy=(x[0]+0.0012*xwidth,y[1]+0.05*yheight), size=9, rotation=90, 
                              horizontalalignment='center', verticalalignment='bottom')
                del x1
                del x
                del y
        
        del ind_list_pref
        del sub_listindex
        del sub_listvalEL
        del sub_listnamEL
        
        # Then loop over the rest of the lines
        for counter in enumerate(listvalEL):
            #print(counter[0])          
            #print(listvalEL[counter[0]],xmin,xmax)
            #print(listvalEL[counter[0]] > xmin and listvalEL[counter[0]] < xmax)
            
            if listvalEL[counter[0]] > xmin and listvalEL[counter[0]] < xmax and printELs[counter[0]] == 1 and list_pref[counter[0]] == 0:
                x1 = np.array(listvalEL[counter[0]])
                x  = np.array([x1,x1])
                y  = np.array([ymin-0.1*yheight,ymin+0.025*yheight])
    
                #print( x, y )
                for i in range(N_Elines-counter[0]+1):          
                    if counter[0]+i < N_Elines-1:
                        if ( listvalEL[counter[0]+i] - listvalEL[counter[0]] ) < visual_resolution:
                            printELs[counter[0]+i] = 0
    
                plt.plot( x, y, color='black', linestyle='-', linewidth=0.5)
                plt.annotate( listnamEL[counter[0]], color='black', xy=(x[0]+0.0012*xwidth,y[1]+0.05*yheight), size=9, rotation=90, 
                              horizontalalignment='center', verticalalignment='bottom')
                del x1
                del x
                del y
                
        del printELs
                
        return
        # Emission-Lines to be showed #####################################################################################################
