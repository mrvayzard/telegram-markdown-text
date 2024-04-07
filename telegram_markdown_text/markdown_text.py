from abc import ABC


class MarkdownText(ABC):
    def __init__(self, *parts):
        _parts = map(
            lambda part: PlainText(part) if isinstance(part, str) else part, parts
        )
        self.parts = list(_parts)

    def __add__(self, other):
        if isinstance(other, str):
            return MarkdownText(self, PlainText(other))
        elif isinstance(other, MarkdownText):
            return MarkdownText(self, other)
        else:
            raise ValueError('This data type is not supported for [other] parameter')

    def __str__(self):
        return self.escaped_text()

    def append(self, element):
        if isinstance(element, str):
            self.parts.append(PlainText(element))
        elif isinstance(element, MarkdownText):
            self.parts.append(element)
        else:
            raise ValueError('This data type is not supported for [element] parameter')

        return self

    def append_ln(self):
        return self.append(PlainText('\n'))

    def escaped_text(self):
        return ''.join(part.escaped_text() for part in self.parts)


class _StyledText(MarkdownText):
    def __init__(self, text: str | MarkdownText):
        if isinstance(text, str):
            _parts = [PlainText(text)]
        elif isinstance(text, MarkdownText):
            _parts = [text]
        else:
            raise ValueError('This data type is not supported for [text] parameter')

        super().__init__(*_parts)

    @property
    def leading_mark(self):
        return ''

    @property
    def trailing_mark(self):
        return ''

    def escaped_text(self):
        return self.leading_mark + super().escaped_text() + self.trailing_mark


class Bold(_StyledText):
    @property
    def leading_mark(self): return '*'

    @property
    def trailing_mark(self): return '*'


class Strikethrough(_StyledText):
    @property
    def leading_mark(self): return '~'

    @property
    def trailing_mark(self): return '~'


class Spoiler(_StyledText):
    @property
    def leading_mark(self): return '||'

    @property
    def trailing_mark(self): return '||'


class Italic(_StyledText):
    @property
    def leading_mark(self): return '_'

    @property
    def trailing_mark(self): return '_'

    def escaped_text(self):
        text = ''.join(part.escaped_text() for part in self.parts)
        text = _fix_underscore_ambiguity(text)
        return self.leading_mark + text + self.trailing_mark


class Underline(_StyledText):
    @property
    def leading_mark(self): return '__'

    @property
    def trailing_mark(self): return '__'

    def escaped_text(self):
        text = ''.join(part.escaped_text() for part in self.parts)
        text = _fix_underscore_ambiguity(text)
        return self.leading_mark + text + self.trailing_mark


class InlineUrl(_StyledText):
    def __init__(self, text: str | MarkdownText, url: str):
        if isinstance(url, str):
            self._url = url
        else:
            raise ValueError('This data type is not supported for [url] parameter')

        super().__init__(text)

    @property
    def leading_mark(self):
        return '['

    @property
    def trailing_mark(self):
        return ']'

    def escaped_text(self):
        return super().escaped_text() + f'({_escape_url(self._url)})'


class InlineUser(InlineUrl):
    def __init__(self, text: str | MarkdownText, user_id: str | int):
        if isinstance(user_id, (str, int)):
            super().__init__(text, f'tg://user?id={user_id}')
        else:
            raise ValueError('This data type is not supported for [user_id] parameter')


class Emoji(InlineUrl):
    def __init__(self, emoji: str, custom_emoji_id: str | int):
        if isinstance(custom_emoji_id, (str, int)):
            super().__init__(emoji, f'tg://emoji?id={custom_emoji_id}')
        else:
            raise ValueError('This data type is not supported for [custom_emoji_id] parameter')

    def escaped_text(self):
        return '!' + super().escaped_text()


class InlineCode(_StyledText):
    @property
    def leading_mark(self):
        return '`'

    @property
    def trailing_mark(self):
        return '`'


class InlineCodeBlock(_StyledText):
    def __init__(self, text: str, language: str = ''):
        self._language = language

        super().__init__(text)

    @property
    def leading_mark(self):
        return f'```{self._language}\n'

    @property
    def trailing_mark(self):
        return '\n```'


class QuoteBlock(MarkdownText):
    """Important! QuoteBlock should be added from a new line only."""

    def escaped_text(self):
        escaped_lines = super().escaped_text().split('\n')
        quoted_lines = map(
            lambda line: '>' + line if (len(line) > 0) else line,
            escaped_lines
        )
        return '\n'.join(quoted_lines) + '**\r'


class PlainText(MarkdownText):
    def __init__(self, text: str):
        if isinstance(text, str):
            self.text = text
        else:
            raise ValueError('This data type is not supported for [text] parameter')

        super().__init__([])

    def escaped_text(self):
        return _escape_markdown(self.text)


def _fix_underscore_ambiguity(text: str):
    updated_text = text

    if text.startswith('_'):
        updated_text = '\r' + updated_text

    if text.endswith('_'):
        updated_text = updated_text + '\r'

    return updated_text


def _escape_markdown(text: str):
    chars_to_escape = {'_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'}
    escaped_text = ''.join(['\\' + char if char in chars_to_escape else char for char in text])
    return escaped_text


def _escape_url(url: str):
    chars_to_escape = {'\\', ')'}
    escaped_text = ''.join(['\\' + char if char in chars_to_escape else char for char in url])
    return escaped_text
