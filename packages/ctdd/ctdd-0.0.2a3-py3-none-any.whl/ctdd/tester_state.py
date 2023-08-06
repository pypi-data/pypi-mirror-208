from .ffi_factory import FFIFactory
from .mocker import Mocker, mock_binder

from crelm import Factory as CrelmFactory
import importlib
import os.path
from functools import partial

def _struct_creator(state, typename):
    struct = state.tube._ffi.new(f'struct {typename} *')
    return struct

class TesterState:

    def __init__(self, module_name: str):
        self._module_name = module_name

        self.factory = FFIFactory()
        self.mocker = Mocker()
        self.externs = []
        self.tube = None
        self.sut = None

        paste = self.create_tube("introspection").squeeze()
        if paste is None:
            raise RuntimeError('introspection build failed')

        for struct_name in paste.struct_names:
            func = partial(_struct_creator, self, struct_name)

            setattr(self.factory, f'{struct_name}', func)

        for typedef_name in paste.typedef_names:
            typedef_decl = paste.typedef_decl(typedef_name)

            if '(*)' in typedef_decl:
                binding_name = typedef_name
                if binding_name.endswith('_t'):
                    binding_name = binding_name[:-2]

                binding_point_name = 'extern_' + binding_name

                function_decl = paste.function_decl(
                    typedef_name, binding_point_name) + ';'
                self.externs.append(function_decl)

                func = partial(mock_binder, self, binding_point_name)

                setattr(self.factory, f'{typedef_name}', func)

    def create_tube(self, name=None):
        test_case_module = importlib.import_module(self._module_name)
        test_case_filename = test_case_module.__file__
        test_case_name = os.path.splitext(
            os.path.basename(test_case_filename))[0]

        c_filename = f'{test_case_name}.c'
        h_filename = f'{test_case_name}.h'

        tube_name = name if name else test_case_name

        return CrelmFactory().create_Tube(tube_name) \
            .set_source_folder_relative(test_case_filename) \
            .add_source_file(c_filename) \
            .add_header_file(h_filename) \
            .add_externs(self.externs)

    def _ensure_tube(self):
        if not self.tube:
            self.sut = None
            self.tube = self.create_tube()

        return self.tube

    def ensure_sut(self):
        self._ensure_tube()

        if not self.sut:
            self.sut = self.tube.squeeze()
            self.factory._ffi = self.tube._ffi

        return self.sut


