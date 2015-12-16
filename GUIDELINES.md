# GUIDELINES

This document lists the basic guidelines for writing the Markdown files for the Markdown to PDF (md2pdf) converter tool.

## General

* Leave a blank line before and after each block (titles, lists, paragraphs, tables, code sections, ...).
* Long words should be marked as code (ie. `long-word`) so they do not go out of the PDF page once rendered.
* The tool interprets the input files as Markdown with soft line break so, a single new line is not interpreted as line break. There should be two blanks lines between paragraphs. 
    * The tool does not allow to scape the new line character with `\` at the end of the lines.
* Inline code inside titles is not allowed. If it is used an error like this could appear:

    ```
    ! Undefined control sequence.
    \SQSPL@scan ->\futurelet \SQSPL@next 
                                         \SQSPL@scani 
    l.3276 element}{The requirements element}}
    ```

## URLs

* In order to write example URLs with tokens we recomended encapsulated it with ** \` ** or with **\`\`\`**. Example: ```http://{foo}/<bar>```

## Images

* Animated GIF images are not supported.
* SVG images are currently not supported.

## HTML

* HTML code in general is not allowed. Only support for anchors is provided. An anchor should be like:
    ```
    <a name="anchorid"></a>
    ```
    Elements between `>` and `</a>` are not allowed.


## Tables

* Only tables with GFM format are supported. Reference: <https://help.github.com/articles/github-flavored-markdown/#tables>
* Column widths are calculated proportionally to the maximum number of characters of its cells. If one of the generated columns is to small, simply add blanks spaces at the end of the cell content to compensate its width.
* Avoid to start cells with `-`, `*`, `+` or `<number>. because they will be interprted as a lists.
* Currently, tables inside code blocks are not allowed.

### Table rows and pipes

Every table row must start and end with a pipe (`|`), so **the following is incorrect**:

```
 A | B 
---|---
 C | D 
```

The table should be writen as follows:

```
| A | B |
|---|---|
| C | D |
```

### Table indentation

Tables should not be idented, so the following is not allowed:

```
  | A | B |
  |---|---|
  | C | D |
```

## Lists

* Indent every sublist and other inner elements inside a list **with 4 spaces (or 8, for indented code blocks)**. For example

    ```
    - Item 1

        - Item 1.2

    - Item 2

        ```
        Code item 2.1
        ```

    - Item 3

            Code item 3.1 - This requires 8 spaces instead of 4!
    ```
