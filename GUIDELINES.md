# This document lists the basic guidelines for writing the Markdown files for the Markdown to PDF converter tool.


* HTML code in general is not allowed. Only support for anchors is provided.
* Inline code inside titles is not allowed. If it is used an error like this could appear:

```
! Undefined control sequence.
\SQSPL@scan ->\futurelet \SQSPL@next 
                                     \SQSPL@scani 
l.3276 element}{The requirements element}}
```

* Leave a blank line before and after each block (titles, lists, paragraphs, tables, code sections, ...).
* Only tables with GFM format are supported. Reference: <https://help.github.com/articles/github-flavored-markdown/#tables>
    * Column widths are calculated proportionally to the maximum number of characters of its cells. If one of the generated columns is to small, simply add blanks spaces at the end of the cell content to compensate its width.
    * Avoid to start cells with `-`, `*`, `+` or `<number>. because they will be interprted as a lists.
* The tool interprets the input files as Markdown with soft line break so, a single new line is not interpreted as line break. There should be two blanks lines between paragraphs. 
    * The tool does not allow to scape the new line character with `\` at the end of the lines.