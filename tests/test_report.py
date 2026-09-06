import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('report',ROOT/'scripts/system_report.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class ReportTests(unittest.TestCase):
    def test_demo_formats_unique_private_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            command=['bash',str(ROOT/'system_check_and_fio.sh'),'--demo','--output-dir',folder]
            for _ in range(2):
                run=subprocess.run(command,capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            reports=list(Path(folder).iterdir());self.assertEqual(len(reports),2)
            for directory in reports:
                data=json.loads((directory/'system_report.json').read_text())
                self.assertTrue(data['demo']);self.assertEqual(data['status'],'partial')
                self.assertEqual(directory.stat().st_mode & 0o077,0)
                for name in ('html','txt','csv','json'): self.assertTrue((directory/('system_report.'+name)).is_file())

    def test_html_and_csv_escaping(self):
        with tempfile.TemporaryDirectory() as folder:
            data={'host':'<script>bad</script>','generated_at':'test','sections':[{'title':'<tag>','status':'ok','text':'=SUM(1,2)\n"quoted"'}],'benchmarks':[]}
            r.render(data,folder)
            html=(Path(folder)/'system_report.html').read_text()
            self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
            with (Path(folder)/'system_report.csv').open(newline='') as f: rows=list(csv.reader(f))
            self.assertTrue(rows[1][3].startswith("'="))
            self.assertEqual(json.loads((Path(folder)/'system_report.json').read_text())['sections'][0]['text'],data['sections'][0]['text'])

    def test_mfa_is_only_a_hint(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sshd';path.write_text('# auth required pam_duo.so\n')
            self.assertIn('No known',r.mfa_hint(path)['text'])
            path.write_text('auth required pam_duo.so\n')
            self.assertIn('does not establish',r.mfa_hint(path)['text'])
            self.assertEqual(r.mfa_hint(path)['status'],'review')

    def test_missing_command(self):
        with patch.object(r.subprocess,'run',side_effect=FileNotFoundError):
            self.assertEqual(r.capture(['missing'])['status'],'unavailable')

    def test_both_fio_results_and_cleanup(self):
        with tempfile.TemporaryDirectory() as folder:
            parent=Path(folder);out=parent/'reports';out.mkdir();keep=parent/'keep';keep.write_text('keep')
            args=SimpleNamespace(fio_dir=folder,size_mib=1,runtime=1)
            def fake(command,**kwargs):
                raw=Path(next(v.split('=',1)[1] for v in command if v.startswith('--output=')))
                raw.write_text(json.dumps({'jobs':[{'error':0,'read':{'iops':100},'write':{'iops':50}}]}))
                return SimpleNamespace(returncode=0)
            with patch.object(r,'capture',return_value={'status':'ok','text':'fio-3.40'}),patch.object(r.subprocess,'run',side_effect=fake):
                results=r.benchmark(args,out)
            self.assertEqual(len(results),2)
            self.assertTrue((out/'random_read.json').exists());self.assertTrue((out/'random_write.json').exists())
            self.assertEqual(keep.read_text(),'keep');self.assertEqual(list(parent.glob('system-report-fio-*')),[])

    def test_failed_fio_has_no_measurement(self):
        with tempfile.TemporaryDirectory() as folder:
            args=SimpleNamespace(fio_dir=folder,size_mib=1,runtime=1)
            with patch.object(r,'capture',return_value={'status':'ok','text':'fio-3.40'}),patch.object(r.subprocess,'run',return_value=SimpleNamespace(returncode=1)):
                result=r.benchmark(args,Path(folder))
            self.assertEqual(result[0]['status'],'failed');self.assertNotIn('read_iops',result[0])

    def test_failure_exit_retains_inventory(self):
        with tempfile.TemporaryDirectory() as folder:
            data={'host':'test','generated_at':'test','sections':[],'benchmarks':[]}
            with patch.object(r,'collect',return_value=data),patch.object(r,'benchmark',side_effect=ValueError('missing FIO')):
                self.assertEqual(r.main(['--benchmark','--fio-dir',folder,'--output-dir',folder]),1)
            result=next(Path(folder).glob('report-*/system_report.json'))
            self.assertEqual(json.loads(result.read_text())['status'],'failed')

    def test_demo_cannot_benchmark(self):
        run=subprocess.run(['bash',str(ROOT/'system_check_and_fio.sh'),'--demo','--benchmark'],capture_output=True)
        self.assertEqual(run.returncode,2)

if __name__=='__main__': unittest.main()
