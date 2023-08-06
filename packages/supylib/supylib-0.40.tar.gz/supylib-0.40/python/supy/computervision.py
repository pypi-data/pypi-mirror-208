# coding: utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import scipy.special
from copy import copy

from skimage.morphology import skeletonize as skeletonize_skimage
from skimage.morphology import thin as thin_skimage
from skimage.morphology import medial_axis as medial_axis_skimage 

# ***************************************************************************************
# ***************************************************************************************
# SUPY_COMPUTERVISION.PY
# -------------------------
# Version 21/02/2021, Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany
# EXPERIMENTAL SOFTWARE: NO WARRANTIES! REGULARLY BACKUP YOUR DATA!
#
# CONTENTS:
# -------------------------
# Part I) Simple Image Transformations for proper displaying and rescaling
#  - def scaleImage_withLimits(img,factor,maxsize=None,minsize=(1,1),interpolation=cv2.INTER_NEAREST)
#  - def getInt8Image(img,nsig_std=None)
#  - def getInt8ImagePyramid(img_list,pad=0,nsig_std=None,bg_val=0)
#  - def getStdImage(img,sz_kernel=0,flagMedian=0)
#  - def getShiftedImage(img,dx,dy,c=0)
#  - def getLoupeImage(img,x1,y1,x2,y2,fac_scale)
#  - def getMaskedOverlay(img,masks,colors,transp,maskorder=None)
#
# Part II) Threshold and Maximum Operations
#  - def localmaxima(im,rx=3,ry=None,flagMask=1,val0=0)
#  - def softmax(a)
#  - def max_per_component(imgs)
#  - def softmax_per_component(imgs)
#  - def getThresholdedImage(im,thresh=0,threshType='abs')
#  - def rankThreshFilter(im, r, p_rank=0.5,thresh_fac=1.0)
#  - def limitPosNegValsByMedians(im,fac_med_pos,fac_med_neg=None)
#  - def getBWImage_locally_darkest(img,sz_kernel,p_darkest)
#  - def getBWImage_darkest(img,p_darkest)
#  - def getBWImage_opened_closed(img,open_and_closes)
#  - def getBWImage(img,th_lo,th_hi, flagMorph,krn_close,krn_open, flagCanny,canny_th1,canny_th2,canny_aperturesize)
# 
# Part III) Kernel Operations
#  - def getDoGKernel(r,sigx1,sigy1=None,sigx2=0,sigy2=None,phi=0.0,weight1=1.0,weight2=1.0,mu_x=0.0,mu_y=0.0,box=None,mu_x_target=0.0,mu_y_target=0.0,flagCircularMask=1,norm=0,ry=None)
#  - def getGaborWaveletKernel(r, lmbda, theta, psi, sigma, gamma)
#  - def getLineKernel(l,b,phi,eps=1e-6,r=None)
#  - def getBlockKernel(r,x1,y1,l,w,phi=0,norm=1)
#  - def getDoBKernel(r,l,alpha,beta,wIn,wOut,phi,offset=[0,0],flagReturnPosNegMasks=0)
# 
# Part IV) Region- and Kernel-based operations
#  - def applyKernelOnImagePos(img,kernel,i,j,op='+',w=1.0,flagInplace=0)
#  - def extractRegion_by_tracking_kernels(region_seed, img_max, img_max_arg, kernels, th, w=1.0, dil_sz=3, maxIterations=None)
#  - def extractRegions_by_doublethresh(img, th1, th2, openclose, minmax_diag=[0,100000], minmax_ACR=[0,1], conn=8)
#  - def reganalysis(stats,nMax,nMin,flagExtended=0)
#  - def eraseBBox(img,bbox,pad=0.2)
#  - def cleanFromSmallObjects(im,mpc_x, mpc_y=None)
#  - def cleanFromNonMaximumRegions(im,rx,ry=None,val0=0,th=0,im_bin=None)
#
# Part V) Skeleton-Algorithms
#  - def skeletonize(img, alg='MedialAxis_skimg', returnDistance=1)
#  - def skeletonize_simple(img)
#  - def skeletonize_NischwitzHaberaecker(img)
#  - def zeroregions_in_neighborhood(im_binary,pad=0) 
#  - def skeleton_inner_leaf_nodes(im_skeleton)
#  - def getSkeletonLength(im_skel,distance,im_leafnodes=None)
#  - def getDist2Backgrnd_quantiles(im_foregrnd_subset,distance,quantiles=[0,0.01,0.1,0.5,1],im_leafnodes=None,flagCircleLeaf=1)
# ***************************************************************************************
# ***************************************************************************************


# ***************************************************************************************
# Part I) Simple Image Transformations and Threshold Operations
# ***************************************************************************************

def scaleImage_withLimits(img,factor,maxsize=None,minsize=(1,1),interpolation=cv2.INTER_NEAREST):
    """
    scale image size by a factor, but limit to a maximum/minimum pixel size (preserving aspect ratio)
    :param img: original image 
    :param factor: scaling factor
    :param maxsize: maximum image size after scaling as tuple (max_width, max_height)
    :param minsize: minimum image size after scaling as tuple (min_width, min_height)
    :returns: img_scaled, actual_factor
    """
    sz_img  = (img.shape[1], img.shape[0])        # width and height of original image
    assert float(sz_img[0])*float(sz_img[1])>0,"image must not be empty!"
    sz_img_scaled = (int(round(sz_img[0]*float(factor))),int(round(sz_img[1]*float(factor))))
    if (not minsize is None) and (sz_img_scaled[0]<minsize[0] or sz_img_scaled[1]<minsize[1]):
        factor = max(float(minsize[0])/float(sz_img[0]), float(minsize[1])/float(sz_img[1]))
        sz_img_scaled = (int(round(sz_img[0]*float(factor))),int(round(sz_img[1]*float(factor))))
    if (not maxsize is None) and (sz_img_scaled[0]>maxsize[0] or sz_img_scaled[1]>maxsize[1]):
        factor = min(float(maxsize[0])/float(sz_img[0]), float(maxsize[1])/float(sz_img[1]))
        sz_img_scaled = (int(round(sz_img[0]*float(factor))),int(round(sz_img[1]*float(factor))))
    assert ((minsize is None) or (sz_img_scaled[0]>=minsize[0] and sz_img_scaled[1]>=minsize[1])) and \
           ((maxsize is None) or (sz_img_scaled[0]<=maxsize[0] and sz_img_scaled[1]<=maxsize[1])),\
           "scaling image to desired limits maxsize="+str(maxisze)+" and minsize="+str(minsize)+" is not possible for img of size="+str(sz_img)+"!"
    img_scaled = cv2.resize(img,sz_img_scaled,interpolation=interpolation)
    return img_scaled,factor
    
def getInt8Image(img,nsig_std=None):
    """
    Convert float image img to a uint8 for displaying in IVisit
    :param img: original image (e.g., of pixel type float)
    :param nsig_std: if None then just scale max/min of img to range 0-255
                     else assume that img is standardized, and convert range 0-255 to nsig standard deviations from 0
    :returns: converted image
    """
    if nsig_std is None:
        img_float = np.array(img,'float')
        c=np.max(img_float)-np.min(img_float)
        if(c==0): 
            return np.zeros(img.shape,'uint8')
        else:     
            return np.array(np.floor((img_float-np.min(img_float))*(1.0/c)*255),'uint8') 
    else:
        im_tmp = np.round((-127.0/nsig_std)*img+127.0)
        im_tmp = np.maximum(im_tmp,0) 
        im_tmp = np.minimum(im_tmp,255) 
        return np.array(255-im_tmp,'uint8')  

def getInt8ImagePyramid(img_list,pad=0,nsig_std=None,bg_val=0):
    """
    Place a list of float images into a single image matrix of type uint8 for displaying in IVisit
    :param img_list: list of original images (e.g., of pixel type float); largest image should be first, the others should be in descending order (not really necessary, but yields best results)
    :param pad: separating empty pixels between individual images of the pyramids
    :param nsig_std: if None then just scale max/min of img to range 0-255
                     else assume that img is standardized, and convert range 0-255 to nsig standard deviations from 0
    :param param bg_val: gray value (int) of background region
    :returns: img_matrix: single image matrix including all converted images of the "pyramid" list img_list
    """
    N=len(img_list)                # number of images to be placed into one common matrix
    assert N>=1,"Image list img_list must contain at least one image!"
    img_sizes     = [img.shape for img in img_list];
    # (i) compute image positions and total size of image matrix where the individual images are to be placed
    im_height = img_sizes[0][0]    # height of the image matrix
    im_width  = img_sizes[0][1]    # width of the image matrix
    img_positions = [(0,0)]        # initialize for first image
    i,j=im_height+pad,0            # next position after placing the n-th image (here n=0)
    n=1                            # initialize with next image index
    while n<N:                     # in each while-loop place img_list[n] into common image matrix
        hn,wn = img_sizes[n][0],img_sizes[n][1]  # size of the next (n-th) image
        if i+hn>im_height:         # exceed image borders in y-direction? If so then extend image matrix by a new column
            i,j=0,im_width+pad                   # new pixel position where to place n-th image in the next column 
            im_width=j+wn          # extend image matrix width by new column for the n-th image
            if hn>im_height:im_height=hn         # extend height if necessary
        else:                      # place image into the old column at the next position (i,j)
            if j+wn>im_width: im_width=j+wn      # extend width if necessary
        img_positions=img_positions+[(i,j)]  # add image position for the n-th image to list
        i,j=i+hn+pad,j             # prospective position of the next image
        n=n+1
    #print("N=",N)
    #print("img_pos=",img_positions)
    # (ii) allocate image matrix and place images
    img_matrix = bg_val*np.ones(shape=(im_height,im_width),dtype='uint8')
    for n in range(N):
        i,j=img_positions[n][0],img_positions[n][1]
        h,w=img_sizes[n][0],img_sizes[n][1]
        img_matrix[i:i+h,j:j+w]=getInt8Image(img_list[n],nsig_std)
    return img_matrix

def getStdImage(img,sz_kernel=0,flagMedian=0):
    """
    standardize image within local region of size sz_kernel, 
    i.e., resulting pixel values means how many standard deviations the original pixel was above the local mean value 
    :param img: original image to be binarized
    :param sz_kernel: kernel size defining local regions; if sz_kernel<=0 then standardize over whole image
    :param flagMedian: if >0 then use median instead of mean value for standardization 
    :returns img_std: the standardized image
    :returns mean_img: local means (or medians)
    :returns sig_img: local standard deviations   
    """
    if sz_kernel>1:
        img_float = np.array(img,'float')       # img as float array (to compute means, variances, etc.)
        if flagMedian<=0:
            mean_img  = cv2.boxFilter(img_float,cv2.CV_64F, (sz_kernel,sz_kernel))                     # local mean values
            mean2_img = cv2.boxFilter(np.multiply(img_float,img_float),cv2.CV_64F, (sz_kernel,sz_kernel))  # local second moments
        else:
            mean_img  = cv2.medianBlur(img,sz_kernel)
            mean2_img = cv2.medianBlur(np.multiply(img,img),sz_kernel)
        sig_img = np.sqrt(np.maximum(0,mean2_img-np.multiply(mean_img,mean_img)))                      # local standard deviations
        img_std = img_float-mean_img
        img_std[sig_img>0]=img_std[sig_img>0]/sig_img[sig_img>0]
    else:
        if sz_kernel==1:
            img_std  = np.zeros(img.shape,'float')           # for kernel size <=1 each pixels corresponds to its mean value of the local region
            mean_img = np.array(img,'float')                 # for kernel size <=1 each pixels corresponds to its mean value of the local region
            sig_img  = np.zeros(img.shape,'float')           # for kernel size <=1 each pixels corresponds to its mean value of the local region
        else:
            im_mean = np.mean(img)                           # use whole image to compute mean value
            im_std  = np.std(img)
            #print("im_mean=",im_mean,"im_std=",im_std)
            if im_std>0:
                img_std = 1.0/im_std*(img-im_mean)
                mean_img,sig_img=im_mean,im_std
            else:
                img_std = np.zeros(img.shape,'float')       # constant image with mean 0 (and std 0 cannot be changed)
                mean_img,sig_img=0.0,0.0
    return img_std, mean_img, sig_img

def getShiftedImage(img,dx,dy,fillValue=0,fillImage=None):
    """
    computed image shifted by dx pixels in x-direction and dy pixels in y-direction; fill empty pixels by c
    :param img: original image to be shifted
    :param dx: shift in x-direction
    :param dy: shift in y-direction
    :param fillValue: default value for empty array locations
    :param fillImage: if not None then fill the same locations in fillImage with fillValue as in the shifted image 
                      such that at filled locations, difference between fillImage and img_shifted will be zero!
    :returns img_shifted: shifted image   
    """
    # preallocate empty array and assign slice by chrisaycock
    img_shifted = np.empty_like(img)      # preallocate empty array
    if dx>=0: img_shifted[:,:dx] = fillValue
    else    : img_shifted[:,dx:] = fillValue
    if dy>=0: img_shifted[:dy,:] = fillValue
    else    : img_shifted[dy:,:] = fillValue
    if not fillImage is None:
        assert fillImage.shape==img.shape,"fillImage.shape="+str(fillImage.shape)+" must be same as img.shape="+str(img.shape)+"!"
        if dx>=0: fillImage[:,:dx] = fillValue
        else    : fillImage[:,dx:] = fillValue
        if dy>=0: fillImage[:dy,:] = fillValue
        else    : fillImage[dy:,:] = fillValue
    if dx>0:
        if   dy>0: img_shifted[dy:,dx:] = img[:-dy,:-dx]
        elif dy<0: img_shifted[:dy,dx:] = img[-dy:,:-dx]
        else     : img_shifted[:  ,dx:] = img[:   ,:-dx]
    elif dx<0:
        if   dy>0: img_shifted[dy:,:dx] = img[:-dy,-dx:]
        elif dy<0: img_shifted[:dy,:dx] = img[-dy:,-dx:]
        else     : img_shifted[:  ,:dx] = img[:   ,-dx:]
    else:
        if   dy>0: img_shifted[dy:,:  ] = img[:-dy,:   ]
        elif dy<0: img_shifted[:dy,:  ] = img[-dy:,:   ]
        else     : img_shifted[:  ,:  ] = img[:   ,:   ]
    return img_shifted

def getLoupeImage(img,pos,r,fac_scale,pad='default',bbox_clipped_region=None): 
    """
    compute enlarged image crop from source image 
    :param img      : original image where the loupe operation should be applied to
    :param pos      : list [x,y] of central position where to crop from original image  
    :param r        : radius (or list of radii [rx,ry]) defining the crop region in the original image
    :param fac_scale: enlargement factor (or list of factors [fac_x,fac_y]) for the loupe image (to be applied to the cropped image)
    :param pad      : if 'default' then fill border regions with 0; otherwise fill up with pad 
    :param bbox_clipped_region: if not None, then should be list [x,y,w,h] of length 4; values will be changed (in-place) to bbox of clipped region in img 
    :returns img_loupe: loupe image (cropped and enlarged)
    """
    if not isinstance(r        , (list, tuple)): r=[r,r]
    if not isinstance(fac_scale, (list, tuple)): fac_scale=[fac_scale,fac_scale]
    assert len(pos)      ==2,"pos=(x,y) must be list of length 2, but actually pos="+str(pos)
    assert len(r)        ==2,"r  =(rx,ry) must be list of length 2, but actually r="+str(r)
    assert len(fac_scale)==2,"fac_scale=(scale_x,scale_y) must be list of length 2, but actually fac_scale="+str(fac_scale)
    x,y,rx,ry  =pos[0],pos[1],r[0],r[1]     # central position and raddi in x/y direction of crop region
    x1,y1,x2,y2=x-rx,y-ry,x+rx+1,y+ry+1     # bbox coordinates of crop region
    sc_x,sc_y  =fac_scale[0],fac_scale[1]   # scaling factors in x/y direction
    x1_img=min(max(x1,0),img.shape[1])
    y1_img=min(max(y1,0),img.shape[0])
    x2_img=min(max(x2,x1+1),img.shape[1])
    y2_img=min(max(y2,y1+1),img.shape[0])
    img_loupe_shape = tuple([y2-y1,x2-x1]+list(img.shape[2:]))
    img_loupe       = np.zeros(img_loupe_shape,dtype=img.dtype)
    if pad!='default': img_loupe[:,:]=pad
    img_loupe[(y1_img-y1):(img_loupe_shape[0]+y2_img-y2),(x1_img-x1):(img_loupe_shape[1]+x2_img-x2)]= img[y1_img:y2_img,x1_img:x2_img]        # crop image
    if not bbox_clipped_region is None:
        assert isinstance(bbox_clipped_region,list) and len(bbox_clipped_region)==4,"optional parameter bbox_clipped_region="+str(bbox_clipped_region)+" should be either None or bounding box list [x,y,w,h]"
        bbox_clipped_region[0]=x1_img
        bbox_clipped_region[1]=y1_img
        bbox_clipped_region[2]=x2_img-x1_img
        bbox_clipped_region[3]=y2_img-y1_img
    sh_img_loupe    = np.array(img_loupe.shape) # shape of cropped image
    sh_img_loupe[0]*= max(1,sc_y)               # scale shape of loupe image (y-direction)
    sh_img_loupe[1]*= max(1,sc_x)               # ditto for x direction
    img_loupe=cv2.resize(img_loupe,(sh_img_loupe[0],sh_img_loupe[1]),interpolation=cv2.INTER_NEAREST)   # scale loupe image
    return img_loupe

def getMaskedOverlay(img,masks,colors,transp,maskorder=None): 
    """
    compute masked overlay image for (possibly multiple) binary masks, each having its own color  
    :param img        : original (color) image of size [h,w,3] 
    :param masks      : binary (0/1) mask of size [h,w] or multiple masks of size [nMasks,h,w] 
    :param colors     : array of RGB values [[R,G,B],...] for each mask (or a single RGB value for all masks)  
    :param transp     : transparency value between 0 and 1 (0 means plot only labels); (1 means plot only image) 
    :param maskorder  : list of mask indexes defining in which order to apply colors (only last color will "survive")
    :returns img_ovrly: overlay image 
    """
    assert len(img.shape)==3 and img.shape[2]==3, "Expected RGB image with shape [h,w,3], but obtained img.shape="+str(img.shape)
    assert len(masks.shape)>=2 and len(masks.shape)<=3, "masks must be either 2D or 3D array, but masks.shape="+str(masks.shape)
    if len(masks.shape)==2: masks=np.expand_dims(masks,0)    # if only one mask then expand dimension (so that we have an 3D-array of 2D masks)
    assert masks.shape[1]==img.shape[0] and masks.shape[2]==img.shape[1],"Image must have same size [h,w] as masks! But masks.shape="+str(masks.shape)+" whereas img.shape="+str(img.shape)
    h,w = img.shape[0], img.shape[1]      # image size
    nMasks=masks.shape[0]                 # number of masks
    if maskorder is None: maskorder=range(nMasks)           # default order is 0,1,2,...
    colors=np.array(colors)
    if len(colors.shape)==1: np.expand_dims(colors,0)       # if only one color then expand dimension (so that we have an 2D-array of 1D colors)
    nColors=colors.shape[0]
    assert nColors==1 or nColors==nMasks,"Number of colors must be either 1 or equal to the number of masks, but nColors="+str(nColors)+" and nMasks="+str(nMasks)
    img_ovrly=np.array(img,dtype=img.dtype)
    if transp<1.0:
        mask1=np.zeros((h,w),dtype='uint8')                   # master mask (OR-ing of all masks)
        mask1[np.sum(masks[maskorder],axis=0)>0]=1          # set pixels where at least one mask is >0
        img_mask_col=np.zeros((h,w,3),dtype=img.dtype)      # allocate array for image mask colors (containing color values for each mask pixel)
        for i in maskorder:
            assert i>=0 and i<nMasks,"maskorder="+str(maskorder)+" contains value i="+str(i)+" that is either <0 or exceeds number of masks nMasks="+str(nMasks)
            img_mask_col[masks[i,:,:]>0]=colors[i%nColors]
        idx_mask_on=mask1>0
        if transp<=0.0:
            img_ovrly[idx_mask_on]=img_mask_col[idx_mask_on] # No transparency? Then just use full colors for mask regions
        else:
            img_ovrly[idx_mask_on]=transp*img_ovrly[idx_mask_on] + (1.0-transp)*img_mask_col[idx_mask_on]
    return img_ovrly

    
# ***************************************************************************************
# Part II) Threshold and Maximum Operations
# ***************************************************************************************

def localmaxima(im,rx=3,ry=None,flagMask=1,val0=0): 
    """
    mark local maxima within radius r (non-maximum suppression)
    :param im: original image
    :param rx: radius in x-direction of the neighborhood region searched for local maxima
    :param ry: radius in y-direction of the neighborhood region searched for local maxima
    :param flagMask: if <1 then non-maximum pixels are set to val0, and maximum pixels are kept; otherwise a binary image is returned
    :param val0: 0-value for non-maximum pixels if flagMask<1 
    """
    if len(im.shape)<2:im = im.reshape()
    if ry is None: ry=rx
    szx,szy=2*rx+1,2*ry+1
    im_dil = cv2.dilate(im, cv2.getStructuringElement(cv2.MORPH_RECT,(szx,szy)))
    im_result = cv2.compare(im,im_dil,cv2.CMP_GE)
    if flagMask<1:
        im_result=np.array(im)
        im_result[im_result<=0]=val0
    return im_result

def softmax(a):  
    """
    Compute Softmax function for potential vector a
    :param a: Vector of dendritic potentials of the softmax neuron population  
    :returns: softmax(a) which is a vector of same size as a  
    """
    e_a = np.exp(a - np.max(a))  # subtract maximum potential such that maximal exponent is 1 (for numerical stability)
    return e_a / e_a.sum()       # return softmax function value

def max_per_component(imgs):
    """
    compute maximum per component for a list of images 
    :param imgs: list of images; max is computed for each i,j over imgs[0,i,j],...,imgs[n-1,i,j], where n is number of images
    :returns: im_max: image of same size as images in imgs where im_max(i,j) is maximum value over all n 
    :returns: im_max_arg: image containing the indexes of the image which is maximal at position (i,j)
    """
    im_max,im_max_arg = imgs[0],np.zeros(imgs[0].shape,'int')
    for i in range(len(imgs)):
        if i>0:
            im=imgs[i]                         # try next image from list and get ...
            im_max = np.maximum(im_max,im)     # maximum over all images (per component)
            im_max_arg[im_max==im]=i           # save index i of maximum
    return im_max,im_max_arg


def softmax_per_component(imgs):
    """
    compute softmax per component for a list of images 
    :param imgs: list of images; softmax is computed for each i,j over imgs[0,i,j],...,imgs[n-1,i,j], where n is number of images
    :returns im_max_softmax: images of same size as images in imgs where im_max_softmax(i,j) is maximum probability (= softmax value) over all n
    :returns imgs_softmax: list of images containing the softmax probabilities 
    :returns im_max_arg: image containing the indexes of the image which is maximal at position (i,j)
    """
    # (i) compute maximas over all images imgs
    im_max,im_max_arg = max_per_component(imgs) 
    # (ii) compute softmax-function component-wise over all stacked images
    im_e_a=[np.exp(im-im_max) for im in imgs]  # list of exp-ed images (shifted by maximum value for numeric stability) 
    im_e_a_sum = np.zeros(im_e_a[0].shape)     # initialize with zeros for summation...
    for im in im_e_a: im_e_a_sum=im_e_a_sum+im # sum all exp-ed images (per components)
    imgs_softmax = [np.divide(im,im_e_a_sum) for im in im_e_a]
    im_max_softmax = np.divide(np.ones(im_e_a_sum.shape),im_e_a_sum)
    return im_max_softmax, imgs_softmax, im_max_arg


def getThresholdedImage(im,thresh=0,threshType='abs'):
    """
    Do thresholding and convert to binary image
    :param im: image to be thresholded
    :param thresh: threshold value (to be interpreted according to threshType)
    :param threshType: either 'abs' (absolute threshold), 'relMax' (threshold relative to image maximum) or 'relMedian' (relative to image median)
    :returns: binary image (0/1 of type uint8) where above-threshold-values are 1
    """
    assert threshType in ['abs','relMax','relMedian']
    if threshType=='abs':
        thresh=thresh
    elif threshType=='relMax':
        thresh=np.max(im)*thresh
    elif threshType=='relMedian':
        thresh=np.median(im)*thresh
    result=np.array(np.zeros(im.shape),'uint8')
    result[im>thresh]=1
    return result

def rankThreshFilter(im, r, p_rank=0.5,thresh_fac=1.0):  # return binary mask of those image-pixels that have at least value eps-fac*p_rank_value, where p_rank_value is the value of the p_rank largest pixel
    """
    compute a binary mask of those image-pixels that have a pixel value that is at least factor thresh_fac larger than the p_rank pixel in the local neighbourhood of radius r
    :param im: image to be filtered
    :param r: kernel radius (i.e., size = 2*r+1) 
    :param p_rank: relative rank for threshold reference setting: p_rank=0 means the largest pixel value in the local window; p_rank=0.5 corresponds to the median (default)
    :param thresh_fac: threshold is set to treshfac*p_rank_value, e.g., for threshfrac=1.1 and p_rank=0.5 all pixels are selected that are more than 10% above the local median
    :returns mask: binary mask of same size as image im, where those pixels are set to 1 that are above the local threshold   
    :returns im_prank: image of p-rank-values (e.g., for p_rank=0.5, each pixel is the local median of im at that location
    """
    m,n            = im.shape                    # get image size
    mask           = np.zeros((m,n),'int')       # binary mask: initialize with 0s 
    im_prank       = np.zeros((m,n),'float')     # image of p-rank-values: initialize with 0s 
    mini,maxi=[max(0,i-r) for i in range(m)],[min(m,i+r+1) for i in range(m)] # mini[i]:maxi[i] is valid row index range in i-th row of image 
    minj,maxj=[max(0,j-r) for j in range(n)],[min(n,j+r+1) for j in range(n)] # minj[j]:maxj[j] is valid column index range in j-th column of image 
    for i in range(m):                           # loop over all image rows
        sz_i = maxi[i]-mini[i]                   # valid range of rows for kernel window
        for j in range(n):                       # loop over all image columns
            sz_j = maxj[j]-minj[j]               # valid range of columns for kernel window
            clipsize = sz_i*sz_j                 # valid size of the image clip
            #print("i=",i,"j=",j,"r=",r,"clipsize=",clipsize)
            clip_flat_sorted = np.sort((-im[mini[i]:maxi[i],minj[j]:maxj[j]]).flat)    # sort pixels values in image clip
            im_prank[i,j]=clip_flat_sorted[int(p_rank*clipsize)]
            #print("cfs.shape=",clip_flat_sorted.shape,"idx=",int(p_rank*clipsize))
            if im[i,j]>thresh_fac*im_prank[i,j]: mask[i,j]=1  # if image pixel value is larger than threshold then set mask pixel
    return mask,im_prank

def limitPosNegValsByMedians(im,fac_med_pos,fac_med_neg=None): 
    """
    Amplitude Clipping using median of positive and negative values
    :param fac_med_pos: positive image values are limited to fac_med_pos*median of positive values
    :param fac_med_neg: negative image values are limited to fac_med_neg*median of negative values (if None then same value as fac_med_pos)
    :returns: clipped/limited image
    """
    if fac_med_neg is None: fac_med_neg=mac_med_pos
    pos,neg=im>0,im<0
    im_AN=np.array(im)
    if np.any(pos):
        med_pos=np.median(im[pos])     # median of positive values of the image
        im_AN=np.minimum(im_AN,fac_med_pos*med_pos)
    if np.any(neg):
        med_neg=np.median(im[neg])     # median of negative values of the image
        im_AN=np.maximum(im_AN,fac_med_neg*med_neg)
    return im_AN

def getBWImage_locally_darkest(img,sz_kernel,p_darkest): 
    """
    binarize image by selecting locally darkest pixels 
    :param img: original image to be binarized
    :param sz_kernel: kernel size defining local regions 
    :param p_darkest: select fraction p_darkest of darkest pixels within loocal regions 
    :returns img_darkest: image where locally darkest pixels are set 
    """
    img_std = getStdImage(img,sz_kernel)[0]                 # get standardized image (does not change order of pixel brightness!)
    th = np.sqrt(2.0)*scipy.special.erfinv(2*p_darkest-1)   # get threshold corresponding to p_darkest assuming Gaussian distribution
    img_darkest = np.zeros(img.shape,'uint8')               # allocate image for locally darkest pixels
    img_darkest[img_std<=th]=255                            # set darkest pixels
    return img_darkest, img_std             # return resulting image and standardized image


def getBWImage_darkest(img,p_darkest):
    """
    Transform Image to a binary (black/white) image
    :param img: original image to be binarized
    :param p_darkest: extract a fraction p_darkest of the darkest pixels of the image 
    :returns img_darkest: image where (globally) darkest pixels are set 
    """
    rank_p = min(img.size-1,np.floor(p_darkest*img.size)) # pixel rank correponding to the brightest of the fracion of p_darkest darkest pixels
    sorted = np.sort(img.flat)                            # sort pixels
    th = sorted[rank_p]                        # threshold for selecting darkest pixels
    img_darkest = copy(img)                    # allocate image for darkest pixels
    img_darkest[img>=th]=0                     # set darkest pixels
    img_darkest[img<th]=255                    # remove brighter pixels
    return img_darkest                         # return resulting image

def getBWImage_opened_closed(img,open_and_closes):
    """
    do morphological operations on img
    :param img: original image 
    :param open_and_closes: list [open1_sz, close1_sz, open2_sz,close2_sz,...] of kernel sizes for opening and closing operations
    :returns img_result: resulting image after morphological operations  
    """
    img_result = copy(img)     # allocate memory for result image
    flagOpen=1                 # start with opening-operation
    for sz in open_and_closes: # loop over all list elements defining kernel sizes
        if sz>0:
            kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(sz,sz))           # create ellipsoid kernel of desired size
            if flagOpen>0:
                img_result = cv2.morphologyEx(img_result,cv2.MORPH_OPEN,kernel)      # do opening operation
            else:
                img_result = cv2.morphologyEx(img_result,cv2.MORPH_CLOSE,kernel)     # do closing operation
        flagOpen=1-flagOpen    # toggle flag (between 0 and 1 corresponding to "close" and "open")
    return img_result          # return resulting image

def getBWImage(img,th_lo,th_hi, flagMorph,krn_close,krn_open, flagCanny,canny_th1,canny_th2,canny_aperturesize):
    """
    Transform Image to a binary (black/white) image
    :param img: original image to be transformed
    :param th_lo: threshold defining the "lo-image" containing the th_lo darkest pixels
    :param th_hi: threshold defining the "hi-image" containing the th-hi darkest pixels  (th_hi<th_lo !!!)
                 It should be th_hi<th_lo such that hi_image will be a subset of lo-image !!!
    :param flagMorph: if >0 then do morphological close/open-operations for the hi-image 
                     else just the hi-image is returned...
    :param krn_close: kernel size for morhological closing operation
    :param krn_open : kernel size for morhological open operation
    :param flagCanny: if >0 then do canny edge detection on original image 
    :param canny_th1: threshold 1 for canny operation 
    :param canny_th2: threshold 2 for canny operation 
    :param canny_aperturesize: aperturesize for canny operation 
    :returns img_bw: final b/w image
    :returns img_bw_hi: hi image
    :returns img_bw_lo: lo image
    :returns img_bw_closed: closed hi image 
    :returns img_bw_opened: opened hi image
    :returns img_edges: image after canny edge detection
    """
    # (i) Sorting and thresholding
    sorted = np.sort(img.flat)
    img_bw_lo=copy(img)
    img_bw_lo[img>sorted[th_lo]]=0
    img_bw_lo[img<=sorted[th_lo]]=255
    img_bw_hi=copy(img)
    img_bw_hi[img>sorted[th_hi]]=0
    img_bw_hi[img<=sorted[th_hi]]=255
    # (ii) morphological operations
    img_bw_closed = copy(img_bw_hi)
    img_bw_opened = copy(img_bw_hi)
    if(flagMorph>0):
        kernel_open  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(krn_open,krn_open))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(krn_close,krn_close))
        img_bw_lo     = cv2.morphologyEx(img_bw_lo,cv2.MORPH_OPEN,kernel_open)
        img_bw_closed = cv2.morphologyEx(img_bw_hi    ,cv2.MORPH_CLOSE,kernel_close) 
        img_bw_opened = cv2.morphologyEx(img_bw_closed,cv2.MORPH_OPEN , kernel_open)
        #img_bw_closed = cv2.dilate(img_bw_hi,np.ones((dil_sz,dil_sz)),iterations=dil_it)
        #img_bw_closed = cv2.erode(img_bw_closed,np.ones((erd_sz,erd_sz)),iterations=erd_it)
        #img_bw_opened = cv2.dilate(img_bw,np.ones((dil_sz,dil_sz)),iterations=dil_it)
        img_bw = np.multiply(img_bw_opened,img_bw_lo)   # AND-ing
        img_bw[img_bw>0]=255
    else:
        img_bw = copy(img_bw_hi)
        #img_bw[img_bw_hi>0]=255
    # (iii) canny edge detection 
    img_edges = copy(img)
    if(flagCanny>0):
        img_edges = cv2.Canny(img,canny_th1,canny_th2,canny_aperturesize)
    return img_bw,img_bw_hi,img_bw_lo,img_bw_closed,img_bw_opened,img_edges

# ***************************************************************************************
# Part III) Kernel Operations
# ***************************************************************************************

def getDoGKernel(r,sigx1,sigy1=None,sigx2=0,sigy2=None,phi=0.0,weight1=1.0,weight2=1.0,mu_x=0.0,mu_y=0.0,box=None,mu_x_target=0.0,mu_y_target=0.0,flagCircularMask=1,norm=0,ry=None):
    """
    generate DifferenceOfGaussian kernel
    that is normalized and oriented
    :param r: kernel radius (i.e., size = 2*r+1) 
    :param sigx1,sigy1: s.d. in x and y direction of the inner unorientated gaussian (sigy defaults to sigx)
    :param sigx2,sigy2: s.d. in x and y direction of the outer unorientated gaussian (sigy defaults to sigx); if 0 then just take first Gaussian (default)!
    :param phi: rotation in rad (default: 0 rad)
    :param weight1: weight for the inner gaussian (=sum over all values)
    :param weight2: weight for the outer gaussian (=sum over all values)
    :param mu_x: offset of Gauss center relative to midpoint in x-direction (before rotation)
    :param mu_y: offset of Gauss center relative to midpoint in y-direction (before rotation)
    :param box: integer list [x1 y1 x2 y2] defining a rectangle that will be cut out (default: whole kernel region [-r -r r r])
    :param mu_x_target: offset of Gauss center relative to midpoint in x-direction (target after rotation)
    :param mu_y_target: offset of Gauss center relative to midpoint in y-direction (target after rotation)
    :param flagCircularMask: if set then apply a circular mask; otherwise full size rectangular
    :param norm: if >0 then the final kernel is normalized to Euklidean length 1
    :param ry: if not None then use ry as radius in y-direction (if None, then r is radius for both x- and y-direction)  
    :returns kernel: resulting kernel  
    """
    if sigy1==None: sigy1=sigx1   # default: sigy1 = sigx1
    if sigy2==None: sigy2=sigx2   # default: sigy2 = sigx2
    sz_x=2*r+1                    # kernel size
    if ry is None: ry,sz_y=r,sz_x # size in y direction same as in x direction?
    else: sz_y=2*ry+1             # size in y direction differs from size in x-direction
    x = np.array([np.arange(-r,r+1) for i in range(sz_y)],'float')           # x values relative to kernel mid point (=origin)
    y = np.array([np.arange(ry,-ry-1,-1) for i in range(sz_x)],'float').T    # y values relative to kernel mid point (=origin)
    kernel1 = np.zeros((sz_y,sz_x))  # allocate kernel
    h = np.sqrt(np.multiply(x,x)+np.multiply(y,y)) # distance of P(x,y) from origin
    mask = np.ones(kernel1.shape)                  # initialize mask with ones
    if flagCircularMask>0: mask[h>r]=0             # set all points outside circle with radius r to zero ?
    x_rot = (x-mu_x_target)*np.cos(-phi)-(y-mu_y_target)*np.sin(-phi)-mu_x   # rotate back to coordinates of the Gauss template function
    y_rot = (y-mu_y_target)*np.cos(-phi)+(x-mu_x_target)*np.sin(-phi)-mu_y   # rotate back to coordinates of the Gauss template function
    x_rot2=np.multiply(x_rot,x_rot)                # x_rot squared
    y_rot2=np.multiply(y_rot,y_rot)                # y_rot squared
    varx1,vary1 = sigx1*sigx1, sigy1*sigy1         # variances for inner Gaussian
    varx2,vary2 = sigx2*sigx2, sigy2*sigy2         # variances for outer Gaussian
    if not box is None:                            # cut out rectangular region and set remaining area to 0 ?
        #mask[(x_rot+mu_x_target)<box[0]]=0
        #mask[(y_rot+mu_y_target)<box[1]]=0
        #mask[(x_rot+mu_x_target)>box[2]]=0
        #mask[(y_rot+mu_y_target)>box[3]]=0
        mask[(x_rot)<box[0]]=0
        mask[(y_rot)<box[1]]=0
        mask[(x_rot)>box[2]]=0
        mask[(y_rot)>box[3]]=0
    #print("mask=",mask)
    #fac1 = 1.0/(2.0*np.pi*sigx1*sigy1)            # pre-factor of Gaussian 1
    #fac2 = 1.0/(2.0*np.pi*sigx2*sigy2)            # pre-factor of Gaussian 2
    g1 = np.exp(-0.5*(x_rot2/varx1+y_rot2/vary1))  # first Gaussian kernel
    g1 = np.multiply(g1,mask)                      # multiply with mask
    g1 = g1*weight1/np.sum(g1)                     # ...normalized to sum 1
    if varx2>0 and vary2>0:
        g2 = np.exp(-0.5*(x_rot2/varx2+y_rot2/vary2))  # second Gaussian kernel
        g2 = np.multiply(g2,mask)                      # multiply with mask
        g2 = g2*weight2/np.sum(g2)                     # ...normalized to sum 1
        kernel = g1-g2                                 # final kernel is difference of gaussians
    else:
        kernel = g1                                # if variances are <=0 then just take first Gaussian kernel
    if norm>0:                                     # normalize to Euklidean length 1?
        nrm=np.linalg.norm(kernel)
        if nrm>0: kernel=kernel/nrm             
    return kernel

def getGaborWaveletKernel(r, lmbda, theta, psi, sigma, gamma):
    """
    generate complex Gabor wavelet kernel that is normalized and oriented
    For details see https://en.wikipedia.org/wiki/Gabor_filter
    :param r: kernel radius (i.e., size = 2*r+1) 
    :param lmbda: wavelength of sinusoidal factor (1/lmbda is frequency)
    :param theta: orientation/rotation in rad
    :param psi: phase offset
    :param sigma: standard deviation of the Gaussian envelope
    :param gamma: spatial aspect ration specifying the ellipticity of the support of the Gabor function
    :returns kernel: resulting kernel  
    """
    sz=2*r+1                      # kernel radius
    kernel1 = np.zeros((sz,sz))   # allocate kernel
    x = np.array([np.arange(-r,r+1) for i in range(sz)],'float')       # x values relative to kernel mid point (=origin)
    y = np.array([np.arange(r,-r-1,-1) for i in range(sz)],'float').T  # y values relative to kernel mid point (=origin)
    h = np.sqrt(np.multiply(x,x)+np.multiply(y,y)) # distance of P(x,y) from origin
    mask = np.ones((sz,sz))                        # initialize mask with ones
    mask[h>r]=0                                    # set all points outside circle with radius r to zero
    x_rot = x*np.cos(-theta)-y*np.sin(-theta)      # rotate back
    y_rot = y*np.cos(-theta)+x*np.sin(-theta)      # rotate back 
    x_rot2=np.multiply(x_rot,x_rot)                # x_rot squared
    y_rot2=np.multiply(y_rot,y_rot)                # y_rot squared
    gamma2,sigma2=gamma*gamma,sigma*sigma          # squared parameters
    g1 = np.exp(-0.5*(x_rot2+gamma2*y_rot2)/sigma2)# first Gaussian factor
    g2 = np.exp(1j*(2.0*np.pi*x_rot/lmbda+psi))    # second Gaussian factor
    kernel = g1*g2                                 # multiply the two Gaussian factors
    kernel = np.multiply(kernel,mask)                  # multiply with mask 
    #kernel = kernel*1.0/np.sum(kernel)             # normalize to sum 1
    return kernel

def getLineKernel(l,b,phi,eps=1e-6,r=None):
    if r==None: r=l   # kernel radius?
    sz=2*r+1          # kernel size
    kernel = np.zeros((sz,sz))   # allocate kernel
    x = np.array([np.arange(-r,r+1) for i in range(sz)],'float')       # x values relative to kernel mid point (=origin)
    y = np.array([np.arange(r,-r-1,-1) for i in range(sz)],'float').T  # y values relative to kernel mid point (=origin)
    h = np.sqrt(np.multiply(x,x)+np.multiply(y,y))          # distance of P(x,y) from origin 
    alpha = np.arctan2(x,y)                                 # angle of P(x,y) to x-axis
    beta  = phi-alpha                                       # angle between direction angle phi and P(x,y)
    
    idx=beta<0
    beta[idx]=beta[idx]+2*np.pi                     # get beta in range [0,2pi]
    idx=beta>(2*np.pi)
    beta[idx]=beta[idx]-2*np.pi                     # get beta in range [0,2pi]
    idx=beta>np.pi
    beta[idx]=2*np.pi-beta[idx]                     # take complementary angle in [0,pi]
    
    line_x, line_y = np.cos(phi), np.sin(phi)       # normalized direction vector of line (length 1)
    p = line_x*x+line_y*y                           # projection length of point(x,y) on line 
    p_abs = np.absolute(p)                          # (=absolute value of scalar product)
    d = np.sqrt(np.multiply(h,h)-np.multiply(p_abs,p_abs))  # distances of point(x,y) to line from Pythagoras 

    #print("d=",d)
    #print("p=",p)

    kernel[d<=(0.5*b)]=1
    kernel[p_abs<=eps]=0

    #print("x=",x)
    #print("y=",y)
    #print("y=",y)
    #print("alpha=",alpha)
    #print("beta=",beta)
    #print("kernel=\n",kernel)
    

def getBlockKernel(r,x1,y1,l,w,phi=0,norm=1):
    """
    generate block kernel that is oriented and maybe normalized 
    :param r: kernel radius (i.e., size = 2*r+1) 
    :param x,y: left upper edge of rectangular block 
    :param l,w: length and width of rectangular block 
    :param phi: rotation in rad
    :returns kernel: resulting kernel  
    """
    sz=2*r+1                      # kernel radius
    kernel = np.zeros((sz,sz))   # allocate kernel
    x = np.array([np.arange(-r,r+1) for i in range(sz)],'float')       # x values relative to kernel mid point (=origin)
    y = np.array([np.arange(r,-r-1,-1) for i in range(sz)],'float').T  # y values relative to kernel mid point (=origin)
    h = np.sqrt(np.multiply(x,x)+np.multiply(y,y)) # distance of P(x,y) from origin
    mask = np.ones((sz,sz))                        # initialize mask with ones
    mask[h>r]=0                                    # set all points outside circle with radius r to zero
    x_rot = x*np.cos(-phi)-y*np.sin(-phi)          # rotate back
    y_rot = y*np.cos(-phi)+x*np.sin(-phi)          # rotate back 
    cond=np.logical_and(x_rot>=x1,np.logical_and(x_rot<=x1+l,np.logical_and(y_rot>=y1,y_rot<=y1+w)))
    kernel[np.where(cond)]=1   # set block
    if norm>0: kernel = kernel*1.0/np.sum(kernel)  # normalize to sum 1 ?
    #print("kernel=\n",kernel)
    #exit(0)
    return kernel

def getDoBKernel(r,l,alpha,beta,wIn,wOut,phi,offset=[0,0],flagReturnPosNegMasks=0):
    """
    generate DoB kernel (DoB=difference of blocks) that is centered and oriented  
    :param r: kernel radius (i.e., size = 2*r+1) 
    :param l: absolute length of block
    :param alpha: aspect ratio width/length (i.e., width = length*alpha)
    :param beta:  magnification factor for outer region (l_out=l*beta; w_out=w+l_out-l or beta=1+(w_out-w)/l)
    :param wIn: total weight of inner kernel; i.e., sum of inner kernel will be wIn
    :param wOut: total weight of outer kernel; i.e., sum of outer kernel will be wOut 
    :param phi: rotation in rad
    :param offset: offset=[offset_x,offset_y] is offset of kernel relativ to midpoint 
    :param flagReturnPosNegMasks: if >0 then return (kernel,mask_pos,mask_neg); else return only kernel
    :returns kernel: resulting kernel  
    """
    # (i) inner kernel
    l1,w1 = l,l*alpha                                  # length,width
    x1,y1 = -l1/2.0+offset[0], -w1/2.0+offset[1]       # left upper corner of rectangular block
    kernel1 = wIn*getBlockKernel(r,x1,y1,l1,w1,phi,1)  # compute kernel, normalize to sum wIn
    # (ii) outer kernel
    l2,w2 = l1*beta, w1+l1*beta-l1  # length,width
    x2,y2 = -l2/2.0+offset[0], -w2/2.0+offset[1]       # left upper corner of rectangular block
    kernel2 = getBlockKernel(r,x2,y2,l2,w2,phi)
    kernel2[kernel1>0]=0            # erase locations where kernel1 is active
    kernel2=kernel2*wOut/np.sum(kernel2)
    # (iii) compose final kernel
    kernel = kernel1+kernel2
    #print("kernel=",kernel)
    if flagReturnPosNegMasks>0: return (kernel,kernel1,kernel2)
    return kernel

# ***************************************************************************************
# Part IV) Region- and Kernel-based operations
# ***************************************************************************************

def applyKernelOnImagePos(img,kernel,i,j,op='+',w=1.0,flagInplace=0):
    """
    apply kernel at given position (i,j) on image by using a certain operation (e.g., +,*,max) and considering kernel/image borders
    :param img: image to apply the kernel on
    :param kernel: the kernel to be applied
    :param i,j: position in image where the kernel is applied to
    :param op: the operation to be used
               op='+'     : result = image+w*kernel
               op='*'     : result = image*w*kernel
               op='*1+'   : result = image*(1+w*kernel))
               op='max*'  : result = max(image,image*w*kernel)
               op='max*1+': result = max(image,image*(1.0+w*kernel))
    :param w: weight the kernel is multiplied with
    :param flagInplace: if >0 then operation is done inplace (otherwise a copy is returned)
    :returns img_res: resulting image 
    """
    img_res = img
    if flagInplace<=0: img_res = np.array(img) # do inplace operation or create a copy?
    (img_m,img_n) = img.shape                  # image size (m=number of rows, n=number of columns)
    (km,kn) = kernel.shape                     # size of kernel (m=number of rows, n=number of columns)
    rm,rn = int((km-1)/2),int((kn-1)/2)        # kernel radii
    assert (2*int(rm)+1 == km)and(2*rn+1 == kn), "Kernel sizes must be odd!! But km="+str(km)+" and kn="+str(kn)+" !!"
    offset_l,offset_r = max(rn-j,0), max(j+rn-img_n+1,0) # cut off kernel pixels due to (left/right) border effects?
    offset_t,offset_b = max(rm-i,0), max(i+rm-img_m+1,0) # cut off kernel pixels due to (top/bottom) border effects?
    #print("o_l,o_r,o_t,o_b=",offset_l,offset_r,offset_t,offset_b)
    #print("idx in image = [",i-rm+offset_t,i+rm-offset_b+1,";",j-rn+offset_l,j+rn-offset_r+1,"]")
    #print("idx in kernl = [",offset_t,km-offset_b,";",offset_l,kn-offset_r,"]")
    assert op in ['+','*','*1+','max*','max*1+'], "Unknown operation op="+str(op)
    if op=='+':
        img_res[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] = img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] + \
                                                                                        w*kernel[offset_t:(km-offset_b),offset_l:(kn-offset_r)]
    elif op=='*':
        img_res[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] = img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] \
                                                                                        * w*kernel[offset_t:(km-offset_b),offset_l:(kn-offset_r)]
    elif op=='*1+':
        img_res[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] = img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] \
                                                                                        * (1.0+w*kernel[offset_t:(km-offset_b),offset_l:(kn-offset_r)])
    elif op=='max*':
        img_res[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] = np.maximum(img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)], \
                                                                                                   img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)]*w*kernel[offset_t:(km-offset_b),offset_l:(kn-offset_r)])
    elif op=='max*1+':
        img_res[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)] = np.maximum(img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)], \
                                                                                                   img[(i-rm+offset_t):(i+rm-offset_b+1), (j-rn+offset_l):(j+rn-offset_r+1)]*(1.0+w*kernel[offset_t:(km-offset_b),offset_l:(kn-offset_r)]))
    return img_res
    

def extractRegion_by_tracking_kernels(region_seed, img_max, img_max_arg, kernels, th, w=1.0, dil_sz=3, maxIterations=None):
    """
    extracts most salient region in img_max by tracking kernel
    :param region_seed: initial region to be expanded (should by binary 0,255)
    :param img_max, img_max_arg: maximum image and their indexes as obtained form max_per_component, for example 
    :param kernels: list of kernels (or their masks) corresponding to the indexes in img_max_arg
    :param th: threshold for termination (on values in img_max)
    :param w: factor to weigh the kernel 
    :param dil_sz: kernel size for dilatation 
    :param maxIterations: maximum number of grow iterations 
    :returns region: binary image of the extracted region 
    """
    #print("extractRegion: th=",th, " w=", w, " dil_sz=",dil_sz," maxIt=",maxIterations)
    cond_evid     = img_max                       # initialize conditional evidence
    (img_m,img_n) = img_max.shape                 # image size (m=number of rows, n=number of columns)
    region        = np.zeros(region_seed.shape,'float')
    region[region_seed>0]=255                       # initialize region with seed region
    margin        = copy(region)                  # initialize margin
    sz_margin     = np.sum(margin>0)              # margin size = sum of pixels 
    dil_kernel    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dil_sz,dil_sz))
    # (i) loop as along there is a new margin
    cnt=0
    while sz_margin>0:                            # are there any new pixels?
        #print("cnt=",cnt)
        list_i, list_j = np.where(margin>0)            # line and column indexes of margin pixels (same size)
        # (ii) loop over all pixels of the margin and update confidence map
        for ii in range(len(list_i)):                  # loop over all pixels in the margin (to update conditional evidence)
            i,j = list_i[ii], list_j[ii]                       # get position of pixel in margin
            kernel = kernels[img_max_arg[i,j]]                 # winning kernel at that pixel location
            cond_evid = np.maximum(cond_evid,applyKernelOnImagePos(img_max,kernel,i,j,'max*1+',w,0))  # update evidence map by overlaying the winning kernel
        # (iii) dilute region and add above-threshold pixels to region
        region_diluted = cv2.dilate(region,dil_kernel,iterations=1)
        margin = region_diluted-region        # new margin is difference between diluted and old region
        margin[cond_evid<th]=0                # where evidence is above threshold
        sz_margin     = np.sum(margin>0)      # margin size = sum of pixels 
        #print("sz_margin",sz_margin)
        region[margin>0]=255                  # set all pixels of the new margin in the new region
        # (iv) check maximum number of iterations
        cnt=cnt+1
        if not maxIterations is None and cnt>=maxIterations: break
    return region, cond_evid                  # return results

def extractRegions_by_doublethresh(img, th1, th2, openclose, minmax_diag=[0,100000], minmax_ACR=[0,1], conn=8):
    """
    extracts regions by double thresholding
    - thresholding with th1 yields most salient seed regions
    - thresholding with th2 yields less salient pixels
    - final regions are th2-regions that overlap with th1-regions
    :param img: original image 
    :param th1, th2 : the two thresholds 
    :param openclose: final regions are diluted by calling getBWImage_opened_closed with openclose sequence 
    :param conn: 4- or 8-connectivity for extracting connected components 
    :param minmax_diag: consider only regions with a diagonal between minmax_diag[0] and minmax_diag[1]
    :param minmax_ACR: consider only regions with an ACR (Area-to-Circle-Ratio) between min[0] and max[0] value
    :returns regions: binary image of the extracted regions 
    """
    # (i) make the two threshold images
    im_th1 = np.zeros(img.shape,'uint8')
    im_th1[img>th1]=255
    im_th2 = np.zeros(img.shape,'uint8')
    im_th2[img>th2]=255
    print("extrReg_doublethresh: n_im_th1=",np.sum(im_th1)/255.0,np.sum(im_th2)/255.0)
    # (ii) extract connected regions for the two images
    cr1 = cv2.connectedComponentsWithStats(im_th1,conn,cv2.CV_32S)
    cr2 = cv2.connectedComponentsWithStats(im_th2,conn,cv2.CV_32S)
    nReg1    = cr1[0]      # number of regions of th1-image
    nReg2    = cr2[0]      # number of regions of th2-image
    print("cr2[2]=",cr2[2])
    reg1_im  = np.zeros(img.shape)
    reg1_im[cr1[1]>0]=1    # binary th1-image
    reg2_im  = cr2[1]      # th2-regions
    # (iii) construct regions image
    regions = np.zeros(img.shape,'uint8')
    for i in range(1,nReg2):        # loop over all th2-regions
        print("i=",i)
        reg2_i=np.zeros(img.shape)
        reg2_i[cr2[1]==i]=1   # extract region i as binary image
        nn=np.sum(np.multiply(reg1_im,reg2_i))    # count overlap bits of reg2_i with reg1
        #diag = np.linalg.norm([cr2[2][i][2],cr2[2][i][3]])    # compute diagonal length of region from width and height
        #print("diag=",diag, "mindiag=",mindiag)
        if nn>0: regions[reg2_i>0]=255            # if there is overlap then set reg2_i in final regions image
    # (iv) dilute...
    regions = getBWImage_opened_closed(regions,openclose)
    # (v) check region size
    cr = cv2.connectedComponentsWithStats(regions,conn,cv2.CV_32S)
    nReg = cr[0]
    print("check region size: nReg=",nReg,np.min(cr[1]),np.max(cr[1]))
    regions = np.zeros(img.shape)
    for i in range(1,nReg):
        diag = np.linalg.norm([cr[2][i][2],cr[2][i][3]])    # compute diagonal length of region from width and height
        ACR  = cr[2][i][4]/(np.pi*diag*diag/4.0)
        print("diag=",diag, "minmax_diag=",minmax_diag)
        print("ACR =",ACR , "minmax_ACR=",minmax_ACR)
        if diag>=minmax_diag[0] and diag<=minmax_diag[1] and ACR>=minmax_ACR[0] and ACR<=minmax_ACR[1]: regions[cr[1]==i]=255  # take region only if diagonal and ACR have valid values 
    return regions

def reganalysis(stats,nMax,nMin,flagExtended=0):
    n=len(stats)
    refstats=n*[0]
    ext_nRegions=n          # number of regions
    ext_nBlack=0            # total number of (black) pixels in regions
    ext_maxBlack=0          # size of largest black region
    ext_meanBlack=0         # mean black region size
    ext_sdBlack=0           # s.d. of black region sizes
    ext_list_nBlack=n*[0]   # for each region number of black pixels...
    for i in range(n): 
        s=stats[i]          # statistics of the i-th region
        # process extended feature set...
        ext_nBlack=ext_nBlack+s[4]                 # total number of black pixels
        if s[4]>ext_maxBlack: ext_maxBlack=s[4]    # maximum number of black pixels of a region
        ext_list_nBlack[i]=s[4]                    # save number of balck pixels of region in list
        # process normal (old) feature set (as of 12/2017)
        sz=s[2]*s[3]                                                      # total area of bounding box in pixel number
        length = np.sqrt(float(s[2])*float(s[2])+float(s[3])*float(s[3])) # length of the diagonal of the bounding box
        width = float(s[4])/length                                        # width is number of pixels per length unit
        bpa = float(s[4])/float(sz)                                       # black pixels per area ratio
        ar = float(s[2])/float(s[3])                                      # aspect ratio
        ar = max(ar,float(s[3])/float(s[2]))                              # aspect ratio >= 1
        score = sz*ar/bpa/width                                           # score value 
        refstats[i]=[score,sz,length,width,bpa,ar,s]    # refined statistics
    if n>0:
        ext_meanBlack=np.mean(ext_list_nBlack)     # mean black pixels per region
        ext_sdBlack=np.std(ext_list_nBlack)        # s.d. of black pixels per region
    scores = [r[0] for r in refstats]
    idx_sorted=np.argsort(scores)
    #print ("XXXX len(idx_sorted)=", len(idx_sorted))
    #print ("idx_sorted=",idx_sorted)
    idx_maxscore=(idx_sorted[max(n-nMax,0):n])[::-1]
    idx_minscore=idx_sorted[0:min(nMin,n)]
    score_max=[scores[i] for i in idx_maxscore]
    sz_max=[refstats[i][1] for i in idx_maxscore]
    bpa_max=[refstats[i][2] for i in idx_maxscore]
    ar_max=[refstats[i][3] for i in idx_maxscore]
    score_min=[scores[i] for i in idx_minscore]
    sz_min=[refstats[i][1] for i in idx_minscore]
    bpa_min=[refstats[i][2] for i in idx_minscore]
    ar_min=[refstats[i][3] for i in idx_minscore]
    if len(idx_sorted)>=1: 
       fv_max0 = [score_max[0],sz_max[0],sz_max[0],bpa_max[0],ar_max[0]]
    else: 
       fv_max0 = [0,0,0,0,0]
    if len(idx_sorted)>=2: 
       fv_max1 = [score_max[1],sz_max[1],sz_max[1],bpa_max[1],ar_max[1]]
    else: 
       fv_max1 = [0,0,0,0,0]
    if len(score_max)>0:
        features = fv_max0 + fv_max1 + \
                   [np.mean(score_max),np.mean(sz_max),np.mean(bpa_max),np.mean(ar_max),\
                    np.mean(score_min),np.mean(sz_min),np.mean(bpa_min),np.mean(ar_min)]
    else:
        features = fv_max0 + fv_max1 + \
                   [0.0,0,0,0,\
                    0.0,0,0,0]
    if flagExtended>0:
        features = [ext_nRegions, ext_nBlack, ext_maxBlack, ext_meanBlack, ext_sdBlack] + features
    return refstats,features

def eraseBBox(img,bbox,pad=0.2):
    size=img.shape
    #print "size=",size
    x1,y1,x2,y2=bbox[0],bbox[1],bbox[0]+bbox[2],bbox[1]+bbox[3]
    padx,pady=round(np.abs(x2-x1)*0.1),round(np.abs(y2-y1)*0.1)
    x1,y1,x2,y2=int(max(0,x1-padx)),int(max(0,y1-pady)),int(min(size[1]-1,x2+padx)),int(min(size[0]-1,y2+pady))
    #print "x1-y2=",x1,y1,x2,y2
    cv2.fillConvexPoly(img, np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]]), 255)

def cleanFromSmallObjects(im,mpc_x, mpc_y=None):     # mpc_x/y = minimum percent coverage in x/y-direction (relative to image size...); x/y are OR-ed
    """
    clean image from small regions/objects
    :param im: original image (should be binary)
    :param mpc_x: minimium percent coverage in x-direction (relative to image size...); will be OR operated with mpc_y (set >1 for enforcing mpc_y alone); 
    :param mpc_y: minimium percent coverage in y-direction (relative to image size...); will be OR operated with mpc_x (set >1 for enforcing mpc_x alone); default value is mpc_x 
    """
    if mpc_y is None: mpc_y=mpc_x
    m,n=im.shape[0],im.shape[1]
    mc_y,mc_x=np.ceil(mpc_y*m),np.ceil(mpc_x*n)      # minimum extension in x/y direction for a object to be maintained
    cr = cv2.connectedComponentsWithStats(im, 8, cv2.CV_32S)
    num_labels=cr[0]  # number of labels
    labels = cr[1]    # label matrix
    stats = cr[2] # stats [left,top,width,height,area]
    centroids = cr[3] # centroid matrix (1 row per region)
    sum_area=0.0
    sum_bbox=0.0
    idx_valid=[]
    res = np.zeros(im.shape,dtype=im.dtype)
    for i in range(1,num_labels):
        if stats[i,2]>=mc_x or stats[i,3]>=mc_y:
            idx_valid=idx_valid+[i]
            res[labels==i]=255
            sum_area+=stats[i,4]
            sum_bbox+=(stats[i,2]*stats[i,3])
    fg_ratio_total=np.sum(np.array(res>0,'int'))/(max(1,float(m)*float(n)))
    fg_ratio_bboxes=sum_area/float(max(1,sum_bbox))
    fill_ratio=min(1.0,float(max(1,sum_bbox))/(max(1,float(m)*float(n))))
    return res,fg_ratio_total,fg_ratio_bboxes,fill_ratio

def cleanFromNonMaximumRegions(im,rx,ry=None,val0=0,th=0,im_bin=None): # remove regions (set to val0) that have no local maxima within (rx,ry)
    """
    clean image from non-maximum regions (i.e., regions that do not have a maximum within enighborhood (rx,ry)
    :param im: original image 
    :param rx: radius in x-direction of neighborhood searched for maximum 
    :param ry: radius in y-direction of neighborhood searched for maximum 
    :param val0: pixels in non-maximum regions will be set to val0 (default 0)
    :param th: threshold (default 0) for defining regions in the original image (by applying connectedComponents to the thresholded/binarized image)
    :param im_bin: binary image for defining regions in the original image (by applying connectedComponents); default is None (that is im will be thresholded!)
    """
    if im_bin is None:
        im_bin=np.zeros(im.shape,dtype='uint8')
        im_bin[im>th]=1                           # set thresholded image
    assert im.shape==im_bin.shape,"im and im_bin must have same shape!"
    mask_localmax = np.array(localmaxima(im,rx,ry),'bool')          # binary mask for local maxima
    cr = cv2.connectedComponentsWithStats(im_bin, 8, cv2.CV_32S)    # get regions
    num_labels=cr[0]  # number of labels
    labels = cr[1]    # label matrix
    stats = cr[2] # stats [left,top,width,height,area]
    centroids = cr[3] # centroid matrix (1 row per region)
    res_mask = np.zeros(im.shape,dtype=im.dtype)           # allocate result mask
    for i in range(1,num_labels):                          # loop over connected regions
        rg_i=np.zeros(im.shape,dtype='bool')               # initialize mask for region i
        rg_i[labels==i]=1                                  # set mask for region i
        if np.any(np.logical_and(rg_i,mask_localmax)): res_mask[rg_i>0]=1   # if regions has a valid local maximum then add that region
    result=np.array(im)
    result[res_mask<1]=val0
    return result

# ***************************************************************************************
# Part V) Skeleton-Algorithms
# ***************************************************************************************

def skeletonize(img, alg='MedialAxis_skimg', returnDistance=1):
    """ 
    compute image sleketon with a specified algorithm : 
    for more details see: https://scikit-image.org/docs/dev/auto_examples/edges/plot_skeleton.html
    :param img: binary input image
    :param alg: skeleton algorithm being either "simpleOpenSubtractErode","NischwitzHaberaecker","MedialAxis_skimg","Zha84_skimg","Lee94_skimg", or "thin_skimg"  
    :param returnDistance: If >0 return also distance matrix: for each pixel the minimum Euklidean distance to the background area is given
    :returns im_skeleton: skeleton of img (also binary)
    :returns distance: distance matrix; for each pixel the minimum Euklidean distance to the background area is given
    """ 
    if alg=="simpleOpenSubtractErode":
        im_skeleton,distance=skeletonize_simple(img),None
    elif alg=="NischwitzHaberaecker":
        im_skeleton,distance=skeletonize_NischwitzHaberaecker(img),None
    elif alg=="MedialAxis_skimg":
        im_skeleton,distance=medial_axis_skimage(img,return_distance=returnDistance)
        #np.set_printoptions(threshold=sys.maxsize)
        #print("im_skeleton=\n",im_skeleton)
        #print("distnace=\n",distance)
    elif alg=="Zha84_skimg":
        im_skeleton,distance=skeletonize_skimage(img),None
    elif alg=="Lee94_skimg":
        im_skeleton,distance=skeletonize_skimage(img,method='lee'),None
    elif alg=="thin_skimg":
        im_skeleton,distance=thin_skimage(img),None
    else:
        print("Warning! Unknown skeleton algorithm",alg)
        im_skeleton,distance=None,None
    if returnDistance>0 and distance is None and not im_skeleton is None:
        distance=scipy.ndimage.distance_transform_edt(img)
    return im_skeleton,distance

def skeletonize_simple(img):
    """ 
    compute image sleketon of binary image img using simple morphological operations: 
    :param img: binary input image 
    :returns: skeleton of img (also binary)
    """ 
    img = np.array(img>0,'uint8') # binarize
    skel = np.zeros(img.shape, np.uint8)                         # Step 1: Create an empty skeleton
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))  #         and get a Cross Shaped Kernel
    # Repeat steps 2-4
    while True:
        open = cv2.morphologyEx(img, cv2.MORPH_OPEN, element)    # Step 2: Open the image
        temp = cv2.subtract(img, open)                           # Step 3: Subtract open from the original image
        eroded = cv2.erode(img, element)                         # Step 4: Erode the original image and refine the skeleton
        print("type(skel,temp)=",type(skel),type(temp),type(skel[0,0]),type(temp[0,0]))
        skel = cv2.bitwise_or(skel,temp)
        img = eroded   #.copy()
        if cv2.countNonZero(img)==0: break                       # Step 5: If there are no white pixels left ie.. the image has been completely eroded, quit the loop
    return skel

def skeletonize_NischwitzHaberaecker(img):
    """ 
    compute image sleketon of binary image img using the algorithm described in: 
    Alfred Nischwitz, Peter Haberäcker: Masterkurs Computergrafik und Bildverarbeitung, Vieweg Verlag, 2004, pp496
    :param img: binary input image 
    :returns: skeleton of img (also binary)
    """ 
    m,n=img.shape[0],img.shape[1]  # image size (m=rows; n=columns)
    b=-1  # b=don't care!
    M=np.array([[0,0,b,1,1,b,b,0],
                [0,0,0,b,1,b,1,b],
                [b,0,0,0,b,1,1,b],
                [1,b,0,0,0,b,1,b],
                [1,b,b,0,0,0,b,1],
                [1,b,1,b,0,0,0,b],
                [b,1,1,b,b,0,0,0],
                [0,b,1,b,1,b,0,0]]);
    shifts = np.array([[ 0, 1],
                       [-1, 1],
                       [-1, 0],
                       [-1,-1],
                       [ 0,-1],
                       [ 1,-1],
                       [ 1, 0],
                       [ 1, 1]])
    # shifted_idx:            i_target:from      i_target:to             j_target:from      j_target:to           i_source:from      i_source:to       j_source:from      j_source:to          
    shifted_idx=np.array([ [max(0,shifts[i,0]),min(m,m+shifts[i,0]), max(0,shifts[i,1]),min(n,n+shifts[i,1]),   max(0,-shifts[i,0]),min(m,m-shifts[i,0]), max(0,-shifts[i,1]),min(n,n-shifts[i,1])] for i in range(8)])
    print("shifted_idx=\n",shifted_idx)
    removed=1
    while removed>0:
        img_old=img            # keep old image for comparison
        for i in range(8):     # loop over bit masks i=0,1,...,7
            T=img              # initialize T with the image
            for j in range(8): # loop over bit positions in masks
                if M[i,j]!=b:
                    si,sj=shifts[j,0],shifts[j,1]  # shift in i- and j-direction
                    H=np.zeros(img.shape)          # initialize H with zeros
                    H[shifted_idx[j,0]:shifted_idx[j,1],shifted_idx[j,2]:shifted_idx[j,3]]=img[shifted_idx[j,4]:shifted_idx[j,5],shifted_idx[j,6]:shifted_idx[j,7]]  # shift operation
                    if M[i,j]==0: H=1-H;           # invert?
                    T=np.logical_and(H,T)          # AND-operation
            img=np.logical_xor(img,T)              # XOR-Operation
        removed=np.sum(np.logical_xor(img_old,img).flat)
        print("removed=",removed,"sum=",np.sum(img.flat))
    print("finished...")
    return img

def zeroregions_in_neighborhood(im_binary,pad=0): 
    """ 
    computes number of zero-regions around each central pixels (igoring values of central pixels) 
    e.g.: Neighborhoods 000   111   000   000   000   110   111   101   
                        0X0   1X1   0X0   0X0   1X0   0X1   1X0   0X0  
                        000   111   010   011   010   010   001   101
                have     1,    0,    1,    1,    2,    3,    2,    4     zero-regions, respectively.
    For details of algorithm see AB4/p219 (Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany, December 2020)
    :param im_binary: binary image to be analyzed for zeroregions
    :param pad: either 0 or 1: border regions are filled with pad bits (to define proper 8-neighborhoods for each pixel)
    :returns im_n_zerregions: binary image of same size as im_binary, where im_n_zeroregions[i,j] is number of zero regions around pixel (i,j)
    """
    # (i) do padding: extend im_binary by 1 padding bit in each direction (left, right, top, bottom)
    im_bin_sh=im_binary.shape
    im_binary0=pad*np.ones((im_bin_sh[0]+2,im_bin_sh[1]+2),'uint8')  # make copy of im_binary with 1 bit padding around in x/y dimension
    im_binary0[1:-1,1:-1]=im_binary                                  # copy binary input image into inner area of array
    im_binary=im_binary0  
    # (ii) define kernel K corresponding to a 3x3 neighborhood around central pixel (central pixel being ignored) 
    K=np.array([[8,4,2],
                [16,0,1],
                [32,64,128]],'uint8')                # each neighbor is a power of 2 (starting with right neighbor and then moving counter-clockwise) such that each neighborhood is 8bit number
    # (iii) compute by hand the number of zero-regions for each possible neighborhood (defined in (ii)); details see AB4/p219 from 1/12/2020
    tabZeroRegions=np.zeros(256,'uint8')             # compute tab_zeroregions[n]=number of zero-regions for neighborhood n
    for n in range(256):                             # iterate over all 2^8 possible 3x3 neighborhood kernels (assuming 0 in center pixel)
        if n==0:
            tabZeroRegions[n]=1                      # only exception case (see AB4/p220): only 0 pixels in neighborhood means 1 zero region
        else:
            n_str=bin(n)[2:]
            n_str=(8-len(n_str))*'0'+n_str           # bit pattern in positions 0...7 around center pixel
            n_iarr=np.zeros(8,'int8')
            for i in range(8):
                if n_str[i]=='1': n_iarr[i]=1;
            delta_n_str=n_iarr-np.roll(n_iarr,1)
            idx_m1=delta_n_str==-1
            tabZeroRegions[n]=np.sum(idx_m1)         # number of zero regions for neighborhood n
        #print("n=",n,n_iarr, delta_n_str,tabZeroRegions[n])
    # (ii) get inner nodes: filter with kernel K and do lookup in tabZeroRegions
    im_filtered=cv2.filter2D(np.array(im_binary,'uint8'),cv2.CV_8U,K)  # compute array where im_filtered[i,j]=number n of neighborhood of pixel (i,j)
    im_n_zero_regions=tabZeroRegions[im_filtered[1:-1,1:-1]]           # im_n_zero_regions[i,j] is number of zero-regions around pixel (i,j); rake only inner regions without padding
    return im_n_zero_regions                         # return result

def skeleton_inner_leaf_nodes(im_skeleton):
    """ 
    extract inner nodes and leaf nodes from skeleton
    Inner Nodes are defined as branching points of the skeleton graph
    Leaf Nodes are defined as end points of the skeleton graph
    Assuming that the skeleton has pixel width 1 such that removing one pixel from the skeleton would destroy connectedness (which is not fulfilled by all skeleton algorithms!) then it holds:
       skeleton pixel is inner node  <==> n_zero_regions >= 3
       skeleton pixel is leaf node   <==> n_zero_regions == 1
    For further details of algorithm see AB4/p221 (Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany, December 2020)
    :param im_skeleton: skeleton image (binary)
    :returns im_innernodes: binary image of same size as im_skeleton, where each 1-pixel corresponds to an inner node of the skeleton graph
    :returns im_leafnodes: binary image of same size as im_skeleton, where each 1-pixel corresponds to an leaf node of the skeleton graph
    """ 
    im_nregions=zeroregions_in_neighborhood(im_skeleton)  # compute for each pixel the number of surrounding zero-regions
    im_innernodes=np.array(np.logical_and(im_skeleton>0,im_nregions>=3),'uint8')
    im_leafnodes =np.array(np.logical_and(im_skeleton>0,im_nregions==1),'uint8')
    return im_innernodes,im_leafnodes

def getSkeletonLength(im_skel,distance,im_leafnodes=None):
    """ 
    Compute skeleton length as sum of pixel-to-pixel Euclidean distances 
    Application example: estimate crack lengths based on its skeleton
    For details of the algorithm see AB4/p222, Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany, 20/02/2021
    :param im_skel: binary skeleton image
    :param distance: distance matrix of skeleton (see skeletonize)
    :param im_leafnodes: if not None, then compute also the total skeleton length, including the distances of leaf nodes to the background area (see AB4/p222)
    :returns skel_len: skeleton length
    :returns skel_len_total: total skeleton length, including distances of leafnodes to background area
    """ 
    sqrt2=np.sqrt(2)
    # (i) define 3x3 kernel that evaluates Euklidean distance from central pixel to each neighboring pixel (see AB4/p222)
    K=np.array([[sqrt2,1.0,sqrt2],
                [1.0  ,0  , 1.0 ],
                [sqrt2,1.0,sqrt2]],'float32')
    # (ii) convolve im_skel with kernel K
    im_filtered=cv2.filter2D(np.array(im_skel,'float32'),cv2.CV_32F,K)  # compute array where im_filtered[i,j]=distances from Pixel (i,j) to neighboring pixels
    cracklen=0.5*np.sum(np.multiply(im_skel,im_filtered))               # sum over distances of all skeleton pixels; divide by two as each path segement is counted twice!
    # (iii) compute total length, including leaf-node-to-background distances? (see AB4/p222)
    if im_leafnodes is None:
        return cracklen
    else:
        cracklen_total=cracklen+np.sum(np.multiply(im_leafnodes,distance))  # add distances of each leaf node to background area 
        return cracklen_total,cracklen

def getDist2Backgrnd_quantiles(im_foregrnd_subset,distance,quantiles=[0,0.01,0.1,0.5,1],im_leafnodes=None,flagCircleLeaf=1):
    """ 
    Compute quantiles of the distance-to-background distribution for foreground pixels in imForegrnd
    Application example: estimate width distribution of a crack from its skeleton and the distance values to background (see skeletonize) 
    For details of the algorithm see AB4/p223, Andreas Knoblauch, HS Albstadt-Sigmaringen, Germany, 20/02/2021
    :param im_foregrnd_subset: binary image being typically a subset of the foreground pixels (e.g., the skeleton of a crack region) 
    :param distance: distance matrix (contains for each foreground pixel the minimum distance to the background area)
    :param quantiles: list of quantiles for which the corresponding distances are computed 
    :param flagCircleLeaf: if >0 then a circular leaf closure is assumed (otherwise a trigonal closure); see AB4/p223 for details
    :param im_leafnodes: if not None, then correct distance distribution for skeleton leaf nodes:
                  - leaf nodes are skeleton end points
                  - depending on the skeleton algorithm, the skeleton leaf nodes may not be on the foreground/background border, but in the inner area of the foreground region!
                  - to correct this one may include all pixels on the line from leaf nodes to background and their distances (see AB4/p223 for further details)
    :returns d_quantiles: distance quantiles,i.e., d_quantiles[i] is the distance of the quantiles[i]*n largest distance of im_foregrnd_subset, where n is the pixel number of im_foregrnd_subset
    :returns quantiles: quantiles parameter (in case default quantiles are used)
    """ 
    d_list=distance[np.multiply(im_foregrnd_subset,distance)>0]          # list of distances >0, that is, list of skeleton distances to background in orgiginal image
    if not im_leafnodes is None:
        lfd_list=distance[np.multiply(im_leafnodes,distance)>0]          # list of leafnode distances to background
        if flagCircleLeaf<=0:                                            # for triangular closure
            for lfd in lfd_list:                                         # add distances d=s for s=1,...,lfd
                d_list=np.concatenate((d_list,range(1,int(round(lfd))))) # add distances to background for line from leaf node to background area in 1-pixel-steps (is only approximation; see AB4/p223)
        else:
            for lfd in lfd_list:
                s=np.array(range(1,int(round(lfd))),'float')             # s=[1,2,...,lfd]
                s=np.sqrt(lfd*lfd-np.multiply(s,s))                      # for circular closure add distances d=sqrt(ldf^2-s^2), see AB2/p223
                d_list=np.concatenate((d_list,s))                        # concatenate with distance list
    d_sorted=-np.sort(-d_list)                                           # sort in descending order
    n=len(d_sorted)                                                      # number of distance samples
    d_quantiles=[d_sorted[min(n-1,int(round(n*q)))] for q in quantiles]  # get distance quantiles
    return d_quantiles, quantiles


