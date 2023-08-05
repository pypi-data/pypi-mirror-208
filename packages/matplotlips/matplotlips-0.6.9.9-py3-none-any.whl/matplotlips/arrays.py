def scg():
    ans='''
n=[]
n=input()
di={'+':'ADD','-':'SUB','*':'MUL','/':'DIV'}
while True:
    n.append(input())
    if(n[-1]=="exit"):
        n.pop(-1)
        break
j=0
for i in n:
    op=di[i[3]]
    print("MOV",i[2],",R",str(j))
    print(op,i[4],",R",str(j))
    print("MOV R",str(j),",",i[0])
    j+=1
'''
    return(ans)

def qti():
    ans = ''' 
#include<stdio.h>
#include<ctype.h>
#include<stdlib.h>
#include<string.h>
void small();
void dove(int i);
int p[5]={0,1,2,3,4},c=1,i,k,l,m,pi;
char sw[5]={'=','-','+','/','*'},j[20],a[5],b[5],ch[2];
void main()
{
printf("Enter the expression:");
scanf("%s",j);
printf("\tThe Intermediate code is:\n");
small();
}
void dove(int i)
{ 
a[0]=b[0]='\0'; 
if(!isdigit(j[i+2])&&!isdigit(j[i-2]))
{
a[0]=j[i-1];
b[0]=j[i+1];
}
if(isdigit(j[i+2])){
a[0]=j[i-1];
b[0]='t';
b[1]=j[i+2];
}
if(isdigit(j[i-2]))
{
b[0]=j[i+1];
a[0]='t';
a[1]=j[i-2];
b[1]='\0'; 
}
if(isdigit(j[i+2]) &&isdigit(j[i-2]))
{ 
a[0]='t';
b[0]='t';
a[1]=j[i-2];
b[1]=j[i+2];
sprintf(ch,"%d",c);
j[i+2]=j[i-2]=ch[0]; 
}
if(j[i]=='*')
printf("\tt%d=%s*%s\n",c,a,b);
if(j[i]=='/')
printf("\tt%d=%s/%s\n",c,a,b);
if(j[i]=='+')
printf("\tt%d=%s+%s\n",c,a,b);if(j[i]=='-')
printf("\tt%d=%s-%s\n",c,a,b);
if(j[i]=='=')
printf("\t%c=t%d",j[i-1],--c);
sprintf(ch,"%d",c);
j[i]=ch[0];
c++;
small();
}
void small()
{ 
pi=0;l=0;
for(i=0;i<strlen(j);i++)
{ 
for(m=0;m<5;m++)
if(j[i]==sw[m])
if(pi<=p[m])
{
pi=p[m];
 l=1;
 k=i;
} 
}
if(l==1)
dove(k);
else
exit(0);}





//input: a=b+c-d

'''
    return(ans)


def icg():
    ans=''' 
OPERATORS = set(['+', '-', '*', '/', '(', ')'])

PRI = {'+': 1, '-': 1, '*': 2, '/': 2}
def infix_to_postfix(formula):
    stack = []  

    output = ''

    for ch in formula:

        if ch not in OPERATORS:

            output += ch

        elif ch == '(':

            stack.append('(')

        elif ch == ')':

            while stack and stack[-1] != '(':
                output += stack.pop()

            stack.pop()  

        else:

            while stack and stack[-1] != '(' and PRI[ch] <= PRI[stack[-1]]:
                output += stack.pop()

            stack.append(ch)
           

    while stack:
        output += stack.pop()

    print(f'POSTFIX: {output}')

    return output


def infix_to_prefix(formula):
    op_stack = []

    exp_stack = []

    for ch in formula:

        if not ch in OPERATORS:

            exp_stack.append(ch)

        elif ch == '(':

            op_stack.append(ch)

        elif ch == ')':

            while op_stack[-1] != '(':
                op = op_stack.pop()

                a = exp_stack.pop()

                b = exp_stack.pop()

                exp_stack.append(op + b + a)

            op_stack.pop()  

        else:

            while op_stack and op_stack[-1] != '(' and PRI[ch] <= PRI[op_stack[-1]]:
                op = op_stack.pop()

                a = exp_stack.pop()

                b = exp_stack.pop()

                exp_stack.append(op + b + a)

            op_stack.append(ch)


    while op_stack:
        op = op_stack.pop()

        a = exp_stack.pop()

        b = exp_stack.pop()

        exp_stack.append(op + b + a)

    print(f'PREFIX: {exp_stack[-1]}')

    return exp_stack[-1]

expres = input("INPUT THE EXPRESSION: ")

pre = infix_to_prefix(expres)

pos = infix_to_postfix(expres)


Input expression: X+Y^Z/R
'''
    return(ans)


def lat():
    ans=r'''
#include<iostream>
#include<stdio.h>
#include<string.h>
#include<stdlib.h>
using namespace std;

int vars,terms,i,j,k,m,rep,cont,temp=-1;
char var[10],term[10],lead[10][10],trail[10][10];
struct grammar
{	
    int prodno;
    char lhs,rhs[20][20];
}gram[50];
void get()
{
    cout<<"\nLEADING AND TRAILING\n";
    cout<<"\nEnter the no. of variables : ";
    cin>>vars;
    cout<<"\nEnter the variables : \n";
    for(i=0;i<vars;i++)
    {
        cin>>gram[i].lhs;
        var[i]=gram[i].lhs;
    }
    cout<<"\nEnter the no. of terminals : ";
    cin>>terms;
    cout<<"\nEnter the terminals : ";
    for(j=0;j<terms;j++)
        cin>>term[j];
    cout<<"\nPRODUCTION DETAILS\n";
    for(i=0;i<vars;i++)
    {
        cout<<"\nEnter the no. of production of "<<gram[i].lhs<<":";
        cin>>gram[i].prodno;
        for(j=0;j<gram[i].prodno;j++)
        {
            cout<<gram[i].lhs<<"->";
            cin>>gram[i].rhs[j];
        }
    }
}
void leading()
{
    for(i=0;i<vars;i++)
    {
        for(j=0;j<gram[i].prodno;j++)
        {
            for(k=0;k<terms;k++)
            {
                if(gram[i].rhs[j][0]==term[k])
                    lead[i][k]=1;
                else
                {
                    if(gram[i].rhs[j][1]==term[k])
                        lead[i][k]=1;
                }
            }
        }
    }
    for(rep=0;rep<vars;rep++)
    {
        for(i=0;i<vars;i++)
        {
            for(j=0;j<gram[i].prodno;j++)
            {
                for(m=1;m<vars;m++)
                {
                    if(gram[i].rhs[j][0]==var[m])
                    {
                        temp=m;
                        goto out;
                    }
                }
                out:
                for(k=0;k<terms;k++)
                {
                    if(lead[temp][k]==1)
                        lead[i][k]=1;
                }
            }
        }
    }
}
void trailing()
{
    for(i=0;i<vars;i++)
    {
        for(j=0;j<gram[i].prodno;j++)
        {
            cont=0;
            while(gram[i].rhs[j][cont]!='\x0')
                cont++;
            for(k=0;k<terms;k++)
            {
                if(gram[i].rhs[j][cont-1]==term[k])
                    trail[i][k]=1;
                else
                {
                    if(gram[i].rhs[j][cont-2]==term[k])
                        trail[i][k]=1;
                }
            }
        }
    }
    for(rep=0;rep<vars;rep++)
    {
        for(i=0;i<vars;i++)
        {
            for(j=0;j<gram[i].prodno;j++)
            {
                cont=0;
                while(gram[i].rhs[j][cont]!='\x0')
                    cont++;
                for(m=1;m<vars;m++)
                {
                    if(gram[i].rhs[j][cont-1]==var[m])
                        temp=m;
                }
                for(k=0;k<terms;k++)
                {
                    if(trail[temp][k]==1)
                        trail[i][k]=1;
                }
            }
        }
    }
}
void display()
{
    for(i=0;i<vars;i++)
    {
        cout<<"\nLEADING("<<gram[i].lhs<<") = ";
        for(j=0;j<terms;j++)
        {
            if(lead[i][j]==1)
                cout<<term[j]<<",";
        }
    }
    cout<<endl;
    for(i=0;i<vars;i++)
    {
        cout<<"\nTRAILING("<<gram[i].lhs<<") = ";
        for(j=0;j<terms;j++)
        {
            if(trail[i][j]==1)
                cout<<term[j]<<",";
        }
    }
}
int main()
{

    get();
    leading();
    trailing();
    display();

}



Enter the no. of variables : 3
Enter the variables : 
E
T
F
Enter the no. of terminals : 5
Enter the terminals : (
)
+
*
id
PRODUCTION DETAILS

Enter the no. of production of E:2
E->E+T
E->T
Enter the no. of production of T:2
T->T*F
T->F
Enter the no. of production of F:2
F->(E)
F->id

'''
    return(ans)

def srp():
    ans=''' 
gram = {
	"E":["2E2","3E3","4"]
}
starting_terminal = "E"

inp = input("Enter the string \n")
inp=inp+"$"

stack = "$"
print(f'{"Stack": <15}'+"|"+f'{"Input Buffer": <15}'+"|"+f'Parsing Action')
print(f'{"-":-<50}')

while True:
	action = True
	i = 0
	while i<len(gram[starting_terminal]):
		if gram[starting_terminal][i] in stack:
			stack = stack.replace(gram[starting_terminal][i],starting_terminal)
			print(f'{stack: <15}'+"|"+f'{inp: <15}'+"|"+f'Reduce S->{gram[starting_terminal][i]}')
			i=-1
			action = False
		i+=1
	if len(inp)>1:
		stack+=inp[0]
		inp=inp[1:]
		print(f'{stack: <15}'+"|"+f'{inp: <15}'+"|"+f'Shift')
		action = False

	if inp == "$" and stack == ("$"+starting_terminal):
		print(f'{stack: <15}'+"|"+f'{inp: <15}'+"|"+f'Accepted')
		break

	if action:
		print(f'{stack: <15}'+"|"+f'{inp: <15}'+"|"+f'Rejected')
		break
	

Enter the string
32423
'''
    return(ans)

def lr0():
    ans='''
#include<iostream>
#include<conio.h>
#include<string.h>

using namespace std;

char prod[20][20],listofvar[26]="ABCDEFGHIJKLMNOPQR";
int novar=1,i=0,j=0,k=0,n=0,m=0,arr[30];
int noitem=0;

struct Grammar
{
	char lhs;
	char rhs[8];
}g[20],item[20],clos[20][10];

int isvariable(char variable)
{
	for(int i=0;i<novar;i++)
		if(g[i].lhs==variable)
			return i+1;
	return 0;
}
void findclosure(int z, char a)
{
	int n=0,i=0,j=0,k=0,l=0;
	for(i=0;i<arr[z];i++)
	{
		for(j=0;j<strlen(clos[z][i].rhs);j++)
		{
			if(clos[z][i].rhs[j]=='.' && clos[z][i].rhs[j+1]==a)
			{
				clos[noitem][n].lhs=clos[z][i].lhs;
				strcpy(clos[noitem][n].rhs,clos[z][i].rhs);
				char temp=clos[noitem][n].rhs[j];
				clos[noitem][n].rhs[j]=clos[noitem][n].rhs[j+1];
				clos[noitem][n].rhs[j+1]=temp;
				n=n+1;
			}
		}
	}
	for(i=0;i<n;i++)
	{
		for(j=0;j<strlen(clos[noitem][i].rhs);j++)
		{
			if(clos[noitem][i].rhs[j]=='.' && isvariable(clos[noitem][i].rhs[j+1])>0)
			{
				for(k=0;k<novar;k++)
				{
					if(clos[noitem][i].rhs[j+1]==clos[0][k].lhs)
					{
						for(l=0;l<n;l++)
							if(clos[noitem][l].lhs==clos[0][k].lhs && strcmp(clos[noitem][l].rhs,clos[0][k].rhs)==0)
								break;
						if(l==n)
						{
							clos[noitem][n].lhs=clos[0][k].lhs;
						strcpy(clos[noitem][n].rhs,clos[0][k].rhs);
							n=n+1;
						}
					}
				}
			}
		}
	}
	arr[noitem]=n;
	int flag=0;
	for(i=0;i<noitem;i++)
	{
		if(arr[i]==n)
		{
			for(j=0;j<arr[i];j++)
			{
				int c=0;
				for(k=0;k<arr[i];k++)
					if(clos[noitem][k].lhs==clos[i][k].lhs && strcmp(clos[noitem][k].rhs,clos[i][k].rhs)==0)
						c=c+1;
				if(c==arr[i])
				{
					flag=1;
					goto exit;
				}
			}
		}
	}
	exit:;
	if(flag==0)
		arr[noitem++]=n;
}

int main()
{
	cout<<"ENTER THE PRODUCTIONS OF THE GRAMMAR(0 TO END) :\n";
	do
	{
		cin>>prod[i++];
	}while(strcmp(prod[i-1],"0")!=0);
	for(n=0;n<i-1;n++)
	{
		m=0;
		j=novar;
		g[novar++].lhs=prod[n][0];
		for(k=3;k<strlen(prod[n]);k++)
		{
			if(prod[n][k] != '|')
			g[j].rhs[m++]=prod[n][k];
			if(prod[n][k]=='|')
			{
				g[j].rhs[m]='\0';
				m=0;
				j=novar;
				g[novar++].lhs=prod[n][0];
			}
		}
	}
	for(i=0;i<26;i++)
		if(!isvariable(listofvar[i]))
			break;
	g[0].lhs=listofvar[i];
	char temp[2]={g[1].lhs,'\0'};
	strcat(g[0].rhs,temp);
	cout<<"\n\n augumented grammar \n";
	for(i=0;i<novar;i++)
		cout<<endl<<g[i].lhs<<"->"<<g[i].rhs<<" ";

	for(i=0;i<novar;i++)
	{
		clos[noitem][i].lhs=g[i].lhs;
		strcpy(clos[noitem][i].rhs,g[i].rhs);
		if(strcmp(clos[noitem][i].rhs,"ε")==0)
			strcpy(clos[noitem][i].rhs,".");
		else
		{
			for(int j=strlen(clos[noitem][i].rhs)+1;j>=0;j--)
				clos[noitem][i].rhs[j]=clos[noitem][i].rhs[j-1];
			clos[noitem][i].rhs[0]='.';
		}
	}
	arr[noitem++]=novar;
	for(int z=0;z<noitem;z++)
	{
		char list[10];
		int l=0;
		for(j=0;j<arr[z];j++)
		{
			for(k=0;k<strlen(clos[z][j].rhs)-1;k++)
			{
				if(clos[z][j].rhs[k]=='.')
				{
					for(m=0;m<l;m++)
						if(list[m]==clos[z][j].rhs[k+1])
							break;
					if(m==l)
						list[l++]=clos[z][j].rhs[k+1];
				}
			}
		}
		for(int x=0;x<l;x++)
			findclosure(z,list[x]);
	}
	cout<<"\n THE SET OF ITEMS ARE \n\n";
	for(int z=0; z<noitem; z++)
	{
		cout<<"\n I"<<z<<"\n\n";
		for(j=0;j<arr[z];j++)
			cout<<clos[z][j].lhs<<"->"<<clos[z][j].rhs<<"\n";

	}

}



ENTER THE PRODUCTIONS OF THE GRAMMAR(0 TO END) :
E->E+T
E->T
T->T*F
T->F
F->(E)
F->i
0

'''
    return(ans)

def la():
    ans=''' 
file  = """
#include<stdio.h>
printf("Hello World!")"""
lines = file.splitlines()

keywords    = ["void", "main", "int", "float", "bool", "if", "for", "else", "while", "char", "return"]
operators   = ["=", "==", "+", "-", "*", "/", "++", "--", "+=", "-=", "!=", "||", "&&"]
punctuations= [";", "(", ")", "{", "}", "[", "]"]

def is_int(x):
    try:
        int(x)
        return True
    except:
        return False

for line in lines:
    for i in line.strip().split(" "):
        if i in keywords:
            print (i, " is a keyword")
        elif i in operators:
            print (i, " is an operator")
        elif i in punctuations:
            print (i, " is a punctuation")
        elif is_int(i):
            print (i, " is a number")
        else:
            print (i, " is an identifier")
'''
    return(ans)


def faf():
    ans=''' 
import sys
sys.setrecursionlimit(60)

def first(string):
    first_ = set()
    if string in non_terminals:
        alternatives = productions_dict[string]

        for alternative in alternatives:
            first_2 = first(alternative)
            first_ = first_ |first_2

    elif string in terminals:
        first_ = {string}

    elif string=='' or string=='@':
        first_ = {'@'}

    else:
        first_2 = first(string[0])
        if '@' in first_2:
            i = 1
            while '@' in first_2:
                first_ = first_ | (first_2 - {'@'})
                if string[i:] in terminals:
                    first_ = first_ | {string[i:]}
                    break
                elif string[i:] == '':
                    first_ = first_ | {'@'}
                    break
                first_2 = first(string[i:])
                first_ = first_ | first_2 - {'@'}
                i += 1
        else:
            first_ = first_ | first_2

    return  first_


def follow(nT):
    follow_ = set()
    prods = productions_dict.items()
    if nT==starting_symbol:
        follow_ = follow_ | {'$'}
    for nt,rhs in prods:
        for alt in rhs:
            for char in alt:
                if char==nT:
                    following_str = alt[alt.index(char) + 1:]
                    if following_str=='':
                        if nt==nT:
                            continue
                        else:
                            follow_ = follow_ | follow(nt)
                    else:
                        follow_2 = first(following_str)
                        if '@' in follow_2:
                            follow_ = follow_ | follow_2-{'@'}
                            follow_ = follow_ | follow(nt)
                        else:
                            follow_ = follow_ | follow_2
    
    return follow_





no_of_terminals=int(input("Enter no. of terminals: "))

terminals = []

print("Enter the terminals :")
for _ in range(no_of_terminals):
    terminals.append(input())

no_of_non_terminals=int(input("Enter no. of non terminals: "))

non_terminals = []

print("Enter the non terminals :")
for _ in range(no_of_non_terminals):
    non_terminals.append(input())

starting_symbol = input("Enter the starting symbol: ")

no_of_productions = int(input("Enter no of productions: "))

productions = []

print("Enter the productions:")
for _ in range(no_of_productions):
    productions.append(input())



productions_dict = {}

for nT in non_terminals:
    productions_dict[nT] = []


for production in productions:
    nonterm_to_prod = production.split("->")
    alternatives = nonterm_to_prod[1].split("/")
    for alternative in alternatives:
        productions_dict[nonterm_to_prod[0]].append(alternative)


FIRST = {}
FOLLOW = {}

for non_terminal in non_terminals:
    FIRST[non_terminal] = set()

for non_terminal in non_terminals:
    FOLLOW[non_terminal] = set()



for non_terminal in non_terminals:
    FIRST[non_terminal] = FIRST[non_terminal] | first(non_terminal)


FOLLOW[starting_symbol] = FOLLOW[starting_symbol] | {'$'}
for non_terminal in non_terminals:
    FOLLOW[non_terminal] = FOLLOW[non_terminal] | follow(non_terminal)


print("{: ^20}{: ^20}{: ^20}".format('Non Terminals','First','Follow'))
for non_terminal in non_terminals:
    print("{: ^20}{: ^20}{: ^20}".format(non_terminal,str(FIRST[non_terminal]),str(FOLLOW[non_terminal])))




    Enter no. of terminals:5
    Enter terminals:
    +
    *
    a
    (   
    )
    Enter no. of non terminals: 5
    Enter non terminals:
    E
    B
    T
    Y
    F
    Enter starting symbol: E
    Enter no. of productions: 5
    Enter the productions:
    E->TB
    B->+TB/@
    T->FY
    Y->*FY/@
    F->a/(E)
'''

    return(ans)

def ntd():
    ans = ''' 
import pandas as pd

nfa = {}                                 
n = int(input("No. of states : "))            
t = int(input("No. of transitions : "))       
for i in range(n):  
    state = input("state name : ")            
    nfa[state] = {}                           
    for j in range(t):
        path = input("path : ")               
        print("Enter end state from state {} travelling through path {} : ".format(state,path))
        reaching_state = [x for x in input().split()]  
        nfa[state][path] = reaching_state     

print("\nNFA :- \n")
print(nfa)                                    
print("\nPrinting NFA table :- ")
nfa_table = pd.DataFrame(nfa)
print(nfa_table.transpose())

print("Enter final state of NFA : ")
nfa_final_state = [x for x in input().split()]      
                 
    
new_states_list = []                          
dfa = {}                                      
keys_list = list(list(nfa.keys())[0])                 
path_list = list(nfa[keys_list[0]].keys())    





dfa[keys_list[0]] = {}                        
for y in range(t):
    var = "".join(nfa[keys_list[0]][path_list[y]])   
    dfa[keys_list[0]][path_list[y]] = var            
    if var not in keys_list:                         
        new_states_list.append(var)                  
        keys_list.append(var)                        
        

 


while len(new_states_list) != 0:                     
    dfa[new_states_list[0]] = {}                     
    for _ in range(len(new_states_list[0])):
        for i in range(len(path_list)):
            temp = []                                
            for j in range(len(new_states_list[0])):
                temp += nfa[new_states_list[0][j]][path_list[i]]  
            s = ""
            s = s.join(temp)                         
            if s not in keys_list:                   
                new_states_list.append(s)            
                keys_list.append(s)                  
            dfa[new_states_list[0]][path_list[i]] = s   
        
    new_states_list.remove(new_states_list[0])       

print("\nDFA :- \n")    
print(dfa)                                           
print("\nPrinting DFA table :- ")
dfa_table = pd.DataFrame(dfa)
print(dfa_table.transpose())

dfa_states_list = list(dfa.keys())
dfa_final_states = []
for x in dfa_states_list:
    for i in x:
        if i in nfa_final_state:
            dfa_final_states.append(x)
            break
        
print("\nFinal states of the DFA are : ",dfa_final_states)       

 
# Code Ouput Example

No. of states : 4
No. of transitions : 2
state name : A
path : a
Enter end state from state A travelling through path a : 
A B
path : b
Enter end state from state A travelling through path b : 
A
state name : B
path : a
Enter end state from state B travelling through path a : 
C
path : b
Enter end state from state B travelling through path b : 
C
state name : C
path : a
Enter end state from state C travelling through path a : 
D
path : b
Enter end state from state C travelling through path b : 
D
state name : D
path : a
Enter end state from state D travelling through path a : 

path : b
Enter end state from state D travelling through path b : 


'''
    return(ans)

def pp():
    ans=''' 

def print_iter(Matched,Stack,Input,Action,verbose=True):
    if verbose==True:
        print(".".join(Matched).ljust(30)," | ",".".join(Stack).ljust(25)," | ",".".join(Input).ljust(30)," | ",Action)
#The predictive parsing algorithm
def predictive_parsing(sentence,parsingtable,terminals,start_state="S",verbose=True):      #Set verbose to false to not see the stages of the algorithm
    status = None
    match = []
    stack = [start_state,"$"]
    Inp = sentence.split(".")
    if verbose==True:
        print_iter(["Matched"],["Stack"],["Input"],"Action")
    print_iter(match,stack,Inp,"Initial",verbose)
    action=[]
    while(len(sentence)>0 and status!=False):
        top_of_input = Inp[0]
        pos = top_of_input
        if stack[0] =="$" and pos == "$" :
            print_iter(match,stack,Inp,"Accepted",verbose)
            return "Accepted"
        if stack[0] == pos:
            print_iter(match,stack,Inp,"Pop",verbose)
            match.append(stack[0])
            del(stack[0])
            del(Inp[0])
            continue
        if stack[0]=="epsilon":
            print_iter(match,stack,Inp,"Poping Epsilon",verbose)
            del(stack[0])
            continue
        try:
            production=parsingtable[stack[0]][pos]
            print_iter(match,stack,Inp,stack[0]+" -> "+production,verbose)
        except:
            return "error for "+str(stack[0])+" on "+str(pos),"Not Accepted"

        new = production.split(".")   
        stack=new+stack[1:]
    return "Not Accepted"

if __name__=="__main__":
    #Example for the working of the predictive parsing :-
    #input for the grammar : E->TE1;E1->+TE1|epsilon;T->FT1 ...
    parsingtable = {
    "E" : {"id" : "T.E1", "(" : "T.E1"},
    "E1" : {"+":"+.T.E1", ")":"epsilon", "$" : "epsilon"},
    "T" : {"id" : "F.T1", "(" : "F.T1" },
    "T1" : {"+" : "epsilon", "*" : "*.F.T1", ")" : "epsilon", "$" : "epsilon"},
    "F":{"id":"id","(":"(.E.)"}
    }
    terminals = ["id","(",")","+","*"]
    print(predictive_parsing(sentence="id.+.(.id.+.id.).$",parsingtable=parsingtable,terminals=terminals,start_state="E",verbose=True))
    #Another Example done in class:-
    print(predictive_parsing(sentence="c.c.c.c.d.d.$",parsingtable={"S" : {"c":"C.C","d":"C.C"},"C":{"c":"c.C","d":"d"}},terminals=["c,d"],start_state="S"))
'''
    return(ans)


def rtn():
    ans=''' 
rows, cols = (20, 3) 
q = [[0]*cols]*rows 

reg = '1*0*1*'
len = len(reg)
i = 0
j = 1
print( q)
while(i<len):
    if reg[i] == 'a':
        try:
            if reg[i+1] != '|' and reg[i+1] !='*':
                q[j][0] = j+1
                j += 1
        except:
            q[j][0] = j+1

    elif reg[i] == 'b':
        try:
            if reg[i+1] != '|' and reg[i+1] !='*':
                q[j][1] = j+1
                j += 1
        except:
            q[j][1] = j+1
        
    elif reg[i]=='e' and reg[i+1]!='|'and reg[i+1]!='*':
        q[j][2]=j+1
        j+=1

    elif reg[i] == 'a' and reg[i+1] == '|' and reg[i+2] =='b':
        q[j][2]=((j+1)*10)+(j+3)
        j+=1
        q[j][0]=j+1
        j+=1
        q[j][2]=j+3
        j+=1
        q[j][1]=j+1
        j+=1
        q[j][2]=j+1
        j+=1
        i=i+2

    elif reg[i]=='b'and reg[i+1]=='|' and reg[i+2]=='a':

        q[j][2]=((j+1)*10)+(j+3)
        j+=1
        q[j][1]=j+1
        j+=1
        q[j][2]=j+3
        j+=1
        q[j][0]=j+1
        j+=1
        q[j][2]=j+1
        j+=1
        i=i+2

    elif reg[i]=='a' and reg[i+1]=='*':

        q[j][2]=((j+1)*10)+(j+3)
        j+=1
        q[j][0]=j+1
        j+=1
        q[j][2]=((j+1)*10)+(j-1)
        j+=1

    elif reg[i]=='b' and reg[i+1]=='*':
        q[j][2]=((j+1)*10)+(j+3)
        j+=1
        q[j][1]=j+1
        j+=1
        q[j][2]=((j+1)*10)+(j-1)
        j+=1

    elif reg[i]==')' and reg[i+1]=='*':

        q[0][2]=((j+1)*10)+1
        q[j][2]=((j+1)*10)+1
        j+=1

    i +=1

print("Transition Function ==>")

for i in range(0,j):
    if q[i][0]!=0:

	    print(f"\n {q[i]},a --> {q[i][0]}")

    elif q[i][1]!=0:
	    print (f"\n {q[i]},b-->{q[i][1]}")

    elif q[i][2]!=0:
		
	    if q[i][2]<10:
		    print(f"\n {q[i]},e-->{q[i][2]}")
	    else:
		    print(f"\n {q[i]},e-->{q[i][2]}/10 and {q[i][2]}%10")
'''


    return(ans)

