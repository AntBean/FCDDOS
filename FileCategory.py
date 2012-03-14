"""
taken from http://www.fileinfo.com/filetypes/web
"""
sourcecodeTypes = ["asa","asax","ascx","ashx","asmx","asp","aspx","axd",
                    "cshtml","csp","css","dhtml","do","dml","hdm","hdml",
                    "htc","htm","html","jhtml","js","jsp","jspx","jws",
                    "mhtnl","mspx","obml","ognc","opml","oth","page","php"
                    "phtm","phtml","phtml","rhtml","sht","shtm","shtml",
                    "stm","stml","vbd","vbhtml","xss"]
"""
taken from http://en.wikipedia.org/wiki/Image_file_formats
"""
imageTypes = ["gif","jpg","jpeg","png","tiff","jfif","exif","raw","bmp",
                "ppm","pgm","pbm","pnm","webp","tga","ilbm","pcx","ecw",
                "sid","cd5","fits","pgf","xcf","psd","psp"]
"""
taken from http://en.wikipedia.org/wiki/Audio_file_format
taken from http://www.libtiff.org/video-formats.html
"""
audioVedioTypes = ["act","aiff","aac","alac","amr","atrac","au",
                    "awb","dct","dss","dvf","flac","gsm","iklax","ivs",
                    "m4p","mmf","mp3","mpc","msv","mxp4","ogg","ra",
                    "ram","tta","vox","wav","wma",
                    "flv","avi","mov","mp4","mpg","wmv","3gp","asf","rm",
                    "swf"]
"""
taken from http://www.fileinfo.com/filetypes/text
only common and very common doc types taken
"""
docTypes = ["abw","doc","docx","dotx","eml","fb2","fdx","lit","log","lst",
            "msg","odt","pages","rtf","sig","sty","tex","txt","wps","yml",
            "pdf"]

fileCategoryNames = ["source","image","audio-vedio","document"]
fileCategories = [sourcecodeTypes,imageTypes,audioVedioTypes,docTypes]
