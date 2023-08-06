#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
from supy.sqldatabase import *
from supy.forms3 import *
from supy.utilities import *
from copy import *
import tkMessageBox
import Image, ImageTk, ImageDraw

############################################################
# TableInputMask_config
# specification of an input mask for a database table
# possible options: col_options[i] can be:
#   None       : no special options (plain input field)
#   list       : make an OptionMenu to select from
#   database   : make an OptionMenu from the keys of the database
#   'filename' : string field with browse button
#   'image'    : string field with browse button and image canvas
#   'sound'    : string field with browse button (is played)
#   any other string : is interpreted as name of a database in the multibase; make on OptionMenu from those keys
############################################################

class TableInputMask_cfg(Table_cfg):
    col_masknames      = [''           ,'Geschlecht']     # column names as it should appear in input mask
    col_options        = None
    col_help_texts     = [''           ,'Geschlecht']     # help text for each input field
    help_event         = "<Button-3>"                     # define event type to be bound to input label for help text
    listboxcols        = ['id','name']                    # col_name of the columns that will be included in the listbox
    copy_default_flags = None       # if copy_default_flags[i]>0 then take for copy option the default attribute value
    recordlabel_txt = "DATA RECORD #"         # Label for Record headings
    recordlabel_font = ('courier',13,'bold')  # font for Record headings
    labelanchor='w'
    labelwidth=None                 # default; may be a list for each entry
    entrysize=40
    flag_singleton = 0              # if set then only a single table entry can be edited!
    pos=None


class TableInputMask:

    def __init__(self,parent,sqldatabase,tablename,cfg=TableInputMask_cfg,paths_relative_to=os.getcwd()):
        self.parent = parent
        self.sqldatabase = sqldatabase
        self.tablename = tablename
        self.cfg = cfg
        self.paths_relative_to = paths_relative_to    # filenames are stored in database relative to this base path
        self.flagModified=0
        self.flag_singleton = self.database.cfg.flag_singleton  # only one database entry
        self.makeWidgets()

    def makeWidgets(self):
        # (i) root box container and frames for other widgets
        self.box = Frame(self.parent)
        self.box.pack(expand=YES, fill=X)
        upperframe = Frame(self.box)
        upperframe.pack(side=TOP,expand=Y,fill=X)
        middle1frame = Frame(self.box)
        middle1frame.pack(side=TOP,expand=Y,fill=X)
        middle2frame = Frame(self.box)
        middle2frame.pack(side=TOP,expand=Y,fill=X)
        lowerframe = Frame(self.box)
        lowerframe.pack(side=TOP,expand=Y,fill=X)
        # (ii) image canvas (displays only the first image field)
        self.imcanvas=None
        self.field_idx_image=0
        if(self.cfg.attr_options!=None)and('image' in self.cfg.attr_options):
            self.imcanvas = Canvas(middle2frame,width=self.cfg.imcanvas_size[0],height=self.cfg.imcanvas_size[1])
            self.imcanvas.pack(side=RIGHT,expand=Y,fill=X)
            for i in range(len(self.cfg.attr_options)):
                if(self.cfg.attr_options[i]=='image'):
                    self.field_idx_image = i
                    break;
        # (iii) Title label for records
        self.recordlabel = None
        if(self.cfg.recordlabel_txt!=""):
            self.recordlabel = Label(middle1frame,text="",font=self.cfg.recordlabel_font)
            self.recordlabel.pack(side=LEFT)
        # (iv) form 
        formframe = Frame(middle2frame)
        formframe.pack(side=LEFT,expand=Y,fill=X)
        self.form = SupyForm(self.database.cfg.attr_names,[""*self.database.attr_n],formframe,self.cfg.labelanchor,
                             labelwidth=self.cfg.labelwidth, entrysize=self.cfg.entrysize, pos=self.cfg.pos,
                             flagButtons=0,options=self.cfg.get_form_options(self.multibase),
                             paths_relative_to=self.paths_relative_to,browse_callback=self.browse_callback,
                             help_event=self.cfg.attr_help_event, help_texts=self.cfg.attr_help_texts, 
                             help_callback=self.cfg.attr_help_callback)
        if(self.flag_singleton):
            self.setFormEntries(self.database.get_record_entry())
        # (v) listbox for database keys
        if not self.flag_singleton:
            listframe = Frame(upperframe)
            listframe.pack(side=LEFT,expand=Y,fill=X)
            sbar = Scrollbar(listframe)
            self.listbox = Listbox(listframe,relief=SUNKEN,exportselection=0)
            list_of_keys = self.database.get_list_of_keys()
            for k in list_of_keys:
                self.listbox.insert('end',k)
            sbar.config(command=self.listbox.yview)
            self.listbox.config(yscrollcommand=sbar.set)
            sbar.pack(side=RIGHT, fill=Y)
            self.listbox.pack(side=LEFT, expand=YES, fill= BOTH)
            self.listbox.bind('<<ListboxSelect>>', self.onListboxSelect)
            if len(list_of_keys)>0 : 
                self.listbox.selection_set(first=0)
                self.onListboxSelect()
            self.listbox.focus_set()
        # (vi) create buttonframes next to listbox
        if not self.flag_singleton:
            buttonframe = Frame(upperframe)
            buttonframe.pack(side=RIGHT,expand=YES, fill=BOTH)
            self.var_radiobutton = IntVar()
            self.var_radiobutton.set(0)
            radiobuttonframe = Frame(buttonframe)
            radiobuttonframe.pack(side=TOP)
            Radiobutton(radiobuttonframe, text='view', command=self.onRadioButtonView,
                        variable=self.var_radiobutton,value=0).pack(side=LEFT)
            Radiobutton(radiobuttonframe, text='edit', command=self.onRadioButtonEdit,
                        variable=self.var_radiobutton,value=1).pack(side=LEFT)
            self.b_new    = Button(buttonframe,text='New'      ,command=self.onNew   )
            self.b_copy   = Button(buttonframe,text='Copy'     ,command=self.onCopy  )
            self.b_delete = Button(buttonframe,text='Delete'   ,command=self.onDelete)
            self.b_new.pack(side=TOP,fill=BOTH)
            self.b_copy.pack(side=TOP,fill=BOTH)
            self.b_delete.pack(side=TOP,fill=BOTH)
        # (vii) bottom buttonframe
        self.b_close=Button(lowerframe, text='Save changes & Close', command=self.onClose)
        self.b_close.pack(side=RIGHT)
        self.b_cancel=Button(lowerframe, text='Cancel changes & Close', command=self.onCancel)
        self.b_cancel.pack(side=RIGHT)
        if not self.flag_singleton:
            self.b_submit=Button(lowerframe, text='Submit Record', command=self.onSubmit)
            self.b_submit.pack(side=RIGHT)
        # (viii) disable input widgets (view only mode)
        if not self.flag_singleton:
            self.onRadioButtonView()

    def reset_listbox(self,idx_select):
        # delete entries of old listbox...
        #self.listbox.
        pass

    def setFormEntries(self,key):
        self.form.setEntryText(0,key)
        c = self.database.get_record_str(key)
        if(c!=None):           # no contents?
            for i in range(len(c)):
                self.form.setEntryText(i,c[i])
        else:
            self.form.setEntryText(0,key)
            for i in range(len(self.database.attr_n-1)):
                self.form.setEntryText(1+i,"")
        self.update_image()
        self.play_sound()

    def browse_callback(self,idx):
        if(idx==self.field_idx_image):
            self.update_image()
        if(self.cfg.attr_options!=None)and(self.cfg.attr_options[idx]=='sound'):
            self.play_sound(idx)

    def play_sound(self,idx=None):
        if(self.cfg.sound_playFlag>0):
            if(idx==None):
                idx=self.cfg.sound_primary_field_idx
            if(idx!=None):
                fname=self.form.entry_vars[idx].get()
                os.system('play ' + search_path(fname,self.paths_relative_to) + ' >/dev/null 2>/dev/null&')

    def load_image(self,fname,size):   # load image with filename fname and set to self.phim
        self.phim,self.draw=None,None
        if(fname):
            try:
                self.image = Image.open(search_path(fname,self.paths_relative_to))
            except IOError as e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
                print "supy.database_inputmask.load_image: Cannot load image ", fname, " !"
                self.phim=None
            else:
                try:
                    self.image = self.image.resize(size)
                except TypeError as e:
                    print "I/O error({0}): {1}".format(e.errno, e.strerror)
                    print "Cannot display image ", fname, " !"
                    print "Invalid size parameter ", size
                    self.phim=None
                else:
                    self.draw = ImageDraw.Draw(self.image)
                    self.phim = ImageTk.PhotoImage(self.image)
        return self.phim,self.draw
        
    def update_image(self):
        if (self.imcanvas!=None):
            self.imcanvas.delete('all');
            fname=self.form.entry_vars[self.field_idx_image].get()
            try:
                sz_str=""
                if(self.cfg.image_size_field_idx!=None):
                    sz_str = self.form.entry_vars[self.cfg.image_size_field_idx].get()
                    sz=json.loads(sz_str)
                else:
                    sz=self.cfg.image_size_default
            except ValueError as e:
                print "Value error: "
                print "Maybe self.cfg.image_size_field_idx of Database ", self.cfg.fname, " points to wrong field ?"
                print "It should have a size content such as [50,50], "
                print "but instead has content sz_str=", sz_str
                print "Please check the configuration class of the Database!"
            else:
                self.load_image(fname,sz)     # sets self.phim
                posx,posy = int((self.cfg.imcanvas_size[0]-sz[0])/2),int((self.cfg.imcanvas_size[1]-sz[1])/2) 
                self.imcanvas.create_image(posx,posy,image=self.phim,anchor=NW)

    def onRadioButtonView(self):
        self.form.disableWidgets()
        if not self.flag_singleton:
            self.b_submit.configure(state=DISABLED)
            self.b_new   .configure(state=DISABLED)
            self.b_copy  .configure(state=DISABLED)
            self.b_delete.configure(state=DISABLED)

    def onRadioButtonEdit(self):
        self.form.enableWidgets()
        if not self.flag_singleton:
            self.b_submit.configure(state=NORMAL)
            self.b_new   .configure(state=NORMAL)
            self.b_copy  .configure(state=NORMAL)
            self.b_delete.configure(state=NORMAL)

    def onListboxSelect(self,evt=None):
        sels = self.listbox.curselection()
        if len(sels)>0:
            index = int(sels[0])
            key = self.listbox.get(index)
            if(self.recordlabel!=None):
                self.recordlabel.configure(text=self.cfg.recordlabel_txt+str(index+1))
            self.setFormEntries(key)

    def selectListboxItem(self,key):
        itemlist = self.listbox.get(0,END)
        if key in itemlist:
            idx = itemlist.index(key)
            self.listbox.selection_clear(first=0,last=END)
            self.listbox.selection_set(first=idx)
            self.listbox.activate(idx)
            self.listbox.see(idx)
            self.onListboxSelect()

    def onNew(self,call_onListboxSelect=1, call_onSubmit=1):
        new_key=self.database.add_default_record()
        self.listbox.insert(END,new_key)
        self.listbox.selection_clear(first=0,last=END)
        self.listbox.selection_set(first=END)
        self.listbox.activate(END)
        self.listbox.see(END)
        if(call_onListboxSelect>0): self.onListboxSelect()
        if(call_onSubmit>0)       : self.onSubmit()
        self.flagModified=1
    
    def onCopy(self):
        sel = self.listbox.curselection()
        if len(sel)>0:
            # get key of selected item
            index = int(sel[0])
            key   = self.listbox.get(index)
            content = self.database.get_record(key)[1:]
            # create new record
            self.onNew(0,0)
            # copy data 
            key_new = self.listbox.get(self.listbox.curselection()[0])
            content_default = deepcopy(self.database.get_record(key_new)[1:])  # content from default record   
            content_new     = deepcopy(content)                                # new content
            if self.cfg.copy_default_flags!=None:
                for i in range(len(self.cfg.copy_default_flags)):
                    if(i>0)and(self.cfg.copy_default_flags[i]>0):
                        content_new[i-1]=content_default[i-1]          # take default contents where flag is set
            self.database.set_record(key_new,*content_new)
            self.onListboxSelect()
            self.onSubmit()
            self.flagModified=1
            
    def onDelete(self):
        sel = self.listbox.curselection()
        if len(sel)>0:
            index = int(sel[0])
            key   = self.listbox.get(index)
            if self.database.delete_record(key):
                self.listbox.delete(index)
        else:
            index=0
        if index>=self.listbox.size():
            index=index-1
        self.listbox.selection_clear(first=0,last=END)
        if index>=0:
            self.listbox.selection_set(first=index)
            self.listbox.activate(index)
            self.onListboxSelect()
        self.flagModified=1
            
    def onSubmit(self):
        # get key of current data record
        key = None
        index = -1
        if self.flag_singleton:
            key = self.database.get_record_entry()    # selects first entry (i.e., key) of first (i.e., only) record
        else:
            sel = self.listbox.curselection()
            if len(sel)>0:
                # get key of selected item
                index = int(sel[0])
                key   = self.listbox.get(index)
        if key!=None:
            # create new database record
            key_new = self.form.entry_vars[0].get()
            content_new = ["" for i in range(self.database.attr_n-1)]
            for i in range(self.database.attr_n-1):
                content_new[i]=self.form.entry_vars[i+1].get()
            # check new database record (JSON may raise error)
            try:
                self.database.set_record_str([key_new]+content_new,1) # check only!!
            except ValueError as e:
                tkMessageBox.showerror("Submit error", "Cannot submit data. Please check your input!")
                print "Problem occured in database ", self.database.filename, " when submitting dataset ", [key_new]+content_new
            else:
                if not self.database.delete_record(key):
                    key_new=key                                  # old key must not be deleted; then use old key again...
                self.database.set_record_str([key_new]+content_new)
                self.flagModified=1
                # update listbox ?
                if not self.flag_singleton:
                    self.listbox.delete(index)
                    self.listbox.insert(index,key_new)
                    self.listbox.selection_set(index)
                    self.listbox.activate(index)
                    self.listbox.see(index)
                    self.onListboxSelect()
                    self.listbox.focus_set()

    def onClose(self):
        self.onSubmit()                 # submit latest changes in the form entry
        if(self.flagModified>0):
            self.database.save()
        self.box.destroy()

    def onCancel(self):
        if(self.flagModified>0):
            self.database.load()
        self.box.destroy()

def fillDBInputMask(parent,title,database,cfg=DBInputMask_config,multibase=None,paths_relative_to=os.getcwd()):
    top=Toplevel(parent)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=DBInputMask(top,database,cfg,multibase,paths_relative_to)
    top.wait_window(f.box)
    top.destroy()
    return None


if __name__ == '__main__':
    # create a dummy database
    class db_dummymask_config(Database_config,DBInputMask_config):
        # database specification
        default_filename = 'dummy_mask.db'
        dummy_img = '../MinotaurusSpiel/trunk/images/default_image.tif'
        dummy_snd = '../MinotaurusSpiel/trunk/sounds/default_sound.wav'
        types = ['type1','type2','type3']
        attr_names      = ['Nickname'  ,'Image'  , 'Imagesize', 'Typeinfo', 'Sound1' , 'Sound2' , 'Sound3' ]
        attr_types      = ['string'    ,'string' , 'json'     , 'string'  , 'string' , 'string' , 'string' ]
        default_record  = ['__new_key_',dummy_img, '[50,50]'  , types[0]  , dummy_snd, dummy_snd, dummy_snd]
        # input mask specification
        attr_options         = [None        ,'image'  , None       , types     , 'sound'  , 'sound'  , 'sound'  ]
        image_size_field_idx = 2
        sound_playFlag = 1
        sound_primary_field_idx = 4

    db_dummymask = Database(db_dummymask_config)
    db_dummymask.print_database()
    root = Tk()
    fillDBInputMask(root,"Edit database XY",db_dummymask,db_dummymask_config)
