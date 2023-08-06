from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern
import xml.etree.ElementTree as etree
from pybtex.database.input import bibtex

from collections import OrderedDict
import re

BRACKET_RE = re.compile(r"\[([^\[]+)\]")
CITE_RE = re.compile(r"@(\w+)")
DEF_RE = re.compile(r"\A {0,3}\[@(\w+)\]:\s*(.*)")
INDENT_RE = re.compile(r"\A\t| {4}(.*)")

CITATION_RE = r"@(\w+)"


class Bibliography(object):
    """Keep track of document references and citations for exporting"""

    def __init__(self, extension, bibtex_file, order):
        self.extension = extension
        self.order = order

        self.citations = OrderedDict()
        self.references = dict()
        self.num_keys = dict()

        if bibtex_file:
            try:
                parser = bibtex.Parser()
                self.bibsource = parser.parse_file(bibtex_file).entries
            except Exception as e:
                print(f"Error loading bibtex file - {e}")
                self.bibsource = dict()
        else:
            self.bibsource = dict()

    def addCitation(self, citekey):
        self.citations[citekey] = self.citations.get(citekey, 0) + 1
        if citekey not in self.num_keys: self.num_keys[citekey] = len(self.citations)

    def setReference(self, citekey, reference):
        self.references[citekey] = reference

    def citationID(self, citekey):
        return "cite-" + citekey

    def referenceID(self, citekey):
        return "ref-" + citekey

    def formatAuthor(self, author):
        out = "%s %s." % (author.last()[0], author.first()[0][0])
        if author.middle():
            out += "%s." % (author.middle()[0][0])
        return out

    def formatReference(self, ref):
        authors = ", ".join(map(self.formatAuthor, ref.persons["author"]))
        title = ref.fields["title"]
        journal = ref.fields.get("journal", "")
        volume = ref.fields.get("volume", "")
        year = ref.fields.get("year")

        reference = "%s: <i>%s</i>." % (authors, title)
        if journal:
            reference += " %s." % journal
            if volume:
                reference += " <b>%s</b>," % volume

        reference += " (%s)" % year

        return reference

    def makeBibliography(self, root):
        if self.order == "alphabetical":
            raise (NotImplementedError)

        div = etree.Element("div")
        div.set("class", "references")

        if not self.citations:
            return div

        table = etree.SubElement(div, "table")
        tbody = etree.SubElement(table, "tbody")
        for id in self.citations:
            tr = etree.SubElement(tbody, "tr")
            tr.set("id", self.referenceID(id))
            ref_id = etree.SubElement(tr, "td")
            ref_id.text = f"[{self.num_keys[id]}]"
            ref_txt = etree.SubElement(tr, "td")
            if id in self.references:
                self.extension.parser.parseChunk(ref_txt, self.references[id])
            elif id in self.bibsource:
                ref_txt.text = self.formatReference(self.bibsource[id])
            else:
                ref_txt.text = "Missing citation"

        return div


class CitationsPreprocessor(Preprocessor):
    """Gather reference definitions and citation keys"""

    def __init__(self, bibliography):
        super().__init__()
        self.bib = bibliography

    def subsequentIndents(self, lines, i):
        """Concatenate consecutive indented lines"""
        linesOut = []
        while i < len(lines):
            m = INDENT_RE.match(lines[i])
            if m:
                linesOut.append(m.group(1))
                i += 1
            else:
                break
        return " ".join(linesOut), i

    def run(self, lines):
        linesOut = []
        i = 0

        while i < len(lines):
            # Check to see if the line starts a reference definition
            m = DEF_RE.match(lines[i])
            if m:
                key = m.group(1)
                reference = m.group(2)
                indents, i = self.subsequentIndents(lines, i + 1)
                reference += " " + indents

                self.bib.setReference(key, reference)
                continue

            # Look for all @citekey patterns inside hard brackets
            for bracket in BRACKET_RE.findall(lines[i]):
                for c in CITE_RE.findall(bracket):
                    self.bib.addCitation(c)
            linesOut.append(lines[i])
            i += 1

        return linesOut


class CitationsPattern(Pattern):
    """Handles converting citations keys into links"""

    def __init__(self, pattern, bibliography):
        super(CitationsPattern, self).__init__(pattern)
        self.bib = bibliography

    def handleMatch(self, m):
        id = m.group(2)
        if id in self.bib.citations:
            a = etree.Element("a")
            a.set("id", self.bib.citationID(id))
            a.set("href", "#" + self.bib.referenceID(id))
            a.set("class", "citation")
            a.text = f"{self.bib.num_keys[id]}"

            return a
        else:
            return None


class CitationsTreeprocessor(Treeprocessor):
    """Add a bibliography/reference section to the end of the document"""

    def __init__(self, bibliography):
        super().__init__()
        self.bib = bibliography

    def run(self, root):
        citations = self.bib.makeBibliography(root)
        root.append(citations)


class CitationsExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            "bibtex_file": ["", "Bibtex file path"],
            "order": ["unsorted", "Order of the references (unsorted, alphabetical)"],
        }
        super(CitationsExtension, self).__init__(*args, **kwargs)
        self.bib = Bibliography(
            self,
            self.getConfig("bibtex_file"),
            self.getConfig("order"),
        )

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.parser = md.parser
        self.md = md

        md.preprocessors.register(CitationsPreprocessor(self.bib), "mdx_bib", 10)
        md.inlinePatterns.register(
            CitationsPattern(CITATION_RE, self.bib), "mdx_bib", 20
        )
        md.treeprocessors.register(CitationsTreeprocessor(self.bib), "mdx_bib", 30)


def makeExtension(*args, **kwargs):
    return CitationsExtension(*args, **kwargs)
