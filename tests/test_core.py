
import unittest
from torefl import Store, StoreWithName
import io

class TestStore(unittest.TestCase):
	"""
	Test reading torefl bases
	"""
	def setUp(self):
		self.store = Store()
	
	def get(self, val):
		return val
	
	def prepareReserve(self):
		self.store.reserve(20)
		
	
	def test_0_reserve(self):
		self.prepareReserve()
		store = self.store
		self.assertEqual(store.capacity(), 20)
		self.assertListEqual(list(store.values()), [])
	
	def test_1_insert(self):
		store = self.store
		idA = self.idA = store.insert(self.get('A'))
		idB = self.idB = store.insert(self.get('B'))
		self.assertNotEqual(idA, idB)
		self.assertEqual(store[idA], self.get('A'))
		self.assertEqual(store[idB], self.get('B'))
		self.assertEquals(store.capacity(), 2)
		self.assertEquals(len(store), 2)
		self.assertEquals(store.idMax(), 1)
		l1 = list(store.values())
		l2 = [self.get('A'), self.get('B')]
		l1.sort()
		l2.sort()
		self.assertListEqual(l1, l2)
	
	def test_1_reserve_insert_less(self):
		store = self.store
		store.reserve(20)
		idA = self.idA = store.insert(self.get('A'))
		idB = self.idB = store.insert(self.get('B'))
		self.assertNotEqual(idA, idB)
		self.assertEqual(store[idA], self.get('A'))
		self.assertEqual(store[idB], self.get('B'))
		self.assertEquals(store.capacity(), 20)
		self.assertEquals(len(store), 2)
		self.assertEquals(store.idMax(), 1)
		l1 = list(store.values())
		l2 = [self.get('A'), self.get('B')]
		l1.sort()
		l2.sort()
		self.assertListEqual(l1, l2)
		
	def test_1_reserve_insert_more(self):
		store = self.store
		store.reserve(2)
		idA = self.idA = store.insert(self.get('A'))
		idB = self.idB = store.insert(self.get('B'))
		idC = self.idC = store.insert(self.get('C'))
		idD = self.idD = store.insert(self.get('D'))
		self.assertEqual(len({idA, idB, idC, idD}), 4)
		self.assertEqual(store[idA], self.get('A'))
		self.assertEqual(store[idB], self.get('B'))
		self.assertEqual(store[idC], self.get('C'))
		self.assertEqual(store[idD], self.get('D'))
		self.assertEquals(store.capacity(), 4)
		self.assertEquals(len(store), 4)
		self.assertEquals(store.idMax(), 3)
		l1 = list(store.values())
		l2 = [self.get('A'), self.get('B'), self.get('C'), self.get('D')]
		l1.sort()
		l2.sort()
		self.assertListEqual(l1, l2)
	
	def test_2_release(self):
		self.test_1_insert()
		store = self.store
		idA = self.idA
		idB = self.idB
		store.release(idA)
		self.assertEqual(list(store.values()), [self.get('B')])
		self.assertEquals(store.capacity(), 2)
		self.assertEqual(len(store), 1)
		self.assertEquals(store.idMax(), 1)
		idA2 = store.insert(self.get('A2'))
		self.assertEqual(idA2, idA, 'Test if it reuses the same id')
		l1 = list(store.values())
		l2 = [self.get('A2'), self.get('B')]
		l1.sort()
		l2.sort()
		self.assertListEqual(l1, l2)
		self.assertEquals(store.capacity(), 2)
		self.assertEqual(len(store), 2)
		self.assertEquals(store.idMax(), 1)
		
	def test_3_replace(self):
		self.test_1_insert()
		store = self.store
		idA = self.idA
		idB = self.idB
		idC = idB
		store.replace(idC, self.get('C'))
		self.assertEqual(store[idA], self.get('A'))
		self.assertEqual(store[idC], self.get('C'))
		self.assertEquals(len(store), 2)
		l1 = list(store.values())
		l2 = [self.get('A'), self.get('C')]
		l1.sort()
		l2.sort()
		self.assertListEqual(l1, l2)
		
	def test_3_replaceNone(self):
		self.test_1_reserve_insert_less()
		store = self.store
		idA = self.idA
		idB = self.idB
		idC = idA + idB + 1
		store.replace(idC, self.get('C'))
		self.assertEqual(store[idA], self.get('A'))
		self.assertEqual(store[idB], self.get('B'))
		self.assertEqual(store[idC], self.get('C'))
		self.assertEquals(store.capacity(), 20)
		self.assertEqual(len(store), 3)
		self.assertEquals(store.idMax(), idC)
		l1 = list(store.values())
		l2 = [self.get('A'), self.get('B'), self.get('C')]
		l1.sort()
		l2.sort()
		self.assertListEqual(l1, l2)

class _Obj(object):
	"""
	
	"""
	def __init__(self, val):
		self.val = val
	
	def __eq__(self, obj):
		try:
			return self.val == obj.val
		except:
			return self.val == obj

class TestStoreWithName(TestStore):
	"""
	
	"""
	def setUp(self):
		self.store = StoreWithName()
	
	def get(self, val):
		return _Obj(val)

	
