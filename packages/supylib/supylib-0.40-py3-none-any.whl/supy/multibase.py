#!/usr/bin/python
# -*- coding: utf-8 -*-

from supy.database import *

###################################################################################################
# Multibase.py
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


class Multibase_config(Database_config):
    attr_names = ['db_name', 'db'  ]
    attr_types = ['string' , 'json']
    default_record = ['__new_key_', None]
    default_filename = 'dummy.mb'
    db_configs = []  # configuration classes for databases (should all be RAM-only) to be stored in multibase

class Multibase:
    def __init__(self,cfg=Multibase_config, filename=None):
        self.cfg=cfg
        self.filename=filename
        if(self.filename==None): self.filename=self.cfg.default_filename
        self.n_db = len(self.cfg.db_configs)
        self.mb = None
        self.load()

    def isModified(self):      # returns True if at least one database is modified
        res=False
        keys = self.mb.get_list_of_keys()
        for k in keys:
            if self.get_database(k).flagModified>0:
                res=True
        if res:
            self.mb.flagModified=1
        return self.mb.flagModified
            
    def get_database(self,key):
        db=self.mb.get_record_entry("db",key)
        return db

    def load(self):
        try:
            f=open(self.filename,'r')
            f.close()
        except IOError as e:
            # error message is written by call to Database constructor...
            self.mb = Database(self.cfg,self.filename)
            # add empty databases
            print "I will add empty databases to multibase ", self.filename, " ..."
            for i in range(self.n_db):
                db = Database(self.cfg.db_configs[i])
                self.mb.set_record(db.filename,db)
        else:
            self.mb = Database(self.cfg,self.filename)    # load database of databases
            # set the database configs of self.cfg for each of the loaded databases
            # this is necessary because during loading the configs are set to the classes of the stored databases
            # but these classes may differ from the classes in self.cfg!!
            for cfg in self.cfg.db_configs:
                if cfg.default_filename in self.mb.get_list_of_keys():
                    db = self.get_database(cfg.default_filename)
                    db.cfg=cfg

    def save(self, filename=None):
        if(filename!=None):
            self.filename=filename
        self.mb.save(self.filename)
        keys = self.mb.get_list_of_keys()
        for k in keys:
            self.get_database(k).flagModified=0

    def print_multibase(self,indent=0,indent_inc=3):
        list_of_keys = self.mb.get_list_of_keys()
        str_indent = ""
        for i in range(indent)    : str_indent     = str_indent     + " "
        str_indent_inc=str_indent
        for i in range(indent_inc): str_indent_inc = str_indent_inc + " "
        print str_indent+"multibase ", self.filename, " contains the following databases:"
        self.mb.print_database(indent+1,indent_inc)
        keys = self.mb.get_list_of_keys()
        for k in keys:
            db = self.get_database(k)
            db.print_database(indent+1,indent_inc)
            
    def import_data_from_multibase(self,other_mb,db_list=None):
        '''
        imports data from another multibase that may have a (slightly) different configuration file
        (i.e., other databases with other configurations)
        Basically uses Database.import_data_from_database()
        If db_list==None then all databases of the multibase are imported, otherwise only those databases with keys in db_list
        '''
        if db_list==None:
            mb_keys = other_mb.mb.get_list_of_keys()
        else:
            mb_keys = db_list
        my_keys = self.mb.get_list_of_keys()
        for k in mb_keys:                                # scan all keys (database names) of other_mb
            if k in my_keys:                             # if key exists also in self then import data
                my_db=self.get_database(k)
                mb_db=other_mb.get_database(k)
                my_db.import_data_from_database(mb_db)    

    def enableCallbacks(self,flag=1):                   # set callback flags of _all_ databases
        keys = self.mb.get_list_of_keys()
        for k in keys:
            self.get_database(k).enableCallbacks(flag)


#######################################
# Module test     
#######################################
if __name__ == '__main__':

    print "#######################################"
    print "# Test for module supy.multibase.py    "
    print "#######################################"

    class Database_config1(Database_config):
        attr_names     = ['id'    ,'name', 'age'] # list of attribute names
        attr_types     = ['string','string','json'] # list of attribtute types ('string' or 'json')
        default_record = ['__new_key_','Andi',40]                  # for example, for adding a new data record
        default_filename = 'db1'            # default file name of database
        flag_RAM_only    = 1                  # if set then database is kept only in RAM (never read/written to disk) 

    class Database_config2(Database_config):
        attr_names     = ['id'    ,'name', 'address'] # list of attribute names
        attr_types     = ['string','string','string'] # list of attribtute types ('string' or 'json')
        default_record = ['__new_key_','Andi','Froschhausen']   # for example, for adding a new data record
        default_filename = 'db2'            # default file name of database
        flag_RAM_only    = 1                  # if set then database is kept only in RAM (never read/written to disk) 

    class Multibase_config1(Multibase_config):
        default_filename = 'dummy.mb'                           # default file name of database
        db_configs       = [Database_config1, Database_config2] # list of database specification that make up the multibase

    multibase = Multibase(Multibase_config1,"dummy.mb")
    print "\nafter loading..."
    multibase.print_multibase()
    db1 = multibase.get_database("db1")
    db2 = multibase.get_database("db2")
    db1.delete_all_records()
    db2.delete_all_records()
    print "\nafter deleting..."
    multibase.print_multibase()
    db1.set_record("id1","Christian",7)
    db1.set_record("id2","Matthias",5)
    db2.set_record("id1","Andi","Bömenkirch")
    db2.set_record("id2","Kattia","Froschhausen")
    print "\nafter inserting records..."
    multibase.print_multibase()
    multibase.save()

