

def lexical():
  print('''file  = open("./add.c", 'r')
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
            print (i, " is an identifier")''')
  print("\n\n")
  print('''#include<iostream>
#include<cstring>
#include<stdlib.h>
#include<ctype.h>
#include<fstream>
using namespace std;

string arr[] = { "void", "using", "namespace", "int", "include", "iostream", "std", "main",
"cin", "cout", "return", "float", "double", "string" };

bool
isKeyword (string a)
{
  for (int i = 0; i < 14; i++)
    {
      if (arr[i] == a)
	{
	  return true;
	}
    }
  return false;
}

int main() 
{ 

	string s; 

	cout << "Enter the input: \n";
	cout << "\n";

	while (cin >> s)
	{
        if (s == "+" || s == "-" || s == "" || s == "/" || s == "^" || s == "&&" || s == "||" || s == "=" || s == "==" || s == "&" || s == "|" || s == "%" || s == "++" || s == "--" || s == "+=" || s == "-=" || s == "/=" || s == "=" || s == "%=")
	    {
	      cout << s << " is an operator\n";
	      s = "";
	    }
	  else if (isKeyword (s))
	    {
	      cout << s << " is a keyword\n";
	      s = "";
	    }
	  else if (s == "(" || s == "{" || s == "[" || s == ")" || s == "}" || s == "]" || s == "<" || s == ">" || s == "()" || s == ";" || s == "<<" || s == ">>" || s == "," || s == "#")
	    {
	      cout << s << " is a symbol\n";
	      s = "";

	    }
	  else if (s == "\n" || s == " " || s == "")
	    {
	      s = "";

	    }
	  else if (isdigit (s[0]))
	    {
	      int x = 0;
	      if (!isdigit (s[x++]))
		{
		  continue;
		}
	      else
		{
		  cout << s << " is a constant\n";
		  s = "";
		}
	    }
	  else
	    {
	      cout << s << " is an identifier\n";
	      s = "";
	    } 
	} 

	return 0; 
} 

// Input for the code

// #include <stdio.h>

// void main ( )

// {
//     int x = 6 ;
//     int y = 4 ;
//     x = x + y ;
//     printf("%d", x);
// }''')
  

def retonfa():
  print('''#include <iostream>
#include<string.h>
using namespace std;
int main()
{
	char reg[20]; int q[20][3],i=0,j=1,len,a,b;
	printf("Enter the regular expression: ");
	for (a = 0; a < 20; a++)
		for (b = 0; b < 3; b++)
			q[a][b] = 0;
	scanf("%s",reg);
	printf("Given regular expression: %s\n",reg);
	len=strlen(reg);
	while(i<len)
	{
		if(reg[i]=='a'&&reg[i+1]!='|'&&reg[i+1]!='*') { q[j][0]=j+1; j++; }
		if(reg[i]=='b'&&reg[i+1]!='|'&&reg[i+1]!='*') {	q[j][1]=j+1; j++;	}
		if(reg[i]=='e'&&reg[i+1]!='|'&&reg[i+1]!='*') {	q[j][2]=j+1; j++;	}
		if(reg[i]=='a'&&reg[i+1]=='|'&&reg[i+2]=='b') 
		{ 
		  q[j][2]=((j+1)*10)+(j+3); j++; 
		  q[j][0]=j+1; j++;
			q[j][2]=j+3; j++;
			q[j][1]=j+1; j++;
			q[j][2]=j+1; j++;
			i=i+2;
		}
		if(reg[i]=='b'&&reg[i+1]=='|'&&reg[i+2]=='a')
		{
			q[j][2]=((j+1)*10)+(j+3); j++;
			q[j][1]=j+1; j++;
			q[j][2]=j+3; j++;
			q[j][0]=j+1; j++;
			q[j][2]=j+1; j++;
			i=i+2;
		}
		if(reg[i]=='a'&&reg[i+1]=='*')
		{
			q[j][2]=((j+1)*10)+(j+3); j++;
			q[j][0]=j+1; j++;
			q[j][2]=((j+1)*10)+(j-1); j++;
		}
		if(reg[i]=='b'&&reg[i+1]=='*')
		{
			q[j][2]=((j+1)*10)+(j+3); j++;
			q[j][1]=j+1; j++;
			q[j][2]=((j+1)*10)+(j-1); j++;
		}
		if(reg[i]==')'&&reg[i+1]=='*')
		{
			q[0][2]=((j+1)*10)+1;
			q[j][2]=((j+1)*10)+1;
			j++;
		}
		i++;
	}
	printf("\n\tTransition Table \n");
	printf("_____________________________________\n");
	printf("Current State |\tInput |\tNext State");
	printf("\n_____________________________________\n");
	for(i=0;i<=j;i++)
	{
		if(q[i][0]!=0) printf("\n  q[%d]\t      |   a   |  q[%d]",i,q[i][0]);
		if(q[i][1]!=0) printf("\n  q[%d]\t      |   b   |  q[%d]",i,q[i][1]);
		if(q[i][2]!=0) 
		{
			if(q[i][2]<10) printf("\n  q[%d]\t      |   e   |  q[%d]",i,q[i][2]);
			else printf("\n  q[%d]\t      |   e   |  q[%d] , q[%d]",i,q[i][2]/10,q[i][2]%10);
		}
	}
	printf("\n_____________________________________\n");
	return 0;
}

// Input 

// (a|b)*abb''')
  print("\n\n")
  print('''rows, cols = (20, 3) 
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
		    print(f"\n {q[i]},e-->{q[i][2]}/10 and {q[i][2]}%10")''')
  

def nfatodfa():
  print('''#include <iostream>
#include <vector>
#include <queue>
#include <set>
#include <algorithm>


using namespace std;
void print(vector<vector<vector<int> > > table)
{
    cout << "  STATE/INPUT  |";
    char a = 'a';
    for (int i = 0; i < table[0].size() - 1; i++)
    {
        cout << "   " << a++ << "   |";
    }
    cout << "   ^   " << endl
         << endl;
    for (int i = 0; i < table.size(); i++)
    {
        cout << "       " << i << "      ";
        for (int j = 0; j < table[i].size(); j++)
        {
            cout << " | ";
            for (int k = 0; k < table[i][j].size(); k++)
            {
                cout << table[i][j][k] << " ";
            }
        }
        cout << endl;
    }
}

void printdfa(vector<vector<int> > states, vector<vector<vector<int> > > dfa)
{
    cout << "  STATE/INPUT  ";
    char a = 'a';
    for (int i = 0; i < dfa[0].size(); i++)
    {
        cout << "|   " << a++ << "   ";
    }
    cout << endl;
    for (int i = 0; i < states.size(); i++)
    {
        cout << "{ ";
        for (int h = 0; h < states[i].size(); h++)
            cout << states[i][h] << " ";
        if (states[i].empty())
        {
            cout << "^ ";
        }
        cout << "} ";
        for (int j = 0; j < dfa[i].size(); j++)
        {
            cout << " | ";
            for (int k = 0; k < dfa[i][j].size(); k++)
            {
                cout << dfa[i][j][k] << " ";
            }
            if (dfa[i][j].empty())
            {
                cout << "^ ";
            }
        }
        cout << endl;
    }
}
vector<int> closure(int s, vector<vector<vector<int> > > v)
{
    vector<int> t;
    queue<int> q;
    t.push_back(s);
    int a = v[s][v[s].size() - 1].size();
    for (int i = 0; i < a; i++)
    {
        t.push_back(v[s][v[s].size() - 1][i]);
        // cout<<"t[i]"<<t[i]<<endl;
        q.push(t[i]);
    }
    while (!q.empty())
    {
        int f = q.front();
        q.pop();
        if (!v[f][v[f].size() - 1].empty())
        {
            int u = v[f][v[f].size() - 1].size();
            for (int i = 0; i < u; i++)
            {
                int y = v[f][v[f].size() - 1][i];
                if (find(t.begin(), t.end(), y) == t.end())
                {
                    // cout<<"y"<<y<<endl;
                    t.push_back(y);
                    q.push(y);
                }
            }
        }
    }
    return t;
}
int main()
{
    int n, alpha;
    cout << "************************* NFA to DFA *************************" << endl
         << endl;
    cout << "Enter total number of states in NFA : ";
    cin >> n;
    cout << "Enter number of elements in alphabet : ";
    cin >> alpha;
    vector<vector<vector<int> > > table;
    for (int i = 0; i < n; i++)
    {
        cout << "For state " << i << endl;
        vector<vector<int> > v;
        char a = 'a';
        int y, yn;
        for (int j = 0; j < alpha; j++)
        {
            vector<int> t;
            cout << "Enter no. of output states for input " << a++ << " : ";
            cin >> yn;
            cout << "Enter output states :" << endl;
            for (int k = 0; k < yn; k++)
            {
                cin >> y;
                t.push_back(y);
            }
            v.push_back(t);
        }
        vector<int> t;
        cout << "Enter no. of output states for input ^ : ";
        cin >> yn;
        cout << "Enter output states :" << endl;
        for (int k = 0; k < yn; k++)
        {
            cin >> y;
            t.push_back(y);
        }
        v.push_back(t);
        table.push_back(v);
    }
    cout << "***** TRANSITION TABLE OF NFA *****" << endl;
    print(table);
    cout << endl
         << "***** TRANSITION TABLE OF DFA *****" << endl;
    vector<vector<vector<int> > > dfa;
    vector<vector<int> > states;
    states.push_back(closure(0, table));
    queue<vector<int> > q;
    q.push(states[0]);
    while (!q.empty())
    {
        vector<int> f = q.front();
        q.pop();
        vector<vector<int> > v;
        for (int i = 0; i < alpha; i++)
        {
            vector<int> t;
            set<int> s;
            for (int j = 0; j < f.size(); j++)
            {

                for (int k = 0; k < table[f[j]][i].size(); k++)
                {
                    vector<int> cl = closure(table[f[j]][i][k], table);
                    for (int h = 0; h < cl.size(); h++)
                    {
                        if (s.find(cl[h]) == s.end())
                            s.insert(cl[h]);
                    }
                }
            }
            for (set<int>::iterator u = s.begin(); u != s.end(); u++)
                t.push_back(*u);
            v.push_back(t);
            if (find(states.begin(), states.end(), t) == states.end())
            {
                states.push_back(t);
                q.push(t);
            }
        }
        dfa.push_back(v);
    }
    printdfa(states, dfa);
}

// Sample Input

// Enter total number of states in NFA : 3
// Enter number of elements in alphabet : 2
// For state 0
// Enter no. of output states for input a : 2
// Enter output states :
// 1 2
// Enter no. of output states for input b : 1
// Enter output states :
// 0
// Enter no. of output states for input ^ : 1
// Enter output states :
// 1
// For state 1
// Enter no. of output states for input a : 1
// Enter output states :
// 2
// Enter no. of output states for input b : 1
// Enter output states :

// 2
// Enter no. of output states for input ^ : 2
// Enter output states :
// 0 1
// For state 2
// Enter no. of output states for input a : 1
// Enter output states :
// 1
// Enter no. of output states for input b : 2
// Enter output states :
// 1 2
// Enter no. of output states for input ^ : 1
// Enter output states :
// 2''')
  print("\n\n")
  print('''import pandas as pd

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

print("\nFinal states of the DFA are : ", dfa_final_states)''')
  


def leftrec():
  print('''#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main()
{
    int n;
    cout << "\nEnter number of non terminals: ";
    cin >> n;
    cout << "\nEnter non terminals one by one: ";
    int i;
    vector<string> nonter(n);
    vector<int> leftrecr(n, 0);
    for (i = 0; i < n; ++i)
    {
        cout << "\nNon terminal " << i + 1 << " : ";
        cin >> nonter[i];
    }
    vector<vector<string> > prod;
    cout << "\nEnter 'esp' for null";
    for (i = 0; i < n; ++i)
    {
        cout << "\nNumber of " << nonter[i] << " productions: ";
        int k;
        cin >> k;
        int j;
        cout << "\nOne by one enter all " << nonter[i] << " productions";
        vector<string> temp(k);
        for (j = 0; j < k; ++j)
        {
            cout << "\nRHS of production " << j + 1 << ": ";
            string abc;
            cin >> abc;
            temp[j] = abc;
            if (nonter[i].length() <= abc.length() && nonter[i].compare(abc.substr(0, nonter[i].length())) == 0)
                leftrecr[i] = 1;
        }
        prod.push_back(temp);
    }
    for (i = 0; i < n; ++i)
    {
        cout << leftrecr[i];
    }
    for (i = 0; i < n; ++i)
    {
        if (leftrecr[i] == 0)
            continue;
        int j;
        nonter.push_back(nonter[i] + "'");
        vector<string> temp;
        for (j = 0; j < prod[i].size(); ++j)
        {
            if (nonter[i].length() <= prod[i][j].length() && nonter[i].compare(prod[i][j].substr(0, nonter[i].length())) == 0)
            {
                string abc = prod[i][j].substr(nonter[i].length(), prod[i][j].length() - nonter[i].length()) + nonter[i] + "'";
                temp.push_back(abc);
                prod[i].erase(prod[i].begin() + j);
                --j;
            }
            else
            {
                prod[i][j] += nonter[i] + "'";
            }
        }
        temp.push_back("esp");
        prod.push_back(temp);
    }
    cout << "\n\n";
    cout << "\nNew set of non-terminals: ";
    for (i = 0; i < nonter.size(); ++i)
        cout << nonter[i] << " ";
    cout << "\n\nNew set of productions: ";
    for (i = 0; i < nonter.size(); ++i)
    {
        int j;
        for (j = 0; j < prod[i].size(); ++j)
        {
            cout << "\n"
                 << nonter[i] << " -> " << prod[i][j];
        }
    }
    return 0;
}

// Sample Input

// Enter number of non terminals: 3
// Enter non terminals one by one: 
// Non terminal 1 : E
// Non terminal 2 : T
// Non terminal 3 : F
// Enter 'esp' for null
// Number of E productions: 2
// One by one enter all E productions
// RHS of production 1: E+T
// RHS of production 2: T
// Number of T productions: 2
// One by one enter all T productions
// RHS of production 1: T*F
// RHS of production 2: F
// Number of F productions: 2
// One by one enter all F productions
// RHS of production 1: esp
// RHS of production 2: i''')


def leftfac():
  print('''#include <iostream>
#include <math.h>
#include <vector>
#include <string>
#include <stdlib.h>
using namespace std;

int main()
{
    cout<<"\nEnter number of productions: ";
    int p;
    cin>>p;
    vector<string> prodleft(p),prodright(p);
    cout<<"\nEnter productions one by one: ";
    int i;
    for(i=0;i<p;++i) {
        cout<<"\nLeft of production "<<i+1<<": ";
        cin>>prodleft[i];
        cout<<"\nRight of production "<<i+1<<": ";
        cin>>prodright[i];
    }
    int j;  
    int e=1;
    for(i=0;i<p;++i) {
        for(j=i+1;j<p;++j) {
            if(prodleft[j]==prodleft[i]) {
                int k=0;
                string com="";
                while(k<prodright[i].length()&&k<prodright[j].length()&&prodright[i][k]==prodright[j][k]) {
                    com+=prodright[i][k];
                    ++k;
                }
                if(k==0)
                    continue;
                char* buffer;
                string comleft=prodleft[i];
                if(k==prodright[i].length()) {
                    prodleft[i]+=string(itoa(e,buffer,10));
                    prodleft[j]+=string(itoa(e,buffer,10));
                    prodright[i]="^";
                    prodright[j]=prodright[j].substr(k,prodright[j].length()-k);
                }
                else if(k==prodright[j].length()) {
                    prodleft[i]+=string(itoa(e,buffer,10));
                    prodleft[j]+=string(itoa(e,buffer,10));
                    prodright[j]="^";
                    prodright[i]=prodright[i].substr(k,prodright[i].length()-k);
                }
                else {
                    prodleft[i]+=string(itoa(e,buffer,10));
                    prodleft[j]+=string(itoa(e,buffer,10));
                    prodright[j]=prodright[j].substr(k,prodright[j].length()-k);
                    prodright[i]=prodright[i].substr(k,prodright[i].length()-k);
                }
                int l;
                for(l=j+1;l<p;++l) {
                    if(comleft==prodleft[l]&&com==prodright[l].substr(0,fmin(k,prodright[l].length()))) {
                        prodleft[l]+=string(itoa(e,buffer,10));
                        prodright[l]=prodright[l].substr(k,prodright[l].length()-k);
                    }
                }
                prodleft.push_back(comleft);
                prodright.push_back(com+prodleft[i]);
                ++p;
                ++e;
            }
        }
    }
    cout<<"\n\nNew productions";
    for(i=0;i<p;++i) {
        cout<<"\n"<<prodleft[i]<<"->"<<prodright[i];
    }
    return 0;
}''')
  

def firstfollow():
  print('''// C program to calculate the First and
// Follow sets of a given grammar
#include <stdio.h>
#include <ctype.h>
#include <string.h>

// Functions to calculate Follow
void followfirst(char, int, int);
void follow(char c);

// Function to calculate First
void findfirst(char, int, int);

int count, n = 0;

// Stores the final result
// of the First Sets
char calc_first[10][100];

// Stores the final result
// of the Follow Sets
char calc_follow[10][100];
int m = 0;

// Stores the production rules
char production[10][10];
char f[10], first[10];
int k;
char ck;
int e;

int main(int argc, char **argv)
{
    int jm = 0;
    int km = 0;
    int i, choice;
    char c, ch;
    count = 8;

    strcpy(production[0], "E=TR");
    strcpy(production[1], "R=+TR");
    strcpy(production[2], "R=#");
    strcpy(production[3], "T=FY");
    strcpy(production[4], "Y=*FY");
    strcpy(production[5], "Y=#");
    strcpy(production[6], "F=(E)");
    strcpy(production[7], "F=i");

    int kay;
    char done[count];
    int ptr = -1;

    // Initializing the calc_first array
    for (k = 0; k < count; k++)
    {
        for (kay = 0; kay < 100; kay++)
        {
            calc_first[k][kay] = '!';
        }
    }
    int point1 = 0, point2, x;

    for (k = 0; k < count; k++)
    {
        c = production[k][0];
        point2 = 0;
        x = 0;

        // Checking if First of c has
        // already been calculated
        for (kay = 0; kay <= ptr; kay++)
            if (c == done[kay])
                x = 1;

        if (x == 1)
            continue;

        // Function call
        findfirst(c, 0, 0);
        ptr += 1;

        // Adding c to the calculated list
        done[ptr] = c;
        printf("\n First(%c) = { ", c);
        calc_first[point1][point2++] = c;

        // Printing the First Sets of the grammar
        for (i = 0 + jm; i < n; i++)
        {
            int lark = 0, chk = 0;

            for (lark = 0; lark < point2; lark++)
            {

                if (first[i] == calc_first[point1][lark])
                {
                    chk = 1;
                    break;
                }
            }
            if (chk == 0)
            {
                printf("%c, ", first[i]);
                calc_first[point1][point2++] = first[i];
            }
        }
        printf("}\n");
        jm = n;
        point1++;
    }
    printf("\n");
    printf("-----------------------------------------------\n\n");
    char donee[count];
    ptr = -1;

    // Initializing the calc_follow array
    for (k = 0; k < count; k++)
    {
        for (kay = 0; kay < 100; kay++)
        {
            calc_follow[k][kay] = '!';
        }
    }
    point1 = 0;
    int land = 0;
    for (e = 0; e < count; e++)
    {
        ck = production[e][0];
        point2 = 0;
        x = 0;

        // Checking if Follow of ck
        // has alredy been calculated
        for (kay = 0; kay <= ptr; kay++)
            if (ck == donee[kay])
                x = 1;

        if (x == 1)
            continue;
        land += 1;

        // Function call
        follow(ck);
        ptr += 1;

        // Adding ck to the calculated list
        donee[ptr] = ck;
        printf(" Follow(%c) = { ", ck);
        calc_follow[point1][point2++] = ck;

        // Printing the Follow Sets of the grammar
        for (i = 0 + km; i < m; i++)
        {
            int lark = 0, chk = 0;
            for (lark = 0; lark < point2; lark++)
            {
                if (f[i] == calc_follow[point1][lark])
                {
                    chk = 1;
                    break;
                }
            }
            if (chk == 0)
            {
                printf("%c, ", f[i]);
                calc_follow[point1][point2++] = f[i];
            }
        }
        printf(" }\n\n");
        km = m;
        point1++;
    }
}

void follow(char c)
{
    int i, j;

    // Adding "$" to the follow
    // set of the start symbol
    if (production[0][0] == c)
    {
        f[m++] = '$';
    }
    for (i = 0; i < 10; i++)
    {
        for (j = 2; j < 10; j++)
        {
            if (production[i][j] == c)
            {
                if (production[i][j + 1] != '\0')
                {
                    // Calculate the first of the next
                    // Non-Terminal in the production
                    followfirst(production[i][j + 1], i, (j + 2));
                }

                if (production[i][j + 1] == '\0' && c != production[i][0])
                {
                    // Calculate the follow of the Non-Terminal
                    // in the L.H.S. of the production
                    follow(production[i][0]);
                }
            }
        }
    }
}

void findfirst(char c, int q1, int q2)
{
    int j;

    // The case where we
    // encounter a Terminal
    if (!(isupper(c)))
    {
        first[n++] = c;
    }
    for (j = 0; j < count; j++)
    {
        if (production[j][0] == c)
        {
            if (production[j][2] == '#')
            {
                if (production[q1][q2] == '\0')
                    first[n++] = '#';
                else if (production[q1][q2] != '\0' && (q1 != 0 || q2 != 0))
                {
                    // Recursion to calculate First of New
                    // Non-Terminal we encounter after epsilon
                    findfirst(production[q1][q2], q1, (q2 + 1));
                }
                else
                    first[n++] = '#';
            }
            else if (!isupper(production[j][2]))
            {
                first[n++] = production[j][2];
            }
            else
            {
                // Recursion to calculate First of
                // New Non-Terminal we encounter
                // at the beginning
                findfirst(production[j][2], j, 3);
            }
        }
    }
}

void followfirst(char c, int c1, int c2)
{
    int k;

    // The case where we encounter
    // a Terminal
    if (!(isupper(c)))
        f[m++] = c;
    else
    {
        int i = 0, j = 1;
        for (i = 0; i < count; i++)
        {
            if (calc_first[i][0] == c)
                break;
        }

        // Including the First set of the
        //  Non-Terminal in the Follow of
        //  the original query
        while (calc_first[i][j] != '!')
        {
            if (calc_first[i][j] != '#')
            {
                f[m++] = calc_first[i][j];
            }
            else
            {
                if (production[c1][c2] == '\0')
                {
                    // Case where we reach the
                    // end of a production
                    follow(production[c1][0]);
                }
                else
                {
                    // Recursion to the next symbol
                    // in case we encounter a "#"
                    followfirst(production[c1][c2], c1, c2 + 1);
                }
            }
            j++;
        }
    }
}''')


  

def predictiveparse():
  print('''#include <iostream>
#include <string.h>
int main()
{
    char fin[10][20], st[10][20], ft[20][20], fol[20][20];
    int a = 0, e, i, t, b, c, n, k, l = 0, j, s, m, p;

    printf("Enter the no. of nonterminals\n");
    scanf("%d", &n);
    printf("Enter the productions in a grammar\n");
    for (i = 0; i < n; i++)
        scanf("%s", st[i]);
    for (i = 0; i < n; i++)
        fol[i][0] = '\0';
    for (s = 0; s < n; s++)
    {
        for (i = 0; i < n; i++)
        {
            j = 3;
            l = 0;
            a = 0;
        l1:
            if (!((st[i][j] > 64) && (st[i][j] < 91)))
            {
                for (m = 0; m < l; m++)
                {
                    if (ft[i][m] == st[i][j])
                        goto s1;
                }
                ft[i][l] = st[i][j];
                l = l + 1;
            s1:
                j = j + 1;
            }
            else
            {
                if (s > 0)
                {
                    while (st[i][j] != st[a][0])
                    {
                        a++;
                    }
                    b = 0;
                    while (ft[a][b] != '\0')
                    {
                        for (m = 0; m < l; m++)
                        {
                            if (ft[i][m] == ft[a][b])
                                goto s2;
                        }
                        ft[i][l] = ft[a][b];
                        l = l + 1;
                    s2:
                        b = b + 1;
                    }
                }
            }
            while (st[i][j] != '\0')
            {
                if (st[i][j] == '|')
                {
                    j = j + 1;
                    goto l1;
                }
                j = j + 1;
            }

            ft[i][l] = '\0';
        }
    }
    printf("First \n");
    for (i = 0; i < n; i++)
        printf("FIRS[%c]=%s\n", st[i][0], ft[i]);
    fol[0][0] = '$';
    for (i = 0; i < n; i++)
    {
        k = 0;
        j = 3;
        if (i == 0)
            l = 1;
        else
            l = 0;
    k1:
        while ((st[i][0] != st[k][j]) && (k < n))
        {
            if (st[k][j] == '\0')
            {
                k++;
                j = 2;
            }
            j++;
        }

        j = j + 1;
        if (st[i][0] == st[k][j - 1])
        {
            if ((st[k][j] != '|') && (st[k][j] != '\0'))
            {
                a = 0;
                if (!((st[k][j] > 64) && (st[k][j] < 91)))
                {
                    for (m = 0; m < l; m++)
                    {
                        if (fol[i][m] == st[k][j])
                            goto q3;
                    }
                    fol[i][l] = st[k][j];
                    l++;
                q3:;
                }
                else
                {
                    while (st[k][j] != st[a][0])
                    {
                        a++;
                    }
                    p = 0;
                    while (ft[a][p] != '\0')
                    {
                        if (ft[a][p] != '@')
                        {
                            for (m = 0; m < l; m++)
                            {
                                if (fol[i][m] == ft[a][p])
                                    goto q2;
                            }
                            fol[i][l] = ft[a][p];
                            l = l + 1;
                        }
                        else
                            e = 1;
                    q2:
                        p++;
                    }
                    if (e == 1)
                    {
                        e = 0;
                        goto a1;
                    }
                }
            }
            else
            {
            a1:
                c = 0;
                a = 0;
                while (st[k][0] != st[a][0])
                {
                    a++;
                }
                while ((fol[a][c] != '\0') && (st[a][0] != st[i][0]))
                {
                    for (m = 0; m < l; m++)
                    {
                        if (fol[i][m] == fol[a][c])
                            goto q1;
                    }
                    fol[i][l] = fol[a][c];
                    l++;
                q1:
                    c++;
                }
            }
            goto k1;
        }
        fol[i][l] = '\0';
    }
    printf("Follow \n");
    for (i = 0; i < n; i++)
        printf("FOLLOW[%c]=%s\n", st[i][0], fol[i]);
    printf("\n");
    s = 0;
    for (i = 0; i < n; i++)
    {
        j = 3;
        while (st[i][j] != '\0')
        {
            if ((st[i][j - 1] == '|') || (j == 3))
            {
                for (p = 0; p <= 2; p++)
                {
                    fin[s][p] = st[i][p];
                }
                t = j;
                for (p = 3; ((st[i][j] != '|') && (st[i][j] != '\0')); p++)
                {
                    fin[s][p] = st[i][j];
                    j++;
                }
                fin[s][p] = '\0';
                if (st[i][k] == '@')
                {
                    b = 0;
                    a = 0;
                    while (st[a][0] != st[i][0])
                    {
                        a++;
                    }
                    while (fol[a][b] != '\0')
                    {
                        printf("M[%c,%c]=%s\n", st[i][0], fol[a][b], fin[s]);
                        b++;
                    }
                }
                else if (!((st[i][t] > 64) && (st[i][t] < 91)))
                    printf("M[%c,%c]=%s\n", st[i][0], st[i][t], fin[s]);
                else
                {
                    b = 0;
                    a = 0;
                    while (st[a][0] != st[i][3])
                    {
                        a++;
                    }
                    while (ft[a][b] != '\0')
                    {
                        printf("M[%c,%c]=%s\n", st[i][0], ft[a][b], fin[s]);
                        b++;
                    }
                }
                s++;
            }
            if (st[i][j] == '|')
                j++;
        }
    }
}
// Enter the no. of nonterminals
// 2
// Enter the productions in a grammar
// S->CC
// C->eC|d''')
  print("\n\n")
  print('''gram = {
	"E":["E+T","T"],
	"T":["T*F","F"],
	"F":["(E)","i"],
    # "S":["CC"],
    # "C":["eC","d"],
}

def removeDirectLR(gramA, A):
	"""gramA is dictonary"""
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
	print(toprint)''')


def shiftreduceparse():
  print('''#include <iostream>
#include <vector>
#include <string>

using namespace std;

int n;
string s;
vector<char> st;
vector<char> a;

void StackAndInput(int i)
{
    // print stack and remaining input vector elements
    cout << "$";
    for (auto x : st)
        cout << x;
    cout << "\t";
    for (int j = i; j < n; j++)
        cout << a[j];
    cout << "\t";
}

void check()
{
    // check if there any reduction possible for stack elements
    for (int i = 0; i < st.size(); i++)
    {
        if (st[i] == 'a')
        {
            st[i] = 'E';
            StackAndInput(i + 1);
            cout << "REDUCE E->a\n";
            check(); // we again do checking because here we may need to reduce continuously
        }
        if (i + 2 < st.size() && st[i] == 'E' && (st[i + 1] == ('+') || st[i + 1] == ('*')) && st[i + 2] == 'E')
        {
            st.pop_back();
            st.pop_back();
            StackAndInput(i + 1);
            if (st[i + 1] == '+')
                cout << "REDUCE E->E+E\n";
            else if (st[i + 1] == '*')
                cout << "REDUCE E->E*E\n";
        }
    }
}

int main()
{
    cout << "GRAMMAR is : \n E->E+E \n E->E*E \n E->a\n";
    cout << "Enter input string: ";
    cin >> s;
    n = s.length();
    for (int i = 0; i < n; i++)
        a.push_back(s[i]);

    cout << "\nstack\tinput\taction\n";
    for (int i = 0; i < n; i++)
    {
        st.push_back(a[i]);
        a[i] = ' '; // replace element with space so that it not visible in output
        StackAndInput(i + 1);
        cout << "SHIFT->" << st.back() << "\n";
        check();
    }
    if (st.size() == 1 && st[0] == 'E')
        cout << "\nstring accepted\n";
    else
        cout << "\nstring rejected\n";
}

// GRAMMAR is : 
//  E->E+E 
//  E->E*E 
//  E->a
// Enter input string: i+i*i
// Sample Input:
// a+a*a''')
  print("\n\n")
  print('''gram = {
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
		break
		
# Enter the string 
# i+i*i''')
  


def leadingtrailing():
    print('''#include<iostream>
#include<conio.h>
#include<stdio.h>
#include<string.h>
#include<stdlib.h>
using namespace std;

int vars,terms,i,j,k,m,rep,count,temp=-1;
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
			count=0;
			while(gram[i].rhs[j][count]!=) //write = ' \ x 0 '
				count++;
			for(k=0;k<terms;k++)
			{
				if(gram[i].rhs[j][count-1]==term[k])
					trail[i][k]=1;
				else
				{
					if(gram[i].rhs[j][count-2]==term[k])
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
				count=0;
				while(gram[i].rhs[j][count]!=) //write = ' \ x 0 '
					count++;
				for(m=1;m<vars;m++)
				{
					if(gram[i].rhs[j][count-1]==var[m])
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

}''')


def lr0():
  print('''#include <iostream>
#include <string.h>

using namespace std;

char prod[20][20], listofvar[26] = "ABCDEFGHIJKLMNOPQR";
int novar = 1, i = 0, j = 0, k = 0, n = 0, m = 0, arr[30];
int noitem = 0;

struct Grammar
{
    char lhs;
    char rhs[8];
} g[20], item[20], clos[20][10];

int isvariable(char variable)
{
    for (int i = 0; i < novar; i++)
        if (g[i].lhs == variable)
            return i + 1;
    return 0;
}
void findclosure(int z, char a)
{
    int n = 0, i = 0, j = 0, k = 0, l = 0;
    for (i = 0; i < arr[z]; i++)
    {
        for (j = 0; j < strlen(clos[z][i].rhs); j++)
        {
            if (clos[z][i].rhs[j] == '.' && clos[z][i].rhs[j + 1] == a)
            {
                clos[noitem][n].lhs = clos[z][i].lhs;
                strcpy(clos[noitem][n].rhs, clos[z][i].rhs);
                char temp = clos[noitem][n].rhs[j];
                clos[noitem][n].rhs[j] = clos[noitem][n].rhs[j + 1];
                clos[noitem][n].rhs[j + 1] = temp;
                n = n + 1;
            }
        }
    }
    for (i = 0; i < n; i++)
    {
        for (j = 0; j < strlen(clos[noitem][i].rhs); j++)
        {
            if (clos[noitem][i].rhs[j] == '.' && isvariable(clos[noitem][i].rhs[j + 1]) > 0)
            {
                for (k = 0; k < novar; k++)
                {
                    if (clos[noitem][i].rhs[j + 1] == clos[0][k].lhs)
                    {
                        for (l = 0; l < n; l++)
                            if (clos[noitem][l].lhs == clos[0][k].lhs && strcmp(clos[noitem][l].rhs, clos[0][k].rhs) == 0)
                                break;
                        if (l == n)
                        {
                            clos[noitem][n].lhs = clos[0][k].lhs;
                            strcpy(clos[noitem][n].rhs, clos[0][k].rhs);
                            n = n + 1;
                        }
                    }
                }
            }
        }
    }
    arr[noitem] = n;
    int flag = 0;
    for (i = 0; i < noitem; i++)
    {
        if (arr[i] == n)
        {
            for (j = 0; j < arr[i]; j++)
            {
                int c = 0;
                for (k = 0; k < arr[i]; k++)
                    if (clos[noitem][k].lhs == clos[i][k].lhs && strcmp(clos[noitem][k].rhs, clos[i][k].rhs) == 0)
                        c = c + 1;
                if (c == arr[i])
                {
                    flag = 1;
                    goto exit;
                }
            }
        }
    }
exit:;
    if (flag == 0)
        arr[noitem++] = n;
}

int main()
{
    cout << "ENTER THE PRODUCTIONS OF THE GRAMMAR(0 TO END) :\n";
    do
    {
        cin >> prod[i++];
    } while (strcmp(prod[i - 1], "0") != 0);
    for (n = 0; n < i - 1; n++)
    {
        m = 0;
        j = novar;
        g[novar++].lhs = prod[n][0];
        for (k = 3; k < strlen(prod[n]); k++)
        {
            if (prod[n][k] != '|')
                g[j].rhs[m++] = prod[n][k];
            if (prod[n][k] == '|')
            {
                g[j].rhs[m] = '\0';
                m = 0;
                j = novar;
                g[novar++].lhs = prod[n][0];
            }
        }
    }
    for (i = 0; i < 26; i++)
        if (!isvariable(listofvar[i]))
            break;
    g[0].lhs = listofvar[i];
    char temp[2] = {g[1].lhs, '\0'};
    strcat(g[0].rhs, temp);
    cout << "\n\n augumented grammar \n";
    for (i = 0; i < novar; i++)
        cout << endl
             << g[i].lhs << "->" << g[i].rhs << " ";

    for (i = 0; i < novar; i++)
    {
        clos[noitem][i].lhs = g[i].lhs;
        strcpy(clos[noitem][i].rhs, g[i].rhs);
        if (strcmp(clos[noitem][i].rhs, "ε") == 0)
            strcpy(clos[noitem][i].rhs, ".");
        else
        {
            for (int j = strlen(clos[noitem][i].rhs) + 1; j >= 0; j--)
                clos[noitem][i].rhs[j] = clos[noitem][i].rhs[j - 1];
            clos[noitem][i].rhs[0] = '.';
        }
    }
    arr[noitem++] = novar;
    for (int z = 0; z < noitem; z++)
    {
        char list[10];
        int l = 0;
        for (j = 0; j < arr[z]; j++)
        {
            for (k = 0; k < strlen(clos[z][j].rhs) - 1; k++)
            {
                if (clos[z][j].rhs[k] == '.')
                {
                    for (m = 0; m < l; m++)
                        if (list[m] == clos[z][j].rhs[k + 1])
                            break;
                    if (m == l)
                        list[l++] = clos[z][j].rhs[k + 1];
                }
            }
        }
        for (int x = 0; x < l; x++)
            findclosure(z, list[x]);
    }
    cout << "\n THE SET OF ITEMS ARE \n\n";
    for (int z = 0; z < noitem; z++)
    {
        cout << "\n I" << z << "\n\n";
        for (j = 0; j < arr[z]; j++)
            cout << clos[z][j].lhs << "->" << clos[z][j].rhs << "\n";
    }
}

// Sample Input

// E->E + T 
// E-> T 
// T->T *F 
// F->(E)
// F->i 
// 0''')


def postfix():
  print('''#include<stdio.h>
#include<stdlib.h>      
#include<ctype.h>    
#include<string.h>

#define SIZE 100



char stack[SIZE];
int top = -1;

void push(char item)
{
	if(top >= SIZE-1)
	{
		printf("\nStack Overflow.");
	}
	else
	{
		top = top+1;
		stack[top] = item;
	}
}
char pop()
{
	char item ;

	if(top <0)
	{
		printf("stack under flow: invalid infix expression");
		getchar();
		exit(1);
	}
	else
	{
		item = stack[top];
		top = top-1;
		return(item);
	}
}
int is_operator(char symbol)
{
	if(symbol == '^' || symbol == '*' || symbol == '/' || symbol == '+' || symbol =='-')
	{
		return 1;
	}
	else
	{
	return 0;
	}
}
int precedence(char symbol)
{
	if(symbol == '^')
	{
		return(3);
	}
	else if(symbol == '*' || symbol == '/')
	{
		return(2);
	}
	else if(symbol == '+' || symbol == '-')          
	{
		return(1);
	}
	else
	{
		return(0);
	}
}

void InfixToPostfix(char infix_exp[], char postfix_exp[])
{ 
	int i, j;
	char item;
	char x;

	push('(');                              
	strcat(infix_exp,")");                 

	i=0;
	j=0;
	item=infix_exp[i];        

	while(item != '\0')        
	{
		if(item == '(')
		{
			push(item);
		}
		else if( isdigit(item) || isalpha(item))
		{
			postfix_exp[j] = item;              
			j++;
		}
		else if(is_operator(item) == 1)       
		{
			x=pop();
			while(is_operator(x) == 1 && precedence(x)>= precedence(item))
			{
				postfix_exp[j] = x;                  
				j++;
				x = pop();                       
			}
			push(x);
		
			push(item);                
		}
		else if(item == ')')         
		{
			x = pop();                   
			while(x != '(')               
			{
				postfix_exp[j] = x;
				j++;
				x = pop();
			}
		}
		else
		{ 
			printf("\nInvalid infix Expression.\n");       
			getchar();
			exit(1);
		}
		i++;


		item = infix_exp[i]; 
	}
	if(top>0)
	{
		printf("\nInvalid infix Expression.\n");      
		getchar();
		exit(1);
	}
	if(top>0)
	{
		printf("\nInvalid infix Expression.\n");       
		getchar();
		exit(1);
	}


	postfix_exp[j] = '\0';
}
int main()
{
	char infix[SIZE], postfix[SIZE];         
	printf("ASSUMPTION: The infix expression contains single letter variables and single digit constants only.\n");
	printf("\nEnter Infix expression : ");
	gets(infix);

	InfixToPostfix(infix,postfix);                  
	printf("Postfix Expression: ");
	puts(postfix);                     

	return 0;
}

// Sample input

// (A+B)*C-D/E''')
  

def prefix():
  print('''#include<stdio.h>
#include<string.h>
#include<stdlib.h>

#define MAX 20

char str[MAX], stack[MAX];
int top = -1;

void push(char c)
{
  stack[++top] = c;
}

char pop()
{
  return stack[top--];
}
// A utility function to check if the given character is operand 
int checkIfOperand(char ch)
{
  return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z');
}

//function to check if it is an operator
int isOperator(char x) 
{
  switch (x) {
  case '+':
  case '-':
  case '/':
  case '*':
    return 1;
  }
  return 0;
}

void postfixToprfix() 
{
  int n, i, j = 0;
  char c[20];
  char a, b, op;

  printf("Enter the postfix expression:\n");
  scanf("%s", str);

  n = strlen(str);

  for (i = 0; i < MAX; i++)
    stack[i] = '\0';
  printf("Prefix expression is:\t");

  for (i = n - 1; i >= 0; i--)
  {
    if (isOperator(str[i]))
    {
      push(str[i]);
    } else
    {
      c[j++] = str[i];
      while ((top != -1) && (stack[top] == '#')) 
      {
        a = pop();
        c[j++] = pop();
      }
      push('#');
    }
  }
  c[j] = '\0';

  i = 0;
  j = strlen(c) - 1;
  char d[20];

  while (c[i] != '\0') {
    d[j--] = c[i++];
  }

  printf("%s\n", d);

}
int main() 
{
  postfixToprfix();

  return 0;
}

// Sample Input

// A+B^C/R''')
  
def threeaddresscode():
  print('''#include <stdio.h>

#include <ctype.h>

#include <stdlib.h>

#include <string.h>

void small();
void dove(int i);
int p[5] = {0,1,2,3,4},
    c = 1, i, k, l, m, pi;
char sw[5] = {'=','-','+','/','*'},
     j[20], a[5], b[5], ch[2];
void main()
{
  printf("Enter the expression:");
  scanf("%s", j);
  printf("\tThe Intermediate code is:\n");
  small();
}
void dove(int i)
{
  a[0] = b[0] = '\0';
  if (!isdigit(j[i + 2]) && !isdigit(j[i - 2]))
  {
    a[0] = j[i - 1];
    b[0] = j[i + 1];
  }
  if (isdigit(j[i + 2]))
  {
    a[0] = j[i - 1];
    b[0] = 't';
    b[1] = j[i + 2];
  }
  if (isdigit(j[i - 2]))
  {
    b[0] = j[i + 1];
    a[0] = 't';
    a[1] = j[i - 2];
    b[1] = '\0';
  }
  if (isdigit(j[i + 2]) && isdigit(j[i - 2]))
  {
    a[0] = 't';
    b[0] = 't';
    a[1] = j[i - 2];
    b[1] = j[i + 2];
    sprintf(ch, "%d", c);
    j[i + 2] = j[i - 2] = ch[0];
  }
  if (j[i] == '*')
    printf("\tt%d=%s*%s\n", c, a, b);
  if (j[i] == '/')
    printf("\tt%d=%s/%s\n", c, a, b);
  if (j[i] == '+')
    printf("\tt%d=%s+%s\n", c, a, b);
  if (j[i] == '-')
    printf("\tt%d=%s-%s\n", c, a, b);
  if (j[i] == '=')
    printf("\t%c=t%d", j[i - 1], --c);
  sprintf(ch, "%d", c);
  j[i] = ch[0];
  c++;
  small();
}
void small()
{
  pi = 0;
  l = 0;
  for (i = 0; i < strlen(j); i++)
  {
    for (m = 0; m < 5; m++)
      if (j[i] == sw[m])
        if (pi <= p[m])
        {
          pi = p[m];
          l = 1;
          k = i;
        }
  }
  if (l == 1)
    dove(k);
  else
    exit(0);
}

// Sample Input

// a=b+c-d''')
  


def codegenerator():
  print('''#include <stdio.h>
#include <string.h>
void main()
{
    char icode[10][30], str[20], opr[10];
    int i = 0;
    printf("\nEnter the set of intermediate code (terminated by exit):\n");
    do
    {
        scanf("%s", icode[i]);
    } while (strcmp(icode[i++], "exit") != 0);
    printf("\nTarget code generation");
    printf("\n*******");
    i = 0;
    do
    {
        strcpy(str, icode[i]);
        switch (str[3])
        {
        case '+':
            strcpy(opr, "ADD");
            break;
        case '-':
            strcpy(opr, "SUB");
            break;
        case '*':
            strcpy(opr, "MUL");
            break;
        case '/':
            strcpy(opr, "DIV");
            break;
        }

        printf("\n\tMov %c,R%d", str[2], i);
        printf("\n\%s%c,,R%d", opr, str[4], i);
        printf("\n\tMov R%d%c", i, str[0]);
    } while (strcmp(icode[++i], "exit") != 0);
}

// Sample Input

// 7+3
// 0
// exit''')
  

def dag():
  print('''#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;
class DAG
{
public:
    char label;
    char data;
    DAG *left;
    DAG *right;

    DAG(char x)
    {
        label = '_';
        data = x;
        left = NULL;
        right = NULL;
    }
    DAG(char lb, char x, DAG *lt, DAG *rt)
    {
        label = lb;
        data = x;
        left = lt;
        right = rt;
    }
};

int main()
{
    int n;
    n = 3;
    string st[n];
    st[0] = "A=x+y";
    st[1] = "B=A*z";
    st[2] = "C=B/x";
    unordered_map<char, DAG *> labelDAGNode;

    for (int i = 0; i < 3; i++)
    {
        string stTemp = st[i];
        for (int j = 0; j < 5; j++)
        {
            char tempLabel = stTemp[0];
            char tempLeft = stTemp[2];
            char tempData = stTemp[3];
            char tempRight = stTemp[4];
            DAG *leftPtr;
            DAG *rightPtr;
            if (labelDAGNode.count(tempLeft) == 0)
            {
                leftPtr = new DAG(tempLeft);
            }
            else
            {
                leftPtr = labelDAGNode[tempLeft];
            }
            if (labelDAGNode.count(tempRight) == 0)
            {
                rightPtr = new DAG(tempRight);
            }
            else
            {
                rightPtr = labelDAGNode[tempRight];
            }
            DAG *nn = new DAG(tempLabel, tempData, leftPtr, rightPtr);
            labelDAGNode.insert(make_pair(tempLabel, nn));
        }
    }
    cout << "Label      ptr      leftPtr       rightPtr" << endl;
    for (int i = 0; i < n; i++)
    {
        DAG *x = labelDAGNode[st[i][0]];
        cout << st[i][0] << "            " << x->data << "            ";
        if (x->left->label == '_')
            cout << x->left->data;
        else
            cout << x->left->label;
        cout << "          ";
        if (x->right->label == '_')
            cout << x->right->data;
        else
            cout << x->right->label;
        cout << endl;
    }
    return 0;
}''')

