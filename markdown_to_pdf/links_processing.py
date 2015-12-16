from __future__ import print_function
from markdown.extensions.toc import slugify
import os
import re
from urllib2 import urlopen, HTTPError
import sys


def print_warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)


def print_error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)


def make_image_path_absolute(image_path,markdown_filepath):
    """Make the given image path absolute"""
    markdown_absolute_filepath = os.path.join(os.getcwd(), os.path.dirname(markdown_filepath))

    if not is_an_url(image_path):
        image_path = os.path.join(markdown_absolute_filepath, image_path)

    return image_path


def print_image_not_found(image_path):
    return '\\textcolor{red}{Image Not Found \\texttt{%s}}' % image_path.replace('&','\\&').replace('%', '\\%').replace('_', '\\_')


def is_image_broken(image_path):
    try:
        if ".svg" in image_path:
            print_warning("SVG format is not currently supported: " + image_path.encode('utf-8'))
            return True
        if not is_an_url(image_path):
            if not os.path.isfile(image_path):
                return True
        else:
            url = image_path.split(' ')[0]
            if not url.startswith('http'):
                url = 'http://' + url
            if not exists_url(url):
                return True

        return False
    except Exception as e:
        print_warning("Error with image: " + image_path.encode('utf-8'))
        return True


def collapse_anchors_before_titles(markdown_content):
    anchor_regex = r'(?P<anchor><a name="[^\"]+"(?:(?:><\/a>)|(?:\/?>)))'
    
    markdown_content = re.sub(
        anchor_regex + r'[ \t]*\n+' + r'(?P<header>.*\n(?:(?:=+)|(?:-+)))',
        r'\g<anchor>\g<header>',
        markdown_content,
        flags=re.IGNORECASE
    )

    return markdown_content
   


def update_local_link(link,markdown_filepath):
    """Makes the given link unique in the final document"""
    if link[0] != '#':
        return "#" + slugify_string(os.path.normpath(os.path.join(os.path.dirname(markdown_filepath), link)))
    else:
        return "#" + slugify_string(markdown_filepath + link)


def process_link_destination(
    link_destination,
    markdown_filepath,
    local_link_callback = update_local_link
):
    if len(link_destination) > 0:
        # Ignore links to external URLS
        if not is_an_url(link_destination):
            return local_link_callback(link_destination,markdown_filepath)

    return link_destination


def is_an_url(link):
    """Returns true if the given string is a URL"""
    if( link.startswith("http://") 
        or link.startswith("https://")
        or link.startswith("http://")
        or link.startswith("www.") ):
        return True
    else:
        return False


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
    try:
       
       return slugify(string.decode('utf-8'), '-').encode('utf-8', 'ignore').replace('_', '-')
    except UnicodeEncodeError as e:
        return slugify(string, '-').replace('_','-')


def remove_code_from_line(line):
    pattern = r"(?<!\\)```(?P<innercode>[^\`]*)(?<!\\)```"
    line = re.sub(pattern,r'\1',line,flags=re.IGNORECASE)
    
    pattern = r"(?<!\\)`(?P<innercode>[^\`]*)(?<!\\)`"
    return re.sub(pattern,r'\1',line,flags=re.IGNORECASE)


def generate_latex_anchor(label_id):
    """Generates a LaTeX label with the given ID"""
    return "\\anchor{%s}" % label_id


def generate_latex_label(label_id):
    """Generates a LaTeX label with the given ID"""
    return "\\label{%s}" % label_id


def exists_url(url):
    try:
        urlopen(url.encode('utf-8')).code
        return True
    except HTTPError:
        return False


def remove_ids_from_a(content):
    pattern = r'\<a[^\>]*(?P<id>id *= *((\'.*\')|(".*"))).*\>'
    return re.sub(pattern,'',content,flags=re.IGNORECASE)

def is_a_markdown_header(line, next_line):
    """Return the nesting level of the Markdown header in markdown_line (if any)"""
    if len(line.strip()) > 0:
        i = 0
        while(i < len(line) and line[i] == '#'):
            i += 1
        if i > 0:
            return True

        if line.strip()[0] != '-' and len(next_line) > 0:
           return re.match('={2,}|-{2,}', next_line) is not None
          
    return False
