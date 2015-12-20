import unittest
# make sure bin directory is in path
import sys, os
sys.path.append(os.path.join(os.pardir,'bin'))

class TestPicMethods(unittest.TestCase):
    def test_pickle_path(self):
        # some pickle paths were too long for the filesystem
        from Pic import Pic
        import Setup
        long_file_name = os.path.abspath(os.path.join(os.pardir,'test_album','other','Stella, on back - Q.A.C. Speech Day - June 14, 1975 L. to R. Two male teachers, Mrs. Elhhetih, Mrs. Lacey, Mde De Nehludoff, Y.T., Mrs. Bisade, Mrs. Abdullehi - principal - and Mrs. Abbe Kyari - wife of the then Governor of Keduna State.tif'))
        short_file_name = Pic.getPicklePath(long_file_name)
        self.assertTrue(len(short_file_name) < Setup.f_namemax)

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
        
    def test_wrong_mode_error(self):
        # this file was causing PIL to throw a wrong mode error
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','girls','ray_img904.tif')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        self.assertTrue('JFIF' in first_part_of_file)
        
    def test_div_zero_error(self):
        # this file was causing PIL to throw ZeroDivisionError
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','girls','IMG_20130512_103812.jpg')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        self.assertTrue('JFIF' in first_part_of_file)
        
    def test_value_error(self):
        # this file was causing PIL to throw a ValueError
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','other','DSC00101.JPG')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        self.assertTrue('JFIF' in first_part_of_file)

    def test_filenotfound_error(self):
        # this file was causing pix2 to throw a FileNotFoundError
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','other','ice_is_food.psd')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        self.assertTrue('JFIF' in first_part_of_file)

    def test_os_error(self):
        # this file was causing pix2 to throw a OSError
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','other','Stella, on back - Q.A.C. Speech Day - June 14, 1975 L. to R. Two male teachers, Mrs. Elhhetih, Mrs. Lacey, Mde De Nehludoff, Y.T., Mrs. Bisade, Mrs. Abdullehi - principal - and Mrs. Abbe Kyari - wife of the then Governor of Keduna State.tif')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        self.assertTrue('JFIF' in first_part_of_file)
    
    @unittest.skip('maybe not really a bug')
    def test_mac_aliases(self):
        # Mac aliases cause problems. Designed behavior is to detect the problem
        # and ignore the alias, not attempt to recognize aliases.
        from Pic import Pic
        # Pic object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        pic_path = os.path.join(os.pardir,'test_album','girls','DSC01202.JPG')
        # Try to convert picture and make sure it's a JPEG (JFIF in the header)
        this_Pic = Pic(this_handler.start_response, pic_path)
        pic_iterator = this_Pic.spitOutResizedImage('thumb')
        first_part_of_file = str(list(pic_iterator)[0])
        pic_iterator.close()
        #self.assertTrue('JFIF' in first_part_of_file)
    

    def test_whole_directory(self):
        # in addition to testing individual troublesome files, go through every file in the album
        import Setup
        from Album import Album
        # Album object needs a "start_response" object. We'll fake it.
        import wsgiref.simple_server
        this_handler = wsgiref.simple_server.ServerHandler(sys.stdin,sys.stdout,sys.stderr, os.environ)
        # recursively import all albums (OK, I guess it will only go 10000 directories deep...)
        album = Album(Setup.albumLoc,this_handler.start_response,recurse=10000)
        
        
if __name__ == '__main__':
    unittest.main()