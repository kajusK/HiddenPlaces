"""Pagination utility."""
from typing import Tuple
from flask import url_for


class Pagination:
    """Pagination navigation.

    Attributes:
        current: Current page number
        next: Link to next page or None
        prev: Link to prev page or None
        pages: Dict of page_num: link
        show: Show pagination (more than 1 page)
    """
    # how many page numbers to show
    nav_len = 8
    # how many number show immediately before/after current page
    window_len = 2

    def __init__(self, current, pages, *args, **kwargs):
        """Initializes pagination object

        Call e.g. like Pagination(1, 10, 'some.route', route_arg1=foo).

        Args:
            current: Current page number (starts from 1)
            pages: Amount of pages available
            Rest of the arguments is passed to url_for generator
        """
        self.current = current
        self.prev = None
        self.next = None
        self.pages = {}
        self.show = True

        if pages <= 1:
            self.show = False
            return

        if current == 2:
            self.prev = url_for(*args, **kwargs)
        elif current != 1:
            self.prev = url_for(*args, **kwargs, page=current - 1)

        if current != pages:
            self.next = url_for(*args, **kwargs, page=current + 1)

        if pages <= self.nav_len:
            numbers = list(range(1, pages+1))
        else:
            win_from, win_to = self._get_window(current, pages)

            numbers = list(range(win_from, win_to + 1))
            lower = 1
            upper = pages
            while len(numbers) < self.nav_len:
                if lower < win_from:
                    numbers.append(lower)
                if upper > win_to and len(numbers) < self.nav_len:
                    numbers.append(upper)
                lower += 1
                upper -= 1

        numbers.sort()
        for number in numbers:
            self.pages[number] = url_for(*args, **kwargs, page=number)

    def _get_window(self, current: int, pages: int) -> Tuple[int, int]:
        """Generates window start/end around current page.

        The generated window has self.window_len items and current page
        is centered if possible.

        Args:
            current: Current page number (starts from 1)
            pages: Amount of all pages available
        Returns:
            win_from, win_to: Tuple with window edges
        """
        win_from = current - self.window_len
        win_to = current + self.window_len
        if win_from < 1:
            win_to += 1 + abs(win_from)
            win_from = 1
        if win_to > pages:
            win_from -= win_to - pages
            win_to = pages
            if win_from < 1:  # pylint: disable=consider-using-max-builtin
                win_from = 1
        return win_from, win_to
