# I just want to extend the usage of dict.
from django import template
register = template.Library();

def getDictKeys(dictionary):
    return sorted(dictionary.keys());

def getDictValue(dictionary,key):
    return dictionary.get(key);

def getListValue(listt,key):
    return listt[key];

def getType(object):
    return type(object);

register.filter('getDictValue',getDictValue);
register.filter('getDictKeys',getDictKeys);
register.filter('getListValue',getListValue);
register.filter('getType',getType);