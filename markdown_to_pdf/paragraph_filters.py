#!/usr/bin/env python

from pandocfilters import *
import re
from links_processing import *
import pprint



def pandoc_filter(key, value, format, meta):
    """Filter applied by Pandoc when converting from Mardown to PDF"""
    if key == 'Para':
        new_value=[]
        new_elements=[]
        #value is list, elemnts is a dic
        for element in value:
            scape_char = False

            if element['t'] == 'LineBreak':
                if len(new_elements) > 1:
                    if new_elements[-1]['t'] == 'Str':
                        if new_elements[-1]['c'][-1] == '\\' and len(new_elements[-1]['c'])> 2:
                            new_elements[-1]['c'] = new_elements[-1]['c'][:-1]
            new_elements.append(element)
        if new_elements[-1]['t'] == 'Str':
            if new_elements[-1]['c'][-1] == '\\' and len(new_elements[-1]['c'])> 2:
                            new_elements[-1]['c'] = new_elements[-1]['c'][:-1]
        
        return Para(new_elements)
    elif key in ['OrderedList', 'BulletList']:
        return None

    return None
    
    
pandoc_filter.current_file = ''


def main():
    toJSONFilter(pandoc_filter)


if __name__ == "__main__":
    main()
