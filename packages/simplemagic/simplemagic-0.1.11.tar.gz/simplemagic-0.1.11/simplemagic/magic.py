
import os
import logging
import subprocess
import puremagic
import typing
from binaryornot.helpers import is_binary_string

from . import fixpuremagic # required
from .utils import SafeStreamReader
from .extra_mimetypes import get_mimetype_by_extension

USING_FILE_COMMAND = True
USING_PUREMAGIC = True
try:
    import magic
    from . import fixmagic # required
    USING_MAGIC = True
except:
    magic = None
    USING_MAGIC = False

from .extra_mimetypes import guess_all_extensions

FILE_COMMAND = "file"
MAGIC_CONTENT_BUFFER = 1024*128
MAGIC_CONTENT_LENGTH = 1024*1024*64
MIMETYPE_FOR_TEXT = "text/plain"
MIMETYPE_FOR_BINARY = "application/octet-stream"
PRIORITY_EXTS = [
    ".zip",
]

logger = logging.getLogger(__name__)

def disable_using_magic():
    global USING_MAGIC
    USING_MAGIC = False

def enable_using_magic():
    global USING_MAGIC
    USING_MAGIC = True

def disable_using_puremagic():
    global USING_PUREMAGIC
    USING_PUREMAGIC = False

def enable_using_puremagic():
    global USING_PUREMAGIC
    USING_PUREMAGIC = True

def disable_using_file_command():
    global USING_FILE_COMMAND
    USING_FILE_COMMAND = False

def enable_using_file_command():
    global USING_FILE_COMMAND
    USING_FILE_COMMAND = True

def set_file_command(cmd):
    global FILE_COMMAND
    FILE_COMMAND = cmd


def get_mimetype_simple_by_stream(stream, filename=None):
    with SafeStreamReader(stream) as stream:
        data = stream.read(MAGIC_CONTENT_BUFFER)
        if is_binary_string(data):
            return MIMETYPE_FOR_BINARY
        else:
            return MIMETYPE_FOR_TEXT


def get_mimetype_simple_by_filename(filename):
    with open(filename, "rb") as fobj:
        data = fobj.read(MAGIC_CONTENT_BUFFER)
        if is_binary_string(data):
            return MIMETYPE_FOR_BINARY
        else:
            return MIMETYPE_FOR_TEXT


def get_mimetype_using_file_command_by_stream(stream, filename=None, magic_content_length=MAGIC_CONTENT_LENGTH):
    with SafeStreamReader(stream) as stream:
        proc = subprocess.Popen(
            [FILE_COMMAND, "--mime-type", "--parameter", "bytes={}".format(magic_content_length), "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            )
        read_length = 0
        while True:
            content = stream.read(MAGIC_CONTENT_BUFFER)
            if not content:
                break
            try:
                proc.stdin.buffer.write(content)
            except:
                break
            read_length += len(content)
            if read_length > magic_content_length:
                break
        try:
            proc.stdin.buffer.close()
        except:
            pass
        proc.wait(1)
        output = proc.stdout.readlines()
        if output:
            try:
                return output[0].split(":")[1].strip()
            except:
                pass
        return None


def get_mimetype_using_file_command_by_filename(filename):
    proc = subprocess.Popen(
        [FILE_COMMAND, "--mime-type", filename],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        )
    proc.wait(1)
    output = proc.stdout.readlines()
    if output:
        try:
            return output[0].split(":")[1].strip()
        except:
            pass
    return get_mimetype_simple_by_filename(filename)


def get_mimetype_using_magic_by_stream(stream, filename=None):
    with SafeStreamReader(stream) as stream:
        result = magic.detect_from_fobj(stream)
        if result:
            return result.mime_type
        else:
            return None

def get_mimetype_using_magic_by_filename(filename):
    result = magic.detect_from_filename(filename)
    if result:
        return result.mime_type
    else:
        return None


def _get_best_mimetype_from_puremagic_result(guessed_types, ext):
    mimetype = __get_best_mimetype_from_puremagic_result(guessed_types, ext)

    # hack for .fla files
    if mimetype == "application/msword" and ext == ".fla":
        return "application/CDFV2"

    return mimetype

def __get_best_mimetype_from_puremagic_result(guessed_types, ext):
    if not guessed_types:
        return None

    mimetype = None
    if not mimetype:
        for guessed_type in guessed_types:
            if guessed_type.extension == ext:
                if guessed_type.mime_type:
                    mimetype = guessed_type.mime_type
                    break
                else:
                    if guessed_type:
                        mimetype = get_mimetype_by_extension(guessed_type.extension)
                        if mimetype:
                            break

    if not mimetype:
        for guessed_type in guessed_types:
            if guessed_type.confidence > 0.5:
                if guessed_type.mime_type:
                    mimetype = guessed_type.mime_type
                    break
                else:
                    if guessed_type.extension:
                        mimetype = get_mimetype_by_extension(guessed_type.extension)
                        if mimetype:
                            break
    
    if not mimetype:
        for guessed_type in guessed_types:
            if guessed_type.extension in PRIORITY_EXTS:
                if guessed_type.mime_type:
                    mimetype = guessed_type.mime_type
                    break
                else:
                    if guessed_type.extension:
                        mimetype = get_mimetype_by_extension(guessed_type.extension)
                        if mimetype:
                            break
    
    if not mimetype:
        if guessed_types[0].mime_type:
            mimetype = guessed_types[0].mime_type
        else:
            if guessed_types[0].extension:
                mimetype = get_mimetype_by_extension(guessed_types[0].extension)

    # hack for .pcap files
    if not mimetype:
        info = guessed_types[0]
        if "libpcap" in info.name or "winpcap" in info.name:
            mimetype = "application/vnd.tcpdump.pcap"

    return mimetype



def get_mimetype_using_puremagic_by_stream(stream, filename, force=True):
    mimetype = None
    with SafeStreamReader(stream) as stream:
        try:
            guessed_types = puremagic.magic_stream(stream, filename=filename)
            ext = os.path.splitext(filename)[1]
            mimetype = _get_best_mimetype_from_puremagic_result(guessed_types, ext)
        except Exception:
            pass
    if not mimetype and force:
        mimetype = get_mimetype_simple_by_stream(stream, filename)
    return mimetype


def get_mimetype_using_puremagic_by_filename(filename, force=True):
    mimetype = None
    try:
        guessed_types = puremagic.magic_file(filename)
        ext = os.path.splitext(filename)[1]
        mimetype = _get_best_mimetype_from_puremagic_result(guessed_types, ext)
    except Exception:
        pass
    if not mimetype and force:
        mimetype = get_mimetype_by_filename(filename)
    return mimetype


def get_mimetype_by_stream(
        stream,
        filename,
        enable_using_magic=True,
        enable_using_file_command=True,
        enable_using_puremagic=True,
        magic_content_length=MAGIC_CONTENT_LENGTH,
        ):
    mimetype = None
    if (not mimetype) and magic and USING_MAGIC and enable_using_magic:
        try:
            mimetype = get_mimetype_using_magic_by_stream(stream, filename)
        except Exception as error:
            logger.warning("get mimetype using magic by stream failed: {error}...".format(error=error))
    if (not mimetype) and USING_FILE_COMMAND and enable_using_file_command:
        try:
            mimetype = get_mimetype_using_file_command_by_stream(stream, filename, magic_content_length)
        except Exception as error:
            logger.warning("get mimetype using file command by stream failed: {error}...".format(error=error))
    if (not mimetype) and USING_PUREMAGIC and enable_using_puremagic:
        try:
            mimetype = get_mimetype_using_puremagic_by_stream(stream, filename, force=False)
        except Exception as error:
            logger.warning("get mimetype using puremagic by stream failed: {error}...".format(error=error))
    if not mimetype:
        mimetype = get_mimetype_simple_by_stream(stream, filename)
    return mimetype


def get_mimetype_by_filename(
        filename,
        enable_using_magic=True,
        enable_using_file_command=True,
        enable_using_puremagic=True,
        ):
    mimetype = None
    if (not mimetype) and magic and USING_MAGIC and enable_using_magic:
        try:
            mimetype = get_mimetype_using_magic_by_filename(filename)
        except Exception as error:
            logger.warning("get mimetype using magic by filename failed: {error}...".format(error=error))
    if (not mimetype) and USING_FILE_COMMAND and enable_using_file_command:
        try:
            mimetype = get_mimetype_using_file_command_by_filename(filename)
        except Exception as error:
            logger.warning("get mimetype using file command by filename failed: {error}...".format(error=error))
    if (not mimetype) and USING_PUREMAGIC and enable_using_puremagic:
        try:
            mimetype = get_mimetype_using_puremagic_by_filename(filename, force=False)
        except Exception as error:
            logger.warning("get mimetype using puremagic by filename failed: {error}...".format(error=error))
    if not mimetype:
        mimetype = get_mimetype_simple_by_filename(filename)
    return mimetype



def lax_extensions_compare(ext, exts, lax_extensions_settings):
    if ext in exts:
        return True
    lax_extensions_settings = lax_extensions_settings or []
    for lax_extensions in lax_extensions_settings:
        if ext in lax_extensions:
            for lax_ext in lax_extensions:
                if lax_ext in exts:
                    return True
    return False

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
    if stream:
        mimetype = get_mimetype_by_stream(
            stream,
            filename=filename,
            enable_using_magic=enable_using_magic,
            enable_using_file_command=enable_using_file_command,
            enable_using_puremagic=enable_using_puremagic,
            magic_content_length=magic_content_length,
            )
    else:
        mimetype = get_mimetype_by_filename(
            filename,
            enable_using_magic=enable_using_magic,
            enable_using_file_command=enable_using_file_command,
            enable_using_puremagic=enable_using_puremagic,
            )
    ext = os.path.splitext(filename)[1]
    exts = guess_all_extensions(mimetype)
    return lax_extensions_compare(ext, exts, lax_extensions), ext, mimetype


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
    match_result, file_ext, file_mimetype = file_content_matches_with_file_extension_test(*args, **kwargs)
    return match_result

def is_file_content_matches_with_file_suffix(*args, **kwargs):
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
    return is_file_content_matches_with_file_extension(*args, **kwargs)


IMAGE_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpe",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".ico",
    ".svg",
    ".webp",
]
DOC_EXTENSIONS = [
    ".docx", # office
    ".pptx",
    ".xlsx",
    ".doc", # old office
    ".ppt",
    ".xls",
    ".wps", # wps
    ".et",
    ".dps",
    ".pdf", # pdf
]
ARCHIVE_EXTENSIONS = [
    ".zip",
    ".rar",
    ".7z",
    ".iso",
]
APPLICATION_EXTENSIONS = [
    ".exe",
    ".msi",
    ".dmg",
    ".zip",
    ".rar",
    ".7z",
    ".iso",
]
LAX_IMAGE_EXTENSIONS = [] + IMAGE_EXTENSIONS
