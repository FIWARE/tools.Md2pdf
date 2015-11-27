#!/usr/bin/env python

import unittest
from markdown_to_pdf import *

def local_link_callback(link, markdown_filepath):
    if link[0] == '#':
        return '#parsed-local-link'
    else: 
        return '#parsed-remote-link'

class TestMarkdownToPdf( unittest.TestCase ):
    def test_is_a_markdown_header(self):
        self.assertEqual( is_a_markdown_header( 'No header', '' ), False )
        self.assertEqual( is_a_markdown_header( '# Header 1', '' ), True )
        self.assertEqual( is_a_markdown_header( '  # Header 1', '' ), False )
        self.assertEqual( is_a_markdown_header( '## Header 2', '' ), True )
        self.assertEqual( is_a_markdown_header( '### Header 3', '' ), True )
        self.assertEqual( is_a_markdown_header( '#### Header 4', '' ), True )
        self.assertEqual( is_a_markdown_header( '##### Header 5', '' ), True )
        self.assertEqual( is_a_markdown_header( '###### Header 6', '' ), True )
        self.assertEqual( is_a_markdown_header( 'Header', '==' ), True )
        self.assertEqual( is_a_markdown_header( 'Header', '--' ), True )
        self.assertEqual( is_a_markdown_header( '', '--' ), False )
        self.assertEqual( is_a_markdown_header( '', '' ), False )
        self.assertEqual( is_a_markdown_header( '-', '-'), False )
        self.assertEqual( is_a_markdown_header( ' ', '-   Win'), False )
        self.assertEqual( is_a_markdown_header( '-   Win', '-   Win'), False )
        self.assertEqual( is_a_markdown_header( '`# Not a header 1`', '' ), False )


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
        self.assertEqual( generate_pandoc_header_ids('# Header', 'file.md'), '\n\n\\phantomsection\\label{filemdheader}\n# Header' )
        self.assertEqual( generate_pandoc_header_ids('```\n# Header\n```', 'file.md'), '```\n# Header\n```' )
        self.assertEqual( generate_pandoc_header_ids(' ```\n# Header\n```', 'file.md'), ' ```\n# Header\n```' )
        self.assertEqual( generate_pandoc_header_ids('\t```\n# Header\n```', 'file.md'), '\t```\n# Header\n```' )
        self.assertEqual( generate_pandoc_header_ids('`# Header`', 'file.md'), '`# Header`' )
        self.assertEqual( generate_pandoc_header_ids('Header\n==', 'file.md'), '\n\n\\phantomsection\\label{filemdheader}\nHeader\n==' )
        self.assertEqual( generate_pandoc_header_ids('Header\n--', 'file.md'), '\n\n\\phantomsection\\label{filemdheader}\nHeader\n--' )


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


    def test_process_html_anchors(self):
        self.assertEqual( process_html_anchors( '<a name="bar"></a>', 'foo' ), '\\phantomsection\\label{foobar}' )
        self.assertEqual( process_html_anchors( '<a name="bar"></A>', 'foo' ), '\\phantomsection\\label{foobar}' )
        self.assertEqual( process_html_anchors( '<A nAmE="bar"></a>', 'foo' ), '\\phantomsection\\label{foobar}' )
        self.assertEqual( process_html_anchors( '<a name="bar"/>', 'foo' ), '\\phantomsection\\label{foobar}' )
        self.assertEqual( process_html_anchors( '<a name="bar" />', 'foo' ), '\\phantomsection\\label{foobar}' )
        self.assertEqual( process_html_anchors( '<A nAmE="bar"\t ></a>', 'foo' ), '\\phantomsection\\label{foobar}' )
        self.assertEqual( process_html_anchors( 'prefix<A    nAmE="bar"></a>suffix', 'foo' ), 'prefix\\phantomsection\\label{foobar}suffix' )
        self.assertEqual( process_html_anchors( '<a name="BaR"></a>', 'foo' ), '\\phantomsection\\label{foobar}' )
        
        # Anchor in header.
        inputStr = '#<a name="top"></a>Filtering results'
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "# Filtering results"
        )
        self.assertEqual( process_html_anchors( inputStr, 'file.md' ), expectedOuputStr )

        # Autoclosed anchor in header
        inputStr = '#<a name="top"/>Filtering results'
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "# Filtering results"
        )
        self.assertEqual( process_html_anchors( inputStr, 'file.md' ), expectedOuputStr )

        # Anchor in underlined header (=).
        inputStr = '<a name="top"></a>Filtering results\n==='
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "Filtering results\n==="
        )
        self.assertEqual( process_html_anchors( inputStr, 'file.md' ), expectedOuputStr )

        # Autoclosed anchor in underlined header (=).
        inputStr = '<a name="top"/>Filtering results\n==='
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "Filtering results\n==="
        )
        self.assertEqual( process_html_anchors( inputStr, 'file.md' ), expectedOuputStr )

        # Anchor in underlined header (-).
        inputStr = '<a name="top"></a>Filtering results\n---'
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "Filtering results\n---"
        )
        self.assertEqual( process_html_anchors( inputStr, 'file.md' ), expectedOuputStr )

        # Autoclosed anchor in underlined header (-).
        inputStr = '<a name="top"/>Filtering results\n---'
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "Filtering results\n---"
        )
        self.assertEqual( process_html_anchors( inputStr, 'file.md' ), expectedOuputStr )
        
        # Anchor in header (with spaces).
        inputStr = '#\t<a name="top"></a> Cosmos'
        expectedOuputStr = (
            "\\phantomsection\\label{filemdtop}\n\n" +
            "# Cosmos"
        )
        self.assertEqual( process_header_html_anchors( inputStr, 'file.md' ), expectedOuputStr )


    def test_parse_image_links(self):
        prefix = os.path.join(os.getcwd(),'rel-dir')

        # Simple image without title
        self.assertEqual( 
            parse_image_links( '![alt_text](link)', 'rel-dir/' ),
            '![alt_text](%s/link)' % prefix )

        # Simple image without title and newline
        self.assertEqual( 
            parse_image_links( '![alt\n_text](link)', 'rel-dir/' ),
            '![alt\n_text](%s/link)' % prefix )

        # Simple image with title
        self.assertEqual( 
            parse_image_links( '![alt_text](link "title")', 'rel-dir/' ),
            '![alt_text](%s/link "title")' % prefix )

        # Image without title inside a link
        self.assertEqual( 
            parse_image_links( '[![alt_text](link)](outter-link-text)', 'rel-dir/' ),
            '[![alt_text](%s/link)](outter-link-text)' % prefix )

        # Image with title inside a link
        self.assertEqual( 
            parse_image_links( '[![alt_text](link "title")](outter-link-text)', 'rel-dir/' ),
            '[![alt_text](%s/link "title")](outter-link-text)' % prefix )

        # Image with URL (should't be changed)
        image_link = '![alt_text](www.fakeurl.com)'
        self.assertEqual( 
            parse_image_links( image_link, 'rel-dir/' ),
            image_link )

        # Image with URL (should't be changed)
        image_link = '![alt_text](www.fakeurl.com "title")'
        self.assertEqual( 
            parse_image_links( image_link, 'rel-dir/' ),
            image_link )

        # Two images together
        input_image = '![alt_text](link)'
        output_image = '![alt_text](%s/link)' % prefix
        self.assertEqual( 
            parse_image_links( '%s%s' % (input_image, input_image), 'rel-dir/' ),
            '%s%s' % (output_image, output_image) )

        # Image inside link
        input_image = '[![Figure 5: Live data](live-data.png)](link)'
        output_image = '[![Figure 5: Live data](%s/live-data.png)](link)' % prefix
        self.assertEqual( 
            parse_image_links( input_image, 'rel-dir/' ),
            output_image )


    def test_extract_referenced_links(self):
        links = {}
    
        # Simple referenced link without title
        markdown_content = extract_referenced_links('[id]: url', links )
        self.assertEqual( markdown_content, '' )
        self.assertEqual( links, {'id': ('url', '')} )

        # Simple referenced link with url between <>
        markdown_content = extract_referenced_links('[id]: <url> "title"', links )
        self.assertEqual( markdown_content, '' )
        self.assertEqual( links, {'id': ('url', 'title')} )

        # Simple referenced link with title
        markdown_content = extract_referenced_links('[id]: url "title"', links )
        self.assertEqual( markdown_content, '' )
        self.assertEqual( links, {'id': ('url', 'title')} )

        # Simple referenced link with title between ''
        markdown_content = extract_referenced_links('[id]: url \'title\'', links )
        self.assertEqual( markdown_content, '' )
        self.assertEqual( links, {'id': ('url', 'title')} )
        
        # Simple referenced link with title between ()
        markdown_content = extract_referenced_links('[id]: url (title)', links )
        self.assertEqual( markdown_content, '' )
        self.assertEqual( links, {'id': ('url', 'title')} )

        # Simple referenced link with id including spaces
        markdown_content = extract_referenced_links('[Eclipse\'s downloads section]: url "title"', links )
        self.assertEqual( markdown_content, '' )
        self.assertEqual( links, {'Eclipse\'s downloads section': ('url', 'title')} )

        # Invalid referenced link
        markdown_content = extract_referenced_links('[id]: "url"', links )
        self.assertEqual( markdown_content, '[id]: "url"' )
        self.assertEqual( links, {} )

        # Code block
        input_markdown_content = \
            'For a list of available task, type\n' +\
            '```bash\n' +\
            'grunt --help\n' +\
            '```'
        markdown_content = extract_referenced_links(input_markdown_content, links )
        self.assertEqual( markdown_content, input_markdown_content )
        self.assertEqual( links, {} )


    def test_make_referenced_links_inline(self):
        links_dict = {
            'link_id': ('url', 'title'), 
            'link_id_2': ('url_2', 'title_2'),
            'Eclipse\'s downloads section': ('url_eclipse', 'title_eclipse')
        }
        self.assertEqual( make_referenced_links_inline('Visit [link_text][link_id] now', links_dict), 'Visit [link_text](url "title") now' )
        self.assertEqual( make_referenced_links_inline('Visit [link_text][link_id_2]', links_dict), 'Visit [link_text](url_2 "title_2")' )

        # Referenced link with id including spaces
        self.assertEqual( make_referenced_links_inline('Visit [link_text][Eclipse\'s downloads section]', links_dict), 'Visit [link_text](url_eclipse "title_eclipse")' )

        # Link with implicit ID (empty brackets)
        self.assertEqual( make_referenced_links_inline('Visit [link_id][]', links_dict), 'Visit [link_id](url "title")' )

        # Link with implicit ID (with no brackets)
        self.assertEqual( make_referenced_links_inline('Visit [link_id]', links_dict), 'Visit [link_id](url "title")' )

        # Regular brackets shouldn't be replaced.
        self.assertEqual( make_referenced_links_inline('Visit [not_a_link]', links_dict), 'Visit [not_a_link]' )

        # Referenced link with invalid ID shouldn't be replaced
        self.assertEqual( make_referenced_links_inline('Visit [link_text][link_id1]', {'link_id': ('url', 'title')}), 'Visit [link_text][link_id1]' )

        # Inline link shouldn't be replaced
        self.assertEqual( make_referenced_links_inline('Visit [link_id](link_id)', {'link_id': ('url', 'title')}), 'Visit [link_id](link_id)' )



    def test_parse_markdown_inline_links(self):
        # Simple local link (to section in same file).
        self.assertEqual(
            parse_markdown_inline_links(
                '[link-text](#link)',
                'foo-dir/',
                local_link_callback ),
            '[link-text](#parsed-local-link)'
        )

        # Simple local link with new line.
        self.assertEqual(
            parse_markdown_inline_links(
                '[action from the\n    request](#request-action)',
                'foo-dir/',
                local_link_callback ),
            '[action from the\n    request](#parsed-local-link)'
        )

        # Simple local link with new line and tab.
        self.assertEqual(
            parse_markdown_inline_links(
                '[action from the\n\t    request](#request-action)',
                'foo-dir/',
                local_link_callback ),
            '[action from the\n\t    request](#parsed-local-link)'
        )

        # Simple local link (to section in other file).
        self.assertEqual(
            parse_markdown_inline_links(
                '[link-text](link)',
                'foo-dir/',
                local_link_callback ),
            '[link-text](#parsed-remote-link)'
        )

        # Simple URL link (shouldn't be parsed).
        self.assertEqual(
            parse_markdown_inline_links(
                '[link-text](www.google.com)',
                'foo-dir/',
                local_link_callback ),
            '[link-text](www.google.com)'
        )


        # Simple link with image inside.
        self.assertEqual(
            parse_markdown_inline_links(
                '[![image](image-link)](#link)',
                'foo-dir/',
                local_link_callback ),
            '[![image](image-link)](#parsed-local-link)'
        )

        # Simple link with image inside with new line.
        self.assertEqual(
            parse_markdown_inline_links(
                '[![ima\nge](image-link)](#link)',
                'foo-dir/',
                local_link_callback ),
            '[![ima\nge](image-link)](#parsed-local-link)'
        )


    def test_have_table_separator(self):
        # Simple text shouldn't be recognized as table separator.
        self.assertEqual( 
            have_table_separator('foo'),
            False
        )

        # Empty list item shouldn't be recognized as table separator.
        self.assertEqual( 
            have_table_separator('- '),
            False
        )

        # Simple table separator.
        self.assertEqual( 
            have_table_separator('|---|'),
            True
        )

        # Simple table separator (with spaces).
        self.assertEqual( 
            have_table_separator('| --- |'),
            True
        )

        # Table separator with alignment specifiers.
        self.assertEqual( 
            have_table_separator('| :- | :-: | -: |'),
            True
        )

        # Table row, not separator
        self.assertEqual( 
            have_table_separator('| Method | Path | Action|'),
            False
        )


if __name__ == "__main__":
    unittest.main()
