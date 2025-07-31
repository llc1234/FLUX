import sys


class Lexer:
    def __init__(self, code_):
        self.code = code_
        self.data_list = []

    def lex_var(self, line):
        print(" - VAR Found: TYPE: ", end="")
        parts = line.split('=', 1)
        left_side = parts[0].strip()
        right_side = parts[1].strip()
            
        tokens = left_side.split()
        var_name = tokens[-1]

        try:
            value = eval(right_side)
        except Exception as e:
            print(f"Error evaluating value: {e}")
            return

        # Determine the type of the value
        if isinstance(value, int):
            var_type = 'INT'
        elif isinstance(value, float):
            var_type = 'FLOAT'
        elif isinstance(value, str):
            var_type = 'STRING'
        else:
            var_type = 'UNKNOWN'

        print(var_type)

        self.data_list.append(('VAR', var_name, var_type, value))

    def tokenize(self):
        for line in self.code.splitlines():
            # stripped = line.strip().split(" ")
            # command = [item for item in stripped if item != '']
            # print(command)

            if "var" in line:
                self.lex_var(line)

        print("data_list ------------------------")
        print(self.data_list)


class Parser:
    def __init__(self):
        pass


def main():
    if len(sys.argv) < 2:
        print("Usage: python FLUX.py program.fx")
        return
    with open(sys.argv[1]) as f:
        lines = f.read()
        print(f"Open file: {sys.argv[1]}")
        print(f"File size: {len(lines)}")

    lex = Lexer(lines)
    tokens = lex.tokenize()
    # parser = Parser(tokens)
    # ast = parser.parse_program()
    # interp = Interpreter()
    # interp.eval(ast)

if __name__ == "__main__":
    main()
