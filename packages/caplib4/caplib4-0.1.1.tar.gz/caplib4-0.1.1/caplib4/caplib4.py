#!/usr/bin/env python
__version__='0.1.1'
last_update='2023-05-16'
author='Damien Marsic, damien.marsic@aliyun.com'
license='GNU General Public v3 (GPLv3)'

import dmbiolib as dbl
import argparse,sys,os
from glob import glob
from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

script=os.path.basename(__file__).split('.')[0]

def main():
    parser=argparse.ArgumentParser(description="Data analysis of protein combinatorial libraries and directed evolution experiments. For full documentation, visit: https://"+script+".readthedocs.io")
    parser.add_argument('-v','--version',nargs=0,action=override(version),help="Display version")
    subparser=parser.add_subparsers(dest='command',required=True)
    parser_a=subparser.add_parser('extract',help="Extract relevant data from read files")
    parser_a.add_argument('-b','--boundaries',default=False,action='store_true',help="Create new configuration file for data extraction using boundaries. Any existing configuration file with the same name will be renamed.")
    parser_a.add_argument('-p','--pattern',default=False,action='store_true',help="Create new configuration file for data extraction using patterns. Any existing configuration file with the same name will be renamed.")
    parser_a.add_argument('-l','--lib_file',type=str,default='',help="File containing the library nucleotide sequence (fasta format only). This option will create a new configuration file into which variable regions will be determined automatically from the library sequence.")
    parser_a.add_argument('-r','--read_files',type=str,help="File(s) containing the sequencing reads, format: gzipped or uncompressed fasta or fastq, using wildcards or partial name. Always use quotes when using wildcards or path (ex. '*.fq.gz' or 'directory/sample?.fastq'). Default: auto-detect.")
    args=parser.parse_args()
    if args.command=='extract':
        extract(args)

def extract(args):
    cf='extract.conf'
    ### Check arguments ###
    print('\n  Checking arguments...      ',end='')
    fail=''
    if args.lib_file:
        lf=glob(args.lib_file)
        if len(lf)==1:
            _,fail=dbl.getfasta(lf[0],'atgc'+dbl.ambiguous,dbl.ambiguous,False)
        elif len(lf)>1:
            fail+='\n  More than one possible library file!'
        else:
            fail+='\n  Library file '+args.lib_file+' could not be found!'
    if args.read_files:
        rf=glob(args.read_files+'*')
        for n in rf:
            fail+=dbl.check_read_file(n)
        args.read_files=rf
    if args.lib_file and args.boundaries:
        fail+='\n  A library file can only be used with pattern type data extraction!'
    if args.pattern and args.boundaries:
        fail+='\n  Patterns and boundaries can not be combined!'
        ### Create configuration file if needed ###
    if not args.pattern and not args.boundaries and not args.lib_file and not dbl.check_file(cf,False):
        fa=(k for k in glob('*.f*a') if dbl.fsize(k)<100000)
        lf=[]   
        for n in fa:
            _,z=dbl.getfasta(n,'atgc'+dbl.ambiguous,dbl.ambiguous,False)
            if not z: lf.append(n)
        if len(lf)==1: args.lib_file=lf[0]
    if args.lib_file: args.pattern=True
    if args.boundaries or args.pattern: dbl.rename(cf); extractconf(args); return
    if not args.boundaries and not args.pattern and not dbl.check_file(cf,False):
        fail+='\n  No configuration file was found. Please run '+script+' extract with the -b, -p or -l argument !'
    if fail:
        print('\n'+fail+'\n')
        sys.exit()
    ### Process configuration file ###
    print('OK\n\n  Checking configuration...  ',end='')
    conf,headfoot=conf_read(cf)
    proj,fail,conf=conf_extract(conf,'PROJECT NAME',True,fail,None,None)
    mode,fail,conf=conf_extract(conf,'MODE',True,fail,'char_p_b',None)
    libnt=parvrs=None
    if mode=='p':
        libnt,fail,conf=conf_extract(conf,'LIBRARY',True,fail,'file_amb',None)
        mindist,fail,conf=conf_extract(conf,'MINIMUM DISTANCE',True,fail,'int_1_100',25)
        strict,fail,conf=conf_extract(conf,'STRICT MATCH',True,fail,'bool',None)
        allow,fail,conf=conf_extract(conf,'ALLOW PARENTAL SEQUENCES',True,fail,'bool',None)
    parnt,fail,conf=conf_extract(conf,'PARENT',True,fail,'file_nt',None)
    sim,fail,conf=conf_extract(conf,'SAVE INCOMPLETE MATCHES',True,fail,'bool',None)
    if libnt:
        libnt,q=dbl.getfasta(libnt,'atgc'+dbl.ambiguous,dbl.ambiguous,False)
        if q: fail+=q; libnt=''
        else: libnt=list(libnt.values())[0]
    if parnt:
        parnt,q=dbl.getfasta(parnt,'atgc','atgc',False)
        if q: fail+=q; parnt=''
        else: parnt=list(parnt.values())[0]
        pf=dbl.frame(parnt,False)
        if pf==None:
            pf=0
        parnt=parnt[pf:]
    if parnt and libnt:
        i=0
        j=7
        while i<len(libnt):
            x=dbl.findall(libnt[i:i+j],parnt,0,None)
            if len(x)==1:
                x=x[0]
                break
            if not x:
                i+=1
                continue
            if len(x)>1:
                j+=1
                continue
        else:
            fail+='\n  Parental sequence does not match library sequence!'
            parnt=''
        if parnt and x-i<0:
            libnt=libnt[i-x:]
        elif parnt and x-i>0:
            libnt=libnt[(3-(x-i)%3)%3:]
    if not parnt and libnt:
        lf=dbl.frame(libnt,False)
        if lf==None:
            lf=0
        libnt=libnt[lf:]
    if parnt and libnt and allow:
        i=7
        while x+i<len(parnt):
            y=dbl.findall(parnt[x:x+7],libnt,0,None)
            if len(y)==1:
                y=y[0]
                break
            i+=1
        for i in range(len(libnt)):
            if libnt[i] in 'atgc' and libnt[i]!=parnt[x-y+i]:
                libnt[i]=dbl.ambiguous[dbl.IUPAC.index(set((libnt[i],parnt[x-y+i])))]
    vrs,fail,conf=conf_extract(conf,'VARIABLE REGIONS',False,fail,None,None)
    if vrs and not mode:
        mode='b' if len(list(vrs.values())[0])==2 else 'p'
    if libnt:
        vrs=dbl.detect_vr(libnt,mindist)
    for n in vrs:
        if (mode=='b' and len(vrs[n])==2) or (mode=='p' and len(vrs[n])==3):
            vrs[n][0],fail,_=conf_check(vrs[n][0],'nt',None,fail,None,None)
            if mode=='p': vrs[n][1],fail,_=conf_check(vrs[n][1],'amb',None,fail,None,None)
            vrs[n][-1],fail,_=conf_check(vrs[n][-1],'nt',None,fail,None,None)
        elif mode=='p' and len(vrs[n])==1:
            y,fail,_=conf_check(vrs[n][0],'amb',None,fail,None,None)
            if parnt:
                z=''
                for m in y:
                    if m in dbl.ambiguous: break
                    z+=m
                vrs[n][0]=z
                for j in range(1,len(y)-len(z)):
                    if y[-j] in dbl.ambiguous: break
                vrs[n].append(y[len(z):-j+1])
                if j>1:
                    vrs[n].append(y[-j+1:])
                else:
                    vrs[n].append('')
                if not z or j==1:
                    fail+='\n  Boundary sequences must not contain ambiguous nucleotides!'
            else:
                fail+='\n  boundary sequences can not be designed. Parental sequence is missing!' 
        else:
            fail+='\n  Wrong variable region format!'
            break
        if parnt:
            if mode=='p':
                parvrs={}
            x=list(dbl.findall(vrs[n][0],parnt,0,None))
            y=list(dbl.findall(vrs[n][-1],parnt,0,None))
            if mode=='b' and x and not y:
                z=dbl.revcomp(vrs[n][-1])
                y=list(dbl.findall(z,parnt,0,None))
                if y: vrs[n][-1]=z
            if mode=='p' and not x:
                for j in range(1,3):
                    x=list(dbl.findall(vrs[n][0][:-j],parnt,0,None))
                    if x:
                        vrs[n][0]=vrs[n][0][:-j]
                        vrs[n][1]=vrs[n][0][-j:]+vrs[n][1]
                        break
            if mode=='p' and x and not y:
                for j in range(1,3):
                    y=list(dbl.findall(vrs[n][-1][j:],parnt,0,None))
                    if y:
                        vrs[n][-1]=vrs[n][-1][j:]
                        vrs[n][1]=vrs[n][1]+vrs[n][-1][:j]
                        break
            if not x:
                fail+='\n  Left probe '+vr[n][0]+' not found in parent sequence!'
            if not y:
                fail+='\n  Right probe '+vr[n][-1]+' not found in parent sequence!'
            if len(x)>1 and mode=='b':
                fail+='\n  Too many matches for left probe '+vr[n][0]+' with parent sequence!'
            if len(y)>1 and mode=='b':
                fail+='\n  Too many matches for right probe '+vr[n][-1]+' with parent sequence!'
            if mode=='p' and x and y and (len(x)>1 or len(y)>1):
                z=[(k,l) for k in x for l in y if len(vrs[n][1])==l-k+len(vrs[n][0])]
                if not z:
                    fail+='\n  Variable region '+n+' could not be found in parent sequence!'
                elif len(z)>1:
                    fail+='\n  Too many matches for variable region '+n+' with parent sequence!'
                else:
                    x=[z[0][0]]
                    y=[z[0][1]]
            if len(x)==1:
                a=x[0]+len(vrs[n][0])
                z=a%3
                if z:
                    vrs[n][0]=vrs[n][0][:-z]
                    if mode=='p':
                        vrs[n][1]=vrs[n][0][-z:]+vrs[n][1]
            if len(y)==1:
                a=y[0]
                z=a%3
                if z:
                    vrs[n][-1]=vrs[n][-1][3-z:]
                    if mode=='p':
                        vrs[n][1]=vrs[n][1]+vrs[n][-1][:3-z]
            if mode=='p' and len(x)==1 and len(y)==1:
                z=x[0]+len(vrs[n][0])
                if y[0]-z==len(vrs[n][1]):
                    parvrs[n]=(dbl.transl(parnt[z:z+len(vrs[n][1])]),int(z/3)+1)
    if parvrs and len(parvrs)==len(vrs):
        z='\n'.join([k+'\t'+parvrs[k][0]+'\t'+str(parvrs[k][1]) for k in parvrs])+'\n'
        with open('parvrs.txt','w') as f:
            f.write(z)
    if vrs:
        z='\n'.join([k+'\t'+'\t'.join(vrs[k]) for k in vrs])
        conf=conf_push(z,conf,'VARIABLE REGIONS')
    else:
        fail+='\n  Variable region(s) missing!'
    rfiles,fail,conf=conf_extract(conf,'READ FILES',False,fail,None,None)
    rfiles,fail=conf_check_rfiles(rfiles,fail)
    if rfiles:
        z='\n'.join([k+'\t'+'\t'.join(rfiles[k]) for k in rfiles])
        conf=conf_push(z,conf,'READ FILES')
    extr,fail,_=conf_extract(conf,'EXTRACTION SETTINGS',False,fail,None,None)
    if extr:
        if set(rfiles)==set(extr):
            for n in rfiles:
                if len(extr[n])!=3:
                    fail+='\n  Wrong content for '+n
                    continue
                x,fail,_=conf_check(extr[n][0],'char_+_-_b_n',None,fail,None,None)
                if x=='n':
                    fail+='\n  No relevant sequence found in file '+rfiles[n][0]+'!'
                extr[n][1]=extr[n][1].replace('[','').replace(']','').split(',')
                x=[k for k in extr[n][1] if k not in vrs]
                if x:
                    fail+='\n  Not found in variable regions: '+', '.join(x)
                extr[n][2]=extr[n][2].replace('[','').replace(']','').split(',')
                for j in range(len(extr[n][2])):
                    extr[n][2][j],fail,_=conf_check(extr[n][2][j],'int',None,fail,None,None)
        else:
            fail+='\n  Prefixes must be the same in both READ FILES and EXTRACTION SETTINGS sections!'
    if fail:
        x,_=conf_read(cf)
        if x!=conf: conf_write(headfoot,conf,cf)
        print('\n'+fail+'\n')
        print('  Edit configuration file before running '+script+' extract again (without arguments)!\n')
        sys.exit()
    print('OK\n')
    if not extr:
        print('  Checking read files...     ',end='')
        extr,vrs=rfile_preprocess(rfiles,vrs)
        for n in extr:
            if extr[n][0]=='n': fail+='\n  No relevant sequence found in file '+rfiles[n][0]+'!'
        if len([extr[k][0] for k in extr if extr[k][0]!='n']):
            x={k:[extr[k][i] if not i else str(extr[k][i]).replace(' ','').replace("'",'') for i in range(3)] for k in extr}
            z='\n'.join([k+'\t'+'\t'.join(x[k]) for k in x])
            conf=conf_push(z,conf,'EXTRACTION SETTINGS: this section is generated automatically. Do not modify unless you know what you are doing!')
            z='\n'.join([k+'\t'+'\t'.join(vrs[k]) for k in vrs])
            conf=conf_push(z,conf,'VARIABLE REGIONS')
        x,_=conf_read(cf)
        if x!=conf: conf_write(headfoot,conf,cf)
        if fail:
            print('\n'+fail+'\n')
        print('  Edit configuration file before running '+script+' extract again (without arguments)!\n')
        sys.exit()
    ### Process read file(s) ###
    rn={}
    stats={}
    for n in rfiles:
        rn[n]=dbl.readcount(rfiles[n][0])
        x=[k for k in extr[n][1]]
        if len(x)>1:
            x+=['all']
        y=6
        if mode=='p' and strict:
            y+=1
        stats[n]={k:[0]*y for k in x}
    x='Wrong length'
    if mode=='b':
        x='Frameshift'
    stat_head=['Unmapped reads',x,'Reads with stop codons','% reads with stop codons']
    if mode=='p' and strict:
        stat_head.append('Invalid sequence')
    stat_head.extend(['More than 1 match','Extracted sequences','Complexity'])
    if mode=='b':
        stat_head.extend(['Most common length,Reads with that length'])
    stat_head.extend(['Number of reads with most common sequence','Number of reads with a single copy sequence'])
    if mode=='p' and parvrs:
        stat_head.extend(['Mutations per read','Parental sequence (%)'])
    rname=proj+'_extract_report.txt'
    dbl.rename(rname)
    r=open(rname,'w')
    x='pattern' if mode=='p' else 'boundaries'
    r.write('Project name: '+proj+'\nExtraction mode: '+x+'\nSave incomplete matches: '+str(sim)+'\n')
    if mode=='p':
        x='strict' if strict else 'loose'
        r.write('Pattern matching: '+x+'\n')
        if parvrs and strict:
            r.write('Allow parental sequence not strictly matching pattern: '+str(allow)+'\n')
    for rf in rfiles:
        r.write('\n--------------------------------------------------\nRead file prefix: '+rf+'\n')
        r.write('Read file(s): '+'\t'.join(rfiles[rf])+'\nNumber of reads / read pairs: '+str(rn[rf])+'\n\n')
        f2=None
        print()
        f,step=dbl.initreadfile(rfiles[rf][0])
        c=0
        distinct=[(1,1)]
        D=max(1,round(rn[rf]/5000))
        if len(rfiles[rf])==2:
            f2,step2=dbl.initreadfile(rfiles[rf][1])
        t='Processing reads from '+rf+'...'
        show=dbl.progress_start(rn[rf],t)
        seq={}
        seqs={}
        l2=''
        for n in extr[rf][1]:
            seq[n]=None
            seqs[n]=defaultdict(int)
        if len(seqs)>1:
            seqs['all']=defaultdict(int)   
        while True:
            l,f,c,name=dbl.getread(f,step,c)
            if not l:
                break
            if f2:
                l2,f2,_,name2=dbl.getread(f2,step2,0)
                x=dbl.check_sync(name,name2)
                if x:
                    print('\n'+x+'\n')
                    sys.exit()
            dbl.progress_check(c,show,t)
            read=[]
            if any(k==extr[rf][0] for k in ('+','b')):
                x=dbl.revcomp(l2)
                read.append(l+'n'+x)
            if any(k==extr[rf][0] for k in ('-','b')):
                x=dbl.revcomp(l)
                read.append(l2+'n'+x)
            low=0
            for k in range(len(extr[rf][1])):
                vr=extr[rf][1][k]
                M=[]
                x=extr[rf][2][k-1] if k else 0
                target=extr[rf][2][k]-x+low
                for j in range(len(read)):
                    match=match2=[]
                    for l in reversed(range(max(1,len(vrs[vr][0])-7))):
                        probe=vrs[vr][0][l:]
                        lp=len(probe)
                        if not lp: continue
                        x=list(dbl.findall(probe,read[j],round((target-lp)*0.85),round(target*1.15)))
                        if len(x)<=1: break
                    if x:
                        match=[(x[0]+lp,j,lp)]
                        low=x[0]+lp
                    else:
                        for l in range(max(1,len(vrs[vr][0])-7)):
                            probe=vrs[vr][0][l:]
                            lp=len(probe)
                            if not lp: break
                            x=list(dbl.findall(probe,read[j],low,None))
                            if x: break
                        if x:
                            match=[(m+lp,j,lp) for m in x]
                    if match:
                        probe=None
                        for l in range(max(1,len(vrs[vr][-1])-7)):
                            if not l:
                                probe=vrs[vr][-1]
                            else:
                                probe=vrs[vr][-1][:-l]
                            if not probe: break
                            x=list(dbl.findall(probe,read[j],low,None))
                            if x: break
                        if x:
                            match2=[(m,j,len(probe)) for m in x]
                    for x in match:
                        for y in match2:
                            if y[0]>x[0]:
                                M.append((x,y))
                if M:
                    M=[(x,y) for (x,y) in M if (mode=='p' and y[0]-x[0]==len(vrs[vr][1])) or (mode=='b' and ((y[0]-x[0])%3==0 or 'n' in read[x[1]][x[0]:y[0]]))]
                    if not M:
                        stats[rf][vr][1]+=1
                if M:
                    S=[]
                    for (x,y) in M:
                        z=read[x[1]][x[0]:y[0]]
                        if mode=='b' and 'n' in z:
                            a=z[:z.find('n')]
                            b=z[z.rfind('n')+1:]
                            z=a+(3-len(a+b)%3)*'n'+b
                        S.append(dbl.transl(z))
                    for j in reversed(range(len(M))):
                        if '*' in S[j]:
                            del S[j]
                            del M[j]
                    if not M:
                        stats[rf][vr][2]+=1
                if M and mode=='p' and strict:
                    for j in reversed(range(len(M))):
                        z=read[M[j][0][1]]
                        if not dbl.match(vrs[vr][1],z[M[j][0][0]:M[j][1][0]]):
                            if not parnt or not allow or dbl.transl(z[M[j][0][0]:M[j][1][0]])!=parvrs[vr][0]:
                                del S[j]
                                del M[j]
                    if not M:
                        stats[rf][vr][4]+=1
                if M:
                    if len(M)>1:
                        x=max([l[0][2]+l[1][2] for l in M])
                        M=[l for l in M if l[0][2]+l[1][2]==x]
                    if len(M)>1:
                        x=min([abs(extr[rf][2][k]-l[0][0]) for l in M])
                        M=[l for l in M if l[0][0]==x]
                    if len(M)>1:
                        x=max([m[0]-l[0] for (l,m) in M])
                        M=[(l,m) for (l,m) in M if m[0]-l[0]==x]
                    if len(M)==1:
                        if len(S)==1:
                            seq[vr]=S[0]
                        else:
                            x,y=M[0][0][0],M[0][1][0]
                            seq[vr]=dbl.transl(read[M[0][0][1]][x:y])
                        low=M[0][1][0]
                    else:
                        stats[rf][vr][-2]+=1
                if not M and not sim:
                    break
            if 'all' in seqs and not None in seq.values():
                seqs['all'][(k for k in seq.values())]+=1
                stats[rf]['all'][-1]+=1
                if stats[rf]['all'][-1]%D==0 and distinct[-1][1]!=len(seqs['all']):
                    distinct.append((stats[rf]['all'][-1],len(seqs['all'])))
            for n in seq:
                if seq[n]:
                    seqs[n][seq[n]]+=1
                    seq[n]=None
                    stats[rf][n][-1]+=1
                    if len(seqs)==1 and stats[rf][n][-1]%D==0 and distinct[-1][1]!=len(seqs[n]):
                        distinct.append((stats[rf][n][-1],len(seqs[n])))
        dbl.progress_end()
        f.close()
        f2 and f2.close()
        ### Process extracted data
        for n in seqs:
            x=stats[rf][n][-1]
            stats[rf][n][0]=rn[rf]-x-stats[rf][n][1]-stats[rf][n][2]-stats[rf][n][4]
            if mode=='p' and strict:
                stats[rf][n][0]-=stats[rf][n][5]
            if seqs[n]:
                stats[rf][n][3]=stats[rf][n][2]/(rn[rf]-stats[rf][n][0]-stats[rf][n][1])*100
            y=len(seqs[n])
            dbl.pr2(r,'  Variable region: '+n+'\n  Processed reads:   '+f'{rn[rf]:,}'.rjust(13)+'\n  Extracted reads:   '+f'{x:,}'.rjust(13)+'\n  Distinct sequences:'f'{y:,}'.rjust(13))
            if not y:
                continue
            fname=proj+'_'+rf+'_'+n
            dbl.seq_write(fname+'.cl4',str(x),None,seqs[n],'Extracted sequences were',r)
            if n=='all' or len(seqs)==1:
                csv_write(fname+'_us.csv',None,distinct,'Extracted reads,Unique sequences','Unique sequences vs extracted reads distribution was',r)
            stats[rf][n].append(y)
            if mode=='b' and n!='all':
                x,y=dbl.size_dist(seqs[n],fname+'_sd.csv',r)
                stats[rf][n].extend([x[0],y[x[0]]])
            x=list(seqs[n].values())
            stats[rf][n].extend([max(x),len([k for k in x if k==1])])
            _=dbl.seq_clust_card_dist(seqs[n],fname+'_cnd.csv',r)
            if mode=='p' and parvrs:
                y=stats[rf][n][-4]
                if n=='all':
                    z=[parvrs[k][0] for k in parvrs]
                else:
                    z=parvrs[n][0]
                x=dbl.mut_per_read(seqs[n],z,fname+'_mnd.csv',r)
                z=0
                for m in x:
                    z+=m*x[m]
                stats[rf][n].append(z/y)
                x=0
                if parvrs[n][0] in seqs[n]:
                    x=seqs[n][parvrs[n][0]]/y*100
                stats[rf][n].append(x)
        if mode=='p':
            _,_=dbl.aa_dist(seqs,parvrs,proj+'_'+rf,r)
    stat_head=['Read file prefix','Region','Reads']+stat_head
    if mode=='p':
        morestat=analyze_complexity(vrs,parvrs,proj,r)
        stats['Design']={k:[None]*len(stat_head) for k in morestat}
        for n in morestat:
            stats['Design'][n][3]=morestat[n][0]
            k=7 if strict else 6
            stats['Design'][n][k]=morestat[n][1]
            if parvrs:
                stats['Design'][n][-2]=morestat[n][2]
                stats['Design'][n][-1]=morestat[n][3]
    x=[]
    for n in stats:
        for m in stats[n]:
            y=rn[n] if n!='Design' else 0
            x.append([n,m,y]+stats[n][m])
    csv_write(proj+'_stats.csv',None,x,stat_head,'Stats were',r)
    r.close()
    print('\n  Report was saved into file: '+rname+'\n')







#############################################################
### high / low memory mode -> read whole read file to memory
### codon compiler compatibility
#  add shannon entropy (function + make csv) (+ add entropy score to stats table ?)
# add sequence alignment when mode==b + entropy + weblogo + aadist
# update frame (remove false) / update dmbiolib first


######################### ANALYSIS ########################################
# Read stats tables and all relevant files in the current or assigned directory
# Visualize complexity: 
        # one axis: distinct sequences (ordered by copy number startign with higher)
        # other axis: cumulative % of all reads (ex if 10%,3%,2% -> 10%, 13%, 15%)
        # true complexity should be when slope flattens


# Data extraction xy (if us.csv files)
# Data extraction barplot (cf cl3 data cleaning, only use columns if some content exists)
# Cluster cardinality (if cnd files)
# Size distribution (if sd files)
# Complexity barplot
# complexity xy (see above)
# Venn diagrams
# aa enrichment (if aad files)
# seqlogo of aa enrichment (if aad files)
# mutant position distribution (if md files)
# mutation number distribution (if mnd files)
# sequence frequency evolution (incl VR frequency evolution, if cl4 files)
# show top selected VRs (if more than 1 VR, enr factor + final frequency)  ???????????????????????????
# show top selected sequences (enr factor + final frequency + show VR score and aa score) ????????????
# show opt-vr and opt-aa + enr value for each vr / each aa
# Bubble plot with bubble surface=freq and bubble height=enr, color=variant, x=child (if more than 1 child)

# see DE5 paper for position scores combining multiple selection rounds (VARIANT command, including % in all samples et. see cl3 todo)



def analyze_complexity(vrs,parvrs,fname,r):
    content=''
    aadist={}
    mutdist={}
    stat={k:[] for k in vrs}
    if len(vrs)>1:
        stat['all']=[]
    total_nac=0
    for vr in vrs:
        t=dbl.complexity(vrs[vr][1])
        nac=0
        ac=af=sf=1
        name=['']*len(t)
        for k in t:
            if len(k)==1:
                continue
            nac+=1
            x=len(k)
            y=1
            q=sum(k.values())
            if '*' in k:
                x-=1
                y=(q-k['*'])/q
            ac*=x
            af*=y
        sf=(1-af)*100
        total_nac+=nac
        content+='\nVariable region name: '+vr+'\nVariable region sequence: '+vrs[vr][1]
        content+='\nExpected reads with stop codons: '+f'{sf:.2f}'+'%\nExpected amino acid complexity: '+f'{ac:,}'+'\n'
        x='Position  ' if parvrs else ''
        content+='Number of ambiguous codons: '+str(nac)+'\nDetailed codon analysis:\n  Index  '+x+'Codon  Stop%  #aa  Translation\n'
        stat[vr].extend([sf,ac])
        for i in range(len(t)):
            content+=str(i).rjust(7)
            if parvrs:
                content+=str(parvrs[vr][1]+i).rjust(10)
            content+=vrs[vr][1][i*3:3+i*3].center(9)
            x=len(t[i])
            y=0
            if '*' in t[i]:
                y=t[i]['*']
                x-=1
            q=sum(t[i].values())
            content+=f'{y/q*100:.2f}'+str(x).rjust(6)
            content+=' '.join([k+':'+str(t[i][k]) for k in t[i]])+'\n'
            if parvrs:
                name[i]=str(parvrs[vr][1]+i)
            elif len(vrs)>1:
                name[i]=vr+'-'+str(i+1)
            else:
                name[i]=str(i+1)
            aadist[name[i]]={k:t[i][k]/(q-y) if k in t[i] else 0 for k in dbl.aa}
            if parvrs:
                if parvrs[vr][0][i] not in t[i]:
                    mutdist[name[i]]=100
                else:
                    mutdist[name[i]]=(q-y-t[i][parvrs[vr][0][i]])/(q-y)*100
        if parvrs:
            stat[vr].append(sum([mutdist[name[k]] for k in range(len(t))])/100)
            stat[vr].append(dbl.prod((100-mutdist[name[k]])/100 for k in range(len(t))))
    if 'all' in stat:
        stat['all'].append((1-dbl.prod([1-stat[k][0]/100 for k in stat if k!='all']))*100)
        stat['all'].append(dbl.prod([stat[k][1] for k in stat if k!='all']))
        if parvrs:
            stat['all'].append(sum([stat[k][2] for k in stat if k!='all']))
            stat['all'].append((1-dbl.prod([1-stat[k][3]/100 for k in stat if k!='all']))*100)
    content='COMPLEXITY REPORT\nVariable regions: '+str(len(vrs))+'\nAmbiguous codons: '+str(total_nac)+'\n'+content
    with open(fname+'_complexity.txt','w') as f:
        f.write(content)
    print('  Complexity report was saved into file: '+fname+'_complexity.txt')
    csv_write(fname+'_design_aad.csv',None,aadist,[k for k in dbl.aa],'Theoretical amino acid distribution was',r)
    if parvrs:
        csv_write(fname+'_design_md.csv',None,mutdist,'Position,% mutant','Theoretical mutation distribution was',r)
    return stat

def extractconf(args):
    z=script+' '+args.command
    if args.read_files:
        content,dirname,_=dbl.conf_start(z)
        y=dbl.prefix(args.read_files)
        rfiles=[y[i]+'\t'+args.read_files[i] for i in range(len(y))]
    else:
        content,dirname,rfiles=dbl.conf_start(z)
    content+='# PROJECT NAME: to be used as prefix in output file names.\n\n'
    content+=dirname+'\n\n'
    content+='# MODE: pattern (p) or boundaries (b).\n\n'
    if args.pattern:
        content+='p\n\n'
        content+='# LIBRARY NUCLEOTIDE SEQUENCE FILE: if exists, will be used to automatically identify variable regions for pattern type data extraction.\n\n'
        content+=str(args.lib_file)+'\n\n'
        content+='# MINIMUM DISTANCE: (only applies if variable regions are determined automatically from the library sequence). Minimum distance in nt between variable regions (making it larger will decrease the number of variable regions).\n\n'
        content+='25\n\n'
    else:
        content+='b\n\n'
    content+='# PARENT NUCLEOTIDE SEQUENCE FILE: if exists, will be used to determine position numbers and reading frames of variable regions.\n\n'
    fa=[k for k in glob('*.f*a') if dbl.fsize(k)<100000]
    pf=[]
    for n in fa:
        _,fail=dbl.getfasta(n,'atgc','atgc',False)
        if not fail:
            pf.append(n)
    if len(pf)==1:
        content+=pf[0]+'\n\n'
    content+='# VARIABLE REGIONS'
    if args.pattern:
        content+=' (will be populated automatically if library sequence exists)'
    content+=': One variable region per line. Each line contains name,  '
    if args.pattern:
        content+='sequence pattern (including enough unambiguous nucleotides each side to be used as probes) (if single sequence, will be divided into 3 parts'
    else:
        content+='left boundary sequence, right boundary sequence (can be either strand, will be corrected if needed) (boundary sequences (if within parental sequence) will be codon-trimmed'
    content+=' automatically if parental sequence is present, otherwise the left boundary must end with a codon and the right boundary must start with a codon), separated by space or tab.\n\n'
    if args.lib_file:
        libnt,_=dbl.getfasta(args.lib_file,'atgc'+dbl.ambiguous,dbl.ambiguous,False)
        libnt=list(libnt.values())[0]
        lf=dbl.frame(libnt,False)
        if lf==None:
            lf=0
        libnt=libnt[lf:]
        vrs=dbl.detect_vr(libnt,25)
        content+='\n'.join([k+'\t'+('\t'.join(vrs[k])) for k in vrs])+'\n\n'
    content+='# SAVE INCOMPLETE MATCHES: in case of multiple variable regions, save all matches even if not all variable regions within reads are detected.\n\nTrue\n\n'
    if args.pattern:
        content+='# STRICT MATCH: only sequences with perfect match to the pattern will be saved (otherwise, all sequences will be saved as long as the probes match and the region has the correct length).\n\nFalse\n\n'
        content+='# ALLOW PARENTAL SEQUENCES: (only if parent sequence exists). Whether to allow parental sequences even if they don\'t match the pattern (as long as the length is the same).\n\nTrue\n\n'
    content+='# READ FILES: one read file or read file pair per line, preceded by a prefix (to be used in output file names) separated by a tab. Unmerged read files (with paired-end reads) are only accepted if they contain distinct variable regions (no overlap).\n\n'
    content+=('\n'.join(rfiles)).replace(' ','\t')+'\n\n'
    dbl.conf_end('extract.conf',content,z)

def rfile_preprocess(rfiles,vrs):
    extr={}
    for n in rfiles:
        extr[n]=['',[],[]]
        S=[0,0]
        D=defaultdict(list)
        g=None
        f,y1=dbl.initreadfile(rfiles[n][0])
        if len(rfiles[n])>1: g,y2=dbl.initreadfile(rfiles[n][1])
        c=0
        rb=defaultdict(lambda:[0,0])
        while c<200:
            x,f,c,n1=dbl.getread(f,y1,c)
            seq=(x,dbl.revcomp(x))
            if g:
                y,g,_,n2=dbl.getread(g,y2,0)
                fail=dbl.check_sync(n1,n2)
                if fail: print(fail+'\n'); sys.exit()
                seq=(seq[0]+'n'+dbl.revcomp(y),y+'n'+seq[1])
            s=[0,0]
            a=0
            for vr in vrs:
                M=[]
                match1=[]
                for i in (0,1):
                    x=list(dbl.findall(vrs[vr][0],seq[i],a,None))
                    if x:
                        match1.extend([(i,k+len(vrs[vr][0])) for k in x])
                if match1:
                    match2=[]
                    for i in (0,1):
                        x=list(dbl.findall(vrs[vr][-1],seq[i],a,None))
                        if x: match2.extend([(i,k) for k in x])
                    for m in match1:
                        for p in match2:
                            if (len(vrs[vr])==2 and p[1]>m[1]) or (len(vrs[vr])==3 and p[1]==m[1]+len(vrs[vr][1])):
                                M.append((m,p))
                if M:
                    a=M[0][0][1]
                if len(M)==1:
                    M=M[0]
                    s[M[0][0]]+=1
                    rb[vr][abs(M[0][0]-M[1][0])]+=1
                    D[vr].append(M[0][1])
            if s[0] and not s[1]: S[0]+=1
            elif s[1] and not s[0]: S[1]+=1
        f.close()
        g and g.close()
        extr[n][0]='b' if (S[0]>c/100 and S[1]>c/100) else '+' if (S[0]>max(c/100,10*S[1]) and S[1]<=c/100) else '-' if (S[0]<=c/100 and S[1]>max(c/100,10*S[0])) else 'n'
        D={k:round(dbl.mean(D[k])) for k in vrs if k in D and len(D[k])>c/100}
        extr[n][1]=list(D.keys())
        extr[n][2]=list(D.values())
        for vr in rb:
            if rb[vr][1]>max(c/100,2*rb[vr][0]):
                vrs[vr][-1]=dbl.revcomp(vrs[vr][-1])
    return extr,vrs




### move to dmbiolib when ready!



def conf_read(fname):
    with open(fname,'r') as f:
        x=f.read().strip()
    headfoot=[x[:x.find('#')],x.split('\n')[-1]]
    x=x[x.find('#'):].split('# ')[1:]
    conf={}
    for l in x:
        n=l.split('\n')
        if len(n)>1 and n[1].startswith('Instructions:'): n[0]+='\n'+n[1]; del n[1]
        m='\n'.join([k.strip().strip('\t') for k in n[1:] if k and not k.startswith('=')])
        conf[n[0]]=m
    return conf,headfoot

def conf_extract(conf,section,single,fail,type,default):
    x=[k for k in conf.keys() if k.lower().startswith(section.lower())]
    if len(x)>1: print('\n  Text "'+section+'" found more than once!'); sys.exit()
    var=conf[x[0]] if len(x) else ''
    if single and any([k in var for k in ('\n',' ','\t')]):
        fail+='\n  Single item expected in "'+section+'"!'
    if not single:
        var=var.replace('\n\n','\n').replace(', ',',').split('\n')
        var=[[k for k in n.split() if k] for n in var]
        var=[k for k in var if k]
        if len(set([k[0] for k in var]))!=len(var):
            fail+='\n  Duplicate item(s) found in "'+section+'"!'
        var=dict([(k[0],k[1:]) for k in var])
    if type: var,fail,conf=conf_check(var,type,default,fail,conf,section)
    return var,fail,conf

def conf_push(var,conf,section):
    x=[k for k in conf.keys() if k.lower().startswith(section.lower())]
    if len(x)>1: print('\n  Text "'+section+'" found more than once!'); sys.exit()
    var='' if var==None else str(var)
    if len(x)==1:
        conf[x[0]]=var
    else:
        conf[section]=var
    return conf

def conf_check(var,type,default,fail,conf,section):
    if var and type=='bool':
        if var[0].lower() in ('y','t',1):
            var=True
        elif var[0].lower() in ('n','f',0):
            var=False
        else:
            fail+='\n  Unknown setting: '+var
    elif var and type.startswith('int'):
        if dbl.intorfloat(var)=='int':
            var=int(var)
            if '_' in type:
                x=type.split('_')[1:]
                y=z=None
                w=''
                if dbl.intorfloat(x[0])=='int':
                    y=int(x[0])
                    w+=' no smaller than '+x[0]
                if len(x)>1 and dbl.intorfloat(x[1])=='int':
                    z=int(x[1])
                    w+=', no larger than '+x[1]
                if (y!=None and var<y) or (z!=None and var>z):
                    fail+='\n  Integer expected'+w+': '+str(var)
        else:
            fail+='\n  Integer expected: '+var
    elif var and type.startswith('float'):
        if intorfloat(var) in ('float','int'):
            var=float(var)
            if '_' in type:
                x=type.split('_')[1:]
                y=z=None
                w=''
                if dbl.intorfloat(x[0]) in ('float','int'):
                    y=float(x[0])
                    w+=' no smaller than '+x[0]
                if len(x)>1 and dbl.intorfloat(x[1]) in ('float','int'):
                    z=float(x[1])
                    w+=', no larger than '+x[1]
                if (y!=None and var<y) or (z!=None and var>z):
                    fail+='\n  Float expected'+w+': '+str(var)
        else:
            fail+='\n  Float expected: '+var
    elif var and type=='file':
        if not dbl.check_file(var,False):
            fail+='\n  File '+var+' could not be found!'
    elif var and type.startswith('file_'):
        w=type.split('_')
        x=''
        if w[1]=='aa':
            x=y=dbl.aa
        elif w[1]=='nt':
            x='atgc'+dbl.ambiguous
            y='atgc'
        elif w[1]=='amb':
            x='atgc'+dbl.ambiguous
            y=dbl.ambiguous
        if w[-1]=='multi':
            z=True
        else:
            z=False
        _,q=dbl.getfasta(var,x,y,z)
        fail+=q
    elif var and type=='rfile':
        fail+=dbl.check_read_file(var)
    elif var and type in ('aa','nt','amb'):
        if type=='aa':
            x=y=dbl.aa
            var=var.upper()
        elif type=='nt':
            x='atgc'+dbl.ambiguous
            y='atgc'
            var=var.lower()
        elif type=='amb':
            x='atgc'+dbl.ambiguous
            y=dbl.ambiguous
            var=var.lower()
        t,req=dbl.check_seq(var,x,y)
        if not t:
            fail+='\n  Sequence '+var+' contains invalid characters!'
        if not req:
            fail+='\n  Sequence '+var+' does not contain expected characters!'
    elif var and type.startswith('char_'):
        choice=type.lower().split('_')[1:]
        if not var:
            var=None
        elif var[0].lower() in choice:
            var=[k for k in choice if k==var[0].lower()][0]
        else:
            fail+='\n  Wrong content: '+var
    if var==None: var=default
    conf=conf_push(var,conf,section) if conf and section else None
    return var,fail,conf

def conf_write(headfoot,conf,fname):
    dbl.rename(fname)
    content=headfoot[0]
    for n in conf:
        content+='# '+n+'\n\n'+conf[n]+'\n\n'
    content+=headfoot[-1]
    with open(fname,'w') as f:
        f.write(content)
    print('  Configuration file was saved successfully.')

def conf_check_rfiles(rf,fail):
    rf=[[k]+rf[k] for k in rf]
    pre=True
    if not rf:
        fail+='\n  Read files are missing!'
        return {},fail
    for x in rf:
        fail+=dbl.check_read_file(x[-1])
        a=1
        if len(x)>1 and glob(x[-2]):
            fail+=dbl.check_read_file(x[-2])
            a=2
        if not x[:-a]:
            pre=False
        elif len(x[:-a])>1:
            fail+='\n  Multiple items found instead of prefix: '+x[:-a]
            return {},fail
    if not pre:
        y=dbl.prefix(rf)
        rf=[[y[i]]+rf[i] for i in range(len(rf))]
    rf=dict([(k[0],k[1:]) for k in rf])
    return rf,fail

def override(func):
    class OverrideAction(argparse.Action):
        def __call__(self,parser,namespace,values,option_string):
            func()
            parser.exit()
    return OverrideAction

def version():
    print('\n  Project: '+script+'\n  Version: '+__version__+'\n  Latest update: '+last_update+'\n  Author: '+author+'\n  License: '+license+'\n')

if __name__ == '__main__':
    main()
