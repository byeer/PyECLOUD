#----------------------------------------------------------------------
#                                                                      
#                           CERN                                       
#                                                                      
#     European Organization for Nuclear Research                       
#                                                                      
#     
#     This file is part of the code:
#                                                                      		            
#		           PyECLOUD Version 5.5.3                     
#                  
#                                                                       
#     Author and contact:   Giovanni IADAROLA 
#                           BE-ABP Group                               
#                           CERN                                       
#                           CH-1211 GENEVA 23                          
#                           SWITZERLAND  
#                           giovanni.iadarola@cern.ch                  
#                                                                      
#                contact:   Giovanni RUMOLO                            
#                           BE-ABP Group                               
#                           CERN                                      
#                           CH-1211 GENEVA 23                          
#                           SWITZERLAND  
#                           giovanni.rumolo@cern.ch                    
#                                                                      
#
#                                                                      
#     Copyright  CERN,  Geneva  2011  -  Copyright  and  any   other   
#     appropriate  legal  protection  of  this  computer program and   
#     associated documentation reserved  in  all  countries  of  the   
#     world.                                                           
#                                                                      
#     Organizations collaborating with CERN may receive this program   
#     and documentation freely and without charge.                     
#                                                                      
#     CERN undertakes no obligation  for  the  maintenance  of  this   
#     program,  nor responsibility for its correctness,  and accepts   
#     no liability whatsoever resulting from its use.                  
#                                                                      
#     Program  and documentation are provided solely for the use  of   
#     the organization to which they are distributed.                  
#                                                                      
#     This program  may  not  be  copied  or  otherwise  distributed   
#     without  permission. This message must be retained on this and   
#     any other authorized copies.                                     
#                                                                      
#     The material cannot be sold. CERN should be  given  credit  in   
#     all references.                                                  
#----------------------------------------------------------------------


from numpy.random import rand
from numpy.random import randn
from numpy import *


class residual_gas_ionization:
    
    def __init__(self, unif_frac, P_nTorr, sigma_ion_MBarn,Temp_K,chamb,E_init_ion):
        
        print 'Start res. gas ioniz. init.'
        self.unif_frac = unif_frac
        self.P_nTorr = P_nTorr
        self.sigma_ion_MBarn = sigma_ion_MBarn
        self.Temp_K = Temp_K
#         self.sigmax = sigmax
#         self.sigmay = sigmay
        self.chamb = chamb
        self.E_init_ion = E_init_ion
        
#         self.x_beam_pos = x_beam_pos
#         self.y_beam_pos = y_beam_pos
        
        print 'Done res. gas ioniz. init.'
    
    def generate(self,MP_e, lambda_t,Dt, sigmax,sigmay, x_beam_pos = 0., y_beam_pos = 0.):
                
                            
            c=299792458.;
            k_B=1.3806503e-23 ;
            me=9.10938291e-31;
            qe=1.602176565e-19;
            
            v0=-sqrt(2.*(self.E_init_ion/3.)*qe/me);
            
            P_Pa=self.P_nTorr*133.32e-9;
            sigma_ion_mq=self.sigma_ion_MBarn*1e-22;
            
            n_gas=P_Pa/(k_B*self.Temp_K);
            
            k_ion=n_gas*sigma_ion_mq*c;
            
            
            DNel=k_ion*lambda_t*Dt;
            
            N_new_MP=DNel/MP_e.nel_mp_ref;
            Nint_new_MP=floor(N_new_MP);
            rest=N_new_MP-Nint_new_MP;
            Nint_new_MP=Nint_new_MP+int(rand()<rest);
            
            if Nint_new_MP>0:
                unif_flag=(rand(Nint_new_MP)<self.unif_frac);
                gauss_flag=~(unif_flag);
                           
                x_temp=gauss_flag*(sigmax*randn(Nint_new_MP)+x_beam_pos)+self.chamb.x_aper*unif_flag*(2.*(rand(Nint_new_MP)-0.5));
                y_temp=gauss_flag*(sigmay*randn(Nint_new_MP)+y_beam_pos)+self.chamb.y_aper*unif_flag*(2.*(rand(Nint_new_MP)-0.5));
                
                flag_np=self.chamb.is_outside(x_temp,y_temp)#(((x_temp/x_aper)**2 + (y_temp/y_aper)**2)>=1);
                Nout=sum(flag_np);
                while(Nout>0):
                    unif_flag1=unif_flag[flag_np];
                    gauss_flag1=~(unif_flag1);
                    x_temp[flag_np]=gauss_flag1*(sigmax*randn(Nout)+x_beam_pos)+self.chamb.x_aper*unif_flag1*(2*(rand(Nout)-0.5));
                    y_temp[flag_np]=gauss_flag1*(sigmay*randn(Nout)+y_beam_pos)+self.chamb.y_aper*unif_flag1*(2*(rand(Nout)-0.5));
                    flag_np=self.chamb.is_outside(x_temp,y_temp)#(((x_temp/x_aper)**2 + (y_temp/y_aper)**2)>=1);
                    Nout=sum(flag_np);
            
                MP_e.x_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=x_temp;#Be careful to the indexing when translating to python
                MP_e.y_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=y_temp;
                MP_e.z_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=0.;#randn(Nint_new_MP,1);
                MP_e.vx_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=v0*(rand()-0.5);#if you note a towards down polarization look here
                MP_e.vy_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=v0*(rand()-0.5);
                MP_e.vz_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=v0*(rand()-0.5);
                MP_e.nel_mp[ MP_e.N_mp: MP_e.N_mp+Nint_new_MP]=MP_e.nel_mp_ref
               
                MP_e.N_mp=int(MP_e.N_mp+Nint_new_MP);
            
            return MP_e
    
