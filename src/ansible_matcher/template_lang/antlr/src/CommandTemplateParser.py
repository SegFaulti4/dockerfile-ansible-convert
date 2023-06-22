# Generated from /home/popovms/course/src/ansible_matcher/antlr/grammar/CommandTemplateParser.g4 by ANTLR 4.12.0
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
        4,1,14,71,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,0,5,
        0,14,8,0,10,0,12,0,17,9,0,1,0,3,0,20,8,0,1,1,1,1,1,1,1,1,5,1,26,
        8,1,10,1,12,1,29,9,1,1,1,3,1,32,8,1,1,1,1,1,1,1,1,1,5,1,38,8,1,10,
        1,12,1,41,9,1,1,1,3,1,44,8,1,3,1,46,8,1,1,2,1,2,1,3,1,3,1,3,1,3,
        3,3,54,8,3,1,3,3,3,57,8,3,1,3,3,3,60,8,3,1,3,3,3,63,8,3,3,3,65,8,
        3,1,3,1,3,1,4,1,4,1,4,0,0,5,0,2,4,6,8,0,0,77,0,10,1,0,0,0,2,45,1,
        0,0,0,4,47,1,0,0,0,6,49,1,0,0,0,8,68,1,0,0,0,10,15,3,2,1,0,11,12,
        5,3,0,0,12,14,3,2,1,0,13,11,1,0,0,0,14,17,1,0,0,0,15,13,1,0,0,0,
        15,16,1,0,0,0,16,19,1,0,0,0,17,15,1,0,0,0,18,20,3,8,4,0,19,18,1,
        0,0,0,19,20,1,0,0,0,20,1,1,0,0,0,21,27,3,4,2,0,22,23,3,6,3,0,23,
        24,3,4,2,0,24,26,1,0,0,0,25,22,1,0,0,0,26,29,1,0,0,0,27,25,1,0,0,
        0,27,28,1,0,0,0,28,31,1,0,0,0,29,27,1,0,0,0,30,32,3,6,3,0,31,30,
        1,0,0,0,31,32,1,0,0,0,32,46,1,0,0,0,33,39,3,6,3,0,34,35,3,4,2,0,
        35,36,3,6,3,0,36,38,1,0,0,0,37,34,1,0,0,0,38,41,1,0,0,0,39,37,1,
        0,0,0,39,40,1,0,0,0,40,43,1,0,0,0,41,39,1,0,0,0,42,44,3,4,2,0,43,
        42,1,0,0,0,43,44,1,0,0,0,44,46,1,0,0,0,45,21,1,0,0,0,45,33,1,0,0,
        0,46,3,1,0,0,0,47,48,5,2,0,0,48,5,1,0,0,0,49,50,5,1,0,0,50,64,5,
        4,0,0,51,53,5,5,0,0,52,54,5,9,0,0,53,52,1,0,0,0,53,54,1,0,0,0,54,
        56,1,0,0,0,55,57,5,10,0,0,56,55,1,0,0,0,56,57,1,0,0,0,57,59,1,0,
        0,0,58,60,5,11,0,0,59,58,1,0,0,0,59,60,1,0,0,0,60,62,1,0,0,0,61,
        63,5,12,0,0,62,61,1,0,0,0,62,63,1,0,0,0,63,65,1,0,0,0,64,51,1,0,
        0,0,64,65,1,0,0,0,65,66,1,0,0,0,66,67,5,6,0,0,67,7,1,0,0,0,68,69,
        5,3,0,0,69,9,1,0,0,0,12,15,19,27,31,39,43,45,53,56,59,62,64
    ]

class CommandTemplateParser ( Parser ):

    grammarFileName = "CommandTemplateParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'<<'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "':'", "'>>'", "<INVALID>", "<INVALID>", "'m'", "'n'", 
                     "'o'", "'p'" ]

    symbolicNames = [ "<INVALID>", "OPEN", "WORD", "SPACE", "FIELD_NAME", 
                      "SPEC_OPEN", "CLOSE", "INSIDE_S", "INSIDE_ANY", "SPEC_MANY", 
                      "SPEC_NO_WILDCARDS", "SPEC_OPTIONAL", "SPEC_PATH", 
                      "SPECS_S", "SPECS_ANY" ]

    RULE_command_template = 0
    RULE_template_part = 1
    RULE_template_word = 2
    RULE_template_field = 3
    RULE_template_postfix = 4

    ruleNames =  [ "command_template", "template_part", "template_word", 
                   "template_field", "template_postfix" ]

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
    SPEC_NO_WILDCARDS=10
    SPEC_OPTIONAL=11
    SPEC_PATH=12
    SPECS_S=13
    SPECS_ANY=14

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.12.0")
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

        def template_postfix(self):
            return self.getTypedRuleContext(CommandTemplateParser.Template_postfixContext,0)


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
            self.state = 10
            self.template_part()
            self.state = 15
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 11
                    self.match(CommandTemplateParser.SPACE)
                    self.state = 12
                    self.template_part() 
                self.state = 17
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 19
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 18
                self.template_postfix()


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
            self.state = 45
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [2]:
                self.enterOuterAlt(localctx, 1)
                self.state = 21
                self.template_word()
                self.state = 27
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 22
                        self.template_field()
                        self.state = 23
                        self.template_word() 
                    self.state = 29
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

                self.state = 31
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==1:
                    self.state = 30
                    self.template_field()


                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 33
                self.template_field()
                self.state = 39
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 34
                        self.template_word()
                        self.state = 35
                        self.template_field() 
                    self.state = 41
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==2:
                    self.state = 42
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
            self.state = 47
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

        def SPEC_NO_WILDCARDS(self):
            return self.getToken(CommandTemplateParser.SPEC_NO_WILDCARDS, 0)

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
            self.state = 49
            self.match(CommandTemplateParser.OPEN)
            self.state = 50
            self.match(CommandTemplateParser.FIELD_NAME)
            self.state = 64
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 51
                self.match(CommandTemplateParser.SPEC_OPEN)
                self.state = 53
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==9:
                    self.state = 52
                    self.match(CommandTemplateParser.SPEC_MANY)


                self.state = 56
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==10:
                    self.state = 55
                    self.match(CommandTemplateParser.SPEC_NO_WILDCARDS)


                self.state = 59
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==11:
                    self.state = 58
                    self.match(CommandTemplateParser.SPEC_OPTIONAL)


                self.state = 62
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 61
                    self.match(CommandTemplateParser.SPEC_PATH)




            self.state = 66
            self.match(CommandTemplateParser.CLOSE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Template_postfixContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SPACE(self):
            return self.getToken(CommandTemplateParser.SPACE, 0)

        def getRuleIndex(self):
            return CommandTemplateParser.RULE_template_postfix

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTemplate_postfix" ):
                listener.enterTemplate_postfix(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTemplate_postfix" ):
                listener.exitTemplate_postfix(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTemplate_postfix" ):
                return visitor.visitTemplate_postfix(self)
            else:
                return visitor.visitChildren(self)




    def template_postfix(self):

        localctx = CommandTemplateParser.Template_postfixContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_template_postfix)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(CommandTemplateParser.SPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





