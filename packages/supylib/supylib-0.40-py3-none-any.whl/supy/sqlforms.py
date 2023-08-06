#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
from supy.sqldatabase import *
from supy.forms3 import *
from supy.utilities import *
from copy import *
import tkinter.messagebox
import tkinter.filedialog
from PIL import Image, ImageTk, ImageDraw

##################################################################################################################################################################
##################################################################################################################################################################
# Part I: SQLListbox and related classes and procedures:
#          classes: SQLListbox, SQLListbox_config, SQLListboxForm,  
##################################################################################################################################################################
##################################################################################################################################################################

"""
getUniqueListOfPreconditions(pcols,pvals,inherited_preconditions,tables):making list of preconditions (list of columns names pcols and associated values pvals) unique
parameters: inherited_preconditions: inherited preconditions in format [(tab1.col1,val1),(tab2.col2,val2),...]
            pcols,pvals : lists of additional column values pairs
returns: unique lists of cond_cols, cond_vals
"""
def getUniqueListOfPreconditions(pcols,pvals,inherited_preconditions,tables,join_on=None,sweeps=3):
    str_error = 'AssertionError in getUniqueListOfPreconditions(pcols,pvals) for pcols='+str(pcols)+', pvals='+str(pvals)+ " : "
    assert isinstance(pcols,list) and isinstance(pvals,list) and len(pcols)==len(pvals), str_error + "pcols and pvals must be lists of equal length!"
    # (i) use inherited preconditions from self.conditioned_on
    cols_cond1=[c[0] for c in inherited_preconditions]
    vals_cond1=[c[1] for c in inherited_preconditions]
    # (ii) add current pre-selections pcols,pvals
    cols_cond1=cols_cond1+pcols
    vals_cond1=vals_cond1+pvals
    # (iii) copy entries according to join_on (only one sweep)
    if join_on!=None:
        for sw in range(sweeps):    # iterate finding transitive hull
            lut={cols_cond1[i]:vals_cond1[i] for i in range(len(cols_cond1))}     # dict for mapping column names to values
            for i in range(len(join_on)):
                assert "=" in join_on[i], str(i)+"-th entry of join_on should be of form 'table.column'!"
                e=join_on[i]
                splt=e.split("=")
                col0,col1=splt[0],splt[1]
                if (col0 in lut) and not (col1 in lut): 
                    cols_cond1,vals_cond1=cols_cond1+[col1], vals_cond1+[lut[col0]]
                elif (col1 in lut) and not (col0 in lut):
                    cols_cond1,vals_cond1=cols_cond1+[col0], vals_cond1+[lut[col1]]
    # (iv) restrict to valid tables and make unique!
    cols_cond,vals_cond=[],[]
    for i in range(len(cols_cond1)):
        assert "." in cols_cond1[i], str(i)+"-th entry of pcols should be of form 'table.column'!"
        tc=cols_cond1[i]
        splt=tc.split(".")
        cols_only=splt[1]     # do not include table name
        tab_only =splt[0]     # only table name
        if(tab_only in tables) and not(tc in cols_cond):   # verify that table is valid and tc is unique
            cols_cond=cols_cond+[tc]
            vals_cond=vals_cond+[vals_cond1[i]]
    # (v) return data
    return cols_cond,vals_cond 

"""
getPreconditions4tables(pcols,pvals,tables):filter preconditions for tables (i.e., include only preconditions with pcols that occur in tables) 
"""
def getPreconditions4tables(pcols,pvals,tables):
    str_error = 'AssertionError in getPreconditions4tables(pcols,pvals,tables) for pcols='+str(pcols)+', pvals='+str(pvals)+', tables='+str(tables)+ " : "
    assert isinstance(pcols,list) and isinstance(pvals,list) and len(pcols)==len(pvals), str_error + "pcols and pvals must be lists of equal length!"
    assert isinstance(tables,list) , str_error + "tables must be a list of strings"
    # filter preconditions to tables in parameter tables
    c,v = [],[]
    for i in range(len(pcols)):
        assert "." in pcols[i], str(i)+"-th entry of pcols should be of form 'table.column'!"
        tc=pcols[i]
        splt=tc.split(".")
        cols_only=splt[1]     # do not include table name
        tab_only =splt[0]     # only table name
        if(tab_only in tables) and not(tc in c):   # verify that table is valid and tc is unique
            c=c+[tc]
            v=v+[pvals[i]]
    return c,v

"""
default function for formatting all column values of a table row in a single string (for displaying in a listbox)
is usually passed to SQLListbox constructor (see there...)
"""
def colvals2str_default(vals,cols_format=None,sep=' | '):
    #print("colvals2str_default: vals=",vals," cols_format=",cols_format)
    if cols_format==None:
        # no special formatting
        s = sep.join(vals)
    else: 
        n=len(vals)
        if isinstance(cols_format,str):
            # use one formatting string for all vals
            cols_format_split=cols_format.split(':')
            frm    = n*[cols_format_split[0]]    # format strings for each column value
            maxlen = n*[cols_format_split[1]]    # maximal width for each column value
        else:
            # individual formatting strings for each val
            assert len(cols_format)==n, "List parameters vals and cols_format must have same length!"
            # initialize with default values
            frm=n*['']
            maxlen = n*[-1]
            # set specified values
            for i in range(n):
                if cols_format[i]!=None:
                    splt = cols_format[i].split(':')
                    assert (len(splt)>0) and (len(splt)<3), "Formating parameter cols_format["+str(i)+"] has wrong format!"
                    frm[i]=splt[0]
                    if (len(splt)>1) and (splt[1]!=''): maxlen[i]=splt[1]
        # do formatting
        for i in range(n): 
            assert vals[i]!=None, "undefined column value '" + str(vals[i]) + "' for vals=" + str(vals) + ", cols_format=" + str(cols_format) \
                             + "!\nYou probably have forgotten to define default values in a SQL table using an SQLListbox!" 
        vals_formatted_raw = ['{0:{1}}'.format(vals[i],frm[i]) for i in range(n)]    # raw formatting 
        #print("vals_formatted raw=", vals_formatted_raw)
        for i in range(n): 
            if maxlen[i]==-1: 
                maxlen[i]=len(vals_formatted_raw[i])                                 # set default values for max length
        vals_formatted = [vals_formatted_raw[i][:int(maxlen[i])] for i in range(n)]  # clip strings 
        #print("vals_formatted=", vals_formatted)
        s = sep.join(vals_formatted)
        #print("s=",s)
    return s

"""
default callback function that is called after selecting a listbox item 
parameters:
   - selected_data_idx : index of listbox
   - selected_data     : selected data record (list of data fields)
   - selected_data_str : string-representation of selected_data (as appeared in listbox)
"""
def callback_select_default(selected_data_idx,selected_data,selected_data_str):
    pass


################################################################################################
# SQLListbox_config
# provides parameters for SQLListbox 
################################################################################################
class SQLListbox_config:
    tables = None
    join_on = None
    cols   = None
    cols_format = None
    cols_sortbutton = None
    cols_sortbutton = None
    where = None
    where_init = None
    labeltext = None
    colvals2str = colvals2str_default
    sep = ' | '
    width = 20
    height = 10
    lbfont = ('courier',12,'normal')
    callback_select = callback_select_default
    mode_multiselect = False
    ref_image = None   # or format [table, key, idx_col_key, idx_col_fname, col_fname, im_size_x, im_size_y] where idx_col_key _or_ idx_col_fname must be specified!

###################################################################################################
# SQLListbox
# provides Listbox Frame for choosing a row (or usually a key) from an SQL table
# where additional information is displayed 
# by de-referenceing keys by natural joins of tables
# Parameters:
#   parent      : parent widget
#   sqldatabase : sqldatabase
#   cfg         : Configuration structure that contains all paramateres listed below
#                 (the may be overridden by inline parameters in the constructor)
#   tables      : tables for making a join 
#                 e.g., tables=['students', 'exams']
#   join_on     : list of join expressions (len is 1 smaller than tables), 
#                 e.g., ['students.id=exams.id_student']
#   cols        : columns (of natural join) which should be displayed in a list item,
#                 e.g., cols=['students.key', 'students.name', 'exam.name', 'exam.grade'] 
#   cols_format   : column format specification for displaying the values of each column
#                   - if cols_format==None then no special formatings are done 
#                   - if cols_format='formatstr:maxwidth' then all columns are formatted 
#                     according to formatstr with maximal column width of maxwidth
#                     e.g., cols_format='10s:15' means that column values are formatted as 
#                           strings with a minimal width of 10 and a maximal width of 15
#                   - if cols_format is a list then cols_format[i] refers to the i-the value
#                 Example: cols_format=[None, ':15' ,'9.2f', '10s:10', '10s:15'] specifies 
#                          - cols_format[0]: no special formatting for value 0 
#                          - cols_format[1]: formating as string with a maximal length of 15 (no info loss) 
#                          - cols_format[2]: formatting as a 9.2 float 
#                          - cols_format[3]: formatting as string with exactly 10 characters 
#                          - cols_format[4]: formatting as string with minimal 10 and maximal 15 chars
#   cols_sortbutton : column names as displayed on listbox buttons to specify sorting order,
#                     e.g., cols_sortbutton=['key','name','exam','grade'],
#                       - must have same length as cols
#                       - If cols_sortby==None then it is assumed cols_sortby=cols 
#                         (i.e., then the buttons have the full column names)
#   where       : where-clause imposing constrainst on the selected columns
#                 e.g., 'exam.grade<=4.0'
#                   - if where==None then no constraints are imposed on the selection,
#   where_init  : where-clause selecting the data item for initial activation/selection
#                 e.g., 'students.key==123 AND exam.name=='Maths'
#                   - if init-where==None then the first data item is selected initially
#   labeltext   : text on label on top of the listboxframe
#   colvals2str : function with format colvals2str(vals,cols_format=None,sep='|') 
#                 to transform a list of columnvalues to a string-type data item 
#                 for displaying as a listbox item
#                 parameters: 
#                   vals        : list of column values
#                   sep         : separater symbol between columns
#                   cols_format : see parameter cols_format...
#   sep : separation symbol between columns in a listbox entry (e.g., ' | ')
#   width, height : width and height of listbox (in chars)
#   lbfont : font for listbox, e.g., ('courier',12,'normal')
#   mode_multiselect: if True then enable selection of multiple list items (otherwise single item)
#   ref_image : If != None then an image (of the first selected item) will be displayed; 
#               format ref_image = [table, key, idx_col_key, idx_col_fname, col_fname, im_size_x, im_size_y] 
#               where idx_col_key _or_ idx_col_fname must be specified!
#   callback_select: function that will be called after selecting an item
#   conditioned_on: list [(table.colum,value),...] which preconditions on records to be displayed    
###################################################################################################
class SQLListbox(Frame):
    """
    Default constructor
    """
    def __init__(self, parent, sqldatabase, cfg=SQLListbox_config, \
                 tables=None, join_on=None, cols=None, \
                 cols_format=None, cols_sortbutton=None, where=None, where_init=None, \
                 labeltext=None, colvals2str=None, sep=None, \
                 width=None, height=None, lbfont=None, mode_multiselect=None, callback_select=None, ref_image=None, conditioned_on=[], catch_focus=True):
        Frame.__init__(self,parent)
        self.sqldatabase = sqldatabase
        # (i) basic initialization by cfg (may be overridden by inline parameters...)
        if tables          ==None : tables          =cfg.tables
        if join_on         ==None : join_on         =cfg.join_on
        if cols            ==None : cols            =cfg.cols
        if cols_format     ==None : cols_format     =cfg.cols_format
        if cols_sortbutton ==None : cols_sortbutton =cfg.cols_sortbutton
        if where           ==None : where           =cfg.where
        if where_init      ==None : where_init      =cfg.where_init
        if labeltext       ==None : labeltext       =cfg.labeltext
        if colvals2str     ==None : colvals2str     =cfg.colvals2str
        if sep             ==None : sep             =cfg.sep
        if width           ==None : width           =cfg.width
        if height          ==None : height          =cfg.height
        if lbfont          ==None : lbfont          =cfg.lbfont
        if mode_multiselect==None : mode_multiselect=cfg.mode_multiselect
        if callback_select ==None : callback_select =cfg.callback_select
        if ref_image       ==None : ref_image       =cfg.ref_image
        self.tables          = tables
        self.join_on         = join_on
        self.cols            = cols
        self.cols_format     = cols_format
        self.cols_sortbutton = cols_sortbutton
        self.where           = where
        self.where_init      = where_init
        self.labeltext       = labeltext
        self.colvals2str     = colvals2str
        self.sep             = sep
        self.width           = width
        self.height          = height
        self.lbfont          = lbfont
        self.mode_multiselect= mode_multiselect
        self.callback_select = callback_select
        self.ref_image       = ref_image
        c,v=getUniqueListOfPreconditions([],[],conditioned_on,self.tables,self.join_on)
        #print("conditioned_on=",conditioned_on)
        #print("c=",c,"v=",v)
        c,v=getPreconditions4tables(c,v,self.tables) 
        #print("c=",c,"v=",v,"self.tables=",self.tables, "db=",self.sqldatabase, " db.name=",self.sqldatabase.filename)
        self.conditioned_on = self.sqldatabase.getWhereClause_from_ColumnValues(self.tables,c,v) # where-clause in string format "table1.col1=val1 AND table2.col2=val2..."
        #print("Listbox: self.cond_on=", self.conditioned_on, " cond=",conditioned_on,"c,v=",c,v)
        # (ii) initialize additional data
        self.idx_cols_sortbutton = list(range(len(self.cols_sortbutton))) # indices for defining order of sorting, e.g., [0,1,2,3]
        self.asc_cols_sortbutton = ['ASC']*len(self.cols_sortbutton)      # flags whether sorting ASCending or DESCending 
        self.data = None                                          # raw data records represented by the listbox, e.g., [(1,'Müller','Mathe',2.7),(2,'Maier','English',3.3)]
        self.data_str = None                                      # string records represented by the listbox, e.g., ['1 | Müller | Mathe | 2.7', '2 | Maier | French | 1.7']
        self.selected_data_idx = None                             # most recently selected key data index, e.g., 0 representing key self.data[0]=(1,'Müller','Mathe',2.7)
        self.selected_data     = None                             # most recently selected key data, e.g., (1,'Müller','Mathe',2.7) in the previous example
        self.selected_data_str = None                             # most recently selected key data string, e.g., '1 | Müller | Mathe | 2.7' in the previous example
        # (iii) insert label and sort buttons
        mainframe=Frame(self)
        mainframe.pack(side=LEFT)
        buttonframe = Frame(mainframe)
        if labeltext!=None:
            Label(buttonframe,text=labeltext).pack(side=TOP)
        Label(buttonframe,text="sort by: ").pack(side=LEFT)
        for i in range(len(self.cols_sortbutton)):
            Button(buttonframe,text=self.cols_sortbutton[i],command=(lambda i=i: self.onSortButtonPress(i))).pack(side=LEFT)
        buttonframe.pack(side=TOP)
        # (iv) insert scrolled listbox
        sbar = Scrollbar(mainframe)
        sm=BROWSE
        if(self.mode_multiselect): sm=MULTIPLE
        self.listbox = Listbox(mainframe,relief=SUNKEN,exportselection=0,selectmode=sm)
        sbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sbar.set, width=self.width, height=self.height)
        if(self.lbfont):
            self.listbox.config(font=self.lbfont)
        sbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=BOTTOM, expand=YES, fill= BOTH)
        self.listbox.bind('<<ListboxSelect>>', self.onListboxSelect)
        # (v) set image?
        if self.ref_image!=None:
            assert isinstance(self.ref_image,(tuple,list)) and len(self.ref_image)==7, "SQLListbox.ref_image must be either None or [table, key, idx_col_key, idx_col_fname, col_fname, im_size_x, im_size_y]"+\
                " but here it is ref_image="+str(self.ref_image)
            self.ref_image_table         = self.ref_image[0]
            self.ref_image_key           = self.ref_image[1]
            self.ref_image_idx_col_key   = self.ref_image[2]
            self.ref_image_idx_col_fname = self.ref_image[3]
            self.ref_image_col_fname     = self.ref_image[4]
            self.ref_image_size_x        = self.ref_image[5]
            self.ref_image_size_y        = self.ref_image[6]
            self.imgcanvas=Canvas(self,relief=SUNKEN, width=self.ref_image_size_x, height=self.ref_image_size_y) 
            self.imgcanvas.pack(side=RIGHT, expand=YES, fill=BOTH, padx=10)
        self.setListboxKeys(catch_focus=catch_focus)

    """
    set listbox keys to current values; sort by column names in sortedby
       - if where_expr!=None then where_expr is used to get initial selection
       - otherwise old selection is maintained
    """
    def setListboxKeys(self, where_expr=None, flag_callback=True, flag_ignoreoldselection=False, conditioned_on=None, catch_focus=True):
        if conditioned_on!=None:
            # update new conditioned_on-expression? (as in constructor?)   EXPERMIMENTAL!!!! check!!!
            c,v=getUniqueListOfPreconditions([],[],conditioned_on,self.tables,self.join_on)
            c,v=getPreconditions4tables(c,v,self.tables) 
            self.conditioned_on = self.sqldatabase.getWhereClause_from_ColumnValues(self.tables,c,v) # where-clause in string format "table1.col1=val1 AND table2.col2=val2..."
        # (i) get old selection (if any) to reselect afterwards
        if(where_expr==None)or(where_expr==""): where_expr=self.where_init
        if(where_expr==None)or(where_expr==""): where_expr=self.conditioned_on
        elif((self.conditioned_on!=None)and(self.conditioned_on!="")): where_expr="("+where_expr+") AND ("+self.conditioned_on+")"
        oldselection=[]
        if(self.data_str)and(self.listbox.curselection()and not flag_ignoreoldselection): # is there already an old selection ???
            oldselection=[self.data_str[int(i)] for i in self.listbox.curselection()]
        elif (where_expr!=None):                                                                  # else: is there a where_init/where_expr clause ?where_expr!=None):
            wc=where_expr
            if(self.conditioned_on!=""): wc="("+where_expr+") AND (" + self.conditioned_on +")"
            d = self.sqldatabase.simple_select(self.cols,self.tables,joinon=self.join_on, where=wc)  # raw data
            #print("\n\nd=",d)
            #print("\nwc=",wc)
            oldselection = [self.colvals2str(di,self.cols_format,self.sep) for di in d]
            if (not self.mode_multiselect) and (len(oldselection)>0):
                oldselection = [oldselection[0]]                            # if not multiselect: just take first element of list
        #print("!!!oldsel=",oldselection, "   where_expr=", where_expr)
        # (ii) get new list data
        wc=self.where
        if(wc==None)or(wc==""): wc=self.conditioned_on
        else: wc = wc + " AND " + self.conditioned_on
        order=[self.cols[self.idx_cols_sortbutton[i]] + " " + self.asc_cols_sortbutton[self.idx_cols_sortbutton[i]] for i in range(len(self.cols_sortbutton))]
        self.data     = self.sqldatabase.simple_select(self.cols,self.tables,joinon=self.join_on, where=wc,orderby=order)  # raw data
        self.data_str = [self.colvals2str(d,self.cols_format,self.sep) for d in self.data]                    # string data
        #print("SQLListbox: self.data_str=", self.data_str)
        #print("SQLListboxc: self.data=", self.data)
        # (iii) delete old listbox data (if any) and store new ones
        self.listbox.delete(0, END)
        idx = []
        for i in range(len(self.data)):
            self.listbox.insert(END,self.data_str[i])
            if self.data_str[i] in oldselection:
                idx=idx + [i]
                #print("match idx=",idx)
        if(not self.mode_multiselect):
            if(len(idx)==0):
                idx=[0]          # in single mode select first entry
            elif(len(idx)>1):
                idx=[idx[-1]]    # if more than one element in old selection (should not be the case) then take last one...
        for i in idx:
            self.listbox.selection_set(i)
        if(len(idx)>0):
            self.listbox.activate(idx[0])
            self.listbox.see(idx[0])
        self.onListboxSelect(flag_callback=flag_callback)
        if catch_focus: self.listbox.focus_set()

    def load_image(self,fname,sizex,sizey):   # load image with filename fname and set to self.phim
        self.phim,self.draw=None,None
        if(fname):
            try:
                #self.image = Image.open(search_path(fname,self.paths_relative_to))
                self.image = Image.open(search_path(fname))
            except IOError as e:
                msg="I/O error({0}): {1}".format(e.errno, e.strerror) + "\nsupy.sqlforms.SupySQLListBox.load_image: Cannot load image " + fname + " !"
                tkinter.messagebox.showerror(title="Submit Error", parent=self, message=msg)
            else:
                dx,dy=self.image.size
                fx=abs(sizex/(1.0*max(abs(dx),1)))
                fy=abs(sizey/(1.0*max(abs(dy),1)))
                f=min(fx,fy)
                imsize_new=[int(f*dx+0.5),int(f*dy+0.5)]
                #self.image.thumbnail(imsize_new, Image.ANTIALIAS)
                self.image=self.image.resize(imsize_new, Image.ANTIALIAS)
                self.draw = ImageDraw.Draw(self.image)
                self.phim = ImageTk.PhotoImage(self.image)
        return self.phim,self.draw

    def onListboxSelect(self,evt=None,flag_callback=True):
        sels = self.listbox.curselection()
        self.selected_data_idx = [int(i) for i in sels] 
        self.selected_data     = [self.data[i] for i in self.selected_data_idx]
        self.selected_data_str = [self.data_str[i] for i in self.selected_data_idx]
        if self.ref_image!=None and len(self.selected_data)>0:
            # (i) get filename of image
            fname=None
            if self.ref_image_idx_col_fname!=None:
                fname=self.selected_data_str[self.ref_image_idx_col_fname]
            else:
                assert self.ref_image_idx_col_key!=None, "SQLListBox.onListboxSelect: self.ref_image="+str(self.ref_image)+" should be in format [table, key, idx_col_key, idx_col_fname, im_size_x, im_size_y]"+\
                                                    ", where idx_col_key or idx_col_fname must be given (!=None) to identify the filename of the image to be displayed!"
                #print("col_key=",self.ref_image_idx_col_key)
                #print("selected-data=",self.selected_data)
                val_key=self.selected_data[0][self.ref_image_idx_col_key]
                wc=self.sqldatabase.getWhereClause_from_ColumnValues([self.ref_image_table],[self.ref_image_key],[val_key]) 
                #print("wc=",wc)
                d = self.sqldatabase.simple_select([self.ref_image_col_fname],self.ref_image_table, where=wc)  # raw data
                #print("d=",d)
                assert d!=None and len(d)==1, "SQLListBox.onListboxSelect: Cannot uniquely determine filename from d="+str(d)
                fname=d[0][0]
                # (ii) load image
                self.load_image(fname,self.ref_image_size_x,self.ref_image_size_y)
                # (iii) draw image on canvas
                if(self.imgcanvas!=None):
                    self.imgcanvas.delete('all');        
                    self.imgcanvas.configure(width=self.ref_image_size_x, height=self.ref_image_size_y)
                    if(self.phim!=None):
                        self.imgcanvas.create_image(0,0,image=self.phim,anchor=NW)
        if (self.callback_select != None) and (flag_callback) : 
            self.callback_select(self.selected_data_idx, self.selected_data, self.selected_data_str)
        #print("!!!!!!!onListBoxSelect", self.selected_data_idx, self.selected_data, self.selected_data_str)

    def onSortButtonPress(self,i):
        if self.idx_cols_sortbutton[0]!=i:
             # if pressed for the first time then change sorting order
             self.idx_cols_sortbutton = [i]+self.idx_cols_sortbutton[1:]
        else:
             # otherwise change ASC/DESC flag
             if self.asc_cols_sortbutton[i]=='ASC':
                 self.asc_cols_sortbutton[i]='DESC'
             else:
                 self.asc_cols_sortbutton[i]='ASC'
        #print ("self.idx_cols_sortbutton=", self.idx_cols_sortbutton, " i=", i)
        self.setListboxKeys()


################################################################################################
# SQLListboxForm_config
# provides parameters for SQLListboxForm 
################################################################################################
class SQLListboxForm_config(SQLListbox_config):
   button_str = ['Ok','Cancel']
   title      = 'SQLListboxForm...'  # is used only for askSQLListboxForm

########################################################################################
# SQLListboxForm
# An input form based on the SQLListbox widget
# Input parameters wrapped from SQLListboxForm (see there for details):
#    sqldatabase : sqldatabase
#    tables      : tables for making a natural join, e.g., tables=['students', 'exams'] 
#    join_on     : list of join expressions (len is 1 smaller than tables), 
#    cols        : columns to be displayed, e.g., cols=['students.key', 'students.name', 'exam.name', 'exam.grade'] 
#    cols_format : specification of display format, e.g., cols_format=[None, ':15' ,'9.2f', '10s:10', '10s:15']
#    cols_sortbutton : column names as displayed on sorting buttons, e.g., cols_sortbutton=['key','name','exam','grade']
#    where       : where-clause imposing constrainst on the selected columns, e.g., 'exam.grade<=4.0'
#    where_init  : where-clause selecting initial item, e.g., 'students.key==123 AND exam.name=='Maths'
#    labeltext   : text on label on top of the listboxframe
#    colvals2str : function of format colvals2str(vals,cols_format=None,sep='|')  
#    sep         : separation symbol between columns in a listbox entry (e.g., ' | ')
#    width, height : width and height of listbox (in chars)
#    lbfont      : font for listbox, e.g., ('courier',12,'normal')
# Additional input parameters:
#    init_pkey     : primary key index and value of the listbox entry that should be activated initially (or None)
#                    represented as tuple (idx,val) where idx and val refer to cols, 
#                    e.g., init_pkey = (0,123) specifies that initially the listbox item with students.key = 123 should be activated 
#    init_item_str : alternative way to specify initially active listbox item if there is no single primary key (then use init_pkey==None)
#                    generate this str using function colvals2str...
#    button_str    : labels on buttons, e.g., button_str=['Ok', 'Cancel']
# Output parameters:
#    use data_selected,data_selected_str=getSelection() to obtain selected data (as list of values or as data item string) 
########################################################################################
class SQLListboxForm:                # add non-modal form box
    def __init__(self, parent, sqldatabase, cfg=SQLListboxForm_config, \
                 tables=None, join_on=None, cols=None, \
                 cols_format=None, cols_sortbutton=None, where=None, where_init=None, \
                 labeltext=None, colvals2str=None, sep=None, \
                 width=None, height=None, lbfont=None, \
                 button_str = None):           # for parameters see SQLListboxForm_config
        # basic initialization
        if button_str==None : 
            #print("cfg=", cfg)
            #print("cfg.button_str=", cfg.button_str)
            button_str = cfg.button_str
        self.result    =None
        self.result_str=None
        self.box = Frame(parent)                             # container frame
        self.box.pack(expand=YES, fill=X)
        # create listbox 
        self.sqllb = SQLListbox(self.box,sqldatabase,cfg,tables,join_on,cols,cols_format,cols_sortbutton,where,where_init,labeltext,colvals2str,sep,width,height,lbfont)
        self.sqllb.pack(side=TOP, expand=Y, fill=X)      
        # create control button frame
        self.buttonframe = Frame(self.box)
        #print("cfg=",cfg)
        Button(self.buttonframe,text=button_str[1],command=self.onCancel).pack(side=RIGHT)
        Button(self.buttonframe,text=button_str[0],command=self.onSubmit).pack(side=RIGHT)
        self.box.master.bind('<Return>', (lambda event: self.onSubmit()))
        self.buttonframe.pack(side=BOTTOM)

    def onSubmit(self):                                      # override this if necessary
        self.result = self.sqllb.selected_data
        self.result_str = self.sqllb.selected_data_str
        self.box.destroy()
     
    def onCancel(self):                                      # override if needed
        self.result=None
        self.result_str=None
        self.box.destroy()
        
def askSQLListboxForm(sqldatabase, cfg=SQLListboxForm_config, \
                      tables=None, join_on=None, cols=None, \
                      parent=None, title=None, \
                      cols_format=None, cols_sortbutton=None, where=None, where_init=None, \
                      labeltext=None, colvals2str=None, sep=None, \
                      width=None, height=None, lbfont=None, \
                      button_str = None):  # for parameters see SQLListboxForm_config
    if title==None: title=cfg.title
    top=Toplevel(parent)
    top.grab_set()                         # make window modal (i.e., redirect all inputs from parent window to listbox dialog)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SQLListboxForm(top,sqldatabase,cfg,tables,join_on,cols,cols_format,cols_sortbutton,where,where_init,labeltext,colvals2str,sep,width,height,lbfont,button_str) 
    top.wait_window(f.box)
    top.destroy()
    return f.result, f.result_str

##################################################################################################################################################################
##################################################################################################################################################################
# Part II: SupySQLntomTextFrame and related classes
##################################################################################################################################################################
##################################################################################################################################################################

class SupySQLntomTextFrame_cfg(SupyTextFrame_cfg):
    tables = None    # e.g., ['citizenshipofstudent','student','citizenship']
    join_on = None   # e.g., ['citizenshipofstudent.key_student=student.key', 'citizenshipofstudent.key_citizenship=citizenship.key']
    cols   = None    # e.g., ['citizenship.key','citizenship.citizenship']
    cols_format = None # e.g., ['5d','10s:10']
    cols_sortbutton = None # e.g., ['ID-C','CITIZENSHIP']
    where = None
    where_init = None
    colvals2str = colvals2str_default
    sep = ' | '
    text_sep = '\n'     # or "; "
    button_str = None   # e.g., ['Ok','Cancel']
    title      = None   # e.g., 'Staatsbürgerschaft von Studenten'
    

class SupySQLntomTextFrame(Frame):
    def __init__(self,sqldatabase,parent=None,cfg=SupySQLntomTextFrame_cfg, readonly=None, height=None, width=None, wrap=None, catch_focus=None, textvariable=None,\
                 tables=None, join_on=None, cols=None, \
                 cols_format=None, cols_sortbutton=None, where=None, where_init=None, \
                 colvals2str=None, sep=None, text_sep=None):
        Frame.__init__(self,parent)
        # (i) basic initialization by cfg (may be overridden by inline parameters...)
        self.stf=SupyTextFrame(self,'',cfg,readonly,height,width,wrap,catch_focus,textvariable)
        self.stf.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self.sqldatabase = sqldatabase
        if tables          ==None : tables          =cfg.tables
        if join_on         ==None : join_on         =cfg.join_on
        if cols            ==None : cols            =cfg.cols
        if cols_format     ==None : cols_format     =cfg.cols_format
        if cols_sortbutton ==None : cols_sortbutton =cfg.cols_sortbutton
        if where           ==None : where           =cfg.where
        if where_init      ==None : where_init      =cfg.where_init
        if colvals2str     ==None : colvals2str     =cfg.colvals2str
        if sep             ==None : sep             =cfg.sep
        if text_sep        ==None : text_sep        =cfg.text_sep
        self.tables          = tables
        self.join_on         = join_on
        self.cols            = cols
        self.cols_format     = cols_format
        self.cols_sortbutton = cols_sortbutton
        self.where           = where
        self.where_init      = where_init
        self.colvals2str     = colvals2str
        self.sep             = sep
        self.text_sep        = text_sep
        # (ii) initialize additional data
        self.idx_cols_sortbutton = list(range(len(self.cols_sortbutton))) # indices for defining order of sorting, e.g., [0,1,2,3]
        self.asc_cols_sortbutton = ['ASC']*len(self.cols_sortbutton)      # flags whether sorting ASCending or DESCending 
        self.data = None                                # raw data records, e.g., [(1,'Müller','Mathe',2.7),(2,'Maier','English',3.3)]
        self.data_str = None                            # string records of the data, e.g., ['1 | Müller | Mathe | 2.7', '2 | Maier | French | 1.7']
        # (iii) insert label and sort buttons
        if(self.cols_sortbutton!=None):
            buttonframe = Frame(self)
            Label(buttonframe,text="sort by: ").pack(side=LEFT)
            for i in range(len(self.cols_sortbutton)):
                Button(buttonframe,text=self.cols_sortbutton[i],command=(lambda i=i: self.onSortButtonPress(i))).pack(side=LEFT)
            buttonframe.pack(side=TOP)
        # (iv) insert text
        self.settext()
        
    def configure(self,state=None,textvariable=None,where=None):
        if(where!=None):
            self.where=where
        self.stf.configure(state,textvariable)

    def settext(self,set_textvariable=True):    # set text according to n-to-m tables
        order=None
        if(self.cols_sortbutton):
            order=[self.cols[self.idx_cols_sortbutton[i]] + " " + self.asc_cols_sortbutton[self.idx_cols_sortbutton[i]] for i in range(len(self.cols_sortbutton))]
        self.data     = self.sqldatabase.simple_select(self.cols,self.tables,joinon=self.join_on, where=self.where,orderby=order)  # raw data
        self.data_str = [self.colvals2str(d,self.cols_format,self.sep) for d in self.data]                                         # string data
        txt='';
        for i in range(len(self.data_str)):
            if i>0: txt=txt+self.text_sep
            txt=txt+self.data_str[i]
        self.stf.settext(txt,set_textvariable)

    def gettext(self):                    # return text of text-widget
        return self.stf.gettext() 

    def onSortButtonPress(self,i):
        if self.idx_cols_sortbutton[0]!=i:
             # if pressed for the first time then change sorting order
             self.idx_cols_sortbutton = [i]+self.idx_cols_sortbutton[1:]
        else:
             # otherwise change ASC/DESC flag
             if self.asc_cols_sortbutton[i]=='ASC':
                 self.asc_cols_sortbutton[i]='DESC'
             else:
                 self.asc_cols_sortbutton[i]='ASC'
        #print ("self.idx_cols_sortbutton=", self.idx_cols_sortbutton, " i=", i)
        self.settext()


##################################################################################################################################################################
##################################################################################################################################################################
# Part III: SupySQLImageFrame and related classes
##################################################################################################################################################################
##################################################################################################################################################################

class SupySQLImageFrame_cfg(SupyImageDialog_config):
    imsize = [100,100]     # in pixels... (original clip will be scaled to this size (approx., if too large)
    readonly = False
    flagDisplayFilename = True
    data_str_init=None
    paths_relative_to=None
    flagSimpleFilenameDialog = False    # if set then only simple dialog requesting filename (no clipping etc.)
    flagDisplayEntry, widthEntry = False,10 # if flagDisplayEntry==True then display textvariable.str as Entry of width widthEntry
    refDB_img  = None   # if set then format refDB = [idx_key, table, col_key, col_filename], 
                        # i.e., idx_key is index in textvariable of image key; table is the table holding the image filenames; col_key/filename are the corresponding column names  

class SupySQLImageFrame(Frame):
    def __init__(self,sqldatabase,parent=None,cfg=SupySQLImageFrame_cfg, textvariable=None,\
                 imsize=None, readonly=None, flagDisplayFilename=None, data_str_init=None, \
                 flagDisplayEntry=None, widthEntry=None, paths_relative_to=os.getcwd()):
        # (i) basic initialization by cfg (may be overridden by inline parameters...)
        Frame.__init__(self,parent)
        self.sqldatabase=sqldatabase
        self.cfg=cfg
        self.textvariable=textvariable
        if readonly           ==None : readonly           =cfg.readonly
        if flagDisplayFilename==None : flagDisplayFilename=cfg.flagDisplayFilename
        if imsize             ==None : imsize             =cfg.imsize
        if data_str_init      ==None : data_str_init      =cfg.data_str_init
        if flagDisplayEntry   ==None : flagDisplayEntry   =cfg.flagDisplayEntry
        if widthEntry         ==None : widthEntry         =cfg.widthEntry
        if paths_relative_to  ==None : paths_relative_to  =cfg.paths_relative_to
        #if ==None :    =cfg.
        self.readonly=readonly
        self.flagDisplayFilename=flagDisplayFilename
        self.imsize=imsize
        self.data_str_init=data_str_init
        self.data_str=self.data_str_init
        self.flagDisplayEntry=flagDisplayEntry
        self.widthEntry=widthEntry
        self.paths_relative_to=paths_relative_to
        # (ii) initialize additional data
        self.phim,self.draw=None,None
        self.data_label,self.data_filename,self.data_mode,self.data_x1,self.data_x2,self.data_y1,self.data_y2=None,None,None,None,None,None,None
        self.entry=None
        if self.flagDisplayEntry:
            self.entry=Entry(self, textvariable=textvariable, width=self.widthEntry, bg="white", disabledforeground='black')
            self.entry.pack(side=TOP, expand=YES, fill=X)
            self.entry.configure(state=DISABLED)   # just for displaying, no editing possible
        self.imgcanvas=Canvas(self,relief=SUNKEN, width=self.imsize[0], height=self.imsize[1])
        self.imgcanvas.pack(side=TOP, expand=YES, fill=BOTH)
        self.label=None
        if(self.flagDisplayFilename):
            self.label=Label(self,text=self.data_str_init)
            self.label.pack(side=BOTTOM, expand=YES, fill=X)
        # (iii) set image
        self.configure(data_str=self.data_str,textvariable=textvariable)

    def configure(self,state=None,data_str=None, textvariable=None):
        #if(textvariable!=None): print("textvariable.get()=",textvariable.get())    # print bewfehl löschen!!!!!
        if(textvariable!=None): 
            self.textvariable=textvariable
            if(self.entry!=None): self.entry.configure(textvariable=textvariable)
            if(data_str!=None):
                self.textvariable.set(data_str)
            self.data_str=self.textvariable.get()
        elif(data_str!=None):
            self.data_str=data_str     # is expected to be in format 'filename' or 'Label | Filename | mode | x1 | x2 | y1 | y2'
            self.textvariable.set(data_str)
        if self.label: self.label.configure(text=self.data_str)
        # first set default values...
        self.data_label=""
        self.data_filename=None
        self.data_mode="full"
        self.data_x1=0
        self.data_x2=0
        self.data_y1=0
        self.data_y2=0
        # set true values...
        if self.data_str!=None and self.data_str!="" and self.data_str!="N.N.":
            s=self.data_str.split('|')
            assert self.cfg.refDB_img!=None or len(s)==1 or len(s)==7, "Assertion error in SupySQLImageFrame.configure(state,data_str): If cfg.refDB_img==None THEN parameter data_str='" + str(data_str) + "' must have format 'Filename' or 'Label | Filename | mode | x1 | x2 | y1 | y2' !"
            if(self.cfg.refDB_img==None):
                if(len(s)==7):
                    self.data_label   =str(s[0])
                    self.data_filename=str(s[1])
                    self.data_mode    =str(s[2])
                    self.data_x1      =int(s[3])
                    self.data_x2      =int(s[4])
                    self.data_y1      =int(s[5])
                    self.data_y2      =int(s[6])
                else:
                    self.data_filename=str(s[0])
            else:
                # get filename through reference in database
                assert self.cfg.refDB_img!=None and isinstance(self.cfg.refDB_img,(list,tuple)) and len(self.cfg.refDB_img)==4, "SupySQLImageFrame.configure: self.cfg.refDB_img="+\
                                            str(self.cfg.refDB_img)+" should be in [idx_key, table, col_key, col_filename]"+\
                                            ", to identify the filename of the referenced image to be displayed!"
                idx_key     =self.cfg.refDB_img[0]
                table       =self.cfg.refDB_img[1]
                col_key     =self.cfg.refDB_img[2]
                col_filename=self.cfg.refDB_img[3]
                #print("col_key=",self.ref_image_idx_col_key)
                #print("selected-data=",self.selected_data)
                assert isinstance(idx_key,int) and idx_key>=0 and idx_key<len(s), \
                    "SupySQLImageFrame.configure: self.cfg.refDB_img[0]=idx_key=" + str(idx_key) + " must be integer between 0 and len(s)=" + str(len(s)) + "!"
                val_key=s[self.cfg.refDB_img[0]]   # key value of image  
                wc=self.sqldatabase.getWhereClause_from_ColumnValues([table],[col_key],[val_key]) 
                #print("wc=",wc)
                d = self.sqldatabase.simple_select([col_filename],[table], where=wc)  # raw data
                #print("d=",d)
                assert d!=None and len(d)==1, "SupySQLImageFrame.configure: Cannot uniquely determine filename from d="+str(d)
                self.data_filename=d[0][0]
        self.setimage()

    def load_image(self,fname,sizex,sizey):   # load image with filename fname and set to self.phim
        self.phim,self.draw=None,None
        if(fname):
            try:
                self.image = Image.open(search_path(fname,self.paths_relative_to))
            except IOError as e:
                msg="I/O error({0}): {1}".format(e.errno, e.strerror) + "\nsupy.sqlforms.SupySQLImageFrame.load_image: Cannot load image " + fname + " !"
                tkinter.messagebox.showerror(title="Submit Error", parent=self, message=msg)
            else:
                if self.data_mode!="full":
                    self.image=self.image.crop([self.data_x1, self.data_y1, self.data_x2, self.data_y2])
                dx,dy=self.image.size
                fx=abs(sizex/(1.0*max(abs(dx),1)))
                fy=abs(sizey/(1.0*max(abs(dy),1)))
                f=min(fx,fy)
                imsize_new=[int(f*dx+0.5),int(f*dy+0.5)]
                #self.image.thumbnail(imsize_new, Image.ANTIALIAS)
                self.image=self.image.resize(imsize_new, Image.ANTIALIAS)
                self.draw = ImageDraw.Draw(self.image)
                self.phim = ImageTk.PhotoImage(self.image)
        return self.phim,self.draw

    def setimage(self):
        # (i) load image
        self.load_image(self.data_filename,self.imsize[0],self.imsize[1])
        # (ii) draw image on canvas
        if(self.imgcanvas!=None):
            self.imgcanvas.delete('all');        
            self.imgcanvas.configure(width=self.imsize[0], height=self.imsize[1])
            if(self.phim!=None):
                self.imgcanvas.create_image(0,0,image=self.phim,anchor=NW)

    def get(self):
        return self.data_str

##################################################################################################################################################################
##################################################################################################################################################################
# Part IV: SupySQLForm and related classes
##################################################################################################################################################################
##################################################################################################################################################################

def displayHelpMessage_default(parent,text,cfg):
    #w=Toplevel(parent)
    #if parent: w.transient(parent)     # make window transient, e.g., minmize with parent etc.
    #w.title(cfg.help_title)
    #l=Label(w,text=text)
    #l.pack()
    #b=Button(w,text=cfg.help_buttonname,command=w.destroy)
    #b.pack()
    tkinter.messagebox.showinfo(cfg.help_title, text, parent=parent)

###############################################################################################################
# SupySQLFormFrame & SupySQLFormFrame_config
# specification of an input form for editing a SQL database table record
# 
# parameters:
# tables                : list of table names to make a join
# join_on               : list of join expressions (len is 1 smaller than tables), 
#                         e.g., tables=['t1','t2','t3'], join_on=['t1.a=t2.a', 't2.b=t3.b'] corresponds to 
#                         SELECT .... FROM t1 join t2 on t1.a=t2.a join t3 on t2.b=t3.b ...
# cols                  : list of columns to be displayed or inputed
# cols_type             : list of type indicators for cols; types can be:
#                         - 'str'/None   : default, input as single line entry 
#                         - 'textfield'  : multi-line text field
#                         - 'filename'   : include browse button for filename dialog
#                         - 'filename-dir'   : include browse button for filename-directory dialog
#                         - 'filename-image' : include browse button for filename dialog and display filename as image
#                         - 'imagefile'  : include browse button for filename dialog and image widget
#                         - 'optionlist' : list to be chosen from
#                         - 'ref'        : reference to other table(s) to choose via an SupySQLListboxForm
#                         - 'ref_ntom'   : n-to-m reference: Display of corresponding records in a read-only textfield
#                                          and possibility to open a new form via browse button
# cols_ref              : if cols_type[i]=='ref' then 
#                               - cols_ref[i] is SQLListboxForm_config reference parameters 
#                               - it is assumed that cols_ref[i].cols[0] is the foreign key
#                                 to reference additional data !!!!!
#                         if type=='optionlist' then cols_ref[i] is the list of option strings
#                         if type=='imagefile' then cols_ref[i]=imageframeconfig 
# cols_readonly         . list of (0/1) flags indicating that an entry field is read-only (1=readonly)
# cols_label            : list of labels for cols
# cols_label_pos        : list of position (x,y) or (x,y,dx,dy) for each column label
# cols_label_width      : list of label widths for each column label
# cols_label_anchor     : list of label anchors (e.g., 'w') for each column label
# cols_pos              : list of positions (x,y) or (x,y,dx,dy) for each cols entry fields
# cols_size             : list of widths or (width,height)-tuples for each cols entry fields (default height ist 1)
# cols_helptext         : list of helptext that is displayed after a help event (e.g., right-click on label)
# cols_browsebutton_pos : list of positions of the browse buttons (e.g., for type='filename' etc.) 
# select_cols           : list of columns used for selecting one table record to be edited
# select_vals           : values for the columns in select_cols 
# help_event            : define event type to be bound to input label for help text, e.g., "<Button-3>"
# help_title            : title of help window
# help_buttonname       : button text for help window
# browse_buttonname     : button text for browse buttons
# checkResults          : function that delivers True if the results (inputs of Forms) are consistent and ok,
#                         for format, see SupySQLForm_checkResults_default below...
# update_tables         : tables to be updated after completion (submit) of the form
# update_tables_pkeys   : list of primary key lists for each tables to be updated
#                         i.e., update_tables_pkeys[i] is a list of the column (as in cols) of table update_tables[i]
#                               that act as primary keys (i.e., that are used in the where-clause to identify the record
#                               to be updated)
# update_tables_cols    : for each table the columns that should actually be updated (not pkeys as they do not change...)
###############################################################################################################

"""
SupySQLForm_checkResults_default: checks if the input record is ok for commit()
Parameters:
   sqldatabase,tables,cols: as in SupySQLForm
   result_row: list of inputs (same order as cols) from the form, corresponding to one row ...
Return values:
   returns either "OK" or a string-type error message
"""
def SupySQLForm_checkResults_default(sqldatabase,tables,cols,result_row):
    return "OK"


class SupySQLFormFrame_config:
    tables                = None
    join_on               = None
    cols                  = None
    cols_type             = None
    cols_ref              = None
    cols_readonly         = None
    cols_label            = None
    cols_label_pos        = None
    cols_label_width      = 15     # may also be list
    cols_label_anchor     = 'w'    # may also be list
    cols_pos              = None
    cols_size             = 40     # may also be list
    cols_helptext         = None
    cols_browsebutton_pos = None
    cols2copy             = None   # if None all columns can be copied (e.g., by Tableeditor.on_lb_copy...); otherwise list of columns (of main table!) to be copied
    select_cols           = None
    select_vals           = None
    flagIgnoreMultipleSelections = False    # if flag set then ignore multiple selections and simply select the first in the list...
    help_event            = "<Button-3>"
    help_title            = "Help"
    help_buttonname       = "Close"
    browse_buttonname     = "Browse"
    checkResults          = SupySQLForm_checkResults_default  # function to check if inputs are valid (see SupySQLForm_checkResults_default)
    update_tables         = None                              # tables to be updated after form submission
    update_tables_pkeys   = None                              # for each table (to be updated) a list of primary keys 
    update_tables_cols    = None                              # for each table (to be updated) a list of columns to be updated
    

class SupySQLFormFrame(Frame):
    def __init__(self,parent, sqldatabase, cfg=SupySQLFormFrame_config, \
                 tables=None, join_on=None, cols=None, cols_type=None, cols_ref=None, cols_readonly=None, \
                 cols_label=None, cols_label_pos=None, cols_label_width=None, cols_label_anchor=None, \
                 cols_pos=None, cols_size=None, cols_helptext=None, cols_browsebutton_pos=None, \
                 select_cols=None, select_vals=None, help_event=None, help_title=None, help_buttonname=None, browse_buttonname=None, \
                 checkResults=None, update_tables=None, update_tables_pkeys=None, update_tables_cols=None, \
                 paths_relative_to=os.getcwd(), browse_callback=None, help_callback=displayHelpMessage_default, conditioned_on=[]):
        Frame.__init__(self,parent, bd=2, relief=GROOVE)    # formbox will have grid layout
        self.sqldatabase = sqldatabase
        self.cfg=cfg
        # (i) basic initialization by cfg (may be overridden by inline parameters...)
        if tables               ==None : tables               =cfg.tables
        if join_on              ==None : join_on              =cfg.join_on
        if cols                 ==None : cols                 =cfg.cols
        if cols_type            ==None : cols_type            =cfg.cols_type
        if cols_ref             ==None : cols_ref             =cfg.cols_ref
        if cols_readonly        ==None : cols_readonly        =cfg.cols_readonly
        if cols_label           ==None : cols_label           =cfg.cols_label
        if cols_label_pos       ==None : cols_label_pos       =cfg.cols_label_pos
        if cols_label_width     ==None : cols_label_width     =cfg.cols_label_width
        if cols_label_anchor    ==None : cols_label_anchor    =cfg.cols_label_anchor
        if cols_pos             ==None : cols_pos             =cfg.cols_pos
        if cols_size            ==None : cols_size            =cfg.cols_size
        if cols_helptext        ==None : cols_helptext        =cfg.cols_helptext
        if cols_browsebutton_pos==None : cols_browsebutton_pos=cfg.cols_browsebutton_pos
        if select_cols          ==None : select_cols          =cfg.select_cols
        if select_vals          ==None : select_vals          =cfg.select_vals
        if help_event           ==None : help_event           =cfg.help_event
        if help_title           ==None : help_title           =cfg.help_title
        if help_buttonname      ==None : help_buttonname      =cfg.help_buttonname
        if browse_buttonname    ==None : browse_buttonname    =cfg.browse_buttonname
        if checkResults         ==None : checkResults         =cfg.checkResults
        if update_tables        ==None : update_tables        =cfg.update_tables
        if update_tables_pkeys  ==None : update_tables_pkeys  =cfg.update_tables_pkeys
        if update_tables_cols   ==None : update_tables_cols   =cfg.update_tables_cols
        self.tables                = tables
        self.join_on               = join_on
        self.cols                  = [c for c in cols]
        self.cols_type             = cols_type
        self.cols_ref              = cols_ref
        self.cols_readonly         = cols_readonly
        self.cols_label            = cols_label
        self.cols_label_pos        = cols_label_pos
        self.cols_label_width      = cols_label_width
        self.cols_label_anchor     = cols_label_anchor
        self.cols_pos              = cols_pos
        self.cols_size             = cols_size
        self.cols_helptext         = cols_helptext
        self.cols_browsebutton_pos = cols_browsebutton_pos
        self.select_cols           = select_cols
        self.select_vals           = select_vals
        self.help_event            = help_event
        self.paths_relative_to     = paths_relative_to
        self.browse_callback       = browse_callback
        self.conditioned_on        = conditioned_on               # in format [(table.col,val_str),...]
        self.precondition_cols, self.precondition_vals=[],[]      # not yet preconditions (will be set by getUniqueListofPreconditions)
        self.help_callback         = help_callback
        self.help_title            = help_title
        self.help_buttonname       = help_buttonname
        self.browse_buttonname     = browse_buttonname
        self.checkResults          = checkResults
        self.update_tables         = update_tables
        self.update_tables_pkeys   = update_tables_pkeys
        self.update_tables_cols    = update_tables_cols
        # (ii) set some default parameters (if not specified)
        if self.cols_type==None:                               # defaults for cols_type
            self.cols_type=len(self.cols)*[None]
        if self.cols_ref==None:                                # defaults for cols_ref
            self.cols_ref=len(self.cols)*[None]
        if(self.cols_readonly==None)or(self.cols_readonly==0): # defaults for cols_readonly
            self.cols_readonly=len(self.cols)*[0]
        if self.cols_label==None:                              # defaults for cols_label 
            self.cols_label=self.cols
        if(self.cols_label_pos==None):                         # defaults for label/cols positions
            if(self.cols_pos==None):
                self.cols_label_pos = [(0,y) for y in range(len(self.cols))]
                self.cols_pos       = [(1,y) for y in range(len(self.cols))]
            else:
                self.cols_label_pos = [(p[0]-1,p[1]) for p in self.cols_pos] 
        else:
            if(self.cols_pos==None):
                self.cols_pos = [(p[0]+1,p[1]) for p in self.cols_label_pos]
        if(self.cols_browsebutton_pos==None):
            self.cols_browsebutton_pos = [(p[0]+1,p[1]) for p in self.cols_pos]
        if not isinstance(self.cols_label_width,list):         # make list of cols_label_width
            self.cols_label_width = len(self.cols)*[self.cols_label_width]
        if not isinstance(self.cols_label_anchor,list):        # make list of cols_label_anchor
            self.cols_label_anchor = len(self.cols)*[self.cols_label_anchor]
        if not isinstance(self.cols_size,list):               # make list of cols_size
            self.cols_size = len(self.cols)*[self.cols_size]
        # (iii) assert parameters (list sizes etc.)
        str_error = "Assertion error in SQLFormFrame.__init__ for tables " + str(self.tables) + ": "
        assert isinstance(self.cols, list), str_error+"parameter cols=" + self.cols 
        assert isinstance(self.cols_type            , list) and (len(self.cols_type            )==len(cols)), str_error+"parameter cols_type            =" + str(self.cols_type)+"; cols="+str(cols)
        assert isinstance(self.cols_ref             , list) and (len(self.cols_ref             )==len(cols)), str_error+"parameter cols_ref             =" + str(self.cols_ref)
        assert isinstance(self.cols_label           , list) and (len(self.cols_label           )==len(cols)), str_error+"parameter cols_label           =" + str(self.cols_label)
        assert isinstance(self.cols_label_pos       , list) and (len(self.cols_label_pos       )==len(cols)), str_error+"parameter cols_label_pos       =" + str(self.cols_label_pos)
        assert isinstance(self.cols_label_width     , list) and (len(self.cols_label_width     )==len(cols)), str_error+"parameter cols_label_width     =" + str(self.cols_label_width)
        assert isinstance(self.cols_label_anchor    , list) and (len(self.cols_label_anchor    )==len(cols)), str_error+"parameter cols_label_anchor    =" + str(self.cols_label_anchor)
        assert isinstance(self.cols_pos             , list) and (len(self.cols_pos             )==len(cols)), str_error+"parameter cols_pos             =" + str(self.cols_pos)
        assert isinstance(self.cols_size            , list) and (len(self.cols_size            )==len(cols)), str_error+"parameter cols_size            =" + str(self.cols_size)
        assert isinstance(self.cols_browsebutton_pos, list) and (len(self.cols_browsebutton_pos)==len(cols)), str_error+"parameter cols_browsebutton_pos=" + str(self.cols_browsebutton_pos)
        assert isinstance(self.select_cols, list) and isinstance(self.select_vals, list) and (len(self.select_cols)==len(self.select_vals)), \
               str_error+"parameter select_cols=" + str(select_cols) + " and select_vals=" + str(select_vals) 
        self.emptyform=True                                    # if no preselctions are possible...
        self.cols4select=[c for c in self.cols]                # column vector for SELECT in SQL queries
        n_ext=0                                                # counter for ntom-refs (must be specially treated)
        for i in range(len(self.cols)):
            if self.cols[i]==None:                             # ntom-refs must not be SELECTed (as they are links to other tables)
                assert i>0, str_error+"parameter cols="+str(self.cols)+": first column must not be None!"
                self.cols[i]="EXTERN"+str(n_ext)               # need a valid unique identifier for that column!!
                n_ext=n_ext+1
                self.cols4select[i]=self.cols[0]               # replace column name by a valid column name for SELECTing 
        for i in range(len(self.cols_label_pos)):
            p=self.cols_label_pos[i]
            assert isinstance(p, tuple) and (len(p)in[2,4]), str_error+"each entry of cols_label_pos =" + str(self.cols_label_pos) + " must be of form (x,y) or (x,y,dx,dy)"
            if(len(p)==2): self.cols_label_pos[i]=p+(1,1)    # extend to format (x,y,dx,dy)
        for i in range(len(self.cols_pos)): 
            p=self.cols_pos[i]
            assert isinstance(p, tuple) and (len(p)in[2,4]), str_error+"each entry of cols_pos =" + str(self.cols_pos) + " must be of form (x,y) or (x,y,dx,dy)"
            if(len(p)==2): self.cols_pos[i]=p+(1,1)          # extend to format (x,y,dx,dy)
        for i in range(len(self.cols_size)): 
            s=self.cols_size[i]
            assert isinstance(s,int) or (isinstance(s,tuple) and (len(s)==2)), str_error+"each entry of cols_size =" + str(self.cols_size) + " must be of form 'width' or '(width,height)'"
            if isinstance(s,int): self.cols_size[i]=(s,1)     # extend to format (width,height)
        # (iv) definition of entry widgets etc.
        self.content = {}                                         # dictionary of input entry widgets
        self.entry_vars = [StringVar() for c in self.cols]        # string-type entry variables 
        self.entry_vars_refdata = [None for c in self.cols]       # if cols_type[i]=='ref' then entry_vars_refdata[i] contains data list as specified by cols_ref[i] 
        for sv in self.entry_vars: sv.set("")
        self.browsebuttons = []                                   # container list for browsebuttons
        for i in range(len(self.cols)):
            # (a) add label and bind help_callback
            lb=Label(self, text=self.cols_label[i], anchor=self.cols_label_anchor[i], width=self.cols_label_width[i])
            lb.grid(row=self.cols_label_pos[i][1], column=self.cols_label_pos[i][0],rowspan=self.cols_label_pos[i][3], columnspan=self.cols_label_pos[i][2])
            if(self.cols_helptext!=None) and (self.cols_helptext[i]!=None) and (self.help_callback!=None):
                lb.bind(help_event,lambda ev,prnt=self,txt=self.cols_helptext[i],cf=self.cfg: self.help_callback(prnt,txt,cf))
            # (b) add entry fields and set default data... 
            brbut = None     # no browse button per default
            if(self.cols_type[i]==None)or(self.cols_type[i]=='str'):
                # (b1) ... for type='str' or None
                entry = Entry(self, textvariable=self.entry_vars[i], width=self.cols_size[i][0], bg="white", disabledforeground='black')
                if(self.cols_readonly[i]): entry.configure(state=DISABLED)
            elif(self.cols_type[i]=='textfield'):
                # (b2) ... for type='textfield'
                entry = SupyTextFrame(self, width=self.cols_size[i][0], height=self.cols_size[i][1], catch_focus=False, textvariable=self.entry_vars[i])
                if(self.cols_readonly[i]): entry.configure(state=DISABLED)
            elif(self.cols_type[i] in ['filename','filename-dir']):
                # (b3) ... for type='filename' or 'filename-dir'
                entry = Entry(self, textvariable=self.entry_vars[i], width=self.cols_size[i][0], bg="white", disabledforeground='black')
                if(self.cols_readonly[i]):
                    entry.configure(state=DISABLED)
                else:
                    brbut = Button(self,text=self.browse_buttonname,command=(lambda i=i,col=self.cols[i]:self.onBrowse(i,col)))
            elif(self.cols_type[i]=='imagefile'):
                # (b4) ... for type='imagefile'
                entry = SupySQLImageFrame(self.sqldatabase, self, cfg=self.cols_ref[i], textvariable=self.entry_vars[i])
                if(self.cols_readonly[i]):
                    entry.configure(state=DISABLED)
                else:
                    brbut = Button(self,text=self.browse_buttonname,command=(lambda i=i,col=self.cols[i]:self.onBrowse(i,col)))
            elif(self.cols_type[i]=='optionlist'):
                # (b5) ... for type='optionlist'
                entry = OptionMenu(self,self.entry_vars[i],*self.cols_ref[i])
                entry.config(width=int(0.88*self.cols_size[i][0]), disabledforeground='black')
                if(self.cols_readonly[i]): entry.configure(state=DISABLED)
            elif(self.cols_type[i]=='ref'):
                # (b6) ... for type='ref'
                if(self.cols_ref[i].ref_image!=None): # display image frame?
                    entry = SupySQLImageFrame(self.sqldatabase, self, cfg=self.cols_ref[i], textvariable=self.entry_vars[i],widthEntry=self.cols_size[i][0])
                else:
                    entry = Entry(self, textvariable=self.entry_vars[i], width=self.cols_size[i][0], bg="white", disabledforeground='black')
                entry.configure(state=DISABLED)   # can be edited only via browse button and listbox dialog...
                if not self.cols_readonly[i]: 
                    brbut = Button(self,text=self.browse_buttonname,command=(lambda i=i,col=self.cols[i]:self.onBrowse(i,col)))
            elif(self.cols_type[i]=='ref_ntom'):
                # (b7) ... for type='ref_ntom'
                entry = SupySQLntomTextFrame(self.sqldatabase,self,cfg=self.cols_ref[i],width=self.cols_size[i][0], height=self.cols_size[i][1], catch_focus=False, textvariable=self.entry_vars[i])
                entry.configure(state=DISABLED)  # can be edited only via browse button and extern (e.g., listbox) dialog...
                if not self.cols_readonly[i]: 
                    brbut = Button(self,text=self.browse_buttonname,command=(lambda i=i,col=self.cols[i]:self.onBrowse(i,col)))
            entry.grid(row=self.cols_pos[i][1],column=self.cols_pos[i][0],rowspan=self.cols_pos[i][3],columnspan=self.cols_pos[i][2])  # side=TOP, expand=YES, fill=X)
            self.content[self.cols[i]] = entry
            if(brbut):
                brbut.grid(row=self.cols_browsebutton_pos[i][1],column=self.cols_browsebutton_pos[i][0]) 
                self.browsebuttons.append(brbut)
        # (c) set default data from sql database for initializing entry fields
        #print ("\n\nset default data: select_cols=",select_cols," select_vals=",select_vals)
        self.setData(self.select_cols,self.select_vals)

    def setData(self,scols=None,svals=None):    # set form data to values of record with scols[i]=svals[i] (for all i)
        #print("\nscols=",scols, "svals=",svals)
        if(scols!=None): self.select_cols=scols
        if(svals!=None): self.select_vals=svals
        #print("\nself.select_cols=",self.select_cols, "self.select_vals=",self.select_vals)
        str_error = "Assertion error in SQLFormFrame.setData for tables " + str(self.tables) + ": "
        wc=self.sqldatabase.getWhereClause_from_ColumnValues(self.tables,self.select_cols,self.select_vals)
        sqldata_def = self.sqldatabase.simple_select(self.cols4select,self.tables,joinon=self.join_on,where=wc)
        #print("\n!!!setData: sqldata_def=",sqldata_def, " from simple_select: wc=", wc, " self.cols=", self.cols, " self.tables=", self.tables, " joinon=", self.join_on)
        assert self.cfg.flagIgnoreMultipleSelections or len(sqldata_def)<=1, str_error + " Cannot uniquely initialize entry fields! Illegal where-clause '" + wc + "' ?"  # make sure that no more than one data entry is there
        self.empty=(len(sqldata_def)==0)
        if not self.empty:
            self.precondition_cols,self.precondition_vals=getUniqueListOfPreconditions(self.cols4select,list(sqldata_def[0]),self.conditioned_on,self.tables)
            #print("\n\nsetData: precondv/c = ", self.precondition_cols,self.precondition_vals)
            for i in range(len(self.cols)): self.setEntryData(i,str(sqldata_def[0][i]))
        else:
            self.precondition_cols,self.precondition_vals=getUniqueListOfPreconditions([],[],self.conditioned_on,self.tables) 
            for i in range(len(self.cols)): self.setEntryData(i,"")
            
    def setEntryData(self,idx,data):
        # (a) configure entry widget accordingly according to data
        #print("\n\nsetEntryData:idx=", idx, " data=", data, " type=", self.cols_type[idx])
        if(self.cols_type[idx]==None)or(self.cols_type[idx]=='str'):
            # (a1) ... for type='str' or None
            self.entry_vars[idx].set(str(data))  
            self.content[self.cols[idx]].configure(textvariable=self.entry_vars[idx])
            #print("setEntryData None/str: idx=", idx, " data=", data, " get()=", self.entry_vars[idx].get(), " entry=", str(self.content[self.cols[idx]]))
        elif(self.cols_type[idx]=='textfield'):
            # (a2) ... for type='textfield'
            self.entry_vars[idx].set(str(data))  
            self.content[self.cols[idx]].configure(textvariable=self.entry_vars[idx])
        elif(self.cols_type[idx]=='filename'):
            # (a3) ... for type='filename' or type='filename-dir'
            #print("\n\n(a3): data=", str(data))
            self.entry_vars[idx].set(str(data))  
            self.content[self.cols[idx]].configure(textvariable=self.entry_vars[idx])
        elif(self.cols_type[idx]=='imagefile'):
            # (a4) ... for type='imagefile'
            self.entry_vars[idx].set(str(data))  
            self.content[self.cols[idx]].configure(textvariable=self.entry_vars[idx])
        elif(self.cols_type[idx]=='optionlist'):
            # (a5) ... for type='optionlist'
            s=str(data)
            assert s=="" or s in self.cols_ref[idx], "Unexpected entry "+s+" for optionlist column "+self.cols[idx] + " with optionlist " + str(self.cols_ref[idx]) + "!" 
            self.entry_vars[idx].set(str(data))  
        elif(self.cols_type[idx]=='ref'):
            # (a6) ... for type='ref'
            if self.empty:
                self.entry_vars_refdata[idx]=None
                self.entry_vars[idx].set("")
            else:
                cf=self.cols_ref[idx]    # SQLListboxForm_config
                wc = self.sqldatabase.getWhereClause_from_ColumnValues(cf.tables,[cf.cols[0]],[data])   # construct where-clause by matching foreign key cf.cols[0] 
                data_ref = self.sqldatabase.simple_select(cf.cols,cf.tables,cf.join_on,wc)              # get foreign key plus additional info data
                assert len(data_ref)==1, "Unexpected length of data_ref! Cannot create entry data!"
                data_ref = list(data_ref[0])             # convert from tupel to list
                data_ref_str = cf.colvals2str(data_ref,cf.cols_format,cf.sep)
                self.entry_vars_refdata[idx]=data_ref
                self.entry_vars[idx].set(data_ref_str)
            self.content[self.cols[idx]].configure(textvariable=self.entry_vars[idx])
        elif(self.cols_type[idx]=='ref_ntom'):
            # (a7) ... for type='ref_ntom'
            cf=self.cols_ref[idx]    # SQLListboxForm_config
            c,v=getPreconditions4tables(self.precondition_cols,self.precondition_vals,cf.tables)
            wc = self.sqldatabase.getWhereClause_from_ColumnValues(cf.tables,c,v)  # construct where-clause by matching preconditions  
            data_ref_list = self.sqldatabase.simple_select(cf.cols,cf.tables,cf.join_on,wc)  # get foreign key plus additional info data
            txt='';
            for i in range(len(data_ref_list)):
                data_ref_item     = list(data_ref_list[i])   # convert from tupel to list
                data_ref_item_str = cf.colvals2str(data_ref_item,cf.cols_format,cf.sep)
                txt=txt+data_ref_item_str + "\n"
            #print("\n\nsetDATa:TXT=",txt)
            self.entry_vars_refdata[idx]=data_ref_list
            self.entry_vars[idx].set(txt)
            self.content[self.cols[idx]].configure(textvariable=self.entry_vars[idx], where=wc)

    def disableWidgets(self):
        # disable entry widgets
        for w in self.content.values():
            w.configure(state=DISABLED)
        # disable browse buttons
        for b in self.browsebuttons:
            b.configure(state=DISABLED)
        
    def enableWidgets(self):
        # enabel entry widths except is type='ref' (listbox-entries are read-only)
        for i in range(len(self.cols)):
            if (self.cols_type[i]!='ref')and(not self.cols_readonly[i]):
                self.content[self.cols[i]].configure(state=NORMAL)
        # enable browse buttons
        for b in self.browsebuttons:
            b.configure(state=NORMAL)
        
    def onBrowse(self,i,col):
        if self.cols_type[i] in ['filename','filename-dir'] or (self.cols_type[i]=='imagefile' and self.cols_ref[i].flagSimpleFilenameDialog):
            s=self.content[col].get()   
            filename  = os.path.basename(s)
            directory = os.path.dirname(s)
            if directory=="":
                directory="."
            if self.cols_type[i] in ['filename','imagefile']:         # ask for filename?
                s=tkinter.filedialog.askopenfilename(initialdir=directory, initialfile=filename)
            else:                                                     # ask for directory?
                s=tkinter.filedialog.askdirectory(initialdir=directory)
            if(s!=None)and(s!="")and(s):
                s=os.path.relpath(s,self.paths_relative_to)
                self.setEntryData(i,s)
                if(self.browse_callback!=None):
                    self.browse_callback(i)
        elif self.cols_type[i]=='imagefile':
            data_str,data_list=askSupyImageDialog(cfg=self.cols_ref[i],parent=self,data_str_init=self.content[col].textvariable.get())
            if (data_str!=None)and(data_str!="")and(data_str): 
                self.setEntryData(i,data_str)
                if(self.browse_callback!=None):
                    self.browse_callback(i)
        elif self.cols_type[i]=='ref':
            wc = self.sqldatabase.getWhereClause_from_ColumnValues(self.cols_ref[i].tables, self.cols_ref[i].cols, self.entry_vars_refdata[i])
            res,res_str = askSQLListboxForm(self.sqldatabase, self.cols_ref[i], where_init=wc,parent=self)
            if(res!=None):
                self.setEntryData(i,res[0][0])   # only foreign key which is assumed to be first data item
                if(self.browse_callback!=None):
                    self.browse_callback(i)
        elif self.cols_type[i]=='ref_ntom':
            if(self.browse_callback!=None):
                self.browse_callback(i)
            if(self.cols_ref[i].ntom_callback!=None):
                cond_on_new=[(self.precondition_cols[i],self.precondition_vals[i]) for i in range(len(self.precondition_cols))]
                cond_on_new=cond_on_new+[(self.select_cols[i],self.select_vals[i]) for i in range(len(self.select_cols))]
                #print("\n\nNTOM_CALLBACK: cond_on_new=", cond_on_new)
                if not self.cols_ref[i].ntom_flagSimple:
                    # invoke full table editor window (usually a call to editSQLTables)
                    #self.commit_inputs()      # commit in order to let see new data during following editing
                    flagCommit=self.cols_ref[i].ntom_callback(self,self.sqldatabase,"",self.cols_ref[i].link_ntom_form_cfg,cond_on_new)     # format von callback: parent,db,cfg_of_link_form,conditioned_on
                else:
                    # invoke simple sqllistbox form to select associated values (usually a call to editSQLTable_ntom_simple)
                    flagCommit=self.cols_ref[i].ntom_callback(self,self.sqldatabase,"",self.cols_ref[i],self.select_vals[0])     # select_cols[0] is assumed to be the value of the primary key!!!!  
                if flagCommit>0: self.setEntryData(i,"")

    def commit_inputs(self):     # submit contents of input widgets to database (and commit)
        f=self  # reference to form
        # (i) extract result values for each column 
        results = ['' for c in f.cols]     # allocate list
        for i in range(len(f.cols)):       # get result record as list of strings
            if f.cols_type[i] in [None,'str','filename','filename-dir','imagefile']:
                results[i]=f.content[f.cols[i]].get()
            elif f.cols_type[i]=='textfield':
                results[i]=f.content[f.cols[i]].gettext()
            elif f.cols_type[i]=='optionlist':
                results[i]=f.entry_vars[i].get()
            elif f.cols_type[i]=='ref':
                if not f.empty: 
                    results[i]=f.entry_vars_refdata[i][0]    # just foreign key...
                else:
                    results[i]=""
        # (ii) check results and update database
        check_res = self.checkResults(f.sqldatabase,f.tables,f.cols,results)
        if check_res!='OK':
            # something wrong, display error message...
            tkinter.messagebox.showerror(title="Submit Error", parent=f, message=check_res)
            results=None
        elif not self.empty:
            # results are ok: Then do update procedure...
            f.sqldatabase.begin_transaction()
            try:
                for i in range(len(self.update_tables)):
                    t =self.update_tables[i]         # table to be updated
                    pk=[p for p in self.update_tables_pkeys[i]]   # copy of list of primary keys for where-clause
                    uc=[u for u in self.update_tables_cols[i]]    # copy of list of columns to be updated
                    #print("pk=",pk, "     uc=",uc)
                    # determine values of primary keys and other columns
                    idx_cols = dict(zip(f.cols,range(len(f.cols))))
                    val_pk=len(pk)*[None]
                    val_uc=len(uc)*[None]
                    for j in range(len(pk)):
                        val_pk[j]=results[idx_cols[pk[j]]]
                        if "." in pk[j] : pk[j] = pk[j].split(".")[1]    # e.g., use only 'name' instead of 'student.name' (no tables names required)
                    for j in range(len(uc)):
                        val_uc[j]=results[idx_cols[uc[j]]]
                        if "." in uc[j] : uc[j] = uc[j].split(".")[1]    # e.g., use only 'name' instead of 'student.name' (no tables names required)
                    # do update query
                    #print("t=",t," uc=",uc," val_uc=", val_uc, " pk=", pk, " val_pk=", val_pk)
                    f.sqldatabase.simple_update_byPKEY(t,uc,val_uc,pk,val_pk,orclause='abort')
            except KeyError as e:
                print ("KeyError Exception while updating tables " + str(self.update_tables) + ": \n\n" + str(sys.exc_info()))
                print ("Maybe you have wrongly defined a form column in your SupySQLForm_config (or derived class)?")
                print ("Look at dictionary idx_cols=", idx_cols)
                print ("and compare to columns in uc=", uc, " !!!!")
                raise e
            except:
                str_error = "Update Exception while updating tables " + str(self.update_tables) + ": \n\n" + str(sys.exc_info()) \
                            + "\nHave you used quotes (') in a textfield? --> Use double quotes (\") instead!" + "\n\nUpdate query will be rolled-back. \nPlease correct your input."
                tkinter.messagebox.showerror(title="Submit Error", parent=f, message=str_error)
                f.sqldatabase.rollback_transaction()
                results=None
            else:
                f.sqldatabase.commit_transaction()
        # (iii) set list of preconditions (as inputs may have changed...)
        wc=self.sqldatabase.getWhereClause_from_ColumnValues(self.tables,self.select_cols,self.select_vals)
        sqldata_def = self.sqldatabase.simple_select(self.cols4select,self.tables,joinon=self.join_on,where=wc)
        assert len(sqldata_def)<=1, str_error + " Cannot uniquely initialize entry fields! Illegal where-clause '" + wc + "' ?"  # make sure that exactly one data entry is there
        self.empty=(len(sqldata_def)==0)
        if not self.empty:
            self.precondition_cols,self.precondition_vals=getUniqueListOfPreconditions(self.cols4select,list(sqldata_def[0]),self.conditioned_on,self.tables)
            for i in range(len(self.cols)): self.setEntryData(i,str(sqldata_def[0][i]))
        else:
            self.precondition_cols,self.precondition_vals=getUniqueListOfPreconditions([],[],self.conditioned_on,self.tables) 
            for i in range(len(self.cols)): self.setEntryData(i,"")
        # (iv) return
        return results
            

##############################################################################################################################
# SupySQLForm & SupySQLForm_config 
# An input form for a record of an SQL database 
# 
# Input parameters wrapped from SupySQLFormFrame (see there for details)
#    tables                : list of table names to make a natural join
#    join_on               : list of join expressions (len is 1 smaller than tables), 
#    cols                  : list of columns to be displayed or inputed
#    cols_type             : list of type indicators ('str'/None; 'textfield'; 'filename'; 'optionlist'; 'ref') 
#    cols_ref              : list of SupySQLForm_config reference parameters (for cols_type[i]=='ref') or optionlist
#    cols_readonly         . list of (0/1) flags indicating that an entry field is read-only (1=readonly)
#    cols_label            : list of labels for cols
#    cols_label_pos        : list of position (x,y) for each column label
#    cols_label_width      : list of label widths for each column label
#    cols_label_anchor     : list of label anchors (e.g., 'w') for each column label
#    cols_pos              : list of positions (x,y) for each cols entry fields
#    cols_size             : list of width or (width,height)-tuples for each cols entry fields (default height ist 1)
#    cols_helptext         : list of helptext that is displayed after a help event (e.g., right-click on label)
#    cols_browsebutton_pos : list of positions of the browse buttons (e.g., for type='filename' etc.) 
#    select_cols           : list of columns used for selecting one table record to be edited
#    select_vals           : values for the columns in select_cols 
#    help_event            : define event type to be bound to input label for help text, e.g., "<Button-3>"
#    help_title            : title of help window
#    help_buttonname       : button text for help window
#    browse_buttonname     : button text for browse buttons
# Additional input parameters:
#    button_str          : labels on buttons, e.g., button_str=['Ok', 'Cancel']
# Output parameters:
#    use data=getData() to obtain data entered in the form (as list of values) 
##############################################################################################################################
"""
SupySQLForm_checkResults_default: checks if the input record is ok for commit()
Parameters:
   sqldatabase,tables,cols: as in SupySQLForm
   result_row: list of inputs (same order as cols) from the form, corresponding to one row ...
Return values:
   returns either "OK" or a string-type error message
"""
def SupySQLForm_checkResults_default(sqldatabase,tables,cols,result_row):
    return "OK"

class SupySQLForm_config(SupySQLFormFrame_config):
    button_str = ['Ok','Cancel']                        # names of the submit/cancel buttons
    title      = 'SupySQLForm...'                       # is used only for askSupySQForm
    
class SupySQLForm:                   # add non-modal form box
    def __init__(self, parent, sqldatabase, cfg=SupySQLForm_config, \
                 tables=None, join_on=None, cols=None, cols_type=None, cols_ref=None, cols_readonly=None, \
                 cols_label=None, cols_label_pos=None, cols_label_width=None, cols_label_anchor=None, \
                 cols_pos=None, cols_size=None, cols_helptext=None, cols_browsebutton_pos=None, \
                 select_cols=None, select_vals=None, help_event=None, help_title=None, help_buttonname=None, browse_buttonname=None, \
                 checkResults=None, update_tables=None, update_tables_pkeys=None, update_tables_cols=None, \
                 paths_relative_to=os.getcwd(), browse_callback=None, help_callback=displayHelpMessage_default, \
                 button_str = None):      
        # basic initialization
        if button_str ==None : button_str = cfg.button_str
        self.button_str = button_str
        self.results=None
        self.box = Frame(parent)                           # container frame
        self.box.pack(expand=YES, fill=X)
        # create form 
        self.form = SupySQLFormFrame(self.box,sqldatabase,cfg,tables,join_on,cols,cols_type,cols_ref,cols_readonly,
                                     cols_label,cols_label_pos,cols_label_width,cols_label_anchor,
                                     cols_pos,cols_size,cols_helptext,cols_browsebutton_pos,
                                     select_cols,select_vals,help_event,help_title,help_buttonname,browse_buttonname,
                                     checkResults, update_tables, update_tables_pkeys, update_tables_cols, \
                                     paths_relative_to,browse_callback,help_callback)
        self.form.pack(side=TOP, expand=Y, fill=X)      
        # create control button frame
        self.buttonframe = Frame(self.box)
        Button(self.buttonframe,text=button_str[1],command=self.onCancel).pack(side=RIGHT)
        Button(self.buttonframe,text=button_str[0],command=self.onSubmit).pack(side=RIGHT)
        self.box.master.bind('<Shift-Return>', (lambda event: self.onSubmit()))
        self.buttonframe.pack(side=BOTTOM)

    def onSubmit(self):                                      # override this if necessary
        self.results=self.form.commit_inputs()
        if(self.results!=None):
            self.box.destroy()
     
    def onCancel(self):                                      # override if needed
        self.results=None
        self.box.destroy()
        
def askSupySQLForm(sqldatabase, cfg=SupySQLForm_config, \
                   parent=None, title=None, \
                   tables=None, join_on=None, cols=None, cols_type=None, cols_ref=None, cols_readonly=None, \
                   cols_label=None, cols_label_pos=None, cols_label_width=None, cols_label_anchor=None, \
                   cols_pos=None, cols_size=None, cols_helpttext=None, cols_browsebutton_pos=None, \
                   select_cols=None, select_vals=None, help_event=None, help_title=None, help_buttonname=None, browse_buttonname=None, \
                   checkResults=None, update_tables=None, update_tables_pkeys=None, update_tables_cols=None, \
                   paths_relative_to=os.getcwd(), browse_callback=None, help_callback=displayHelpMessage_default, \
                   button_str = None):  # for parameters see SQLListboxForm_config
    if title==None: title=cfg.title
    top=Toplevel(parent)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SupySQLForm(top,sqldatabase, cfg, tables,join_on,cols, cols_type, cols_ref, cols_readonly, \
                  cols_label, cols_label_pos, cols_label_width, cols_label_anchor, \
                  cols_pos, cols_size, cols_helpttext, cols_browsebutton_pos, \
                  select_cols, select_vals, help_event, help_title, help_buttonname, browse_buttonname, \
                  checkResults, update_tables, update_tables_pkeys, update_tables_cols, \
                  paths_relative_to, browse_callback, help_callback, \
                  button_str)
    top.wait_window(f.box)
    top.destroy()
    return f.results



##################################################################################################################################################################
##################################################################################################################################################################
# Part V: Module test
##################################################################################################################################################################
##################################################################################################################################################################
if __name__ == '__main__':
    # create a dummy database
    class tb_student_cfg(Table_cfg):
        name = 'student'
        # column definitions
        col_names           = ['id'         ,'name'        ,'address' ]
        col_types           = ['INTEGER'    ,'TEXT'        ,'TEXT'    ]
        col_references      = [None         ,None          ,None      ]
        col_constraints     = ['PRIMARY KEY','NOT NULL'    ,None      ]
        col_ref_constraints = [None         ,None          ,None      ]
        col_defaults        = [None         ,None          ,None      ]
        indexes             = [('idx_name',['name'])]
        # default rows (that will be stored during creation)
        rows_default     = ["(1,'Müller' , 'Musterweg 5    ; 72475 Musterstadt')", \
                            "(2,'Maier'  , 'Maierweg 6     ; 72473 Maierstadt' )", \
                            "(3,'Biegert', 'Biegertweg 6   ; 72471 Biegertstadt' )", \
                            "(4,'Schmitz', 'Schmitzweg 6   ; 72469 Schmitzstadt' )", \
                            "(5,'Alonso' , 'Schillerstr. 6 ; 72467 Knotendorf' )"]

    class tb_course_cfg(Table_cfg):
        name = 'course'
        # column definitions
        col_names           = ['id'         ,'course'     ]
        col_types           = ['INTEGER'    ,'TEXT'       ]
        col_references      = [None         ,None         ]
        col_constraints     = ['PRIMARY KEY','NOT NULL'   ]
        col_ref_constraints = [None         ,None         ]
        col_defaults        = [None         ,None         ]
        indexes             = [('idx_name',['course'])]
        # default rows (that will be stored during creation)
        rows_default     = ["(1,'Mathe'  )", \
                            "(2,'English')", \
                            "(3,'Biology')"]

    class tb_exam_cfg(Table_cfg):
        name = 'exam'
        # column definitions
        col_names           = ['id'         ,'id_student'       ,'id_course','grade','remark']
        col_types           = ['INTEGER'    ,'INTEGER'          ,'INTEGER'  ,'FLOAT','TEXT']
        col_references      = [None         ,'student'          ,'course'   ,None   ,None]
        col_constraints     = ['PRIMARY KEY','NOT NULL'         ,'NOT NULL' ,None   ,None]
        col_ref_constraints = [None         ,'ON DELETE CASCADE',None       ,None   ,None] 
        col_defaults        = [None         ,None               ,None       ,None   ,None]
        indexes             = None 
        # default rows (that will be stored during creation)
        rows_default     = ["(1, 2,1, 3.3, '')", \
                            "(2, 2,2, 4.0, '')", \
                            "(3, 4,3, 1.0, '')", \
                            "(4, 4,1, 2.0, '')", \
                            "(5, 3,1, 2.3, '')"]

    class db_dummy_cfg(sqldatabase_cfg):
        default_filename = 'sqldatabase_demo.db'
        table_configs = [tb_student_cfg, tb_course_cfg, tb_exam_cfg]
        
    print("\nModule test of supylib module supy.sqlforms.py")
    print("--------------------------------------------------\n") 
    db = sqldatabase(db_dummy_cfg,debugLevel=2)
    db.print_database(1)
    root = Tk()

    ##################################################################################################################################################################
    print("Part (i): Test of SQLListboxForm:")
    print("--------------------------------")
    ##################################################################################################################################################################

    class db_sqllb_form_cfg(SQLListboxForm_config):
        tables = None
        join_on = None
        cols   = None
        cols_format = None
        cols_sortbutton = None
        cols_sortbutton = None
        where = None
        where_init = None
        colvals2str = colvals2str_default
        sep = ' | '
        width = 20
        height = 10
        lbfont = ('courier',12,'normal')
        mode_multiselect = True
        callback_select = callback_select_default
        button_str = ['Ok','Cancel']
        title      = 'SQLListboxForm...'

    #lb = SQLListbox(root,db,['exam','student'],['exam.id','student.name','student.address'],\
    #                cols_format=['3d','3s:5','10s:10'],cols_sortbutton=['exxID','stName','stAdr'],labeltext='SQLListbox',\
    #                width=40, height=15)
    #lb.pack()
    #root.mainloop()
    res,res_str = askSQLListboxForm(db,db_sqllb_form_cfg, \
                                    ['exam','student'],['exam.id_student==student.id'],['exam.id','student.name','student.address'],\
                                    root,"SQLListboxForm-Dialog...",\
                                    cols_format=['3d','3s:5','10s:10'],cols_sortbutton=['exxID','stName','stAdr'],labeltext='SQLListbox',\
                                    width=40, height=15)
    print("Result:", res, res_str)

    ##################################################################################################################################################################
    print("Part I(ii)a: Test of SupySQLForm:")
    print("--------------------------------")
    ##################################################################################################################################################################

    class db_sql_form_cfg(SupySQLForm_config):
        tables                = ['student']
        join_on               = None
        cols                  = ['student.id','student.name']
        cols_type             = ['str','filename']
        cols_ref              = None
        cols_readonly         = [0,0]
        cols_label            = ['ID','Name']
        cols_label_pos        = None
        cols_label_width      = 15     # may also be list
        cols_label_anchor     = 'w'    # may also be list
        cols_pos              = None
        cols_size             = 40     # may also be list
        cols_helptext         = ['Student id...','Student name...']
        cols_browsebutton_pos = None
        select_cols           = ['student.name']
        select_vals           = ['Maier']
        help_event            = "<Button-3>"
        help_title            = "Help"
        help_buttonname       = "Close"
        browse_buttonname     = "Browse"
        checkResults = SupySQLForm_checkResults_default               # function to check if inputs are valid (see SupySQLForm_checkResults_default)
        update_tables = ['student']                                   # tables to be updated after form submission
        update_tables_pkeys = [['student.id']]                        # for each table (to be updated) a list of primary keys 
        update_tables_cols  = [['student.name']]                      # for each table (to be updated) a list of columns to be updated
        button_str = ['Ok','Cancel']                                  # names of the submit/cancel buttons
        title      = 'SupySQLForm...'                                 # is used only for askSupySQLForm
    res = askSupySQLForm(db,db_sql_form_cfg)
    print("Result:", res)

    ##################################################################################################################################################################
    print("Part (ii)b: Advanced Test of SupySQLForm (I):")
    print("----------------------------------------------")
    ##################################################################################################################################################################

    class lb_EXAM_student_cfg(SQLListboxForm_config):
        tables = ['student']
        cols   = ['student.id', 'student.name']
        cols_format = ['5d','10s:10']
        cols_sortbutton = ['ID','NAME']
        where = None
        where_init = None
        colvals2str = colvals2str_default
        sep = ' | '
        width = 40
        height = 10
        lbfont = ('courier',12,'normal')
        callback_select = callback_select_default
        button_str = ['Ok','Cancel']
        title      = 'lb_EXAM_student'

    class lb_EXAM_course_cfg(SQLListboxForm_config):
        tables = ['course']
        cols   = ['course.id', 'course.course']
        cols_format = ['5d','10s:10']
        cols_sortbutton = ['ID','NAME']
        where = None
        where_init = None
        colvals2str = colvals2str_default
        sep = ' | '
        width = 20
        height = 10
        lbfont = ('courier',12,'normal')
        callback_select = callback_select_default
        button_str = ['Ok','Cancel']
        title      = 'lb_EXAM_course'

    class db_sql_form_cfg(SupySQLForm_config):
        tables                = ['exam','student','course']
        cols                  = ['exam.id', 'exam.id_student'  , 'exam.id_course', 'exam.grade', 'exam.remark']
        cols_type             = ['str'    , 'ref'              , 'ref'           , 'optionlist', 'textfield'  ]
        cols_ref              = [None     , lb_EXAM_student_cfg, lb_EXAM_course_cfg, ['1.2','2.3','4.0','5.0'],None]
        cols_readonly         = [1        ,0                , 0               , 0           ,0]
        cols_label            = ['ID','Student', 'Kurs', 'Note', 'Bemerkung']
        cols_label_pos        = None
        cols_label_width      = 15     # may also be list
        cols_label_anchor     = 'w'    # may also be list
        cols_pos              = None
        #cols_size             = 40     # may also be list
        cols_size             = [40,40,40,40,(40,10)]    
        cols_helptext         = ['Exam id...','Student name...', 'Kurs name...','Note ...','Bemerkung...']
        cols_browsebutton_pos = None
        select_cols           = ['exam.id']
        select_vals           = [2]
        help_event            = "<Button-3>"
        help_title            = "Help"
        help_buttonname       = "Close"
        browse_buttonname     = "Browse"
        checkResults = SupySQLForm_checkResults_default               # function to check if inputs are valid (see SupySQLForm_checkResults_default)
        update_tables = ['exam']                                      # tables to be updated after form submission
        update_tables_pkeys = [['exam.id']]                           # for each table (to be updated) a list of primary keys 
        update_tables_cols  = [['exam.id_student','exam.id_course','exam.grade','exam.remark']] # for each table (to be updated) a list of columns to be updated
        button_str = ['Ok','Cancel']                                  # names of the submit/cancel buttons
        title      = 'SupySQLForm...'                                 # is used only for askSupySQForm

    db.print_database(1)
    res = askSupySQLForm(db,db_sql_form_cfg)
    print("Result:", res)
    db.print_database(1)

    ##################################################################################################################################################################
    print("Part (ii)b: Advanced Test of SupySQLForm (II):")
    print("----------------------------------------------")
    ##################################################################################################################################################################
    class refntom_COURSE_student_cfg(SupySQLntomTextFrame_cfg):
        tables = ['student','course','exam']
        join_on = ['student.id=exam.id_student','exam.id_course=course.id']
        preselect_on_cols = ['student.id']             # preselect output on values of these columns 
        cols   = ['course.id', 'course.course']        # cols to be displayed...
        cols_format = ['5d','10s:10']
        cols_sortbutton = ['ID','NAME']
        where = None
        where_init = None
        colvals2str = colvals2str_default
        sep = ' | '
        width = 40
        height = 10
        lbfont = ('courier',12,'normal')
        readonly=True
        ntom_callback=None
        link_ntom_form_cfg=None

    class db_sql_form2_cfg(SupySQLForm_config):
        tables                = ['student']
        join_on               = None
        cols                  = ['student.id', 'student.name', None]
        cols_type             = ['str'       , 'str'         , 'ref_ntom'   ]
        cols_ref              = [None        , None          , refntom_COURSE_student_cfg]
        cols_readonly         = [1           ,1              , 0            ]
        cols_label            = ['ID','Student', 'Kurse']
        cols_label_pos        = None
        cols_label_width      = 15     # may also be list
        cols_label_anchor     = 'w'    # may also be list
        cols_pos              = None
        #cols_size             = 40     # may also be list
        cols_size             = [40,40,(40,10)]    
        cols_helptext         = ['Exam id...','Student name...', 'Kurs name...']
        cols_browsebutton_pos = None
        select_cols           = ['student.id']
        select_vals           = [2]
        help_event            = "<Button-3>"
        help_title            = "Help"
        help_buttonname       = "Close"
        browse_buttonname     = "Browse"
        checkResults = SupySQLForm_checkResults_default               # function to check if inputs are valid (see SupySQLForm_checkResults_default)
        update_tables = ['student']                                      # tables to be updated after form submission
        update_tables_pkeys = [['student.id']]                        # for each table (to be updated) a list of primary keys 
        update_tables_cols  = [['student.name']] # for each table (to be updated) a list of columns to be updated
        button_str = ['Ok','Cancel']                                  # names of the submit/cancel buttons
        title      = 'SupySQLForm2...'                                 # is used only for askSupySQForm

    db.print_database(1)
    res = askSupySQLForm(db,db_sql_form2_cfg)
    print("Result:", res)
    db.print_database(1)


