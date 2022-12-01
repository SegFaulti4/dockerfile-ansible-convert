parser grammar CommandTemplateParser;

options { tokenVocab=CommandTemplateLexer; }

command_template
    :   template_part (SPACE template_part)*
    ;

template_part
    :   template_word (template_field template_word)* template_field?
    |   template_field (template_word template_field)* template_word?
    ;

template_word
    :   WORD
    ;

template_field
    :   OPEN FIELD_NAME ( SPEC_OPEN (SPEC_MANY)? (SPEC_OPTIONAL)? (SPEC_PATH)? )? CLOSE
    ;
