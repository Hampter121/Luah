import os


def yuriinject_env(yurilua, yurig):
    """
    Environment variable management for Luah.
    Provides get, set, delete, and list operations for environment variables.
    """
    
    def yurienv_get(yurikey, yuridefault=None):
        """Get an environment variable"""
        yurikey = str(yurikey)
        yurivalue = os.environ.get(yurikey)
        if yurivalue is None:
            return yuridefault
        return yurivalue
    
    def yurienv_set(yurikey, yurivalue):
        """Set an environment variable"""
        yurikey = str(yurikey)
        yurivalue = str(yurivalue)
        os.environ[yurikey] = yurivalue
        return True
    
    def yurienv_delete(yurikey):
        """Delete an environment variable"""
        yurikey = str(yurikey)
        if yurikey in os.environ:
            del os.environ[yurikey]
            return True
        return False
    
    def yurienv_has(yurikey):
        """Check if an environment variable exists"""
        yurikey = str(yurikey)
        return yurikey in os.environ
    
    def yurienv_list():
        """List all environment variables as a table"""
        yurienvs = {}
        for yurik, yuriv in os.environ.items():
            yurienvs[yurik] = yuriv
        return yurilua.table_from(yurienvs)
    
    def yurienv_keys():
        """Get list of all environment variable names"""
        yurikeys = list(os.environ.keys())
        return yurilua.table_from(yurikeys)
    
    def yurienv_clear():
        """Clear all environment variables (use with caution!)"""
        os.environ.clear()
        return True
    
    def yurienv_update(yuritbl):
        """Update multiple environment variables from a table"""
        if not yuritbl:
            return False
        
        # Convert Lua table to Python dict
        yuridict = {}
        for yurik, yuriv in yuritbl.items():
            yuridict[str(yurik)] = str(yuriv)
        
        os.environ.update(yuridict)
        return True
    
    # Inject env namespace
    yurig.env = yurilua.table_from({
        "get":    yurienv_get,
        "set":    yurienv_set,
        "delete": yurienv_delete,
        "has":    yurienv_has,
        "list":   yurienv_list,
        "keys":   yurienv_keys,
        "clear":  yurienv_clear,
        "update": yurienv_update,
    })
