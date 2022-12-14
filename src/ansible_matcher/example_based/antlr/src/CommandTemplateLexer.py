# Generated from /home/popovms/course/dockerfile-ansible-convert/src/ansible_matcher/example_based/antlr/grammar/CommandTemplateLexer.g4 by ANTLR 4.11.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,11,79,6,-1,6,-1,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,
        2,5,7,5,2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,
        1,0,1,0,1,0,1,0,1,1,1,1,1,1,4,1,36,8,1,11,1,12,1,37,1,2,4,2,41,8,
        2,11,2,12,2,42,1,3,1,3,5,3,47,8,3,10,3,12,3,50,9,3,1,4,1,4,1,4,1,
        4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,7,1,7,1,8,1,8,1,9,1,9,1,
        10,1,10,1,10,1,10,1,10,1,11,1,11,1,11,1,11,0,0,12,3,1,5,2,7,3,9,
        4,11,5,13,6,15,7,17,8,19,9,21,10,23,0,25,11,3,0,1,2,5,2,0,32,32,
        123,123,1,0,123,123,1,0,32,32,3,0,65,90,95,95,97,122,4,0,48,57,65,
        90,95,95,97,122,80,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,1,9,1,0,0,
        0,1,11,1,0,0,0,1,13,1,0,0,0,1,15,1,0,0,0,2,17,1,0,0,0,2,19,1,0,0,
        0,2,21,1,0,0,0,2,23,1,0,0,0,2,25,1,0,0,0,3,27,1,0,0,0,5,35,1,0,0,
        0,7,40,1,0,0,0,9,44,1,0,0,0,11,51,1,0,0,0,13,55,1,0,0,0,15,60,1,
        0,0,0,17,64,1,0,0,0,19,66,1,0,0,0,21,68,1,0,0,0,23,70,1,0,0,0,25,
        75,1,0,0,0,27,28,5,123,0,0,28,29,5,123,0,0,29,30,1,0,0,0,30,31,6,
        0,0,0,31,4,1,0,0,0,32,36,8,0,0,0,33,34,5,123,0,0,34,36,8,1,0,0,35,
        32,1,0,0,0,35,33,1,0,0,0,36,37,1,0,0,0,37,35,1,0,0,0,37,38,1,0,0,
        0,38,6,1,0,0,0,39,41,7,2,0,0,40,39,1,0,0,0,41,42,1,0,0,0,42,40,1,
        0,0,0,42,43,1,0,0,0,43,8,1,0,0,0,44,48,7,3,0,0,45,47,7,4,0,0,46,
        45,1,0,0,0,47,50,1,0,0,0,48,46,1,0,0,0,48,49,1,0,0,0,49,10,1,0,0,
        0,50,48,1,0,0,0,51,52,5,58,0,0,52,53,1,0,0,0,53,54,6,4,1,0,54,12,
        1,0,0,0,55,56,5,125,0,0,56,57,5,125,0,0,57,58,1,0,0,0,58,59,6,5,
        2,0,59,14,1,0,0,0,60,61,3,7,2,0,61,62,1,0,0,0,62,63,6,6,3,0,63,16,
        1,0,0,0,64,65,5,109,0,0,65,18,1,0,0,0,66,67,5,111,0,0,67,20,1,0,
        0,0,68,69,5,112,0,0,69,22,1,0,0,0,70,71,3,13,5,0,71,72,1,0,0,0,72,
        73,6,10,4,0,73,74,6,10,2,0,74,24,1,0,0,0,75,76,3,7,2,0,76,77,1,0,
        0,0,77,78,6,11,3,0,78,26,1,0,0,0,7,0,1,2,35,37,42,48,5,5,1,0,2,2,
        0,4,0,0,6,0,0,7,6,0
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
    SPEC_MANY = 8
    SPEC_OPTIONAL = 9
    SPEC_PATH = 10
    SPECS_S = 11

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE", "INSIDE", "SPECS" ]

    literalNames = [ "<INVALID>",
            "'{{'", "':'", "'}}'", "'m'", "'o'", "'p'" ]

    symbolicNames = [ "<INVALID>",
            "OPEN", "WORD", "SPACE", "FIELD_NAME", "SPEC_OPEN", "CLOSE", 
            "INSIDE_S", "SPEC_MANY", "SPEC_OPTIONAL", "SPEC_PATH", "SPECS_S" ]

    ruleNames = [ "OPEN", "WORD", "SPACE", "FIELD_NAME", "SPEC_OPEN", "CLOSE", 
                  "INSIDE_S", "SPEC_MANY", "SPEC_OPTIONAL", "SPEC_PATH", 
                  "SPECS_CLOSE", "SPECS_S" ]

    grammarFileName = "CommandTemplateLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


