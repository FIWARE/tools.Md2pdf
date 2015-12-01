from __future__ import print_function
import re
from sys import platform
import math
from hyphenate import *



def translate_md_tables(markdown_content):
    """ Convert github tables to grid tables"""

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
        elif candidate_header is not None:
            readed_lines.append(candidate_header)

        readed_lines.append(line) 
        candidate_header = None
        table = False
        separator = False
        table_lines = []
    markdown_content = '\n'.join(readed_lines)
    return markdown_content


def count_row_columns(row):
    stripped_row = row.strip().strip('|')
    return stripped_row.count('|') - stripped_row.count('\|') + 1


def split_row_columns(row):
    # TODO: Don't split \|
    if platform == "win32":
        # If we don't strip columns in Windows tables aren't rendered in PDF.
        columns = row.strip().strip('|').split('|')
        return [column.strip() for column in columns]
    else:
        return row.strip('|').split('|')


def generate_md_table(header, header_separator, rows):

    # TODO improve how the columns are counted
    n_cols = count_row_columns(header)
    table=[]
    if count_row_columns(header_separator) != n_cols:
        print("Mismatched number of columns for the header", n_cols, " <> ", count_row_columns(header_separator))
        return [header]+[header_separator]+rows

    
    table.append(split_row_columns(header))

    for row in rows:
        if count_row_columns(row) != n_cols:
            print("Mismatched number of columns for the row")
            return [header]+[header_separator]+rows
        
        table.append(split_row_columns(row))
    
    table = fix_table_hyphenation(table)

    col_lengths = [max(len(str(x)) for x in col) for col in zip(*table)]

    col_lengths = [int(math.ceil(col_len + (sum(col_lengths)-col_len)*0.2 )) for col_len in col_lengths]

    table = fix_col_length(table, col_lengths)

    return create_table_as_rows(table, col_lengths)


    
def fix_col_length(table, col_lengths):
    new_table = []
    for row in table:
        new_row = []
        for col, element in enumerate(row):
            element = element + " " *(col_lengths[col]- len(element))
            #element = element + " " * int(math.ceil((col_lengths[col]+(sum(col_lengths) - col_lengths[col] )*0)- len(element)) )
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


def add_breakable_char(element):
    new_ele =''
    if element is None:
        return ''

    if "`" in element:
        return process_breakable_with_code(element)
        
    if "http" in element:
        
        return process_breakable_with_html(element)

    #try hypenathion using a libray
    subelements = hyphenate_word(element)

    if isinstance(subelements, basestring):
         # add more break characters if len >4
        if len(subelements) > 4:
            subelements = re.sub("([a-zA-Z0-9 ]{3})", "\\1\\BreakableChar{}", subelements, 0, re.DOTALL)
        return subelements
    else:
        for subelement in subelements:
            # add more break characters if len >4
            if len(subelement) > 4:
                new_ele = new_ele + re.sub("([a-zA-Z0-9 ]{3})", "\\1\\BreakableChar{}", subelement, 0, re.DOTALL)
            else:
                new_ele = new_ele +'\\BreakableChar{}'+ subelement

    return new_ele


def process_breakable_with_code(element):


    #search inline code with ``` - do not process it
    pattern='(?P<prev>.*)(?P<code>```[^`]+```)(?P<last>.*)'
    result = re.search(pattern,element, flags=re.IGNORECASE)

    if result:
        return (add_breakable_char(result.group('prev')) +
            result.group('code') +
            add_breakable_char(result.group('last'))
            )    

    #search inline code with ` - do not process it
    pattern='(?P<prev>.*)(?P<code>`[^`]+`)(?P<last>.*)'
    result = re.search(pattern,element, flags=re.IGNORECASE)

    if result:
        return (add_breakable_char(result.group('prev')) +
            result.group('code') +
            add_breakable_char(result.group('last'))
            )

    return element



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

    return element #avoid urlize the element, pandoc will do it for us
    if result:
        return (add_breakable_char(result.group('prev')) +
            re.sub('(https?://[^ ]*)','\\url{\\1}',result.group('url')) +
            add_breakable_char(result.group('last'))
            )
    else:
        return element



def have_table_separator(line):
    header_div_pattern=r'^\|[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|$'
    return re.search(header_div_pattern,line.strip()) is not None
