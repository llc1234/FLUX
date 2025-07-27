import sys


class Token:
    def __init__(self, type_, value=None):
        self.type = type_       # e.g. 'NUMBER', 'IDENT', 'KEYWORD', etc.
        self.value = value
    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r})"

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.current_char = code[0] if code else None
    
    def advance(self):
        self.pos += 1
        self.current_char = self.code[self.pos] if self.pos < len(self.code) else None
    
    def peek(self):
        return self.code[self.pos+1] if self.pos+1 < len(self.code) else None
    
    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            c = self.current_char
            if c.isspace():
                # Keep newline as a token for statement endings
                if c == '\n':
                    tokens.append(Token('NL'))
                self.advance()
                continue
            # Multi-char operators
            if c == '<' and self.peek() == '<':
                tokens.append(Token('LSHIFT','<<')); self.advance(); self.advance(); continue
            if c == '+' and self.peek() == '=':
                tokens.append(Token('PLUSEQ','+=')); self.advance(); self.advance(); continue
            if c == '-' and self.peek() == '=':
                tokens.append(Token('MINUSEQ','-=')); self.advance(); self.advance(); continue
            if c == '*' and self.peek() == '=':
                tokens.append(Token('TIMESEQ','*=')); self.advance(); self.advance(); continue
            if c == '/' and self.peek() == '=':
                tokens.append(Token('DIVEQ','/=')); self.advance(); self.advance(); continue
            # Number literal
            if c.isdigit():
                num_str = ''
                has_dot = False
                while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
                    if self.current_char == '.':
                        if has_dot: raise Exception("Invalid number")
                        has_dot = True
                    num_str += self.current_char
                    self.advance()
                tokens.append(Token('NUMBER', float(num_str) if has_dot else int(num_str)))
                continue
            # Identifier, keyword, or boolean literal
            if c.isalpha() or c == '_':
                id_str = ''
                while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
                    id_str += self.current_char
                    self.advance()
                if id_str in ('function','end','for','while','if','return','print','input'):
                    tokens.append(Token('KEYWORD', id_str))
                elif id_str == 'in':
                    tokens.append(Token('KEYWORD','in'))
                elif id_str in ('int','float','string','bool'):
                    tokens.append(Token('TYPE', id_str))
                elif id_str in ('true','false'):
                    tokens.append(Token('BOOL', id_str == 'true'))
                else:
                    tokens.append(Token('IDENT', id_str))
                continue
            # String literal
            if c == '"':
                self.advance()
                str_val = ''
                while self.current_char is not None and self.current_char != '"':
                    if self.current_char == '\\':
                        # Handle escape sequences \n or \"
                        if self.peek() == 'n':
                            str_val += '\n'; self.advance(); self.advance(); continue
                        if self.peek() == '"':
                            str_val += '"'; self.advance(); self.advance(); continue
                        # (Other escapes can be added)
                    str_val += self.current_char
                    self.advance()
                if self.current_char != '"':
                    raise Exception("Unterminated string")
                self.advance()
                tokens.append(Token('STRING', str_val))
                continue
            # Single-char tokens
            if c == '+': tokens.append(Token('PLUS','+')); self.advance(); continue
            if c == '-': tokens.append(Token('MINUS','-')); self.advance(); continue
            if c == '*': tokens.append(Token('TIMES','*')); self.advance(); continue
            if c == '/': tokens.append(Token('DIVIDE','/')); self.advance(); continue
            if c == '=': tokens.append(Token('EQ','=')); self.advance(); continue
            if c == '<': tokens.append(Token('LT','<')); self.advance(); continue
            if c == '>': tokens.append(Token('GT','>')); self.advance(); continue
            if c == '(': tokens.append(Token('LPAREN','(')); self.advance(); continue
            if c == ')': tokens.append(Token('RPAREN',')')); self.advance(); continue
            if c == '[': tokens.append(Token('LBRACKET','[')); self.advance(); continue
            if c == ']': tokens.append(Token('RBRACKET',']')); self.advance(); continue
            if c == ':': tokens.append(Token('COLON',':')); self.advance(); continue
            if c == ',': tokens.append(Token('COMMA',',')); self.advance(); continue
            raise Exception(f"Unexpected character: {c}")
        tokens.append(Token('EOF'))
        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0]
    
    def error(self, msg):
        raise Exception(f"{msg}. Got {self.current}")
    
    def advance(self):
        self.pos += 1
        self.current = self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF')
        return self.current
    
    def eat(self, type_, value=None):
        if self.current.type == type_ and (value is None or self.current.value == value):
            tok = self.current
            self.advance()
            return tok
        else:
            self.error(f"Expected {type_} {value}")
    
    def peek(self):
        return self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else Token('EOF')
    
    def parse_program(self):
        stmts = []
        while self.current.type != 'EOF':
            if self.current.type == 'NL':
                self.advance(); continue
            if self.current.type=='KEYWORD' and self.current.value=='function':
                stmts.append(self.parse_function())
            else:
                stmts.append(self.parse_statement())
        return ('PROGRAM', stmts)
    
    def parse_function(self):
        self.eat('KEYWORD','function')
        name = self.eat('IDENT').value
        self.eat('LPAREN')
        params = []
        if self.current.type == 'TYPE':
            while True:
                ptype = self.eat('TYPE').value
                pname = self.eat('IDENT').value
                params.append((ptype,pname))
                if self.current.type=='COMMA': self.eat('COMMA')
                else: break
        self.eat('RPAREN')
        if self.current.type=='NL': self.advance()
        body = []
        while not (self.current.type=='KEYWORD' and self.current.value=='end'):
            if self.current.type=='NL': self.advance(); continue
            body.append(self.parse_statement())
        self.eat('KEYWORD','end')
        self.eat('KEYWORD','function')
        if self.current.type=='NL': self.advance()
        return ('FUNCDEF', name, params, body)
    
    def parse_statement(self):
        if self.current.type == 'TYPE':
            # Variable declaration
            vtype = self.eat('TYPE').value
            vname = self.eat('IDENT').value
            self.eat('EQ')
            expr = self.parse_expression()
            if self.current.type=='NL': self.advance()
            return ('VAR_DECL', vtype, vname, expr)
        if self.current.type=='KEYWORD':
            if self.current.value=='print':
                return self.parse_print()
            if self.current.value=='if':
                return self.parse_if()
            if self.current.value=='while':
                return self.parse_while()
            if self.current.value=='for':
                return self.parse_for()
            if self.current.value=='return':
                return self.parse_return()
        if self.current.type=='IDENT':
            nxt = self.peek().type
            # Assignment (including += etc) or function call
            if nxt in ('EQ','PLUSEQ','MINUSEQ','TIMESEQ','DIVEQ'):
                return self.parse_assignment()
            if nxt=='LPAREN':
                call_node = self.parse_call()
                if self.current.type=='NL': self.advance()
                return call_node
        self.error("Unknown statement start")
    
    def parse_assignment(self):
        name = self.eat('IDENT').value
        if self.current.type=='EQ':
            self.eat('EQ'); op='='
        else:
            tok = self.current
            op = tok.value
            self.advance()
        expr = self.parse_expression()
        if self.current.type=='NL': self.advance()
        return ('ASSIGN', name, op, expr)
    
    def parse_print(self):
        self.eat('KEYWORD','print')
        parts = []
        while self.current.type=='LSHIFT':
            self.eat('LSHIFT')
            parts.append(self.parse_expression())
        if self.current.type=='NL': self.advance()
        return ('PRINT', parts)
    
    def parse_if(self):
        self.eat('KEYWORD','if')
        cond = self.parse_expression()
        if self.current.type=='NL': self.advance()
        branch=[]
        while not (self.current.type=='KEYWORD' and self.current.value=='end'):
            if self.current.type=='NL': self.advance(); continue
            branch.append(self.parse_statement())
        self.eat('KEYWORD','end'); self.eat('KEYWORD','if')
        if self.current.type=='NL': self.advance()
        return ('IF', cond, branch)
    
    def parse_while(self):
        self.eat('KEYWORD','while')
        if self.current.type=='LPAREN':
            self.eat('LPAREN'); cond=self.parse_expression(); self.eat('RPAREN')
        else:
            cond = self.parse_expression()
        if self.current.type=='NL': self.advance()
        body=[]
        while not (self.current.type=='KEYWORD' and self.current.value=='end'):
            if self.current.type=='NL': self.advance(); continue
            body.append(self.parse_statement())
        self.eat('KEYWORD','end'); self.eat('KEYWORD','while')
        if self.current.type=='NL': self.advance()
        return ('WHILE', cond, body)
    
    def parse_for(self):
        self.eat('KEYWORD','for')
        var = self.eat('IDENT').value
        self.eat('EQ')
        start = self.parse_expression()
        self.eat('KEYWORD','in')
        end = self.parse_expression()
        if self.current.type=='NL': self.advance()
        body=[]
        while not (self.current.type=='KEYWORD' and self.current.value=='end'):
            if self.current.type=='NL': self.advance(); continue
            body.append(self.parse_statement())
        self.eat('KEYWORD','end'); self.eat('KEYWORD','for')
        if self.current.type=='NL': self.advance()
        return ('FOR', var, start, end, body)
    
    def parse_return(self):
        self.eat('KEYWORD','return')
        expr = self.parse_expression()
        if self.current.type=='NL': self.advance()
        return ('RETURN', expr)
    
    def parse_call(self):
        node = self.parse_primary()
        if node[0] != 'CALL':
            self.error("Expected function call")
        return node
    
    def parse_expression(self):
        node = self.parse_term()
        while self.current.type in ('PLUS','MINUS'):
            op = self.current.value
            if op == '+': self.eat('PLUS')
            else: self.eat('MINUS')
            right = self.parse_term()
            node = ('BINOP', op, node, right)
        # After arithmetic, check for comparison
        if self.current.type in ('LT','GT'):
            op = self.current.value
            self.advance()
            right = self.parse_term()
            return ('CMP', op, node, right)
        return node
    
    def parse_term(self):
        node = self.parse_factor()
        while self.current.type in ('TIMES','DIVIDE'):
            op = self.current.value
            if op=='*': self.eat('TIMES')
            else: self.eat('DIVIDE')
            right = self.parse_factor()
            node = ('BINOP', op, node, right)
        return node
    
    def parse_factor(self):
        if self.current.type=='PLUS':
            self.eat('PLUS')
            return self.parse_factor()
        if self.current.type=='MINUS':
            self.eat('MINUS')
            return ('UMINUS', self.parse_factor())
        return self.parse_primary()
    
    def parse_primary(self):
        tok = self.current
        if tok.type=='NUMBER':
            self.advance()
            return ('NUMBER', tok.value)
        if tok.type=='STRING':
            self.advance()
            return ('STRING', tok.value)
        if tok.type=='BOOL':
            self.advance()
            return ('BOOL', tok.value)
        if tok.type=='IDENT':
            name = tok.value; self.advance()
            # Array slicing or function call or variable
            if self.current.type=='LBRACKET':
                # slicing: [start:end]
                self.eat('LBRACKET')
                start = None
                if self.current.type!='COLON':
                    start = self.parse_expression()
                if self.current.type=='COLON':
                    self.eat('COLON')
                    end = None
                    if self.current.type!='RBRACKET':
                        end = self.parse_expression()
                else:
                    end = None
                self.eat('RBRACKET')
                return ('SLICE', name, start, end)
            if self.current.type=='LPAREN':
                self.eat('LPAREN')
                args=[]
                if self.current.type!='RPAREN':
                    while True:
                        args.append(self.parse_expression())
                        if self.current.type=='COMMA': self.eat('COMMA'); continue
                        break
                self.eat('RPAREN')
                return ('CALL', name, args)
            return ('VAR', name)
        if tok.type=='KEYWORD' and tok.value=='input':
            # Input call: input << expr
            self.eat('KEYWORD','input')
            self.eat('LSHIFT')
            prompt = self.parse_expression()
            return ('INPUT', prompt)
        if tok.type=='LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            return expr
        self.error("Unexpected token in expression")
    
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_vars = {}    # global scope
        self.functions = {}      # function name -> (params, body)
        self.envs = [self.global_vars]  # stack of scopes
    
    def current_env(self):
        return self.envs[-1]
    def get_var(self, name):
        for env in reversed(self.envs):
            if name in env:
                return env[name]
        raise Exception(f"Variable '{name}' not defined")
    def set_var(self, name, value):
        for env in reversed(self.envs):
            if name in env:
                env[name] = value
                return
        raise Exception(f"Variable '{name}' not defined")
    
    def eval(self, node):
        typ = node[0]
        if typ == 'PROGRAM':
            for stmt in node[1]:
                self.exec(stmt)
        else:
            return self.exec(node)
    
    def exec(self, node):
        typ = node[0]
        # Function definition: store it
        if typ == 'FUNCDEF':
            _, name, params, body = node
            self.functions[name] = (params, body)
            return
        if typ == 'VAR_DECL':
            _, vartype, name, expr = node
            val = self.eval(expr)
            # Type enforcement (convert or check)
            if vartype == 'int':
                if isinstance(val,float): val = int(val)
                elif not isinstance(val,int): raise Exception("Type mismatch int")
            if vartype == 'float':
                if isinstance(val,int): val = float(val)
                elif not isinstance(val,float): raise Exception("Type mismatch float")
            if vartype == 'string':
                if not isinstance(val,str): val = str(val)
            if vartype == 'bool':
                if isinstance(val,(int,float)): val = bool(val)
                elif not isinstance(val,bool): raise Exception("Type mismatch bool")
            self.current_env()[name] = val
        elif typ == 'ASSIGN':
            _, name, op, expr = node
            val = self.eval(expr)
            if op == '=':
                self.set_var(name, val)
            else:
                old = self.get_var(name)
                if op == '+=':
                    # String concatenation if either side is string
                    if isinstance(old,str) or isinstance(val,str):
                        res = str(old) + str(val)
                    else:
                        res = old + val
                elif op == '-=': res = old - val
                elif op == '*=': res = old * val
                elif op == '/=': res = old / val
                self.set_var(name, res)
        elif typ == 'PRINT':
            _, parts = node
            out_str = ''
            for part in parts:
                v = self.eval(part)
                out_str += str(v) if v is not None else ''
            print(out_str, end='')
        elif typ == 'IF':
            _, cond, branch = node
            if self.eval(cond):
                for stmt in branch:
                    self.exec(stmt)
        elif typ == 'WHILE':
            _, cond, body = node
            while self.eval(cond):
                for stmt in body:
                    self.exec(stmt)
        elif typ == 'FOR':
            _, var, start_expr, end_expr, body = node
            start = self.eval(start_expr); end = self.eval(end_expr)
            if not (isinstance(start,int) and isinstance(end,int)):
                raise Exception("Loop bounds must be integers")
            for i in range(start, end):
                self.current_env()[var] = i
                for stmt in body:
                    self.exec(stmt)
        elif typ == 'RETURN':
            _, expr = node
            val = self.eval(expr)
            raise ReturnException(val)
        elif typ == 'CALL':
            _, name, args = node
            arg_vals = [self.eval(a) for a in args]
            if name not in self.functions:
                raise Exception(f"Function '{name}' not defined")
            params, body = self.functions[name]
            if len(arg_vals) != len(params):
                raise Exception(f"Argument count mismatch in call to {name}")
            # Create new local scope
            new_env = {}
            for (ptype,pname), val in zip(params, arg_vals):
                new_env[pname] = val
            self.envs.append(new_env)
            ret_val = None
            try:
                for stmt in body:
                    self.exec(stmt)
            except ReturnException as re:
                ret_val = re.value
            self.envs.pop()
            return ret_val
        elif typ == 'INPUT':
            _, prompt_expr = node
            prompt_val = self.eval(prompt_expr)
            ret = input(str(prompt_val))
            return ret
        elif typ == 'NUMBER':
            return node[1]
        elif typ == 'STRING':
            return node[1]
        elif typ == 'BOOL':
            return node[1]
        elif typ == 'VAR':
            return self.get_var(node[1])
        elif typ == 'BINOP':
            _, op, left, right = node
            l = self.eval(left); r = self.eval(right)
            if op == '+':
                if isinstance(l,str) or isinstance(r,str): return str(l) + str(r)
                return l + r
            if op == '-': return l - r
            if op == '*': return l * r
            if op == '/':
                res = l / r
                if isinstance(l,int) and isinstance(r,int) and res.is_integer():
                    return int(res)
                return res
        elif typ == 'CMP':
            _, op, left, right = node
            l = self.eval(left); r = self.eval(right)
            if op == '<': return l < r
            if op == '>': return l > r
        elif typ == 'UMINUS':
            return -self.eval(node[1])
        elif typ == 'SLICE':
            _, name, start_node, end_node = node
            s = self.get_var(name)
            if not isinstance(s,str): raise Exception("Slice on non-string")
            start = self.eval(start_node) if start_node is not None else 0
            end = self.eval(end_node) if end_node is not None else None
            return s[start:end]
        else:
            raise Exception(f"Unknown AST node: {typ}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python FLUX.py program.fx")
        return
    with open(sys.argv[1]) as f:
        lines = f.read()
    lex = Lexer(lines)
    tokens = lex.tokenize()
    parser = Parser(tokens)
    ast = parser.parse_program()
    interp = Interpreter()
    interp.eval(ast)

if __name__ == "__main__":
    main()
