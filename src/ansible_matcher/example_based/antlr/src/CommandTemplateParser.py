# Generated from /home/popovms/course/dockerfile-ansible-convert/src/ansible_matcher/example_based/antlr/grammar/CommandTemplateParser.g4 by ANTLR 4.11.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,13,61,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,1,0,1,0,5,0,12,8,0,
        10,0,12,0,15,9,0,1,1,1,1,1,1,1,1,5,1,21,8,1,10,1,12,1,24,9,1,1,1,
        3,1,27,8,1,1,1,1,1,1,1,1,1,5,1,33,8,1,10,1,12,1,36,9,1,1,1,3,1,39,
        8,1,3,1,41,8,1,1,2,1,2,1,3,1,3,1,3,1,3,3,3,49,8,3,1,3,3,3,52,8,3,
        1,3,3,3,55,8,3,3,3,57,8,3,1,3,1,3,1,3,0,0,4,0,2,4,6,0,0,66,0,8,1,
        0,0,0,2,40,1,0,0,0,4,42,1,0,0,0,6,44,1,0,0,0,8,13,3,2,1,0,9,10,5,
        3,0,0,10,12,3,2,1,0,11,9,1,0,0,0,12,15,1,0,0,0,13,11,1,0,0,0,13,
        14,1,0,0,0,14,1,1,0,0,0,15,13,1,0,0,0,16,22,3,4,2,0,17,18,3,6,3,
        0,18,19,3,4,2,0,19,21,1,0,0,0,20,17,1,0,0,0,21,24,1,0,0,0,22,20,
        1,0,0,0,22,23,1,0,0,0,23,26,1,0,0,0,24,22,1,0,0,0,25,27,3,6,3,0,
        26,25,1,0,0,0,26,27,1,0,0,0,27,41,1,0,0,0,28,34,3,6,3,0,29,30,3,
        4,2,0,30,31,3,6,3,0,31,33,1,0,0,0,32,29,1,0,0,0,33,36,1,0,0,0,34,
        32,1,0,0,0,34,35,1,0,0,0,35,38,1,0,0,0,36,34,1,0,0,0,37,39,3,4,2,
        0,38,37,1,0,0,0,38,39,1,0,0,0,39,41,1,0,0,0,40,16,1,0,0,0,40,28,
        1,0,0,0,41,3,1,0,0,0,42,43,5,2,0,0,43,5,1,0,0,0,44,45,5,1,0,0,45,
        56,5,4,0,0,46,48,5,5,0,0,47,49,5,9,0,0,48,47,1,0,0,0,48,49,1,0,0,
        0,49,51,1,0,0,0,50,52,5,10,0,0,51,50,1,0,0,0,51,52,1,0,0,0,52,54,
        1,0,0,0,53,55,5,11,0,0,54,53,1,0,0,0,54,55,1,0,0,0,55,57,1,0,0,0,
        56,46,1,0,0,0,56,57,1,0,0,0,57,58,1,0,0,0,58,59,5,6,0,0,59,7,1,0,
        0,0,10,13,22,26,34,38,40,48,51,54,56
    ]

class CommandTemplateParser ( Parser ):

    grammarFileName = "CommandTemplateParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{{'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "':'", "'}}'", "<INVALID>", "<INVALID>", "'m'", "'o'", 
                     "'p'" ]

    symbolicNames = [ "<INVALID>", "OPEN", "WORD", "SPACE", "FIELD_NAME", 
                      "SPEC_OPEN", "CLOSE", "INSIDE_S", "INSIDE_ANY", "SPEC_MANY", 
                      "SPEC_OPTIONAL", "SPEC_PATH", "SPECS_S", "SPECS_ANY" ]

    RULE_command_template = 0
    RULE_template_part = 1
    RULE_template_word = 2
    RULE_template_field = 3

    ruleNames =  [ "command_template", "template_part", "template_word", 
                   "template_field" ]

    EOF = Token.EOF
    OPEN=1
    WORD=2
    SPACE=3
    FIELD_NAME=4
    SPEC_OPEN=5
    CLOSE=6
    INSIDE_S=7
    INSIDE_ANY=8
    SPEC_MANY=9
    SPEC_OPTIONAL=10
    SPEC_PATH=11
    SPECS_S=12
    SPECS_ANY=13

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Command_templateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def template_part(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CommandTemplateParser.Template_partContext)
            else:
                return self.getTypedRuleContext(CommandTemplateParser.Template_partContext,i)


        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(CommandTemplateParser.SPACE)
            else:
                return self.getToken(CommandTemplateParser.SPACE, i)

        def getRuleIndex(self):
            return CommandTemplateParser.RULE_command_template

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand_template" ):
                listener.enterCommand_template(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand_template" ):
                listener.exitCommand_template(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommand_template" ):
                return visitor.visitCommand_template(self)
            else:
                return visitor.visitChildren(self)




    def command_template(self):

        localctx = CommandTemplateParser.Command_templateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_command_template)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.template_part()
            self.state = 13
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==3:
                self.state = 9
                self.match(CommandTemplateParser.SPACE)
                self.state = 10
                self.template_part()
                self.state = 15
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Template_partContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def template_word(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CommandTemplateParser.Template_wordContext)
            else:
                return self.getTypedRuleContext(CommandTemplateParser.Template_wordContext,i)


        def template_field(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CommandTemplateParser.Template_fieldContext)
            else:
                return self.getTypedRuleContext(CommandTemplateParser.Template_fieldContext,i)


        def getRuleIndex(self):
            return CommandTemplateParser.RULE_template_part

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTemplate_part" ):
                listener.enterTemplate_part(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTemplate_part" ):
                listener.exitTemplate_part(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTemplate_part" ):
                return visitor.visitTemplate_part(self)
            else:
                return visitor.visitChildren(self)




    def template_part(self):

        localctx = CommandTemplateParser.Template_partContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_template_part)
        self._la = 0 # Token type
        try:
            self.state = 40
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [2]:
                self.enterOuterAlt(localctx, 1)
                self.state = 16
                self.template_word()
                self.state = 22
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 17
                        self.template_field()
                        self.state = 18
                        self.template_word() 
                    self.state = 24
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

                self.state = 26
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==1:
                    self.state = 25
                    self.template_field()


                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 28
                self.template_field()
                self.state = 34
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 29
                        self.template_word()
                        self.state = 30
                        self.template_field() 
                    self.state = 36
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                self.state = 38
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==2:
                    self.state = 37
                    self.template_word()


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Template_wordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(CommandTemplateParser.WORD, 0)

        def getRuleIndex(self):
            return CommandTemplateParser.RULE_template_word

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTemplate_word" ):
                listener.enterTemplate_word(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTemplate_word" ):
                listener.exitTemplate_word(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTemplate_word" ):
                return visitor.visitTemplate_word(self)
            else:
                return visitor.visitChildren(self)




    def template_word(self):

        localctx = CommandTemplateParser.Template_wordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_template_word)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            self.match(CommandTemplateParser.WORD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Template_fieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPEN(self):
            return self.getToken(CommandTemplateParser.OPEN, 0)

        def FIELD_NAME(self):
            return self.getToken(CommandTemplateParser.FIELD_NAME, 0)

        def CLOSE(self):
            return self.getToken(CommandTemplateParser.CLOSE, 0)

        def SPEC_OPEN(self):
            return self.getToken(CommandTemplateParser.SPEC_OPEN, 0)

        def SPEC_MANY(self):
            return self.getToken(CommandTemplateParser.SPEC_MANY, 0)

        def SPEC_OPTIONAL(self):
            return self.getToken(CommandTemplateParser.SPEC_OPTIONAL, 0)

        def SPEC_PATH(self):
            return self.getToken(CommandTemplateParser.SPEC_PATH, 0)

        def getRuleIndex(self):
            return CommandTemplateParser.RULE_template_field

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTemplate_field" ):
                listener.enterTemplate_field(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTemplate_field" ):
                listener.exitTemplate_field(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTemplate_field" ):
                return visitor.visitTemplate_field(self)
            else:
                return visitor.visitChildren(self)




    def template_field(self):

        localctx = CommandTemplateParser.Template_fieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_template_field)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.match(CommandTemplateParser.OPEN)
            self.state = 45
            self.match(CommandTemplateParser.FIELD_NAME)
            self.state = 56
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 46
                self.match(CommandTemplateParser.SPEC_OPEN)
                self.state = 48
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==9:
                    self.state = 47
                    self.match(CommandTemplateParser.SPEC_MANY)


                self.state = 51
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==10:
                    self.state = 50
                    self.match(CommandTemplateParser.SPEC_OPTIONAL)


                self.state = 54
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==11:
                    self.state = 53
                    self.match(CommandTemplateParser.SPEC_PATH)




            self.state = 58
            self.match(CommandTemplateParser.CLOSE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





