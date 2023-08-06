#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
from supy.forms3 import *
from supy.utilities import *
from copy import *
import tkinter.messagebox
import tkinter.filedialog
from PIL import Image, ImageTk, ImageDraw


##################################################################################################################################################################
##################################################################################################################################################################
# Part I: SQLImageDialog and related classes and procedures:
#         classes: SQLImageDialog, SQLImageDialog_config, SQLImageDialogForm
#         SQLImageDialog: for inputing and clipping a image   
# Data Exchange:
##################################################################################################################################################################
##################################################################################################################################################################
class SQLImageDialog_config:
    text_labels    = ["Label","Filename","Mode","x1" ,"x2" ,"y1" ,"y2" ]
    pos_labels     = [(0,0)  ,(1,0)     ,(2,0)                 ,(3,0)  ,(4,0)  ,(5,0)  ,(6,0)  ]
    entry_width    = [40     ,40        ,None                  ,10     , 10    , 10    , 10    ]
    entry_pos      = [(0,1)  ,(1,1)     ,(2,1)                 ,(3,1)  ,(4,1)  ,(5,1)  ,(6,1)  ]   # format (row,column)
    entry_type     = [['ef'],['ef']     ,['ol',['full','clipped']],['ef'] ,['ef'] ,['ef'] ,['ef'] ]   # 'ef'=entry field; 'ol'=option list
    label_sticky   = 'w'                                                                           # Ausrichtung der Labels (within grid cell)
    entry_sticky   = 'w'                                                                           # Ausrichtung der Entries (within grid cell)
    title          = 'SQLImageDialog'
    button_str     = ['Browse', 'Browse', 'Ok','Apply','Cancel']                                   # Text on buttons 
    button_pos     = [[1,3],[3,3],None,None]
    image_canvas_size = [200, 100]                                                                 # Size of image canvas
    clipframe_mark_size = (5,2)           # side length and line width of marking rectangle                    
    clipframe_mark_color = ('red','red')  # color of square and rectangle of mark symbol

class SQLImageDialogFrame(Frame):
    """
    Default constructor
    """
    def __init__(self, parent, data_str_init=None, cfg=SQLImageDialog_config, paths_relative_to=os.getcwd()):
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
        self.sbarCenterView()                          # center view on clip (i.e. adjust srollbars accordingly)

    def setData_from_str(self,data_str):                         # split data_str in components and save in object fields
        if data_str:
            s=data_str.split('|')
            assert len(s)==7, "Assertion error in SQLImageDialog.setData_from_str(data_str): Parameter data_str='" + data_str + "' must have format 'Label | Filename | mode | x1 | x2 | y1 | y2' !"
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
                msg="I/O error({0}): {1}".format(e.errno, e.strerror) + "\nsupy.sqlforms.SQLImageDialogFrame.load_image: Cannot load image " + fname + " !"
                tkinter.messagebox.showerror(title="Submit Error", parent=self, message=msg)
            else:
                self.draw = ImageDraw.Draw(self.image)
                self.phim = ImageTk.PhotoImage(self.image)
        return self.phim,self.draw

    def setImage(self):
        # (i) load image
        self.load_image(self.data_filename)
        # (ii) draw image on canvas
        if(self.imcanvas!=None):
            self.imcanvas.delete('all');
            szx,szy=0,0
            if(self.phim!=None):
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
        if(s!=None)and(s!="")and(s):
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


class SQLImageDialog:
    def __init__(self, parent, data_str_init=None, cfg=SQLImageDialog_config):           # for parameters see SQLListboxForm_config
        # basic initialization
        self.cfg = cfg
        self.data_list=None
        self.data_str =None
        self.box = Frame(parent)                             # container frame
        self.box.pack(expand=YES, fill=X)
        # create ImageDialogFrame
        self.imdia = SQLImageDialogFrame(self.box,data_str_init,cfg) 
        self.imdia.pack(side=TOP) #, expand=Y, fill=X)      
        # create control button frame
        self.buttonframe = Frame(self.box)
        Button(self.buttonframe,text=self.cfg.button_str[4],command=self.onCancel).pack(side=RIGHT)
        Button(self.buttonframe,text=self.cfg.button_str[2],command=self.onSubmit).pack(side=RIGHT)
        Button(self.buttonframe,text=self.cfg.button_str[3],command=self.onApply).pack(side=LEFT)
        self.box.master.bind('<Return>', (lambda event: self.onSubmit()))
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
 
def askSQLImageDialog(cfg=SQLImageDialog_config, parent=None, title=None, data_str_init=None):
    if title==None: title=cfg.title
    top=Toplevel(parent)
    top.grab_set()                         # make window modal (i.e., redirect all inputs from parent window to listbox dialog)
    if parent: top.transient(parent)       # make window transient, e.g., minimize with parent etc.
    if title: top.title(title) 
    f=SQLImageDialog(top,data_str_init,cfg)
    top.wait_window(f.box)
    top.destroy()
    return f.data_str, f.data_list   # return results
    

##################################################################################################################################################################
##################################################################################################################################################################
# Part II: ScrolledText: A Tkinter Text Widget with scrollbars
##################################################################################################################################################################
##################################################################################################################################################################

class ScrolledTextFrame(Frame):
    def __init__(self,parent=None,text_str=''):
        Frame.__init__(self,parent)
        self.text=Text(self,relief=SUNKEN)
        self.sbarx, self.sbary = Scrollbar(self,orient=HORIZONTAL), Scrollbar(self,orient=VERTICAL)
        self.sbarx.config(command=self.text.xview)
        self.sbary.config(command=self.text.yview)
        self.text.config(xscrollcommand=self.sbarx.set,yscrollcommand=self.sbary.set)
        self.sbarx.pack(side=BOTTOM, fill=X)
        self.sbary.pack(side=RIGHT, fill=Y)
        self.settext(text_str)

    def settext(self,text_str=''):        # set text given by text_str
        self.text.delete('1.0',END)
        self.text.insert('1.0',text_str)
        self.text.mark_set(INSERT, END)
        self.text.focus()

    def gettext(self):                    # return text of text-widget
        return self.text.get('1.0', END+'-1c')    # first through last
        


##################################################################################################################################################################
##################################################################################################################################################################
# Part IV: Module test
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
        col_names           = ['id'         ,'id_student'       ,'id_course','grade']
        col_types           = ['INTEGER'    ,'INTEGER'          ,'INTEGER'  ,'FLOAT']
        col_references      = [None         ,'student'          ,'course'   ,None   ]
        col_constraints     = ['PRIMARY KEY','NOT NULL'         ,'NOT NULL' ,None   ]
        col_ref_constraints = [None         ,'ON DELETE CASCADE',None       ,None   ] 
        col_defaults        = [None         ,None               ,None       ,None    ]
        indexes             = None 
        # default rows (that will be stored during creation)
        rows_default     = ["(1, 2,1, 3.3)", \
                            "(2, 2,2, 4.0)", \
                            "(3, 4,3, 1.0)", \
                            "(4, 4,1, 2.0)", \
                            "(5, 3,1, 2.3)"]

    class db_dummy_cfg(sqldatabase_cfg):
        default_filename = 'sqldatabase_demo.db'
        table_configs = [tb_student_cfg, tb_course_cfg, tb_exam_cfg]
        
    print("\nModule test of supylib module supy.sqlforms.py")
    print("--------------------------------------------------\n") 
    db = sqldatabase(db_dummy_cfg)
    db.print_database(1)
    root = Tk()

    ##################################################################################################################################################################
    print("Part I: Test of SQLImageDialog:")
    print("--------------------------------")
    ##################################################################################################################################################################
    class mySQLImageDialog_config(SQLImageDialog_config):
        text_labels    = ["Label","Filename","Mode","x1" ,"x2" ,"y1" ,"y2" ]
        pos_lables     = [(0,0)  ,(1,0)     ,(2,0)                 ,(3,0)  ,(4,0)  ,(5,0)  ,(6,0)  ]
        entry_width    = [40     ,40        ,None                  ,10     , 10    , 10    , 10    ]
        entry_pos      = [(0,1)  ,(1,1)     ,(2,1)                 ,(3,1)  ,(4,1)  ,(5,1)  ,(6,1)  ]   # format (row,column)
        entry_type     = [['ef'],['ef']     ,['ol',['full','clipped']],['ef'] ,['ef'] ,['ef'] ,['ef'] ]   # 'ef'=entry field; 'ol'=option list
        label_sticky   = 'w'                                                                           # Ausrichtung der Labels (within grid cell)
        entry_sticky   = 'w'                                                                           # Ausrichtung der Entries (within grid cell)
        title          = 'SQLImageDialog'
        button_str     = ['Browse', 'Browse', 'Ok','Apply','Cancel']                                   # Text on buttons 
        button_pos     = [[1,3],[3,3],None,None]
        image_canvas_size = [500, 300]                                                                 # Size of image canvas
        clipframe_mark_size = (5,2)           # side length and line width of marking rectangle                    
        clipframe_mark_color = ('red','red')  # color of square and rectangle of mark symbol

    res_str, res_list = askSQLImageDialog(mySQLImageDialog_config,parent=root,title="Mein Titel...",data_str_init="Studenten WS 13/14|bild1.jpg|clipped|1180|1300|820|846")
    print("Result: res_str=", res_str, " res_list=", res_list)

    ##################################################################################################################################################################
    print("Part II: Test of SQLListboxForm:")
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
    print("Part IIIa: Test of SupySQLForm:")
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
        cols_width            = 40     # may also be list
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
    print("Part IIIb: Advanced Test of SupySQLForm:")
    print("-----------------------------------------")
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
        cols                  = ['exam.id', 'exam.id_student'  , 'exam.id_course', 'exam.grade']
        cols_type             = ['str'    , 'ref'              , 'ref'           , 'optionlist']
        cols_ref              = [None     , lb_EXAM_student_cfg, lb_EXAM_course_cfg, ['1.2','2.3','4.0','5.0']]
        cols_readonly         = [1        ,0                , 0               , 0           ]
        cols_label            = ['ID','Student', 'Kurs', 'Note']
        cols_label_pos        = None
        cols_label_width      = 15     # may also be list
        cols_label_anchor     = 'w'    # may also be list
        cols_pos              = None
        cols_width            = 40     # may also be list
        cols_helptext         = ['Exam id...','Student name...', 'Kurs name...','Note ...']
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
        update_tables_cols  = [['exam.id_student','exam.id_course','exam.grade']] # for each table (to be updated) a list of columns to be updated
        button_str = ['Ok','Cancel']                                  # names of the submit/cancel buttons
        title      = 'SupySQLForm...'                                 # is used only for askSupySQForm

    db.print_database(1)
    res = askSupySQLForm(db,db_sql_form_cfg)
    print("Result:", res)
    db.print_database(1)

