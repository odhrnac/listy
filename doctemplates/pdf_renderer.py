"""Print letters to PDF in headless Chromium (Playwright), from the same HTML document the editor preview shows.

Setup on a new computer:  pip install playwright   (and optionally: playwright install chromium).
Without Playwright's own Chromium, Microsoft Edge or Google Chrome installed on the computer is used.
"""
import os
from urllib.parse import unquote, urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.exceptions import SuspiciousFileOperation
from django.utils._os import safe_join

from .rendering import letter_document

PLAYWRIGHT_MISSING = 'PDF generation (v2) needs Playwright. Install it with: pip install playwright'

# The letter is loaded from this made-up address; every request is answered from local files, nothing goes online
ORIGIN = 'http://letter.local'


class LetterRenderer:
    """One browser for a whole batch of letters:

        with LetterRenderer() as renderer:
            renderer.render(template, data, '/path/to/letter.pdf')
    """

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise RuntimeError(PLAYWRIGHT_MISSING) from e
        self._playwright = sync_playwright().start()
        try:
            self._browser = self._launch()
        except Exception:
            self._playwright.stop()
            raise
        self._page = self._browser.new_page()
        self._page.route('**/*', self._serve)
        self._html = ''
        return self

    def __exit__(self, *exc_info):
        self._browser.close()
        self._playwright.stop()

    def _launch(self):
        errors = []
        for channel in (None, 'msedge', 'chrome'):  # Playwright's Chromium, then the browsers found on Windows PCs
            try:
                return self._playwright.chromium.launch(channel=channel)
            except Exception as e:
                errors.append(f'{channel or "chromium"}: {str(e).splitlines()[0]}')
        raise RuntimeError('No browser for PDF generation found. Run "playwright install chromium". '
                           + ' | '.join(errors))

    def _serve(self, route):
        path = unquote(urlsplit(route.request.url).path)
        if path == '/letter':
            return route.fulfill(body=self._html, content_type='text/html; charset=utf-8')

        static_prefix = '/' + settings.STATIC_URL.strip('/') + '/'
        file_path = None
        if path.startswith(settings.MEDIA_URL):
            try:
                file_path = safe_join(settings.MEDIA_ROOT, path[len(settings.MEDIA_URL):])
            except SuspiciousFileOperation:
                pass
        elif path.startswith(static_prefix):
            file_path = finders.find(path[len(static_prefix):])

        if file_path and os.path.isfile(file_path):
            route.fulfill(path=file_path)
        else:
            route.fulfill(status=404, body='')

    def render(self, template, data, output_path):
        """Write one letter (template filled with data) as a PDF file."""
        self._html = letter_document(template, data, for_pdf=True)
        self._page.goto(f'{ORIGIN}/letter')
        self._page.wait_for_function("document.documentElement.dataset.paginated === '1'")
        self._page.pdf(path=output_path, prefer_css_page_size=True, print_background=True)
