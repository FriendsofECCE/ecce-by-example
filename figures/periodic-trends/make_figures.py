#!/usr/bin/env python3
"""Plots for chapters/periodic-trends.tex from the stored General Chemistry example outputs (ECCE repo).
Usage: python3 figures/periodic-trends/make_figures.py [ECCE repo root, default ~/tmp/ecce/ECCE]"""
import sys, os, re, math
LN={'s':0,'p':1,'d':2,'f':3}
def parse(fn):
    L=open(fn).read().splitlines()
    h={}; aol=[]; orbs={}; coefs={}
    i=0
    while i<len(L):
        l=L[i]
        if l.startswith('begin ao_labels'):
            i+=1
            while not L[i].startswith('end'):
                lab=L[i].split()[2]; aol.append(re.sub(r'^\d+','',lab)[0]); i+=1
        elif l.startswith('begin orbitals'):
            k=l.split()[2]; orbs[k]=[]; i+=1
            while not L[i].startswith('end'):
                p=L[i].split(); orbs[k].append((float(p[1]),float(p[2]))); i+=1
        elif l.startswith('begin mo_coefficients'):
            k=l.split()[2]; coefs[k]=[]; i+=1
            while not L[i].startswith('end'):
                p=L[i].split(); coefs[k].append([float(x) for x in p[1:]]); i+=1
        elif l.startswith('begin'):
            while not L[i].startswith('end'): i+=1
        elif not l.startswith('progress') and not l.startswith('#') and l.strip():
            p=l.split(None,1); h[p[0]]=p[1] if len(p)>1 else ''
        i+=1
    out={}
    for k in orbs:
        labs=[]; cnt={'s':0,'p':0,'d':0,'f':0}
        for j,(e,o) in enumerate(orbs[k]):
            w={'s':0,'p':0,'d':0,'f':0}
            for c,a in zip(coefs[k][j],aol): w[a]+=c*c
            t=max(w,key=w.get)
            n={'s':cnt['s']+1,'p':cnt['p']//3+2,'d':cnt['d']//5+3,'f':cnt['f']//7+4}[t]
            cnt[t]+=1
            labs.append((f"{n}{t}",e,o))
        out[k]=labs
    return h,out
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# reuse parse() without running main
EH=27.211386245988
ROOT=sys.argv[1] if len(sys.argv)>1 else os.path.expanduser('~/tmp/ecce/ECCE')
G=ROOT+'/data/client/examples/genchem/'
OUT=os.path.dirname(os.path.abspath(__file__))+'/'
V='.ecce-9.5.2-dev.png'
el=['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar']
nist=[13.598434599702,24.587389011,5.391714996,9.322699,8.298019,11.2602880,14.53413,13.618055,17.42282,21.564541,5.13907696,7.646236,5.985769,8.15168,10.486686,10.3600167,12.967633,15.7596119]
def homo(o):
    occ=[(e,l) for k in o for (l,e,oc) in o[k] if oc>0]
    return max(occ)
def E(p): return float(parse(p)[0]['energy_total'])
koop=[];b3=[]
print('Z el  NIST  Koopmans(eV) HOMOlab  B3LYP-HOMO(eV) lab  Zeff(HF valence)')
zeff=[]
for i,s in enumerate(el):
    h,o=parse(f'{G}koopmans/ecceqm-{s}_HF/{s}_HF.qmout'); e,l=homo(o)
    n=int(l[0]); z=n*math.sqrt(-2*e); zeff.append(z); koop.append(-e*EH)
    h2,o2=parse(f'{G}atoms/ecceqm-{s}/{s}.qmout'); e2,l2=homo(o2); b3.append(-e2*EH)
    print(f'{i+1:2d} {s:2s} {nist[i]:7.3f} {-e*EH:7.2f} {l:3s} {e:.4f}  {-e2*EH:6.2f} {l2} {e2:.4f}  {z:.2f}')
print('dSCF HF IE:')
dscf={}
for s in ['Li','Be','C','N','O','F','Ne']:
    d=G+'ionisation-and-electron-affinity/'
    v=(E(f'{d}ecceqm-{s}_HF_cation/{s}_HF_cation.qmout')-E(f'{d}ecceqm-{s}_HF_neutral/{s}_HF_neutral.qmout'))
    dscf[s]=v*EH; print(s, f'{v:.6f} Eh {v*EH:.2f} eV {v*2625.4996:.1f} kJ/mol')
print('PBE0 EA:')
for s in ['Li','Be','C','N','O','F']:
    d=G+'ionisation-and-electron-affinity/'
    v=(E(f'{d}ecceqm-{s}_PBE0_neutral/{s}_PBE0_neutral.qmout')-E(f'{d}ecceqm-{s}_anion/{s}_anion.qmout'))
    print(s, f'{v:.6f} Eh {v*EH:.2f} eV {v*2625.4996:.1f} kJ/mol')
print('1s Zeff from HF:', [(s, round(math.sqrt(-2*[e for (l,e,oc) in list(parse(f"{G}koopmans/ecceqm-{s}_HF/{s}_HF.qmout")[1].values())[0] if l=="1s"][0]),2)) for s in ['He','Ne','Ar']])
Z=list(range(1,19))
plt.rcParams.update({'font.size':11})
fig,ax=plt.subplots(figsize=(7,4.2),facecolor='white')
ax.plot(Z,nist,'o-',color='black',label='Experiment (NIST ASD)')
ax.plot(Z,koop,'s--',color='#0072B2',label="HF, Koopmans' theorem ($-\\varepsilon_\\mathrm{HOMO}$)")
zs=[el.index(s)+1 for s in dscf]; ax.plot(zs,list(dscf.values()),'^',color='#D55E00',ms=8,label='HF, $E$(cation) $-$ $E$(atom)')
ax.plot(Z,b3,'d:',color='#009E73',label='B3LYP, $-\\varepsilon_\\mathrm{HOMO}$')
ax.set_xticks(Z); ax.set_xticklabels(el); ax.set_xlabel('Atom'); ax.set_ylabel('First ionisation energy / eV')
ax.set_ylim(0,27); ax.grid(alpha=.3); ax.legend(fontsize=9,loc='upper right'); fig.tight_layout(); fig.savefig(OUT+'ie'+V,dpi=200,facecolor='white')
fig,ax=plt.subplots(figsize=(7,3.6),facecolor='white')
ax.plot(Z,zeff,'o-',color='#0072B2'); ax.set_xticks(Z); ax.set_xticklabels(el)
ax.set_xlabel('Atom'); ax.set_ylabel('$Z_\\mathrm{eff}$ of the HOMO'); ax.grid(alpha=.3); ax.set_ylim(0,3.5)
fig.tight_layout(); fig.savefig(OUT+'zeff'+V,dpi=200,facecolor='white')
# Ca Cr Cu levels
fig,axs=plt.subplots(1,3,figsize=(7,3.8),sharey=True,facecolor='white')
names={"1":"singlet","2":"doublet","7":"septet"}
for ax,s in zip(axs,['Ca','Cr','Cu']):
    h,o=parse(f'{G}atoms/ecceqm-{s}/{s}.qmout'); labs=o['restricted']
    sets={}
    for l,e,oc in labs:
        if l in ('3d','4s','4p'): sets.setdefault(l,[]).append((e,oc))
    for l,x in (('4s',0),('3d',1),('4p',2)):
        v=sets[l]; e=sum(a for a,_ in v)/len(v)*EH; occ=sum(b for _,b in v)
        col='black' if occ>0 else '#888888'
        ax.hlines(e,x-0.38,x+0.38,color=col,lw=2.5)
        ax.text(x,e-0.25,f'{l}\n{occ:g} e\n{e:.2f}',ha='center',va='top',fontsize=8,color=col)
    ax.set_title(f'{s} ({names[h["multiplicity"]]})',fontsize=11)
    ax.set_xlim(-0.6,2.6); ax.set_xticks([])
axs[0].set_ylabel('B3LYP orbital energy / eV'); axs[0].set_ylim(-9.5,0.5)
fig.tight_layout(); fig.savefig(OUT+'tm-levels'+V,dpi=200,facecolor='white')
