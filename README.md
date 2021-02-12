PyInterpreter
=============

A simple script interpreter written in python. All tokens must be seperated by spaces, except for tokens within expressions (calculations).
String values should be enclosed between double quotes (") and can be formatted with python3 f-formatting syntax, e.g. `f"The number is {nr}."`
All python3 math functions are available for expressions e.g. `a = 3+math.sin(math.pi/2)`. Expressions and strings can be enclosed in parentheses '(', ')'

The script resembles javascript a bit, for example:
~~~
# This is a comment

print ("Hello World!")

var firstName = "John"
var lastName = "Smith"
print (f"\nMy name is {firstName} {lastName}")

print ("\nWatch me count even numbers between 0 and 10:")
for x = 0 ... 10 : 2 {
  gosub showNumber
}

sub showNumber
  print (f"  {x}")
return                                   
~~~

It is possible to create functions, however passing variables is not (yet) implemented.

---

Usage
-----
1) Copy PyInterpreter.py to your project
<br/>
2) Add to your main projectfile
~~~
    Import PyInterpreter
~~~

3) If you want to add function use addSystemFunction e.g.
```PyInterpreter.addSystemFunction('sleep',time.sleep,[(int,float),])```<br/>
First argument is call name, second is python function, this is list of allowed types for each argument the function takes.

4) If you want to add variables use addSystemVar e.g.
```PyInterpreter.addSystemVar('pi', math,pi)```<br/>

5) Run script with loadScript and runScript() e.g.
```PyInterpreter.loadScript("myscript.pyi")```
```PyInterpreter.runScript()```
or
```PyInterpreter.runScript("myscript.pyi")```

6) After loading script, the script can be rerun with runScript(). 
System variables can be changed with modSystemVar. e.g.
```PyInterpreter.modSystemVar('pi', 3.2)```
```PyInterpreter.runScript()```

---  
  
  
Core allowed statements
-----------------------
The script language only consists of the following allowed statements:
Syntax                  | Example        | Description                                                             
:-----------------------|:---------------|:-----------------------------------------------------------------------
\# comment              | `# comment`    | lines starting with # are considered comments
statement # comment     | `a 1 # comment`| comments can also start mid sentence
.                       | .
var vName value/calc    | `var a 1`      | create variable with name vName and initialize <br/> with literal (int/float/string) or expression 
vName calculation       | `var b 1+a`    | assignement of literal or expression to variable vName  
if condition lineNr     | `if a 7`       | if condition (literal/variable/expression) is true jump to line lineNr  
.                       | .
label lName             | `label part2`  | make an alias lName for current line number                     
goto lName / lineNr     | `goto part2`   | go to line number associated with alias lName
.                       | .
sub lName               | `sub myfunc1`  | same as label                     
gosub lName / lineNr    | `gosub myfunc1`| same as goto, but put current line number on callStack  
return                  | `return`       | set line number to last added line number put on callStack  
.                       | .
exit                    | `exit`         | stop interpreter  
  
Several statements on one line can be seperated with ';' but this is not encouraged and mainly used for internally rewriting macro's

---


Macro statements  
----------------
Also multiline If/For/While statements are possible, because they are rewritten to core statements.
All multiline macro statements can be nested.

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
- single equal signs '=' e.g. var assignement:
~~~
    var b = 1
    b = 2
~~~
- triple points '...' and colon ':' e.g. for statement:
~~~
    for i = 4 ... 10 : 2 {        
~~~
 - calculations and strings can be enclosed in parentheses '(', ')'.
~~~
    var a = (1+2*3)
    print (a)
~~~
   
