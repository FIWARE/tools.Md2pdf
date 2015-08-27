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
        self.assertEqual( generate_pandoc_header_id( 'dirA', '# Header' ), '{#dirA__header}' )
        self.assertEqual( generate_pandoc_header_id( 'dirA/dirA1', '# Markdown Header' ), '{#dirA_dirA1__markdown-header}' )
        self.assertEqual( generate_pandoc_header_id( 'dirA/dirA1', '### Header' ), '{#dirA_dirA1__header}' )
        self.assertEqual( generate_pandoc_header_id( 'dirA/dirA1', '### 1?2<3>4?5(6)7&8"9\'10=11/12' ), '{#dirA_dirA1__1-2-3-4-5-6-7-8-9-10-11-12}' )


    def test_generate_pandoc_section_id(self):
        self.assertEqual( generate_pandoc_section_id( 'file.md' ), '{#file.md}' )
        self.assertEqual( generate_pandoc_section_id( 'dir/file.md' ), '{#dir_file.md}' )
        self.assertEqual( generate_pandoc_section_id( 'dir1/dir2/file.md' ), '{#dir1_dir2_file.md}' )


    def test_slugfy(self):
        self.assertEqual( slugfy( 'String' ), 'string' )
        self.assertEqual( slugfy( 'String with spaces' ), 'string-with-spaces' )
        self.assertEqual( slugfy( '1?2<3>4?5(6)7&8"9\'10=11/12' ), '1-2-3-4-5-6-7-8-9-10-11-12' )


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
        self.assertEqual( generate_pandoc_header_ids('# Header', 'file.md'), '# Header {#file.md__header}\n' )
        self.assertEqual( generate_pandoc_header_ids('```\n# Header\n```', 'file.md'), '```\n# Header\n```\n' )
        self.assertEqual( generate_pandoc_header_ids(' ```\n# Header\n```', 'file.md'), ' ```\n# Header\n```\n' )
        self.assertEqual( generate_pandoc_header_ids('\t```\n# Header\n```', 'file.md'), '\t```\n# Header\n```\n' )
        self.assertEqual( generate_pandoc_header_ids('`# Header`', 'file.md'), '`# Header`\n' )

if __name__ == "__main__":
    unittest.main()
