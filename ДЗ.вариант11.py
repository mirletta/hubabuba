# Конфигурационные языки:
# - D2, Mermaid, PlantUML, DOT (языки описания графов)
# - YAML, TOML, JSON, CSV, XML (языки общего назначения)
# - CSS, HTML (языки описания веб-страниц)
# - Lark
# - DSL (Domain Specific Language, предметно-ориентированные языки)

import tomli_w
import lark

grammar = r"""
%ignore /\s+/
%ignore /\*[^\n]*/      // однострочные комментарии
%ignore /\{-[^-]*-\}/   // многострочные комментарии

NUM: /0[bB][01]+/
NAME: /[_a-zA-Z][_a-zA-Z0-9]*/

start: (const | table)*

const: NAME ":=" value ";"

table: "table" "(" [pair ("," pair)*] ")"
pair: NAME "=>" value

array: "(" "{" [value ("," value)*] "}" ")"

prefixed: "#" "[" prefix "]"
prefix: add | sub | mul | power

add: "+" value value
sub: "-" value value
mul: "*" value value
power: "pow" "(" value value ")"

?value: table
      | array
      | prefixed
      | NAME
      | NUM
"""

class T(lark.Transformer):
    def __init__(self):
        super().__init__(visit_tokens=True)
        self.constants = {}
    
    def NAME(self, name):
        return str(name)
    
    def NUM(self, num):
        val = num.value
        if val.lower().startswith('0b'):
            return int(val[2:], 2)
        return int(val, 2)
    
    def const(self, items):
        name, val = items
        self.constants[name] = val
        return None
    
    def table(self, items):
        if not items:
            return {}
        
        result = {}
        for key, value in items:
            if isinstance(value, lark.Tree) and value.data == 'prefix':
                value = value.children[0]
            
            if isinstance(value, str) and value in self.constants:
                result[key] = self.constants[value]
            else:
                result[key] = value
        return result
    
    def pair(self, items):
        key, val = items
        return (key, val)
    
    def array(self, items):
        if items is None:
            return []
        
        result = []
        for item in items:
            if isinstance(item, str) and item in self.constants:
                result.append(self.constants[item])
            else:
                result.append(item)
        return result
    
    def add(self, items):
        a, b = items
        a = self.constants.get(a, a) if isinstance(a, str) else a
        b = self.constants.get(b, b) if isinstance(b, str) else b
        return a + b
    
    def sub(self, items):
        a, b = items
        a = self.constants.get(a, a) if isinstance(a, str) else a
        b = self.constants.get(b, b) if isinstance(b, str) else b
        return a - b
    
    def mul(self, items):
        a, b = items
        a = self.constants.get(a, a) if isinstance(a, str) else a
        b = self.constants.get(b, b) if isinstance(b, str) else b
        return a * b
    
    def power(self, items):
        a, b = items
        a = self.constants.get(a, a) if isinstance(a, str) else a
        b = self.constants.get(b, b) if isinstance(b, str) else b
        return a ** b
    
    def prefixed(self, items):
        return items[0]
    
    def start(self, items):
        result = {}
        for item in items:
            if isinstance(item, dict):
                result.update(item)
        return result


INPUT = '''
test := 0b101;
table(
    a => 0b1,
    b => test,
    c => ({0b10, 0b11}),
    d => #[+ 0b1 0b1],
    e => #[pow(0b10 0b11)]
)
'''

IR = dict(
    abc=42,
    def_=[42, 1],
    xyz=dict(key=123))

OUTPUT = '''
abc = 42
def = [42, 1]
[xyz]
key = 123
'''

def transform(input: str) -> str:
    parser = lark.Lark(grammar, parser='lalr')
    treee = parser.parse(input)
    
  
    print("Дерево парсинга:")
    for subtree in treee.iter_subtrees():
        indent = "▶ " * (subtree.meta.line - 1 if hasattr(subtree.meta, 'line') else 0)
        print(f"{indent}{subtree.data}")
        for child in subtree.children:
            if isinstance(child, lark.Tree):
                continue
            print(f"{indent}{child}")
    
    a = T().transform(treee)
    output = tomli_w.dumps(a)
    return output

print(transform(INPUT))
