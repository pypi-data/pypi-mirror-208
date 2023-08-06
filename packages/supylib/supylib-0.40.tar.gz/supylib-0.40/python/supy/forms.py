#!/usr/bin/python
# -*- coding: utf-8 -*-

############################################################
# a reusable form class
############################################################
     
from Tkinter import *
import tkMessageBox
import tkFileDialog
import os,time,datetime

class SupyForm:                                           # add non-modal form box
    def __init__(self, labels, default_entries=None, parent=None,labelanchor='w',labelwidth=None,entrysize=40,pos=None,
                 flagButtons=1,options=None,paths_relative_to=os.getcwd(),browse_callback=None,
                 help_event="<F1>",help_texts=None,help_callback=None):        # pass field labels list
        '''
        labels: list of strings where labels[i] is the label of the i-th input field
        default_entries: list of default entries that are displayed initially in the input field
        parent: parent widget
        labelanchor: aliggnment of label
        labelwidth: width of label fields, either a None, a single number, or a list (for each input field)
        entrysize: width of entry fields, either a single number or a list (for each input field)
        pos: either None or list; pos[i]=(x,y) is grid position for i-th label etc.  
        flagButtons: If >0 then buttons are displayed for submit/cancel actions 
        options: either None or a list where options[i] is either 'filename' or None or a string list for a Optionmenu
        paths_relative_to: save browsed paths relative to this path
        browse_callback(idx): function that is called after selecting a filename, parameter idx is field index
        help_event: event that evokes help function (e.g., pressing F1 over the label)
        help_texts: either None or list of help strings for each label
        help_call : either None (then default call is used) or function 
        '''
        self.parent=parent
        if(pos==None):
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
            if(help_texts!=None) and (help_texts[i]!=None):
                if(help_callback==None):
                    help_callback=self.displayHelpMessage_default
                lb.bind(help_event,lambda ev,txt=help_texts[i]: help_callback(txt))
            if(options==None)or(options[i]==None)or(options[i]=='filename')or(options[i]==[]):                
                entry = Entry(formbox, textvariable=self.entry_vars[i], width=entrysize[i], 
                              bg="white", disabledforeground='black')
            else:
                entry = OptionMenu(formbox,self.entry_vars[i],*options[i])
                entry.config(width=int(0.88*entrysize[i]), disabledforeground='black')
            self.content[labels[i]] = entry
            if default_entries and (len(default_entries)>=(i+1)):
                self.setEntryText(i,default_entries[i])                
            entry.grid(row=row_label,column=column_label+1) # side=TOP, expand=YES, fill=X)
            if(options!=None)and(options[i]=='filename'):
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
        s=tkFileDialog.askopenfilename(initialdir=directory, initialfile=filename)
        if(s!=None)and(s!="")and(s):
            s=os.path.relpath(s,self.paths_relative_to)
            self.setEntryText(i,s)
            if(self.browse_callback!=None):
                self.browse_callback(i)

    def onSubmit(self):                                      # override this
        for key in self.content.keys():                      # user inputs in 
            print key, '\t=>\t', self.content[key].get()     # self.content[k]
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
        
def askSupyForm(labels,default_entries=None,parent=None,title=None,labelanchor='w',labelwidth=None,entrysize=40):      
    top=Toplevel(parent)
    if parent: top.transient(parent)       # make window transient, e.g., minmize with parent etc.
    if title: top.title(title) 
    f=SupyForm(labels,default_entries,top,labelanchor,labelwidth,entrysize)
    top.wait_window(f.box)
    top.destroy()
    return f.results

# *****************************
# slider for dates
# *****************************
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
        if (self.command !=None) and (initFlag==0):
            self.command(value)

    def get(self):
        return self.current_date


    
# *****************************
# slider for dates
# *****************************
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
            print key, '\t=>\t', self.content[key].get()     # self.content[k]
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

if __name__ == '__main__':
    root=Tk()
    s=DateSlider(root)
    s.pack(side=TOP)
    # Example 1: SupyFrom
    labels=['Name', 'Age', 'Job']
    defaults=['Fridolin','40',u"Großer Mandarin"]
    r=askSupyForm(labels,defaults,root,"Python ask form ...",'e',30,40)
    print r
    # Example 2: SupySliderFrom
    labels=['var1','var2','var3','date']
    defaults=[3,14,5,datetime.date(2012,11,21)]
    ranges=[(0,10,1),(10,20,2),(5,10,0.1),(datetime.date(2012,1,1),datetime.date(2012,12,31))]
    r=askSupySliderForm(labels,defaults,ranges,root,"Slider Form example",'e',None,30,40)
