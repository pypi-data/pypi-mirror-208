#!/usr/bin/env python
__version__='0.4.3'
last_update='2023-05-17'
author='Damien Marsic, damien.marsic@aliyun.com'
license='GNU General Public v3 (GPLv3)'
docs='https://dmbiolib.readthedocs.io'

import sys,os,gzip,time,math
from glob import glob
from collections import defaultdict,Counter
import numpy as np
from matplotlib import pyplot as plt

script=os.path.basename(__file__).split('.')[0]
dna='atgc'
ambiguous="ryswkmbdhvn"
aa="ARNDCQEGHILKMFPSTWYV"
IUPAC=[set('ag'),set('ct'),set('gc'),set('at'),set('gt'),set('ac'),set('cgt'),set('agt'),set('act'),set('acg'),set('atgc')]
gcode={
'ggg':'G','gga':'G','ggc':'G','ggt':'G','gag':'E','gaa':'E','gac':'D','gat':'D','gcg':'A', 'gca':'A', 'gcc':'A', 'gct':'A', 'gtg':'V', 'gta':'V', 'gtc':'V', 'gtt':'V',
'agg':'R','aga':'R','agc':'S','agt':'S','aag':'K','aaa':'K','aac':'N','aat':'N','acg':'T', 'aca':'T', 'acc':'T', 'act':'T', 'atg':'M', 'ata':'I', 'atc':'I', 'att':'I',
'cgg':'R','cga':'R','cgc':'R','cgt':'R','cag':'Q','caa':'Q','cac':'H','cat':'H','ccg':'P', 'cca':'P', 'ccc':'P', 'cct':'P', 'ctg':'L', 'cta':'L', 'ctc':'L', 'ctt':'L',
'tgg':'W','tga':'*','tgc':'C','tgt':'C','tag':'*','taa':'*','tac':'Y','tat':'Y','tcg':'S', 'tca':'S', 'tcc':'S', 'tct':'S', 'ttg':'L', 'tta':'L', 'ttc':'F', 'ttt':'F'}
bpairs={'a':'t','c':'g','g':'c','t':'a','n':'n','r':'y','y':'r','s':'s','w':'w','k':'m','m':'k','b':'v','d':'h','h':'d','v':'b'}

def aa_dist(seqs,parvrs,fname,r):
    aadist={}
    mutdist={}
    for vr in seqs:
        if parvrs and not vr in parvrs:
            continue
        if not seqs[vr]:
            continue
        temp={}
        total=0
        mut={}
        name=[]
        for i in range(len(list(seqs[vr].keys())[0])):
            if parvrs:
                name.append(str(parvrs[vr][1]+i))
                mut[name[i]]=0
            elif len(seqs)>1:
                name.append(vr+'-'+str(i+1))
            else:
                name.append(str(i+1))
            temp[name[i]]=defaultdict(int)
        for seq in seqs[vr]:
            total+=seqs[vr][seq]
            for i in range(len(seq)):
                temp[name[i]][seq[i]]+=seqs[vr][seq]
                if parvrs and seq[i]!=parvrs[vr][0][i]:
                    mut[name[i]]+=seqs[vr][seq]
        for n in temp:
            aadist[n]={k:0 for k in aa}
            for m in temp[n]:
                aadist[n][m]=temp[n][m]/total
        for n in mut:
            mutdist[n]=mut[n]/total*100
    if fname and aadist:
        csv_write(fname+'_aad.csv',None,aadist,[k for k in aa],'Amino acid distribution was',r)
        if parvrs and mutdist:
            csv_write(fname+'_md.csv',None,mutdist,'Position,% mutant','Mutation distribution was',r)
    return aadist,mutdist

def aln2seq(fn,type,full,ref):
    fail=''
    seq={}
    if ref:
        ref,fail=getfasta(ref,type,type,False)
        if fail:
            return seq,fail
        ref=list(ref.values())[0]
    with open(fn,'r') as f:
        x=f.read().strip().split('\n')
    x=[k for k in x if k]
    for i in range(len(x)):
        if x[i].replace(' ','').isdigit():
            q=x[i].split()
            break
    else:
        fail+='\n  File format not recognized!'
    q=[int(k) for k in q]
    x=x[i+1:]
    if not x or '.' in x[0]:
        fail+='\n  No reference sequence!'
    else:
        w=x[0].split()[1:]
        wt=x[0].split()[0]
    x=x[1:]
    if len(q)!=len(w):
        fail+='\n  Number of indices is different from number of regions!'
    if not x:
        fail+='\n  No sequence found!'
    for n in x:
        l=n.split()
        y=l[0]
        z=l[1:]
        if y in seq:
            fail+='\n  Duplicate sequence name '+y+' found in file '+fn+'! All sequences must have a different name!'
        if len(z)!=len(w):
            fail+='\n  Number of regions of sequence '+y+' is different from that of reference!'
            continue
        for i in range(len(z)):
            t=''
            for j in range(len(z[i])):
                if z[i][j]=='.':
                    t+=w[i][j]
                else:
                    t+=z[i][j]
            z[i]=t
        if full and ref:
            t=ref[:q[0]]
            for i in range(len(q)):
                t+=z[i]
                if i==len(q)-1:
                    a=len(ref)
                else:
                    a=q[i+1]
                t+=ref[q[i]+len(z[i]):a]
            z=t
        else:
            z=','.join(z)
        if type==aa:
            z=z.upper()
        else:
            z=z.lower()
        t,req=check_seq(z.replace(',',''),type,type)
        if not t:
            fail+='\n  Sequence '+y+' in '+fn+' contains invalid characters!'
        if not req:
            fail+='\n  Sequence '+y+' in '+fn+' does not contain expected characters!'
        if y and not fail:
            seq[y]=z
    return seq,fail,wt

def check_file(filename,strict):
    try:
        f=open(filename,'r')
    except IOError:
        if strict:
            print("\n  File "+filename+" could not be found!\n")
            sys.exit()
        else:
            return False
    else:
        return True

def check_plot_format(x):
    format=''
    y=('svg','png','jpg','jpeg','pdf','ps','eps','pgf','raw','rgba','tif','tiff')
    if x not in ('Single multipage pdf',)+y:
        print("\n  File format not recognized. Options are: "+', '.join(y)+" (or single multipage pdf file with no -f argument).\n")
        sys.exit()
    if len(x)<5:
        format=x
    return format

def check_read_file(x):
    fail=''
    if check_file(x,False):
        f=rfile_open(x)
        for i in range(5):
            y=f.readline().strip()
            if y:
                break
        if y and y[0] in ('@','>'):
            y=f.readline().strip().lower()
            t,req=check_seq(y,'atgc'+ambiguous,'atgc')
            if not t:
                fail+='\n  File '+x+' contains invalid characters!'
            if not req:
                fail+='\n  File '+x+' does not contain expected characters!'
        else:
            fail+='\n  File '+x+' has incorrect format!'
        f.close()
    else:
        fail+='\n  File '+x+' not found!'
    return fail

def check_seq(seq,type,required):
    t=True
    req=False
    seq=seq.lower()
    type=type.lower()
    required=required.lower()
    for i in seq:
        if i not in type:
            t=False
            break
        if i in required:
            req=True
    return t,req

def check_sync(l1,l2):
    fail=''
    if l1[0] not in ('@','>') or l2[0] not in ('@','>'):
        fail='\n  Wrong read file format! Only fastq, gzipped fastq or fasta are accepted formats!'
    elif l1[:l1.find(' ')]!=l2[:l2.find(' ')]:
        fail='\n  R1 and R2 reads are not synchronized! Please use raw read files!'
    return fail

def complexity(seq):
    i=0
    t=[]
    while i+3<=len(seq):
        t.append(defaultdict(int))
        x=seq[i:i+3]
        i+=3
        c=[[],[],[]]
        for n in range(3):
            if x[n] in ambiguous:
                for m in IUPAC[ambiguous.index(x[n])]:
                    c[n].append(m)
            else:
                c[n].append(x[n])
        for n1 in c[0]:
            for n2 in c[1]:
                for n3 in c[2]:
                    t[-1][gcode[n1+n2+n3]]+=1
    return t

def compress(seq):
    x=''
    for n in seq:
        if x and n in 'atgc' and n==x[-1]:
            continue
        x+=n
    return x

def conf_start(title):
    content='=== '+title.upper()+' CONFIGURATION FILE ===\n\n'
    x=dirname()
    y=find_read_files()
    return content,x,y

def conf_end(fname,content,title):
    with open(fname,'w') as f:
        f.write(content+'\n=== END OF CONFIGURATION FILE ===\n')
    print('\n  Edit the file '+fname+' before running '+title+' again (without arguments)!\n\n')

def csv_read(fname,dic,header):
    with open(fname,'r') as f:
        x=f.read().strip().split('\n')
    x=[n.split(',') for n in x if n]
    if header:
        header=x[0]
        x=x[1:]
    y=[None]*min([len(x[i]) for i in range(len(x))])
    for i in range(min(100,len(x))):
        for j in range(1,len(y)+1):
            z=intorfloat(x[i][-j])
            if z==y[j-1]:
                continue
            if not y[j-1] or z=='other' or (z=='float' and y[j-1]=='int'):
                y[j-1]=z
    for n in ('int','float'):
        q=int
        if n=='float':
            q=float
        z=[-i-1 for i in range(len(y)) if y[i]==n]
        for i in z:
            for j in range(len(x)):
                x[j][i]=q(x[j][i])
    if dic and len(x[0])>1:
        x={n[0]:n[1:] for n in x}
    return header,x

def csv_write(fname,keys,listordict,header,descr,r):
    content=''
    if isinstance(listordict,dict):
        if not keys:
            keys=list(listordict.keys())
        x=list(listordict.values())[0]
    else:
        x=listordict[0]
    if isinstance(x,list) or isinstance(x,tuple) or isinstance(x,dict):
        x=len(x)
        if keys: x+=1
    else:
        x=str(x).count(',')+2
    if header:
        if isinstance(header,list) or isinstance(header,tuple):
            y=','.join(header)
        else:
            y=header
            header=header.split(',')
        if y.count(',')+1==x-1:
            y=','+y
        content+=str(y)+'\n'
    for i in range(len(listordict)):
        a=''
        if keys:
            if i>=len(keys):
                break
            a=keys[i]
        if isinstance(listordict,dict):
            x=listordict[a]
        else:
            x=listordict[i]
        if isinstance(x,list) or isinstance(x,tuple):
            b=','.join([str(k) if k!=None else '' for k in x])
        elif isinstance(x,dict):
            b=','.join([str(x[k]) if x[k]!=None else '' for k in header])
        else:
            b=str(x)
        if a: a=str(a)+','
        content+=a+b+'\n'
    with open(fname,'w') as f:
        f.write(content)
    if descr:
        pr2(r,'\n  '+descr+' saved into file: '+fname)

def detect_vr(libnt,mindist):
    vrs={}
    a=0
    vr=''
    for n in range(0,len(libnt),3):
        x=libnt[n:n+3]
        amb=any([i not in 'atgc' for i in x])
        if amb and vr:
            vr+=libnt[a:n+3]
            a=n+3
        if vr and (n+len(x)>=len(libnt) or (not amb and n+3-a>mindist)):
            rprobe=''
            if a<len(libnt):
                rprobe=libnt[a:a+15]
                x=[i for i in rprobe if i not in 'atgc']
                if x:
                    rprobe=rprobe[:rprobe.find(x[0])]
            vrs['VR'+str(len(vrs)+1)]=[lprobe,vr,rprobe]
            vr=''
            continue
        if not vr and amb:
            vr=x
            lprobe=libnt[max(0,n-15,a):n]
            a=n+3
    return vrs

def diff(seqs):
    z=len(seqs[0])
    x=[(seqs[i],seqs[j]) for i in range(len(seqs)) for j in range(i+1, len(seqs))]
    for (a,b) in x:
        y=0
        for i in range(len(a)):
            if a[i]!=b[i]:
                y+=1
        z=min(z,y)
    return z

def dirname():
    x=os.getcwd()
    for n in ('\\','/'):
        if n in x:
            x=x[x.rfind(n)+1:]
    return x

def entropy(matrix):
    score=0
    for n in matrix:
        H=0
        for m in n:
            if m!=0:
                H+=m*(math.log(m,2))
        H*=-1
        score+=H
    return score

def exprange(a,b,c):
    while a<b:
        yield a
        a*=c

def find_ambiguous(x):
    y={}
    for i in range(len(x)):
        if x[i] not in 'atgc' and (i==0 or x[i-1] in 'atgc'):
            j=1
            while i+j<len(x) and x[i+j] not in 'atgc':
                j+=1
            y[i]=j
    return y

def find_read_files():
    rfiles=glob('*.f*.gz')
    if not rfiles:
        rfiles=glob('*.f*a')+glob('*.f*q')
    if not rfiles:
        return {}
    x=defaultdict(int)
    for n in rfiles:
        for m in ('_R1','_R2','_1.','_2.'):
            if m in n:
                x[m]+=1
    for (a,b) in (('_R1','_R2'),('_1.','_2.')):
        if x[a]>0 and x[a]==x[b]:
            break
    else:
        a,b='',''
    y=[n.replace(a,'*') for n in rfiles if a and a in n]+[n for n in rfiles if (a not in n and b not in n) or not a]
    z=prefix(y)
    for i in range(len(y)):
        x=y[i]
        if a and '*' in x:
            x=y[i].replace('*',a)+' '+y[i].replace('*',b)
        y[i]=z[i]+' '+x
    return sortfiles(y,' ')

def findall(probe,seq,start,end,overlap=False):
    i=seq.find(probe,start,end)
    while i!=-1:
        yield i
        if overlap:
            i+=1
        else:
            i+=len(probe)
        i=seq.find(probe,i,end)

def format_dna(seq,margin,cpl,cpn):
    x=len(str(len(seq)))
    if cpn<=x:
        cpn=x+1
    c=0
    t=''
    m=' '*margin
    i=0
    while c<len(seq):
        t+=m
        while i+cpn<=cpl and c+i+cpn<=len(seq):
            x=cpn+i
            i+=cpn
            if x>=cpn or x>=len(str(c+i)):
                t+=str(c+i).rjust(min(cpn,x))
            else:
                t+=' '*x
        t+='\n'+m+seq[c:c+cpl]+'\n'
        c+=cpl
        i=-(c%cpn)
    return t

def frame(seq,strict=False):
    trans={}
    stop={}
    for i in range(3):
        trans[i]=transl(seq[i:3*(len(seq[i:])//3)+i])
        if seq.startswith('atg') and len(seq)%3==0 and not '*' in trans[i][:-1]: return 0
        if '*' in trans[i]:
            stop[i]=trans[i].find('*')
        elif seq.startswith('atg') and len(seq)%3==0:
            return 0
    if len(stop)==2: return [i for i in trans if not i in stop][0]
    if len(stop)==3 and not strict:
        x=[i for i in stop if stop[i]==max(stop.values())]
        if len(x)==1 and stop[x[0]]>=len(seq)/3*.9:
            return x[0]
    else:
        return None

def fsize(filename):
    return os.path.getsize(filename)

def getfasta(fn,type,required,multi):
    fail=''
    seq={}
    if not check_file(fn,False):
        fail+='\n  File '+fn+' could not be found!'
        return seq,fail
    with open(fn,'r') as f:
        x=f.read().strip()
    if x[0]!='>':
        fail+='\n  '+fn+' is not a fasta file!'
        return seq,fail
    if not multi and x.count('>')>1:
        fail+='\n  File '+fn+' contains more than one sequence!'
        return seq,fail
    x=x.split('>')
    for n in x:
        if not n:
            continue
        y=n[:n.find('\n')]+' '
        y=y[:y.find(' ')]
        if not y:
            fail+='\n  Sequence with no name found in file '+fn+'! All sequences must have a name!'
        z=n[n.find('\n'):]
        if y in seq:
            fail+='\n  Duplicate sequence name '+y+' found in file '+fn+'! All sequences must have a different name!'
        z=z.replace(' ','').replace('\n','')
        if type==aa:
            z=z.upper()
        else:
            z=z.lower()
        t,req=check_seq(z,type,required)
        if not t:
            fail+='\n  Sequence '+y+' in '+fn+' contains invalid characters!'
        if not req:
            fail+='\n  Sequence '+y+' in '+fn+' does not contain expected characters!'
        if y and not fail:
            seq[y]=z
    return seq,fail

def getread(f,y,counter):
    name=''
    seq=''
    if not y:
        while True:
            l=f.readline().strip()
            if not l:
                l=f.readline().strip()
            if l[0]=='>':
                name=l
            if not l or (seq and l[0]=='>'):
                break
            if not seq and l[0]=='>':
                continue
            seq+=l.lower()
    else:
        z=0
        while z<y:
            l=f.readline().strip()
            if not z:
                name=l
            if z==1:
                seq=l.lower()
            z+=1
    if seq:
        counter+=1
    return seq,f,counter,name

def initreadfile(rfile):
    f=rfile_open(rfile)
    l=f.readline().strip()
    if not l or l[0] not in ('>','@'):
        f.close()
        print('  '+rfile+' does not look like a fastq or fasta file.\n')
        sys.exit()
    if l[0]=='>':
        l=f.readline().strip()
        l=f.readline().strip()
        if l and l[0]=='>':
            y=2
        else:
            y=0
    else:
        y=4
    f.seek(0)
    return f,y

def intorfloat(x):
    try:
        float(x)
        try:
            int(x)
            return 'int'
        except ValueError:
            return 'float'
    except ValueError:
        return 'other'

def match(text1, text2):
    if len(text1)==len(text2):
        for l in range(len(text1)):
            if not nt_match(text1[l], text2[l]):
                return False
        return True
    else:
        return False

def mean(x):
    return sum(x)/len(x)
    
def mut_per_read(seqs,parseq,fname,r):
    mut=defaultdict(int)
    parseq=''.join(parseq)
    for n in seqs:
        x=0
        m=''.join(n)
        for i in range(len(m)):
            if m[i]!=parseq[i]:
                x+=1
        mut[x]+=seqs[n]
    if fname:
        csv_write(fname,sorted(mut),mut,'Number of mutations,Number of reads','Mutation number distribution was',r)
    return mut

def nt_match(nt1, nt2):
    if nt1==nt2:
        return True
    elif (nt2 in ambiguous and nt1 in IUPAC[ambiguous.index(nt2)]) or (nt1 in ambiguous and nt2 in IUPAC[ambiguous.index(nt1)]):
        return True
    elif nt1 in ambiguous and nt2 in ambiguous and (not IUPAC[ambiguous.index(nt2)]-IUPAC[ambiguous.index(nt1)] or not IUPAC[ambiguous.index(nt1)]-IUPAC[ambiguous.index(nt2)]):
        return True
    else:
        return False

def plot_end(fig,name,format,mppdf):
    fig.subplots_adjust(bottom=0.15)
    fig.tight_layout()
    if format:
        g=name+'.'+format
        plt.savefig(g,dpi=600)
        print('  Figure was saved into file: '+g+'\n')
    else:
        mppdf.savefig()
    plt.close()

def plot_start(x,y,z):
    colors=plt.get_cmap(x,y)
    fig=plt.figure(figsize=(12,6.75))
    plt.title(z,size=15,weight='roman')
    return colors,fig

def pr2(f,t):
    print(t)
    if f:
        f.write(t+'\n')

def prefix(y):
    z=[0]*len(y)
    while True:
        for i in range(len(y)):
            x=len(y[i])
            for n in ('-','_','.','*'):
                p=y[i].find(n,z[i]+1)
                if p>0 and p<x:
                    x=p
            z[i]=x
        if len(set([y[i][:z[i]] for i in range(len(y))]))==len(set(y)): break
    return [y[i][:z[i]] for i in range(len(y))]

def prod(x):
    p=1
    for n in x:
        p*=n
    return p

def progress_check(c,show,t):
    if c in show:
        k=show[c]
        print('\r  '+t+' '*(8-len(k))+k+'%',end='')

def progress_end():
    print('\b\b\b\b\b\b100.0%\n')

def progress_start(nr,t):
    y=np.arange(0,nr,nr/1000)
    x=[round(n) for n in y]
    z=np.arange(0,100,0.1)
    y=[str(round(n,1)) for n in z]
    show=dict(zip(x,y))
    print('  '+t+'     0.0%',end='')
    return show

def readcount(R):
    if R[-3:]=='.gz':
        f=gzip.open(R,'r')
    else:
        f=open(R,'rb')
    if R[-1].lower()=='a' or R[-4:].lower()=='a.gz':
        nr=xcount(f,'>')
    else:
        nr=xcount(f,'\n')//4
    f.close()
    return nr

def rename(name):
    if glob(name) and fsize(name):
        t=str(time.time())
        n=name[:name.rfind('.')]+'-'+t[:t.find('.')]+name[name.rfind('.'):]
        os.rename(name,n)
        print('\n  Existing '+name+' file was renamed as '+n+'\n  Creating new '+name+' file...')

def revcomp(seq):
    rs=(seq[::-1]).lower()
    x=''.join([bpairs.get(rs[i], 'X') for i in range(len(seq))])
    return x

def rfile_create(x):
    if x[-2:]=='gz':
        f=gzip.open(x,'wb')
    else:
        f=open(x,'w')
    return f

def rfile_open(x):
    if x[-2:]=='gz':
        f=gzip.open(x,'rt')
    else:
        f=open(x,'r')
    return f

def seq_clust_card_dist(seqs,fname,r):
    if isinstance(seqs,dict):
        seqs=[seqs[k] for k in seqs]
    total=sum(seqs)    
    x=Counter(seqs)
    sccd={k:x[k]/total for k in x}
    if fname:
        csv_write(fname,sorted(sccd),sccd,'Sequence cluster cardinality,Fraction of distinct sequences','Sequence cluster cardinality distribution was',r)
    return sccd

def seq_write(fname,top,seqs,dic,descr,r):
    content=''
    if top:
        content+=str(top)+'\n'
    if not seqs:
        seqs=sorted(dic,key=dic.get,reverse=True)
    for seq in seqs:
        x=str(seq).replace(' ','').replace('(','').replace(')','').replace("'","")
        if dic:
            x+='\t'+str(dic[seq])
        content+=x+'\n'
    with open(fname,'w') as f:
        f.write(content)
    if descr:
        pr2(r,'  '+descr+' saved into file: '+fname)

def shortest_probe(seqs,lim,host,t):
    if lim<1:
        lim=1
    fail=''
    q=-1
    x=min([len(k) for k in seqs])
    y=set([k[-x:] for k in seqs])
    if len(y)!=len(seqs):
        fail='\n  Duplicate '+t+' found! '+t[0].upper()+t[1:]+'s must all be different when trimmed to their maximal common size!'
    if host and len([k for k in y if k in host+host[:x-1]]):
        fail+='\n  '+t[0].upper()+t[1:]+' found in the host genome!'
    if not fail:
        q=lim
        while True:
            y=set([k[-q:] for k in seqs])
            if len(y)==len(seqs) and max([k.count(p) for k in seqs for p in y])==1 and not len([k for k in y if k in host+host[:q-1]]):
                break
            q+=1
    return q,fail

def size_dist(seqs,fname,r):
    sd=defaultdict(int)
    for n in seqs:
        sd[len(n)]+=seqs[n]
    keys=sorted(sd,key=sd.get,reverse=True)
    if fname:
        csv_write(fname,keys,sd,'Length (nt),Number of reads','Sequence length distribution was',r)
    return keys,sd

def sortfiles(x,str):
    x.sort()
    if not str:
        str='.'
    y=[k for k in x if not any(i.isdigit() for i in k[:k.rfind(str)])]
    x=[k for k in x if not k in y]
    z=[(int(''.join([n for n in k if n.isdigit()])),k) for k in x]
    for n in sorted(z):
        y.append(n[1])
    return y

def transl(seq):
    seq=seq.lower()
    x=''.join([gcode.get(seq[3*i:3*i+3],'X') for i in range(len(seq)//3)])
    return x

def xcount(f,x):
    def _make_gen(reader):
        b=reader(1024*1024)
        while b:
            yield b
            b=reader(1024*1024)
    f_gen=_make_gen(f.read)
    return sum(buf.count(bytes(x,'utf-8')) for buf in f_gen)

if  script in sys.argv and any(k in sys.argv for k in ('-v','--version','-h','--help')):
    print('\n  Project: '+script+'\n  Description: a library of Python functions for bioinformatics\n  Version: '+__version__+'\n  Latest update: '+last_update+'\n  Author: '+author+'\n  License: '+license+'\n  Documentation: '+docs+'\n')
