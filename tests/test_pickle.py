import unittest
# make sure cgi-bin directory is in path
import sys, os
sys.path.append(os.path.join(os.pardir,'bin'))

class TestPickleMethods(unittest.TestCase):
    def test_pickle_Pic_object(self):
        # make sure pickling and unpickling is working.
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','boys','1370366193_1ace76e049_b_d.jpg')
        # Try to pickle
        this_Pic = Pic(this_handler.start_response, pic_path)
        self.assertTrue('1370366193_1ace76e049_b_d.jpg' in this_Pic.getFileName())
        # Now unpickle
        new_Pic = Pic.loadPickledVersion(this_handler.start_response,pic_path)
        self.assertTrue('1370366193_1ace76e049_b_d.jpg' in new_Pic.getFileName())
        # clean up our pickly mess
        os.remove(this_Pic.getPicklePath(pic_path))
        
if __name__ == '__main__':
    unittest.main()