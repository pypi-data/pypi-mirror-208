
from .magic import get_mimetype_by_stream
from .magic import get_mimetype_by_filename
from .magic import is_file_content_matches_with_file_extension
from .magic import file_content_matches_with_file_extension_test

from .magic import enable_using_file_command
from .magic import disable_using_file_command
from .magic import set_file_command

from .magic import LAX_IMAGE_EXTENSIONS
from .magic import IMAGE_EXTENSIONS
from .magic import DOC_EXTENSIONS
from .magic import ARCHIVE_EXTENSIONS
from .magic import APPLICATION_EXTENSIONS

from .extra_mimetypes import register_mimetype_extensions
from .extra_mimetypes import guess_all_extensions

from .utils import SafeStreamReader

# alias
from .magic import is_file_content_matches_with_file_suffix
