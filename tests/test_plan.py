import unittest
from scripts.plan_report import plan
class TestReportPlan(unittest.TestCase):
 def setUp(self):
  self.data={"operating_system":"Ubuntu","host_count":2,"purpose":"SOC","access":"non-root","sections":["CPU"],"benchmark_approved":False,"output_classification":"restricted"}
 def test_safe_default(self):
  output=plan(self.data)
  self.assertIn("Not approved",output)
  self.assertIn("No host commands executed",output)
 def test_approved_still_requires_explicit_command(self):
  self.data["benchmark_approved"]=True
  self.assertIn("separate operational approval",plan(self.data))
 def test_invalid(self):
  self.data["host_count"]=0
  with self.assertRaises(ValueError):plan(self.data)
 def test_escape(self):
  self.data["operating_system"]="<script>"
  self.assertNotIn("<script>",plan(self.data))
