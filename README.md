PyInterpreter
=============

A simple script interpreter written in python. All tokens should be seperated by spaces, except for tokens within expressions (calculations).
String values should be enclosed between double quotes (") and can be formatted with python3 f-formatting syntax, e.g. `f"The number is {nr}."`
All python3 math functions are available for expressions e.g. `a = 3+math.sin(math.pi/2)`. Expressions and strings can be enclosed in parentheses '(', ')'

The script resembles javascript a bit, for example:
~~~
# This is a comment

var firstName = "John"                                
var lastName  = "Adams"                               
print (f"My name is {firstName} {lastName}")          

print ("Watch me count even number between 0 and 10:")  
for x = 0 ... 10 : 2 {                               
  gosub showNumber                                   
}

exit                                                 

sub showNumber                                        
  print (f"  {x}")
return                                         
~~~

It is possible to create functions, however passing variables is not (yet) implemented.

---  
  
  
Core allowed statements
-----------------------
The script language only consists of the following allowed statements:
Syntax                  | Description                                                             
:-----------------------|:-----------------------------------------------------------------------
\# comment              | lines starting with # are considered comments
statement # comment     | comments can also start mid sentence
.                       | .
var vName value/calc    | create variable with name vName and initialize with literal (int/float/string) or expression 
vName calculation       | assignement literal or expression to variable vName  
if condition lineNr     | if condition (literal/variable/expression) is true jump to line lineNr  
.                       | .
label lName             | make an alias lName for current line number                     
goto lName / lineNr     | go to line number associated with alias lName
.                       | .
sub lName               | same as label                     
gosub lName / lineNr    | same as goto, but put current line number on callStack  
return                  | set line number to last added line number put on callStack  
.                       | .
exit                    | stop interpreter  
  
Several statements on one line can be seperated with ';' but this is not encouraged and mainly used for internally rewriting macro's

---


Macro statements  
----------------
Also multiline If/For/While statements are possible, because they are rewritten to core statements  

**If**
Line | Macro statement        | Core statement
:----|:-----------------------|:-----------------------------------------------------------------------
1    |`if cond {`             | `if not(cond) goto 3`
2    |`  ...`                 | `  ...`
3    |`}`                     | ``
Variable in for-loop does not have to be defined beforehand

**For**
Line | Macro statement        | Core statement
:----|:-----------------------|:-----------------------------------------------------------------------
1    | `for i 4 10 2 {`       | `var i 4`
2    | `  ...`                | `  ...`
3    | `}`                    | `i i+2 ; if i<10 goto 1`

**While**
Line | Macro statement        | Core statement
:----|:-----------------------|:-----------------------------------------------------------------------
1    | `while cond { `        | `if not(cond) goto 3 `
2    | `  ...        `        | `  ...               `
3    | `}            `        | `if cond goto 1      `

**Remarks:**
- Macro's can be nested

---

Internal variables and functions
--------------------------------
It is possible to define and call upon internal functions

Syntax                  | Description
:-----------------------|:-----------------------------------------------------------------------
sleep 2                 | int or float nr of seconds
print                   | print to console
print version           | prints current script version
---

Allowed formatting
------------------
Some characters are ignored and can be used to make your script more readable:
- single equal signs 
~~~
    var b = 1
    b = 2
~~~
- triple points and ':'
~~~
    for i = 4 ... 10 : 2 {        
~~~
 - calculations and strings can be enclosed in parentheses '(', ')'.
~~~
  var a = (1+2*3)
  print (a)
~~~
   
