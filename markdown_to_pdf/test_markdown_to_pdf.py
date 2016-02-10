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
        self.assertEqual( is_a_markdown_header( '<a name="section2"></a>`Timestamp` Interceptor','------------'), True )
        self.assertEqual( is_a_markdown_header( 'Not a header','- List item'), False )


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


    def test_make_image_path_absolute(self):
        prefix = os.path.join(os.getcwd(),'rel-dir')

        # Local image
        self.assertEqual( 
            make_image_path_absolute('link', 'rel-dir/'),
            '%s/link' % prefix)

        # Remote image (URL should't be changed)
        self.assertEqual( 
            make_image_path_absolute('www.fakeurl.com', 'rel-dir/' ),
            'www.fakeurl.com')

        # Remote image (URL should't be changed)
        self.assertEqual( 
            make_image_path_absolute('http://www.fakeurl.com', 'rel-dir/' ),
            'http://www.fakeurl.com')


    def test_process_link_destination(self):
        # Simple local link (to section in same file).
        self.assertEqual(
            process_link_destination(
                '#link',
                'foo-dir/',
                local_link_callback ),
            '#parsed-local-link'
        )

        # Simple local link (to section in other file).
        self.assertEqual(
            process_link_destination(
                '[link-text](dst_file.md/link)',
                'foo-dir/',
                local_link_callback ),
            '#parsed-remote-link'
        )

        # Simple URL link (shouldn't be parsed).
        self.assertEqual(
            process_link_destination(
                'www.google.com',
                'foo-dir/',
                local_link_callback ),
            'www.google.com'
        )

        # Simple URL link (shouldn't be parsed).
        self.assertEqual(
            process_link_destination(
                'http://www.google.com',
                'foo-dir/',
                local_link_callback ),
            'http://www.google.com'
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

   
    def test_remove_code_from_line(self):
        test_cases = [
            [
                'Line without code should not be modified',
                'Line without code should not be modified'
            ],
            [
                'This `code` and this `code` should be removed',
                'This code and this code should be removed'
            ],
            [
                'Escaped \`code\` should not be removed',
                'Escaped \`code\` should not be removed'
            ],
            [
                'This ```code` and this ```code``` should be removed',
                'This code and this code should be removed'
            ],
            [
                'Escaped \`\`\`code\`\`\` should not be removed',
                'Escaped \`\`\`code\`\`\` should not be removed'
            ],
        ]

        for test_case in test_cases:
            input_str = test_case[0]
            expected_output = test_case[1]
            self.assertEqual(remove_code_from_line(input_str), expected_output)


    def test_normalize_file_extension(self):
        # File with .pdf extension. Do not change it.
        self.assertEqual(normalize_file_extension('dir/file.pdf'), 'dir/file.pdf')

        # File with multiple extensions ending in .pdf. Do not change it.
        self.assertEqual(normalize_file_extension('dir/file.txt.pdf'), 'dir/file.txt.pdf')

        # File without extesion. Add .pdf extension.
        self.assertEqual(normalize_file_extension('dir/file'), 'dir/file.pdf')

        # File with empty extension. Add .pdf extension.
        self.assertEqual(normalize_file_extension('dir/file.'), 'dir/file.pdf')

        # File with extension other than pdf. Add .pdf extension.
        self.assertEqual(normalize_file_extension('dir/file.txt'), 'dir/file.txt.pdf')

    def test_fix_special_characters_inside_links(self):
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/a\<aa'),'http://www.test.com/a\<aa')
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/a\\<aa'),'http://www.test.com/a\\<aa')
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/a<aa'),'http://www.test.com/a\<aa')
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/a\>aa'),'http://www.test.com/a\>aa')
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/a\\>aa'),'http://www.test.com/a\\>aa')
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/a>aa'),'http://www.test.com/a\>aa')
        self.assertEqual(fix_special_characters_inside_links('http://www.test.com/aaa'),'http://www.test.com/aaa')

        

    def test_fix_blanck_spaces_before_code_tag(self):
        self.assertEqual(fix_blanck_spaces_before_code_tag('\n```code'),'\n```code')
        self.assertEqual(fix_blanck_spaces_before_code_tag('\n ```code'),'\n```code')
        self.assertEqual(fix_blanck_spaces_before_code_tag('\n  ```code'),'\n```code')
        self.assertEqual(fix_blanck_spaces_before_code_tag('\n   ```code'),'\n```code')
        self.assertEqual(fix_blanck_spaces_before_code_tag('\n    ```code'),'\n    ```code')


    def test_fix_html_before_title(self):
        self.assertEqual(fix_html_before_title('>\n#title'),'>\n\n#title')
        self.assertEqual(fix_html_before_title('>\n\n#title'),'>\n\n#title')
        self.assertEqual(fix_html_before_title('>\n\n\n#title'),'>\n\n\n#title')
        self.assertEqual(fix_html_before_title('>#title'),'>#title')


    def test_fix_new_line_after_img(self):
        self.assertEqual(fix_new_line_after_img('![alt text](img/url.jpg)'),'![alt text](img/url.jpg)')
        self.assertEqual(fix_new_line_after_img('![alt text](img/url.jpg)\n'),'![alt text](img/url.jpg)\n\n')
        self.assertEqual(fix_new_line_after_img('![alt text](img/url.jpg)\n\n'),'![alt text](img/url.jpg)\n\n')
        self.assertEqual(fix_new_line_after_img('![alt text](img/url.jpg)\n\n\n'),'![alt text](img/url.jpg)\n\n\n')
        self.assertEqual(fix_new_line_after_img('![alt text](img/url.jpg)\n\n\n\n'),'![alt text](img/url.jpg)\n\n\n\n')


    def test_separate_latex_anchors(self):
        self.assertEqual(separate_latex_anchors('\\anchor{aaaa}\n\\anchor'),'\\anchor{aaaa}\n\n\\anchor')
        self.assertEqual(separate_latex_anchors('\\anchor{aaaa}\n\n\\anchor'),'\\anchor{aaaa}\n\n\\anchor')
        self.assertEqual(separate_latex_anchors('\\anchor{aaaa}\n\n\n\\anchor'),'\\anchor{aaaa}\n\n\n\\anchor')
        self.assertEqual(separate_latex_anchors('\\anchor{aaaa}\\anchor'),'\\anchor{aaaa}\\anchor')


    def test_add_newlines_before_markdown_headers(self):
        self.assertEqual(add_newlines_before_markdown_headers('text\n```code\n#title asdfs \n asdfasdf\n```'),'text\n```code\n#title asdfs \n asdfasdf\n```')

        self.assertEqual(add_newlines_before_markdown_headers('text\n```code\n```\n#title asdfs \n asdfasdf'),'text\n```code\n```\n\n\n#title asdfs \n asdfasdf')

        self.assertEqual(add_newlines_before_markdown_headers('text\n  ```code\n#title asdfs \n asdfasdf\n```'),'text\n  ```code\n#title asdfs \n asdfasdf\n```')

        self.assertEqual(add_newlines_before_markdown_headers('text\n  ```code\n```\n#title asdfs \n asdfasdf'),'text\n  ```code\n```\n\n\n#title asdfs \n asdfasdf')

        self.assertEqual(add_newlines_before_markdown_headers('text\n#title asdfs \n asdfasdf'),'text\n\n\n#title asdfs \n asdfasdf')


    def test_remove_ids_from_a(self):
        self.assertEqual(remove_ids_from_a('<a href=#link id="identifier">text</a>'),'<a href=#link >text</a>')

        self.assertEqual(remove_ids_from_a('<a href=#link id= "identifier">text</a>'),'<a href=#link >text</a>')

        self.assertEqual(remove_ids_from_a('<a href=#link id = "identifier">text</a>'),'<a href=#link >text</a>')

        self.assertEqual(remove_ids_from_a('<a href=#link id= "identifier">text</a>'),'<a href=#link >text</a>')


        self.assertEqual(remove_ids_from_a('<a id="identifier" href=#link>text</a>'),'<a  href=#link>text</a>')

        self.assertEqual(remove_ids_from_a('<a id= "identifier" href=#link>text</a>'),'<a  href=#link>text</a>')

        self.assertEqual(remove_ids_from_a('<a id = "identifier" href=#link>text</a>'),'<a  href=#link>text</a>')

        self.assertEqual(remove_ids_from_a('<a id= "identifier" href=#link>text</a>'),'<a  href=#link>text</a>')

        

        self.assertEqual(remove_ids_from_a('<a href=#link id=\'identifier\'>text</a>'),'<a href=#link >text</a>')

        self.assertEqual(remove_ids_from_a('<a href=#link id= \'identifier\'>text</a>'),'<a href=#link >text</a>')

        self.assertEqual(remove_ids_from_a('<a href=#link id = \'identifier\'>text</a>'),'<a href=#link >text</a>')

        self.assertEqual(remove_ids_from_a('<a href=#link id= \'identifier\'>text</a>'),'<a href=#link >text</a>')


        self.assertEqual(remove_ids_from_a('<a id=\'identifier\' href=#link>text</a>'),'<a  href=#link>text</a>')

        self.assertEqual(remove_ids_from_a('<a id= \'identifier\' href=#link>text</a>'),'<a  href=#link>text</a>')

        self.assertEqual(remove_ids_from_a('<a id = \'identifier\' href=#link>text</a>'),'<a  href=#link>text</a>')

        self.assertEqual(remove_ids_from_a('<a id= \'identifier\' href=#link>text</a>'),'<a  href=#link>text</a>')



if __name__ == "__main__":
    unittest.main()
