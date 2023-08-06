import FiReTiTiPyLib.ImageTools as imTools
import numpy
import random
import unittest



class Test_ImageTools(unittest.TestCase):
	
	def test_Dimensions(self):
		for i in range(13):
			w = random.randint(7, 31)
			h = random.randint(7, 31)
			self.assertEqual((imTools.Dimensions(numpy.ndarray(shape=(h, w)))), (w, h, 1, True),
							"Should be (%d, %d, 1, True)." % (h, w))
			self.assertEqual((imTools.Dimensions(numpy.ndarray(shape=(3, h, w)))), (w, h, 3, True),
							"Should be (%d, %d, 3, True)." % (h, w))
			self.assertEqual((imTools.Dimensions(numpy.ndarray(shape=(h, w, 3)))), (w, h, 3, False),
							"Should be (%d, %d, 3, False)." % (h, w))



	def test_AddMoveChannels(self):
		for i in range(13):
			w = random.randint(7, 31)
			h = random.randint(7, 31)
			
			self.assertEqual(imTools.AddMoveChannels(numpy.ndarray(shape=(h, w)), True).shape, (1, h, w),
							"Should be (1, %d, %d)." % (h, w))
			self.assertEqual(imTools.AddMoveChannels(numpy.ndarray(shape=(h, w)), False).shape, (h, w, 1),
							"Should be (%d, %d, 1)." % (h, w))
			
			self.assertEqual(imTools.AddMoveChannels(numpy.ndarray(shape=(3, h, w)), True).shape, (3, h, w),
							"Should be (3, %d, %d)." % (h, w))
			self.assertEqual(imTools.AddMoveChannels(numpy.ndarray(shape=(3, h, w)), False).shape, (h, w, 3),
							"Should be (%d, %d, 3)." % (h, w))
			self.assertEqual(imTools.AddMoveChannels(numpy.ndarray(shape=(h, w, 3)), False).shape, (h, w, 3),
							"Should be (%d, %d, 3)." % (h, w))
			self.assertEqual(imTools.AddMoveChannels(numpy.ndarray(shape=(h, w, 3)), True).shape, (3, h, w),
							"Should be (3, %d, %d)." % (h, w))
			
			with self.assertRaises(Exception):
				imTools.AddMoveChannels(numpy.ndarray(shape=(h, w, 3, 1)), True)
			with self.assertRaises(Exception):
				imTools.AddMoveChannels(numpy.ndarray(shape=(1, h, w, 3)), False)



if __name__ == '__main__':
	unittest.main()
