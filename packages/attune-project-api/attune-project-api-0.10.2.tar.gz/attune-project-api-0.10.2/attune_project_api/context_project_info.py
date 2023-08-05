from collections import namedtuple

"""
This tuple is used by the client code to specify the name and the key of the 
project being loaded.
"""
ContextProjectInfo = namedtuple("ContextProjectInfo", ["key", "name"])
