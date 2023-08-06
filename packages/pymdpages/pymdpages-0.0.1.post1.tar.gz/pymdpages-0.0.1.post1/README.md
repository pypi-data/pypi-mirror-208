# pymdpages: a minimalistic python-markdown static page generator for academic articles

## Installation

```bash
pip install pymdpages
```

## Usage

`pymdpages` requires that you have, within your working directory:

- `css/main.css` and `css/highlight.css` for main sheetstyling and Pygments syntax highlighting;
- `js/mathjax-config.js` to configure MathJax 3 to work;
- `bib/` containing bibliography references;
- `template/head.html` and `template/tail.html` as HTML templates to be used before and after the
  Markdown text.

This repository comes with example files. See the help information for how to pass these to
`pymdpages`:

```bash
pymdpages --help
```

Once you have these set up, simply do:

```bash
pymdpages markdown_file_1.md markdown_file_2.md ...
```

`pymdpages` will emulate the same file structure as the `.md` files you pass it, e.g. `a/b/c/d.md`
will create `out/a/b/c/d.html`.
