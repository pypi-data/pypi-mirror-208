def solve(n):
    if n == 14:
        print('''for x in range(10): #or in '0123456789ABCDEF'
    if (int('97968' + str(x) + '15', 15) + int('7' + str(x) +'233', 15)) % 14 ==0:
        print(x, (int('97968' + str(x) + '15', 15) + int('7' + str(x) +'233', 15)) // 14)''')
    elif n == 8:
        print('''from itertools import *
n = 1
for i in product('АБЗИ', repeat=4):
    print(i, n)
    n+=1''')
    elif n == 23:
        print('''def task23(start, end):
    if start > end or start == 15: #not include number
        return 0
    if start == end:
        return 1
    if start < end:
        return task23(start+1, end) + task23(start*2, end) + task23(start*3,end)
print(task23(1,11)*task23*(11,25)) #11 - number for include
''')
    elif n == 17:
        print('''f=open("1_17.txt")
a=[]
for s in f:
    a.append(int(s))
a2=[]
for x in a:
    if 9 < x < 100:
        a2.append(x)
max2=max(a2)
pari=[]
for i in range(len(a)-1):
    if (len(str(a[i])) == 2 and len(str(a[i+1])) != 2 or len(str(a[i])) != 2 and len(str(a[i+1])) ==2) and (a[i] + a[i+1]) % max2 == 0:
        pari.append(a[i] + a[i+1])
print(len(pari), max(pari))''')
    elif n == 24:
        print('''f=open('1_24.txt')
s = f.readline()
res = [s[0]]
for i in range(len(s) - 1):
    if s[i] not in 'ABC' or s[i+1] not in 'ABC': #letters for not including
        res[-1] += s[i+1]
    else:
        res.append(s[i+1])
print(len(max(res, key=len)))''')
    elif n == 25:
        print('''from fnmatch import *
for x in range(317, 10**8, 317):
    if fnmatch(str(x),'12??1*56'):
        print(x, x // 317)''')
    elif n == 26:
        print('''f=open('1_26.txt')
k=int(f.readline())
n=int(f.readline())
passagirs = []
yacheiki = [0]*k
for s in f:
    st,end = map(int,s.split())
    passagirs.append([st,end])
passagirs.sort()
cnt=0
max_numb=0
for one_pas in passagirs:
    for j in range(k):
        if yacheiki[j] + 1 <= one_pas[0]:
            yacheiki[j] = one_pas[1]
            cnt+=1
            max_numb=j+1
            break
print(cnt,max_numb)''')


if __name__ == '__main__':
    t=int(input())
    print(solve(t))