'''
Core allowed statements
-----------------------
var vName vValue      # create variable with name vName and value vValue
var vName calculation # create variable with name vName and value as result from calculation
vName Calculation     # put result of calculation in variable vName
if vName lineNr       # if value of vName>0 goto lineNr

label lName           # create reference to current lineNr with name lName
goto lName / lineNr   # go to lineNr (with name lName)

sub lName             # create reference to current lineNr with name lName
gosub lName / lineNr  # go to lineNr with name lName, but put current line on callStack
return                # return to last linenr put on callStack

Remarks:
- All items in a statement should be separated by space(s)
- Calculations may not have spaces
- Calculations may contain all python3 math functions e.g. 'a 3+math.sin(math.pi/2)'
- Several statements on one line can be seperated with ; but not encouraged and mainly used for internally rewriting macro's
- String values should be enclosed between double quotes "
- Use f"abc {var1:abc} def" to format string with vars

Macro statements        (will be replaced by preprocessor with core statements)
----------------------
if cond {             # if not(cond) goto linenr
}                     # pass

for i 4 10 2 {        # var i 4  
}                     # i i+2   ; if i<10 goto linenr

while cond {          # if not(cond) goto linenr   
}                     # if cond goto linenr

Remarks:
- Macro's can be nested
- Variable in for-loop does not have to be defined beforehand

Internal functions
----------------------
sleep 2               # int or float nr of seconds
print                 # print tp console


Allowed formatting
----------------------
- single equal signs will be replaced by single spaces, this makes the following formatting possible
    var b = 1
    b = 2
- triple points and : will be replaced by single space, this makes the following formatting possible
    for i = 4 ... 10 : 2 {        
'''

import os
import time
import re
import math

# GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)

# FOLLOWING VARS, SYSTEM FUNCTIONS can be called from scipt
systemVars={'scriptpath':scriptpath, 'pi':math.pi, 'version':'09.02.21'}
systemDefs={'sleep':(time.sleep,[[int,float],]),
            'print':(print,[[bool,int,float,str],]),
            }
callStack=[]

def millis():
    return time.time()*1000

#####################################################
# ERROR TRACING
#####################################################
errorStack=[]
def logError(lineNr,scriptline,token,errMsg,indent=0):
    errLine=f"{lineNr+1:4} > '{scriptline.strip()}'\n"
    if token: errLine+=f"  Token: '{token}'\n"
    errLine+=f"  {errMsg}"
    errorStack.append (errLine)  

def printErrorStack():
    if errorStack:
        print ("Errors found:")
        for error in errorStack:
            print (error)
quitOnError=True # needed for debugging error messages

#####################################################
# FILE IO
#####################################################
def scriptLoad(scriptpath):
    with open(scriptpath, "r") as reader: # open file
        scriptlines=reader.readlines()                  # read all lines
    #read script (can be edited by user)
    return scriptlines

#####################################################
# CODE REWRITING
#####################################################
def replaceOutsideQuotes(strLine,replaceDict):
    parts=strLine.split('"')
    for pNr in range(0,len(parts),2): # ony part #0,2,4... are outside of quotes
        for oldSeq in replaceDict:
            newSeq=replaceDict[oldSeq]
            parts[pNr]=parts[pNr].replace(oldSeq,newSeq)
    #print (parts)
    strLine='"'.join(parts)
    return strLine

def findGroupEnd(scriptlines,fromLineNr):
    level=1
    for lineNr in range(fromLineNr+1,len(scriptlines)):
        scriptline = scriptlines[lineNr]
        statements = scriptline2statements(scriptline)
        if statements:
            for statement in statements:
                tokens=statement2tokens(statement)
                for token in tokens[1:-1]:
                    if token=="{" or token=="}": return -1
                if tokens[0]=="}": level-=1
                if tokens[-1]=="{": level+=1
                if level==0: return lineNr

    #if nothing found we return -1 so rewrite macros can append error to stack
    return -1

def removeRemarks(scriptlines):
    for lnr,scriptline in enumerate(scriptlines):
        # remove remarks
        if len(scriptline.strip())==0:       #do nothing if empty    
            #print (f"{lnr} empty")
            scriptlines[lnr]="\n"
        elif scriptline.strip()[0]=='#': 
            scriptlines[lnr]="\n"
            #print (f"{lnr} comment")
        else:    
            #count nr quotes
            if scriptline.count('"')%2==1:     # if odd number of quotes, the line is malformed
                logError(lnr,scriptline,None,"SyntaxError: String not closed on line.")
                return False
            #remove remark 
            PATTERN_REMARKS = re.compile(r'''((?:[^#"']|"[^"]*"|'[^']*')+)''')    
            scriptline= PATTERN_REMARKS.split(scriptline)[1::2][0]  
            scriptlines[lnr]=scriptline

    return scriptlines

def rewriteSyntax(scriptlines):    
    for lineNr,scriptline in enumerate(scriptlines):
        #replacements are now not specific for commands, but can be made by checking against first token
        #  cmd=statement2tokens(scriptline)[0]
        replaceDict={'  ' :' ',
                    ' = ':' ', 
                    ' : ': ' ',
                    '...':' '}
        scriptlines[lineNr]=replaceOutsideQuotes(scriptline,replaceDict)
    return scriptlines

def rewriteMacros(scriptlines):
    # ; not accounted for
    for lineNr,scriptline in enumerate(scriptlines):
        tokens=statement2tokens(scriptline)
        scriptline=scriptline.strip() # for printing errorStack without \n
        
        if tokens:
            #print (f"Scriptline: {lineNr}> {scriptline} {len(tokens)} {tokens}")        
            cmd=tokens[0]

            if cmd=="if" and tokens[-1]=="{":
                if len(tokens)!=3:  
                    logError(lineNr,scriptline,None,f"SyntaxError: If statement has {('more','less')[len(tokens)<3]} tokens than expected.")
                    return False          
                else:
                    jumpNr=findGroupEnd(scriptlines,lineNr)                                         # find closing bracket
                    fndClosingBracket = (jumpNr>=0)
                    if fndClosingBracket:                                                           # if } found
                        cond=tokens[1]
                        scriptlines[lineNr]=f"if not({cond}) {jumpNr}"#                               # {scriptlines[lineNr]}"
                        scriptlines[jumpNr]=f""##                                                     # {scriptlines[jumpNr]}"            
                    else:   
                        logError(lineNr,scriptline,None,f"SyntaxError: If statement is missing closing bracket {'}'}.")
                        return False            
            if cmd=="while":
                if tokens[-1]!="{" or len(tokens)!=3:  
                    logError(lineNr,scriptline,None,f"SyntaxError: While statement has {('more','less')[len(tokens)<3]} tokens than expected.")
                    return False          
                else:
                    jumpNr=findGroupEnd(scriptlines,lineNr)                                         # find closing bracket
                    fndClosingBracket = (jumpNr>=0)
                    if fndClosingBracket:                                                           # if } found
                        cond=tokens[1]
                        scriptlines[lineNr]=f"if not({cond}) {jumpNr}"#                               # {scriptlines[lineNr]}"
                        scriptlines[jumpNr]=f"if {cond} {lineNr}"#                                    # {scriptlines[jumpNr]}"
                    else:                                                                           # if } not found
                        logError(lineNr,scriptline,None,f"SyntaxError: While statement is missing closing bracket {'}'}.")
                        return False            
            if cmd=="for":
                if tokens[-1]!="{" or (len(tokens)!=5 and len(tokens)!=6):  
                    logError(lineNr,scriptline,None,f"SyntaxError: For statement has {('more','less')[len(tokens)<5]} tokens than expected.")
                    return False          
                else:
                    tkVar  = tokens[1]
                    tkFrom = tokens[2]
                    tkTo   = tokens[3]
                    tkStep = tokens[4] if len(tokens)==6 else 1
                    jumpNr=findGroupEnd(scriptlines,lineNr)                                         # find closing bracket
                    fndClosingBracket = (jumpNr>=0)
                    if fndClosingBracket:                                                           # if } found
                        scriptlines[lineNr]=f"var {tkVar} {tkFrom}"#                                  # {scriptlines[lineNr]}"
                        if int(tkStep)>0:
                            scriptlines[jumpNr]=f"{tkVar} {tkVar}+{tkStep} ; if {tkVar}<{tkTo} {lineNr}"#  # {scriptlines[jumpNr]}"
                        else:    
                            scriptlines[jumpNr]=f"{tkVar} {tkVar}+{tkStep} ; if {tkVar}>{tkTo} {lineNr}"#  # {scriptlines[jumpNr]}"
                    else:                                                                           # if } not found
                        logError(lineNr,scriptline,None,f"SyntaxError: For statement is missing closing bracket {'}'}.")
                        return False  
    
    return scriptlines


#####################################################
# CODE EXTRACTION
#####################################################

def multiSplit(strText,delimiters):
    regular_exp = '|'.join(map(re.escape, delimiters))
    return re.split(regular_exp, strText) 

#https://stackoverflow.com/questions/2785755/how-to-split-but-ignore-separators-in-quoted-strings-in-python
def statement2tokens(scriptline):
    # remove remarks
    scriptline=scriptline.strip()               
    if len(scriptline)>0:
        PATTERN_SPACES = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        tokens= PATTERN_SPACES.split(scriptline)[1::2]
        return tokens
    else:
        return None

def scriptline2statements(scriptline):
    # remove remarks
    if len(scriptline.strip())==0: return None
    if scriptline.strip()[0]=='#': return None
    if len(scriptline)>0:
        PATTERN_SPACES = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
        tokens= PATTERN_SPACES.split(scriptline)[1::2]
        return tokens
    else:
        return None

def extractLabels(scriptlines,varis):
    # create list of labels
    lineNr=0
    while lineNr<len(scriptlines):                  
        tokens=statement2tokens(scriptlines[lineNr])
        if tokens:
            cmd=tokens[0]
            nrArgs=len(tokens)-1
            if (cmd=="label" or cmd=="sub")  and nrArgs==1: 
                labelName =tokens[1]
                labelValue=lineNr
                varis[labelName]=labelValue
        lineNr+=1 
    return varis

#####################################################
# CODE EVALUATION
#####################################################

'''
def tokenIsString(token):
    if not token.count('"')==2: return False
    return ( (token[0]=='"') and (token[-1]=='"') )
def strIsNumber(strEval):
    return strEval.replace('.','0').isdigit()
'''
def evalArgument(varis,calcToken,linenr):
    try:
        return eval(calcToken,None,varis)
    except Exception as e:
        #print (f"Error evalStrArgument: {calcToken} is not a valid calculation.")   
        #print (f"       {e}")
        return ValueError(f"{e}")

def evalStatement(tokens,varis,linenr):
    args=[]             
    cmd=tokens[0]                                
    for tnr,token in enumerate(tokens[1:]):                            
        if ((cmd!="var" or tnr>0) and               # if cmd='var' do not eval 1st arg (name), but do eval 2nd arg (initial value of var) 
             cmd!="label"):                         # if cmd='label' first argument is name of label and should not be evaluated
            args.append(evalArgument(varis,token,linenr))                  
            #print (f"  {tokens[tnr+1]} -> {args[-1]}")
        else: 
            args.append(token)
            #print (f"  raw {token}")
    return args

def typeToken(arg):
    #this is run by runScipt/evalStatement after it did evalArgument on all rokens
    if isinstance(arg,str): return str
    if isinstance(arg,bool): return bool
    if isinstance(arg,int): return int
    if isinstance(arg,float): return float
    return None    

def checkArgs(lineNr,statement,tokens,tAllowedTypes):
    #this is run by runScipt/evalStatement after it did evalArgument on all rokens
    #print (f"checkArgs:{tokens} {tAllowedTypes}")
    if len(tokens)!=len(tAllowedTypes): 
        logError(lineNr,statement,None,f"ArgError: {len(tokens)} tokens found, {len(tAllowedTypes)} needed.")
        return False

    for token,allowedTypeList in zip(tokens,tAllowedTypes):
        tokenType=typeToken(token)
        #print (f"{token}:{tokenType} ? {tAllowedTypes}")
        if not (tokenType in allowedTypeList):
            logError(lineNr,statement,token,f"ArgError: {token} of type {tokenType}, allowed {allowedTypeList}.")
            return False
    
    return True

def runScript(scriptpath):
    global errorStack

    # load script
    scriptlines=scriptLoad(scriptpath)
    # remove remarks
    ret=removeRemarks(scriptlines)
    if ret: scriptlines=ret
    else:
        printErrorStack()
        if quitOnError: return     
    # rewrite syntax
    ret=rewriteSyntax(scriptlines)
    if ret: scriptlines=ret
    else:
        printErrorStack()
        if quitOnError: return     
    # rewrite macros to core statements, returns false if error with brackets
    ret=rewriteMacros(scriptlines)
    if ret: scriptlines=ret
    else:
        printErrorStack()
        if quitOnError: return     
    # make room for variables and fill with systemvars
    varis=systemVars.copy()
    # convert labels to linenumbers and store as variables
    varis=extractLabels(scriptlines,varis)
    # process script
    level=0
    linenr=0
    while linenr<len(scriptlines):                                  # follow lines and control statements until last line
        statements=scriptline2statements(scriptlines[linenr])
        #tokens=scriptline2tokens(scriptlines[linenr])
        if statements:
            for statement in statements:
                statement=statement.strip()
                tokens=statement2tokens(statement)
                if tokens:
                    #print (f"{linenr+1:02}> {statement.strip()}")
                    # extract command
                    cmd=tokens[0]                                       
                    # convert tokens to evaluated arguments
                    args=evalStatement(tokens,varis,linenr)
                    nrArgs=len(args)
                    # handle evaluation errors
                    errors=0
                    for argNr,arg in enumerate(args):
                        if arg.__class__.__name__=='ValueError':
                            logError(linenr,statement,tokens[argNr-1],f"EvalError: {arg.args[0].capitalize()}")
                            linenr=len(scriptlines)
                    # handle command
                    if not errors:
                        if cmd=="var"      and checkArgs(linenr,statement,args,[[str],[str,float,bool,int],]):
                            varis[args[0]]=args[1]                             # add variable to variable list
                            #print (f"cmd==var:{args}")                        
                            #print (f"  varis:{varis}")                        
                        elif cmd in varis  and checkArgs(linenr,statement,args,[[str,float,int],]) : 
                            varis[cmd]=args[0]                                  # change value of variable 
                            #print (f"  set var '{cmd}' {args[0]} -> {varis}")
                        elif cmd=="label"  and checkArgs(linenr,statement,args,[[str],]) : 
                            pass                                                # already handled in extractLabels
                        elif cmd=="sub"    and checkArgs(linenr,statement,args,[[str],]) : 
                            pass                                                # already handled in extractLabels
                        elif cmd=="goto"   and checkArgs(linenr,statement,args,[[int],]):                           
                            linenr=args[0]                                      # change linenr to that associated with label
                        elif cmd=="gosub"  and checkArgs(linenr,statement,args,[[int],]):                           
                            callStack.append(linenr)
                            linenr=args[0]                                      # change linenr to that associated with label
                        elif cmd=="return" and checkArgs(linenr,statement,args,[]):                           
                            linenr=callStack.pop()
                        elif cmd=="if"     and checkArgs(linenr,statement,args,[[bool],[int]]):   
                            #print (f"if {args[0]} {args[1]}")                
                            if args[0]: linenr=args[1]                          # set linenr
                        #elif cmd=="print" and checkArgs(args,[[bool,int,float,str],]):   
                        #    print (args[0])                                     # print message
                        elif cmd=="exit"   and checkArgs(linenr,statement,args,[]):
                            linenr=len(scriptlines)                             # print message
                        elif cmd in systemDefs:                            
                            functionH=systemDefs[cmd][0]
                            allowedTypes=systemDefs[cmd][1]
                            #print (f"system:{cmd} vs {functionH} {allowedTypes} ")
                            if checkArgs(linenr,statement,args,allowedTypes): 
                                functionH(*args)                                # call external function
                        else:
                            logError(linenr,statement,arg,f"CmdError: Command '{cmd}'not valid.")
                            linenr=len(scriptlines)
                # if tokens statemen
            # for statement in statements
        # if statements           
        linenr+=1
    # while linenr<len(scriptlines)  
    printErrorStack()

if __name__=="__main__":
    def test():
        # TEST tokens, strings and comment spltting
        print (statement2tokens('print " dit is #in-string-comment en # dit ook " maar # dit is echt "een comment"'))

        labels={}
        varis={'a':3, 'b':"'tst'", 'c':5, 't':True, 'f':False}
        # TEST multiSplit
        print ("\nTest multisplit")
        print (multiSplit('f"a+b{c}d"',("+", "==", "!=","{","}",":",'"')))
        print (multiSplit('f"abc{b:23}"',("+", "==", "!=","{","}",":",'"')))

        # TEST evalArgument to distinguis text from numeric arguments
        print ("\nTest evalArgument on String(variable)s")
        print ('abc+def'      == evalArgument(labels,varis,'"abc+def"') )
        print ("'tst''tst'"   == evalArgument(labels,varis,"b+b") )
        print ("abc003"       == evalArgument(labels,varis,'f"abc{a:03}"') )

        #''' TEST evalNumArgument
        print ("\nTest evalArgument on numeric(variable)s")
        ret=  8==evalArgument(labels,varis,"a+c")
        print (ret)
        ret= 16==evalArgument(labels,varis,"a+(c+a)+c")
        print (ret)
        ret= True==evalArgument(labels,varis,"c==5")
        print (ret)
        ret= True==evalArgument(labels,varis,"(c==5)")
        print (ret)
        ret= False==evalArgument(labels,varis,"not(c==5)")
        print (ret)
        ret= True==evalArgument(labels,varis,"(c>3)")
        print (ret)
        ret= False==evalArgument(labels,varis,"not(c>3)")
        print (ret)
        ret= True==evalArgument(labels,varis,"t")
        print (ret)
        ret= False==evalArgument(labels,varis,"t==False")
        print (ret)
        ret= False==evalArgument(labels,varis,"f==t")
        print (ret)

    #test()
    #runScript(os.path.join(scriptdir,"testAll.sng"))
    runScript(os.path.join(scriptdir,"debug.sng"))
