import unittest
# make sure bin directory is in path
import sys, os
sys.path.append(os.path.join(os.pardir,'bin'))

class TestPicMethods(unittest.TestCase):
    def test_Pic_object_info(self):
        # there was a problem using PIL to read ray_img882.tif
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','boys','ray_img882.tif')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        self.assertTrue('JFIF' in first_part_of_file)
        
if __name__ == '__main__':
    unittest.main()