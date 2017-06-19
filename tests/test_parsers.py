
import unittest
import torefl.parser as parsers
import io

class TestBase(unittest.TestCase):
	"""
	Test reading torefl bases
	"""
	def setUp(self):
		buf = """_torefl000
		30
		10:Test1:A Title
		11:Test2:
		12:Test3:Another Title
		"""
		self.f = io.StringIO(buf)
	
	def test_ParseBase(self):
		d1, d2, n = parsers.parseBase(self.f)
		self.assertDictEqual(d1, {'Test1':10, 'Test2':11, 'Test3':12})
		self.assertDictEqual(d2, {'A Title':10, 'Another Title':12})
		self.assertEqual(n, 30)
	
