# coding: utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import copy
from time import time as clock
import os,sys,re

if sys.version[0]=='3' and int(re.split(r'\.|\~',sys.version)[1])<=6:
   import pickle5 as pickle
else:
   import pickle

# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# SUPY_RGPS.PY   - RANDOM GRID PATH SEARCH
# ------------------------------------------
# Version 14/05/2023, Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany
# EXPERIMENTAL SOFTWARE: NO WARRANTIES! REGULARLY BACKUP YOUR DATA!
# 
# original implemention from 14/05/2022 see ~/hs-albsig/02-research/DeepSemanticLearning/ADALOSS/pytorch/RandomGridPathSearch.py
# brief description of RandomGridPathSearch see the following publication (sect. 2.3):
#    A.Knoblauch: Adapting loss functions to learning progress improves accuracy of classification in neural networks.
#    In: M.Ceci, S.Flesca, E.Masciari, G.Manco, Z.W.Raś: Foundations of Intelligent Systems, Proceedings of ISMIS 2022,
#    Lecture Notes in Artificial Intelligence (LNAI), vol 13515, pp272-282, Springer, Cham, 2022
# for some theoretical background see AB4/p250
# for example application see: ~/hs-albsig/02-research/DeepSemanticLearning/ADALOSS/pytorch/powerError_DCNN_CIFAR10_PyTorch_adaptive_rgps_savebestmodel.py
#
# CONTENTS:
# -------------------------
# class Grid:                                 # class for grid noides (without any reference to parameters)
#    def __init__(self,gshape,ginc=1)
#    def setGridIncrement(self,ginc=1)
#    def get_gidx0(self)                      # get first (0th) grid index
#    def inc_gidx(self,gidx)
#    def addoffset_gidx(self,gidx,offset)
#    def get_gidx_neighbors(self,gidx,r=1)
#    def grid2flat(self,gidx)                 # convert grid index into flat index
#    def flat2grid(self,flat_idx)             # convert flat index into grid index
#
# class ParGrid:                              # class for definining Parameter Grids
#    def __init__(self,name)
#    def addParameter(self,par_label,par_range,par_initlimits=None)
#    def addStage(self,stagedef)              # dict_stagedef = {'parlabel_1':[ginc_1,r_1], 'parlabel_2':[ginc_2,r_2]}
#    def initParameterGrid(self)
#    def strParValue(self,gidx)               # return grid par string "x1=%val1, x2=%val2, ..." 
#    def outputState(self)
#
# class RandomGridPathSearch:                 # class defining a random grid path search 
#    def __init__(self,f,pargrid,Z=10,B=3,flagMidpoint=0,flagMax=1,exp_names=None)
#    def evaluateGridPoint(self,gidx_flat,args,datadict,f=None,fname_tmp=None,verbose=1)      # evaluate one grid point at (flat) grid index gidx_flat using function f with parameters args
#    def evaluateGridNeighbors(self,gidx_flat,args,datadict,f=None,fname_tmp=None,verbose=1)  # evaluate grid neighbors of central grid point at (flat) grid index gidx_flat using function f with parameters args
#    def save_data_tmp(self,datadict,fname_tmp,verbose=1)
#    def load_data_tmp(self,datadict,fname_tmp,verbose=1)
#    def get_reduced_indexes_within_initlimits(self,reduced_grid,ginc=1)
#    def searchOptimum(self,args,datadict,f=None,verbose=1,fname_tmp=None)
#
# def gpar_str(gpar)                          # extract grid parameter string from dict gpar={'x1':val1,'x2':val2,...}
# def outputRandomGridPathSearch(datadict,mode=0,indent=0):
#
# Module Test
#
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************


class Grid:                                   # class for grid noides (without any reference to parameters)
    def __init__(self,gshape,ginc=1):
        self.gshape=gshape                                                          # gshape
        self.gdim=len(gshape)                                                       # grid dimension 
        self.gsize=np.prod(self.gshape)                                             # total number of grid points
        self.gshape_cum=list(np.array([np.prod(self.gshape[0:i]) for i in range(self.gdim)],'int')) # cumulated grid shapes: gshape_cum[i] is size of grid[0,...,0] (i-1 times repeated)
        self.setGridIncrement(ginc)
        
    def setGridIncrement(self,ginc=1):
        if not isinstance(ginc,list): ginc=len(self.gshape)*[ginc]
        assert len(ginc)==len(self.gshape),"grid increment ginc="+str(ginc)+" must have same length as gshape="+str(self.gshape)+"!"
        self.ginc=ginc                                                              # set grid increments (per dimension)
        self.gshape_ginc=[self.gshape[i]//self.ginc[i] for i in range(self.gdim)]   # grid shape given grid increments
        self.gsize_ginc=np.prod(self.gshape_ginc)                                   # grid size given grid increments
   
    def outputState(self):
        print("Grid: gshape=",self.gshape,"gdim=",self.gdim,"gsize=",self.gsize,"gshape_cum=",
              self.gshape_cum,"ginc=",self.ginc,"gshape_ginc=",self.gshape_ginc,"gsize_ginc=",self.gsize_ginc)
        
    def get_gidx0(self):    # get first (0th) grid index
        return self.gdim*[0]

    def inc_gidx(self,gidx):
        for ip in range(self.gdim):
            gidx[ip]+=self.ginc[ip]
            if gidx[ip]<self.gshape[ip]: break
            gidx[ip]=0

    def addoffset_gidx(self,gidx,offset):
        res=copy.copy(gidx)
        for d in range(self.gdim):
            res[d]+=offset[d]*self.ginc[d]
            if res[d]<0 or res[d]>=self.gshape[d]: return None
        return res
            
    def get_gidx_neighbors(self,gidx,r=1):
        if not isinstance(r,list): r=self.gdim*[r] # render r as list
        assert isinstance(r, list) and len(r)==self.gdim,"r="+str(r)+" must be list of radii for each dimension of pargrid with length gdim="+str(self.gdim)+"!"
        r_npa=np.array(r,'int')                     # render r as numpy array
        list_neighbors=[]                           # initialize empty list of neighbors 
        gshape_offsets=[2*ri+1 for ri in r]         # grid shape of neighbor offsets (e.g., 3x3x... for r=1)
        grid_offsets=Grid(gshape_offsets)           # create grid object for neighbor window
        idx_offset=grid_offsets.get_gidx0()         # index of current offset
        for i in range(grid_offsets.gsize):         # iterate over offset grid points
            offset=np.array(idx_offset,'int')-r_npa # relative grid locations
            if np.sum(np.abs(offset))>0:            # exclude zero offset (that would be the index gidx, not a neighbor)
                neighbor = self.addoffset_gidx(gidx,offset)
                if not neighbor is None: list_neighbors+=[neighbor]   # add neighbor to list
            grid_offsets.inc_gidx(idx_offset)       # get next offset
        return list_neighbors                       # return list of neighbors

    def grid2flat(self,gidx):              # convert grid index into flat index
        return np.sum(np.multiply(gidx,self.gshape_cum))

    def flat2grid(self,flat_idx):              # convert flat index into grid index
        gidx=self.gdim*[0]
        for d in range(self.gdim-1,-1,-1):
            gidx[d]=flat_idx//self.gshape_cum[d]
            flat_idx-=gidx[d]*self.gshape_cum[d]
        return gidx

class ParGrid:                     # class for definining Parameter Grids
    def __init__(self,name):
        self.name=name             # name of parameter grid
        self.nPar=0                # number of parameters (or grid dimensions)
        self.nStage=0              # number of optimization stages
        self.par_labels=[]         # list of parameter labels
        self.par_ranges=[]         # list of parameter ranges (in order of labels)
        self.par_initlimits=[]     # list of parameter limits [[min_val,max_val],...] (in order of labels) used for initialization
        self.stage_defs=[]         # list of stagedefs (in order of labels)
        self.stage_gincs=[]        # grid increment lists for each stage 
        self.stage_rs=[]           # radius lists for each stage (for determining neighbors on grid; maximum norm)
        self.state=0               # 0=addParameters; 1=addStages; 2=readytouse
        
    def addParameter(self,par_label,par_range,par_initlimits=None):
        assert self.state==0,"state="+str(self.state)+", but you can add new parameters only in state 0 (before calling addStage() or initParameterGrid()!"
        self.par_labels+=[par_label]
        self.par_ranges+=[par_range]
        self.par_initlimits+=[par_initlimits]
        self.nPar+=1
        
    def addStage(self,stagedef):              # dict_stagedef = {'parlabel_1':[ginc_1,r_1], 'parlabel_2':[ginc_2,r_2]}
        assert self.state<=1,"state="+str(self.state)+", but you can add new stage only in state 0 or 1 (before calling initParameterGrid()!"
        for k in stagedef.keys(): assert k in self.par_labels, "parameter k="+str(k)+" to be staged has not been added to ParGrid object!"
        self.state=1
        self.stage_defs+=[stagedef]
        self.nStage+=1

    def initParameterGrid(self):
        assert self.nPar>=1 and self.nStage>=0,"nPar="+str(self.nPar)+" must be >0, and nStage="+str(self.nStage)+" must be >=0!"
        assert self.nPar==len(self.par_labels) and self.nPar==len(self.par_ranges),"nPar="+str(self.nPar)+" must have same length as par_labels and par_ranges!"
        self.state=2
        if self.nStage<=0: self.nStage=1
        self.stage_gincs=np.ones((self.nStage,self.nPar),'int').tolist()   # set grid increments to default value 1 for all stages and all parameters
        self.stage_rs   =np.ones((self.nStage,self.nPar),'int').tolist()   # set grid radii to default value 1 for all stages and all parameters
        for i in range(len(self.stage_defs)):
            sd=self.stage_defs[i]
            for j in range(self.nPar):
                if self.par_labels[j] in sd.keys(): sdj=sd[self.par_labels[j]]   # read stage information for parameter j
                else: sdj=[1,1]                                                  # if not available then use defaults ginc=1, r=1
                assert isinstance(sdj,(list,tuple)) and len(sdj)==2,"stage i="+str(i)+": stage definition for par_label="+str(par_labels[j])+" must have format [ginc,r]!"
                self.stage_gincs[i][j]=sdj[0]      # set grid increment for stage i, parameter j
                self.stage_rs   [i][j]=sdj[1]      # set radius for stage i, parameter j

    def strParValue(self,gidx):    # return grid par string "x1=%val1, x2=%val2, ..." 
        assert self.nPar==len(gidx),"Grid index gidx="+str(gidx)+" must have same length as nPar="+str(nPar) 
        gpar={self.par_labels[i]:self.par_ranges[i][gidx[i]] for i in range(self.nPar)}
        return gpar_str(gpar)
                
    def outputState(self):
        print("Parameter Grid: ",self.name)
        print("nPar=",self.nPar,"nStage=",self.nStage,"state=",self.state)
        print("par_labels=",self.par_labels)
        print("par_ranges=",self.par_ranges)
        #print("par_initlimits=",self.par_initlimits)
        print("self.stagedefs=",self.stage_defs)
        print("self.stage_gincs=",self.stage_gincs)
        print("self.stage_rs   =",self.stage_rs)
    
class RandomGridPathSearch:
    def __init__(self,f,pargrid,Z=10,B=3,flagMidpoint=0,flagMax=1,exp_names=None):
        """
        :param f      : function to be evaluated; dict_exp=f(args); f takes arguments args (dict) and returns a dict of the experimental results; dict_exp['value'] is function value
        :param pargrid: parameter grid of class ParGrid 
        :param Z      : number of initial random grid points to be evaluated
        :param B      : number of best grid points from the Z random points to be optimized by a local path search
        :param flagMidpoint: if >0 then additionally start also from the midpoint of the grid
        :param flagMax: if >0 then optimize by maximizing (else by minimizing)
        :param exp_names: list of experiment names (if None then default experiment names are 'exp<i>' (under this name data of experiments are stored in dict)
        """
        # (i) save basic parameters
        self.f=f                                  # function to optimize
        self.pargrid=pargrid                      # parameter grid (list of ['label',val_list,gincs,rs])
        self.Z=Z                                  # number of random grid points that are evaluated to get initial grid points 
        self.B=B                                  # number of best random grid points selected to be initial points
        self.flagMidpoint=flagMidpoint            # if set then include the grid midpoint to set of B best points
        self.flagMax=flagMax                      # if set then maximize function f (else minimize f)
        self.exp_names=exp_names                  # list of experiment names        
        # (ii) extract additional information
        if self.pargrid.state<2: self.pargrid.initParameterGrid()
        self.pargrid.outputState()
        self.par_labels=self.pargrid.par_labels   # parameter labels
        self.par_values=self.pargrid.par_ranges   # for each parameter label the corresponding list of values (assumed to be ordered!!)
        self.par_initlimits=self.pargrid.par_initlimits # for each parameter initialization limits [...,[min_i,max_i],...]
        self.gdim=self.pargrid.nPar               # grid dimension (number of parameters to be manipulated)
        self.gshape=[len(pv) for pv in self.par_values]          # grid shape
        self.grid=Grid(self.gshape,self.pargrid.stage_gincs[0])  # grid object (and set grid increments of first optimization stage)
        self.gsize=self.grid.gsize                # grid size
        if self.exp_names is None:
            self.exp_names=['exp'+str(i) for i in range(self.gsize)]  # default experiment names are 'exp<i>' (under this name data of experiments are stored in dict)
        self.list_experiments=[]                  # list of all experiments that have actually been evaluated! (whereas exp_names is list of all potential experiments for each grid point)
        self.idxZ=None                            # random indexes for random search
        self.t_total_old=float(0)                 # time (in sec) spent sofar (for loaded data)
        self.stage=0                              # init with first optimization stage
        # (iii) do assertions
        assert self.Z>=0 and self.Z<=self.grid.gsize_ginc,"Number Z="+str(self.Z)+" of random grid points must be between 0 and gsize_ginc="+str(self.grid.gsize_ginc)+"!"
        assert B>=0 and B<=self.Z,"Number B="+str(self.B)+" of best random grid points must be between 0 and Z="+str(self.Z)+"!"
        assert B>0 or flagMidpoint>0,"Either B="+str(self.B)+" or flagMidpoint="+str(self.flagMidpoint)+" must be larger than 0 (otherwise noting to do)!"
        assert isinstance(self.exp_names, list) and len(self.exp_names)==self.gsize,"exp_names must be list of length gsize="+str(self.gsize)+"!"

    def evaluateGridPoint(self,gidx_flat,args,datadict,f=None,fname_tmp=None,verbose=1):  # evaluate one grid point at (flat) grid index gidx_flat using function f with parameters args
        """
        :param gidx    : grid index at which function f should be evaluated
        :param args    : dict of function parameters; grid parameters will be set in this dict before calling f
        :param datadict: main data dictionary where dict_exp of current experiment will be stored under key obtained from self.exp_names (using flat index of gidx)
        :param f       : function to be evaluated; dict_exp=f(args); f takes arguments args and returns a dict of the experimental results; dict_exp['value'] is function value 
        """
        if f is None: f= self.f                        # take default function f?
        gidx=self.grid.flat2grid(gidx_flat)            # get grid index of flat grid index
        name_exp=self.exp_names[gidx_flat]             # experiment name corresponding to grid point
        if not name_exp in datadict.keys(): datadict[name_exp]=None  # insert dummy result entry
        if datadict[name_exp] is None:                 # grid point not yet evaluated?
            # (i) set grid parameters
            print("\nExperiment",len(self.list_experiments)+1,"/",self.gsize,"in grid",self.gshape)
            print("    gidx_flat=",gidx_flat,"gidx=",gidx,":")
            str_descr="stage="+str(self.stage+1)+"/"+str(self.pargrid.nStage)+"; experiment "+str(len(self.list_experiments)+1)+"/"+str(self.gsize)
            gpar_dict={}
            for ip in range(self.gdim):                # set current grid parameters
                args[self.par_labels[ip]]=self.par_values[ip][gidx[ip]]
                gpar_dict[self.par_labels[ip]]=self.par_values[ip][gidx[ip]]
                print("   ",self.par_labels[ip],"=",self.par_values[ip][gidx[ip]])
                str_descr=str_descr+";   "+str(self.par_labels[ip])+"="+str(self.par_values[ip][gidx[ip]])
            # (ii) do experiment by evaluating function f
            t1_exp=clock()   # measure time for experiment 
            dict_exp=f(args,str_descr) # do experiment 
            t2_exp=clock()   # measure time for experiment 
            # (iii) save meta information
            dict_exp['name_exp']=name_exp                        # save name of experiment
            dict_exp['args']=copy.deepcopy(args)                 # save (deep copy of) arguments (experimental parameters)
            dict_exp['t_exp']=float(t2_exp-t1_exp)               # save time required for experiment
            dict_exp['gpar']=gpar_dict                           # save grid parameter values
            dict_exp['gidx']=copy.copy(gidx)                     # save (copy of) grid index
            dict_exp['gidx_flat']=gidx_flat                      # save flat grid index
            # (iv) save data in main data dict
            datadict[name_exp]=dict_exp                          # save experimental data in main data dict
            self.list_experiments+=[name_exp]                    # append experiment name to list of actually evaluated grid points
            self.save_data_tmp(datadict,fname_tmp,verbose)       # save data
        value=datadict[name_exp]['value']                        # get value of this experiment
        return value
    
    def evaluateGridNeighbors(self,gidx_flat,args,datadict,f=None,fname_tmp=None,verbose=1):  # evaluate grid neighbors of central grid point at (flat) grid index gidx_flat using function f with parameters args
        """
        :param gidx    : grid index at which function f should be evaluated
        :param args    : dict of function parameters; grid parameters will be set in this dict before calling f
        :param datadict: main data dictionary where dict_exp of current experiment will be stored under key obtained from self.exp_names (using flat index of gidx)
        :param f       : function to be evaluated; dict_exp=f(args); f takes arguments args and returns a dict of the experimental results; dict_exp['value'] is function value 
        """
        if f is None: f=self.f               # get defaults?
        r=self.pargrid.stage_rs[self.stage]  # get radii for current stage (defining neighborhodd on current grid position)
        gidx              =self.grid.flat2grid(gidx_flat)                                         # get grid index of flat grid index of central point
        idx_neighbors_grid=self.grid.get_gidx_neighbors(gidx,r)                                   # get list of neighbors (in terms of grid indexes)
        idx_neighbors     =[self.grid.grid2flat(i) for i in idx_neighbors_grid]                   # list of flat indexes of the neighboring points
        val_neighbors     =[self.evaluateGridPoint(i,args,datadict,f,fname_tmp,verbose) for i in idx_neighbors] # evaluate neighbor points and store values in list
        if len(val_neighbors)>0:
            i_best_nb         =np.argmax(val_neighbors) if self.flagMax else np.argmin(val_neighbors) # index of the best neighbors
            idx_best_nb       =idx_neighbors[i_best_nb]                                               # flat grid index of the best neighbor 
            val_best_nb       =val_neighbors[i_best_nb]                                               # value of the best neighbor
        else:
            idx_best_nb,val_best_nb=None,None                                                         # no neighbors?
        return idx_best_nb,val_best_nb                                                            # return index and value of best neighbor

    def save_data_tmp(self,datadict,fname_tmp,verbose=1):
        if not fname_tmp is None and not fname_tmp=="":
            if verbose>0: print("Saving datadict to temporary data file fname_tmp=",fname_tmp)
            fname_tmp_tmp=fname_tmp+'.tmp'                                      # first save into *tmp.tmp file (in order not to destroy a previous tmp file)
            datadict['list_experiments']=self.list_experiments                  # save actual experiments (to be able to reconstruct experiments already performed)
            datadict['idxZ']=self.idxZ                                          # save random indexes for initial random search (to be reconstructed after loading)
            datadict['t_total_old']=float(self.t_total_old+clock()-self.t1_total)
            with open(fname_tmp_tmp, 'wb') as f:
                pickle.dump(datadict, f, protocol=pickle.HIGHEST_PROTOCOL)
            os.rename(fname_tmp_tmp,fname_tmp)                                  # only rename to desired temporary filename if data has been correctly stored 

    def load_data_tmp(self,datadict,fname_tmp,verbose=1):
        if not fname_tmp is None and not fname_tmp=="" and os.path.isfile(fname_tmp):
            assert len(self.list_experiments)==0,"self.list_experiments="+str(self.list_experiments)+" should be empty list! Otherwise previous experiments would be lost!"
            if verbose>0: print("Loading temporary data file fname_tmp=",fname_tmp)
            with open(fname_tmp, 'rb') as handle: datadict1 = pickle.load(handle)
            datadict.update(datadict1)
            self.list_experiments=datadict['list_experiments']
            self.idxZ=datadict['idxZ']
            self.t_total_old=datadict['t_total_old']
            if verbose>0:
                print("   sofar completed",len(self.list_experiments),"experiments: ",self.list_experiments)
                print("   for idxZ=",self.idxZ)
                print("   in time t_total_old=",self.t_total_old)
        else:
            if verbose>0: print("No temporary data file loaded: fname_tmp=",fname_tmp)
            self.list_experiments=[]
            self.idxZ=None

    def get_reduced_indexes_within_initlimits(self,reduced_grid,ginc=1):
        """
        :param reduced grid: reduced grid (with increment ginc) 
        :param ginc        : increment of reduced grid (assumed for indexes in flat_indexes)
        :returns fidx_valid    : list of valid flat indexes (w.r.t. reduced shape)
        :returns fidx_mid_valid: flat index of valid midpoint (w.r.t. reduced shape)
        """
        #print("get_reduced_indexes_within_initlimits:")
        #print("---------------------------------------")
        rg_shape=reduced_grid.gshape   # shape of the reduced grid
        if not isinstance(ginc,list): ginc=len(rg_shape)*[ginc]
        assert len(rg_shape)==len(self.gshape),"parameter grid "+self.name+": rediced_grid.shape="+str(reduced_grid.shape)+" must be equal to gshape="+str(self.gshape)
        #print("rg_shape=",rg_shape,"ginc=",ginc)
        valid_idx_rg=[]                # for each dimension list of valid (reduced) parameter indexes
        for ip in range(len(rg_shape)):
            assert self.par_initlimits[ip] is None or len(self.par_initlimits[ip])==2,\
                "parameter grid "+self.name+": self.par_initlimits["+str(ip)+"]="+str(self.par_initlimits[ip])+" should be list [min,max] for par_label="+str(self.par_labels[ip])
            assert rg_shape[ip]>0 and (rg_shape[ip]-1)*ginc[ip] < self.gshape[ip] 
            valid_idx_rg.append([ j for j in range(rg_shape[ip]) if self.par_initlimits[ip]==None or (self.par_values[ip][j*ginc[ip]]>=self.par_initlimits[ip][0] and self.par_values[ip][j*ginc[ip]]<=self.par_initlimits[ip][1]) ])
        gshape_valid=[len(v) for v in valid_idx_rg]                 # shape of the "valid" reduced_grid
        assert np.prod(gshape_valid)>0,"reduced valid grid has zero elements! valid_idx_rg="+str(valid_idx_rg)+" for RandomGridPathSearch with pargrid.name="+str(self.pargrid.name)+"!"
        #print("valid_idx_rg=",valid_idx_rg)
        offset_valid=np.array([v[0] for v in valid_idx_rg],'int')   # minimum/first valid index (=offset) for each parameter dimension
        gvalid=Grid(gshape_valid)                                   # valid reduced grid
        print("gvalid.gshape=",gvalid.gshape)
        gidx_valid = [np.array(gvalid.flat2grid(i),'int')+offset_valid for i in range(gvalid.gsize)]   # valid grid indexes (w.r.t. reduced shape)
        fidx_valid = [reduced_grid.grid2flat(gi) for gi in gidx_valid]                                 # valid flat indexes (w.r.t. reduced shape)
        # (ii) compute midpoint of valid grid
        gidx_mid_valid=[gvalid.gshape[i]//2+offset_valid[i] for i in range(self.gdim)]  # grid index of mid point (w.r.t. reduced shape)
        fidx_mid_valid=reduced_grid.grid2flat(gidx_mid_valid)                           # flat index of mid point (w.r.t. reduced shape)
        return fidx_valid, fidx_mid_valid
            
    def searchOptimum(self,args,datadict,f=None,verbose=1,fname_tmp=None):
        self.t1_total=clock()                                                          # measure time of optimization procedure
        if verbose>0:
            print("\nDoing RandomGridPathSearch with Z=",self.Z,"B=",self.B,"flagMidpoint=",self.flagMidpoint," with parameter grid:")
            self.pargrid.outputState()
            print("Temporary Results will be loaded/stored from/to file:",fname_tmp)
        self.load_data_tmp(datadict,fname_tmp,verbose)                                 # load previously stored temporary file?
        # (i) do initial random search and select B best grid points
        ginc_stage0=self.grid.ginc                                                     # grid increments for stage 0 (as initialized in self.grid)
        grid_stage0=Grid(self.grid.gshape_ginc)                                        # generate reduced parameter grid with ginc for stage 0 
        ridx,ridx_mid=self.get_reduced_indexes_within_initlimits(grid_stage0,ginc_stage0) # get (flat) indexes for all (reduced) grid points that are within initlimits (and midpoint) 
        a     =np.random.permutation(len(ridx))                                        # permutate reduced grid points for selecting random grid points
        if self.idxZ is None:
            assert len(a)>=self.Z,"reduced grid of stage0 has only len(a)="+str(len(a))+" elements, but at least Z="+str(self.Z)+" needed!"
            self.idxZ=np.array(ridx,'int')[a[0:self.Z]]                                # array of flat indexes for Z randomly selected grid points for initial random search
            self.idxZ=[np.array(grid_stage0.flat2grid(i)) for i in self.idxZ]          # convert to (reduced) grid indexes (to be convertible to full grid)
            self.idxZ=[np.multiply(ig,ginc_stage0) for ig in self.idxZ]                # convert to full grid indexes by multiplying with grid increments (of stage 0)
            self.idxZ=np.array([self.grid.grid2flat(ig) for ig in self.idxZ ],'int')   # convert to flat indexes
        valsZ =[] 
        for i in range(self.Z):                
            v=self.evaluateGridPoint(self.idxZ[i],args,datadict,f,fname_tmp,verbose)   # evaluate random grid points
            valsZ+=[v]                                                                 # store values in list
        fac    =-1.0 if self.flagMax>0 else 1.0                                        # factor to consider maximizing versus minimizing  
        idxB   =self.idxZ[np.argsort(fac*np.array(valsZ,'float'))[:self.B]]            # array of flat indexes of the B best of Z random grid points
        # (ii) add grid midpoint?
        ridx_mid_grid=grid_stage0.flat2grid(ridx_mid)                                  # convert to grid index
        idx_mid=[ridx_mid_grid[i]*ginc_stage0[i] for i in range(self.gdim)]            # grid index of mid point (lies on reduced valid grid of stage 0)
        idx_mid_flat=self.grid.grid2flat(idx_mid)                                      # flat index of mid point
        if not idx_mid_flat in list(idxB):                                             # if midpoint is not yet in list of best...
            idxB=np.append(idxB,idx_mid_flat)                                          # ...then append midpoint to list of best
        # (iii) do local path search for each initial grid point in idxB
        if verbose>0:
            print("Testing best",len(idxB),"paths in idxB=",idxB,"at initial grid positions",[self.grid.flat2grid(i) for i in idxB],"in grid",self.gshape)
        search_paths=[]                                                                # init list of search paths (one search path for each initial grid point in idxB)
        for i in range(len(idxB)):                                                     # loop over all initial points
            idx_best=idxB[i]                                                           # (flat) index of currently best grid point
            val_best=self.evaluateGridPoint(idx_best,args,datadict,f,fname_tmp,verbose)# value of currently best grid point
            search_path=[[idx_best,self.grid.flat2grid(idx_best),val_best,0]]          # initialize search path with initial grid point; last component is stage
            for st in range(self.pargrid.nStage):                                      # loop over all stages
                if verbose>0:
                    print("\nTesting Path",i+1,"/",len(idxB)," in stage",st+1,"/",self.pargrid.nStage)
                self.stage=st                                                          # set current stage
                self.grid.setGridIncrement(self.pargrid.stage_gincs[st])               # set grid increments for stage
                while True:
                    print("\nTesting neighbors of idx_best=",idx_best,"gidx=",self.grid.flat2grid(idx_best))
                    idx_best_nb,val_best_nb=self.evaluateGridNeighbors(idx_best,args,datadict,f,fname_tmp,verbose)
                    flagImprovement = not idx_best_nb is None and ((self.flagMax>0 and val_best_nb>val_best) or (self.flagMax<=0 and val_best_nb<val_best))  # is best neighbor improvement over current optimum?
                    if flagImprovement:                                                     # improvement?
                        idx_best,val_best=idx_best_nb,val_best_nb                           # if yes, then take over new optimal index and value
                        search_path+=[[idx_best,self.grid.flat2grid(idx_best),val_best,st]] # save new optimum in search path
                        print("\nImproved to val=",val_best,"at idx_best=",idx_best,"gidx=",self.grid.flat2grid(idx_best))
                    else:
                        break                                                               # if no improvement then local search ends
            search_paths+=[search_path]                                                 # append search path to list
            if verbose>0:
                print("... Resulting Search Path:",search_path,"with best value=",search_path[-1][2])
        # (iv) select best search path
        best_idxs  = [p[-1][0] for p in search_paths]                                  # list of flat winner indexes for each search path
        best_gidxs = [p[-1][1] for p in search_paths]                                  # list of grid winner indexes for each search path
        best_vals  = [p[-1][2] for p in search_paths]                                  # list of winner values for each search path
        i = np.argsort(fac*np.array(best_vals))[0]                                     # find array index of best grid point
        best_idx  = best_idxs[i]                                                       # flat grid index of best grid point
        best_gidx = best_gidxs[i]                                                      # grid index of best grid point
        best_val  = best_vals[i]                                                       # corresponding optimal value
        conf = len(list(set(best_idxs)))                                               # confidence measure = number of different local optima
        # (v) store results of random grid path search in datadict
        dict_rgps={}
        dict_rgps['best_idx']=best_idx                # best grid point index (flat)
        dict_rgps['best_gidx']=best_gidx              # best grid point index
        dict_rgps['best_val']=best_val                # optimal value
        dict_rgps['conf']=conf                        # confidence measure: number of different local optima
        dict_rgps['search_paths']=search_paths        # search paths
        dict_rgps['best_idxs']=best_idxs
        dict_rgps['best_gidxs']=best_gidxs
        dict_rgps['best_vals']=best_vals
        dict_rgps['exp_names']=self.exp_names         # list of experiment names (for all grid points; in order of flat indexes)
        dict_rgps['list_experiments']=self.list_experiments # save actual experiments
        dict_rgps['idxZ']=self.idxZ
        dict_rgps['idxB']=idxB
        dict_rgps['pargrid']=copy.deepcopy(self.pargrid)
        dict_rgps['Z']=self.Z
        dict_rgps['B']=self.B
        dict_rgps['flagMidpoint']=self.flagMidpoint
        dict_rgps['flagMax']=self.flagMax
        dict_rgps['evalGridFactor']=float(len(self.list_experiments))/float(self.gsize)   # fraction of evaluated grid points
        dict_rgps['par_labels']=self.par_labels
        dict_rgps['par_values']=self.par_values
        dict_rgps['par_initlimits']=self.par_initlimits
        dict_rgps['stage_gincs']=self.pargrid.stage_gincs
        dict_rgps['stage_rs']=self.pargrid.stage_rs
        dict_rgps['gdim']=self.gdim
        dict_rgps['gshape']=self.gshape
        dict_rgps['gsize']=self.gsize
        t2_total=clock()                                   # measure total time
        dict_rgps['t_total']=float(self.t_total_old+t2_total-self.t1_total) # total time for optimization procedure
        datadict['RandomGridPathSearch']=dict_rgps         # save dict_rgps in main data dict
        datadict['list_experiments']=self.list_experiments   # save actual experiments
        datadict['nExperiments']=len(self.list_experiments)  # number of actual experiments
        datadict['gshape']=self.gshape                # redundant (for compatibility)
        datadict['gdim']=self.gdim                    # redundant (for compatibility)
        datadict['pargrid']=dict_rgps['pargrid']      # redundant (for compatibility)
        if verbose>0:
            print("\nBest result of random grid path search: best_idx=",best_idx,"best_gidx=",best_gidx,"/",self.gshape,"best_val=",best_val,"conf=",conf,"/",len(search_paths))
            print("Best parameters: ")
            for ip in range(self.gdim):                # set current grid parameters
                print("   ",self.par_labels[ip],"=",self.par_values[ip][best_gidx[ip]],"from",self.par_values[ip])
            print("Evaluated nExperiments=",datadict['nExperiments'],"/",self.gsize,"gridpoints in t_total=",dict_rgps['t_total'])
            print("Average time/experiment=",dict_rgps['t_total']/datadict['nExperiments'])

def gpar_str(gpar):          # extract grid parameter string from dict gpar={'x1':val1,'x2':val2,...}
    s=""
    p=list(gpar.keys())      # list of parameters
    for i in range(len(p)):  # extract parameter values
        if i>0: s=s+", "
        s=s+str(p[i])+"="+str(gpar[p[i]])
    return s
            
def outputRandomGridPathSearch(datadict,mode=0,indent=0):
    """
    pretty print results of random grid path search
    :param dixt_rgps: data obtained from datadict['RandomGridPathSearch']
    :param mode     : 0=just print raw dict
                      1=pretty print
    :param indent   : number of leading spaces per printed line
    """
    dict_rgps=datadict['RandomGridPathSearch']
    grid=Grid(dict_rgps['gshape'])
    ind=""
    if indent>0: ind=indent*" ";
    if mode<=0:
        print(dict_rgps)
    if mode>=1:
        print(ind+"\nQuick Summary:")
        print(ind+"Best result of random grid path search with Z=",dict_rgps['Z'],", B=",dict_rgps['B'],", flagMidpoint=",dict_rgps['flagMidpoint'],":")
        print(ind+ind+"best_idx=",dict_rgps['best_idx'],", best_gidx=",dict_rgps['best_gidx'],"/",dict_rgps['gshape'],", best_val=",dict_rgps['best_val'],", conf=",dict_rgps['conf'],"/",len(dict_rgps['search_paths']))
        print(ind+"Best parameters: ")
        idx_searchpath_winners=[dict_rgps['search_paths'][ip][-1][0] for ip in range(len(dict_rgps['search_paths']))]   # for each search path the index of the winning (last) experiment
        gidx_searchpath_winners=[grid.flat2grid(idx) for idx in idx_searchpath_winners]                                 # corresponding grid indexes
        for ip in range(dict_rgps['gdim']):          # set current grid parameters
            pval_list=[dict_rgps['par_values'][ip][gi[ip]] for gi in gidx_searchpath_winners]                           # parameter values of the search path winners
            pval_best=dict_rgps['par_values'][ip][dict_rgps['best_gidx'][ip]]                                           # parameter value of the best search path
            nbest=pval_list.count(pval_best)
            print(ind+ind,dict_rgps['par_labels'][ip],"=",pval_best,"   (",nbest,"/",len(pval_list),";",min(pval_list),"-",max(pval_list),")    from",dict_rgps['par_values'][ip])
        print(ind+"Evaluated nExperiments=",len(dict_rgps['list_experiments']),"/",dict_rgps['gsize'],"gridpoints in t_total=",dict_rgps['t_total'])
        print(ind+"Average time/experiment=",dict_rgps['t_total']/len(dict_rgps['list_experiments']))
    if mode>=3:
        print(ind+"\nInitial Random Search:")
        print(ind+"Random Evaluations: Z=",dict_rgps['Z'],", idxZ=",dict_rgps['idxZ'],", flagMidpoint=",dict_rgps['flagMidpoint'],", flagMax=",dict_rgps['flagMax'])
        for iz in dict_rgps['idxZ']:
            gidx    =grid.flat2grid(iz)          # grid index
            name_exp=dict_rgps['exp_names'][iz]  # name of experiment
            data_exp=datadict[name_exp]          # experimental data
            print(ind+ind+name_exp+" at gidx=",gidx,": Value=",data_exp['value'],"for ",gpar_str(data_exp['gpar']))
        s='with'
        if dict_rgps['flagMidpoint']<=0: s='without'
        print(ind+"Best B=",dict_rgps['B'],s,"midpoint: idxB=",dict_rgps['idxB'])
        for ib in dict_rgps['idxB']:
            gidx    =grid.flat2grid(ib)          # grid index
            name_exp=dict_rgps['exp_names'][ib]  # name of experiment
            data_exp=datadict[name_exp]          # experimental data
            print(ind+ind+name_exp+" at gidx=",gidx,": Value=",data_exp['value'],"for ",gpar_str(data_exp['gpar'])) 
    if mode>=2:
        assert len(dict_rgps['search_paths'])==len(dict_rgps['idxB']),"Length of list search_paths should be identical to length of list idxB!"    # comment this out if idxB is not available 
        for ip in range(len(dict_rgps['search_paths'])):
            pth=dict_rgps['search_paths'][ip]
            print(ind+"GridPathSearch",ip,"for", dict_rgps['exp_names'][dict_rgps['idxB'][ip]],"in",len(pth),"steps :")                            # comment this out if idxB is not available 
            print(ind+ind+str(dict_rgps['search_paths'][ip]))
            for i in range(len(pth)):                # loop over path
                idx=pth[i][0]                        # flat index
                if len(pth[i])>3: stage=pth[i][3]    # stage number
                else: stage=0                        # default (for old data format)
                gidx    =grid.flat2grid(idx)         # grid index
                name_exp=dict_rgps['exp_names'][idx] # name of experiment
                data_exp=datadict[name_exp]          # experimental data
                print(ind+ind+ind+name_exp+" at gidx=",gidx,": Value=",data_exp['value'],"for ",gpar_str(data_exp['gpar']),"in stage ",stage) 
                
            
if __name__ == '__main__':
    print("RandomGridPathSearch.py -- Unit Test")
    print("-------------------------------------")
    print("-------------------------------------")
    print("(for algorithm design/analysis see AB4/p250/251)")
    
    #rgps = RandomGridPathSearch()
    print("\n(i) Test class Grid:")
    print("--------------------")
    gshape=[3,5,4]
    print("gshape=",gshape)
    grid=Grid(gshape)
    grid.outputState()
    gidx=grid.get_gidx0()
    print("gsize=",grid.gsize)
    for i in range(grid.gsize):
        i_gidx=grid.flat2grid(i)
        i_flat=grid.grid2flat(i_gidx)
        print("i=",i,"gidx=",gidx,"i_gidx=",i_gidx,"i_flat=",i_flat)
        grid.inc_gidx(gidx)
    grid=Grid([3,3])
    grid.outputState()
    print("Neighbors of [0,0]",grid.get_gidx_neighbors([0,0],r=1))
    print("Neighbors of [0,1]",grid.get_gidx_neighbors([0,1],r=1))
    print("Neighbors of [0,2]",grid.get_gidx_neighbors([0,2],r=1))
    print("Neighbors of [1,0]",grid.get_gidx_neighbors([1,0],r=1))
    print("Neighbors of [2,0]",grid.get_gidx_neighbors([2,0],r=1))
    print("Neighbors of [1,1]",grid.get_gidx_neighbors([1,1],r=1))
    gshape=[3,5,4]
    print("gshape=",gshape)
    grid=Grid(gshape)
    r=[0,2,1]
    print("Neighbors of [1,2,3] for r=",r,":",grid.get_gidx_neighbors([1,2,3],r=r))
    #exit(0)
    
    print("\n(ii) Test class RandomGridPathSearch:")
    print("----------------------------------------")
    print("----------------------------------------")
    print("\n(ii.1) Define RandomGridPathSearch:")
    print("----------------------------------------")
    def f(args):
        x1=args['x1']
        x2=args['x2']
        x3=args['x3']
        dict_exp={}
        #dict_exp['value']=5*x1+2*x2+3*x3-x1*x2*x3
        dict_exp['value']=x1+x2+x3 
        return dict_exp
    pargrid = ParGrid("dummygrid")
    pargrid.addParameter('x1',[0.01,0.1,0.5,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0],par_initlimits=[0.5,7])
    pargrid.addParameter('x2',[-5.0,-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0,5.0],par_initlimits=[-1.0,0])
    pargrid.addParameter('x3',[0.0, 1.0, 2.0, 3.0],par_initlimits=[2,10])
    pargrid.addStage({'x1':[4,1],'x2':[3,1],'x3':[2,1]})
    #pargrid.addStage({'x1':[4,3],'x2':[3,2],'x3':[2,1]})
    pargrid.addStage({})
    args={}
    args['x1']=-1000
    args['x2']=-1000
    args['x3']=-1000
    data_dict={}
    rgps = RandomGridPathSearch(f,pargrid,Z=10,B=3,flagMidpoint=0,flagMax=1)
    print("\n(ii.2) Test get_reduced_indexes_within_initlimits(.)")
    print("--------------------------------------------------------")
    test_stage=0;                                          # define stage
    ginc_s=pargrid.stage_gincs[test_stage]                 # ginc of certain stage
    grid_s=Grid(rgps.grid.gshape,ginc_s)                   # grid using that ginc of certain stage 
    rgrid=Grid(grid_s.gshape_ginc)                         # reduced grid for that stage
    print("rgrid.gshape=",rgrid.gshape)
    ri,rm=rgps.get_reduced_indexes_within_initlimits(rgrid,ginc_s) # test get_reduced_indexes_within_initlimits(.)
    print("ri=",ri,"rm=",rm)
    for i in ri:
        gidx_rg=rgrid.flat2grid(i)      # valid grid indexes (w.r.t. reduced grid)
        gidx=[gidx_rg[i]*ginc_s[i] for i in range(len(gidx_rg))]   # valid grid indexes (w.r.t. original grid)
        print("ri_flat=",i,"gidx_rg=",gidx_rg,"gidx=",gidx,"pars=",pargrid.strParValue(gidx))
    mid_gidx_rg=rgrid.flat2grid(rm)     # mid point w.r.t. reduced grid
    mid_gidx   =[mid_gidx_rg[i]*ginc_s[i] for i in range(rgrid.gdim)]
    print("midpoint in valid grid: rm=",rm,"mid_gidx_rg=",mid_gidx_rg,"mid_gidx=",mid_gidx,"pars=",pargrid.strParValue(mid_gidx))
    exit(0)
    print("\n(ii.3) Test searchOptimum(.)")
    print("---------------------------------")
    rgps.searchOptimum(args,data_dict)
    print("\nResult of RandomGridPathSearch:")
    outputRandomGridPathSearch(data_dict,mode=2,indent=3)
    #print("data_dict=",data_dict)
    #print("search_paths=",data_dict['RandomGridPathSearch']['search_paths'])
    #print("optimum=",data_dict['RandomGridPathSearch']['grid'])
    exit(0)
    
    import json
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            return json.JSONEncoder.default(self, obj)
    print(json.dumps(data_dict['RandomGridPathSearch'],indent=3,sort_keys=True,cls=NumpyEncoder))
