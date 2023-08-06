# Copyright (C) 2021,2022,2023 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Convert and back source text file into text as well."""

import logging

from reportlab.lib.pagesizes import A5, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from txt2ebook.formats.base import BaseWriter
from txt2ebook.models import Chapter, Volume

logger = logging.getLogger(__name__)


class PdfDocTemplate(SimpleDocTemplate):
    """Custom PDF template."""

    def afterFlowable(self, flowable):
        """Registers TOC entries."""
        if flowable.__class__.__name__ == "Paragraph":
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == "Heading1":
                self.notify("TOCEntry", (0, text, self.page))
            if style == "Heading2":
                self.notify("TOCEntry", (2, text, self.page))


class PdfWriter(BaseWriter):
    """Module for writing ebook in PDF format."""

    def __post_init__(self):
        """Post init code."""
        pdf_filename = self._output_filename(".pdf")
        logger.info("Create pdf file: %s", pdf_filename.resolve())

        self._init_styles()
        self.doc = PdfDocTemplate(
            str(pdf_filename),
            pagesize=portrait(A5),
            title=self.book.title,
            author=", ".join(self.book.authors),
        )

    def write(self) -> None:
        """Generate PDF files."""
        pdf = []
        pdf.append(self.to_title(self.book.title))
        pdf.append(self.to_title(", ".join(self.book.authors)))
        pdf.append(PageBreak())

        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                name="TOCHeading1",
                fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
                fontSize=12,
                firstLineIndent=0,
                leftIndent=0,
            ),
            ParagraphStyle(
                name="TOCHeading2",
                fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
                fontSize=12,
                firstLineIndent=0,
                leftIndent=0,
            ),
        ]
        pdf.append(self.to_title(self._("toc")))
        pdf.append(toc)
        pdf.append(PageBreak())

        for section in self.book.toc:
            if isinstance(section, Volume):
                logger.info("Create PDF volume : %s", section.title)
                pdf.append(self.to_title(section.title, "Heading1"))
                pdf.append(PageBreak())
                for chapter in section.chapters:
                    logger.info("Create PDF chapter : %s", chapter.title)
                    self.to_chapter(pdf, chapter)
            if isinstance(section, Chapter):
                self.to_chapter(pdf, section)

        self.doc.multiBuild(pdf)

    def _init_styles(self) -> None:
        pdfmetrics.registerFont(
            TTFont(
                self.langconf.DEFAULT_PDF_FONT_NAME,
                self.langconf.DEFAULT_PDF_FONT_FILE,
            )
        )

        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name=self.language,
                fontName=self.langconf.DEFAULT_PDF_FONT_NAME,
                fontSize=12,
                spaceAfter=12,
                leading=16,
                firstLineIndent=24,
            )
        )

    def to_title(self, words: str, style: str = "title") -> str:
        """Create the title for the section."""
        font_name = self.langconf.DEFAULT_PDF_FONT_NAME
        return Paragraph(
            f"<font name='{font_name}'>{words}</font>",
            self.styles[style],
        )

    def to_chapter(self, pdf, chapter):
        """Generate each chapter."""
        pdf.append(self.to_title(chapter.title, "Heading2"))
        for paragraph in chapter.paragraphs:
            pdf.append(
                Paragraph(
                    paragraph.replace("\n", ""), self.styles[self.language]
                )
            )
        pdf.append(PageBreak())
