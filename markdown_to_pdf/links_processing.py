from __future__ import print_function
from markdown.extensions.toc import slugify
import os
import re
from urllib2 import urlopen, HTTPError
import sys

def print_warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)


def parse_image_links(markdown_content, markdown_filepath):
    """Add a prefix to all the image links in the given Markdown content"""
    regex_str = r'!\[(.*?(?:\n.*?)?)\]\((.*?)\)'
    reference_regex = re.compile(regex_str)

    references_to_change = reference_regex.findall(markdown_content)

    markdown_absolute_filepath = os.path.join(os.getcwd(), os.path.dirname(markdown_filepath))

    if references_to_change:
        for reference in references_to_change:
            link_text = reference[0]
            link      = reference[1]

            if not is_an_url(link):
                old_reference = "![%s](%s)" % (link_text, link)

                new_link = os.path.join(markdown_absolute_filepath, link)
                new_reference = "![%s](%s)" % (link_text, new_link)

                markdown_content = markdown_content.replace(old_reference, new_reference)

    return markdown_content


def remove_broken_images(markdown_content):
    """Check the destination of all image links and remove the invalid ones"""
    regex_str = r'!\[(.*?(?:\n.*?)?)\]\((.*?)\)'
    reference_regex = re.compile(regex_str)

    references_to_change = reference_regex.findall(markdown_content)

    if references_to_change:
        for reference in references_to_change:
            link_text = reference[0]
            link      = reference[1]

            if not is_an_url(link):
                old_reference = "![%s](%s)" % (link_text, link)

                if not os.path.isfile(link.split(' ')[0]):
                    print_warning( "Ignoring local image not found [" + link.split(' ')[0] + "]" )
                    markdown_content = markdown_content.replace(old_reference, ' ')
            else:
                url = link.split(' ')[0]
                if not url.startswith('http'):
                    url = 'http://' + url
                if not exists_url(url):
                    old_reference = "![%s](%s)" % (link_text, link)
                    print_warning( "Ignoring remote image not found [" + link + "]" )
                    markdown_content = markdown_content.replace(old_reference, ' ')

    return markdown_content


def update_local_link(link,markdown_filepath):
    """Makes the given link unique in the final document"""
    if link[0] != '#':
        return "#" + slugify_string(os.path.normpath(os.path.join(os.path.dirname(markdown_filepath), link)))
    else:
        return "#" + slugify_string(markdown_filepath + link)


def parse_markdown_inline_links( 
    markdown_content,
    markdown_filepath,
    local_link_callback = update_local_link
    ):
    """Parse all the Markdown links in the given Markdown content"""
    link_regexes = [
        r'(?<!!)\[(\!\[.*?\n?.*?\]\(.*?\))\]\((.*?)\)', # Links with image inside
        r'(?<!!)\[([^\!].*?\n?.*?)\]\((.*?)\)'          # Links without image inside.
    ]

    for regex_str in link_regexes:
        reference_regex = re.compile(regex_str)

        references_to_change = reference_regex.findall(markdown_content)

        if references_to_change:
            for reference in references_to_change:
                link_text = reference[0]
                link      = reference[1]

                if len(link) > 0:
                    # Ignore links to external URLS
                    if not is_an_url(link):
                        original_ref = "[%s](%s)" % (link_text, link)
                       	
                        new_link = local_link_callback(link,markdown_filepath)
                        
                        new_ref = "[%s](%s)" % (link_text, new_link)

                        markdown_content = markdown_content.replace(original_ref, new_ref)
                else:
                    print_warning( 'Empty link found: [%s](%s)' % (link_text, link) )

    return markdown_content


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
                markdown_line = remove_code_from_line(markdown_line)
                markdown_output_content += "\n\n" + generate_latex_anchor( make_header_id_unique(generate_pandoc_header_slug(markdown_filepath, markdown_line), used_ids) ) + "\n"

        markdown_output_content += markdown_line
        markdown_output_content += "\n"
        line_index += 1

    return markdown_output_content[:-1]  


def remove_code_from_line(line):
    pattern = "```(?P<innercode>[^\`]*)```"
    line = re.sub(pattern,r'\1',line,flags=re.IGNORECASE)
    
    pattern = "`(?P<innercode>[^\`]*)`"
    return re.sub(pattern,r'\1',line,flags=re.IGNORECASE)

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
 
    markdown_content = re.sub( 
        r'(#+)\s*<a name="([^\"]+)"(?:(?:><\/a>)|(?:\/>))\s*(.*?)',
        lambda match: process_header_html_anchor(match.groups()[1], match.groups()[2], match.groups()[0], anchor_id_prefix), 
        markdown_content, 
        flags=re.IGNORECASE )

    markdown_content = re.sub( 
        r'(#+)\s*<a name="([^\"]+)"\s*>(.*?)</a>\s*',
        lambda match: process_header_html_anchor(match.groups()[1], match.groups()[2], match.groups()[0], anchor_id_prefix), 
        markdown_content, 
        flags=re.IGNORECASE )

    markdown_content = re.sub( 
        r'<a name="([^\"]+)"(?:(?:><\/a>)|(?:\/>))\s*(.*?)\n((?:=+)|(?:-+))',
        lambda match: process_header_html_anchor(match.groups()[0], match.groups()[1], match.groups()[2], anchor_id_prefix), 
        markdown_content, 
        flags=re.IGNORECASE )

    markdown_content = re.sub( 
        r'<a name="([^\"]+)">\s*(.*?)</a>\n((?:=+)|(?:-+))',
        lambda match: process_header_html_anchor(match.groups()[0], match.groups()[1], match.groups()[2], anchor_id_prefix), 
        markdown_content, 
        flags=re.IGNORECASE )
   
    return markdown_content


def process_header_html_anchor(anchor_name, header_text, header_separators, prefix ):
    latex_label = generate_latex_anchor(prefix + slugify_string(anchor_name))
    if header_separators.startswith('#'):
        return latex_label + '\n\n' + header_separators + " " + header_text
    else:
        return latex_label + '\n\n' + header_text + "\n" + header_separators


def process_html_anchors(markdown_content, markdown_filepath):
    """Process HTML anchors so links to them are fixed on the PDF

    Find HTML anchors of the form <a name="foo"></a> and replace them with 
    LaTeX labels so links to such anchors are rendered correctly on the
    resulting PDF

    Arguments:
    markdown_content - MD content the substitutions will be applied on
    markdown_filepath - Path to the MD file containing previous content.
    """
    anchor_id_prefix = slugify_string(markdown_filepath)

    # Anchors in headers requires special treatment. Handle them first.
    markdown_content = process_header_html_anchors(markdown_content, markdown_filepath)

    anchor_regexes = [
        r'<a[ \t]+name="(.*)"[ \t]*></a>',
        r'<a[ \t]+name="(.*)"[ \t]*/>'
    ]
    
    for anchor_regex in anchor_regexes:
        markdown_content = re.sub( 
            anchor_regex, 
            lambda match_object: process_html_anchor( match_object, anchor_id_prefix ), 
            markdown_content, 
            flags=re.IGNORECASE )
   
    return markdown_content


def convert_referenced_links_to_inline(markdown_content):
    """Turns Markdown referenced links into inline ones"""
    referenced_links = {}
    markdown_content = extract_referenced_links(markdown_content, referenced_links)
    return make_referenced_links_inline(markdown_content, referenced_links)


def extract_referenced_links(markdown_content,referenced_links):
    """Extract all referenced links from the given markdown_content.

    Find all referenced links of the form "[id] = link", remove them
    from content and add them to referenced_links.
    """
    referenced_links.clear()

    markdown_lines = markdown_content.split('\n')
    markdown_output_content = ""
    inside_a_code_block = False

    for markdown_line in markdown_lines:
        if markdown_line.lstrip().startswith('```'):
            inside_a_code_block = not inside_a_code_block

        if not inside_a_code_block:
            match = re.match(r'\[(.+?)\]\: ([^\" ]+)(?: +((?:".*")|(?:\'.*\')|(?:\(.*\)))){0,1}', markdown_line)
            if match != None:
                id_ = match.group(1)

                link = match.group(2)
                if len(link) > 2 and link[0] == '<' and link[-1] == '>':
                    link = link[1:-1]

                if match.group(3) is not None:
                    title = match.group(3)[1:-1]
                else:
                    title = ''

                referenced_links[id_] = (link, title)
            else:
                markdown_output_content += markdown_line + '\n'
        else:
            markdown_output_content += markdown_line + '\n'

    # Strip the last \n character
    if len(markdown_output_content) > 0:
        markdown_output_content = markdown_output_content[0:-1]

    return markdown_output_content


def make_referenced_links_inline(markdown_content,links_dict):
    """Replace referenced links with inline ones

    Replace every referenced link of the form [link_text][id] with
    a inline link of the form [link_text](destination "title").
    Tokens destination and title are retrieved from the given
    links dictionary"""
    return re.sub( 
        r'\[(.+?)\](?:\[(.*?)\]){0,1}(?!\()', 
        lambda match : make_referenced_link_inline(match.group(1), match.group(2), links_dict),
        markdown_content
    )


def make_referenced_link_inline(link_text,link_id,links_dict):
    """Create an inline link from a referenced one"""
    implicit_id = False
    if link_id is None or len(link_id) == 0: 
        link_id = link_text
        implicit_id = True

    if link_id in links_dict:
        return '[%s](%s "%s")' % (link_text, links_dict[link_id][0], links_dict[link_id][1])
    else:
        if not implicit_id:
            return '[%s][%s]' % (link_text, link_id)
        else:
            return '[%s]' % link_text


def process_html_anchor( matchObject, prefix ):
    return generate_latex_anchor( prefix + slugify_string( matchObject.groups()[0] ) )


def generate_latex_anchor(label_id):
    """Generates a LaTeX anchor with the given ID"""
    return "\\phantomsection\\label{%s}" % label_id


def exists_url(url):
    try:
        urlopen(url).code
        return True
    except HTTPError:
        return False


def remove_ids_from_a(content):
    pattern = r'\<a[^\>]*(?P<id>id *= *((\'.*\')|(".*"))).*\>'
    return re.sub(pattern,'',content,flags=re.IGNORECASE)

def is_a_markdown_header(line, next_line):
    """Return the nesting level of the Markdown header in markdown_line (if any)"""
    if len(line) > 0:
        i = 0
        while(i < len(line) and line[i] == '#'):
            i += 1
        if i > 0:
            return True

        if line[0].isalpha() and len(next_line) > 0:
           return (next_line[0] == '=' or next_line[0] == '-')
          
    return False
