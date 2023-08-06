#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import inspect

###################################################################################################
# supy.serialize.py
#
# Simple encoder/decoder classes for serializing python objects and python classes 
#
# Encoding works for objects of arbitrary classes
#
# However, creation of objects during decoding requires some conventions:
# - Decoder creates an object by calling the creator (__init__) with arguments corresponding
#   to all object fields
# - Thus, the creators (__init__ method) must offer parameters with names being identical to 
#   the relevant object fields
# - if classes have attribute fields set inside the constructor 
#   (that is, the fields are not given as parameters to __init__) 
#   then the constructor __init__ must have an **args parameters 
#   in order to catch additional parameters that are not used
# For further reference see the examples in the module test below...
# 
# Code inspired from a tutorial on http://pymotw.com/2/json/
# 
# 28.3.2013 - 7.4.2013 by Andreas Knoblauch
###################################################################################################


###################################################################################################
# SupyEncoder: Encoder class
###################################################################################################
class SupyEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if inspect.isclass(obj):
            d = {'__isclass__':True, 
                 '__class__':obj.__name__, 
                 '__module__':obj.__module__,
                 }
        else:
            d = {'__isclass__':False, 
                 '__class__':obj.__class__.__name__, 
                 '__module__':obj.__module__,
                 }
            d.update(obj.__dict__)
        if d['__class__']=="instancemethod":     # so far do not consider methods
            return None
        else:
            return d


###################################################################################################
# SupyDecoder: Decoder class
###################################################################################################
class SupyDecoder(json.JSONDecoder):
    
    def __init__(self,**args):
        json.JSONDecoder.__init__(self,object_hook=self.dict_to_object,**args)

    def dict_to_object(self, d):
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module, class_name)
            if d.pop('__isclass__'):
                obj = class_
            else:
                args = dict( (key.encode('ascii'), value) for key, value in d.items())
                obj = class_(**args)
        else:
            obj = d
        return obj


#######################################
# Module test     
#######################################
if __name__ == '__main__':

    print "#######################################"
    print "# Test for module supy.serialize.py    "
    print "#######################################"

    class obj_cfg:
        a=5
        b=7
        c=10

    class MyObj(object):                  # simple class, all object fields given in __init__
        def __init__(self, s):
            self.s = s
        def __repr__(self):
            return '<MyObj(%s)>' % self.s

    class MyObj2(object):                 # ditto, but cfg may be a class parameter
        def __init__(self, s, cfg=None):
            self.s = s
            self.cfg=cfg
        def __repr__(self):
            return '<MyObj(%s)>' % self.s

    class MyObj3(object):                 # as MyObj2, but __init__ defines additional fields not given in the parameter list 
        def __init__(self, s, cfg=None, **args):      # **args is required because __init__ sets additional fields 
            self.s = s
            self.cfg=cfg
            self.f1 = 245
            self.f2 = 456

        def __repr__(self):
            return '<MyObj(%s)>' % self.s

    print "\n\n##### (i) encoding/decoding directly with the supy classes #####"
    obj = MyObj('internal data')
    obj2 = MyObj2(obj,cfg=obj_cfg)
    obj3 = MyObj3(obj,cfg=obj_cfg)
    print "obj=",obj
    print "obj2=",obj2
    print "obj3=",obj3
    str_obj = SupyEncoder().encode(obj)
    str_obj2 = SupyEncoder().encode(obj2)
    str_obj3 = SupyEncoder().encode(obj3)
    print "encoded obj=", str_obj
    print "encoded obj2=", str_obj2
    print "encoded obj3=", str_obj3

    obj_ = SupyDecoder().decode(str_obj)
    print "decoded obj_=",obj_
    obj2_ = SupyDecoder().decode(str_obj2)
    print "decoded obj2_=",obj2_
    obj3_ = SupyDecoder().decode(str_obj3)
    print "decoded obj3_=",obj3_

    print "\n\n##### (ii) encoding/decoding with json.dumps/loads #####"
    obj = MyObj('internal data')
    obj2 = MyObj2(obj,cfg=obj_cfg)
    obj3 = MyObj3(obj2,cfg=obj_cfg)
    obj4 = [1,2,3,4]
    print "obj3=",obj3
    str_obj3 = json.dumps(obj3,cls=SupyEncoder)
    print "encoded obj3=", str_obj3
    obj3_ = json.loads(str_obj3,cls=SupyDecoder)
    print "decoded obj3_=",obj3_
    print "\nobj4=",obj4
    str_obj4 = json.dumps(obj4,cls=SupyEncoder)
    print "encoded obj4=", str_obj4
    obj4_ = json.loads(str_obj4,cls=SupyDecoder)
    print "decoded obj4_=",obj4_
    
