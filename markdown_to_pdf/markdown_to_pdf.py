#!/usr/bin/env python

import sys
import yaml
from subprocess import call
from markdown.extensions.toc import slugify
import os
import re


def get_markdown_filepaths(configuration_filepath):
    """Return a list of markdown file paths from the given configuration file"""
    markdown_filepaths = []
    configuration_dirpath = os.path.dirname(configuration_filepath)
    
    with open(configuration_filepath, 'r') as configuration_file:
         configuration_file_content = yaml.load(configuration_file)

    if len(configuration_dirpath) > 0:
        markdown_filepaths = [os.path.normpath(configuration_dirpath + '/' + filename) for filename in configuration_file_content['files_order']]
    else:
        markdown_filepaths = [os.path.normpath(filename) for filename in configuration_file_content['files_order']]

    return markdown_filepaths


def build_monolitic_markdown_file(monolitic_markdown_filepath, markdown_filepaths):
    with open(monolitic_markdown_filepath, 'w') as monolitic_markdown_file:
        for markdown_filepath in markdown_filepaths:
            with open(markdown_filepath, 'r') as markdown_file:
                markdown_content = markdown_file.read()

                markdown_content = parse_markdown_links(markdown_content, markdown_filepath)
                markdown_content = parse_image_links(markdown_content, markdown_filepath)

                markdown_content = generate_pandoc_header_ids(markdown_content, markdown_filepath)

                markdown_content = prevent_latex_images_floating(markdown_content)

                markdown_content = process_header_html_anchors(markdown_content, markdown_filepath)

                file_latex_label = "\phantomsection\n\\label{%s}" % slugify_string(markdown_filepath)
                monolitic_markdown_file.write("\n\n" + file_latex_label + "\n\n" + markdown_content + "\n")


def parse_image_links(markdown_content, markdown_filepath):
    """Add a prefix to all the image links in the given Markdown content"""
    regex_str = r'!\[(.*)\]\((.*)\)'
    reference_regex = re.compile(regex_str)

    references_to_change = reference_regex.findall(markdown_content)

    markdown_absolute_filepath = os.path.join(os.getcwd(), os.path.dirname(markdown_filepath))

    if references_to_change:
        for reference in references_to_change:
            link_text = reference[0]
            link      = reference[1]

            if not is_an_url(link):
                original_reference = r'!\[(.*)\]\((.*)\)'

                new_link = os.path.join(markdown_absolute_filepath, link)
                new_reference = "![%s](%s)" % (link_text, new_link)

                markdown_content = re.sub(original_reference, new_reference, markdown_content)

    return markdown_content


def parse_markdown_links(markdown_content, markdown_filepath):
    """Parse all the Markdown links in the given Markdown content"""
    regex_str = "\[([^\[\]]+)\]\(([^\(\)]+)\)"
    reference_regex = re.compile(regex_str)

    references_to_change = reference_regex.findall(markdown_content)

    if references_to_change:
        for reference in references_to_change:
            link_text = reference[0]
            link      = reference[1]

            # Ignore links to external URLS
            if not is_an_url(link):
                original_ref = "[%s](%s)" % (link_text, link)
                    
                if link[0] != '#':
                    new_link = "#" + slugify_string(os.path.normpath(os.path.join(os.path.dirname(markdown_filepath), link)))
                else:
                    new_link = "#" + slugify_string(markdown_filepath + link)
                
                new_ref = "[%s](%s)" % (link_text, new_link)

                markdown_content = markdown_content.replace(original_ref, new_ref)

    return markdown_content


def get_markdown_header_level(markdown_line):
    """Return the nesting level of the Markdown header in markdown_line (if any)"""
    i = 0
    while(i <len( markdown_line) and markdown_line[i] == '#'):
        i += 1
    return i


def is_an_url(link):
    """Returns true if the given string is a URL"""
    if( link.startswith("http://") 
        or link.startswith("https://")
        or link.startswith("http://")
        or link.startswith("www.") ):
        return True
    else:
        return False


def generate_pandoc_header_id(filepath, markdown_header):
    """Generate a Pandoc ID for a given Markdown header

    Arguments:
    filepath - Path of the file containing the header.
    markdown_header - Markdown header
    """
    return "{#" + generate_pandoc_header_slug(filepath, markdown_header) + "}"


def generate_pandoc_header_slug(filepath, markdown_header):
    """Generate a Pandoc slug for a given Markdown header

    Arguments:
    filepath - Path of the file containing the header.
    markdown_header - Markdown header
    """
    slug_filepath = slugify_string(filepath)
    slug_markdown_header =  slugify_string(markdown_header.strip().lstrip('#').strip())
    
    return slug_filepath + slug_markdown_header


def make_header_id_unique(header_id, used_ids):
    """Make the given ID unique given a dictionary of used_ids

    Arguments:
    header_id - Slugified header ID
    used_id - Dictionary associating each header ID without suffixes to 
    the number of times that such ID has been used.
    """
    if header_id in used_ids:
        unique_header_id = header_id + '-' + str(used_ids[header_id])
        used_ids[header_id] += 1
    else:
        unique_header_id = header_id
        used_ids[header_id] = 1

    return unique_header_id

def slugify_string(string):
    """slugify_string the given string"""
    return slugify(unicode(string), '-').encode('utf-8', 'ignore').replace('_', '-')


def generate_pandoc_section_id(filepath):
    """Generate a Pandoc ID for the given filepath"""
    return "{#" + slugify_string(filepath) + "}"


def generate_pandoc_header_ids(markdown_content, markdown_filepath):
    """Append a Pandoc ID (for section linking) to every header in the given Markdown content)

    Arguments:
    markdown_content = Markdown content string
    markdown_filepath = Path to the Markdown content file. This is used as a prefix for the IDs.
    """
    markdown_lines = markdown_content.split('\n')
    markdown_output_content = ""
    inside_a_code_block = False
    used_ids = {}

    for markdown_line in markdown_lines:
        header_level = get_markdown_header_level(markdown_line)
        markdown_output_content += markdown_line

        if markdown_line.lstrip().startswith('```'):
            inside_a_code_block = not inside_a_code_block

        if(not inside_a_code_block and header_level > 0):
            markdown_output_content += " {#" + make_header_id_unique(generate_pandoc_header_slug(markdown_filepath, markdown_line), used_ids) + "}"

        markdown_output_content += "\n"

    return markdown_output_content


def prevent_latex_images_floating(markdown_content):
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
    return re.sub(original_regex, new_regex, markdown_content)


def generate_pdf_from_markdown(pdf_filepath, markdown_filepath):
    """Generate a PDF from the given Markdown file using Pandoc

    Arguments:
    pdf_filepath - filepath of the output PDF file
    markdown_filepath - filepath of the Markdown input file"""
    latex_config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'latex-configuration')
    latex_code_sections_config_path = os.path.join(latex_config_dir, 'code-sections.tex')

    call(["pandoc", "--latex-engine=xelatex", "--toc-depth=3", "--listings", "-H", latex_code_sections_config_path, "--toc", "--from", "markdown", "--output", pdf_filepath, markdown_filepath])


def process_header_html_anchors(markdown_content, markdown_filepath):
    """Process header anchors so links to them are fixed on the PDF

    Find Markdown headers with HTML anchors (ie. 
    "#<a name="anchor_id"></a> Header") and replace them with LaTeX 
    labels so links to such anchors are rendered correctly on the 
    resulting PDF

    Arguments:
    markdown_content - MD content the substitutions will be applied on
    markdown_filepath - Path to the MD file containing previous content.
    """
    anchor_id_prefix = slugify_string(markdown_filepath)

    regex_str = r'(#+.*)<a name="([^\"]+)"><\/a>(.*)'
    reference_regex = re.compile(regex_str)

    references_to_change = reference_regex.findall(markdown_content)
    
    if references_to_change:
        for reference in references_to_change:
            previous_content = reference[0]
            link = reference[1]
            next_content = reference[2]

            original_ref = "%s<a name=\"%s\"></a>%s" % (previous_content, link, next_content)

            new_link = anchor_id_prefix + slugify_string(link)
            new_ref = "%s%s\n\n\\phantomsection\n\\label{%s}\n" % (previous_content, next_content, new_link)

            markdown_content = markdown_content.replace(original_ref, new_ref)

    return markdown_content


def main():
    if len(sys.argv) != 3:
        print "ERROR: This script expects 2 arguments"
        print "Usage: \n\t" + sys.argv[0] + " <output-pdf-file> <input-conf-file>"
        sys.exit(-1)

    monolitic_markdown_filepath = "/var/tmp/markdown-to-pdf-temp.md"
    input_conf_file = sys.argv[2]
    output_pdf_file = sys.argv[1]

    markdown_filepaths = get_markdown_filepaths(input_conf_file)
    build_monolitic_markdown_file(monolitic_markdown_filepath, markdown_filepaths)
    generate_pdf_from_markdown(output_pdf_file, monolitic_markdown_filepath)


if __name__ == "__main__":
    main()
