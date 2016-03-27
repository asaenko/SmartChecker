# -*- coding: utf-8 -*-

class InfoCache(object):
    """A singleton Class can store the information shared in global/modules.
    """
    _cache = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._cache
        return self

    def set(self,key,value):
        self._cache[key] = value   
        return self._cache[key]
        
    def get(self,key):
        return self._cache.get(key,None)
 
    def __getitem__(self,key):
        return self.get(key)
    
    def __setitem__(self,key,value):
        self._cache[key] = value

    def __repr__(self):
        return "InfoCache:%s" % self._cache
    
    def __contains__(self,key):
        return key in self._cache

shareinfo = InfoCache()        