"""This is a module that implements a lexer in python."""
from typing import Callable, Protocol


class LexerProtocol(Protocol):
    """
    A lexer protocol that has to implement an iterator that tokenizes a string,
    takes content (str) and returns an iterator which yields strings
    """

    def __init__(self, content: str):
        ...

    def __iter__(self):
        ...

    def __next__(self) -> str:
        ...


class Lexer:
    """
    A lexer class that tokenizes a string.  (Iterator)
    Can also be used with a set of special terms that will be treated as one token,
    this might be useful when tokenizing something like programming languages for e.g. [c#, .net]
    so they wont be split

    Attrs:
        content : str
        special_terms : (set[str] | None)

    Usage:
        basic:
        >>> lexer = Lexer("Hello, World!")
        >>> list(lexer)
        ['hello', ',', 'world', '!']

        with special terms:
        >>> special_terms = {"world!"}
        >>> lexer = Lexer("Hello, World!", special_terms=special_terms)
        >>> list(lexer)
        ['hello', ',', 'world!']
    """

    def __init__(self, content: str, special_terms: set[str] | None = None):
        """
        Creates a lexer iterator from the given string contents

        Args:
            content : str
                The string to be tokenized
            special_terms : set[str] (optional)
                A set of special terms to be treated as one term

        Returns:
            self : Lexer
                A lexer iterator with tokenized strings

        Note:
            The special_terms set is case insensitive.
        """
        self.content = content.lower()
        self.special_terms = special_terms

    def chop(self, n: int) -> str:
        """Chops of n characters from the content and returns them."""
        token = self.content[:n]
        self.content = self.content[n:]
        return token

    def trim_left(self):
        """Removes leading whitespace"""
        self.content = self.content.lstrip()

    def chop_while(self, condition: Callable) -> str:
        """Collects characters from the content while the condition is true."""
        n = 0
        while n < len(self.content) and condition(self.content[n]):
            n += 1
        return self.chop(n)

    def next_token(self) -> str | None:
        """Retrieves the next token from the content."""
        self.trim_left()
        if len(self.content) == 0:
            return None

        if self.special_terms is not None:
            for term in self.special_terms:
                if self.content.startswith(term.lower()):
                    return self.chop(len(term))

        if self.content[0].isnumeric():
            return self.chop_while(lambda x: x.isnumeric())

        if self.content[0].isalpha():
            term = self.chop_while(lambda x: x.isalnum())
            # TODO: add steming
            return term

        return self.chop(1)

    def __iter__(self):
        return self

    def __next__(self) -> str:
        token = self.next_token()
        if token is None:
            raise StopIteration
        return token


def lexify(content: str, special_terms: set[str] | None = None) -> list[str]:
    """
    Tokenizes a string.
    Can also be used with a set of special terms that will be treated as one token,
    this might be useful when tokenizing something like programming languages for e.g. [c#, .net]
    so they wont be split

    Args:
        content : str
            The string to be tokenized
        special_terms : set[str] | None (optional)
            A set of special terms to be treated as one term

    Returns:
        list[str]: list of tokens
    """
    lexer = Lexer(content, special_terms=special_terms)
    return list(lexer)
