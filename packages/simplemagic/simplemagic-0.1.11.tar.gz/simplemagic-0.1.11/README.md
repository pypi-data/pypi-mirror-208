# simplemagic

Simple file magic. We try to get file's mimetype using 'file-magic', 'command file' and 'puremagic'. On linux we need system package 'file-libs' which mostly already installed. On MacOS we need system package 'libimage' which can be installed by 'brew install libmagic'. On windows we need file command which can be install by 'pacman -S file' within msys2. If system package missing, we try to get the file's mimetype using 'puremagic' which is write in pure python without any extra depends.

## Install

```
pip3 install simplemagic
```

## System requirements

### Linux

- file-libs

Mostly it is installed already, and you can installed it with command:

```
yum install file-libs
```

### MacOS

- libmagic

You can installed it with command:

```
brew install libmagic
```

### Windows

libmagic mostly not working on windows. Suggest you install msys2 on in system, and in msys2 you can install libmagic with command:

```
pacman -S file
```

Add msys2's bin path to your system's PATH env. We can call the external command `file` to get the mimetype of a file.

## APIS

- simplemagic.get_mimetype_by_stream
- simplemagic.get_mimetype_by_filename
- simplemagic.guess_all_extensions
- simplemagic.is_file_content_matches_with_file_extension # mostly we just use this function to check if the file cotent is matches with the file extension.
- simplemagic.file_content_matches_with_file_extension_test

You can read the source code to find other private apis which maybe you will need to reset the global settings or running env.

### simplemagic.magic.file_content_matches_with_file_extension_test

```
def file_content_matches_with_file_extension_test(
        filename,
        stream=None,
        enable_using_magic=True,
        enable_using_file_command=True,
        enable_using_puremagic=True,
        magic_content_length=MAGIC_CONTENT_LENGTH,
        lax_extensions=None,
        ):
    """Detect the file's mimetypes by it's content and test if it matches with the given file extension.

    Returns:
        (bool): True if file content matches with the file extension.
        (str): The file's extension.
        (str): The mimetype detected by the file content.

    Parameters:
        filename(str): A filename string.
        stream(file): Opened file instance. If stream is
        enable_using_magic(bool): Use libmagic engine or not. Default to True.
        enable_using_file_command(bool): Use file command or not. Default to True.
        enable_using_puremagic(bool): Use puremagic engine or not. Default to True.
        magic_content_length(int): Read max while doing file's mimetype test.
        lax_extensions(List[List[str]]): Extra information for compares. Extensions in a lax set can be used in mix.
    """
    pass
```

### simplemagic.magic.is_file_content_matches_with_file_extension

```
def is_file_content_matches_with_file_extension(*args, **kwargs):
    """Detect the file's mimetypes by it's content and test if it matches with the given file extension.

    Returns:
        (bool): True if file content matches with the file extension.

    Parameters:
        filename(str): A filename string.
        stream(file): Opened file instance. If stream is
        enable_using_magic(bool): Use libmagic engine or not. Default to True.
        enable_using_file_command(bool): Use file command or not. Default to True.
        enable_using_puremagic(bool): Use puremagic engine or not. Default to True.
        magic_content_length(int): Read max while doing file's mimetype test.
        lax_extensions(List[List[str]]): Extra information for compares. Extensions in a lax set can be used in mix.
    """
```

## Examples

```
import simplemagic

ext = ".docx"
filename = "ok.docx"
result, ext, mimetype = simplemagic.file_content_matches_with_file_extension_test(filename)
if result:
    print("the file content is matches with the file extension.")
else:
    print(f"the file content is NOT matches with the file extension.")
    print(f"The mimetype detected by the file content is {mimetype}, but the given file extension {ext} is not in the suggest extension set of this mimetype!")
```

## filemagic command util

simplemagic also ships a command util `filemagic`.

### Usage of the command filemagic

```
test@test simplemagic % filemagic --help
Usage: filemagic [OPTIONS] [FILENAME]...

  Get file's mimetype information.

Options:
  --disable-magic         Don't use libmagic.
  --disable-file-command  Don't use file command.
  --disable-puremagic     Don't use puremagic.
  --help                  Show this message and exit.
```

### Example files test result

```
test@test simplemagic % filemagic *

ok.bash_history: text/plain
ok.bash_profile: text/plain
ok.bashrc: text/plain
ok.conf: text/plain
ok.coverage: application/vnd.sqlite3
ok.csv: text/plain
ok.dat: application/octet-stream
ok.doc: application/msword
ok.docx: application/vnd.openxmlformats-officedocument.wordprocessingml.document
ok.dot: application/vnd.openxmlformats-officedocument.wordprocessingml.document
ok.dps: application/vnd.openxmlformats-officedocument.presentationml.presentation
ok.dpt: application/vnd.openxmlformats-officedocument.presentationml.presentation
ok.et: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
ok.ett: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
ok.gif: image/gif
ok.gitignore: text/plain
ok.htaccess: text/plain
ok.in: text/plain
ok.ini: text/plain
ok.java: text/x-java
ok.jpg: image/jpeg
ok.less: text/plain
ok.log: text/plain
ok.md: text/plain
ok.pages: application/zip
ok.pdf: application/pdf
ok.pl: text/x-perl
ok.png: image/png
ok.pptx: application/vnd.openxmlformats-officedocument.presentationml.presentation
ok.properties: text/plain
ok.py: text/x-script.python
ok.rpm: application/x-rpm
ok.scss: text/plain
ok.sh: text/x-shellscript
ok.sql: text/plain
ok.svg: image/svg+xml
ok.tar.gz: application/gzip
ok.ttf: font/sfnt
ok.txt: text/plain
ok.txt.bz2: application/x-bzip2
ok.whl: application/zip
ok.woff: application/octet-stream
ok.woff2: application/octet-stream
ok.wps: application/vnd.openxmlformats-officedocument.wordprocessingml.document
ok.wpt: application/vnd.openxmlformats-officedocument.wordprocessingml.document
ok.wsdl: text/xml
ok.xlsx: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
ok.xmind: application/zip
ok.xml: text/xml
ok.xsl: text/xml
ok.yml: text/plain
ok.zip: application/zip
private.DS_Store: application/octet-stream
private.bpmn: text/xml
private.cab: application/vnd.ms-cab-compressed
private.class: application/x-java-applet
private.dll: application/x-dosexec
private.dmg: application/x-bzip2
private.doc: application/msword
private.dwg: image/vnd.dwg
private.fla: application/CDFV2
private.ftl: text/html
private.ico: image/vnd.microsoft.icon
private.img: application/octet-stream
private.inf: text/plain
private.jsp: text/html
private.mht: message/rfc822
private.mp4: video/mp4
private.mpp: application/vnd.ms-office
private.msi: application/x-msi
private.pcap: application/vnd.tcpdump.pcap
private.pps: application/vnd.ms-powerpoint
private.ppt: application/vnd.ms-powerpoint
private.psd: image/vnd.adobe.photoshop
private.pyc: application/x-bytecode.python
private.rar: application/x-rar
private.reg: text/x-ms-regedit
private.swf: application/x-shockwave-flash
private.tar: application/x-tar
private.tif: image/tiff
private.vsd: application/vnd.ms-office
private.xls: application/vnd.ms-excel
private.xps: application/zip
private.xsd: text/xml
```

## Notice

Always upgrade your libmagic to the latest, old libmagic may get wrong answer.

## Compatibility

- test passed on python3.6, python3.7, python3.8, python3.9 and python3.10
- test failed on python2.7, python3.3, python3.4, python3.5

## Releases

### v0.1.0

- First release.

### v0.1.1

- Recover stream position after mimetype detect.
- Fix small file handling problem in puremagic.
- Fix .gz extension problem.
- Fix .bz2 extension problem.


### v0.1.5

- Put function is_file_content_matches_with_file_extension to public.
- Using magic.detect_from_fobj instead of magic.detect_from_content to improve the recognition.
- Change register_mimetype_extensions' parameters, and fix the problem.
- Fix .dps, .dpt, .et, .ett extension problems.
- Fix .dox problem.
- Fix .mptt problem.
- Fix .csv problem.
- Fix .pcap problem.
- Fix .rpm problem.
- Fix .dmg problem.
- Fix .reg problem.
- Fix .dwg problem.
- Fix .xps problem.
- Fix .ttf problem.
- Fix .woff and .woff2 problem.
- Fix java .class problem.
- Fix .jsp problem.
- Fix .less and .scss problem.
- Fix .pyc problem.
- Fix .fla problem.
- Fix .vsd problem.


### v0.1.7

- Add magic_content_length parameter in function is_file_content_matches_with_file_extension to control the stream content read length locally.
- Fix export api name problem.

### v0.1.8

- Add lax_extensions parameter in function is_file_content_matches_with_file_extension to support lax extension compares, especially for user missing .jpg, .png extension for images.
- Add LAX_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpe", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".ico"].

### v0.1.9

- Remove .svg from text/plain, for both libmagic and puremagic are not treat .svg file as text/plain. libmagic treat it as image/svg+xml, and puremagic treat it as application/xml. If put .svg in candidate extensions of text/plain, in image lex compares model, will allow user upload plain text script in image file field.

### v0.1.10

- Add mimetype and file extension binding from nginx's default mimetype settings.
- Add mimetype and file extension binding from https://docs.w3cub.com/http/basics_of_http/mime_types/complete_list_of_mime_types.html.
- Add mimetype adn file extension binding from https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types.


### v0.1.11

- Add many items in EXTRA_MIMETYPE_EXTENSIONS.
