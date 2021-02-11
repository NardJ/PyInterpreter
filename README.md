# scriptInterpreter

A simple script interpreter written in python. All tokens should be seperated by spaces, except for tokens within calculations.
String values should be enclosed between double quotes (") and can be formatted with python3 f-formatting syntax, e.g. `f"The number is {nr}."`
Calculations may contain python3 math functions e.g. `a = 3+math.sin(math.pi/2)`. Calculations and strings can be enclosed in parentheses '(', ')'

The script resembles javascript a bit, for example:
~~~
# Comments are possible but uses # instead of //

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

### Core allowed statements  
The script language only consists of the following allowed statements:
Syntax                  | Description                                                             
:-----------------------|:-----------------------------------------------------------------------
\# comment               | lines starting with # are considered comments
statement # comment     | comments can also start mid sentence
.                       | .
var vName vValue        | create variable with name vName and value vValue                       
var vName calculation   | create variable with name vName and value as result from calculation  
vName Calculation       | put result of calculation in variable vName  
if vName lineNr         | if value of vName>0 goto lineNr  
.                       | .
label lName             | create reference to current lineNr with name lName                     
goto lName / lineNr     | go to lineNr (with name lName)                                         
.                       | .
sub lName               | create reference to current lineNr with name lName  
gosub lName / lineNr    | go to lineNr with name lName, but put current line on callStack  
return                  | return to last linenr put on callStack  
  
Several statements on one line can be seperated with ';' but this is not encouraged and mainly used for internally rewriting macro's

---

### Macro statements  
Also multiline If/For/While statements are possible, because they are rewritten to core statements  

**If**
~~~               
if cond {               
  ...
}
~~~               
becomes:
~~~               
if not(cond) goto linenr
  ...
[empty line]
~~~               

**For**
```{r, attr.source='.numberLines'}               
for i 4 10 2 {      
  ...                     
}                       
```  
becomes:
```{r, attr.source='.numberLines'}         
var i 4
  ...
i i+2   ; if i<10 goto linenr
```              

**While**
~~~               
while cond { 
  ...          
}           
~~~               
becomes:
~~~
if not(cond) goto linenr   
  ...
if cond goto linenr  
~~~               

**Remarks:**
- Macro's can be nested
- Variable in for-loop does not have to be defined beforehand

---

### Internal variables and functions
It is possible to define and call upon internal functions

Syntax                  | Description
:-----------------------|:-----------------------------------------------------------------------
sleep 2                 | int or float nr of seconds
print                   | print to console
print version           | prints current script version
---

### Allowed formatting
Some characters are ignored and can be used to make your script more readable:
- single equal signs 
~~~
    var b = 1
    b = 2
~~~
- triple points and : 
~~~
    for i = 4 ... 10 : 2 {        
~~~
 - calculationd and strings can be enclosed in parentheses '('
~~~
  var a = (1+2*3)
  print (a)
~~~
   
