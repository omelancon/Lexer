from src.Lexer.Lexer import Lexer
from src.Visual import visual_lexer
import copy

number = "[1-9][0-9]*"
decimal = number + "\.[0-9]+"


def INT(t, v):
    t.params[v] = "I have seen that one"
    return "INT"


rules = [
    (number, INT),
    (decimal, "FLOAT"),
    ("\+", "PLUS"),
    ("\*", "TIMES"),
    ("=", "EQUAL"),
    (" ", None),
    ("#.*", None)
]

lexer = Lexer(rules=rules)
lexer.set_line_rule("\n")
lexer.build()

visual_lexer.plot_dfa(lexer.dfa.start)

buffer = """1 + 3.08 * 5 = 1.54
# We can put some comments here
1+1=2"""

lexer.read(buffer)

new = copy.deepcopy(lexer)

new.save("test.p")

loaded = Lexer.load("test.p")

tk = True

while tk:
    tk = loaded.lex()
    print tk
