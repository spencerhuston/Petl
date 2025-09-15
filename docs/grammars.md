## Petl Grammar
```
<type> ::= 'int' | 'bool' | 'char' | 'string' | 'none'
    | <type> '->' <type>
    | '('[<type>[','<type>]*]')' '->' '('[<type>[','<type>]*]')'
    | 'list''['<type>']'
    | 'dict''['<type>','<type>']'
    | 'tuple''['<type>[','<type>]*']'
    | 'schema'
    | 'union''['<type>[','<type>]*']'
    | 'table'
    | <ident (alias)>

<literal> ::= <int> | <bool> | <char> | <string> | <none> | <range>
<int> ::= [integer]
<bool> ::= 'true' | 'false'
<char> ::= '''[character]'''
<string> ::= '"'[character]*'"'
<none> ::= 'none'
<range> ::= <int>'..'<int>

<atom> ::= <literal>
    | '('<smp>')'
    | <ident>

<param> ::= <ident>[':' <type>]
<lambda> ::= '|'[<param>[','<param>]*]'|' '->' <type> '{'<exp>'}'

<app> ::= <atom>['('[<smp>[','<smp>]*]')']

<pattern> ::= <ident>':'<type> ['if' <smp>] | <literal>['|'<literal>]* | <range> | '_'
<match> ::= 'match' <atom> '{' 'case' <pattern> '=>' <smp>[',''case' <pattern> '=>' <smp>]*'}'

<collection> ::= '['[<smp>[':'<smp>][','<smp>[':'<smp>]]*]']'

<tight> ::= <app>['|>'<app>]
    | <collection>
    | '('<smp>')'
    | '{'<exp>'}'

<arithOp> ::= '+' | '-' | '*' | '/' | '%' |
<boolOp> ::= '<' | '>' | '<=' | '>=' | '==' | 'not' | 'and' | 'or'
<op> ::= <arithOp> | <boolOp> | '++'

<utight> ::= [<op>]<tight>

<alias> ::= 'alias' <ident> '=' <type>

<schema> ::= '$''{'<ident>':'<type>[','<ident>':'<type>]*'}'

<smp> ::= <utight>[<op><utight>]
    | 'if' '('<smp>')' '{' <exp> '}' ['else' '{' <exp> '}']
    | 'for' <ident> 'in' <smp> '{' <exp> '}'
    | <collection>['++' <tight>]
    | <schema>
    | <match>
    | <lambda>
    | <alias>

<exp> ::= <smp>[';'<_exp>]
    | 'let' <ident>[':'<type>][<ident>[':'<type>]]* '=' <smp>';'<exp>
```

---
## PQL Grammar
```
<literal> ::= <int> | <bool> | <char> | <string> | <none> | <range>
<int> ::= [integer]
<bool> ::= 'true' | 'false'
<char> ::= '''[character]'''
<string> ::= '"'[character]*'"'
<none> ::= 'none'
<range> ::= <int>'..'<int>

<atom> ::= <literal>
    | '('<smp>')'
    | <ident>

<tight> ::= <atom>
    | '('<smp>')'

<arithOp> ::= '+' | '-' | '*' | '/' | '%' |
<boolOp> ::= '<' | '>' | '<=' | '>=' | '==' | 'not' | 'and' | 'or'
<op> ::= <arithOp> | <boolOp> | 'in'

<utight> ::= [<op>]<tight>

<smp> ::= <utight>[<op><utight>]
    | '('<smp>[','<smp>]')'
```