SINGLE_LINE_COMMENT_PATTERNS = {
    'slash': r'//[^\n]*',           # For languages using // comments
    'hash': r'#[^\n]*',             # For Python-style # comments
    'html': r'<!--[^\n]*-->',       # For HTML comments
    'css': r'/\*[^\n]*?\*/'         # For CSS-style single line comments
}


BLOCK_COMMENT_PATTERNS = {
    'c_style': r'/\*[\s\S]*?\*/',           # For C-style /* */ comments
    'python': r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',  # For Python docstrings
    'html': r'<!--[^\n]*-->'                # For HTML comments
}

LANGUAGE_COMMENT_STYLES = {
    'python': {'inline': 'hash', 'block': 'python'},
    'javascript': {'inline': 'slash', 'block': 'c_style'},
    'java': {'inline': 'slash', 'block': 'c_style'},
    'go': {'inline': 'slash', 'block': 'c_style'},
    'rust': {'inline': 'slash', 'block': 'c_style'},
    'c': {'inline': 'slash', 'block': 'c_style'},
    'cpp': {'inline': 'slash', 'block': 'c_style'},
    'csharp': {'inline': 'slash', 'block': 'c_style'},
    'php': {'inline': 'slash', 'block': 'c_style'},
    'ruby': {'inline': 'hash', 'block': 'c_style'},
    'swift': {'inline': 'slash', 'block': 'c_style'},
    'kotlin': {'inline': 'slash', 'block': 'c_style'},
    'html': {'inline': 'html', 'block': 'html'},
    'css': {'inline': 'css', 'block': 'c_style'},
    'scss': {'inline': 'css', 'block': 'c_style'},
    'sass': {'inline': 'css', 'block': 'c_style'},
    'less': {'inline': 'css', 'block': 'c_style'}
}

COMMON_PATTERNS = {
    'empty_lines': r'\n\s*\n',
    'trailing_whitespace': r'[ \t]+$',
    'multiple_spaces': r' {2,}',
    'inline_comments': {
        lang: SINGLE_LINE_COMMENT_PATTERNS[style['inline']]
        for lang, style in LANGUAGE_COMMENT_STYLES.items()
    },
    'block_comments': {
        lang: BLOCK_COMMENT_PATTERNS[style['block']]
        for lang, style in LANGUAGE_COMMENT_STYLES.items()
    }
}
