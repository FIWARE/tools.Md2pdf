#!/usr/bin/env python

import unittest
from markdown_to_pdf import *

class TestMarkdownToPdf( unittest.TestCase ):
    def test_get_markdown_header_level(self):
        self.assertEqual( get_markdown_header_level( 'No header' ), 0 )
        self.assertEqual( get_markdown_header_level( '# Header 1' ), 1 )
        self.assertEqual( get_markdown_header_level( '  # Header 1' ), 0 )
        self.assertEqual( get_markdown_header_level( '## Header 2' ), 2 )
        self.assertEqual( get_markdown_header_level( '### Header 3' ), 3 )
        self.assertEqual( get_markdown_header_level( '#### Header 4' ), 4 )
        self.assertEqual( get_markdown_header_level( '##### Header 5' ), 5 )
        self.assertEqual( get_markdown_header_level( '###### Header 6' ), 6 )


    def test_generate_pandoc_header_id(self):
        self.assertEqual( generate_pandoc_header_id( 'dirA', '# Header' ), '{#diraheader}' )
        self.assertEqual( generate_pandoc_header_id( 'dirA/dirA1', '# Markdown Header' ), '{#diradira1markdown-header}' )
        self.assertEqual( generate_pandoc_header_id( 'dirA/dirA1', '### Header' ), '{#diradira1header}' )
        self.assertEqual( generate_pandoc_header_id( 'dirA/dirA1', '### 1?2<3>4?5(6)7&8"9\'10=11/12' ), '{#diradira1123456789101112}' )


    def test_generate_pandoc_section_id(self):
        self.assertEqual( generate_pandoc_section_id( 'filemd' ), '{#filemd}' )
        self.assertEqual( generate_pandoc_section_id( 'dir/filemd' ), '{#dirfilemd}' )
        self.assertEqual( generate_pandoc_section_id( 'dir1/dir2/filemd' ), '{#dir1dir2filemd}' )


    def test_slugify_string(self):
        self.assertEqual( slugify_string( 'String' ), 'string' )
        self.assertEqual( slugify_string( 'String with spaces' ), 'string-with-spaces' )
        self.assertEqual( slugify_string( '1?2<3>4?5(6)7&8"9\'10=11/12' ), '123456789101112' )


    def test_prevent_latex_images_floating(self):
        self.assertEqual( prevent_latex_images_floating( '![](foo.png)' ), '![](foo.png)\ ' )
        self.assertEqual( prevent_latex_images_floating( '![foo](bar.png)' ), '![foo](bar.png)\ ' )
        self.assertEqual( prevent_latex_images_floating( '![foo](bar.png)\n' ), '![foo](bar.png)\ \n' )


    def test_is_an_url(self):
        self.assertEqual( is_an_url( 'www.google.com' ), True )
        self.assertEqual( is_an_url( 'http://www.google.com' ), True )
        self.assertEqual( is_an_url( 'http:/www.google.com' ), False )
        self.assertEqual( is_an_url( 'https://www.google.com' ), True )


    def test_generate_pandoc_header_ids(self):
        self.assertEqual( generate_pandoc_header_ids('# Header', 'file.md'), '# Header {#filemdheader}\n' )
        self.assertEqual( generate_pandoc_header_ids('```\n# Header\n```', 'file.md'), '```\n# Header\n```\n' )
        self.assertEqual( generate_pandoc_header_ids(' ```\n# Header\n```', 'file.md'), ' ```\n# Header\n```\n' )
        self.assertEqual( generate_pandoc_header_ids('\t```\n# Header\n```', 'file.md'), '\t```\n# Header\n```\n' )
        self.assertEqual( generate_pandoc_header_ids('`# Header`', 'file.md'), '`# Header`\n' )


    def test_process_header_html_anchors(self):
        inputStr = '#<a name="top"></a>Filtering results'
        expectedOuputStr = (
            "#Filtering results\n" +
            "\n" +
            "\\phantomsection\n" +
            "\\label{filemdtop}\n"
        )
        self.assertEqual( process_header_html_anchors( inputStr, 'file.md' ), expectedOuputStr )


    def test_make_header_id_unique(self):
        user_ids = {}
        self.assertEqual( make_header_id_unique( 'header', user_ids ), 'header' )
        self.assertEqual( user_ids, { 'header': 1 } )

        self.assertEqual( make_header_id_unique( 'header', user_ids ), 'header-1' )
        self.assertEqual( user_ids, { 'header': 2 } )

        self.assertEqual( make_header_id_unique( 'header', user_ids ), 'header-2' )
        self.assertEqual( user_ids, { 'header': 3 } )

        self.assertEqual( make_header_id_unique( 'new-header', user_ids ), 'new-header' )
        self.assertEqual( user_ids, { 'header': 3, 'new-header': 1 } )

        self.assertEqual( make_header_id_unique( 'new-header', user_ids ), 'new-header-1' )
        self.assertEqual( user_ids, { 'header': 3, 'new-header': 2 } )


if __name__ == "__main__":
    unittest.main()
