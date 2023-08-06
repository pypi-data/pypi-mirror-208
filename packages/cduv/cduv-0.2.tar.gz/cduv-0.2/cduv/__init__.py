def lexical_analyzwe_1():
    s = """file  = open("./add.c", 'r')
lines = file.readlines()

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
            print (i, " is an identifier")"""
    return s


def re_to_nfa_2():
    s = """rows, cols = (20, 3) 
q = [[0]*cols]*rows 

reg = input('Enter your regular expression : ')
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
      OUTPUT -> (a|b)*abb"""
    return s


def nfa_to_dfa3():
    s = """import pandas as pd

nfa = {}
n = int(input("No. of states : "))
t = int(input("No. of transitions : "))
for i in range(n):
    state = input("state name : ")
    nfa[state] = {}
    for j in range(t):
        path = input("path : ")
        print("Enter end state from state {} travelling through path {} : ".format(state, path))
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

#-------------------------------------------------

dfa = {}
keys_list = list(
    list(nfa.keys())[0])
path_list = list(nfa[keys_list[0]].keys())

dfa[keys_list[0]] = {}
for y in range(t):
    var = "".join(nfa[keys_list[0]][
                      path_list[y]])
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

print("\nFinal states of the DFA are : ", dfa_final_states)
INPUT :
No. of states : 3
No. of transitions : 2
state name : A
path : 0
Enter end state from state A travelling through path 0 :
A
path : 1
Enter end state from state A travelling through path 1 :
A B
state name : B
path : 0
Enter end state from state B travelling through path 0 :
C
path : 1
Enter end state from state B travelling through path 1 :
C
state name : C
path : 0
Enter end state from state C travelling through path 0 :
path : 1
Enter end state from state C travelling through path 1 :
NFA :-
{'A': {'0': ['A'], '1': ['A', 'B']}, 'B': {'0': ['C'], '1': ['C']}, 'C': {'0': [], '1': []}}
Printing NFA table :-
 0 1
A [A] [A, B]
B [C] [C]
C [] []
Enter final state of NFA :
C

"""

    return s


def leftfactoring4a():
    s = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void main() {
  char ch, lhs[20][20], rhs[20][20][20], temp[20], temp1[20];
  int n, n1, count[20], x, y, i, j, k, c[20];
  printf("\nEnter the no. of nonterminals : ");
  scanf("%d", &n);
  n1 = n;
  for (i = 0; i < n; i++) {
    printf("\nNonterminal %d \nEnter the no. of productions : ", i + 1);
    scanf("%d", &c[i]);
    printf("\nEnter LHS : ");
    scanf("%s", lhs[i]);
    for (j = 0; j < c[i]; j++) {
      printf("%s->", lhs[i]);
      scanf("%s", rhs[i][j]);
    }
  }
  for (i = 0; i < n; i++) {
    count[i] = 1;
    while (memcmp(rhs[i][0], rhs[i][1], count[i]) == 0)
      count[i]++;
  }
  for (i = 0; i < n; i++) {
    count[i]--;
    if (count[i] > 0) {
      strcpy(lhs[n1], lhs[i]);
      strcat(lhs[i], "'");
      for (k = 0; k < count[i]; k++)
        temp1[k] = rhs[i][0][k];
      temp1[k++] = '\0';
      for (j = 0; j < c[i]; j++) {
        for (k = count[i], x = 0; k < strlen(rhs[i][j]); x++, k++)
          temp[x] = rhs[i][j][k];
        temp[x++] = '\0';
        if (strlen(rhs[i][j]) == 1)
          strcpy(rhs[n1][1], rhs[i][j]);
        strcpy(rhs[i][j], temp);
      }
      c[n1] = 2;
      strcpy(rhs[n1][0], temp1);
      strcat(rhs[n1][0], lhs[n1]);
      strcat(rhs[n1][0], "'");
      n1++;
    }
  }
  printf("\n\nThe resulting productions are : \n");
  for (i = 0; i < n1; i++) {
    if (i == 0)
      printf("\n %s -> %c|", lhs[i], (char)238);
    else
      printf("\n %s -> ", lhs[i]);
    for (j = 0; j < c[i]; j++) {
      printf(" %s ", rhs[i][j]);
      if ((j + 1) != c[i])
        printf("|");
    }
    printf("\b\b\b\n");
  }
}"""

    return s


def leftrecursion4b():
    s = """#include<iostream>
#include<string>
using namespace std;
int main()
{  string ip,op1,op2,temp;
    int sizes[10] = {};
    char c;
    int n,j,l;
    cout<<"Enter the Parent Non-Terminal : ";
    cin>>c;
    ip.push_back(c);
    op1 += ip + "\'->";
    ip += "->";
    op2+=ip;
    cout<<"Enter the number of productions : ";
    cin>>n;
    for(int i=0;i<n;i++)
    {   cout<<"Enter Production "<<i+1<<" : ";
        cin>>temp;
        sizes[i] = temp.size();
        ip+=temp;
        if(i!=n-1)
            ip += "|";
    }
    cout<<"Production Rule : "<<ip<<endl;
    for(int i=0,k=3;i<n;i++)
    {
        if(ip[0] == ip[k])
        {
            cout<<"Production "<<i+1<<" has left recursion."<<endl;
            if(ip[k] != '#')
            {
                for(l=k+1;l<k+sizes[i];l++)
                    op1.push_back(ip[l]);
                k=l+1;
                op1.push_back(ip[0]);
                op1 += "\'|";
            }
        }
        else
        {
            cout<<"Production "<<i+1<<" does not have left recursion."<<endl;
            if(ip[k] != '#')
            {
                for(j=k;j<k+sizes[i];j++)
                    op2.push_back(ip[j]);
                k=j+1;
                op2.push_back(ip[0]);
                op2 += "\'|";
            }
            else
            {
                op2.push_back(ip[0]);
                op2 += "\'";
            }}}
    op1 += "#";
    cout<<op2<<endl;
    cout<<op1<<endl;
    return 0;}"""

    return s


def firstfollow5():
    s = """import sys
sys.setrecursionlimit(60)

def first(string):
    #print("first({})".format(string))
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
                #print("inside while")

                first_ = first_ | (first_2 - {'@'})
                #print('string[i:]=', string[i:])
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


    #print("returning for first({})".format(string),first_)
    return  first_


def follow(nT):
    #print("inside follow({})".format(nT))
    follow_ = set()
    #print("FOLLOW", FOLLOW)
    prods = productions_dict.items()
    if nT==starting_symbol:
        follow_ = follow_ | {'$'}
    for nt,rhs in prods:
        #print("nt to rhs", nt,rhs)
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
    #print("returning for follow({})".format(nT),follow_)
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


#print("terminals", terminals)

#print("non terminals", non_terminals)

#print("productions",productions)


productions_dict = {}

for nT in non_terminals:
    productions_dict[nT] = []


#print("productions_dict",productions_dict)

for production in productions:
    nonterm_to_prod = production.split("->")
    alternatives = nonterm_to_prod[1].split("/")
    for alternative in alternatives:
        productions_dict[nonterm_to_prod[0]].append(alternative)

#print("productions_dict",productions_dict)

#print("nonterm_to_prod",nonterm_to_prod)
#print("alternatives",alternatives)


FIRST = {}
FOLLOW = {}

for non_terminal in non_terminals:
    FIRST[non_terminal] = set()

for non_terminal in non_terminals:
    FOLLOW[non_terminal] = set()

#print("FIRST",FIRST)

for non_terminal in non_terminals:
    FIRST[non_terminal] = FIRST[non_terminal] | first(non_terminal)

#print("FIRST",FIRST)


FOLLOW[starting_symbol] = FOLLOW[starting_symbol] | {'$'}
for non_terminal in non_terminals:
    FOLLOW[non_terminal] = FOLLOW[non_terminal] | follow(non_terminal)

#print("FOLLOW", FOLLOW)

print("{: ^20}{: ^20}{: ^20}".format('Non Terminals','First','Follow'))
for non_terminal in non_terminals:
    print("{: ^20}{: ^20}{: ^20}".format(non_terminal,str(FIRST[non_terminal]),str(FOLLOW[non_terminal])))"""

    return s


def predparsing6():
    s = """"gram = {
	"E":["E+T","T"],
	"T":["T*F","F"],
	"F":["(E)","i"],
    # "S":["CC"],
    # "C":["eC","d"],
}

def removeDirectLR(gramA, A):
	#gramA is dictonary
	temp = gramA[A]
	tempCr = []
	tempInCr = []
	for i in temp:
		if i[0] == A:
			#tempInCr.append(i[1:])
			tempInCr.append(i[1:]+[A+"'"])
		else:
			#tempCr.append(i)
			tempCr.append(i+[A+"'"])
	tempInCr.append(["e"])
	gramA[A] = tempCr
	gramA[A+"'"] = tempInCr
	return gramA


def checkForIndirect(gramA, a, ai):
	if ai not in gramA:
		return False 
	if a == ai:
		return True
	for i in gramA[ai]:
		if i[0] == ai:
			return False
		if i[0] in gramA:
			return checkForIndirect(gramA, a, i[0])
	return False

def rep(gramA, A):
	temp = gramA[A]
	newTemp = []
	for i in temp:
		if checkForIndirect(gramA, A, i[0]):
			t = []
			for k in gramA[i[0]]:
				t=[]
				t+=k
				t+=i[1:]
				newTemp.append(t)

		else:
			newTemp.append(i)
	gramA[A] = newTemp
	return gramA

def rem(gram):
	c = 1
	conv = {}
	gramA = {}
	revconv = {}
	for j in gram:
		conv[j] = "A"+str(c)
		gramA["A"+str(c)] = []
		c+=1

	for i in gram:
		for j in gram[i]:
			temp = []	
			for k in j:
				if k in conv:
					temp.append(conv[k])
				else:
					temp.append(k)
			gramA[conv[i]].append(temp)


	#print(gramA)
	for i in range(c-1,0,-1):
		ai = "A"+str(i)
		for j in range(0,i):
			aj = gramA[ai][0][0]
			if ai!=aj :
				if aj in gramA and checkForIndirect(gramA,ai,aj):
					gramA = rep(gramA, ai)

	for i in range(1,c):
		ai = "A"+str(i)
		for j in gramA[ai]:
			if ai==j[0]:
				gramA = removeDirectLR(gramA, ai)
				break

	op = {}
	for i in gramA:
		a = str(i)
		for j in conv:
			a = a.replace(conv[j],j)
		revconv[i] = a

	for i in gramA:
		l = []
		for j in gramA[i]:
			k = []
			for m in j:
				if m in revconv:
					k.append(m.replace(m,revconv[m]))
				else:
					k.append(m)
			l.append(k)
		op[revconv[i]] = l

	return op

result = rem(gram)
terminals = []
for i in result:
	for j in result[i]:
		for k in j:
			if k not in result:
				terminals+=[k]
terminals = list(set(terminals))
#print(terminals)

def first(gram, term):
	a = []
	if term not in gram:
		return [term]
	for i in gram[term]:
		if i[0] not in gram:
			a.append(i[0])
		elif i[0] in gram:
			a += first(gram, i[0])
	return a

firsts = {}
for i in result:
	firsts[i] = first(result,i)
#	print(f'First({i}):',firsts[i])

def follow(gram, term):
	a = []
	for rule in gram:
		for i in gram[rule]:
			if term in i:
				temp = i
				indx = i.index(term)
				if indx+1!=len(i):
					if i[-1] in firsts:
						a+=firsts[i[-1]]
					else:
						a+=[i[-1]]
				else:
					a+=["e"]
				if rule != term and "e" in a:
					a+= follow(gram,rule)
	return a

follows = {}
for i in result:
	follows[i] = list(set(follow(result,i)))
	if "e" in follows[i]:
		follows[i].pop(follows[i].index("e"))
	follows[i]+=["$"]
#	print(f'Follow({i}):',follows[i])

resMod = {}
for i in result:
	l = []
	for j in result[i]:
		temp = ""
		for k in j:
			temp+=k
		l.append(temp)
	resMod[i] = l

# create predictive parsing table
tterm = list(terminals)
tterm.pop(tterm.index("e"))
tterm+=["d"]
pptable = {}
for i in result:
	for j in tterm:
		if j in firsts[i]:
			pptable[(i,j)]=resMod[i[0]][0]
		else:
			pptable[(i,j)]=""
	if "e" in firsts[i]:
		for j in tterm:
			if j in follows[i]:
				pptable[(i,j)]="e" 	
pptable[("F","i")] = "i"
toprint = f'{"": <10}'
for i in tterm:
	toprint+= f'|{i: <10}'
print(toprint)
for i in result:
	toprint = f'{i: <10}'
	for j in tterm:
		if pptable[(i,j)]!="":
			toprint+=f'|{i+"->"+pptable[(i,j)]: <10}'
		else:
			toprint+=f'|{pptable[(i,j)]: <10}'
	print(f'{"-":-<76}')
	print(toprint)
 Enter the no. of nonterminals
2
Enter the productions in a grammar
S->CC
C->eC | d
First
FIRS[S] = ed
FIRS[C] = ed
Follow
FOLLOW[S] =$
FOLLOW[C] =ed$
M [S , e] =S->CC
M [S , d] =S->CC
M [C , e] =C->eC
M [C , d] =C->d"""

    return s


def shiftreduceparsing7():
    s = """gram = {
	"E":["E*E","E+E","i"]
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
		break"""
    return s


def lroitems9():
    s = """#include<iostream>
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
Output:-
ENTER THE PRODUCTIONS OF THE GRAMMAR(0 TO END) :
E->E+T
E->T
T->T*F
T->F
F->(E)
F->i
0
augumented grammar
A->E
E->E+T
E->T
T->T*F
T->F
F->(E)
F->i
THE SET OF ITEMS ARE
I0
A->.E
E->.E+T
E->.T
T->.T*F
T->.F
F->.(E)
F->.i
I1
A->E.
E->E.+T
I2
E->T.
T->T.*F
I3
T->F.
I4
F->(.E)
E->.E+T
E->.T
T->.T*F
T->.F
F->.(E)
F->.i
I5
F->i.
I6
E->E+.T
T->.T*F
T->.F
F->.(E)
F->.i
I7
T->T*.F
F->.(E)
F->.i
I8
F->(E.)
E->E.+T
I9
E->E+T.
T->T.*F
I10
T->T*F.
I11
F->(E)."""
    return s


def preftopost10():
    s = """OPERATORS = set(['+', '-', '*', '/', '(', ')'])

PRI = {'+': 1, '-': 1, '*': 2, '/': 2}
def infix_to_postfix(formula):
    stack = []  # only pop when the coming op has priority

    output = ''

    for ch in formula:

        if ch not in OPERATORS:

            output += ch

        elif ch == '(':

            stack.append('(')

        elif ch == ')':

            while stack and stack[-1] != '(':
                output += stack.pop()

            stack.pop()  # pop '('

        else:

            while stack and stack[-1] != '(' and PRI[ch] <= PRI[stack[-1]]:
                output += stack.pop()

            stack.append(ch)

            # leftover

    while stack:
        output += stack.pop()

    print(f'POSTFIX: {output}')

    return output


### INFIX ===> PREFIX ###

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

            op_stack.pop()  # pop '('

        else:

            while op_stack and op_stack[-1] != '(' and PRI[ch] <= PRI[op_stack[-1]]:
                op = op_stack.pop()

                a = exp_stack.pop()

                b = exp_stack.pop()

                exp_stack.append(op + b + a)

            op_stack.append(ch)

            # leftover

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
OUTPUT : A+B^C/R"""

    return s


def threeaddresscode11():
    s = """#include<stdio.h>
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
OUTPUT: a=b+c-d"""

    return s


def dag12():
    s = """#include <stdio.h>
#include <string.h>
int i = 1, j = 0, no = 0, tmpch = 90;
char str[100], left[15], right[15];
void findopr();
void explore();
void fleft(int);
void fright(int);
struct exp {
  int pos;
  char op;
} k[15];
void main() {

  printf("\t\tINTERMEDIATE CODE GENERATION OF DAG\n\n");

  scanf("%s", str);
  printf("The intermediate code:\t\tExpression\n");
  findopr();
  explore();
}
void findopr() {
  for (i = 0; str[i] != '\0'; i++)
    if (str[i] == ':') {
      k[j].pos = i;
      k[j++].op = ':';
    }
  for (i = 0; str[i] != '\0'; i++)
    if (str[i] == '/') {
      k[j].pos = i;
      k[j++].op = '/';
    }
  for (i = 0; str[i] != '\0'; i++)
    if (str[i] == '*') {
      k[j].pos = i;
      k[j++].op = '*';
    }
  for (i = 0; str[i] != '\0'; i++)
    if (str[i] == '+') {
      k[j].pos = i;
      k[j++].op = '+';
    }
  for (i = 0; str[i] != '\0'; i++)
    if (str[i] == '-') {
      k[j].pos = i;
      k[j++].op = '-';
    }
}
void explore() {
  i = 1;
  while (k[i].op != '\0') {
    fleft(k[i].pos);
    fright(k[i].pos);
    str[k[i].pos] = tmpch--;
    printf("\t%c := %s%c%s\t\t", str[k[i].pos], left, k[i].op, right);
    for (j = 0; j < strlen(str); j++)
      if (str[j] != '$')
        printf("%c", str[j]);
    printf("\n");
    i++;
  }
  fright(-1);
  if (no == 0) {
    fleft(strlen(str));
    printf("\t%s := %s", right, left);
  }
  printf("\t%s :=  %c", right, str[k[--i].pos]);
}
void fleft(int x) {
  int w = 0, flag = 0;
  x--;
  while (x != -1 && str[x] != '+' && str[x] != '*' && str[x] != '=' &&
         str[x] != '\0' && str[x] != '-' && str[x] != '/' && str[x] != ':') {
    if (str[x] != '$' && flag == 0) {
      left[w++] = str[x];
      left[w] = '\0';
      str[x] = '$';
      flag = 1;
    }
    x--;
  }
}
void fright(int x) {
  int w = 0, flag = 0;
  x++;
  while (x != -1 && str[x] != '+' && str[x] != '*' && str[x] != '\0' &&
         str[x] != '=' && str[x] != ':' && str[x] != '-' && str[x] != '/') {
    if (str[x] != '$' && flag == 0) {
      right[w++] = str[x];
      right[w] = '\0';
      str[x] = '$';
      flag = 1;
    }
    x++;
  }
}
OUTPUT : a=b*-c+b*-c"""
    return s
