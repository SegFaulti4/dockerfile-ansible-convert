# Generated from /home/popovms/course/src/ansible_matcher/antlr/grammar/CommandTemplateLexer.g4 by ANTLR 4.11.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,13,87,6,-1,6,-1,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,
        2,5,7,5,2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,
        7,12,2,13,7,13,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,4,1,40,8,1,11,1,12,
        1,41,1,2,4,2,45,8,2,11,2,12,2,46,1,3,1,3,5,3,51,8,3,10,3,12,3,54,
        9,3,1,4,1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,7,1,7,
        1,8,1,8,1,9,1,9,1,10,1,10,1,11,1,11,1,11,1,11,1,11,1,12,1,12,1,12,
        1,12,1,13,1,13,0,0,14,3,1,5,2,7,3,9,4,11,5,13,6,15,7,17,8,19,9,21,
        10,23,11,25,0,27,12,29,13,3,0,1,2,5,2,0,32,32,60,60,1,0,60,60,1,
        0,32,32,3,0,65,90,95,95,97,122,4,0,48,57,65,90,95,95,97,122,88,0,
        3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,1,9,1,0,0,0,1,11,1,0,0,0,1,13,
        1,0,0,0,1,15,1,0,0,0,1,17,1,0,0,0,2,19,1,0,0,0,2,21,1,0,0,0,2,23,
        1,0,0,0,2,25,1,0,0,0,2,27,1,0,0,0,2,29,1,0,0,0,3,31,1,0,0,0,5,39,
        1,0,0,0,7,44,1,0,0,0,9,48,1,0,0,0,11,55,1,0,0,0,13,59,1,0,0,0,15,
        64,1,0,0,0,17,68,1,0,0,0,19,70,1,0,0,0,21,72,1,0,0,0,23,74,1,0,0,
        0,25,76,1,0,0,0,27,81,1,0,0,0,29,85,1,0,0,0,31,32,5,60,0,0,32,33,
        5,60,0,0,33,34,1,0,0,0,34,35,6,0,0,0,35,4,1,0,0,0,36,40,8,0,0,0,
        37,38,5,60,0,0,38,40,8,1,0,0,39,36,1,0,0,0,39,37,1,0,0,0,40,41,1,
        0,0,0,41,39,1,0,0,0,41,42,1,0,0,0,42,6,1,0,0,0,43,45,7,2,0,0,44,
        43,1,0,0,0,45,46,1,0,0,0,46,44,1,0,0,0,46,47,1,0,0,0,47,8,1,0,0,
        0,48,52,7,3,0,0,49,51,7,4,0,0,50,49,1,0,0,0,51,54,1,0,0,0,52,50,
        1,0,0,0,52,53,1,0,0,0,53,10,1,0,0,0,54,52,1,0,0,0,55,56,5,58,0,0,
        56,57,1,0,0,0,57,58,6,4,1,0,58,12,1,0,0,0,59,60,5,62,0,0,60,61,5,
        62,0,0,61,62,1,0,0,0,62,63,6,5,2,0,63,14,1,0,0,0,64,65,3,7,2,0,65,
        66,1,0,0,0,66,67,6,6,3,0,67,16,1,0,0,0,68,69,9,0,0,0,69,18,1,0,0,
        0,70,71,5,109,0,0,71,20,1,0,0,0,72,73,5,111,0,0,73,22,1,0,0,0,74,
        75,5,112,0,0,75,24,1,0,0,0,76,77,3,13,5,0,77,78,1,0,0,0,78,79,6,
        11,4,0,79,80,6,11,2,0,80,26,1,0,0,0,81,82,3,7,2,0,82,83,1,0,0,0,
        83,84,6,12,3,0,84,28,1,0,0,0,85,86,9,0,0,0,86,30,1,0,0,0,7,0,1,2,
        39,41,46,52,5,5,1,0,2,2,0,4,0,0,6,0,0,7,6,0
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
    SPEC_OPTIONAL = 10
    SPEC_PATH = 11
    SPECS_S = 12
    SPECS_ANY = 13

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "INSIDE", "SPECS" ]

    literalNames = [ "<INVALID>",
            "'<<'", "':'", "'>>'", "'m'", "'o'", "'p'" ]

    symbolicNames = [ "<INVALID>",
            "OPEN", "WORD", "SPACE", "FIELD_NAME", "SPEC_OPEN", "CLOSE", 
            "INSIDE_S", "INSIDE_ANY", "SPEC_MANY", "SPEC_OPTIONAL", "SPEC_PATH", 
            "SPECS_S", "SPECS_ANY" ]

    ruleNames = [ "OPEN", "WORD", "SPACE", "FIELD_NAME", "SPEC_OPEN", "CLOSE", 
                  "INSIDE_S", "INSIDE_ANY", "SPEC_MANY", "SPEC_OPTIONAL", 
                  "SPEC_PATH", "SPECS_CLOSE", "SPECS_S", "SPECS_ANY" ]

    grammarFileName = "CommandTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None

