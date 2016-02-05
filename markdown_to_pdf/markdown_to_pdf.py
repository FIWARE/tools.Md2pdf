#!/usr/bin/env python

from __future__ import print_function
import yaml
from subprocess import call, Popen
import os
import re
import shutil
import pypandoc
import string
import errno
import getopt
import tempfile


from convert_md_tables import *
from links_processing import *
from check_requirements import *

# We need Pandoc to convert from GFM to Markdown with some extensions added
# and other removed. This global set the Markdown format with its extensions.
MD2PDF_INNER_FORMAT = \
    'markdown' +\
    '+lists_without_preceding_blankline' +\
    '-startnum' +\
    '-fancy_lists'


def get_markdown_filepaths(configuration_filepath):
    """Return a list of markdown file paths from the given configuration file"""
    markdown_filepaths = []
    configuration_dirpath = os.path.dirname(configuration_filepath)
    
    with open(configuration_filepath, 'rU') as configuration_file:
         configuration_file_content = yaml.load(configuration_file)

    try:
        configuration_file_content['files_order']
    except Exception, e:
        #try to load from RTD yml format
        configuration_file_content['files_order'] = convert_md_filepaths_from_RTD_format(configuration_filepath)

    if len(configuration_dirpath) > 0:
        markdown_filepaths = [os.path.normpath(configuration_dirpath + '/' + filename) for filename in configuration_file_content['files_order']]
    else:
        markdown_filepaths = [os.path.normpath(filename) for filename in configuration_file_content['files_order']]

    return markdown_filepaths


def convert_md_filepaths_from_RTD_format(configuration_filepath):
    file_paths=[]
    prefix=""

    with open(configuration_filepath, 'rU') as configuration_file:
         configuration_file_content = yaml.load(configuration_file)

    try:
        prefix = "./"+configuration_file_content['docs_dir']
    except Exception, e:
        prefix = ""

    for page in configuration_file_content['pages']:
        if isinstance(page, basestring):
            file_paths.append(page)
        elif isinstance(page, dict):
            for element in page:
                file_paths += create_file_order_list(page[element])
        else:
            for element in page:
                file_paths += create_file_order_list(element)

    if len(prefix)>2:
        if prefix[-1]!="/":
            prefix+="/"

    file_paths = [prefix + path for path in file_paths]
    return file_paths

def create_file_order_list(elements):
    paths = []

    if isinstance(elements, basestring):
        return [elements]
    
    if isinstance(elements,dict):
        for element in elements:
            paths = create_file_order_list(elements[element])
    else:
        for element in elements:
            paths = paths + create_file_order_list(element)

    return paths

def build_monolitic_markdown_file(monolitic_markdown_filepath, markdown_filepaths):
    with open(monolitic_markdown_filepath, 'wb') as monolitic_markdown_file:
        for markdown_filepath in markdown_filepaths:
            temp_file = os.path.join(tempfile.gettempdir(),'temp_md_m2pdf.md')
            
            print('Processing file [%s] ...' % markdown_filepath)
            with open(markdown_filepath, 'rU') as markdown_file:
                markdown_content = markdown_file.read().decode('utf-8')
                
                markdown_content = fix_empty_lines(markdown_content)

                markdown_content = fix_blanck_spaces_before_code_tag(markdown_content)

                markdown_content = remove_ids_from_a(markdown_content)

                markdown_content = fix_html_before_title(markdown_content)
                markdown_content = fix_img_in_new_line(markdown_content)
                
                markdown_content = fix_new_line_after_img(markdown_content)

                markdown_content = pypandoc.convert(markdown_content, 'markdown_github', format='markdown_github', filters=['md2pdf_pandoc_paragraph_filter'])

                markdown_content = pypandoc.convert(markdown_content, 'markdown_github+all_symbols_escapable', format='markdown_github+all_symbols_escapable')
                
                markdown_content = pypandoc.convert(markdown_content, 'markdown_github', format=MD2PDF_INNER_FORMAT)

                markdown_content = fix_special_characters_inside_links(markdown_content)
   
                markdown_content = prevent_latex_images_floating(markdown_content)

                markdown_content = add_newlines_before_markdown_headers( markdown_content )

                markdown_content = separate_latex_anchors(markdown_content)

                markdown_content = collapse_anchors_before_titles(markdown_content)
                
                markdown_content = translate_md_tables(markdown_content)

                file_latex_label = generate_latex_anchor(slugify_string(markdown_filepath))

                # This "file marker" is appended at the beginning of the 
                # contents of every file so the filepath is passed to the
                # Pandoc filter which need it for links processing.
                file_marker = '<md2pdf:file:%s/>' % markdown_filepath

                monolitic_markdown_file.write( ("\n" + file_marker + "\n\n\\newpage\n\n" + file_latex_label + "\n\n" + markdown_content + "\n").encode('UTF-8'))

                print('Processing file [%s] ...OK' % markdown_filepath)


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
    markdown_content = re.sub(
        r'\n([ \t]*)!\[', 
        r'\n\n\1![',
        markdown_content
    )
    markdown_content = re.sub(
        r'\n\n\n([ \t]*)!\[',
        r'\n\n\1![',
        markdown_content
    )
    return markdown_content

def fix_new_line_after_img(markdown_content):
    markdown_content =  re.sub(r'(?P<img>!\[[^\[\]]*\]\([^\(\)]*\)\n)',r'\g<img>\n', markdown_content)
    
    markdown_content =  re.sub('(?P<img>!\[[^\[\]]*\]\([^\(\)]*\)\n\n)\n','\g<img>', markdown_content)

    return markdown_content

def fix_empty_lines(markdown_content):
    #transform to normal whitespace
    markdown_content = markdown_content.replace(u'\u2000',' ')
    markdown_content = markdown_content.replace(u'\u2001',' ')
    markdown_content = markdown_content.replace(u'\u2002',' ')
    markdown_content = markdown_content.replace(u'\u2003',' ')
    markdown_content = markdown_content.replace(u'\u2004',' ')
    markdown_content = markdown_content.replace(u'\u2005',' ')
    markdown_content = markdown_content.replace(u'\u2006',' ')
    markdown_content = markdown_content.replace(u'\u2007',' ')
    markdown_content = markdown_content.replace(u'\u2008',' ')
    markdown_content = markdown_content.replace(u'\u2009',' ')
    markdown_content = markdown_content.replace(u'\u200a',' ')
    #replace whitespace
    return re.sub(r'\n[ \t]*\n','\n\n',markdown_content)


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


def generate_pdf_from_markdown(pdf_filepath, markdown_filepath,developer_mode):
    """Generate a PDF from the given Markdown file using Pandoc

    Arguments:
    pdf_filepath - filepath of the output PDF file
    markdown_filepath - filepath of the Markdown input file"""
    dir_name = os.path.dirname(pdf_filepath)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    latex_config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'latex-configuration')
    latex_code_sections_config_path = os.path.join(latex_config_dir, 'code-sections.tex')

    pandoc_options = ["--latex-engine=xelatex", "--toc-depth=3", "--listings", "-H", latex_code_sections_config_path, "--toc", "--from", MD2PDF_INNER_FORMAT, "--filter", "md2pdf_pandoc_filter"]

    # If developer mode is on, convert temporal file to LaTeX.
    if developer_mode == True:
        latex_filepath = os.path.join(tempfile.gettempdir(),'markdown-to-pdf-temp.tex')
        print('Generating LaTeX (developer mode) ...')
        call(["pandoc"] + pandoc_options + ["--output", latex_filepath, markdown_filepath])
        print('LaTeX generated: [%s] (developer mode)' % latex_filepath)

    # Generate PDF.
    print('Generating PDF...')
    pandoc_call_return_value = call(["pandoc"] + pandoc_options + ["--output", pdf_filepath, markdown_filepath])

    if pandoc_call_return_value != 0:
        raise RuntimeError(
            ( 
                'Conversion to PDF failed - ' +\
                'Pandoc failed with code: (%d)'
            ) % pandoc_call_return_value
        )

    print('Generating PDF...OK')


def generate_md_cover(configuration_file_path, temp_cover_path):
    """Generate a MD cover using cover_metadata"""

    with open(configuration_file_path, 'rU') as configuration_file:
        configuration_file_content = yaml.load(configuration_file)

    cover_template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cover_template')
    cover_template_path = os.path.join(cover_template_dir, 'cover_template.md')

    try:
        cover_metadata = configuration_file_content['cover_metadata']
    except:
        print_warning("Metadata for cover not provided")
        print_warning("Default values will be used")
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




def generate_default_cover_file(input_conf_file, output_file):
    """ Generate the default metadata cover, try to get title from input file"""
    print ("Cover metadata not provided. Trying to generate it")
    configuration = {}
    with open(input_conf_file, 'rU') as configuration_file:
        configuration_file_content = yaml.load(configuration_file)

    try:
        #try if defined in the default config file
        configuration_file_content['cover_metadata']
        
        configuration['cover_metadata'] = configuration_file_content['cover_metadata']

    except Exception, e:
        #load default values
        cover_template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cover_template')
        default_cover_conf_file = os.path.join(cover_template_dir, 'default_cover_metadata.yml')
        with open(default_cover_conf_file, 'rU') as configuration_file:
            default_configuration_file_content = yaml.load(configuration_file)
        
        try:
            #try to obtain site_name
            default_configuration_file_content['cover_metadata']['title']=configuration_file_content['site_name']
        except Exception as e:
            pass        
        
        try:
            #try to obtain site description
            default_configuration_file_content['cover_metadata']['description']=configuration_file_content['site_description']
        except Exception as e:
            pass

        configuration['cover_metadata'] = default_configuration_file_content['cover_metadata']

    with open(output_file, 'w') as outfile:
        outfile.write( yaml.dump(configuration, default_flow_style=False) )


def convert_from_GFM(original_md, converted_md):
     call(["pandoc", "--from", "markdown_github", "--to", "markdown", "--output", converted_md, original_md])

def render_pdf_cover(input_md_path, output_pdf_path):
    """ convert a MD cover to a PDF """

    call(["pandoc", "--from", "markdown", "--output", output_pdf_path, input_md_path], cwd=tempfile.gettempdir())


def merge_cover_with_content(pdf_files_list, output_pdf):
    """ merge two pdf files"""
    call(["pdftk", pdf_files_list[0], pdf_files_list[1], "output", output_pdf])


def separate_latex_anchors(markdown_content):
    """Fixes an LaTeX error caused by having one empty \anchor

    Fixes an LaTeX error caused by having one \anchor followed inmediatly by 
    other (without content in the middle)"""
    return re.sub(
        r'\\anchor{(.*?)}\n\\anchor',
        r'\\anchor{\1}\n\n\\anchor',
        markdown_content
    )


def normalize_file_extension(filepath):
    """Adds extension .pdf to the given filepath if it does not have it"""
    filename, file_extension = os.path.splitext(filepath)

    if not file_extension.endswith('.pdf'):
        print_warning('Filepath [%s] without extension, adding .pdf' % filepath)
        if file_extension == '':
            file_extension = '.pdf'
        else:
            if file_extension[-1] == '.':
                file_extension = file_extension[0:-1]
            file_extension += '.pdf'

    return filename + file_extension


def main():
    #first check requirements
    check_all_requirements()
    # Parse user arguments.
    try:
        opts, args = getopt.getopt(sys.argv[1:],"i:o:c:",["input=","output=","cover=","develop"])
    except getopt.GetoptError as error:
        print(str(error)) 
        print('Usage: \n\tmd2pdf -i <input-conf-file> -o <output-pdf-file>')
        sys.exit(2)

    # Default argument values.
    input_conf_file = 'md2pdf.yml'
    output_pdf_file = 'output.pdf'
    cover_metadata_file = None
    generated_default_cover_metadata_file = os.path.join(tempfile.gettempdir(),'default_cover_metadata.yml')
    developer_mode = False

    # Process user arguments.
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_conf_file = arg
        elif opt in ("-o", "--output"):
            output_pdf_file = arg
        elif opt in ('--develop'):
            developer_mode = True
        elif opt in ('--cover', "-c"):
            cover_metadata_file = arg

    #check if cover metadata is provided
    if cover_metadata_file is None:
        generate_default_cover_file(input_conf_file, generated_default_cover_metadata_file)
        cover_metadata_file = generated_default_cover_metadata_file

    # Check that input file exists.
    if not os.path.isfile(input_conf_file):
        print('ERROR: input file [%s] not found' % (input_conf_file), file=sys.stderr)
        sys.exit(2)

    # Normalize output filepath
    output_pdf_file = normalize_file_extension(output_pdf_file)

    # Set auxiliar file paths.
    temp_dirpath = tempfile.gettempdir()
    monolitic_markdown_filepath = os.path.join(temp_dirpath,'markdown-to-pdf-temp.md')
    temp_cover_md_path = os.path.join(temp_dirpath,'markdown-to-pdf-cover-temp.md')
    temp_pdf_path = os.path.join(temp_dirpath,'markdown-to-pdf-content-temp.pdf')
    temp_cover_pdf_path = os.path.join(temp_dirpath,'markdown-to-pdf-cover-temp.pdf')
    cover_template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cover_template')

    shutil.copy2(os.path.join(cover_template_dir, 'cover_img.png'), os.path.join(temp_dirpath,'cover_img.png'))

    shutil.copy2(os.path.join(cover_template_dir, 'fiware_logo.png'), os.path.join(temp_dirpath,'fiware_logo.png'))
    
    output_dir = os.path.dirname(output_pdf_file)
    
    if '' != output_dir:
        try:
            os.makedirs(output_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    

    try:
        markdown_filepaths = get_markdown_filepaths(input_conf_file)

        build_monolitic_markdown_file(monolitic_markdown_filepath, markdown_filepaths)

        generate_pdf_from_markdown(temp_pdf_path, monolitic_markdown_filepath,developer_mode)

        if generate_md_cover(cover_metadata_file, temp_cover_md_path):
            render_pdf_cover(temp_cover_md_path, temp_cover_pdf_path)
            merge_cover_with_content([temp_cover_pdf_path, temp_pdf_path], output_pdf_file)
        else:
            shutil.copy2(temp_pdf_path, output_pdf_file)

        print('PDF generated [%s]' % output_pdf_file)
    except RuntimeError as error:
        print_error(error)
        exit(1)


if __name__ == "__main__":
    main()
