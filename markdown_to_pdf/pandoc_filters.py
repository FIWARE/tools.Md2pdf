#!/usr/bin/env python

from pandocfilters import *
import re
from links_processing import *


def extract_file_marker(key, value):
    """Extract the file marker (if exists) from the given Pandoc object

    Arguments:
    key - key of the Pandoc object
    value - value of the Pandoc object
    """
    if key == 'RawInline' and value[0] == 'html':
        match = re.match(r'^<md2pdf:file:(.*)/>$', value[1])
        if match is not None:
            return match.group(1)
        else:
            return None
    else:
        return None


def html_inline_filter(value,markdown_filepath,generate_anchor):
    anchor_id_prefix = slugify_string(markdown_filepath)

    anchor_regexes = [
        r'<a[ \t]+name="(.*)"[ \t]*>',
        r'<a[ \t]+name="(.*)"[ \t]*/>'
    ]

    inline_html = value[1]
    
    for anchor_regex in anchor_regexes:
        match = re.match(anchor_regex,inline_html,re.IGNORECASE)
        if match is not None:
            if generate_anchor == True:
                return RawInline('tex',generate_latex_anchor(anchor_id_prefix + slugify_string(match.group(1))))
            else:
                return RawInline('tex',generate_latex_label(anchor_id_prefix + slugify_string(match.group(1))))
    
    return None


def header_filter(value,format,meta,markdown_filepath):
    """Filter applied by Pandoc to headers"""
    anchor_id_prefix = slugify_string(markdown_filepath)

    # Generate a LaTeX anchor fo the header
    latex_anchor = generate_latex_label(make_header_id_unique(generate_pandoc_header_slug(markdown_filepath, stringify(value[2])), header_filter.used_ids))

    # Process header children using the right filter.
    header_content = walk(value[2], header_children_filter, format, meta)

    # Replace the old header with a new one with its children processed and
    # an added LaTeX anchor.
    return Header(
        value[0], 
        value[1], 
        header_content + [RawInline('tex',latex_anchor)]
    )
header_filter.used_ids = {}


def header_children_filter(key, value, format, meta):
    """Filter applied by Pandoc to the children of all headers"""
    if key == 'Code':
        # Aparently, Pandoc does not like code inside headers. We turn code 
        # into plain strings.
        return Emph([Str(value[1])])
    elif key == 'RawInline' and value[0] == 'html':
        return html_inline_filter(value,pandoc_filter.current_file,False)
    else:
        return None


def pandoc_filter(key, value, format, meta):
    """Filter applied by Pandoc when converting from Mardown to PDF"""
    if key == 'Link':
        value[1][0] = process_link_destination(value[1][0], pandoc_filter.current_file)
        if len(value[1][0]) == 0:
            print_warning(
                "Found empty link ([%s]()) in file [%s]" % 
                (stringify(value[0]), pandoc_filter.current_file)
            )
        # Process link children in AST tree
        value[0] = walk(value[0],pandoc_filter,format,meta)
        return Link(value[0],value[1])
    elif key == 'Image':
        src_image_path = value[1][0]
        value[1][0] = make_image_path_absolute(value[1][0], pandoc_filter.current_file)
        if is_image_broken(value[1][0]):
            print_warning(
                (
                'Ignoring local image not found [%s] in file [%s]' +
                '- Warning added to PDF'
                ) % (
                    unicode(src_image_path).encode('utf-8'),
                    unicode(pandoc_filter.current_file).encode('utf-8')
                )
            )
            return RawInline('tex', print_image_not_found(src_image_path.encode('utf-8')))
        else:
            return Image(value[0],value[1])
    elif key == 'Header':
        return header_filter(value,format,meta,pandoc_filter.current_file)
    elif key == 'RawInline' and value[0] == 'html':
        html_filter_result = html_inline_filter(value, pandoc_filter.current_file,True)
        if html_filter_result is not None:
            return html_filter_result
        else:
            file_marker = extract_file_marker(key,value)
            if file_marker is not None:
                pandoc_filter.current_file = file_marker
            return None
    
pandoc_filter.current_file = ''


def main():
    toJSONFilter(pandoc_filter)


if __name__ == "__main__":
    main()
