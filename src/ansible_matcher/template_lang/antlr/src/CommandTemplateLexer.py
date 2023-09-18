# Generated from /home/popovms/course/src/ansible_matcher/antlr/grammar/CommandTemplateLexer.g4 by ANTLR 4.12.0
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,14,91,6,-1,6,-1,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,
        2,5,7,5,2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,
        7,12,2,13,7,13,2,14,7,14,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,4,1,42,
        8,1,11,1,12,1,43,1,2,4,2,47,8,2,11,2,12,2,48,1,3,1,3,5,3,53,8,3,
        10,3,12,3,56,9,3,1,4,1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,
        1,6,1,7,1,7,1,8,1,8,1,9,1,9,1,10,1,10,1,11,1,11,1,12,1,12,1,12,1,
        12,1,12,1,13,1,13,1,13,1,13,1,14,1,14,0,0,15,3,1,5,2,7,3,9,4,11,
        5,13,6,15,7,17,8,19,9,21,10,23,11,25,12,27,0,29,13,31,14,3,0,1,2,
        5,2,0,32,32,60,60,1,0,60,60,1,0,32,32,3,0,65,90,95,95,97,122,4,0,
        48,57,65,90,95,95,97,122,92,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,
        1,9,1,0,0,0,1,11,1,0,0,0,1,13,1,0,0,0,1,15,1,0,0,0,1,17,1,0,0,0,
        2,19,1,0,0,0,2,21,1,0,0,0,2,23,1,0,0,0,2,25,1,0,0,0,2,27,1,0,0,0,
        2,29,1,0,0,0,2,31,1,0,0,0,3,33,1,0,0,0,5,41,1,0,0,0,7,46,1,0,0,0,
        9,50,1,0,0,0,11,57,1,0,0,0,13,61,1,0,0,0,15,66,1,0,0,0,17,70,1,0,
        0,0,19,72,1,0,0,0,21,74,1,0,0,0,23,76,1,0,0,0,25,78,1,0,0,0,27,80,
        1,0,0,0,29,85,1,0,0,0,31,89,1,0,0,0,33,34,5,60,0,0,34,35,5,60,0,
        0,35,36,1,0,0,0,36,37,6,0,0,0,37,4,1,0,0,0,38,42,8,0,0,0,39,40,5,
        60,0,0,40,42,8,1,0,0,41,38,1,0,0,0,41,39,1,0,0,0,42,43,1,0,0,0,43,
        41,1,0,0,0,43,44,1,0,0,0,44,6,1,0,0,0,45,47,7,2,0,0,46,45,1,0,0,
        0,47,48,1,0,0,0,48,46,1,0,0,0,48,49,1,0,0,0,49,8,1,0,0,0,50,54,7,
        3,0,0,51,53,7,4,0,0,52,51,1,0,0,0,53,56,1,0,0,0,54,52,1,0,0,0,54,
        55,1,0,0,0,55,10,1,0,0,0,56,54,1,0,0,0,57,58,5,58,0,0,58,59,1,0,
        0,0,59,60,6,4,1,0,60,12,1,0,0,0,61,62,5,62,0,0,62,63,5,62,0,0,63,
        64,1,0,0,0,64,65,6,5,2,0,65,14,1,0,0,0,66,67,3,7,2,0,67,68,1,0,0,
        0,68,69,6,6,3,0,69,16,1,0,0,0,70,71,9,0,0,0,71,18,1,0,0,0,72,73,
        5,109,0,0,73,20,1,0,0,0,74,75,5,110,0,0,75,22,1,0,0,0,76,77,5,111,
        0,0,77,24,1,0,0,0,78,79,5,112,0,0,79,26,1,0,0,0,80,81,3,13,5,0,81,
        82,1,0,0,0,82,83,6,12,4,0,83,84,6,12,2,0,84,28,1,0,0,0,85,86,3,7,
        2,0,86,87,1,0,0,0,87,88,6,13,3,0,88,30,1,0,0,0,89,90,9,0,0,0,90,
        32,1,0,0,0,7,0,1,2,41,43,48,54,5,5,1,0,2,2,0,4,0,0,6,0,0,7,6,0
    ]

class CommandTemplateLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    INSIDE = 1
    SPECS = 2

    OPEN = 1
    WORD = 2
    SPACE = 3
    FIELD_NAME = 4
    SPEC_OPEN = 5
    CLOSE = 6
    INSIDE_S = 7
    INSIDE_ANY = 8
    SPEC_MANY = 9
    SPEC_NO_WILDCARDS = 10
    SPEC_OPTIONAL = 11
    SPEC_PATH = 12
    SPECS_S = 13
    SPECS_ANY = 14

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "INSIDE", "SPECS" ]

    literalNames = [ "<INVALID>",
            "'<<'", "':'", "'>>'", "'m'", "'n'", "'o'", "'p'" ]

    symbolicNames = [ "<INVALID>",
            "OPEN", "WORD", "SPACE", "FIELD_NAME", "SPEC_OPEN", "CLOSE", 
            "INSIDE_S", "INSIDE_ANY", "SPEC_MANY", "SPEC_NO_WILDCARDS", 
            "SPEC_OPTIONAL", "SPEC_PATH", "SPECS_S", "SPECS_ANY" ]

    ruleNames = [ "OPEN", "WORD", "SPACE", "FIELD_NAME", "SPEC_OPEN", "CLOSE", 
                  "INSIDE_S", "INSIDE_ANY", "SPEC_MANY", "SPEC_NO_WILDCARDS", 
                  "SPEC_OPTIONAL", "SPEC_PATH", "SPECS_CLOSE", "SPECS_S", 
                  "SPECS_ANY" ]

    grammarFileName = "CommandTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.12.0")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


