# $Id$

# Support for image operations using PIL.

from PIL import Image

def resize(fpath, resized_fpath, (new_width, new_height), movie):
    if movie:
        # not implemented yet for PIL
        import image_im
        return image_im.resize(fpath, resized_fpath, (new_width, new_height), movie)

    # TODO add "movie" text with ImageDraw.text()
    originalImage = Image.open(fpath)
    newImage = originalImage.resize((new_width, new_height))
    newImage.save(resized_fpath)

def get_size(fpath):
    image = Image.open(fpath)
    return int(image.size[0]), int(image.size[1])

