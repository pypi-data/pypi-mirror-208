#!/usr/bin/python
# -*- coding: utf-8 -*-

from supy.sqlforms import *



##################################################################################################################################################################
##################################################################################################################################################################
# Part I: SQLTableEditor 
#         classes: SQLTableEditor, SQLTableEditor_config
##################################################################################################################################################################
##################################################################################################################################################################

################################################################################################
# SQLTableEditor_config
# provides parameters for SQLTableEditor 
################################################################################################
class SQLTableEditor_config:
    table_cfg            = None               # table to be edited, first column is assumed to be primary key of type INTEGER!!!
    pkeys_readonly       = []                 # records with primary key in this list are considered as READ_ONLY (e.g., for default records)
    min_max_records      = None               # or [nMin, nMax]; if !=None this specifies the minimum and maximum number of data records in the table
    cfg_choiceLB         = None               # configuration for choice listbox (typically a SQLListbox_config)
    cfg_recForm          = None               # configuration for record form (typically a SupySQLForm_config)
    align_widgets        = 'horizontal'       # either 'vertical' or 'horizontal' for alignment of listbox and form
    lbButtons_str        = ['New', 'Copy', 'Delete']            # text for listbox buttons
    recFormButtons_str   = ['Reset', 'Default', 'Commit']       # text for form buttons
    ctrlRadioButtons_str = ['View', 'Edit']                     # text for radiobuttons (read-only, write/edit option)
    ctrlButtons_str      = ['Commit & Close', 'Cancel & Close'] # text for control buttons
    text_showinfo_cannot_delete_readonly = ("Info", "Cannot delete read-only data record!")
    text_askyesno_delete = ("Delete data record?", "Do you really want to delete this data record? \nData record : ")
    # extend tbed_.... to get a valid initialization of a new record that is conditioned on exam.key (because examofcourse has no direct link to exam)
    ntom_init_on_new     = None    # list of [col_to_be_initialized,col_initialized_by,where_cond]

###################################################################################################################
# SQLTableEditor
# consists of:
#    (1) choiceLB: a listbox to choose one data record from a database table (e.g., a SQLListbox)
#                  !!! first data entry of listbox should correspond to primary key of the table to be edited !!!
#    (2) recForm: a form to edit the record (e.g., a SupySQLForm)
#    (3) lbButtons: buttons to control the database table via the listbox:
#                   - New: Insert a new (default) record into the table
#                   - Copy: Insert a copy of the selected data recrod into the table
#                   - Delete: Delete the selected data record
#   (4) formButtons: buttons to control the record form:
#                   - Reset/Rollback: reset data record to the values of the last commit
#                   - Default: Set data record to default values
#                   - Commit: Commit data record to current input values
#   (5) ctrlRadioButtons: radio buttons to control the SQLTableEditor
#                    - view: read-only mode 
#                    - edit: edit (write) mode 
#   (6) ctrlButtons: buttons to control the SQLTableEditor
#                    - Commit & Close: Commit last inputs and close editor
#                    - Cancel & Close: Cancel last inputs and close editor
#   Extension as of 19/9/2016:
#   (7) extrabuttons = [[buttontext, buttonlocation, action],...]
#         - buttontext is text on buttons
#         - buttonlocation is currently only 'listboxleft' (on the left side of the listbox) possible
#         - action is a method that will be called if the button is pressed
###################################################################################################################

class SQLTableEditorFrame(Frame): 
    def __init__(self, parent, sqldatabase, cfg=SQLTableEditor_config, cond_on=[], extrabuttons=[]):
        Frame.__init__(self,parent)  
        # (i) basic initialization and flags
        self.parent=parent
        self.sqldatabase = sqldatabase
        self.cfg         = cfg
        self.conditioned_on = cond_on
        self.flag_readonly           =1  # default is read-only model (also set by self.on_ctrl_mode_readonly()
        self.extrabuttons_listboxleft=[e for e in extrabuttons if e[1]=='listboxleft']
        # (ii) allocate widgets
        # (ii.a) record form
        self.recFormFrame = Frame(self)
        self.recForm=SupySQLFormFrame(self.recFormFrame,self.sqldatabase,self.cfg.cfg_recForm,conditioned_on=cond_on)
        self.rfButtons_frame  = Frame(self.recFormFrame)
        self.rfButton_Reset   = Button(self.rfButtons_frame,text=self.cfg.recFormButtons_str[0],command=self.on_rf_reset)
        self.rfButton_Default = Button(self.rfButtons_frame,text=self.cfg.recFormButtons_str[1],command=self.on_rf_default)
        self.rfButton_Commit  = Button(self.rfButtons_frame,text=self.cfg.recFormButtons_str[2],command=self.on_rf_commit)
        # (ii.b) listbox 
        self.lbFrame=Frame(self)
        self.choiceLB=SQLListbox(self.lbFrame,self.sqldatabase,self.cfg.cfg_choiceLB,callback_select=self.on_lb_select,conditioned_on=cond_on)
        self.lbButtons_frame  = Frame(self)
        self.lbButtons_extra_left = [Button(self.lbButtons_frame,text=e[0],command=lambda : self.onExtraButton(e)) for e in self.extrabuttons_listboxleft]
        self.lbButtons_New    = Button(self.lbButtons_frame,text=self.cfg.lbButtons_str[0],command=self.on_lb_new)
        self.lbButtons_Copy   = Button(self.lbButtons_frame,text=self.cfg.lbButtons_str[1],command=self.on_lb_copy)
        self.lbButtons_Delete = Button(self.lbButtons_frame,text=self.cfg.lbButtons_str[2],command=self.on_lb_delete)
        # (ii.c) control panel
        self.ctrl_frame = Frame(self)
        self.var_ctrlRadioButton = IntVar()
        self.var_ctrlRadioButton.set(0)
        self.ctrlRadioButton_frame = Frame(self.ctrl_frame)
        self.ctrlRadioButton_view = Radiobutton(self.ctrlRadioButton_frame, text=self.cfg.ctrlRadioButtons_str[0], command=self.on_ctrl_mode_readonly,variable=self.var_ctrlRadioButton,value=0)
        self.ctrlRadioButton_edit = Radiobutton(self.ctrlRadioButton_frame, text=self.cfg.ctrlRadioButtons_str[1], command=self.on_ctrl_mode_edit    ,variable=self.var_ctrlRadioButton,value=1)
        self.ctrlButtons_frame = Frame(self.ctrl_frame)
        self.ctrlButton_CommitClose = Button(self.ctrlButtons_frame,text=self.cfg.ctrlButtons_str[0], command=self.on_ctrl_commitclose)
        self.ctrlButton_CancelClose = Button(self.ctrlButtons_frame,text=self.cfg.ctrlButtons_str[1], command=self.on_ctrl_cancelclose)
        # (ii.d) packing
        if self.cfg.align_widgets=='horizontal':
            # align widgets horizontally
            self.lbFrame.grid(row=0,column=0)          # lbFrame on self
            self.choiceLB.pack(side=TOP)               # lb on lbframe
            self.lbButtons_frame.grid(row=1, column=0) # lbButtons on self
            for b in self.lbButtons_extra_left: b.pack(side=LEFT)   # extrabuttons?
            self.lbButtons_New.pack(side=LEFT)         # buttons on lbButtons
            self.lbButtons_Copy.pack(side=LEFT)
            self.lbButtons_Delete.pack(side=LEFT)
            self.recFormFrame.grid(row=0,column=1)     # recFormFrame on self
            self.recForm.pack(side=TOP)
            self.rfButtons_frame.pack(side=BOTTOM)
            self.rfButton_Reset.pack(side=LEFT)
            self.rfButton_Default.pack(side=LEFT)
            self.rfButton_Commit.pack(side=LEFT)
            self.ctrl_frame.grid(row=1, column=1)      # ctrl panel on self
            self.ctrlButtons_frame.pack(side=RIGHT)    # ctrlButtonsFrame on ctrl panel
            self.ctrlButton_CancelClose.pack(side=RIGHT)
            self.ctrlButton_CommitClose.pack(side=RIGHT)
            self.ctrlRadioButton_frame.pack(side=RIGHT) # radiobuttons on ctrl panel 
            self.ctrlRadioButton_view.pack(side=LEFT)
            self.ctrlRadioButton_edit.pack(side=LEFT)
        else:
            # align widgets vertically
            pass
        # (iii) finish initialization of transaction control
        self.on_ctrl_mode_readonly()    # default is read-only mode
        
    """
    get_new_primary_key 
     - get new primary key for inserting a new data record into table
     - assumes that the first column of the table is the primary key!!!
     - here: assumes that the primary key has INTEGER-type
    """
    def get_new_primary_key(self):
        table_name = self.cfg.table_cfg.name          # name of the table
        pkey_col   = self.cfg.table_cfg.col_names[0]  # column name of primary key
        return self.sqldatabase.get_new_primary_key(table_name,pkey_col)[0]

    """
    commit_inputs
     - is called when inputs are committed
     - checks if there is an active transaction and commmits inputs (and sets transaction flag to zero)
    """
    def commit_inputs(self):
        if self.flag_readonly==0:  
            # (i) commit data of input widgets to database
            self.recForm.commit_inputs()
            # (ii) update listbox widget 
            table_name = self.cfg.table_cfg.name          # name of the table
            pkey_col   = self.cfg.table_cfg.col_names[0]  # column name of primary key
            where_expr = None                             # just in case of an empty table...
            if(self.choiceLB.selected_data!=None)and(self.choiceLB.selected_data!=[])and(len(self.choiceLB.selected_data[0])>0):
                pk = self.choiceLB.selected_data[0][0]        # it is assumed that primary key corresponds to first entry of listbox data
                where_expr = table_name+"."+pkey_col + " = " + str(pk)
            self.choiceLB.setListboxKeys(where_expr,flag_callback=False, flag_ignoreoldselection=True)   # update listbox, but no callback (to avoid recursion loop)
            
        
    """
    on_lb_select
     - is called if a selection from the choice listbox has been made
     - then: - save data from recFormFrame to database
             - display selected data
    """
    def on_lb_select(self,selected_data_idx,selected_data,selected_data_str):
        # (i) commit old input data (if necessary)
        self.commit_inputs()       # commit old transaction (if there is any)
        # (ii) get new selection and begin transaction (if necessary)
        if(selected_data!=None)and(selected_data!=[])and(len(selected_data[0])>0):
            self.recForm.setData([self.cfg.cfg_choiceLB.cols[0]],[selected_data[0][0]])

    """
    on_lb_new
     - is called on pressing the "New" Button 
     - then: - insert a new record into database (with new primary key and default values)
             - select new data record (and save old data from recForm)
    """
    def on_lb_new(self):
        if (self.cfg.min_max_records!=None) and (len(self.cfg.min_max_records)==2): 
            if self.choiceLB.data!=None and len(self.choiceLB.data)>=self.cfg.min_max_records[1]: return;     # ignore new-command if there are already the maximum number of records!
        success=0    # flag for success to commit new record
        # (i) commit old input data (if necessary)
        self.commit_inputs()       # commit old transaction (if there is any)
        # (ii) insert default record
        table_name = self.cfg.table_cfg.name          # name of the table
        pkey_col   = self.cfg.table_cfg.col_names[0]  # column name of primary key
        pk = self.get_new_primary_key()               # new primary key
        #print(" new primary key pk=", pk)
        cmd = 'insert into ' + table_name + ' (' + pkey_col + ' ) values (' + str(pk) + ')' 
        self.sqldatabase.begin_transaction()
        try:
            if(self.sqldatabase.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
            self.sqldatabase.curs.execute(cmd)
        except:
            str_error = "Insert Exception while inserting new record in table " + str(table_name) + ": \n\n" + str(sys.exc_info()) + \
                        "\n\nInsert query will be rolled-back."
            tkinter.messagebox.showerror(title="Insert Error", parent=self, message=str_error)
            self.sqldatabase.rollback_transaction()
        else:
            # (iii) set inherited (preconditioned) values
            print("\ncond.on=",self.conditioned_on)
            print("\nchoiceLB.tables=",self.choiceLB.tables)
            print("\nchoicLB.join_on=",self.choiceLB.join_on)
            c1,v1=getUniqueListOfPreconditions([],[],self.conditioned_on,self.choiceLB.tables,self.choiceLB.join_on)
            #c,v=[i[0] for i in self.conditioned_on], [i[1] for i in self.conditioned_on]
            print("\n\nafter getUniqueListOfPreconditions: onlb_new1: c1,v1=",c1,v1)
            c,v=getPreconditions4tables(c1,v1,[table_name])
            print("\n\nonlb_new2: c,v=",c,v)
            if len(c)>0: self.sqldatabase.simple_update_byPKEY(table_name,c,v,[pkey_col],[str(pk)])
            # (iv) check if there are (additional) ntom initializations
            if self.cfg.ntom_init_on_new==None:   
                success=1
            else:
                for jj in range(len(self.cfg.ntom_init_on_new)):
                    inon=self.cfg.ntom_init_on_new[jj]
                    assert isinstance(inon,list) and (len(inon)==4) and (not "." in inon[0]) and ("." in inon[1]) and ("." in inon[2]) and ("." in inon[3]), "Wrong format of list ntom_init_on_new=" + str(self.cfg.ntom_init_on_new) + \
                            " !\nInstead, each list entry self.cfg.ntom_init_on_new[i] must have format [col_in_tab2_to_be_initialized, tabnm.key, tabnm.key_to_tab1, tab1.key]" 
                    col_in_tab2_to_be_initialized=inon[0]
                    tabnm_key = inon[1]
                    tabnm_key_to_tab1 = inon[2]
                    tab1_key = inon[3]
                    tabnm=tabnm_key.split(".")[0]
                    keynm=tabnm_key.split(".")[1]
                    assert tab1_key in c1, "Cannot find tab1.key="+str(tab1_key)+" in preconditions " + str(c1) + " for ntom_init_on_new=" + str(self.cfg.ntom_init_on_new) + " !" 
                    val1_key = [v1[i] for i in range(len(c1)) if c1[i]==tab1_key][0]
                    wc = self.sqldatabase.getWhereClause_from_ColumnValues([tabnm],[tabnm_key_to_tab1],[val1_key])
                    res = self.sqldatabase.simple_select([tabnm_key],[tabnm],where=wc)
                    if (res==None) or (len(res)==0):
                        str_error="Cannot insert new record because there is no appropriate initialization!\n" + self.cfg.ntom_init_on_new_errormsg
                        tkinter.messagebox.showerror(title="Insert Error", parent=self, message=self.cfg.ntom_init_on_new_errormsg[jj])
                        self.sqldatabase.rollback_transaction()
                    else:
                        self.sqldatabase.simple_update_byPKEY(table_name,[col_in_tab2_to_be_initialized],[res[0][0]],[pkey_col],[str(pk)])
                        success=1
        # (v) select new data record
        if(success>0):
            self.sqldatabase.commit_transaction()
            self.choiceLB.setListboxKeys(table_name+"."+pkey_col + " = " + str(pk), flag_ignoreoldselection=True)

    """
    on_lb_copy
     - is called on pressing the "Copy" Button 
     - then: - insert a new record into database being a copy of the current data record 
             - select new data record (and save old data from recForm)
    """
    def on_lb_copy(self):
        if (self.cfg.min_max_records!=None) and (len(self.cfg.min_max_records)==2): 
            if self.choiceLB.data!=None and len(self.choiceLB.data)>=self.cfg.min_max_records[1]: return;     # ignore copy-command if there are already the maximum number of records!
        if (self.choiceLB.selected_data!=None) and (len(self.choiceLB.selected_data)>0) and (len(self.choiceLB.selected_data[0])>0): # is there selected data to be copied??
            # (i) commit old input data (if necessary)
            self.commit_inputs()       # commit old transaction (if there is any)
            # (ii) insert new record that contains copy of the current data
            table_name = self.cfg.table_cfg.name          # name of the table
            table_cols = self.cfg.table_cfg.col_names     # columns of the table
            pkey_col   = self.cfg.table_cfg.col_names[0]  # column name of primary key
            pk_new = self.get_new_primary_key()           # new primary key
            pk_old = self.choiceLB.selected_data[0][0]    # it is assumed that primary key corresponds to first entry of listbox data
            cols2copy = [c for c in table_cols[1:] if (self.cfg.cfg_recForm.cols2copy==None) or (c in self.cfg.cfg_recForm.cols2copy)]  # columns to be copied (without primarky key)
            cols2copy = [pkey_col] + cols2copy    # columns to be copied (with primary key at pos 0)
            wc=self.sqldatabase.getWhereClause_from_ColumnValues([table_name],[pkey_col],[pk_old])
            rec=self.sqldatabase.simple_select(cols2copy,[table_name],where=wc)      # old column data (including primary key at pos 0)
            assert (len(rec)==1)and(len(rec[0])==len(cols2copy)), \
                " Cannot create copy of columns " + cols2copy + " for table " + str(table_name) + " because of primary key mismatch!\nResult record for primary key=" + str(pk_old) + " is " + str(rec)
            rec=list(rec[0])                              # copy of record
            rec[0]=pk_new                                 # replace primary key by new one
            self.sqldatabase.begin_transaction()          # do insertion transaction
            try:
                self.sqldatabase.simple_insert(table_name,cols2copy,rec)    # insert new record
            except:
                str_error = "Insert Exception while inserting copy record in table " + str(table_name) + ": \n\n" + str(sys.exc_info()) + \
                            "\n\nInsert query will be rolled-back."
                tkinter.messagebox.showerror(title="Insert Error", parent=self, message=str_error)
                self.sqldatabase.rollback_transaction()
            else:
                self.sqldatabase.commit_transaction()
            # (iii) copy cascade in related tables (by ref_ntom)
            form_cfg=self.cfg.cfg_recForm
            for i in range(len(form_cfg.cols)):
                if (form_cfg.cols[i]==None)and(form_cfg.cols_type[i]=='ref_ntom')and(form_cfg.cols_readonly[i]==0):
                    ntom_cc=form_cfg.cols_ref[i].ntom_copy_cascade    # defnition of copy cascade behavior in format:
                    if (ntom_cc!=None):                               #     [(table1,key1),(tablenm,keynm,foreignkey,[list of columns to be copied])]
                        # (iii.1) decode ntom_copy_cascade parameters...
                        cc_tab1 ,cc_key1                                    = ntom_cc[0][0],ntom_cc[0][1]
                        cc_tabnm,cc_keynm,cc_keynm_foreigntab1,cc_cols2copy = ntom_cc[1][0],ntom_cc[1][1],ntom_cc[1][2],ntom_cc[1][3]
                        assert cc_tab1==table_name and cc_key1==pkey_col, "Mismatch during copy cascade of table "+table_name+" with primary key " + pkey_col + " with invalid ntom_copy_cascade=" + str(ntom_cc) + "!"
                        # (iii.2) get all records of tabnm that are associated with old record in tab1 where key1=pk_old
                        wc=self.sqldatabase.getWhereClause_from_ColumnValues([cc_tabnm],[cc_keynm_foreigntab1],[pk_old])
                        oldrecs=self.sqldatabase.simple_select(cc_cols2copy,[cc_tabnm],where=wc)      # records in tabnm associated with tab1.pk_old
                        print("\n\n oldrecs=", str(oldrecs))
                        # (iii.3) for each such record, insert a copy associated with tab1.pk_new
                        for orc in oldrecs:
                            print("\norc = ", orc)
                            cc_tabnm_pk_new = self.sqldatabase.get_new_primary_key(cc_tabnm,cc_keynm)[0]    # new primary key for tabnm
                            self.sqldatabase.simple_insert(cc_tabnm, [cc_keynm,cc_keynm_foreigntab1]+cc_cols2copy, [cc_tabnm_pk_new,pk_new]+list(orc))
            # (iv) select new data record
            self.choiceLB.setListboxKeys(table_name+"."+pkey_col + " = " + str(pk_new), flag_ignoreoldselection=True)

    """
    on_lb_delete
     - delete selected data record 
     - then: - select next data record (of listbox)
    """
    def on_lb_delete(self):
        if (self.cfg.min_max_records!=None) and (len(self.cfg.min_max_records)==2): 
            if self.choiceLB.data!=None and len(self.choiceLB.data)<=self.cfg.min_max_records[0]: return;     # ignore delete-command if there are only the minimum number of records in the table!
        if (self.choiceLB.selected_data!=None) and (len(self.choiceLB.selected_data)>0) and (len(self.choiceLB.selected_data[0])>0): # is there selected data to be deleted??
            # (i) check if data record should really be deleted
            pk = self.choiceLB.selected_data[0][0]       # it is assumed that primary key corresponds to first entry of listbox data
            if(self.cfg.pkeys_readonly!=None)and(pk in self.cfg.pkeys_readonly):
                tkinter.messagebox.showinfo(self.cfg.text_showinfo_cannot_delete_readonly[0], self.cfg.text_showinfo_cannot_delete_readonly[1], parent=self)
            elif tkinter.messagebox.askyesno(self.cfg.text_askyesno_delete[0],self.cfg.text_askyesno_delete[1] + self.choiceLB.selected_data_str[0] + " ?"):
                # (ii) delete data record
                table_name = self.cfg.table_cfg.name          # name of the table
                pkey_col   = self.cfg.table_cfg.col_names[0]  # column name of primary key
                self.sqldatabase.begin_transaction()          # do delete transaction
                try:
                    self.sqldatabase.simple_delete(table_name,[pkey_col],[pk])
                except:
                    str_error = "Delete Exception while deleting record in table " + str(table_name) + ": \n\n" + str(sys.exc_info()) + \
                                "\n\nDelete query will be rolled-back."
                    tkinter.messagebox.showerror(title="Delete Error", parent=self, message=str_error)
                    self.sqldatabase.rollback_transaction()
                else:
                    self.sqldatabase.commit_transaction()
                # (iii) select neighboring data record
                i=self.choiceLB.selected_data_idx[0]
                pk_next=None
                if len(self.choiceLB.data)>(i+1):
                    pk_next = self.choiceLB.data[i+1][0]
                elif i>0:
                    pk_next = self.choiceLB.data[i-1][0]
                wc=None
                if(pk_next!=None): wc = table_name+"."+pkey_col + " = " + str(pk_next)
                self.choiceLB.setListboxKeys(wc, flag_ignoreoldselection=True)

    """
    on_rf_reset
     - reset (non-primary-key) form data to values stored in database 
    """
    def on_rf_reset(self):
        if(self.choiceLB.selected_data!=None) and (len(self.choiceLB.selected_data)>0):
            self.recForm.setData([self.cfg.cfg_choiceLB.cols[0]],[self.choiceLB.selected_data[0][0]])

    """
    on_rf_default
     - reset (non-primary-key) form data to default values  
    """
    def on_rf_default(self):
        rf_cfg=self.cfg.cfg_recForm
        data_default = self.sqldatabase.simple_select_defaultvalues(rf_cfg.cols,rf_cfg.tables)
        print("data_default=", data_default)
        for i in range(len(data_default)):
            if (i>0) and (data_default[i]!=None):                # skip first (primary key) column and None-data
                self.recForm.setEntryData(i,data_default[i])

    """
    on_rf_commit
     - commit form data data into sql database   
    """
    def on_rf_commit(self):
        self.commit_inputs()

    """
    on_ctrl_mode_readonly
     - enter read-only mode    
    """
    def on_ctrl_mode_readonly(self):
        # (i) commit old inputs (if necessary) and set readonly flag
        self.commit_inputs()
        self.flag_readonly=1
        # (ii) disable record form widgets
        self.recForm.disableWidgets()
        self.rfButton_Reset.configure(state=DISABLED)
        self.rfButton_Default.configure(state=DISABLED)
        self.rfButton_Commit.configure(state=DISABLED)
        # (iii) disable listbox widgets
        self.lbButtons_New.configure(state=DISABLED)
        self.lbButtons_Copy.configure(state=DISABLED)
        self.lbButtons_Delete.configure(state=DISABLED)
        # (iv) disable control panel widgets
        self.ctrlButton_CommitClose.configure(state=DISABLED)

    """
    on_ctrl_mode_edit
     - enter edit (read&write) mode    
    """
    def on_ctrl_mode_edit(self):
        # (i) set readonly flag
        self.flag_readonly=0
        # (ii) disable record form widgets
        self.recForm.enableWidgets()
        self.rfButton_Reset.configure(state=NORMAL)
        self.rfButton_Default.configure(state=NORMAL)
        self.rfButton_Commit.configure(state=NORMAL)
        # (iii) disable listbox widgets
        self.lbButtons_New.configure(state=NORMAL)
        self.lbButtons_Copy.configure(state=NORMAL)
        self.lbButtons_Delete.configure(state=NORMAL)
        # (iv) disable control panel widgets
        self.ctrlButton_CommitClose.configure(state=NORMAL)

    """
    on_ctrl_commitclose
     - commit form values and close     
    """
    def on_ctrl_commitclose(self):
        self.recForm.commit_inputs()
        self.parent.commitclose=1
        self.destroy()

    """
    on_ctrl_cancelclose
     - cancel form values and close     
    """
    def on_ctrl_cancelclose(self):
        self.destroy()

    """
    onExtraButton
     - extra actions if one of the extra buttons have been pressed
     - e is in the format [buttontext, buttonlocation, action]
     - buttontext is actually ignored!     
    """
    def onExtraButton(self,e):
        assert isinstance(e,(list,tuple)) and len(e)==3, "extra-action description must be in format [buttontext, buttonlocation, action]"
        assert e[1] in ['listboxleft'], "Unknown button location "+str(e[1])
        f=e[2]
        if e[1]=='listboxleft': f(self.choiceLB) 

def editSQLTables(parent, sqldatabase, title=None, cfg=SQLTableEditor_config,cond_on=[], extrabuttons=[], flagIndepFromParent=0):  # for parameters see SQLListboxForm_config
    if title==None: title=cfg.title
    top=Toplevel()
    top.commitclose=0
    if(flagIndepFromParent<=0): 
        top.grab_set()    # make window modal (i.e., redirect all inputs from parent window to listbox dialog)
        if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SQLTableEditorFrame(top,sqldatabase, cfg, cond_on, extrabuttons)
    f.pack()
    top.wait_window(f)
    ret_val=top.commitclose         # =1 if committed (otherwise 0)
    top.destroy()
    return ret_val


""" 
editSQLTable_ntom_simple: link to tables via a simple n-to-m table (that contains only primary keys)
cfg must contain fields:
   ntom_table1, ntom_key1='student','key'                 : master table and its primary key
   ntom_table2,ntom_key2='minority','key'                 : slave table and key
   ntom_tablenm = 'minorityofstudent'                     : n-to-m table
   ntom_tablenm_cols=['key','key_student','key_minority'] : primary key, key name of table 1, key name of table 2 
"""
def editSQLTable_ntom_simple(parent, sqldatabase, title=None, cfg=None, key1_val=None):  # for parameters see SQLListboxForm_config
    assert cfg!=None and key1_val!=None, "editSQLTable_ntom_simple(parent,sqldatabase,titel,cfg,cond_on): Parameter cfg must not be 'None'"
    # (i) determine old selection
    tab1,key1                    = cfg.ntom_table1, cfg.ntom_key1
    tab2,key2                    = cfg.ntom_table2, cfg.ntom_key2
    tabnm, keynm, keynm1, keynm2 = cfg.ntom_tablenm, cfg.ntom_tablenm_cols[0], cfg.ntom_tablenm_cols[1], cfg.ntom_tablenm_cols[2]
    tabs    = [tab1,tab2,tabnm]    # list of all 3 tables
    join_on = [tab1+"."+key1+"="+tabnm+"."+keynm1, tab2+"."+key2+"="+tabnm+"."+keynm2]      # list of join conditions of the three tables
    wc=sqldatabase.getWhereClause_from_ColumnValues([tab1],[tab1+"."+key1],[key1_val])      # where-condition to select primary key key1_val 
    oldsel = sqldatabase.simple_select([tabnm+"."+keynm,tabnm+"."+keynm1,tabnm+"."+keynm2],tabs,join_on,wc) # old selection in format res=[(keynm,keyval1,keyval2,),(keynm,keyval1,keyval2,),...]   
    # (ii) invoke SQLListbox 
    oldsel_t2keys = [os[2] for os in oldsel]                                               # list of table2-keys (for preselection of listbox items)
    key2val_impossible=sqldatabase.get_new_primary_key(tab2,key2)[0]                       # impossible key for OR-Expression below (to avoid selection of all if oldsel_t2keys==[])
    where_init=sqldatabase.getWhereClause_from_ColumnValues([tab2],[tab2+"."+key2]+[tab2+"."+key2 for i in oldsel_t2keys],[key2val_impossible]+oldsel_t2keys,oper="OR")
    newsel = askSQLListboxForm(sqldatabase,cfg.link_ntom_listbox_cfg,where_init=where_init)[0] # new selection in format [(keyval2_0,val_0), (keyval2_1,val_1),...]
    if newsel==None:
        return 0
    else:
        newsel_t2keys = [ns[0] for ns in newsel]
        # (iii) determine items to be inserted and/or deleted 
        to_delete = []                   # keys of t2-items to be deleted
        for i in range(len(oldsel)):
            if not oldsel_t2keys[i] in newsel_t2keys:
                to_delete = to_delete + [oldsel_t2keys[i]]
        to_insert = []                   # t2-keys to be inserted (in association with key1=key1_val)
        for i in range(len(newsel)):
            if not newsel_t2keys[i] in oldsel_t2keys:
                to_insert = to_insert + [newsel_t2keys[i]]
        # (iv) insert/delete items (if necessary)
        for k in to_delete:
            print("deleting k=", k)
            sqldatabase.simple_delete(tabnm,[keynm1,keynm2],[key1_val,k])
        for k in to_insert:
            pk=sqldatabase.get_new_primary_key(tabnm)[0]
            sqldatabase.simple_insert(tabnm,[keynm,keynm1,keynm2],[pk,key1_val,k])
        return 1


##################################################################################################################################################################
##################################################################################################################################################################
# Part II: Module test
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
        rows_default     = ["(0,'N.N.'   , 'N.N.')", \
                            "(1,'Müller' , 'Musterweg 5    ; 72475 Musterstadt')", \
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
        rows_default     = ["(0,'N.N.'   )", \
                            "(1,'Mathe'  )", \
                            "(2,'English')", \
                            "(3,'Biology')"]

    class tb_exam_cfg(Table_cfg):
        name = 'exam'
        # column definitions
        col_names           = ['id'         ,'id_student'       ,'id_course','grade']
        col_types           = ['INTEGER'    ,'INTEGER'          ,'INTEGER'  ,'TEXT']
        col_references      = [None         ,'student'          ,'course'   ,None   ]
        #col_constraints     = ['PRIMARY KEY','NOT NULL'         ,'NOT NULL' ,None   ]
        col_constraints     = ['PRIMARY KEY',None               ,None       ,None   ]
        col_ref_constraints = [None         ,'ON DELETE CASCADE',None       ,None   ] 
        col_defaults        = [None         , 0                ,0       ,'"N.N."'        ]
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

    print("\nModule test of supylib module supy.sqltableeditor.py")
    print("---------------------------------------------------------\n") 
    db = sqldatabase(db_dummy_cfg)
    db.print_database(1)

    
    class lb_EXAM_student_cfg(SQLListboxForm_config):
        tables = ['student']
        cols   = ['student.id', 'student.name']
        cols_format = ['5d','10s:10']
        cols_sortbutton = ['ID','NAME']
        where = None
        where_init = None
        colvals2str = colvals2str_default
        sep = ' | '
        width = 35
        height = 10
        lbfont = ('courier',12,'normal')
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
        button_str = ['Ok','Cancel']
        title      = 'lb_EXAM_course'

    class lb_EXAM_cfg(SQLListboxForm_config):
        tables = ['exam','student','course']
        join_on = ['student.id=exam.id_student', 'course.id=exam.id_course']
        cols   = ['exam.id', 'student.name', 'course.course']
        cols_format = ['5d','10s:10', '10s:10']
        cols_sortbutton = ['ID','STUD','COURSE']
        where = None
        where_init = None
        colvals2str = colvals2str_default
        sep = ' | '
        width = 40
        height = 10
        lbfont = ('courier',12,'normal')
        button_str = ['Ok','Cancel']
        title      = 'lb_EXAM'



    class db_sql_form_cfg(SupySQLForm_config):
        tables                = ['exam','student','course']
        join_on               = ['student.id=exam.id_student', 'course.id=exam.id_course']
        cols                  = ['exam.id', 'exam.id_student'  , 'exam.id_course', 'exam.grade']
        cols_type             = ['str'    , 'ref'              , 'ref'           , 'optionlist']
        cols_ref              = [None     , lb_EXAM_student_cfg, lb_EXAM_course_cfg, ['N.N.','1.0','1.3','1.7','2.0','2.3','2.7','3.0','3.3','3.7','4.0','4.7','5.0']]
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
        title      = 'SupySQLForm...'                                 # is used only for askSupySQLForm

    db.print_database(1)
    res = askSupySQLForm(db,db_sql_form_cfg)
    print("Result:", res)
    db.print_database(1)

    # **************************
    class sql_table_editor_cfg(SQLTableEditor_config):
        table_cfg          = tb_exam_cfg        # table to be edited, first column is assumed to be primary key of type INTEGER!!!
        pkeys_readonly     = [0]                # records with primary key in this list are considered as READ_ONLY (e.g., for default records)
        cfg_choiceLB       = lb_EXAM_cfg        # configuration for choice listbox (typically a SQLListbox_config)
        cfg_recForm        = db_sql_form_cfg    # configuration for record form (typically a SupySQLForm_config)
        align_widgets      = 'horizontal'       # either 'vertical' or 'horizontal' for alignment of listbox and form
        lbButtons_str        = ['New', 'Copy', 'Delete']            # text for listbox buttons
        recFormButtons_str   = ['Reset', 'Default', 'Commit']       # text for form buttons
        ctrlRadioButtons_str = ['View', 'Edit']                     # text for radiobuttons (read-only, write/edit option)
        ctrlButtons_str      = ['Commit & Close', 'Cancel & Close'] # text for control buttons
        text_showinfo_cannot_delete_readonly = ("Info", "Cannot delete data record because it is read-only!")
        text_askyesno_delete = ("Delete Record?", "Do you really want to delete the selected record: ")
    #r=Tk()
    r=None 
    resxx = editSQLTables(r,db,"title hallo XXX",sql_table_editor_cfg)
