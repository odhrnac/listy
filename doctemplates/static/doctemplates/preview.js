// Splits a template preview into A4 pages.
//
// The rendered body (.tpl-source) is moved block by block into copies of the page
// skeleton (<template class="tpl-page">). A block that does not fit moves to the next
// page, and a block with CSS "break-before: page" always starts a new page. When the
// whole body is one wrapper element (e.g. <div class="letter">…</div>), its children
// are split instead and every page gets its own copy of the wrapper.
// Images and fields marked data-page="first"/"last" are kept only on that page.
(function () {
    function isBlank(node) {
        return node.nodeType === Node.COMMENT_NODE || (node.nodeType === Node.TEXT_NODE && !node.textContent.trim());
    }

    function forcesBreak(node) {
        if (node.nodeType !== Node.ELEMENT_NODE) return false;
        return ['page', 'always', 'left', 'right'].includes(getComputedStyle(node).breakBefore);
    }

    function paginate(preview) {
        const source = preview.querySelector('.tpl-source');
        const skeleton = preview.querySelector('template.tpl-page');
        const pagesBox = preview.querySelector('.tpl-pages');

        const elements = [...source.children];
        const wrapper = elements.length === 1 && ![...source.childNodes].some(n => n.nodeType === Node.TEXT_NODE && !isBlank(n))
            ? elements[0] : null;
        const blocks = [...(wrapper || source).childNodes].filter(n => !isBlank(n));

        const pages = [];
        let body, target;

        function newPage() {
            const copy = skeleton.content.cloneNode(true);
            pages.push({ label: copy.querySelector('.tpl-page-label'), box: copy.querySelector('.tpl-page-box') });
            body = copy.querySelector('.tpl-body');
            target = wrapper ? body.appendChild(wrapper.cloneNode(false)) : body;
            pagesBox.appendChild(copy);
        }

        function overflows() {
            return body.scrollHeight > body.clientHeight + 1;
        }

        newPage();
        for (const block of blocks) {
            const pageHasContent = target.childNodes.length > 0;
            target.appendChild(block);
            if (pageHasContent && (forcesBreak(block) || overflows())) {
                newPage();
                target.appendChild(block);
            }
        }

        pages.forEach((page, i) => {
            if (page.label) page.label.textContent = `Page ${i + 1} / ${pages.length}`;
            page.box.querySelectorAll('[data-page="first"]').forEach(el => { if (i !== 0) el.remove(); });
            page.box.querySelectorAll('[data-page="last"]').forEach(el => { if (i !== pages.length - 1) el.remove(); });
        });
    }

    function run() {
        document.querySelectorAll('.tpl-preview').forEach(paginate);
    }

    // Page breaks depend on text height, so load the letter's fonts (@font-face in the template CSS) first.
    // The body is hidden until it is paginated, so the browser would not start loading them on its own.
    window.addEventListener('load', () => {
        Promise.all([...document.fonts].map(font => font.load().catch(() => null))).then(run);
    });
})();
