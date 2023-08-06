
import sys
from dataclasses import dataclass


@dataclass
class _ContentSet:
    h: str = ''
    c: str = ''
    py: str = ''

    def get(self, key):
        if 'h' == key:
            return self.h

        if 'c' == key:
            return self.c

        if 'py' == key:
            return self.py

        raise ValueError(f'invalid key "{key}"')


_file_content_set = _ContentSet(
    h=r"""#pragma once

{content}
""", c=r"""#include "{full_name}.h"

{content}
""", py=r"""from ctdd import Tester

class BootstrapTests(Tester):
    def test_sut_compiles(self):
        self.assertIsNotNone(self.sut)

{content}

Tester.go()
""")

_test_content_set = _ContentSet(py=r"""
class {Name}Tests(Tester):
    pass
""")

_class_content_set = _ContentSet(h=r"""
struct {name}_config_t
{{
    char const *name;
}};

struct {name}_state_t
{{
    struct {name}_config_t config;
}};

int {name}_init(struct {name}_state_t *, struct {name}_config_t const *);
void {name}_run(struct {name}_state_t *);
""", c=r"""
int {name}_init(struct {name}_state_t *state, struct {name}_config_t const *config)
{{
    state->config = *config;

    return -1;
}}

void {name}_run(struct {name}_state_t *state)
{{
}}
""", py=r"""
class InitTests(Tester):
    def test_init_copies_config(self):
        expected = "{name}"

        config = self.factory.{name}_config_t()
        config.name = self.factory.C_string(expected)
        state = self.factory.{name}_state_t()
        
        self.sut.{name}_init(state, config)
        actual = self.factory.P_str(config.name)

        self.assertEqual(expected, actual)
        
        
    def test_init_returns_zero(self):
        config = self.factory.{name}_config_t()
        state = self.factory.{name}_state_t()
        
        self.assertEqual(0, self.sut.{name}_init(state, config))
""")


def _emit_files(name, exts, file_templates, content_templates):
    clean_name = _clean_name(name)

    replacements = {
        'full_name': name,
        'Name': clean_name.title(),
        'name': clean_name.lower()
    }
    for ext in exts:
        content = content_templates.get(ext).format_map(replacements)
        replacements['content'] = content
        file = file_templates.get(ext).format_map(replacements)

        filename = f'{name}.{ext}'

        print(f'creating {filename}')

        with open(filename, 'w') as f:
            f.write(file)


def _clean_name(name):
    if name.endswith('_tests'):
        name = name[:-6]

    if name.endswith('_test'):
        name = name[:-5]

    return name


def main() -> int:
    print(sys.argv)

    if '-c' == sys.argv[1]:
        name = sys.argv[2]
        print(f'creating class "{name}" tester files')
        _emit_files(name, ('h', 'c', 'py'),
                    _file_content_set, _class_content_set)

    if '-t' == sys.argv[1]:
        name = sys.argv[2]
        print(f'creating test "{name}" tester file')
        _emit_files(name, ('h', 'c', 'py',),
                    _file_content_set, _test_content_set)

    return 0


if __name__ == '__main__':
    sys.exit(main())
