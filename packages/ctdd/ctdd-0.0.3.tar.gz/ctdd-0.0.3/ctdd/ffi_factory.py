# todo foss: move this to crelm

class FFIFactory:
    def __init__(self, ffi=None):
        self._ffi = ffi

        self._objects = []

    def _create(self, type, init=None):
        if not self._ffi:
            raise RuntimeError('_ffi not set')
        
        o = self._ffi.new(type, init)
        self._objects.append(o)
        return o

    @property
    def null_pointer(self):
        if not self._ffi:
            raise RuntimeError('_ffi not set')

        return self._ffi.NULL
    
    def C_string(self, v:str):
        return self._create('char[]', v.encode('utf-8'))

    def P_str(self, cdata):
        return self._ffi.string(cdata).decode('utf-8')

    def C_int(self, v):
        if isinstance(v, int):
            return self._create('int *', v)

        return None

    def C_int_array(self, v):
        if isinstance(v, int):
            return self._create(f'int[{v}]')

        if isinstance(v, list) or isinstance(v, tuple):
            return self._create('int[]', v)
        
        return None

    def P_tuple(self, cdata, length): # todo foss: length?
        return tuple(cdata)


