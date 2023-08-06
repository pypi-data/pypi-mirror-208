#!/usr/bin/python
# -*- coding: utf-8 -*-
     
import os.path,sys,inspect, copy

def search_path(fname,paths=None):                   
    '''
    # if fname does not exist then try also paths in parameter paths and fname relative to module 
    '''
    # (i) ensure that path is a list
    if paths is None:
        paths=[]
    elif not isinstance(paths,list):
        paths=[paths]
    # (ii) append empty path (in order to search first to fname)
    paths = [""]+paths
    # (iii) append callers module paths to paths
    frame=inspect.currentframe()
    caller_paths=[]
    while not frame is None:
        code=frame.f_code
        co_filename = code.co_filename
        dr,fn = os.path.split(co_filename)
        caller_paths = [os.path.abspath(dr)]+caller_paths
        frame=frame.f_back
    paths = paths + caller_paths
    # (iv) now scan paths until file exists
    #print "scanning paths ", paths
    fname_result=None
    for p in paths:
        fname_result=os.path.join(p,fname)
        if os.path.exists(fname_result):
            break
    if(fname_result is None):
        print("supy.utilities.search_path: Cannot find file ", fname, " in paths ", paths, " !")
        fname_result=fname        # cannot find any better than fname
    return fname_result
        

def parseStringAsList(s,eltype='int',res_default=None): 
    """
    return string s as a list of elements from eltype useful to decode list attributes '[1,2,3,4]' which are stored as strings in the database tables,
    but should be transformed again as list of numerical elements after a query
    e.g., parseStringAsList('[1,2,3,4]','int') returns a integer list [1,2,3,4]
    eltype may be either 'int', 'float', 'string', 'binary' (or 'bool')
    in case of an excpetion use res_default as result of the transformation...
    """
    try:
        s=s.strip()    # remove white space from left and right
        s=s.lstrip('[')  # remove opening brackets from left
        s=s.rstrip(']')  # remove closing brackets form right
        sl = s.split(',')
        res=[]
        if eltype in ['int','integer','float','double','binary','bool','boolean']:            
            res=[float(ss.translate({ord(i):None for i in "'"})) for ss in sl]
            if eltype in ['int','integer','binary','bool','boolean']:
                res=[int(round(f)) for f in res]
        else:
            if eltype in ['string','text','str','txt']:
                res=[ss.strip() for ss in sl]           # remove white space (at beginning and ending of the substring)
                res=[ss.strip("'") for ss in sl]        # remove string delimiters (at beginning and ending of the substring)
    except ValueError as e:
        if(not res_default is None): 
            res=res_default
            print("Warning: ValueError in supy.utilities.parseStringAsList(...) for string s=",s,"eltype=",eltype,". Return default result res_default=",res_default)
        else:
            raise e
    return res


def asNumber(s,eltype='int',res_default=0): 
    """
    return string s as a single number of type eltype (int, float, bool, etc.)
    if error occurs return res_default
    e.g., asNumber('234','int')=234
          asNumber('234','float')=234.0
          asNumber('abcds','int',res_default=0)=0
    """
    n=res_default
    try:
        n=float(s)
        if eltype in ['int','integer','binary','bool','boolean']:
            n=int(round(n))
        if eltype in ['binary','bool','boolean']:
            n=bool(n)
    except ValueError as e:
        if(not res_default is None): 
            n=res_default
            print("Warning: ValueError in supy.utilities.asNumber(...) for string s=",s,"eltype=",eltype,". Return default result res_default=",res_default)
        else:
            raise e
    return n


def resource_path_pyinstaller(relative_path, default_path=None):  
    """
    transfers a relative path into an absolute path using PyInstallers _MEIPASS 
    """
    try:
        base_path = sys._MEIPASS    # PyInstaller creates a temp folder and stores path in _MEIPASS
    except Exception:
        if not default_path is None:
            base_path=default_path
        else:
            base_path = os.getcwd()     # previously: os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getAllFilenamesInFolder(path_to_folder,filetypes=['.png','.PNG','.jpg','.JPG','.tif','.TIF'],flagFullPaths=0):
    """
    get list of all filenames of desired types in the folder
    :param path_to_folder: path to the folder of the images
    :param filetypes: postfixes of the files to be selected
    :param flagFullPaths: If >0 then return list of full paths (pathtofolder+fname)
    :returns filelist: list of all filenames
    """
    filelist_all = os.listdir(path_to_folder)    # get list of all files in directory
    #print("filelist_all=\n",filelist_all)
    filelist = []
    for f in filelist_all:
        filename, fileextension = os.path.splitext(f)
        if fileextension in filetypes:
            if flagFullPaths>0:
                filelist=filelist+[os.path.join(path_to_folder,f)]
            else:
                filelist=filelist+[f]
    return filelist
    
if __name__ == '__main__':
    pass

