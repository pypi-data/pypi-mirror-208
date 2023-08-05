'''
See COPYRIGHT.md for copyright information.
'''
from regex import compile as re_compile, match as re_match, DOTALL as re_DOTALL

edgarAdditionalTags = {
    "listing",
    "plaintext",
    "strike",
    "xmp",
    "page",
    "exibitindex",
    "r",
    "segments",
    "segment",
    "module",
    "name",
    "cik",
    "ccc"
    } | set("f{}".format(i) for i in range(1,100))
disallowedElements = {
    "abbrev",
    "acronym",
    "applet",
    "area",
    "au",
    "banner",
    "base",
    "basefont",
    "bgsound",
    "blink",
    "col",
    "colgroup",
    "credit",
    "del",
    "embed",
    "fig",
    "fn",
    "form",
    "frame",
    "frameset",
    "input",
    "ins",
    "lang",
    "lh",
    "map",
    "marquee",
    "nextid",
    "nobr",
    "noembed",
    "noframe",
    "noframes",
    "note",
    "object",
    "option",
    "overlay",
    "param",
    "person",
    "q",
    "range",
    "s",
    "script",
    "select",
    "spot",
    "style",
    "tab",
    "tbody",
    "textarea",
    "tfoot",
    "thead",
    "wbr",
    "empty"
    }

disallowedElementAttrs = {
    "body": ("background",),
    "meta": ("http-equiv",),
    "*": {
        "onabort",
        "onafterprint",
        "onbeforeprint",
        "onbeforeunload",
        "onblur",
        "oncanplay",
        "oncanplaythrough",
        "onchange",
        "onclick",
        "oncontextmenu",
        "oncopy",
        "oncuechange",
        "oncut",
        "ondblclick",
        "ondrag",
        "ondragend",
        "ondragenter",
        "ondragleave",
        "ondragover",
        "ondragstart",
        "ondrop",
        "ondurationchange",
        "onemptied",
        "onended",
        "onerror",
        "onfocus",
        "onhashchange",
        "oninput",
        "oninvalid",
        "onkeydown",
        "onkeypress",
        "onkeyup",
        "onload",
        "onloadeddata",
        "onloadedmetadata",
        "onloadstart",
        "onmessage",
        "onmousedown",
        "onmousemove",
        "onmouseout",
        "onmouseover",
        "onmouseup",
        "onmousewheel",
        "onoffline",
        "ononline",
        "onpagehide",
        "onpageshow",
        "onpaste",
        "onpause",
        "onplay",
        "onplaying",
        "onpopstate",
        "onprogress",
        "onratechange",
        "onreset",
        "onresize",
        "onscroll",
        "onsearch",
        "onseeked",
        "onseeking",
        "onselect",
        "onshow",
        "onstalled",
        "onstorage",
        "onsubmit",
        "onsuspend",
        "ontimeupdate",
        "ontoggle",
        "onunload",
        "onvolumechange",
        "onwaiting",
        "onwheel"
        }
    }
requiredElementAttrs = {
    "img": {"src"}
    }
recognizedElements = {
    "address",
    "b",
    "big",
    "blockquote",
    "br",
    "caption",
    "center",
    "cite",
    "code",
    "dd",
    "dfn",
    "dir",
    "div",
    "dl",
    "dt",
    "em",
    "font",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "hr",
    "i",
    "img",
    "isindex",
    "kbd",
    "li",
    "menu",
    "ol",
    "p",
    "pre",
    "samp",
    "small",
    "strong",
    "sub",
    "sup",
    "td",
    "th",
    "title",
    "tr",
    "tt",
    "u",
    "ul",
    "var"
    } | edgarAdditionalTags
