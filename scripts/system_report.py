#!/usr/bin/env python3
"""Linux inventory and optional file-based FIO benchmark reports."""
import argparse
import csv
from datetime import datetime, timezone
from html import escape
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile


def capture(command):
    try:
        proc = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=20, env={**os.environ, 'LC_ALL':'C'})
        return {'status':'ok' if proc.returncode == 0 else 'unavailable', 'text':proc.stdout.strip() if proc.returncode == 0 else 'Command failed or permission denied.'}
    except (OSError, subprocess.TimeoutExpired):
        return {'status':'unavailable', 'text':'Command unavailable or timed out.'}


def mfa_hint(path=Path('/etc/pam.d/sshd')):
    try:
        lines = [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    except OSError:
        return {'status':'unavailable', 'text':'SSH PAM configuration could not be read. MFA enforcement is unknown.'}
    found = any(re.search(r'\bpam_(google_authenticator|duo|oath)\.so\b', line) for line in lines)
    return {'status':'review', 'text':('A known MFA module reference was found. ' if found else 'No known MFA module reference found in this file. ')+'This does not establish MFA enforcement. Review PAM includes, effective sshd policy, Match blocks and authentication paths.'}


def collect():
    sections=[]
    for title, command in [('CPU',['lscpu']),('Memory',['free','-h']),('Block devices',['lsblk','-o','NAME,SIZE,TYPE,MOUNTPOINT']),('Filesystems',['df','-h']),('Groups',['getent','group'])]:
        sections.append({'title':title, **capture(command)})
    users=capture(['getent','passwd'])
    entries=[]
    if users['status']=='ok':
        for row in users['text'].splitlines():
            fields=row.split(':')
            if len(fields)>=7 and fields[2].isdigit() and 1000<=int(fields[2])<65534:
                entries.append(fields[0])
    sections.append({'title':'User account selection','status':users['status'],'text':('UID 1000–65533 heuristic; service accounts may be included.\n'+('\n'.join(entries) or 'No matching users.')) if users['status']=='ok' else users['text']})
    for name in entries:
        for title,cmd in [('Password aging',['chage','-l',name]),('Account status',['passwd','-S',name])]:
            sections.append({'title':f'{title}: {name}',**capture(cmd)})
    sections.append({'title':'SSH MFA configuration hint',**mfa_hint()})
    return {'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),'host':platform.node(),'demo':False,'sections':sections,'benchmarks':[]}


def positive(value):
    number=int(value)
    if not 1<=number<=3600:
        raise argparse.ArgumentTypeError('Use an integer from 1 to 3600')
    return number


def benchmark(args, report_dir):
    version=capture(['fio','--version'])
    if version['status']!='ok' or not re.match(r'^fio-\d',version['text']):
        raise ValueError('Flexible I/O Tester is required; a different program named fio may be installed')
    parent=Path(args.fio_dir).expanduser().resolve()
    if not parent.is_dir():
        raise ValueError('--fio-dir must be an existing directory on the target filesystem')
    needed=args.size_mib*1024*1024
    if shutil.disk_usage(parent).free < needed + 64*1024*1024:
        raise ValueError('Insufficient free space for the test file plus 64 MiB reserve')
    results=[]
    # Only a private temporary directory is ever removed; no raw device arguments.
    with tempfile.TemporaryDirectory(prefix='system-report-fio-',dir=parent) as folder:
        for name,mode in [('random_read','randread'),('random_write','randwrite')]:
            raw=report_dir/(name+'.json')
            command=['fio','--name='+name,'--filename='+str(Path(folder)/'benchmark.bin'),'--ioengine=psync','--iodepth=1','--numjobs=1','--direct=1','--rw='+mode,'--bs=4k','--size='+str(needed),'--runtime='+str(args.runtime),'--time_based=1','--group_reporting=1','--output-format=json','--output='+str(raw)]
            print('Benchmark: '+name,flush=True)
            try:
                result=subprocess.run(command,capture_output=True,timeout=args.runtime+120)
                if result.returncode:
                    raise ValueError('fio exited unsuccessfully')
                data=json.loads(raw.read_text(encoding='utf-8'))
                jobs=data.get('jobs',[])
                if not jobs or any(job.get('error',0) for job in jobs):
                    raise ValueError('fio returned missing jobs or job errors')
                values={direction:sum(float(job[direction]['iops']) for job in jobs) for direction in ('read','write')}
                results.append({'name':name,'status':'ok','read_iops':values['read'],'write_iops':values['write'],'raw_file':raw.name})
            except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired):
                results.append({'name':name,'status':'failed','message':'Benchmark failed; inspect the retained raw JSON if available. No IOPS claimed.'})
                break
    return results


def csv_cell(value):
    value=str(value)
    return "'"+value if value.lstrip().startswith(('=','+','-','@')) else value


def render(data, destination):
    destination=Path(destination)
    text=[]; rows=[['Category','Key','Status','Value']]
    cards=[]
    for section in data['sections']:
        title,status,value=section['title'],section['status'],section['text']
        text.append(f'{title} [{status}]\n{value}\n')
        rows.append(['System',title,status,value])
        cards.append(f'<details><summary>{escape(title)} <span>{escape(status)}</span></summary><pre>{escape(value)}</pre></details>')
    benchmarks=[]
    for item in data['benchmarks']:
        if item['status']=='ok':
            value=f'Read {item["read_iops"]:,.2f} IOPS / Write {item["write_iops"]:,.2f} IOPS'
        else: value=item.get('message','No measurements')
        text.append(f'{item["name"]} [{item["status"]}]\n{value}')
        rows.append(['FIO',item['name'],item['status'],value])
        benchmarks.append(f'<p><b>{escape(item["name"])}</b> · {escape(item["status"])}<br>{escape(value)}</p>')
    unavailable=sum(s['status']=='unavailable' for s in data['sections'])
    label='SYNTHETIC DEMO' if data.get('demo') else 'LOCAL SNAPSHOT'
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><title>System report</title><style>
body{margin:0;background:#0c1421;color:#eef3fa;font:16px/1.6 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:36px 24px}header{border-bottom:1px solid #35506d;padding-bottom:24px}h1{font-size:clamp(28px,5vw,46px);margin:8px 0;line-height:1.2}h2{font-size:23px}small{color:#72e5bd;letter-spacing:.12em}p{color:#c1cfe0}nav{display:flex;flex-wrap:wrap;gap:12px}a{color:#86d8ff;text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid #72e5bd;outline-offset:3px}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin:28px 0}.metric{padding:20px;border:1px solid #35506d;border-radius:10px;background:#142439}.metric b{display:block;font-size:32px;color:#72e5bd}details{border:1px solid #35506d;border-radius:8px;margin:12px 0}summary{cursor:pointer;padding:18px;overflow-wrap:anywhere}summary span{color:#f5ce87;font-size:14px;margin-left:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:20px;background:#080f19;font:14px/1.7 monospace}.note{border-left:3px solid #f5ce87;padding-left:16px}@media print{body{background:white;color:black}details{break-inside:avoid}pre{background:white}a,p,small,.metric b{color:black}}
</style><main><header><small>THE SAFEHOUSE / '''+label+'''</small><h1>System inspection report</h1><p>'''+escape(data['host'])+' · '+escape(data['generated_at'])+'''</p><nav aria-label="Report downloads"><a href="system_report.txt">Text report</a><a href="system_report.csv">CSV report</a><a href="system_report.json">JSON report</a></nav></header><section class="metrics"><div class="metric"><b>'''+str(len(cards))+'''</b>Collected sections</div><div class="metric"><b>'''+str(unavailable)+'''</b>Unavailable sections</div><div class="metric"><b>'''+str(len(data['benchmarks']))+'''</b>Benchmark results</div></section><p class="note">A point-in-time inventory, not a security certification. Unavailable sections need a permission or dependency review. SSH MFA hints require manual verification.</p><h2>System and account evidence</h2>'''+''.join(cards)+'''<h2>Disk I/O benchmark</h2>'''+(''.join(benchmarks) or '<p>Not requested. Run with --benchmark and an approved --fio-dir to collect measurements.</p>')+'</main></html>'
    (destination/'system_report.html').write_text(html,encoding='utf-8')
    (destination/'system_report.txt').write_text(f'{label}\n{data["host"]}\n{data["generated_at"]}\n\n'+'\n'.join(text),encoding='utf-8')
    (destination/'system_report.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    with (destination/'system_report.csv').open('w',encoding='utf-8',newline='') as handle:
        csv.writer(handle).writerows([[csv_cell(v) for v in row] for row in rows])


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',default='./system_reports',help='Parent for a unique private report directory')
    p.add_argument('--benchmark',action='store_true',help='Opt in to disk load and temporary file writes')
    p.add_argument('--fio-dir',help='Existing directory on the filesystem to benchmark')
    p.add_argument('--runtime',type=positive,default=10,help='Seconds per test (default 10)')
    p.add_argument('--size-mib',type=positive,default=256,help='Test file size in MiB (default 256)')
    p.add_argument('--demo',action='store_true',help='Render bundled synthetic data; no system collection or FIO')
    args=p.parse_args(argv)
    if args.demo and args.benchmark: p.error('--demo cannot be combined with --benchmark')
    if args.benchmark and not args.fio_dir: p.error('--benchmark requires --fio-dir')
    if not args.demo and platform.system()!='Linux': p.error('System collection requires Linux')
    os.umask(0o077)
    try:
        parent=Path(args.output_dir).expanduser().resolve(); parent.mkdir(parents=True,exist_ok=True)
        folder=Path(tempfile.mkdtemp(prefix='report-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-',dir=parent))
        print('Preparing '+('synthetic demo' if args.demo else 'system inventory'),flush=True)
        data=json.loads((Path(__file__).resolve().parents[1]/'examples/demo.json').read_text()) if args.demo else collect()
        failed=False
        if args.benchmark:
            try: data['benchmarks']=benchmark(args,folder)
            except (OSError,ValueError) as exc: data['benchmarks']=[{'name':'preflight','status':'failed','message':str(exc)}]
            failed=any(item['status']=='failed' for item in data['benchmarks'])
        data['status']='failed' if failed else ('partial' if any(s['status']=='unavailable' for s in data['sections']) else 'complete')
        render(data,folder)
        print(f'Report status: {data["status"]}\nReports saved in: {folder}',flush=True)
        return 1 if failed else 0
    except (OSError,ValueError) as exc:
        print(f'Report failed: {exc}')
        return 1

if __name__=='__main__': raise SystemExit(main())
