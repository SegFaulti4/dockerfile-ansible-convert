lexer grammar CommandTemplateLexer;

OPEN            :   '<<'                        -> pushMode(INSIDE) ;
WORD            :   ( ~[ <] | '<' ~'<' )+ ;
SPACE           :   [ ]+ ;

mode INSIDE;

FIELD_NAME      :   [a-zA-Z_][a-zA-Z_0-9]* ;
SPEC_OPEN       :   ':'                         -> mode(SPECS) ;
CLOSE           :   '>>'                        -> popMode ;
INSIDE_S        :   SPACE                       -> skip ;
INSIDE_ANY      :   . ;

mode SPECS;

SPEC_MANY           : 'm' ;
SPEC_NO_WILDCARDS   : 'n' ;
SPEC_OPTIONAL       : 'o' ;
SPEC_PATH           : 'p' ;
SPECS_CLOSE         : CLOSE                     -> type(CLOSE), popMode ;
SPECS_S             : SPACE                     -> skip ;
SPECS_ANY           : . ;
