import sys
# set default encoding to windows locale in order to handle unicode path names
# correctly. This is done here for built executables
# or in Lib\site.py when running from sources

if sys.platform == 'win32':
    import locale, codecs
    enc = locale.getdefaultlocale()[1]
    if enc.startswith('cp'):            # "cp***" ?
        try:
            codecs.lookup(enc)
        except LookupError:
            import encodings
            encodings._cache[enc] = encodings._unknown
            encodings.aliases.aliases[enc] = 'mbcs'

    if hasattr(sys, 'setdefaultencoding'):
        try:
            sys.setdefaultencoding(enc)    
        except LookupError:
            sys.setdefaultencoding('ascii')    
        del sys.setdefaultencoding
