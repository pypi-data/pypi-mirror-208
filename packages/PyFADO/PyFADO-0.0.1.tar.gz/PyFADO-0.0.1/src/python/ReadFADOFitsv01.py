#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:40:24 2019

RESUME : FADO plotting routine in Python

Version: v01 beta

@author: Jean Gomes Copyright (c) pyFADO

@email: jean@iastro.pt
    
License: pyFADO module  is freely available under the General 
Public License (GPL).

If you would like to redistribute it  or if  you made changes 
please contact jean@iastro.pt in order  to  avoid duplication 
of the package. This will help the future mantainance. 
                                                                      
Publications  making  use  of  this  pyFADO module  FADO must 
acknowledge   the   presentation  article  of  the  code  by 
Gomes & Papaderos (2017) 
            

DISCLAIMER
          
THIS SOFTWARE IS PROVIDED  BY THE COPYRIGHT  HOLDERS "AS IS"
AND ANY EXPRESS OR  IMPLIED WARRANTIES,  INCLUDING, BUT  NOT
LIMITED TO,  THE IMPLIED  WARRANTIES OF MERCHANTABILITY  AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT,  INDI-
RECT,   INCIDENTAL,  SPECIAL,  EXEMPLARY,  OR  CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBS- 
TITUTE GOODS OR SERVICES; LOSS OF USE,  DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED  AND  ON ANY THEORY OF 
LIABILITY,  WHETHER  IN CONTRACT, STRICT  LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE)  ARISING  IN ANY WAY OUT
OF  THE  USE  OF  THIS  SOFTWARE, EVEN  IF  ADVISED  OF  THE
POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import print_function, division, absolute_import

import os

# Import astropy library
from astropy.io import fits
import numpy as np
from astropy import units as u

import matplotlib.pyplot as plt
from pylab import *

#from .PlotFADOv01 import PlotFADO
from PlotFADOv01 import PlotFADO

# Class of objects
class mean_stellar(object):
    
    def __init__( self, light, mass, oneGyr=False, solarmet=False ):
        self.light = light
        self.mass = mass
        if oneGyr:
            self.light_1Gyr = light / 1.0e9
            self.mass_1Gyr = mass / 1.0e9
        if solarmet:
            self.light_solar = light / 0.02  
            self.mass_solar = mass / 0.02
            
class mass(object):
    
    def __init__( self, ever, corr ):
        self.ever      = ever
        self.corrected = corr
        
class redshift(object):
    
    def __init__( self, value, v ):
        c = 299792.458 # [km/s]
        
        # Convert the shifts to final redshift and equivalent velocity in km/s
        self.firstvalue = value
        self.value      = (1.0+value) * (1.0+v/c) - 1.0
        self.velocity   = self.value * c
        # It should not matter for low velocities
        self.relativistic_velocity  = c * ( ( (1.+self.value)**2 - 1. ) / ( (1.+self.value)**2 + 1. ) )

class ReadFADOFits(object):
    """ ============================================================
 @author: Jean Gomes 
 @date  : Mon Apr 29 14:40:24 2019
 License: pyFADO module  is freely available under the General Public License (GPL).
 Resume : pyFADO reading fits class in Python from the output files of the FADO run.
 
 How to use it
 
 First import this reading library containing all the classes

 from ReadFADOFitsv01 import ReadFADOFits
 
 For a run of FADO with a given galaxy then you have 4 files:
 * galaxy_1D.fits
 * galaxy_DE.fits
 * galaxy_EL.fits
 * galaxy_ST.fits
 
 name   = 'galaxy'
 galaxy = ReadFADOFits( name, path=path, showheader=False )
 
 path and showheader arguments are optional.
 
 Then you read the files and store into the galaxy object.
 
 Disclaimer
           
 THIS SOFTWARE IS PROVIDED  BY THE COPYRIGHT  HOLDERS "AS IS"
 AND ANY EXPRESS OR  IMPLIED WARRANTIES,  INCLUDING, BUT  NOT
 LIMITED TO,  THE IMPLIED  WARRANTIES OF MERCHANTABILITY  AND
 FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT,  INDI-
 RECT,   INCIDENTAL,  SPECIAL,  EXEMPLARY,  OR  CONSEQUENTIAL 
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBS- 
 TITUTE GOODS OR SERVICES; LOSS OF USE,  DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED  AND  ON ANY THEORY OF 
 LIABILITY,  WHETHER  IN CONTRACT, STRICT  LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE)  ARISING  IN ANY WAY OUT
 OF  THE  USE  OF  THIS  SOFTWARE, EVEN  IF  ADVISED  OF  THE
 POSSIBILITY OF SUCH DAMAGE.
 ============================================================
 """
     
    def __init__( self, name, path='./', showheader=False, printspectrum=False, printpopvector=False, printstavector=False ):
        self.name_1D       = name + '_1D.fits'
        self.name_DE       = name + '_DE.fits'
        self.name_ST       = name + '_ST.fits'
        
        if path[len(path)-1] != '/':
            path = path + '/'
            
        self.path          = path
        
        # Check if directory and FADO files exist
        path__to__dir = os.path.isdir(self.path)
        name_1D_exist = os.path.isfile(self.path + self.name_1D)
        name_DE_exist = os.path.isfile(self.path + self.name_DE)
        name_ST_exist = os.path.isfile(self.path + self.name_ST)
        
        #print(path__to__dir,name_1D_exist,name_DE_exist)
        if path__to__dir and name_1D_exist and name_1D_exist and name_ST_exist:
            self.showheader     = showheader
            self.printspectrum  = printspectrum
            self.printpopvector = printpopvector
            self.printstavector = printstavector
            
            self.Read1DFits( self.showheader, self.printspectrum )
            print("")
            self.ReadDEFits( self.showheader, self.printpopvector )
            print("")
            self.ReadSTFits( self.showheader, self.printstavector )
                
        else:
            print("Error: verify if directory and/or files exist")
            print("    Directory: {} ==> {}".format(self.path,path__to__dir))
            print("_1D extension: {} ==> {}".format(self.name_1D,name_1D_exist))
            print("_DE extension: {} ==> {}".format(self.name_DE,name_DE_exist))
            print("_ST extension: {} ==> {}".format(self.name_ST,name_ST_exist))
        
        # Reading FADO one-dimensional spectra image ######################################################################################
    def Read1DFits( self, showheader=False, printspectrum=False ):
    
        # open fits file
        full_path = self.path + self.name_1D
        fits_file = fits.open(full_path)
    
        print('File info from FADO: _1D.fits extension')
        print(fits_file.info())
    
        header = fits_file[0].header
    
        #print("Print header of file")
        if showheader:
            print('')
            print('showheader: {}'.format(showheader))
            print(repr(header))
       
        #with fits_file as hdul:
        #    hdul.info()
    
        #for i in header.info():
        #    print(i)
    
        data = fits_file[0].data
        
        self.Naxis1_1D = fits_file[0].header['NAXIS1']
        self.Naxis2_1D = fits_file[0].header['NAXIS2']
        print("Naxis1: {} x Naxis2: {} pixels".format(self.Naxis1_1D,self.Naxis2_1D))
        
        self.CRVAL1_1D = header['CRVAL1']
        self.CRPIX1_1D = header['CRPIX1']
        self.CDELT1_1D = header['CDELT1']
        
        self.arq_base = header['ARQ_BASE']                                                       
        self.arq_conf = header['ARQ_CONF']
        
        self.olsynini = header['OLSYNINI']
        self.olsynfin = header['OLSYNFIN']
        self.olsyndel = header['OLSYNDEL']        
        
        self.galsnorm = header['GALSNORM']
        self.lambda_0 = header['LAMBDA_0']
        self.fluxunit = header['FLUXUNIT']
        self.fluxunit = 10**(self.fluxunit)
        
        # Redshift
        self.redshift_aux = header['REDSHIFT']
        
        l = []
        j = 0
        for i in range(self.Naxis1_1D):
            l.append( self.CRVAL1_1D + (j-1) * self.CDELT1_1D )
            j = j + 1
        
        #f = data[0]
        #e = data[1]
        #m = data[2]
        #b = data[3]
        #s = data[7]
        #n = data[8]
        
        # Residual - Sem tratamentos dentários
        #r = f - b
        r = data[0] - data[3]
        
        # Close fits file
        fits_file.close()
    
        # Store everything in spectrum
        self.spectrum = np.zeros((self.Naxis1_1D,8))
        self.spectrum[:,0] = l[:]    # lambda
        self.spectrum[:,1] = data[0] # Flux
        self.spectrum[:,2] = data[1] # Error
        self.spectrum[:,3] = data[2] # Mask
        self.spectrum[:,4] = data[3] # Best-fit
        self.spectrum[:,5] = data[7] # Smoothed
        self.spectrum[:,6] = data[8] # Nebular
        self.spectrum[:,7] = r[:]    # Residual sem tratamentos dentários
        
        # Delete
        del data
        del r
        del l
        ###--------------------------------------------------------------------------------------------------------------------------------

        if printspectrum:
            print('')
            print('Print extracted spectra')
            print(self.spectrum)

#        return spectrum
        # Reading FADO one-dimensional spectra image ######################################################################################

        # Reading FADO DE population vectors ##############################################################################################
    def ReadDEFits( self, showheader=False, printpopvector=False ):
    
        # open fits file
        full_path = self.path + self.name_DE
        fits_file = fits.open(full_path)
    
        print('File info from FADO: _DE.fits extension')
        print(fits_file.info())
    
        header = fits_file[0].header
    
        #print("Print header of file")
        if showheader:
            print('')
            print('showheader: {}'.format(showheader))
            print(repr(header))
       
        #print(repr(header))
        #with fits_file as hdul:
        #    hdul.info()
    
        #for i in header.info():
        #    print(i)
    
        data = fits_file[0].data
        
        self.Naxis1_DE = fits_file[0].header['NAXIS1']
        self.Naxis2_DE = fits_file[0].header['NAXIS2']
        print("Naxis1: {} x Naxis2: {} pixels".format(self.Naxis1_DE,self.Naxis2_DE))
        
        self.CRVAL1_DE = header['CRVAL1']
        self.CRPIX1_DE = header['CRPIX1']
        self.CDELT1_DE = header['CDELT1']
        
        self.numparam = header['NUMPARAM']                                                 
        self.num_base = header['NUM_BASE']                                           
        self.nindivid = header['NINDIVID']
        
        # Extinction parameters
        self.reddening_law       = header['R_LAWOPT']
        self.AV_extinction       = header['GEXTINCT'] #* u.mag                                          
        self.AV_extinction_error = header['GEXTBDEV'] #* u.mag
        
        self.AV_extinction_nebular = header['GNEBULAR'] #* u.mag                                          
        self.AV_extinction_nebular_error = header['GNEBBDEV'] #* u.mag
        
        #print(self.AV_extinction, self.AV_extinction_error)
        
        #GNEBULAR=            2.063E+00                                                  
        #GNEBBDEV=            4.148E-0
        
        # Kinematics
        #V0SYSGAL=            4.501E+01                                                  
        #V0SYSDEV=            7.105E-15                                                  
        #VTSYSGAL=           -2.083E+01                                                  
        #VTSYSDEV=            8.569E+01                                                  
        #VDSYSGAL=            1.054E+02
        self.systemic_velocity   = header['V0SYSGAL']
        self.velocity_dispersion = header['VDSYSGAL']
        
        # Call object redshift
        # It must have been read before
        self.redshift = redshift( self.redshift_aux,self.systemic_velocity )
        del self.redshift_aux
        
        #ROWNUM_1= 'Best solution - Light fractions'                                     
        #ROWNUM_2= 'Mean solution - Light fractions'                                     
        #ROWNUM_3= 'Med. solution - Light fractions'                                     
        #ROWNUM_4= 'Standard deviation - Light pop.'                                     
        #ROWNUM_5= 'Best solution - Mass  corrected'                                     
        #ROWNUM_6= 'Mean solution - Mass  corrected'                                     
        #ROWNUM_7= 'Med. solution - Mass  corrected'                                     
        #ROWNUM_8= 'Standard deviation - Mass  cor.'                                     
        #ROWNUM_9= 'Best solution - Mass     formed'                                     
        #ROWNUM10= 'Mean solution - Mass     formed'                                     
        #ROWNUM11= 'Med. solution - Mass     formed'                                     
        #ROWNUM12= 'Standard deviation - Mass  for.'
        #BASEPOPX= '13 ==> Single solution from one single spectrum'                     
        #BASECHI2= '14 ==> Single solution from one single spectrum'                     
        #BASEADEV= '15 ==> Single solution from one single spectrum'                     
        #BASEGEXT= '16 ==> Single solution from one single spectrum'                     
        #ROWS_LUM= '17-23 ==> Individual PV solutions - Light'                           
        #ROWSMCOR= '24-30 ==> Individual PV solutions - Mass corrected'                  
        #ROWSMFOR= '31-37 ==> Individual PV solutions - Mass    formed'                     
        #ROWS_AGE= '38 ==> Age of base elements'                                         
        #ROWSLAGE= '39 ==> Log of age--SSP base'                                         
        #ROWS_MET= '40 ==> Metallicity of base elements'                                 
        #ROWS_ALP= '41 ==> Alpha enhancement of base elements'
        
        self.light_fractions     = np.zeros((self.Naxis1_DE))
        self.mass_fractions      = np.zeros((self.Naxis1_DE))
        self.met_stellar_pop     = np.zeros((self.Naxis1_DE))
        self.log_age_stellar_pop = np.zeros((self.Naxis1_DE))
        self.age_stellar_pop     = np.zeros((self.Naxis1_DE))
        
        self.light_fractions[:]     = data[0] # Best solution - Light fractions
        self.mass_fractions[:]      = data[4] # Best solution - Mass  corrected
        self.met_stellar_pop[:]     = data[self.Naxis2_DE-4] 
        self.log_age_stellar_pop[:] = data[self.Naxis2_DE-5]
        self.age_stellar_pop[:]     = data[self.Naxis2_DE-6]
        
        #print(self.light_fractions)
        #print(sum(self.light_fractions[0:self.num_base-1]))
        #print(np.size(data[0]))
        
        #print(self.met_stellar_pop)
        #print(self.age_stellar_pop)
        #print(self.log_age_stellar_pop)
        
        ## Evaluate number of ages and metallicities
        #minimum_age   = np.min( self.log_age_stellar_pop[0:self.num_base] )
        #maximum_age   = np.max( self.log_age_stellar_pop[0:self.num_base] )
        
        sorted_met    = np.sort( self.met_stellar_pop[0:self.num_base] )
        minmindif_met = sorted_met[1:self.num_base] - sorted_met[0:self.num_base-1]
        index_dif_met = np.arange( 0,len(minmindif_met),1 )
        index_dif_met = index_dif_met[ minmindif_met > 0.0 ]
        minmindif_met = minmindif_met[ minmindif_met > 0.0 ]
        
        self.N_metallicities = np.size(minmindif_met) + 1
        self.N_ages = np.empty(0)
        
        # Se for igual a zero ou temos uma única metalicidade ou algo errado (assume-se o primeiro)
        if np.size(minmindif_met) > 1:
            Z_grid = sorted_met[0]
            Z_grid = np.append( Z_grid, sorted_met[ index_dif_met+1 ] )
            
        z = np.empty(0)
        for a in enumerate(Z_grid):
            x = self.age_stellar_pop[ (self.age_stellar_pop > -999.0) & (self.met_stellar_pop == Z_grid[a[0]]) ]
            z = np.concatenate( (x,z) )
            self.N_ages = np.append( self.N_ages,np.size(x) ) # Number of ages per metallicity
        
        # Close fits file
        fits_file.close()
    
        # Delete
        del data
        ###--------------------------------------------------------------------------------------------------------------------------------
        
        # Reading FADO DE population vectors ##############################################################################################

        # Reading FADO DE population vectors ##############################################################################################
    def ReadSTFits( self, showheader=False, printstavector=False ):
    
        # open fits file
        full_path = self.path + self.name_ST
        fits_file = fits.open(full_path)
    
        print('File info from FADO: _ST.fits extension')
        print(fits_file.info())
    
        header = fits_file[0].header
    
        #print("Print header of file")
        if showheader:
            print('')
            print('showheader: {}'.format(showheader))
            print(repr(header))
       
        
        #print(repr(header))
        
        #ROWNUM_1= 'Luminosity weighted mean stellar age'                                
        #ROWNUM_2= 'Mass weighted mean stellar age'                                      
        #ROWNUM_3= 'Luminosity weighted mean stellar age (LOG)'                          
        #ROWNUM_4= 'Mass weighted mean stellar age (LOG)'                                
        #ROWNUM_5= 'Luminosity weighted mean stellar metallicity'                        
        #ROWNUM_6= 'Mass weighted mean stellar metallicity'                              
        #ROWNUM_7= 'Mass ever formed'                                                    
        #ROWNUM_8= 'Mass presently available'                                            
        #ROWNUM_9= 'Mass ever formed pAGB'                                               
        #ROWNUM10= 'Mass presently available pAGB'                                       
        #ROWNUM11= 'Mass ever formed < 1 Gyr'                                            
        #ROWNUM12= 'Mass presently available < 1 Gyr'                                    
        #ROWNUM13= 'Mass ever formed < 5 Gyr'                                            
        #ROWNUM14= 'Mass presently available < 5 Gyr'                                    
        #ROWNUM15= 'Total Luminosity at lambda0'                                         
        #ROWNUM16= 'Total Luminosity from stars < 1 Gyr at l0'                           
        #ROWNUM17= 'Total Luminosity from stars < 5 Gyr at l0'
        #ROWNUM18= 'chi2    '                                                            
        #ROWNUM19= 'Sum pop X'                                                           
        #ROWNUM20= 'Sum pop M'                                                           
        #ROWNUM21= 'Stellar extinction'                                                  
        #ROWNUM22= 'Nebular extinction'                                                  
        #ROWNUM23= 'Systemic velocity stars'                                             
        #ROWNUM24= 'Velocity dispersion stars'                                           
        #ROWNUM25= 'Systemic velocity nebular'                                           
        #ROWNUM26= 'Velocity dispersion nebular'                                         
        #ROWNUM27= 'log Q(H)'                                                            
        #ROWNUM28= 'log Q(HeI)'                                                          
        #ROWNUM29= 'log Q(HeII)'                                                         
        #ROWNUM30= 'log Q(H) pAGB'                                                       
        #ROWNUM31= 'tau ratio'                                                           
        #ROWNUM32= 'tau ratio corrected for extinction'                                  
        #ROWNUM33= 'tau ratio pAGB'                                                      
        #ROWNUM34= 'tau ratio pAGB corrected for extinction'                             
        #ROWNUM35= 'Psi     '                                                            
        #ROWNUM36= 'Psi corrected for extinction'                                        
        #ROWNUM37= 'zeta    '                                                            
        #ROWNUM38= 'zeta corrected for extinction'     
        
        #MASSEVER= 'Mass ever formed -------------'                                      
        #LOGMEBST=            5.252E+00                                                  
        #LOGMEAVE=            5.252E+00                                                  
        #LOGMEDEV=            5.320E-08                                                  
        #MASSCORR= 'Mass presently available -----'                                      
        #LOGMCBST=            5.248E+00                                                  
        #LOGMCAVE=            5.248E+00                                                  
        #LOGMCDEV=            5.320E-08
        
        #self.mean_stellar_age_light = header['BST_LAGE']
        #self.mean_stellar_age_mass  = header['BST_MAGE']
        
        #self.mean_stellar_age_mass.set(Gyr, self.mean_stellar_age_light / 1.0e9)
        #self.mean_stellar_age_light.Gyr = self.mean_stellar_age_light / 1.0e9
        #self.mean_stellar_age_mass.Gyr  = self.mean_stellar_age_mass  / 1.0e9
        
        #self.mean_stellar_log_age_light = header['BSTLLAGE']
        #self.mean_stellar_log_age_mass  = header['BSTLMAGE']
        
        #self.mean_stellar_metallicity = header['BST_LMET']
        
        # Call object mass
        self.log_stellar_mass = mass( header['LOGMEBST'],header['LOGMCBST'] )
        
        # Call object mean_stellar
        self.mean_stellar_age         = mean_stellar( header['BST_LAGE'],header['BST_MAGE'], oneGyr=True )
        self.mean_stellar_log_age     = mean_stellar( header['BSTLLAGE'],header['BSTLMAGE'] )
        self.mean_stellar_metallicity = mean_stellar( header['BST_LMET'],header['BST_MMET'], solarmet=True )
        
        #print(self.mean_stellar_age.light,self.mean_stellar_age.mass,self.mean_stellar_metallicity.light,self.mean_stellar_metallicity.mass)
        
        #with fits_file as hdul:
        #    hdul.info()
    
        #for i in header.info():
        #    print(i)
    
        data = fits_file[0].data
        
        self.Naxis1_ST = fits_file[0].header['NAXIS1']
        self.Naxis2_ST = fits_file[0].header['NAXIS2']
        print("Naxis1: {} x Naxis2: {} pixels".format(self.Naxis1_ST,self.Naxis2_ST))
        
        self.CRVAL1_ST = header['CRVAL1']
        self.CRPIX1_ST = header['CRPIX1']
        self.CDELT1_ST = header['CDELT1']
                
        # Close fits file
        fits_file.close()
    
        # Delete
        del data
        ###--------------------------------------------------------------------------------------------------------------------------------
        
        # Reading FADO DE population vectors ##############################################################################################

        # Simpler Quick Parameters from FADO: Stellar Populations #########################################################################
        # Mean stellar age (light and mass-weighted)
        # Mean stellar metallicity (light and mass-weighted)
        # Stellar mass
        # Stellar extinction in the V-band
    def SimplerFADOStellarPopulations( self ):
        print( " ============================================================ " )
        print( "... Compact information regarding the stellar populations:")
        print("")
        print( "... Mean stellar age")
        print( "... Mean stellar age light-weighted                       : {:8.5g} [yr] or {:8.5f} [Gyr]".format(self.mean_stellar_age.light,self.mean_stellar_age.light_1Gyr) )
        print( "... Mean stellar age mass-weighted                        : {:8.5g} [yr] or {:8.5f} [Gyr]".format(self.mean_stellar_age.mass,self.mean_stellar_age.mass_1Gyr) )
        print( "... Mean stellar logarithmic age light-weighted           : {:7.5f}".format(self.mean_stellar_log_age.light) )
        print( "... Mean stellar logarithmic age mass-weighted            : {:7.5f}".format(self.mean_stellar_log_age.mass) )
        print( "... Mean stellar metallicity")
        print( "... Mean stellar metallicity light-weighted               : {:7.5f}        or {:8.5f} [Z_solar]".format(self.mean_stellar_metallicity.light,self.mean_stellar_metallicity.light_solar) )
        print( "... Mean stellar metallicity mass-weighted                : {:7.5f}        or {:8.5f} [Z_solar]".format(self.mean_stellar_metallicity.mass,self.mean_stellar_metallicity.mass_solar) )
        print("")
        print( "... Total stellar masses" )
        print( "... Log of total stellar mass presently available (corr.) : {:7.5f} [Solar masses]".format(self.log_stellar_mass.corrected) )
        print( "... Log of total stellar mass ever formed (not-corrected) : {:7.5f} [Solar masses]".format(self.log_stellar_mass.ever) )
        print("")
        print("... Extinction")
        print( "... Stellar extinction in the V-band                      : {:7.5f} +/- {:7.5g}".format(self.AV_extinction,self.AV_extinction_error) )
        print( "... Nebular extinction in the V-band                      : {:7.5f} +/- {:7.5g}".format(self.AV_extinction_nebular,self.AV_extinction_nebular_error) )
        print( "... Extinction-law used in FADO object.reddening_law      : {}".format(self.reddening_law) )
        print( " ============================================================ " )
        print("")
        # Simpler Quick Parameters from FADO: Stellar Populations #########################################################################
        
        # Simpler Quick Parameters from FADO: Kinematics of Stellar Populations ###########################################################
        # Systemic velocity
        # Velocity dispersion
        # Redshift
    def SimplerFADOKinematics( self ):
        print( " ============================================================ " )
        print( "... Compact information regarding the kinematics of stellar populations:")
        print("")
        print( "... Systemic velocity")
        print( "... Systemic velocity (non-relativistic correction)       : {:8.5f} [km/s]".format(self.redshift.velocity) )
        print( "... Systemic velocity (    relativistic correction)       : {:8.5f} [km/s]".format(self.redshift.relativistic_velocity) )
        print( "... Velocity dispersion                                   : {:8.5f} [km/s]".format(self.velocity_dispersion) )
        print( "... First redshift estimation                             : {:8.5e} ".format(self.redshift.firstvalue)    )
        print( "... Final redshift (correction due to the fitting)        : {:8.5e} ".format(self.redshift.value)    )
        print( " ============================================================ " )
        print("")
        # Simpler Quick Parameters from FADO: Kinematics of Stellar Populations ###########################################################
    
        # Simpler Quick Parameters from FADO: Fit parameters ##############################################################################
        # Systemic velocity
        # Velocity dispersion
        # Redshift
    def SimplerFADOFitParameters( self ):
        print( " ============================================================ " )
        print( "... Compact information regarding the fit parameters of FADO:")
        print("")
        print( "... Parameters for the fitting")
        print( "... Normalization wavelength used in the FADO fit         : {:8.5f} [Å]".format(self.lambda_0) )
        print( "... Flux density at the normalization wavelength          : {:8.5f}".format(self.galsnorm) )
        print( "... Flux density in units of                              : {:8.5e} [erg/s/cm²/Å]".format(self.fluxunit) )
        print( "... Fit was done from {} to {} Å with δλ = {}".format(self.olsynini,self.olsynfin,self.olsyndel) )
        print("")
        print( "... Number of base elements used in the fit               : {}".format(self.num_base) )
        print( "... Number of ages {} and number of metallicities {}".format(self.N_ages,self.N_metallicities) )
        for i in range(self.N_metallicities):
            print( "... Minimum age for metallicity {:8.5f} is {} [yrs]".format(self.met_stellar_pop[i*np.array(self.N_ages[i], dtype=int)],self.age_stellar_pop[0:np.array(self.N_ages[i], dtype=int)-1].min()) )
            print( "... Maximum age for metallicity {:8.5f} is {} [yrs]".format(self.met_stellar_pop[i*np.array(self.N_ages[i], dtype=int)],self.age_stellar_pop[0:np.array(self.N_ages[i], dtype=int)-1].max()) )
        print( "" )
        print( "... The base file used in FADO was: {}".format(self.arq_base) )
        print( "... The configuration file used in FADO was: {}".format(self.arq_conf) )
        print( " ============================================================ " )
        print("")
        # Simpler Quick Parameters from FADO: Fit parameters ##############################################################################
        


        # Main ############################################################################################################################
def main():
    #name = '0266.51630.100.7xt.FADO'
    #path = 'input'
    
    #path ='/run/media/jean/Isaac/FADOMCDS/bin/Release/'
    #name = 'test'
    
    #path ='input'
    #name ='0266.51602.089.23.7xt.FADO'
    r_object = ReadFADOFits( name, path=path, showheader=False )
    #p_object = PlotFADO( r_object, xmin=3000.0 , xmax=9300.0, ymin=-0.3, ymax=+1.6, ymin_residual=-0.1, ymax_residual=0.1 )
        
if __name__ == "__main__":
    main()
        # Main ############################################################################################################################

