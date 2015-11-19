#!/usr/bin/env python

import yaml
from subprocess import call, Popen
import os
import re
import shutil
import pypandoc
import string
import errno


from convert_md_tables import *
from links_processing import *


def get_markdown_filepaths(configuration_filepath):
    """Return a list of markdown file paths from the given configuration file"""
    markdown_filepaths = []
    configuration_dirpath = os.path.dirname(configuration_filepath)
    
    with open(configuration_filepath, 'rU') as configuration_file:
         configuration_file_content = yaml.load(configuration_file)

    if len(configuration_dirpath) > 0:
        markdown_filepaths = [os.path.normpath(configuration_dirpath + '/' + filename) for filename in configuration_file_content['files_order']]
    else:
        markdown_filepaths = [os.path.normpath(filename) for filename in configuration_file_content['files_order']]

    return markdown_filepaths


def build_monolitic_markdown_file(monolitic_markdown_filepath, markdown_filepaths):
    with open(monolitic_markdown_filepath, 'w') as monolitic_markdown_file:
        for markdown_filepath in markdown_filepaths:
            temp_file = '/var/tmp/temp_md_m2pdf.md'
            
            with open(markdown_filepath, 'rU') as markdown_file:
                markdown_content = markdown_file.read().decode('utf-8')
                
                markdown_content = fix_blanck_spaces_before_code_tag(markdown_content)

                markdown_content = fix_html_before_title(markdown_content)
                markdown_content = fix_img_in_new_line(markdown_content)
                
                markdown_content = fix_new_line_after_img(markdown_content)

                markdown_content = pypandoc.convert(markdown_content, 'markdown_github', format='md')

                markdown_content = fix_special_characters_inside_links(markdown_content)
                
                markdown_content = parse_image_links(markdown_content, markdown_filepath)
    		markdown_content = remove_broken_images(markdown_content)

    		markdown_content = convert_referenced_links_to_inline(markdown_content)

		markdown_content = parse_markdown_inline_links(markdown_content, markdown_filepath)
    
    		markdown_content = generate_pandoc_header_ids(markdown_content, markdown_filepath)

    		markdown_content = process_html_anchors( markdown_content, markdown_filepath )
   
    		markdown_content = prevent_latex_images_floating(markdown_content)

    		markdown_content = add_newlines_before_markdown_headers( markdown_content )
                
                markdown_content = translate_md_tables(markdown_content)

                file_latex_label = generate_latex_anchor(slugify_string(markdown_filepath))

                monolitic_markdown_file.write( ("\n\n\\newpage" + file_latex_label + "\n\n" + markdown_content + "\n").encode('UTF-8'))


def fix_special_characters_inside_links(markdown_content):
    pattern_url = r'(?P<prev>.*?)(?P<url>https?://[^ \n]*)(?P<last>.*)'
    pattern = r'([^\\])(?P<character>[<>])'

    if markdown_content is None:
        return ''
    
    result = re.search(pattern_url,markdown_content,re.IGNORECASE | re.DOTALL)

    if result:
        return (fix_special_characters_inside_links(result.group('prev')) + 
                re.sub(pattern,'\\1\\'+re.escape('\\2'),result.group('url')) +
                fix_special_characters_inside_links(result.group('last')) )

    else:
        return markdown_content

def fix_blanck_spaces_before_code_tag(markdown_content):

    markdown_content = re.sub(r'(\n {1,3}```)', r'\n```', markdown_content)
    return markdown_content

def fix_html_before_title(markdown_content):

    markdown_content = markdown_content.replace('>\n#','>\n\n#')
    return markdown_content

def fix_img_in_new_line(markdown_content):
    markdown_content = markdown_content.replace('\n![', '\n\n![')
    markdown_content = markdown_content.replace( '\n\n\n![','\n\n![')
    return markdown_content

def fix_new_line_after_img(markdown_content):
    markdown_content =  re.sub(r'(?P<img>!\[[^\[\]]*\]\([^\(\)]*\)\n)',r'\g<img>\n', markdown_content)
    
    markdown_content =  re.sub('(?P<img>!\[[^\[\]]*\]\([^\(\)]*\)\n\n)\n','\g<img>', markdown_content)

    return markdown_content



def add_newlines_before_markdown_headers(markdown_content):
    markdown_lines = markdown_content.split('\n')
    markdown_output_content = ""
    inside_a_code_block = False
    used_ids = {}
    line_index = 0

    for markdown_line in markdown_lines:
      
        if markdown_line.lstrip().startswith('```'):
            inside_a_code_block = not inside_a_code_block

        if not inside_a_code_block:
            if (line_index + 1) < len(markdown_lines):
                next_markdown_line = markdown_lines[line_index+1]
            else:
                next_markdown_line = ''

            if is_a_markdown_header(markdown_line,next_markdown_line):
                markdown_output_content += "\n\n"

        markdown_output_content += markdown_line
        markdown_output_content += "\n"
        line_index += 1

    return markdown_output_content[:-1]


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
    dir_name = os.path.dirname(pdf_filepath)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    latex_config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'latex-configuration')
    latex_code_sections_config_path = os.path.join(latex_config_dir, 'code-sections.tex')

    call(["pandoc","--latex-engine=xelatex", "--toc-depth=3", "--listings", "-H", latex_code_sections_config_path, "--toc", "--from", "markdown", "--output", pdf_filepath, markdown_filepath])


def generate_md_cover(configuration_file_path, temp_cover_path):
    """Generate a MD cover using cover_metadata"""

    with open(configuration_file_path, 'rU') as configuration_file:
        configuration_file_content = yaml.load(configuration_file)

    cover_template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cover_template')
    cover_template_path = os.path.join(cover_template_dir, 'cover_template.md')

    try:
        cover_metadata = configuration_file_content['cover_metadata']
    except:
        print("Metadata for cover not provided")
        return False

    with open (cover_template_path, "rU") as myfile:
        data=myfile.read()
    
    try:
        data = data.replace('<title>', cover_metadata['title'] )
    except Exception as e:
        print("Metadata title not found")
        data = data.replace('<title>', '')

    for key, value in cover_metadata.iteritems():
        if key != 'title':
            data =  data + "\n**"+ key + "**: " + value + "   "


    with open(temp_cover_path, "w") as text_file:
        text_file.write(data)

    return True

def convert_from_GFM(original_md, converted_md):
     call(["pandoc", "--from", "markdown_github", "--to", "markdown", "--output", converted_md, original_md])

def render_pdf_cover(input_md_path, output_pdf_path):
    """ convert a MD cover to a PDF """

    call(["pandoc", "--from", "markdown", "--output", output_pdf_path, input_md_path], cwd="/var/tmp/")


def merge_cover_with_content(pdf_files_list, output_pdf):
    """ merge two pdf files"""
    call(["pdftk", pdf_files_list[0], pdf_files_list[1], "output", output_pdf])

def main():
    if len(sys.argv) != 3:
        print("ERROR: This script expects 2 arguments")
        print("Usage: \n\t" + sys.argv[0] + " <output-pdf-file> <input-conf-file>")
        sys.exit(-1)

    monolitic_markdown_filepath = "/var/tmp/markdown-to-pdf-temp.md"
    temp_cover_md_path = "/var/tmp/markdown-to-pdf-cover-temp.md"
    temp_pdf_path = "/var/tmp/markdown-to-pdf-content-temp.pdf"
    temp_cover_pdf_path = "/var/tmp/markdown-to-pdf-cover-temp.pdf"
    cover_template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cover_template')


    shutil.copy2(os.path.join(cover_template_dir, 'cover_img.png'), "/var/tmp/cover_img.png")

    shutil.copy2(os.path.join(cover_template_dir, 'fiware_logo.png'), "/var/tmp/fiware_logo.png")
    
    input_conf_file = sys.argv[2]
    output_pdf_file = sys.argv[1]

    output_dir = os.path.dirname(output_pdf_file)
    
    if '' != output_dir:
        try:
            os.makedirs(output_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    
    """
    if not os.path.exists(os.path.dirname(output_pdf_file)):
        os.makedirs(os.path.dirname(output_pdf_file))
    """    
    markdown_filepaths = get_markdown_filepaths(input_conf_file)
    build_monolitic_markdown_file(monolitic_markdown_filepath, markdown_filepaths)


    generate_pdf_from_markdown(temp_pdf_path, monolitic_markdown_filepath)


    if generate_md_cover(input_conf_file, temp_cover_md_path):
        render_pdf_cover(temp_cover_md_path, temp_cover_pdf_path)
        merge_cover_with_content([temp_cover_pdf_path, temp_pdf_path], output_pdf_file)
    else:
        shutil.copy2(temp_pdf_path, output_pdf_file)



if __name__ == "__main__":
    main()
