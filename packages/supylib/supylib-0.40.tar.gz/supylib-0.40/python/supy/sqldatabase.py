#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import sqlite3
from sqlite3 import OperationalError 
from supy.utilities import *

#########################################################################################################################
# supy.sqldatabase.py
#
# Simple database class for persistent storage of data records in files that is based on SQLITE
# 
# Database tables are defined with config classes (e.g., Table_config) that contain
#   - column names
#   - colum types
#   - column consraints (if any): note that any tables needs one primary key!
#   - column references (if any): foreign key reference, should be a only a table name
#   - column reference constraint (if any): foreign key constraints such as (on delete cascade)
#   - column default entries (if any)
#   - indexes
#
# 28.7.2014 - 30.7.2014 by Andreas Knoblauch
#########################################################################################################################


# ***************************************************************************
# class Table_cfg
# baseclass for database table specification
# ***************************************************************************
class Table_cfg:
    # table specification
    name = 'tb_demo'
    col_names           = ['id'         ,'name'      ,'address' ]
    col_types           = ['INTEGER'    ,'TEXT'      ,'TEXT'    ]
    col_references      = [None         ,None        ,None      ]
    col_constraints     = ['PRIMARY KEY','NOT NULL'  ,None      ]
    col_ref_constraints = [None         ,None        ,None      ]
    col_defaults        = [None         ,None        ,None      ]
    indexes             = [('idx_name',['name'])]
    # default rows (that will be stored during creation)
    rows_default     = ["(1,'Müller', 'Musterweg 5; 72475 Musterstadt')", \
                        "(2,'Maier' , 'Maierweg 6 ; 72473 Maierstadt' )"]
    # class methods
    @classmethod    
    def colnametupel(cls):
        return '(' + ','.join(n for n in cls.col_names) + ')'
    @classmethod    
    def colvaluetupel(cls,vallist):
        return '(' + ','.join(str(v) for v in vallist) + ')'


# ***************************************************************************
# class sqldatabase_cfg
# configuration of a complete sql database 
# - contains a (default) filename 
# - contains database specification by a list of table specifications 
#   (with derivatives of class Table_config)
# ***************************************************************************
class sqldatabase_cfg:
    default_filename = 'sqldatabase_demo.db'
    table_configs = [Table_cfg]


# ***************************************************************************
# class sqldatabase
# creation and management of a sql database 
# as specified by a derivative of sqldatabase_cfg  
# ***************************************************************************
class sqldatabase:
    def __init__(self,cfg=sqldatabase_cfg, filename=None, debugLevel=0):
        self.cfg=cfg
        self.filename=filename
        if(self.filename==None): self.filename=self.cfg.default_filename
        self.table_names = [tc.name for tc in self.cfg.table_configs]
        self.n_tables = len(self.table_names)
        self.cfg_of_table = {tc.name:tc for tc in self.cfg.table_configs}  # cfg_of_table['tablename'] is cfg of table with name 'tablename'
        self.idx_of_col   = {tc.name:{tc.col_names[i]:i for i in range(len(tc.col_names))} \
                                 for tc in self.cfg.table_configs }        # idx_of_column['tablename']['columnanme'] is index of column 'columnname' in table 'tablename'
        self.idx_of_pkey_cols = {tc.name:[i for i in range(len(tc.col_names)) if tc.col_constraints!=None and "PRIMARY KEY" in str(tc.col_constraints[i]).upper()]  \
                                 for tc in self.cfg.table_configs }        # idx_of_column['tablename']['columnanme'] is index of column 'columnname' in table 'tablename'
        self.db   = None            # reference to sql database
        self.curs = None            # reference to cursor to interact with sql database
        self.debugLevel=debugLevel
        self.connect()

    """
    connect to and initialize database
    """
    def connect(self):
        print("try to connect to fn=", self.filename)
        db1 = sqlite3.connect(self.filename)    # if database exists then just connect   
        db1.execute('pragma foreign_keys=ON')   # foreign key support necessary for DELETE CASCADE 
        self.db=db1                             # if no error occurs then assign db
        self.db.isolation_level = None          # necessary to have control over transactions
        self.curs=self.db.cursor()
        self.curs.execute("select name from sqlite_master WHERE type='table'")   # get all table names
        rowcount=len(self.curs.fetchall())
        if(rowcount!=self.n_tables):
            if(rowcount<=0):
                self.create_new_db()
            else:
                raise Exception("Database "+self.filename+" does not match specification!")

    """
    delete all tables of database
    """
    def delete_db(self):
        if(self.db):
            self.curs.execute("select name from sqlite_master WHERE type='table'")   # get all table names
            table_names = self.curs.fetchall()
            if len(table_names)>0:
                self.begin_transaction()
                for n in table_names:
                    cmd = "drop table " + n[0]
                    try:
                        if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
                        self.curs.execute(cmd)
                    except OperationalError as e:
                        print("Error during execution of sqlite command: ", cmd)
                        raise e
                self.commit_transaction()

    """
    add/create new tables to database according to specifications in list tb_cfg
    """
    def add_tables(self,tb_cfgs):
        self.begin_transaction()
        for t in tb_cfgs: 
            # (i) create table t
            n=len(t.col_names)
            cmd = 'create table ' + t.name + ' ('
            for j in range(n):
                if(j>0): 
                    cmd=cmd+', '
                tb_name      = t.col_names[j]
                tb_type      = t.col_types[j]
                tb_ref       = t.col_references[j]
                tb_cnstr     = t.col_constraints[j]
                tb_ref_cnstr = t.col_ref_constraints[j]
                tb_def       = t.col_defaults[j]
                cmd = cmd + tb_name + ' ' + tb_type 
                if(tb_ref!=None)and(tb_ref!=''):
                    cmd = cmd + ' references ' + tb_ref
                    if(tb_ref_cnstr!=None)and(tb_ref_cnstr!=''):
                        cmd = cmd + ' ' + tb_ref_cnstr
                if(tb_cnstr!=None)and(tb_cnstr!=''):
                    cmd = cmd + ' ' + tb_cnstr 
                if(tb_def!=None):
                    cmd = cmd + " DEFAULT " + str(tb_def)
            cmd = cmd + ')'
            try:
                if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
                self.curs.execute(cmd)
            except OperationalError as e:
                print("Error during execution of sqlite command: ", cmd)
                raise e
            else:
                # (ii) insert default rows in table t
                for r in t.rows_default:
                    cmd = 'insert into ' + t.name + ' ' + t.colnametupel() + ' values ' + r
                    try:
                        if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
                        self.curs.execute(cmd)
                    except OperationalError as e:
                        print("Error during execution of sqlite command: ", cmd)
                        raise e
        # (iii) finalize transaction
        self.commit_transaction()
        self.resetIndexes()


    """
    create new (empty) database according to specification self.cfg.table_configs
    and insert default data records
    """
    def create_new_db(self):
        self.delete_db()    # delete all tables (if any)
        self.add_tables(self.cfg.table_configs)

    """
    create new (empty) database according to specification self.cfg.table_configs
    and insert default data records
    """
    def create_new_db_old(self):
        self.delete_db()    # delete all tables (if any)
        #print("begin_trans", len(self.cfg.table_configs))
        self.begin_transaction()
        for t in self.cfg.table_configs:
            # (i) create table t
            n=len(t.col_names)
            cmd = 'create table ' + t.name + ' ('
            for j in range(n):
                if(j>0): 
                    cmd=cmd+', '
                tb_name      = t.col_names[j]
                tb_type      = t.col_types[j]
                tb_ref       = t.col_references[j]
                tb_cnstr     = t.col_constraints[j]
                tb_ref_cnstr = t.col_ref_constraints[j]
                tb_def       = t.col_defaults[j]
                cmd = cmd + tb_name + ' ' + tb_type 
                if(tb_ref!=None)and(tb_ref!=''):
                    cmd = cmd + ' references ' + tb_ref
                    if(tb_ref_cnstr!=None)and(tb_ref_cnstr!=''):
                        cmd = cmd + ' ' + tb_ref_cnstr
                if(tb_cnstr!=None)and(tb_cnstr!=''):
                    cmd = cmd + ' ' + tb_cnstr 
                if(tb_def!=None):
                    cmd = cmd + " DEFAULT " + str(tb_def)
            cmd = cmd + ')'
            #print("cmd=",cmd)
            try:
                if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
                self.curs.execute(cmd)
            except OperationalError as e:
                print("Error during execution of sqlite command: ", cmd)
                raise e
            # (ii) insert default rows in table t
            for r in t.rows_default:
                cmd = 'insert into ' + t.name + ' ' + t.colnametupel() + ' values ' + r
                try:
                    if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
                    self.curs.execute(cmd)
                except OperationalError as e:
                    print("Error during execution of sqlite command: ", cmd)
                    raise e
        self.commit_transaction()
        self.resetIndexes()

    """
    drop all current indexes and reset new indexes as specified in self.cfg
    """
    def resetIndexes(self):
        self.begin_transaction()
        # (i) drop all indexes of the database
        self.curs.execute("select name from sqlite_master WHERE type='index'")   # get all index names
        index_names = self.curs.fetchall()
        for n in index_names:
            cmd = "drop index " + n[0]
            try:
                self.curs.execute(cmd)
            except OperationalError as e:
                print("Error during execution of sqlite command: ", cmd)
                raise e
        # (ii) create new indexes for all tables
        for t in self.cfg.table_configs:
            if t.indexes!=None:
                for i in range(len(t.indexes)):
                    n         = t.name+"_"+t.indexes[i][0]     # name of index
                    idx_cols  = t.indexes[i][1]     # columns of the index
                    if len(idx_cols)>0 : 
                        cmd = "create index " + n + " on " + t.name + "( "
                        for j in range(len(idx_cols)):
                            if j>0 : cmd = cmd + ", "
                            cmd = cmd + idx_cols[j] + " "
                        cmd = cmd + ")"
                        try:
                            self.curs.execute(cmd)
                        except OperationalError as e:
                            print("Error during execution of sqlite command: ", cmd)
                            raise e
        self.commit_transaction()
 
        
    """
    execute query and convert resulting list of row tuples to list of row dicts with field name keys
    thus, rowdicts[i][field] will return value of field of i-th record
    """
    def query2dicts(self,query,params=()):    
        try:
            self.curs.execute(query, params)
        except OperationalError as e:
            print("Error during execution of sqlite query '", query, "' with parameters: ", params)
            raise e
        colnames = [desc[0] for desc in self.curs.description]
        rowdicts = [dict(zip(colnames,row)) for row in self.curs.fetchall()]
        return rowdicts, colnames

    """
    formatted output of dict of records (e.g., from query2dictts)
    use optional parameter colnames to define an order of columns (otherwise alphabetical order)
    """
    def print_records(self,recs, colnames=None,sept=('-'*40)):
        print(len(recs), 'records')
        print(sept)
        #print("recs=", recs)
        for rec in recs:
            if(colnames):
                cn=colnames
            else:
                cn=rec
            maxkey = max(len(key) for key in cn)     # max key len
            for key in cn:
                print('%-*s => %s' % (maxkey, key, rec[key]))
            print(sept)

    """
    print table table_name
    """
    def print_table(self,table_name,format=True):
        curs=self.curs
        curs.execute('select count(*) from ' + table_name)
        nrec = curs.fetchone()[0]
        cmd = 'select * from ' + table_name
        curs.execute(cmd)
        colnames = [desc[0] for desc in self.curs.description]
        if not format:
            s1="Table %s (%d records)" % (table_name, nrec)
            s2="... with columns "+str(colnames)
            print(s1)
            print(s2)
            print(('-'*(max([len(s1)+1,len(s2)+1,15]))))
            while True:
                rec = curs.fetchone()
                if not rec: break
                print(rec)
        else:
            s1="Table %s" % (table_name)
            s2="... with columns "+str(colnames)
            print(s1)
            #print(s2)
            print(('-'*(max([len(s1)+1,len(s2)+1,15]))))
            print(('-'*(max([len(s1)+1,len(s2)+1,15]))))
            recs,cn = self.query2dicts(cmd) 
            self.print_records(recs,cn)

    """
    print database
    """
    def print_database(self,format=True):
        print("Database %s" % self.filename)
        print("... with Tables ", self.table_names)
        for t in self.table_names:
            self.print_table(t,format)
        
    """
    return string s as a list of elements from eltype (wrapper on supy.utilities method)
    useful to decode list attributes '[1,2,3,4]' which are stored as strings in the database tables,
    but should be transformed again as list of numerical elements after a query
    e.g., parseStringAsList('[1,2,3,4]','int') returns a integer list [1,2,3,4]
    eltype may be either 'int', 'float', 'string', 'binary' (or 'bool')
    in case of an excpetion use res_default as result of the transformation...
    """
    def parseStringAsList(self,s,eltype='int',res_default=None): 
        return parseStringAsList(s,eltype,res_default)

    """
    execute query and convert resulting list of row tuples to list of row dicts with field name keys
    thus, rowdicts[i][field] will return value of field of i-th record
    """
    def getColType(self,table,column):
        cfg_table=self.cfg_of_table[table]
        idx_col  =self.idx_of_col[table][column]
        return cfg_table.col_types[idx_col]

    """
    convert a column value to an appropriate string depending on column type,
    e.g., for type=INTEGER a value 5 becomes '5' (or '5' remains '5'), but for type=TEXT a value '5' must become '"5"'.
    """
    def toValueStr(self,table,col,val):
        coltype = self.getColType(table,col)
        v=str(val)               # per default just convert to str
        if(coltype=='TEXT'):
            v="'" + v + "'"
        return v

    """
    construct a simple where clause from matching table columns against column values
    Parameters:
       tables: list of tablenames
       cols  : list of column-names (for multiples entries cols[i] must be in the form 'table.colname')
       vals  : corresponding values (one data record from the external database
       oper  : operator for concatenating multiple conditions (default: AND)
    Returns: Where clause
    Example: wc=self.getWhereClause_from_data_matches(t,c,v) for c=['id','name'], v=[5,'Schmitz'] 
             returns wc=" id=5 AND name='Schmitz'"
    """
    def getWhereClause_from_ColumnValues(self,tables,cols, vals, oper="AND"):
        #print("getWhere... self=",self,"tables=",tables,"cols=",cols,"vals=",vals,"oper=",oper)
        str_error = 'AssertionError in sqldatabase.getWhereClause_from_ColumnValues(self,tables,cols, vals) for tables='+str(tables)+', cols='+str(cols)+', vals='+str(vals)+ " : "
        assert isinstance(tables,list) and isinstance(cols,list) and isinstance(vals,list), str_error + " All arguments must be lists!"
        assert len(cols)==len(vals), str_error + " List parameters cols and vals must have same length!"
        assert (len(cols)==0) or (len(tables)>0), str_error + " Missing table name!" 
        # (i) extract pure column names (from 'students.name' extract only 'name') 
        cols_only = [c for c in cols]     # copy of list
        tab_only  = [tables[0]]*len(cols)
        for i in range(len(cols)):
            if "." in cols[i]:
                splt=cols[i].split(".")
                cols_only[i]=splt[1]     # do not include table name
                tab_only [i]=splt[0]     # only table name
                assert tab_only[i] in tables, str_error + " table of " + str(cols[i]) + " is not in table list " + str(tables)
        # (ii) construct where clause
        wc=''
        for i in range(len(cols)):
            tab_cfg = self.cfg_of_table[tab_only[i]]
            assert cols_only[i] in tab_cfg.col_names, str_error + " Column " + str(cols_only[i]) + " does not exist in table " + str(tab_only[i]) 
            if wc!='': wc=wc+' '+oper+' '
            wc=wc+cols[i]+'=='
            coltype = self.getColType(tab_only[i],cols_only[i])
            #print("coltype=",coltype)
            if(coltype=='TEXT'):
                wc=wc+"'"+str(vals[i])+"'"
            else:
                wc=wc+str(vals[i])
        return wc


    """
    simple select default values of columns 
    parameters:
       colnames: list of column names of the columns to be selected
       tables: either a single table name or a list of tables for making a join
       strval: if True then all values are converted to strings
       strval: if True then all values are converted to strings
    """
    def simple_select_defaultvalues(self,colnames,tables,strval=False):
        str_error = 'AssertionError in sqldatabase.simple_select_defaultvalues(self,colnames,tables) for tables='+str(tables)+', colnames='+str(colnames)+ " : "
        assert isinstance(colnames,list), str_error+" Parameter colnames must be a list!"
        assert isinstance(tables,list) or isinstance(tables,str), str_error+" Parameter tables must be a string or a list!"
        res = [None for c in colnames]      # initialize results with list of None's
        for i in range(len(colnames)):
            # (a) extract table t and columname c
            c = colnames[i]
            if "." in c:
                splt=c.split(".")
                t=splt[0]
                c=splt[1]
                assert (t==tables) or (t in tables), str_error+" Table t=" + t + " does not match parameter tables!"
            else:
                t=tables
                if isinstance(tables,list): t=t[0]
            # (b) get default values
            cfg_table=self.cfg_of_table[t]
            idx_col  =self.idx_of_col[t][c]
            if(cfg_table.col_defaults!=None)and(cfg_table.col_defaults[idx_col]!=None):
                res[i]=cfg_table.col_defaults[idx_col]
                if(strval): res[i]=str(res[i])
                if(cfg_table.col_types[i]=='TEXT'): res[i]=res[i][1:-1]
        return res 
            

    """
    simple select query
    parameters:
       colnames: list of column names of the columns to be selected
       tables: either a single table name or a list of tables for making a join
       joinon: "join on" expression for each combination of tables (either None or a list being on item shorter than tables),
               e.g., tables=['t1','t2','t3'], join_on=['t1.a=t2.a', 't2.b=t3.b'] corresponds to 
                     SELECT .... FROM t1 join t2 on t1.a=t2.a join t3 on t2.b=t3.b ...
       where: where statement
       orderby: list of column names for sorting
       strval: if True then all values are converted to strings
    """
    def simple_select(self,colnames,tables,joinon=None,where=None,orderby=None,strval=False):
        # (i) decode column names
        if(colnames=='*'):
            str_colnames='*'
        else:
            str_colnames = ','.join(n for n in colnames)
        cmd = "select " + str_colnames + " from " 
        # (ii) decode table names and joins
        if isinstance(tables,str):
            str_tables = tables        # only single table (no join necessary)
        else:
            if joinon==None:
                # natural join
                str_tables = ' natural join '.join(n for n in tables)
            else:
                # general join
                for i in range(len(tables)):
                    if i==0:
                        str_tables=tables[0]
                    else:
                        str_tables = str_tables + " join " + tables[i] 
                        if len(joinon)>=i:
                            str_tables = str_tables + " on " + joinon[i-1]
        cmd = cmd + str_tables
        # (iv) decode where
        if(where!=None)and(where!=""):
            cmd = cmd + " where " + where
        # (iii) decode orderby
        if(orderby!=None):
            str_orderby = ','.join(n for n in orderby)
            cmd = cmd + " order by " + str_orderby 
        # (iv) execute command and convert to strings (if necessary)
        try:
            if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
            self.curs.execute(cmd)
        except OperationalError as e:
            print("Error during execution of sqlite command: ", cmd)
            raise e
        data=self.curs.fetchall()
        if(self.debugLevel>1): print("RESULT OF SQL Command:\n", data)
        if (strval):  # convert all values to strings
            for i in range(len(data)):
                data[i]=list(data[i])
                data[i]=[str(d) for d in data[i]]
        return data


    """
    simple update query
    parameters:
       table: table to be updated
       colnames    : list of column names to be updated
       col_values  : list of column values corresponding to colnames
       pkeys       : list of columns acting as primary key to determine the row to be updated (in where clause)
       pkey_values : list of column values corresponding to pkeys
       orclause    : either 'rollback', 'abort', 'replace', 'fail', 'ignore', etc. 
    """
    def simple_update_byPKEY(self,table,colnames,col_values, pkeys, pkey_values, orclause=None):
        # (i) make assertions
        strerror="Assertion error in simple_update_byPKEY(self,table,colnames,col_values,pkeys,pkey_values) of table " \
            + str(table) + " with primary keys " + str(pkeys) + " = " + str(pkey_values) + ": "
        assert len(colnames)==len(col_values), strerror + "Parameters colnames and col_values must have same length!"
        assert len(pkeys)>0, strerror + "Parameter pkeys must contain at least one primary key!" 
        assert len(pkeys)==len(pkey_values), strerror + "Parameters pkeys and pkey_values must have same length!"
        # (ii) generate SQL query
        cmd = "update " 
        if orclause!=None : cmd = cmd + "or " + orclause + " "
        cmd = cmd + table + " set " 
        for i in range(len(colnames)):
            if(i>0): cmd = cmd + ", "
            cni=colnames[i]    # in case tab.col then remove tab.
            if "." in cni:
                splt=cni.split(".")
                cni=splt[1]    # only column name
            cmd = cmd + cni + " = " + self.toValueStr(table,cni,col_values[i])
        cmd = cmd + " where "
        for i in range(len(pkeys)):
            if(i>0): cmd = cmd + ", "
            cmd = cmd + pkeys[i] + " = " + self.toValueStr(table,pkeys[i],pkey_values[i])
        # (iii) perform update query
        try:
            if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
            self.curs.execute(cmd)
        except OperationalError as e:
            print("Error during execution of sqlite command: ", cmd)
            raise e

    """
    simple insert query
    parameters:
       table: table where new record should be inserted into
       colnames    : list of column names where values are available 
       col_values  : list of column values corresponding to colnames
    """
    def simple_insert(self,table,colnames,col_values):
        # (i) make assertions
        strerror="Assertion error in simple_insert(self,table,colnames,col_values) of table " \
            + str(table) + " with colnames=" + str(colnames) + " and col_values=" + str(col_values) + ": "
        assert table in self.table_names, strerror + " Table " + str(table) + " is not database table!"
        assert (colnames==None) or (len(colnames)==len(col_values)), strerror + " Parameters colnames and col_values must have same length!"
        # (ii) generate SQL query
        cmd = "insert into " + table 
        if (colnames!=None) and (len(colnames)>0):
            cmd = cmd + " ("
            for i in range(len(colnames)):
                if(i>0): cmd=cmd + ", "
                cmd = cmd + colnames[i] 
            cmd = cmd + ")"
        cmd = cmd + " values ( "
        for i in range(len(col_values)):
            if(i>0): cmd=cmd + ", "
            cmd = cmd + self.toValueStr(table,colnames[i],col_values[i])
        cmd = cmd + " )"
        # (iii) perform insert query
        try:
            if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
            self.curs.execute(cmd)
        except OperationalError as e:
            print("Error during execution of sqlite command: ", cmd)
            raise e

    """
    simple delete query
    parameters:
       table: table where record should be deleted
       colnames    : list of column names where values are available 
       col_values  : list of column values corresponding to colnames
    """
    def simple_delete(self,table,colnames,col_values):
        # (i) make assertions
        strerror="Assertion error in simple_delete(self,table,colnames,col_values) of table " \
            + str(table) + " with colnames=" + str(colnames) + " and col_values=" + str(col_values) + ": "
        assert table in self.table_names, strerror + " Table " + str(table) + " is not database table!"
        assert (colnames!=None) and (col_values!=None) and (len(colnames)==len(col_values)), strerror + " Parameters colnames and col_values must have same length!"
        # (ii) generate and perform SQL query
        cmd = "delete from " + table + " where " + self.getWhereClause_from_ColumnValues([table],colnames,col_values)
        try:
            self.curs.execute(cmd)
        except OperationalError as e:
            print("Error during execution of sqlite command: ", cmd)
            raise e

    """
    get_new_primary_key 
     - get new primary key for inserting a new data record into table
     - assumes that table has a unique primary key (i.e., only one column is primary key) 
     - here: assumes that the primary key has INTEGER-type !!
    """
    def get_new_primary_key(self,table, par_pkey_col=None):
        idx_of_pkey_cols = self.idx_of_pkey_cols[table]
        assert len(idx_of_pkey_cols)==1, "Currently only single-column primary-keys supported! However, table " + str(table) + " has multiple primary keys!"
        idx_of_pkey_col=idx_of_pkey_cols[0]           # only one primary key allowed!
        table_name = table                                          # name of the table
        pkey_col   = self.cfg_of_table[table].col_names[idx_of_pkey_col]  # column name of primary key
        assert par_pkey_col==None or par_pkey_col==pkey_col, "Column " + par_pkey_col + " of table " + table + " is not the primary key !!"
        cmd = 'select max(' + pkey_col + ') from ' + table
        try:
            if(self.debugLevel>0): print("EXECUTE SQL COMMAND: ", cmd)
            self.curs.execute(cmd)
        except OperationalError as e:
            print("Error during execution of sqlite command: ", cmd)
            raise e
        res=self.curs.fetchall()
        if(self.debugLevel>1):  print("RESULT OF SQL Command:\n", res)
        if(res==None) or (len(res)==0) or (res[0]==None) or (res[0][0]==None):
            res=0               # changed from res=1 to res=0 (19/9/2017)
        else:
            res=int(res[0][0])+1
        if(self.debugLevel>1):  print("REFINED RESULT OF SQL Command:\n", res)
        return res, pkey_col

    """
    begin_transaction 
    """
    def begin_transaction(self):
        self.curs.execute("begin transaction")

    """
    commit_transaction
    """
    def commit_transaction(self):
        self.curs.execute("commit transaction")

    """
    rollback_transaction
    """
    def rollback_transaction(self):
        self.curs.execute("rollback transaction")

    """
    set debug flag
    """
    def setDebugMode(self,debugLevel=0):
        self.debugLevel=debugLevel


#######################################
# Module test     
#######################################
if __name__ == '__main__':
    print("\nModule test of supylib module supy.sqldatabase.py")
    print("----------------------------------------------------\n") 
    db = sqldatabase()
    db.print_database(1)
    
