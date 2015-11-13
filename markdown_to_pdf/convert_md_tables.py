from __future__ import print_function
import re

from hyphenate import *



def translate_md_tables(markdown_content):
    lines = markdown_content.split('\n')

    candidate_header = None
    table = False
    readed_lines = []
    table_lines = []
    separator = None

    for line in lines:
        if candidate_header is not None and have_table_separator(line):

            separator = line
            table = True
            continue
        if '|' in line:
            if candidate_header is None:
                candidate_header = line

                continue

            else :

                table_lines.append(line)
                continue

        #TODO translate table
        if table:
            readed_lines += generate_md_table(candidate_header, separator, table_lines)

        readed_lines.append(line) 
        candidate_header = None
        table = False
        separator = False
        table_lines = []
    markdown_content = '\n'.join(readed_lines)
    return markdown_content


def generate_md_table(header, header_separator, rows):

    # TODO improve how the columns are counted
    n_cols = header.strip('|').count('|')
    table=[]
    if header_separator.strip('|').count('|') != n_cols:
        print("Mismatched number of columns for the header", n_cols, " <> ", header_separator.strip(' |').count('|'))
        return [header]+[header_separator]+rows

    table.append(header.strip('|').split('|'))

    for row in rows:
        if row.strip(' |').count('|') - row.strip('|').count('\|') != n_cols:
            print("Mismatched number of columns for the row")
            return [header]+[header_separator]+rows
        
        table.append(row.strip('|').split('|'))
            
    
    table = fix_table_hyphenation(table)

    col_lengths = [max(len(str(x)) for x in col) for col in zip(*table)]

    table = fix_col_length(table, col_lengths)

    return create_table_as_rows(table, col_lengths)


    
def fix_col_length(table, col_lengths):
    new_table = []
    for row in table:
        new_row = []
        for col, element in enumerate(row):
            element = element + " " *(col_lengths[col]- len(element))
            new_row.append(element)

        new_table.append(new_row)

    return new_table

def fix_table_hyphenation(table):
    new_table = []
    for row in table:
        new_row = []
        for element in row:
            new_row.append(add_breakable_char(element))
        new_table.append(new_row)

    return new_table


def create_table_as_rows(table, col_lengths):

    new_table = []
    separator_char = '='
    separator = '+'
    for col_len in col_lengths:
        separator = separator  + col_len* "-" + '+'
    new_table.append(separator)

    first = True
    for row in table:
        new_row = '|'
        separator='+'
        first = True
        for col, element in enumerate(row):
            new_row = new_row + element + '|'
            
            separator = separator + (col_lengths[col])* separator_char + '+'
            first = False

        first = False

        new_table.append(new_row)
        new_table.append(separator)

        #only the first time '=' is used
        separator_char = '-'
    return new_table


def add_breakable_char2(element):
    new_ele =''
    if '\\' in element or '*' in element:
        return element

    for character in element:
        if character in (string.ascii_letters + string.digits):
            new_ele = new_ele + "\\BreakableChar{}"+ character
        else:
            new_ele = new_ele + character

    return new_ele

def add_breakable_char(element):
    new_ele =''
    if element is None:
        return ''
    if "http" in element:
        
        return process_breakable_with_html(element)

    #try hypenathion using a libray
    subelements = hyphenate_word(element)

    if isinstance(subelements, basestring):
         # add more break characters if len >4
        if len(subelements) > 4:
            subelements = re.sub("(.{4})", "\\1\\BreakableChar{}", subelements, 0, re.DOTALL)
        return subelements
    else:
        for subelement in subelements:
            # add more break characters if len >4
            if len(subelement) > 4:
                new_ele = new_ele + re.sub("(.{4})", "\\1\\BreakableChar{}", subelement, 0, re.DOTALL)
            else:
                new_ele = new_ele + subelement

    return new_ele


def process_breakable_with_html(element):

    #search md link - we do not process it
    pattern = '(?P<prev>.*)(?P<mdurl>\[.*\]\(https?://[^ ]*\))(?P<last>.*)'
    result = re.search(pattern,element, flags=re.IGNORECASE)

    

    if result:
        return (add_breakable_char(result.group('prev')) +
            result.group('mdurl') +
            add_breakable_char(result.group('last'))
            )

    #pattern = '(?P<prev>.*?)(?P<url>https?://[^ ]*)(?P<last>.*)'
    pattern = '(?P<prev>.*[^\[].*[^\]][^\(])?(?P<url>https?://[^ ]*)(?P<last>.*)'
    result = re.search(pattern,element, flags=re.IGNORECASE)

    if result:
        return (add_breakable_char(result.group('prev')) +
            re.sub('(https?://[^ ]*)','\\url{\\1}',result.group('url')) +
            add_breakable_char(result.group('last'))
            )
    else:
        return element



def have_table_separator(line):
    header_div_pattern=r'^\|?[- |]*((\-:?\|:?\-))[- |]*\|?$'
    return re.search(header_div_pattern,line.strip()) is not None
