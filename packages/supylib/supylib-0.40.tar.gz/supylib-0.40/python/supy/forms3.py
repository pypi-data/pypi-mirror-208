#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
#import tkmessagebox
#import tkFileDialog
import os,time,datetime
import tkinter.messagebox
import tkinter.filedialog
from PIL import Image, ImageTk, ImageDraw
from supy.utilities import *

##################################################################################################################################################################
##################################################################################################################################################################
# Part I: SupyImageDialog and related classes and procedures:
#         classes: SupyImageDialog, SupyImageDialog_config, SupyImageDialogForm
#         SupyImageDialog: for inputing and clipping a image   
# Data Exchange:
##################################################################################################################################################################
##################################################################################################################################################################
class SupyImageDialog_config:
    text_labels    = ["Label","Filename","Mode","x1" ,"x2" ,"y1" ,"y2" ]
    pos_labels     = [(0,0)  ,(1,0)     ,(2,0)                 ,(3,0)  ,(4,0)  ,(5,0)  ,(6,0)  ]
    entry_width    = [40     ,40        ,None                  ,10     , 10    , 10    , 10    ]
    entry_pos      = [(0,1)  ,(1,1)     ,(2,1)                 ,(3,1)  ,(4,1)  ,(5,1)  ,(6,1)  ]   # format (row,column)
    entry_type     = [['ef'],['ef']     ,['ol',['full','clipped']],['ef'] ,['ef'] ,['ef'] ,['ef'] ]   # 'ef'=entry field; 'ol'=option list
    label_sticky   = 'w'                                                                           # Ausrichtung der Labels (within grid cell)
    entry_sticky   = 'w'                                                                           # Ausrichtung der Entries (within grid cell)
    title          = 'SupyImageDialog'
    button_str     = ['Browse', 'Browse', 'Ok','Apply','Cancel']                                   # Text on buttons 
    button_pos     = [[1,3],[3,3],None,None]
    image_canvas_size = [200, 100]                                                                 # Size of image canvas
    clipframe_mark_size = (5,2)           # side length and line width of marking rectangle                    
    clipframe_mark_color = ('red','red')  # color of square and rectangle of mark symbol

class SupyImageDialogFrame(Frame):
    """
    Default constructor
    """
    def __init__(self, parent, data_str_init=None, cfg=SupyImageDialog_config, paths_relative_to=os.getcwd()):
        # (i) do some basic initialization
        Frame.__init__(self,parent)  
        self.cfg=cfg                                        # configuration data
        self.paths_relative_to = paths_relative_to
        self.data_str=data_str_init                         # string representation of dialog result; format: "Label | Filename | mode | x1 | x2 | y1 | y2" (as could be saved in SQL table)
        self.data_list     = None
        self.data_label    = None                           # label to describe image
        self.data_filename = None                           # filename (inc. path) of image
        self.data_mode     = None                           # either 'full' or 'clipped': in former case the raw image is used, in the latter case a clip (see below) 
        self.data_x1       = None                           # (x1,x2,y1,y2) define a rectangle to clip from the original image
        self.data_x2       = None
        self.data_y1       = None
        self.data_y2       = None
        # (ii) allocate input widgets
        n_ip = len(self.cfg.text_labels)                     # number of input widgets
        self.leftframe = Frame(self, bd=2, relief=GROOVE)
        self.leftframe.pack(side=LEFT)
        self.rightframe = Frame(self)
        self.rightframe.pack(side=RIGHT,expand=YES, fill=BOTH)
        Button(self.leftframe,text=self.cfg.button_str[0],command=self.onBrowseFilename).grid(row=self.cfg.button_pos[0][0],column=self.cfg.button_pos[0][1])
        Button(self.leftframe,text=self.cfg.button_str[1],command=self.onBrowseClip    ).grid(row=self.cfg.button_pos[1][0],column=self.cfg.button_pos[1][1])        
        for i in range(n_ip): Label(self.leftframe,text=self.cfg.text_labels[i],anchor=self.cfg.label_sticky).grid(row=self.cfg.pos_labels[i][0],column=self.cfg.pos_labels[i][1],sticky=self.cfg.label_sticky)  # labels
        self.entry_vars = [StringVar() for i in range(n_ip)] # string-type entry variables 
        self.entry_field = [None for i in range(n_ip)]
        for i in range(n_ip):
            if   self.cfg.entry_type[i][0]=='ef':      # entry-field?
                entry = Entry(self.leftframe, textvariable=self.entry_vars[i], width=self.cfg.entry_width[i], bg="white", disabledforeground='black')
            elif self.cfg.entry_type[i][0]=='ol':      # option-list?
                entry = OptionMenu(self.leftframe,self.entry_vars[i],*self.cfg.entry_type[i][1])
            else:
                assert 0, "Wrong entry type: self.cfg.entry_type[i][0]="+str(self.cfg.entry_type[i][0])+" for i="+str(i)
            entry.grid(row=self.cfg.entry_pos[i][0],column=self.cfg.entry_pos[i][1],sticky=self.cfg.entry_sticky)
            self.entry_field[i]=entry
        self.dictEntryVar = {'label':self.entry_vars[0], 'fname':self.entry_vars[1], 'mode':self.entry_vars[2], \
                             'x1':self.entry_vars[3], 'x2':self.entry_vars[4], 'y1':self.entry_vars[5], 'y2':self.entry_vars[6]}
        # (iii) allocate image widgets (on rightframe)
        self.imcanvas = Canvas(self.rightframe,relief=SUNKEN)
        self.imcanvas.config(width=self.cfg.image_canvas_size[0], height=self.cfg.image_canvas_size[1])
        self.imcanvas.config(scrollregion=(0,0,self.cfg.image_canvas_size[0],self.cfg.image_canvas_size[1]))
        self.sbarx, self.sbary = Scrollbar(self.rightframe,orient=HORIZONTAL), Scrollbar(self.rightframe,orient=VERTICAL)
        self.sbarx.config(command=self.imcanvas.xview)
        self.sbary.config(command=self.imcanvas.yview)
        self.imcanvas.config(xscrollcommand=self.sbarx.set,yscrollcommand=self.sbary.set)
        self.sbarx.pack(side=BOTTOM, fill=X)
        self.sbary.pack(side=RIGHT, fill=Y)
        self.imcanvas.pack(side=RIGHT,expand=YES,fill=BOTH)
        self.imcanvas.bind("<Button-1>",self.onPressedB1)
        self.imcanvas.bind("<B1-Motion>",self.onMovedB1)
        self.imcanvas.bind("<ButtonRelease-1>",self.onReleasedB1)
        self.phim, self.draw = None, None
        self.imcanvas_state='IDLE'
        # (iv) set data 
        self.setData_from_str(self.data_str)           # set data fields from self.data_str
        if self.phim: self.sbarCenterView()            # center view on clip (i.e. adjust srollbars accordingly)

    def setData_from_str(self,data_str):                         # split data_str in components and save in object fields
        if data_str:
            s=data_str.split('|')
            assert len(s)==7, "Assertion error in SupyImageDialog.setData_from_str(data_str): Parameter data_str='" + data_str + "' must have format 'Label | Filename | mode | x1 | x2 | y1 | y2' !"
            self.data_label   =str(s[0])
            self.data_filename=str(s[1])
            self.data_mode    =str(s[2])
            self.data_x1      =int(s[3])
            self.data_x2      =int(s[4])
            self.data_y1      =int(s[5])
            self.data_y2      =int(s[6])
            self.data_str = data_str
            self.data_list = [self.data_label, self.data_filename, self.data_mode, self.data_x1, self.data_x2, self.data_y1, self.data_y2]
        else:
            self.data_label, self.data_filename, self.data_mode = "", "",str(self.cfg.entry_type[2][0])
            self.data_x1, self.data_x2, self.data_y1, self.data_y2 = 0,0,0,0
        self.dictEntryVar['label'].set(self.data_label)
        self.dictEntryVar['fname'].set(self.data_filename)
        self.dictEntryVar['mode' ].set(self.data_mode)
        self.dictEntryVar['x1'   ].set(str(self.data_x1))
        self.dictEntryVar['x2'   ].set(str(self.data_x2))
        self.dictEntryVar['y1'   ].set(str(self.data_y1))
        self.dictEntryVar['y2'   ].set(str(self.data_y2))
        self.setImage()

    def setData_from_form(self):                               # evaluate form inputs and store them in result data fields
        self.data_label    = str(self.dictEntryVar['label'].get())
        self.data_filename = str(self.dictEntryVar['fname'].get())
        self.data_mode     = str(self.dictEntryVar['mode' ].get())
        self.data_x1       = int(self.dictEntryVar['x1'   ].get())
        self.data_x2       = int(self.dictEntryVar['x2'   ].get())
        self.data_y1       = int(self.dictEntryVar['y1'   ].get())
        self.data_y2       = int(self.dictEntryVar['y2'   ].get())
        self.data_str      = self.data_label + '|' + self.data_filename + '|' + self.data_mode + '|' + str(self.data_x1) + '|' + str(self.data_x2) + '|' + str(self.data_y1) + '|' + str(self.data_y2) 
        self.data_list = [self.data_label, self.data_filename, self.data_mode, self.data_x1, self.data_x2, self.data_y1, self.data_y2]

    def load_image(self,fname):   # load image with filename fname and set to self.phim
        self.phim,self.draw=None,None
        if(fname):
            try:
                self.image = Image.open(search_path(fname,self.paths_relative_to))
            except IOError as e:
                msg="I/O error({0}): {1}".format(e.errno, e.strerror) + "\nsupy.forms.SupyImageDialogFrame.load_image: Cannot load image " + fname + " !"
                tkinter.messagebox.showerror(title="Submit Error", parent=self, message=msg)
            else:
                self.draw = ImageDraw.Draw(self.image)
                self.phim = ImageTk.PhotoImage(self.image)
        return self.phim,self.draw

    def setImage(self):
        # (i) load image
        self.load_image(self.data_filename)
        # (ii) draw image on canvas
        if(not self.imcanvas is None):
            self.imcanvas.delete('all');
            szx,szy=0,0
            if(not self.phim is None):
                szx,szy=self.phim.width(), self.phim.height()
                self.imcanvas.config(scrollregion=(0,0,szx,szy))
                self.imcanvas.create_image(0,0,image=self.phim,anchor=NW)
                if(self.dictEntryVar['mode'].get()=='clipped'):
                    self.imcanvas.create_rectangle(self.data_x1,self.data_y1,self.data_x2,self.data_y2,width=self.cfg.clipframe_mark_size[1],outline=self.cfg.clipframe_mark_color[1])
                    dxy=int(self.cfg.clipframe_mark_size[0]*0.5) 
                    self.imcanvas.create_rectangle(self.data_x1-dxy,self.data_y1-dxy,self.data_x1+dxy,self.data_y1+dxy,width=self.cfg.clipframe_mark_size[1],outline=self.cfg.clipframe_mark_color[0])
                    self.imcanvas.create_rectangle(self.data_x2-dxy,self.data_y2-dxy,self.data_x2+dxy,self.data_y2+dxy,width=self.cfg.clipframe_mark_size[1],outline=self.cfg.clipframe_mark_color[0])

    def sbarCenterView(self):     # center scrollbar position on clipped image (if necessary)
        x1,x2,y1,y2 = self.data_x1, self.data_x2, self.data_y1, self.data_y2     # bounding box clipped image
        dx,dy       = abs(x2-x1), abs(y2-y1)                                     # width, height of clipped image
        imx,imy     = self.phim.width(), self.phim.height()                      # width, height of original image
        cvx,cvy     = self.imcanvas.winfo_width(), self.imcanvas.winfo_height()  # canvas size
        if(cvx<2) : cvx=self.imcanvas.winfo_reqwidth()
        if(cvy<2) : cvy=self.imcanvas.winfo_reqheight()
        fx,fy,padx,pady=0,0,0,0   
        if(x2>cvx)and(imx>cvx):
            padx=int(0.5*(cvx-dx))
            if(padx<0):
                padx=0
            fx=(x1-padx)/imx
        if(y2>cvy)and(imy>cvy):
            pady=int(0.5*(cvy-dy))
            if(pady<0):
                pady=0
            fy=(y1-pady)/imy
        self.imcanvas.xview_moveto(fx)
        self.imcanvas.yview_moveto(fy)

    def onBrowseFilename(self):
        s=self.dictEntryVar['fname'].get()   
        filename  = os.path.basename(s)
        directory = os.path.dirname(s)
        if directory=="":
            directory="."
        s=tkinter.filedialog.askopenfilename(initialdir=directory, initialfile=filename)
        if(not s is None)and(s!="")and(s):
            s=os.path.relpath(s,self.paths_relative_to)
            self.dictEntryVar['fname'].set(s)
            self.data_filename=s
            self.setImage()

    def onPressedB1(self,event):    # pressed left button on image canvas
        # check if clicked on lower-right (x2,y2)-mark
        szx,szy=self.phim.width(), self.phim.height()
        x,y=int(event.x+szx*self.sbarx.get()[0]),int(event.y+szy*self.sbary.get()[0])
        tol=2*self.cfg.clipframe_mark_size[0]
        if (abs(x-self.data_x1)<tol) and (abs(y-self.data_y1)<tol):
            # click on upper-left mark: then move upper-left mark
            self.imcanvas_state='MOVE_UL'
            self.onMovedB1(event)
        elif (abs(x-self.data_x2)<tol) and (abs(y-self.data_y2)<tol):
            # click on lower-right mark: then move lower-right mark
            self.imcanvas_state='MOVE_LR'
            self.onMovedB1(event)
        else:
            # else: set upper-left and then move lower-right mark
            self.dictEntryVar['x1'].set(str(x))
            self.dictEntryVar['y1'].set(str(y))
            self.data_x1,self.data_y1=x,y
            self.imcanvas_state='MOVE_LR'
            self.onMovedB1(event)

    def onMovedB1(self,event):      # moved left button on image canvas
        if(self.imcanvas_state!='IDLE'):
            szx,szy=self.phim.width(), self.phim.height()
            x,y=int(event.x+szx*self.sbarx.get()[0]),int(event.y+szy*self.sbary.get()[0])
            if(self.imcanvas_state=='MOVE_LR'):
                # move lower-right mark
                self.dictEntryVar['x2'].set(str(x))
                self.dictEntryVar['y2'].set(str(y))
                self.data_x2,self.data_y2=x,y
            else: 
                # move upper-left mark
                self.dictEntryVar['x1'].set(str(x))
                self.dictEntryVar['y1'].set(str(y))
                self.data_x1,self.data_y1=x,y
            self.setImage()

    def onReleasedB1(self,event):   # released left button on image canvas
        self.onMovedB1(event)
        self.imcanvas_state='IDLE'

    def onBrowseClip(self):
        pass

    def onApply(self):
        self.setData_from_form()
        self.setImage()


class SupyImageDialog:
    def __init__(self, parent, data_str_init=None, cfg=SupyImageDialog_config):           # for parameters see SupyListboxForm_config
        # basic initialization
        self.cfg = cfg
        self.data_list=None
        self.data_str =None
        self.box = Frame(parent)                             # container frame
        self.box.pack(expand=YES, fill=X)
        # create ImageDialogFrame
        self.imdia = SupyImageDialogFrame(self.box,data_str_init,cfg) 
        self.imdia.pack(side=TOP) #, expand=Y, fill=X)      
        # create control button frame
        self.buttonframe = Frame(self.box)
        Button(self.buttonframe,text=self.cfg.button_str[4],command=self.onCancel).pack(side=RIGHT)
        Button(self.buttonframe,text=self.cfg.button_str[2],command=self.onSubmit).pack(side=RIGHT)
        Button(self.buttonframe,text=self.cfg.button_str[3],command=self.onApply).pack(side=LEFT)
        self.box.master.bind('<Return>', (lambda event: self.onSubmit()))
        self.box.master.bind('<Shift-Return>', (lambda event: self.onSubmit()))
        self.buttonframe.pack(side=TOP)

    def onSubmit(self):                                      # override this if necessary
        self.imdia.setData_from_form()
        self.data_list = self.imdia.data_list 
        self.data_str  = self.imdia.data_str 
        self.box.destroy()
     
    def onApply(self):
        self.imdia.onApply()

    def onCancel(self):                                      # override if needed
        self.data_list=None
        self.data_str=None
        self.box.destroy()
 
def askSupyImageDialog(cfg=SupyImageDialog_config, parent=None, title=None, data_str_init=None):
    if title is None: title=cfg.title
    top=Toplevel(parent)
    top.grab_set()                         # make window modal (i.e., redirect all inputs from parent window to listbox dialog)
    if parent: top.transient(parent)       # make window transient, e.g., minimize with parent etc.
    if title: top.title(title) 
    f=SupyImageDialog(top,data_str_init,cfg)
    top.wait_window(f.box)
    top.destroy()
    return f.data_str, f.data_list         # return results
    

##################################################################################################################################################################
##################################################################################################################################################################
# Part II: SupyTextFrame/Form: A Tkinter Text Widget with scrollbars
##################################################################################################################################################################
##################################################################################################################################################################

class SupyTextFrame_cfg:
    readonly=False
    height=24
    width=80
    wrap=NONE        # either NONE or CHAR
    catch_focus=True  # catch Focus to textfield after construction??

class SupyTextFrame(Frame):
    def __init__(self,parent=None,text_str='',cfg=SupyTextFrame_cfg, readonly=None, height=None, width=None, wrap=None, catch_focus=None, textvariable=None):
        Frame.__init__(self,parent)
        self.cfg=cfg
        if(readonly    is None): readonly   =cfg.readonly
        if(height      is None): height     =cfg.height
        if(width       is None): width      =cfg.width
        if(wrap        is None): wrap       =cfg.wrap
        if(catch_focus is None): catch_focus=cfg.catch_focus
        self.readonly   =readonly
        self.height     =height
        self.width      =width
        self.wrap       =wrap
        self.catch_focus=catch_focus
        self.textvariable = textvariable
        self.text=Text(self,wrap=self.wrap,relief=SUNKEN,width=self.width,height=self.height)
        self.sbarx, self.sbary = Scrollbar(self,orient=HORIZONTAL), Scrollbar(self,orient=VERTICAL)
        self.sbarx.config(command=self.text.xview)
        self.sbary.config(command=self.text.yview)
        self.text.config(xscrollcommand=self.sbarx.set,yscrollcommand=self.sbary.set)
        self.sbarx.pack(side=BOTTOM, fill=X)
        self.sbary.pack(side=RIGHT, fill=Y)
        self.text.pack(side=LEFT, expand=YES, fill=BOTH)
        if (text_str=='' or text_str is None)and (not textvariable is None and textvariable.get()!=''): 
            self.settext(textvariable.get())
        else:
            self.settext(text_str)

    def configure(self,state=None,textvariable=None):
        if(not state is None):
            self.text.configure(state=state)
        if(not textvariable is None):
            self.textvariable=textvariable
            self.settext(textvariable.get(),set_textvariable=False)

    def settext(self,text_str='',set_textvariable=True):        # set text given by text_str
        oldstate = self.text.cget('state')     # save old state
        self.text.configure(state=NORMAL)      # set state NORMAL to be able to reset text
        if(self.textvariable and set_textvariable): self.textvariable.set(text_str)
        self.text.delete('1.0',END)
        self.text.insert('1.0',text_str)
        self.text.mark_set(INSERT, END)
        if(self.readonly):
            self.text.configure(state=DISABLED)
        else:
            self.text.mark_set(INSERT, END)
            if self.catch_focus: self.text.focus()
            self.text.configure(state=oldstate)

    def gettext(self):                    # return text of text-widget
        if(self.textvariable): self.textvariable.set(self.text.get('1.0', END+'-1c'))
        return self.text.get('1.0', END+'-1c')    # first through last
        

class SupyTextForm_cfg(SupyTextFrame_cfg):
    txt_button_submit="Submit"
    txt_button_cancel="Cancel"
    title="SupyTextForm"

class SupyTextForm:
    """
    Input form using a Text widget
    Parameters:
       parent = master widget
       default_text = initial text
    """
    def __init__(self, parent, default_text=None, cfg=SupyTextFrame_cfg, readonly=None, height=None, width=None, wrap=None):    
        self.cfg=cfg
        self.box = Frame(parent)
        self.box.pack(expand=YES, fill=X)
        self.textbox=SupyTextFrame(self.box,default_text,cfg,readonly,height,width,wrap)
        self.textbox.pack(side=TOP,expand=YES,fill=X)
        Button(self.box, text=self.cfg.txt_button_cancel, command=self.onCancel).pack(side=RIGHT)
        Button(self.box, text=self.cfg.txt_button_submit, command=self.onSubmit).pack(side=RIGHT)
        self.result=None

    def onSubmit(self):
        self.result=self.textbox.gettext()
        self.box.destroy()
     
    def onCancel(self):                                       # override if need
        self.results=None
        self.box.destroy()
    
def askSupyTextForm(default_text=None, cfg=SupyTextForm_cfg, parent=None, title=None, readonly=None, height=None, width=None, wrap=None, grab_set=True):      
    if title is None: title=cfg.title
    top=Toplevel(parent)
    if grab_set: top.grab_set()            # make window modal (i.e., redirect all inputs from parent window to listbox dialog)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SupyTextForm(top,default_text,cfg,readonly,height,width,wrap)
    top.wait_window(f.box)
    top.destroy()
    return f.result


##################################################################################################################################################################
##################################################################################################################################################################
# Part III: SupyForm: a reusable form class 
#           python3-version of moudule supy.forms.py
##################################################################################################################################################################
##################################################################################################################################################################

class SupyForm:                                           # add non-modal form box
    def __init__(self, labels, default_entries=None, parent=None,labelanchor='w',labelwidth=None,entrysize=40,pos=None,
                 flagButtons=1,options=None,paths_relative_to=os.getcwd(),browse_callback=None,
                 help_event="<F1>",help_texts=None,help_callback=None):        # pass field labels list
        '''
        labels: list of strings where labels[i] is the label of the i-th input field
        default_entries: list of default entries that are displayed initially in the input field
        parent: parent widget
        labelanchor: alignment of label
        labelwidth: width of label fields, either a None, a single number, or a list (for each input field)
        entrysize: width of entry fields, either a single number or a list (for each input field)
        pos: either None or list; pos[i]=(x,y) is grid position for i-th label etc.  
        flagButtons: If >0 then buttons are displayed for submit/cancel actions 
        options: either None or a list where options[i] is either 'filename' or 'filename-saveas' or 'filename-dir' or None or a string list for a Optionmenu
        paths_relative_to: save browsed paths relative to this path
        browse_callback(idx): function that is called after selecting a filename, parameter idx is field index
        help_event: event that evokes help function (e.g., pressing F1 over the label)
        help_texts: either None or list of help strings for each label
        help_call : either None (then default call is used) or function 
        '''
        self.parent=parent
        if(pos is None):
            pos = [(0,y) for y in range(len(labels))]
        if(not labelwidth):
            labelwidth=max([len(s) for s in labels])
        if not isinstance(labelwidth,list):
            labelwidth = [labelwidth for y in range(len(labels))]
        if not isinstance(entrysize,list):
            entrysize = [entrysize for y in range(len(labels))]
        self.options = options
        self.paths_relative_to = paths_relative_to
        self.browse_callback=browse_callback
        self.browsebuttons = []
        self.labels = labels
        box = Frame(parent)
        box.pack(expand=YES, fill=X)
        formbox = Frame(box, bd=2, relief=GROOVE)     # formbox will have grid layout
        self.formbox=formbox
        formbox.pack(side=TOP, expand=Y, fill=X)      # runs onSubmit method
        self.content = {}                 # dictionary of input entries
        self.results = None               # final results as set by onSubmit()
        self.entry_vars = [StringVar() for l in labels]
        for sv in self.entry_vars: sv.set("")
        for i in range(len(labels)):
            row_label,column_label=pos[i][1], pos[i][0]
            lb=Label(formbox, text=labels[i], anchor=labelanchor, width=labelwidth[i])
            lb.grid(row=row_label,column=column_label)
            if(not help_texts is None) and (not help_texts[i] is None):
                if(help_callback is None):
                    help_callback=self.displayHelpMessage_default
                lb.bind(help_event,lambda ev,txt=help_texts[i]: help_callback(txt))
            if(options is None)or(options[i] is None)or(options[i]=='filename')or(options[i]=='filename-saveas')or(options[i]=='filename-dir')or(options[i]==[]):                
                entry = Entry(formbox, textvariable=self.entry_vars[i], width=entrysize[i], 
                              bg="white", disabledforeground='black')
                self.content[labels[i]] = entry
            else:
                entry = OptionMenu(formbox,self.entry_vars[i],*options[i])
                entry.config(width=int(0.88*entrysize[i]), disabledforeground='black')
                self.content[labels[i]] = self.entry_vars[i]
            if default_entries and (len(default_entries)>=(i+1)):
                self.setEntryText(i,default_entries[i])                
            entry.grid(row=row_label,column=column_label+1) # side=TOP, expand=YES, fill=X)
            if(not options is None)and(options[i] in ['filename','filename-saveas','filename-dir']):
                b=Button(formbox,text='Browse',command=(lambda i=i,label=labels[i]:self.onBrowse(i,label)))
                b.grid(row=row_label,column=column_label+2)
                self.browsebuttons.append(b)   
        if(flagButtons>0):
            Button(box, text='Cancel', command=self.onCancel).pack(side=RIGHT)
            Button(box, text='Submit', command=self.onSubmit).pack(side=RIGHT)
            box.master.bind('<Return>', (lambda event: self.onSubmit()))
        self.box=box
        self.formbox=formbox
        self.labels=labels

    def displayHelpMessage_default(self,text):
        w=Toplevel(self.parent)
        if self.parent: w.transient(self.parent)     # make window transient, e.g., minmize with parent etc.
        w.title("Help")
        l=Label(w,text=text)
        l.pack()
        b=Button(w,text="Close",command=w.destroy)
        b.pack()
        #tkMessageBox.showinfo("Help", text, parent=w)

    def setEntryText(self,idx,txt):
        if isinstance(self.content[self.labels[idx]],Entry):
            self.entry_vars[idx].set(txt)
            self.content[self.labels[idx]].configure(textvariable=self.entry_vars[idx])
        else:
            if (txt in self.options[idx]):
                self.entry_vars[idx].set(txt)

    def disableWidgets(self):
        for w in self.content.values():
            w.configure(state=DISABLED)
        for b in self.browsebuttons:
            b.configure(state=DISABLED)
        
    def enableWidgets(self):
        for w in self.content.values():
            w.configure(state=NORMAL)
        for b in self.browsebuttons:
            b.configure(state=NORMAL)
        
    def onBrowse(self,i,label):
        s=self.content[label].get()   
        filename  = os.path.basename(s)
        directory = os.path.dirname(s)
        if directory=="":
            directory="."
        if self.options[i]=='filename':
            s=filedialog.askopenfilename(initialdir=directory, initialfile=filename)
        elif self.options[i]=='filename-saveas':
            s=filedialog.asksaveasfilename(initialdir=directory, initialfile=filename)
        elif self.options[i]=='filename-dir':
            s=filedialog.askdirectory(initialdir=directory)
        #print("raw s=",s)
        if(not s is None)and(s!="")and(s):
            #if self.options[i]=='filename-dir':
            #s_rel=os.path.relpath(s,self.paths_relative_to)
            #s_base=os.path.basename(s)
            #print("s_rel=",s_rel, "s_base=",s_base)
            #if self.options[i]=='filename-dir':
            #s=os.path.relpath(s,self.paths_relative_to)
            #else:
            s=os.path.relpath(s,self.paths_relative_to)
            #print("s=",s)
            self.setEntryText(i,s)
            if(not self.browse_callback is None):
                self.browse_callback(i)

    def onSubmit(self):                                      # override this
        #for key in self.content.keys():                      # user inputs in 
        #    print(key, '\t=>\t', self.content[key].get())    # self.content[k]
        self.results = [self.content[l].get() for l in self.labels] 
        self.box.destroy()
     
    def onCancel(self):                                      # override if need
        self.results=None
        self.box.destroy()
     
#class DynamicPyFeForm(PyFeForm):
#    def __init__(self, labels=None):
#        labels = raw_input('Enter field names: ').split()
#        Form.__init__(self, labels)
#    def onSubmit(self):
#        print 'Field values...'
#        Form.onSubmit(self)           
#        self.onCancel()
        
def askSupyForm(labels,default_entries=None,parent=None,title=None,labelanchor='w',labelwidth=None,entrysize=40,pos=None,
                flagButtons=1,options=None,paths_relative_to=os.getcwd(),browse_callback=None,
                help_event="<F1>",help_texts=None,help_callback=None):      
    top=Toplevel(parent)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SupyForm(labels,default_entries,top,labelanchor,labelwidth,entrysize,pos,
               flagButtons,options,paths_relative_to,browse_callback,
               help_event,help_texts,help_callback)
    top.wait_window(f.box)
    top.destroy()
    return f.results


##################################################################################################################################################################
##################################################################################################################################################################
# Part IV: DateSlider: slider for dates
#          python3-version of moudule supy.forms.py
##################################################################################################################################################################
##################################################################################################################################################################

class DateSlider(Frame):
    def __init__(self, parent, from_date=datetime.date(2012,1,1),to_date=datetime.date(2012,12,31),init_date=datetime.date(2012,1,1),orient_arg='horizontal',command=None,*args):
        Frame.__init__(self,parent)
        dd=to_date-from_date
        self.var=IntVar()
        self.var.set((init_date-from_date).days)
        self.from_date=from_date
        self.current_date=init_date
        self.to_date=to_date
        self.command=command
        self.slider = Scale(self,from_=0,to_=dd.days,command=self.onMove,variable=self.var,*args,orient=orient_arg)
        self.slider.pack(side=RIGHT)
        self.label = Label(self,text="Halleluja")
        self.label.pack(side=LEFT)
        self.onMove(self.var.get(),1)
        
    def onMove(self,value,initFlag=0):
        self.current_date=self.from_date+datetime.timedelta(self.var.get())
        self.str_date = "%02d/%02d/%04d" % (self.current_date.month, self.current_date.day, self.current_date.year)
        self.label.configure(text=self.str_date)
        if (not self.command is None) and (initFlag==0):
            self.command(value)

    def get(self):
        return self.current_date


    
##################################################################################################################################################################
##################################################################################################################################################################
# Part V: SupySliderForm: Input form using Sliders
#         python3-version of moudule supy.forms.py
##################################################################################################################################################################
##################################################################################################################################################################

class SupySliderForm:
    """
    Input form using Sliders
    Parameters:
       parent = master widget
       labels = list of name lables for sliders
       default_values = initial slider values (either float or date)
       ranges = list of triples (v_min,v_max,delta_v)
    """
    def __init__(self, parent, labels, default_values, ranges=None, labelanchor='w',command=None,labelwidth=None,sliderwidth=40):        # pass field labels list
        if(not labelwidth):
            labelwidth=max([len(s) for s in labels])
        box = Frame(parent)
        box.pack(expand=YES, fill=X)
        sliderbox=Frame(box)
        sliderbox.pack(side=TOP,expand=YES,fill=X)

        #rows = Frame(box, bd=2, relief=GROOVE)        # box has rows, button
        #lcol = Frame(rows)                            # rows has lcol, rcol
        #rcol = Frame(rows)                            # button or return key,
        #rows.pack(side=TOP, expand=Y, fill=X)         # runs onSubmit method
        #lcol.pack(side=LEFT)
        #rcol.pack(side=RIGHT, expand=Y, fill=X)
        self.labels=labels
        self.content = {}                 # dictionary of sliders
        self.results = None               # final results as set be onSubmit()
        for i in range(len(labels)):
            label = labels[i]
            Label(sliderbox, text=label+": ", anchor=labelanchor, width=labelwidth).grid(row=i,column=0)
            default_value=default_values[i]
            range_=ranges[i]
            if type(default_value)==datetime.date:
                slider=DateSlider(sliderbox,range_[0],range_[1],default_value,command=self.onUpdate)
            else:
                slider=Scale(sliderbox,from_=range_[0],to_=range_[1],resolution=range_[2],command=self.onUpdate,orient='horizontal')
                slider.set(default_value)
            slider.grid(row=i,column=1) #side=TOP, expand=YES, fill=X)
            self.content[label] = slider
        Button(box, text='Cancel', command=self.onCancel).pack(side=RIGHT)
        Button(box, text='Submit', command=self.onSubmit).pack(side=RIGHT)
        box.master.bind('<Return>', (lambda event: self.onSubmit()))
        self.box=box
        self.sliderbox=sliderbox
        self.command=command
   
    def onUpdate(self,value=0):                                   # override this
        self.results = [self.content[l].get() for l in self.labels] 
        if(self.command):
            self.command()
     
    def onSubmit(self):
        for key in self.content.keys():                      # user inputs in 
            print(key, '\t=>\t', self.content[key].get())    # self.content[k]
        self.onUpdate()
        self.box.destroy()
     
    def onCancel(self):                                       # override if need
        self.results=None
        self.box.destroy()
    
def askSupySliderForm(labels,default_values,ranges,parent=None,title=None,labelanchor='w',command=None,labelwidth=None,sliderwidth=40):      
    top=Toplevel(parent)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SupySliderForm(top,labels,default_values,ranges,labelanchor,command,labelwidth,sliderwidth)
    top.wait_window(f.box)
    top.destroy()
    return f.results

##################################################################################################################################################################
##################################################################################################################################################################
# Part VI: Module test
##################################################################################################################################################################
##################################################################################################################################################################
if __name__ == '__main__':
    ##################################################################################################################################################################
    print("\nModule test of supylib module supy.forms3.py:")
    print("------------------------------------------------")
    print("\nPart (i): Test of SupyImageDialog:")
    print("----------------------------------")
    ##################################################################################################################################################################
    root=Tk()
    class mySupyImageDialog_config(SupyImageDialog_config):
        text_labels    = ["Label","Filename","Mode","x1" ,"x2" ,"y1" ,"y2" ]
        pos_lables     = [(0,0)  ,(1,0)     ,(2,0)                 ,(3,0)  ,(4,0)  ,(5,0)  ,(6,0)  ]
        entry_width    = [40     ,40        ,None                  ,10     , 10    , 10    , 10    ]
        entry_pos      = [(0,1)  ,(1,1)     ,(2,1)                 ,(3,1)  ,(4,1)  ,(5,1)  ,(6,1)  ]   # format (row,column)
        entry_type     = [['ef'],['ef']     ,['ol',['full','clipped']],['ef'] ,['ef'] ,['ef'] ,['ef'] ]   # 'ef'=entry field; 'ol'=option list
        label_sticky   = 'w'                                                                           # Ausrichtung der Labels (within grid cell)
        entry_sticky   = 'w'                                                                           # Ausrichtung der Entries (within grid cell)
        title          = 'SupyImageDialog'
        button_str     = ['Browse', 'Browse', 'Ok','Apply','Cancel']                                   # Text on buttons 
        button_pos     = [[1,3],[3,3],None,None]
        image_canvas_size = [500, 300]                                                                 # Size of image canvas
        clipframe_mark_size = (5,2)           # side length and line width of marking rectangle                    
        clipframe_mark_color = ('red','red')  # color of square and rectangle of mark symbol

    res_str, res_list = askSupyImageDialog(mySupyImageDialog_config,parent=root,title="Mein Titel...",data_str_init="Studenten WS 13/14|bild1.jpg|clipped|1180|1300|820|846")
    print("Result: res_str=", res_str, " res_list=", res_list)

    ##################################################################################################################################################################
    print("\nPart (ii): Test of SupyTextForm")
    print("--------------------------------")
    ##################################################################################################################################################################
    def_text='Hallo Zeile 1\nDies ist die zweite Zeile\n...und dies die dritte und letzte Zeile!!!!!!!'
    res_str=askSupyTextForm(def_text,wrap=NONE)
    print("Result: res_str=", res_str)

    ##################################################################################################################################################################
    print("\nPart (iii): Test of SupyForm")
    print("--------------------------------")
    ##################################################################################################################################################################
    s=DateSlider(root)
    s.pack(side=TOP)
    # Example 1: SupyForm
    labels=['Name', 'Age', 'Job']
    defaults=['Fridolin','40',"Großer Mandarin"]
    r=askSupyForm(labels,defaults,root,"Python ask form ...",'e',30,40)
    print(r)

    ##################################################################################################################################################################
    print("\nPart (iv): Test of SupySliderFrom")
    print("--------------------------------")
    ##################################################################################################################################################################
    # Example 2: SupySliderFrom
    labels=['var1','var2','var3','date']
    defaults=[3,14,5,datetime.date(2012,11,21)]
    ranges=[(0,10,1),(10,20,2),(5,10,0.1),(datetime.date(2012,1,1),datetime.date(2012,12,31))]
    r=askSupySliderForm(labels,defaults,ranges,root,"Slider Form example",'e',None,30,40)
