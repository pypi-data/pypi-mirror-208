#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import supy.serialize

###################################################################################################
# database.py
#
# Simple database class for persistent storage of data records in files
# 
# Type of data is defined by a list of attribute definitions
#     Each attribute i has a name attr_names[i] and a type attr_types[i] being either 'string' or 'json'  
#     Type 'json' means that the data can be of any Python type, where
#     'json' data gets converted into a string by using json.dump() when storing in a file
#     Thus, type 'json' is typically used for any data type other than 'string' (e.g., numbers, lists, etc.)
# 
# Each database record consists of a number of data entries, i.e., one data entry for each attribute.
# The first data entry (corresonding to the frist attribute) is defined to be the key of the data record.
# The first attribute is also called the key attribute.
#
# The database stores an arbitrary number of data records in a dictionary (db) 
# Data records can be accessed via their key attribute data value, 
# i.e., get_record(key) which returns a list of all data entries (including the key)
# similarly, get_entry(attr_name,key) returns a single entry, i.e., the data entry corresponding
# to a certain attribute with name attr_name.
# 
# If flag_singleton is set then the database is forced to contain exactly one data record.
#
# 28.3.2013 - 7.4.2013 by Andreas Knoblauch
###################################################################################################

class Database_config:
    attr_names     = ['id'    ,'image' ,'sound1','sound2','info'  ,'imagesize'] # list of attribute names
    attr_types     = ['string','string','string','string','string','json'] # list of attribtute types ('string' or 'json')
    default_record = ['__new_key_','','','','',[100,100]]                  # for example, for adding a new data record
    encoder = supy.serialize.SupyEncoder                                   # json.JSONEncoder for serializing database objects and classes
    decoder = supy.serialize.SupyDecoder                                   # json.JSONDecoder for de-serializing database objects and classes
    readonly_record_keys = []                                              # records with these keys cannot be deleted!!             
    flag_singleton = 0                    # if set then the database contains exactly one data record!!
    default_filename = 'dummy.db'         # default file name of database
    flag_RAM_only    = 0                  # if set then database is kept only in RAM (never read/written to disk) 

class Database:
    def __init__(self,cfg=Database_config, filename=None, db=None, **args):
        self.cfg=cfg
        self.filename=filename
        if(self.filename==None): self.filename=self.cfg.default_filename
        self.flagEnableCallbacks=0                # no callbacks during creation!
        self.attr_n    = len(self.cfg.attr_names) # number of attributes
        self.key_name  = self.cfg.attr_names[0]   # first attribute is key attribute name
        self.db = db
        if(self.db==None):
            self.db = {}                          # empty database
            if not self.cfg.flag_RAM_only:        
                self.load()                       # for non-RAM databased try to load database from file
        self.checkSingleton()                     # check singleton
        self.attr_dict = {self.cfg.attr_names[i]:i for i in range(self.attr_n)}
        self.callbacks_DeletedRecord      =[]     # list of callbacks when a record was deleted
        self.callbacks_InsertedRecord     =[]     # list of callbacks when a record was inserted
        self.callbacks_ModifiedRecord     =[]     # list of callbacks when a record was modified
        self.callbacks_ReorganizedDatabase=[]     # list of callbacks after major reorganization of database 
        self.callbacks_SaveDatabase       =[]     # list of callbacks after call to save (that is intercepted due to flag_RAM_only) 
        self.callbacks_LoadDatabase       =[]     # list of callbacks after call to load (that is intercepted due to flag_RAM_only) 
        self.enableCallbacks()                    # now enable callbacks
        self.flagModified=0                       # if set then there is need to save database

    def enableCallbacks(self,flag=1):             # set callback flag and return old flag
        oldflag=self.flagEnableCallbacks
        self.flagEnableCallbacks=flag
        return oldflag

    def bind(self,eventlist,callback):
        if not isinstance(eventlist,list):
            eventlist = [eventlist]
        for e in eventlist:
            if   e=="<deleted-record>"      : self.callbacks_DeletedRecord      .append(callback)
            elif e=="<inserted-record>"     : self.callbacks_InsertedRecord     .append(callback)
            elif e=="<modified-record>"     : self.callbacks_ModifiedRecord     .append(callback)
            elif e=="<reorganized-database>": self.callbacks_ReorganizedDatabase.append(callback)
            elif e=="<request-to-save-database>": self.callbacks_SaveDatabase   .append(callback)
            elif e=="<request-to-load-database>": self.callbacks_LoadDatabase   .append(callback)
            else:
                raise TypeError, "bind: Unknown event type!"

    def do_callbacks(self,eventlist,key=None):
        if self.flagEnableCallbacks:
            for e in eventlist:
                if   e=="<deleted-record>"   : 
                    for cb in self.callbacks_DeletedRecord      : cb(key)
                elif e=="<inserted-record>"  : 
                    for cb in self.callbacks_InsertedRecord     : cb(key)
                elif e=="<modified-record>"  : 
                    for cb in self.callbacks_ModifiedRecord     : cb(key)
                elif e=="<reorganized-database>": 
                    for cb in self.callbacks_ReorganizedDatabase: cb()
                elif e=="<request-to-save-database>": 
                    for cb in self.callbacks_SaveDatabase       : cb()
                elif e=="<request-to-load-database>": 
                    for cb in self.callbacks_LoadDatabase       : cb()
                else:
                    raise TypeError, "do_callbacks: Unknown event type!"

    def size(self):           
        ''' 
        returns total number of data records that are stored in the database
        '''
        return len(self.db)

    def checkSingleton(self,keep_key=None):                 
        '''
        If flag_singleton is true then enforce the database to be a singleton (with exactly one entry)
        If database is empty a new default record is added
        If database has more then one record then all records are deleted except keep_key or (if None) the first key 
        '''
        if(self.cfg.flag_singleton):
            n=self.size() 
            if(n!=1):
                if n==0:                       # if database is empty then add default entry
                    self.add_default_record()
                elif n>1:                      # if database has more than one entry then delete all except first
                    keys = self.get_list_of_keys()
                    if (keep_key==None) or not(keep_key in keys):
                        for i in range(len(keys)-1):
                            self.delete_record(keys[i+1])
                    else:
                        keys.remove(keep_key)
                        for k in keys:
                            self.delete_record(k)
            
    def get_record(self,key=None):               
        '''
        returns data record with given key; if key=None then return first data record
        '''
        if(key==None):
            key = self.get_first_key() 
        if(key in self.db):
            return [key] + self.db[key]
        else:
            return None

    def get_record_str(self,key=None):               
        '''
        similar as get_record but returns list of strings (obtained by json) 
        '''
        c = self.get_record(key)
        if(c!=None):
            for i in range(self.attr_n):
                if self.cfg.attr_types[i]=='json':
                    c[i]=json.dumps(c[i])
        return c

    def get_record_entry(self,attr_name=None, key=None):
        '''
        returns data record entry with given key and attribute name
        if attr_name and/or key==None then just take first entry and/or key, respectively
        '''
        if(key==None):
            key = self.get_first_key()
        if(attr_name==None):
            attr_name = self.key_name
        res=None
        if(key in self.db) and (attr_name in self.attr_dict):
            idx=self.attr_dict[attr_name]   # attr index
            res=self.get_record(key)[idx]
        return res
            
    def set_record(self,*record):
        '''
        write record to database
        record parameters must be in order of attr_names
        only and final method that can insert or modify a data record in the database 
        thus, this method is responsible for organizing corresponding callbacks
        '''
        assert len(record)==self.attr_n, "Invalid record length in call to set_record() for database " \
            + self.filename + " ! Record length is " + str(len(record)) + ", but attribute list has length " \
            + str(self.attr_n) + "!"
        key=record[0]
        flagInsert=0
        if (key not in self.db) and ((not self.cfg.flag_singleton) or (self.size()==0)):   # is it really an insertion??
            flagInsert=1
        self.db[key]=list(record[1:])
        self.checkSingleton(key)      # may delete a record (if singleton)
        self.flagModified=1
        if(flagInsert>0 ): self.do_callbacks(['<inserted-record>'],key)
        if(flagInsert==0): self.do_callbacks(['<modified-record>'],key) 

    def set_record_str(self,record_str,check_only=0):  # entry_str is list of strings
        '''
        write record given by list of strings to database
        json attributes are transformed via json.loads
        '''
        assert len(record_str)==self.attr_n, "Invalid record length in call set_record_str() for database " + self.filename
        record=[None for i in range(self.attr_n)]
        for i in range(len(record_str)):
            if self.cfg.attr_types[i]=='string':
                record[i]=record_str[i]
            else:
                try:
                    record[i]=json.loads(record_str[i])
                except ValueError as e:
                    print "Error during json.loads with argument ", record_str[i], " !\n"
                    raise e
        if not check_only:
            self.set_record(*record)

    def set_record_entry(self,attr,key,entry):
        idx = self.attr_dict[attr]  
        rec = self.get_record(key)
        rec[idx] = entry
        self.set_record(*rec)

    def set_default_record(self,key=None):
        '''
        Set record with given key to the default record entries of self.cfg.default_record
        '''
        record = [self.cfg.default_record[i] for i in range(self.attr_n)]    # shallow copy
        if(key!=None):
            record[0]=key
        self.set_record(*record)

    def add_default_record(self):
        '''
        adds new record with new unique key to the (otherwise) default record entries of self.cfg.default_record
        and returns new key
        '''
        # (i) find a new dummy-key-name, e.g., "__new_item_XXX__"
        keys = self.get_list_of_keys()
        i=0
        new_key_prefix=self.cfg.default_record[0]
        new_key_postfix="__"
        while 1:
            i=i+1
            new_key = new_key_prefix + str(i) + new_key_postfix
            if not(new_key in keys): 
                break
        # (ii) insert new default entry and return new key
        self.set_default_record(new_key)
        return new_key
        
    def delete_record(self,key):
        '''
        delete record with given key
        returns 1 if delete operation was successfull
        and 0 otherwise 
        '''
        if (key in self.db) and (key not in self.cfg.readonly_record_keys):
            del self.db[key]
            self.do_callbacks(['<deleted-record>'],key) 
            self.checkSingleton()     # may add a new record
            self.flagModified=1
            return 1
        else:
            return 0
        
    def delete_all_records(self):
        '''
        delete all data record of the database
        '''
        old=self.enableCallbacks(0)
        keys = self.get_list_of_keys()    # keep keys
        for k in keys:
            self.delete_record(k)
        self.enableCallbacks(old)
        self.do_callbacks(['<reorganized-database>'])
        self.flagModified=1

    def load(self,filename=None,blockMultipleCallbacks=0):
        '''
        load database from file with name self.filename
        '''
        if self.cfg.flag_RAM_only:
            self.do_callbacks(['<request-to-load-database>'])
        else:
            if filename==None:
                filename=self.filename
            try:
                f=open(filename,'r')
            except IOError as e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
                if(self.cfg.flag_singleton):
                    print "I will add single default entry to empty database", self.filename
                else:
                    print "I will set database ", self.filename, " to empty database."
                old=self.enableCallbacks(0)
                self.delete_all_records()       # sets db to {} or adds single default entry
                self.enableCallbacks(old)
                self.flagModified=0
            except:
                print "Unexpected error while loading database ", self.filename, ":", sys.exc_info()[0]
                raise
            else:
                self.db = json.load(f,cls=self.cfg.decoder)
                if(self.cfg.flag_singleton):
                    n=self.size()
                    if(n==0):
                        print "Loaded empty database ", self.filename, "!"
                        print "I will add default data record."
                    if(n>1):
                        print "Singleton Database ", self.filename, " has more than one data record!"
                        print "I will erase all data records except the first one."
                self.checkSingleton()
                self.do_callbacks(['<reorganized-database>'])
                self.flagModified=0
        
    def save(self,filename=None):
        if self.cfg.flag_RAM_only:
            self.do_callbacks(['<request-to-save-database>'])
        else:
            if(filename!=None):
                self.filename=filename
            try:
                f=open(self.filename,'w')
            except IOError as e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
                print "Unable to save database ", self.filename
            except:
                print "Unexpected error while trying to save database ", self.filename, ":", sys.exc_info()[0]
                raise
            else:
                json.dump(self.db,f,cls=self.cfg.encoder)
                f.flush()
                self.flagModified=0

    def get_list_of_keys(self):
        keys = self.db.keys()
        keys.sort()
        return keys

    def get_first_key(self):
        keys = self.get_list_of_keys()
        if(len(keys)>0):
            key=keys[0]
        else:
            key=None
        return key

    def print_database(self,indent=0,indent_inc=3):
        list_of_keys = self.get_list_of_keys()
        str_indent = ""
        for i in range(indent)    : str_indent     = str_indent     + " "
        str_indent_inc=str_indent
        for i in range(indent_inc): str_indent_inc = str_indent_inc + " "
        print str_indent+"database ", self.filename, " with attributes ", self.cfg.attr_names, " :" 
        for k in list_of_keys:
            print str_indent_inc, k, " : ", self.db[k] 

    def import_data_from_database(self,db):
        '''
        imports data from another database that may have a (slightly) different configuration file
         - uses only record entries of db that has corresponding attributes in the current database
         - otherwise the default attribute value is used.
         - If a key is already existing then an record from db is not inserted in current database
        Use this method, for example, after you have extended a database configuration by additional attributes,
        and want to use old database files (which were generated with the old configuration)
        '''
        db_attr_names = db.cfg.attr_names    # attribute list of the database db to be imported from
        db_keys = db.get_list_of_keys()      # keys of the database db to be imported from
        my_attr_names = self.cfg.attr_names  # attribute list of self
        my_keys = self.get_list_of_keys()    # keys of self
        # check whether the two attribute lists are identical
        equal_attributes = True
        if (len(db_attr_names)!=len(my_attr_names)):
            equal_attributes = False
        else:
            for i in range(len(db_attr_names)):
                if db_attr_names[i]!=my_attr_names[i]:
                    equal_attributes=False
                    break
        for k in db_keys:
            if not k in my_keys:                            # if key is not yet in self then insert new record...
                if equal_attributes:
                    r = db.get_record(k)                    # if attribute lists are equal then just insert record from db
                    self.set_record(*r)
                else:                                       # otherwise insert only those attribute entries that exist in self:
                    my_r  = self.cfg.default_record             # new record with default values
                    my_r[0] = k                                 # first field is assumed to be the key...
                    self.set_record(*my_r)                      # set new record, modify fields afterwards...
                    for a in db_attr_names:         
                        if a in my_attr_names:                  # if attribute a exists in self then set it in new record
                            db_e = db.get_record_entry(a,k)
                            self.set_record_entry(a,k,db_e)


#######################################
# Module Test 
#######################################

if __name__ == '__main__':
    # create a dummy database
    db = Database(Database_config)
    print "\nAfter load():"
    db.print_database()
    db.delete_all_records()
    print "\nAfter delete():"
    db.print_database()
    db.set_record('item1','../MinotaurusSpiel/trunk/images/default_image.jpg','../MinotaurusSpiel/trunk/sounds/default_sound.wav','../MinotaurusSpiel/trunk/sounds/default_sound.wav','type1',[40,40])
    db.set_record('item2','../MinotaurusSpiel/trunk/images/default_image.jpg','../MinotaurusSpiel/trunk/sounds/default_sound.wav','../MinotaurusSpiel/trunk/sounds/default_sound.wav','type2',[40,40])
    db.set_record('item3','../MinotaurusSpiel/trunk/images/default_image.jpg','../MinotaurusSpiel/trunk/sounds/default_sound.wav','../MinotaurusSpiel/trunk/sounds/default_sound.wav','type3',[40,40])
    db.save()
    print "\nAfter insertion():"
    db.print_database()
