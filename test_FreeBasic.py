"""
can you make a FreeBASIC intrupiter in python that fully works just like the real program. add (if and else and var and functions and print and input and loop and while loops and some basic math). make a test code with the intrupiter to run with all the stuff to add to the intrupiter. this is how to run "python FreeBASIC.py program.bas". dont turn the basic code into python then run. use the python to run it.
"""



# FreeBASIC.py -- a simple FreeBASIC-like interpreter in Python.

import sys, re

# Storage for variables, array lower bounds, and function definitions
var_table = {}    # name -> value (int/float/string or list for array)
var_low   = {}    # array lower bounds (name -> lower index)
functions = {}    # name.lower() -> {"args": [...], "body": [statements]}

def eval_expr(expr):
    """Evaluate a numeric/string expression (supports +,-,*,/ and function calls)."""
    # Tokenize: numbers, identifiers, parentheses, and operators.
    tokens = re.findall(r'\d+\.\d+|\d+|MOD|\^|[A-Za-z_]\w*|\+|\-|\*|\/|\(|\)|\,', expr, re.IGNORECASE)
    # Recursive-descent parser
    def parse_factor():
        token = tokens.pop(0)
        # Number
        if re.match(r'^\d+(\.\d+)?$', token):
            return float(token) if '.' in token else int(token)
        # Identifier or function/array
        if re.match(r'^[A-Za-z_]\w*$', token):
            name = token.lower()
            # Function or array call if followed by '('
            if tokens and tokens[0] == '(':
                tokens.pop(0)  # consume '('
                args = []
                if tokens[0] != ')':
                    args.append(parse_expr())
                    while tokens[0] == ',':
                        tokens.pop(0)
                        args.append(parse_expr())
                tokens.pop(0)  # consume ')'
                if name in functions:
                    # Call user-defined function
                    func = functions[name]
                    # Bind arguments
                    saved = {}
                    for arg_name, arg_val in zip(func["args"], args):
                        if arg_name in var_table:
                            saved[arg_name] = var_table[arg_name]
                        var_table[arg_name] = arg_val
                    # Execute function body
                    for stmt in func["body"]:
                        exec_statement(stmt)
                    # Get return value from 'result'
                    ret = var_table.get("result", 0)
                    # Restore environment
                    for arg_name in func["args"]:
                        if arg_name in saved: var_table[arg_name] = saved[arg_name]
                        elif arg_name in var_table: del var_table[arg_name]
                    if "result" in var_table: del var_table["result"]
                    return ret
                else:
                    # Array access: assume single-dimension
                    if token not in var_table or not isinstance(var_table[token], list):
                        return 0
                    idx = int(args[0])
                    lb = var_low.get(token, 0)
                    arr = var_table[token]
                    if idx < lb or idx >= len(arr):
                        return 0
                    return arr[idx]
            else:
                # Simple variable
                if name not in var_table:
                    var_table[name] = 0
                return var_table[name]
        # Parentheses
        if token == '(':
            val = parse_expr()
            tokens.pop(0)  # consume ')'
            return val
        # Unary plus/minus
        if token == '+': return +parse_factor()
        if token == '-': return -parse_factor()
        return 0

    def parse_term():
        val = parse_factor()
        while tokens and tokens[0] in ('*', '/'):
            op = tokens.pop(0)
            rhs = parse_factor()
            if op == '*': val *= rhs
            else: val /= rhs
        return val

    def parse_expr():
        val = parse_term()
        while tokens and tokens[0] in ('+', '-'):
            op = tokens.pop(0)
            rhs = parse_term()
            if op == '+': val += rhs
            else: val -= rhs
        return val

    # Remove empty tokens
    tokens = [tok for tok in tokens if tok]
    return parse_expr()

def exec_statement(stmt):
    """Execute a parsed statement dict."""
    typ = stmt["type"]
    if typ == "print":
        content = stmt["content"]
        # Handle string literals inside quotes
        parts = re.split(r'(".*?")', content)
        out = ""
        for part in parts:
            if not part: continue
            if part.startswith('"') and part.endswith('"'):
                out += part[1:-1]
            else:
                # Evaluate expressions (split on commas/semicolons for BASIC print)
                for seg in re.split(r';|,', part):
                    seg = seg.strip()
                    if not seg: continue
                    val = eval_expr(seg)
                    out += str(val)
        print(out)
    elif typ == "input":
        var = stmt["var"].lower()
        val = input(stmt.get("prompt",""))
        try: var_table[var] = int(val)
        except:
            try: var_table[var] = float(val)
            except: var_table[var] = val
    elif typ == "assign":
        name = stmt["target"].lower()
        val = eval_expr(stmt["expr"])
        idx_expr = stmt.get("index")
        if idx_expr is not None:
            idx = int(eval_expr(idx_expr))
            if name not in var_table or not isinstance(var_table[name], list):
                var_table[name] = []
            arr = var_table[name]
            lb = var_low.get(name, 0)
            if idx < lb or idx >= len(arr):
                # Expand array if needed
                newlen = max(len(arr), idx+1)
                if newlen > len(arr):
                    arr.extend([0]*(newlen-len(arr)))
                var_table[name] = arr
            arr[idx] = val
        else:
            var_table[name] = val
    elif typ == "if":
        left = eval_expr(stmt["left"])
        right= eval_expr(stmt["right"])
        op = stmt["op"]
        cond = False
        if op==">": cond = left>right
        if op=="<": cond = left<right
        if op=="=": cond = left==right
        if op=="<>": cond= left!=right
        if op==">=": cond= left>=right
        if op=="<=": cond= left<=right
        if cond:
            for s in stmt["true"]: exec_statement(s)
        else:
            for s in stmt["false"]: exec_statement(s)
    elif typ == "for":
        var = stmt["var"].lower()
        start = eval_expr(stmt["start"])
        end   = eval_expr(stmt["end"])
        step  = eval_expr(stmt["step"]) if stmt.get("step") else 1
        i = start
        # Loop inclusive like BASIC
        while (step>0 and i <= end) or (step<0 and i >= end):
            var_table[var] = i
            for s in stmt["body"]:
                exec_statement(s)
            i += step
    elif typ == "while":
        op = stmt["op"]
        def cond(): 
            L = eval_expr(stmt["left"]); R = eval_expr(stmt["right"])
            return (L>R if op==">" else
                    L<R if op=="<" else
                    L==R if op=="=" else
                    L!=R if op=="<>" else
                    L>=R if op==">=" else
                    L<=R if op=="<=" else False)
        while cond():
            for s in stmt["body"]:
                exec_statement(s)
    elif typ == "dim":
        name = stmt["var"].lower()
        lb = stmt.get("lower", 0)
        ub = stmt.get("upper", 0)
        size = ub - lb + 1
        var_table[name] = [0]*size
        var_low[name] = lb
    # (Function defs handled at parse time; no action here.)

def parse_condition(cond):
    """Split a condition like 'A > B' into (left, op, right)."""
    ops = [">=", "<=", "<>", ">", "<", "="]
    for op in ops:
        if op in cond:
            parts = cond.split(op,1)
            return parts[0].strip(), op, parts[1].strip()
    return cond, None, None

def parse_statements(lines, start, terminators=None):
    """Parse lines into a list of statement dicts, until a terminator."""
    stmts = []
    i = start
    while i < len(lines):
        raw = lines[i].strip()
        # Remove comments starting with ' or REM
        if "'" in raw: raw = raw.split("'",1)[0]
        if raw.upper().startswith("REM"): raw = ""
        line = raw.strip()
        if not line:
            i+=1; continue
        up = line.upper()
        # Check for end of a block
        if terminators:
            for term in terminators:
                if up == term or (term=="ENDIF" and up=="END IF") or (term=="WEND" and up=="WEND"):
                    return stmts, i
        # FUNCTION ... END FUNCTION
        if up.startswith("FUNCTION"):
            # e.g. "FUNCTION fname(a,b)"
            fn_part = line[len("FUNCTION"):].strip()
            name,args = fn_part.split("(",1)
            name = name.strip().lower()
            args = args.rstrip(")").split(",") if "(" in fn_part else []
            args = [a.strip().lower() for a in args if a.strip()]
            body_lines = []
            i+=1
            nested = 1
            while i < len(lines) and nested>0:
                line2 = lines[i].strip()
                if line2.upper().startswith("FUNCTION"): nested+=1
                if line2.upper().startswith("END FUNCTION") or line2.upper().startswith("END SUB"):
                    nested-=1
                    if nested==0: break
                if nested>0: body_lines.append(line2)
                i+=1
            # Recursively parse body
            fn_body, _ = parse_statements(body_lines, 0, None)
            functions[name] = {"args": args, "body": fn_body}
            i+=1; continue

        # IF ... THEN ... [ELSE] ... ENDIF
        if up.startswith("IF"):
            cond_str = line[2:line.upper().find("THEN")].strip() if "THEN" in up else line[2:].strip()
            left, op, right = parse_condition(cond_str)
            # Parse true block up to ELSE or ENDIF
            true_stmts, nxt = parse_statements(lines, i+1, terminators=["ELSE","ENDIF"])
            false_stmts = []
            # If we hit ELSE, parse the false block up to ENDIF
            if nxt < len(lines) and lines[nxt].strip().upper().startswith("ELSE"):
                false_stmts, end_if = parse_statements(lines, nxt+1, terminators=["ENDIF"])
                i = end_if
            else:
                i = nxt
            stmt = {"type":"if", "left":left, "op":op, "right":right,
                    "true": true_stmts, "false": false_stmts}
            stmts.append(stmt); i+=1; continue

        # FOR ... TO ... [STEP ...] ... NEXT
        if up.startswith("FOR"):
            # Regex to extract FOR variable, start, end, optional step
            m = re.match(r'FOR\s+(\w+)\s*=\s*(.*?)\s+TO\s+(.*?)(?:\s+STEP\s+(.*))?$', line, re.IGNORECASE)
            if m:
                var, start_expr, end_expr, step_expr = m.group(1), m.group(2), m.group(3), m.group(4)
            else:
                # Fallback naive parsing
                parts = line.split()
                var = parts[1]; rest = line[line.index('=')+1:]
                if "STEP" in rest.upper():
                    first,to_and_step = rest.split("TO",1)
                    start_expr = first.split('=')[1].strip()
                    end_part = to_and_step.split("STEP",1)
                    end_expr = end_part[0].strip(); step_expr = end_part[1].strip()
                else:
                    start_expr = rest.split("TO")[0].split('=')[1].strip()
                    end_expr   = rest.split("TO")[1].strip(); step_expr = None
            body_stmts, nxt = parse_statements(lines, i+1, terminators=["NEXT"])
            stmt = {"type":"for", "var":var.lower(),
                    "start":start_expr.strip(), "end":end_expr.strip(),
                    "step": step_expr.strip() if step_expr else None,
                    "body": body_stmts}
            stmts.append(stmt); i = nxt+1; continue

        # WHILE ... WEND
        if up.startswith("WHILE"):
            cond_str = line[5:].strip()
            left, op, right = parse_condition(cond_str)
            body_stmts, nxt = parse_statements(lines, i+1, terminators=["WEND"])
            stmt = {"type":"while", "left":left, "op":op, "right":right, "body":body_stmts}
            stmts.append(stmt); i = nxt+1; continue

        # DIM for array or variable
        if up.startswith("DIM"):
            rem = line[3:].strip()
            # Array with To
            m = re.match(r'(\w+)\s*\(\s*(\d+)\s+TO\s+(\d+)\s*\)', rem, re.IGNORECASE)
            if m:
                name, lb, ub = m.group(1).lower(), int(m.group(2)), int(m.group(3))
            else:
                m2 = re.match(r'(\w+)\s*\(\s*(\d+)\s*\)', rem, re.IGNORECASE)
                if m2:
                    name, lb, ub = m2.group(1).lower(), 0, int(m2.group(2))
                else:
                    name, lb, ub = rem.split()[0].lower(), 0, 0
            stmt = {"type":"dim", "var":name, "lower":lb, "upper":ub}
            stmts.append(stmt); i+=1; continue

        # PRINT
        if up.startswith("PRINT"):
            content = line[5:].strip()
            stmts.append({"type":"print", "content":content}); i+=1; continue

        # INPUT
        if up.startswith("INPUT"):
            parts = line.split()
            var = parts[1] if len(parts)>1 else ""
            stmts.append({"type":"input","var":var}); i+=1; continue

        # Assignment (var or array element)
        if "=" in line:
            left,right = line.split("=",1)
            left=left.strip(); right=right.strip()
            if "(" in left and ")" in left:
                nm, idx = left.split("(",1)
                idx = idx.rstrip(")")
                stmt = {"type":"assign", "target":nm.lower(), "index":idx, "expr":right}
            else:
                stmt = {"type":"assign", "target":left.lower(), "index":None, "expr":right}
            stmts.append(stmt); i+=1; continue

        # No recognized statement; skip
        i+=1

    return stmts, i

def main():
    if len(sys.argv) < 2:
        print("Usage: python FreeBASIC.py program.bas")
        return
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    program_stmts, _ = parse_statements(lines, 0, None)
    for stmt in program_stmts:
        exec_statement(stmt)

if __name__ == "__main__":
    main()
