# pix2
https://github.com/GitRay/pix2  
Fork of pix, the python photo gallery

## summary
pix2 is a minimalist gallery system. To organize all your photos, we traverse a directory structure and as-needed
generate thumb-nails and web optimized versions of your images. Through a simple
'.meta' file in each directory you can assign comments to each image.

pix2 doesn't try to do what other programs do well. In true unix style pix2 does one thing and does it well in a very transparent manner.
- No image cropping or rotating; IrfanView, Gimp, etc.. all do a better job and are more flexible. The EXIF rotation setting is obeyed.
- No album management; the filesystem is a familiar and intuitive way to manage your images.
- No uploads; if you have an account on a box and are running a web server, you should have a firm grasp on ftp or scp.

## install instructions
- For best performance, make sure Python Image Library (PIL) or pillow is installed
- ImageMagick may also be used, and is a fallback if PIL is not available.
- Put the "static" directory somewhere that your web server can serve static files.
- Put the "bin" directory somewhere that your WSGI server can start your application.
- Edit the "bin/Setup.py" file to suit your server's setup.

## album setup and guidelines
- Your directory structure will dictate the hierarhcy for albums and picture placement
- To hide a picture rename it with .<picture name> just like you'd hide a file in unix
- Spaces and strange Unicode characters in filenames should be handled correctly. If you find an exception, let me know.

## anatomy of a .meta file
  - The 'test_album' folder contains some examples of .meta files.
  - In each directory optionally create a .meta file, the format for the picture comments are  
    pic_file_name = comment
  - It's not necessary to have every file in there.  In vim do: ':r!ls' to get a complete listing of the files in this directory.  then just slap a '= comment' on each line you want to provide a comment.
  - The comment for a picture can only be on 1 line!
  - To add a description for the current album create 2 lines at the top, literally '&lt;album description&gt;' and '&lt;/album description&gt;'. Between these lines put the description.
  - To control the thumbnail order, add a '=' after the file name wether or not the picture has a comment associated with it and put them in the order you want in the .meta file. Pictures with no '=' and pictures not in the .meta file will be put at the end of the thumbnails in reverse alphabetical order (because autonumbered photos will then display most recent first).
  - here is a sample .meta file (in between the snip tags!) In the example below demian_and_leo.jpg would go first, then 
    dawn_demian_bobbi.jpg and lastly mom.jpg. mom.jpg would go last since it has no '=' and is therefore an illegal (and ignored) line.  
&lt;snip&gt;  
&lt;album description&gt;  
here are some pictures of my family. these were taken at family reunions and stuff.  
&lt;/album description&gt;  
demian_and_leo.jpg = this is me and my cousin leo  
mom.jpg  
dawn_demian_bobbi.jpg =  
&lt;/snip&gt;


## style sheets
- Some extra style sheets are in pix/extra_styles. You can use these to replace the default style sheets located in the 'static' directory.

## anatomy of the template file
The template file is 'pix/static/template.html' it's just a simple html document, you can pretty much do with it what you want, you place the tokens for the generated elements into your html.
- @title@  
 Shows you the current directory with a delimiter in front of it (the assumption is that you will have a string before the delimiter, like the name of your site. The delimiter is set in 'pix/bin/Setup.py' by changing the 'seperator' variable. Default is '&raquo;' (&amp;raquo;)
- @breadcrumb@  
 A delimited string that shows you where you are at in the directory hierarchy inside the albums.  It gives you links to go to whatever level you want. It uses the same delimiter as @title&#64;.
- @albums@  
 If there are no sub-directories in the current directory this returns an empty string. If there are sub-directories this gives you the string '&lt;h2&gt;n albums&lt;/h2&gt;', where 'n' is the number of sub-albums, followed by an list of albums in reverse-alphabetical order (my album names start with the date, so this has the effect of displaying the most recent first).
- @pics@  
 This returns thumbnail images of all the pictures in the current directory. Thumbnails are set to be a max of 80 width or 60 height in the file 'pix/bin/Pic.py'.
- @album-description@  
 If there is no currently selected web-pic we print the album description, this is found in the '.meta' file.  All lines between the "album description" tags will be displayed as the album description.
- @web-pic@  
 When the user selects a thumbnail or picture from the list, the web pic is displayed.  The web pic is resized for typical web viewing (set to no larger than 500x400 in 'pix/bin/Pic.py'). If the user wants to see the original image (assuming it's larger than the web-pic) they can click on the web version to be directed to the full-resolution original. The original will always be converted to JPEG for download.
- @comment@  
 This is where the comment (if any) associated with the picture is placed.

## administration
- All administrative functions are done on the host. This keeps pix2 simple and (hopefully) more secure.

## trouble shooting
- Does the wsgi server have permission to read the pictures directory and write to the pic_cache directory?
- Does the webserver have read access to the static files and the pic_cache directory?
