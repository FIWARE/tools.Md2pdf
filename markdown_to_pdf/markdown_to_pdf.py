#!/usr/bin/env python

import sys
import yaml
from subprocess import call
import os
import re


def get_markdown_filepaths( configuration_filepath ):
    """Return a list of markdown file paths from the given configuration file"""
    markdown_filepaths = []
    markdown_dirpath = os.path.dirname( configuration_filepath )
    
    with open( configuration_filepath, 'r' ) as configuration_file:
         configuration_file_content = yaml.load( configuration_file )

    markdown_filepaths = [markdown_dirpath + '/' + filename for filename in configuration_file_content['files_order']]

    return markdown_filepaths


def build_monolitic_markdown_file( monolitic_markdown_filepath, markdown_filepaths ):
    with open( monolitic_markdown_filepath, 'w' ) as monolitic_markdown_file:
        for markdown_filepath in markdown_filepaths:
            with open( markdown_filepath, 'r' ) as markdown_file:
                markdown_content = markdown_file.read()

                new_path_prefix = os.path.join( os.getcwd(), os.path.dirname( markdown_filepath ) )
                markdown_content = parse_markdown_links( markdown_content, markdown_filepath )
                markdown_content = parse_image_links( markdown_content, new_path_prefix )

                markdown_content = generate_pandoc_header_ids( markdown_content, markdown_filepath )

                markdown_content = prevent_latex_images_floating( markdown_content )

                monolitic_markdown_file.write( "##### " + generate_pandoc_section_id( markdown_filepath ) + "\n\n" + markdown_content + "\n" )


def parse_image_links( markdown_content, prefix ):
    """Add a prefix to all the image links in the given Markdown content"""
    regex_str = r'!\[(.*)\]\((.*)\)'
    reference_regex = re.compile( regex_str )

    references_to_change = reference_regex.findall( markdown_content )

    if references_to_change:
        for reference in references_to_change:
            link_text = reference[0]
            link      = reference[1]

            if not is_an_url( link ):
                original_reference = r'!\[(.*)\]\((.*)\)'

                new_link = os.path.join( prefix, link )
                new_reference = "![%s](%s)" % (link_text, new_link)

                markdown_content = re.sub( original_reference, new_reference, markdown_content )

    return markdown_content


def parse_markdown_links( markdown_content, markdown_filepath ):
    """Parse all the Markdown links in the given Markdown content"""
    regex_str = "\[(.+)\]\((.+)(#.*)?\)"
    reference_regex = re.compile( regex_str )

    references_to_change = reference_regex.findall( markdown_content )

    if references_to_change:
        for reference in references_to_change:
            link_text = reference[0]
            page      = reference[1]
            section   =  reference[2]

            # Ignore links to external URLS
            if not is_an_url( page ):
                original_ref = "[%s](%s%s)" % ( link_text, page, section)
                if page[0] != '#':
                    new_page = "#" + generate_pandoc_section_slug( os.path.join( os.path.dirname( markdown_filepath ), page ) ).replace( '#', '__' )
                else:
                    new_page = "#" + generate_pandoc_section_slug( markdown_filepath + page ).replace( '#', '__' )

                new_ref = "[%s](%s%s)" % ( link_text, new_page, section)

                markdown_content = markdown_content.replace( original_ref, new_ref )

    return markdown_content


def get_markdown_header_level( markdown_line ):
    """Return the nesting level of the Markdown header in markdown_line (if any)"""
    i = 0
    while( i < len( markdown_line ) and markdown_line[i] == '#' ):
        i += 1
    return i


def is_an_url( link ):
    """Returns true if the given string is a URL"""
    if( link.startswith("http://") 
        or link.startswith("https://")
        or link.startswith("http://")
        or link.startswith("www.") ):
        return True
    else:
        return False


def generate_pandoc_header_id( dirpath, markdown_header ):
    """Generate a Pandoc ID for a given Markdown header

    Arguments:
    dirpath - Path of the directory containing the file with the header.
    markdown_header - Markdown header
    """
    slug_dirpath = dirpath.replace( '/', '_' )
    slug_markdown_header =  slugfy( markdown_header.strip().lstrip('#').strip() )
    
    return "{#" + slug_dirpath + "__" + slug_markdown_header + "}"


def slugfy( string ):
    """Slugfy the given string"""
    replacement_characters_list = [ ' ', '?', '<', '>', '?', '(', ')', '"', '&', '\'', '=', '/' ]

    string = string.lower()
    for char in replacement_characters_list:
        string = string.replace( char, '-' )
    
    return string
    


def generate_pandoc_section_id( filepath ):
    """Generate a Pandoc ID for the given filepath"""
    return "{#" + generate_pandoc_section_slug( filepath ) + "}"


def generate_pandoc_section_slug( filepath ):
    return filepath.replace( '/', '_' )


def generate_pandoc_header_ids( markdown_content, markdown_filepath ):
    """Append a Pandoc ID (for section linking) to every header in the given Markdown content)

    Arguments:
    markdown_content = Markdown content string
    markdown_filepath = Path to the Markdown content file. This is used as a prefix for the IDs.
    """
    markdown_lines = markdown_content.split('\n')
    markdown_output_content = ""
    inside_a_code_block = False

    for markdown_line in markdown_lines:
        header_level = get_markdown_header_level( markdown_line )
        markdown_output_content += markdown_line

        if markdown_line.lstrip().startswith( '```' ):
            inside_a_code_block = not inside_a_code_block

        if( not inside_a_code_block and header_level > 0 ):
            markdown_output_content += " " + generate_pandoc_header_id( markdown_filepath, markdown_line )

        markdown_output_content += "\n"

    return markdown_output_content


def prevent_latex_images_floating( markdown_content ):
    """Applies a simple \"hack\" so images aren't floated in resulting PDF.

    When rendering a PDF from Markdown, a floating is given by LaTeX to some 
    standalone images (those alone in a paragraph); this caused some images
    to appear in the middle of a code section or a paragraph. This simple 
    hack adds a escaped space to the images, so they are interpreted as 
    images embeded in a paragraph and therefore no floating is applied by
    LaTeX.

    Arguments:
    markdown_content - Markdown content this hack is applied to.
    """
    original_regex = r'!\[(.*)\]\((.*)\)'
    new_regex = r'![\1](\2)\\ '
    return re.sub( original_regex, new_regex, markdown_content )


def generate_pdf_from_markdown( pdf_filepath, markdown_filepath ):
    """Generate a PDF from the given Markdown file using Pandoc

    Arguments:
    pdf_filepath - filepath of the output PDF file
    markdown_filepath - filepath of the Markdown input file"""
    latex_config_dir = os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'latex-configuration' )
    latex_code_sections_config_path = os.path.join( latex_config_dir, 'code-sections.tex' )

    call( [ "pandoc", "--latex-engine=xelatex", "--toc-depth=3", "--listings", "-H", latex_code_sections_config_path, "--toc", "--from", "markdown", "--output", pdf_filepath, markdown_filepath ] )


def main():
    if( len( sys.argv ) != 3 ):
        print "ERROR: This script expects 2 arguments"
        print "Usage: \n\t" + sys.argv[0] + " <output-pdf-file> <input-conf-file>"
        sys.exit(-1)

    monolitic_markdown_filepath = "/var/tmp/markdown-to-pdf-temp.md"
    input_conf_file = sys.argv[2]
    output_pdf_file = sys.argv[1]

    markdown_filepaths = get_markdown_filepaths( input_conf_file )
    build_monolitic_markdown_file( monolitic_markdown_filepath, markdown_filepaths )
    generate_pdf_from_markdown( output_pdf_file, monolitic_markdown_filepath )


if __name__ == "__main__":
    main()
