import mimetypes

EXTRA_MIMETYPE_EXTENSIONS = {
    None: [],
    "application/x-python": [
        ".pyc",
    ],
    "application/x-bytecode.python": [
        ".pyc",
    ],
    "application/x-rar": [
        ".rar",
    ],
    "application/x-mach-binary": [
        ".so",
    ],
    "application/x-dosexec": [
        ".exe",
        ".dll",
    ],
    "application/x-makefile": [
        ".txt",
        ".am",
        ".m4",
    ],
    "application/x-archive": [
        ".lib",
    ],
    "application/x-yaml": [
        ".yml",
        ".yaml",
    ],
    "application/vnd.sqlite3": [
        ".coverage",
        ".db",
        ".sqlite3",
        ".sqlite",
    ],
    "application/gzip": [
        ".gz",
    ],
    "application/x-gzip": [
        ".gz",
    ],
    "application/x-bzip2": [
        ".bz2",
        ".bzip2",
        ".tbz2",
        ".tb2",
        ".dmg",
    ],
    "application/x-msi": [
        ".msi",
    ],
    "application/x-rpm": [
        ".rpm",
    ],
    "application/x-java-applet": [
        ".class",
    ],
    "application/java": [
        ".class",
    ],
    "application/java-archive": [
        ".war",
        ".ear",
        ".jar",
    ],
    "application/x-java-archive-diff": [
        ".jardiff",
    ],
    "application/x-httpd-php": [
        ".php",
    ],
    "application/x-cocoa": [
        ".cco",
    ],
    "application/x-makeself": [
        ".run",
    ],
    "application/x-perl": [
        ".pm",
        ".pl",
    ],
    "application/x-pilot": [
        ".prc",
        ".pdb",
    ],
    "application/x-redhat-package-manager": [
        ".rpm",
    ],
    "application/x-sea": [
        ".sea",
    ],
    "application/x-tcl": [
        ".tk",
        ".tcl",
    ],
    "application/x-x509-ca-cert": [
        ".pem",
        ".crt",
        ".der",
    ],
    "application/vnd.rar": [
        ".rar",
    ],
    "application/x-cdf": [
        ".cda",
    ],
    "application/atom+xml": [
        ".xml",
    ],
    # fix old version office files
    "application/x-visio": [
        ".vsd",
    ],
    "application/excel": [
        ".xls",
        ".xlb",
        ".xlm",
        ".xla",
        ".xlc",
        ".xlt",
        ".xlw",
    ],
    "application/msword": [
        ".doc",
        ".dot",
        ".wiz",
        ".mpp",
    ],  # file 5.11 (most centos release using this version of file and libmagic) and puremagic treat .mpp file as msword file
    "application/vnd.ms-word": [
        ".doc",
        ".dot",
        ".wiz",
        ".mpp",
    ],
    "application/powerpoint": [
        ".ppt",
        ".pot",
        ".ppa",
        ".pps",
        ".pwz",
    ],
    "application/mspowerpoint": [
        ".ppt",
        ".pot",
        ".ppa",
        ".pps",
        ".pwz",
    ],
    "application/vnd.ms-office": [
        ".doc",
        ".dot",
        ".wiz",
        ".xls",
        ".xlb",
        ".xlm",
        ".xla",
        ".xlc",
        ".xlt",
        ".xlw",
        ".ppt",
        ".pot",
        ".ppa",
        ".pps",
        ".pwz",
        ".mpp",
        ".mpt",
        ".xps",
        ".vsd",
    ],
    "image/avif": [
        ".avif",
    ],
    "image/x-jng": [
        ".jng",
    ],
    "image/x-icon": [
        ".ico",
    ],
    "image/webp": [
        ".webp",
    ],
    "image/x-dwg": [
        ".dwg",
    ],
    "image/x-ms-bmp": [
        ".bmp",
    ],
    "font/collection": [
        ".ttf",
        ".cff",
        ".svg",
    ],
    "font/sfnt": [
        ".ttf",
        ".cff",
        ".svg",
    ],
    "font/otf": [
        ".ttf",
        ".cff",
        ".svg",
    ],
    "font/ttf": [
        ".ttf",
    ],
    "font/ttc": [
        ".ttc",
    ],
    "font/woff": [
        ".woff",
    ],
    "font/woff2": [
        ".woff2",
    ],
    "application/font-woff": [
        ".woff",
    ],
    "application/font-woff2": [
        ".woff2",
    ],
    "audio/3gpp": [
        ".3gp",
    ],
    "audio/3gpp2": [
        ".3g2",
    ],
    "audio/wav": [
        ".wav",
    ],
    "audio/opus": [
        ".opus",
    ],
    "audio/x-midi": [
        ".mid",
        ".midi",
    ],
    "audio/aac": [
        ".aac",
    ],
    "audio/x-m4a": [
        ".m4a",
    ],
    "audio/x-realaudio": [
        ".ra",
    ],
    "video/3gpp": [
        ".3gpp",
        ".3gp",
    ],
    "text/x-component": [
        ".htc",
    ],
    "text/html": [
        ".jsp",
        "php",
        ".django",
        ".ftl",
        ".shtml",
    ],
    "text/mathml": [
        ".mml",
    ],
    "text/x-script.python": [
        ".py",
        ".java",
        ".go",
    ],
    "text/x-script.perl": [
        ".pl",
    ],
    "text/x-script.shell": [
        ".sh",
    ],
    "text/x-python": [
        ".py",
        ".java",
        ".go",
    ],
    "text/x-shellscript": [
        ".sh",
    ],
    "text/x-perl": [
        ".pl",
    ],
    "text/x-java": [
        ".java",
        ".py",
        ".go",
    ],
    "text/javascript": [
        ".js",
        ".mjs",
    ],
    "application/ld+json": [
        ".jsonld",
    ],
    "text/x-ms-regedit": [
        ".reg",
    ],
    "text/troff": [
        ".1",
    ],
    "text/PGP": [
        ".txt",
    ],
    # fix for zip based files
    "application/zip": [
        ".whl",
        ".pages",
        ".xmind",
        ".wps",
        ".wpt",
        ".dps",
        ".dpt",
        ".et",
        ".ett",
        ".xps",
    ],
    # fix for wps
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx",
        ".doc",
        ".dot",
        ".wps",
        ".wpt",
    ],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [
        ".dps",
        ".dpt",
    ],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".et",
        ".ett",
    ],
    # fix for text/xml
    "application/xml": [
        ".xml",
        ".xsl",
        ".wsdl",
        ".svg",
        ".xsd",
        ".bpmn",
    ],
    "text/xml": [
        ".xml",
        ".xsl",
        ".wsdl",
        ".svg",
        ".xsd",
        ".bpmn",
    ],
    # fix for programming source code and config files
    "text/plain": [
        "",
        ".wsdl",
        ".bpmn",
        ".gitignore",
        ".py",
        ".pl",
        ".sh",
        ".pl",
        ".java",
        ".c",
        ".h",
        ".hpp",
        ".cpp",
        ".json",
        ".yml",
        ".yaml",
        ".sql",
        ".css",
        ".js",
        ".json",
        ".django",
        ".html",
        ".htm",
        ".xml",
        ".xsl",
        ".out",
        ".jsp",
        ".php",
        ".log",
        ".conf",
        ".cnf",
        ".ini",
        ".properties",
        ".rules",
        ".cnf",
        ".pem",
        ".pub",
        ".crt",
        ".key",
        ".cmd",
        ".bat",
        ".pxd",
        ".pyi",
        ".md",
        ".rst",
        ".in",
        ".bashrc",
        ".bash_profile",
        ".bash_history",
        ".csv",
        ".reg",
        ".inf",
        ".less",
        ".scss",
        ".ftl",
        ".xsd",
        ".htaccess",
        ".pm",
        ".pl",
        ".js",
        ".mjs",
        ".jsonld",
    ],
    # 'application/vnd.binary' equivalent to 'application/octet-stream'
    "application/vnd.binary": [
        "",
        ".a",
        ".bin",
        ".bpk",
        ".dat",
        ".data",
        ".deploy",
        ".dist",
        ".distz",
        ".dll",
        ".dms",
        ".dump",
        ".elc",
        ".exe",
        ".lrf",
        ".mar",
        ".mobipocket-ebook",
        ".o",
        ".obj",
        ".pkg",
        ".so",
        ".img",
        ".dmg",
        ".backup",
        ".bak",
        ".woff",
        ".woff2",
        ".DS_Store",
        ".deb",
        ".iso",
        ".msm",
        ".msi",
        ".msp",
    ],
    # fix for .dat, data
    "application/octet-stream": [
        "",
        ".a",
        ".bin",
        ".bpk",
        ".dat",
        ".data",
        ".deploy",
        ".dist",
        ".distz",
        ".dll",
        ".dms",
        ".dump",
        ".elc",
        ".exe",
        ".lrf",
        ".mar",
        ".mobipocket-ebook",
        ".o",
        ".obj",
        ".pkg",
        ".so",
        ".img",
        ".dmg",
        ".backup",
        ".bak",
        ".woff",
        ".woff2",
        ".DS_Store",
        ".deb",
        ".iso",
        ".msm",
        ".msi",
        ".msp",
    ],
    "application/rss+xml": [
        ".rss",
    ],
    "application/x-rar-compressed": [
        ".rar",
    ],
    "audio/midi": [
        ".kar",
        ".mid",
        ".midi",
    ],
    "video/mp2t": [
        ".ts",
    ],
    "video/x-m4v": [
        ".m4v",
    ],
    "video/x-ms-asf": [
        ".asx",
        ".asf",
    ],
    "application/x-freearc": [
        ".arc",
    ],
    "application/vnd.amazon.ebook": [
        ".azw",
    ],
    "application/x-bzip": [
        ".bz",
    ],
    "audio/webm": [
        ".weba",
    ],
    "video/3gpp2": [
        ".3g2",
    ],
    # ===================================================================
    # Hacks
    # ===================================================================
    # fix some old libimage treat java source code as c source code.
    "text/x-c": [
        ".java",
    ],
    # fix magic treat doc file as .cdfv2 file.
    "application/CDFV2": [
        ".doc",
        ".fla",
    ],
}


def register_mimetype_extensions(data):
    """data is a dict with key as mimetype and value as extensions, e.g.
    {
        "application/mspowerpoint": ['.ppt', '.pot', '.ppa', '.pps', '.pwz'],
    }
    """
    for mimetype, extra_exts in data.items():
        if isinstance(extra_exts, str):
            extra_exts = [extra_exts]
        if mimetype in EXTRA_MIMETYPE_EXTENSIONS:
            EXTRA_MIMETYPE_EXTENSIONS[mimetype] += extra_exts
        else:
            EXTRA_MIMETYPE_EXTENSIONS[mimetype] = [] + extra_exts


def guess_all_extensions(mimetype):
    mimetype = mimetype or "text/plain"
    exts = mimetypes.guess_all_extensions(mimetype)
    extra_exts = EXTRA_MIMETYPE_EXTENSIONS.get(mimetype, [])
    result = list(set(exts + extra_exts))
    result.sort()
    return result


def get_mimetype_by_extension(ext):
    mimetype = mimetypes.types_map.get(ext, None)
    if mimetype is None:
        for mt, exts in EXTRA_MIMETYPE_EXTENSIONS.items():
            if ext in exts:
                return mt
    return mimetype
