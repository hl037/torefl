======
TOREFL
======

TOREFL means To REFerence List, as the list of publications you will like to reference later when you will write some latex documents... And since some parts were developed at Paris, you will get the... reference (pun intended)

Features
========

* Non-verbose command line interface
* Easy management of references with tags, rating etc.
* Pdf and metadata saved in the file system
* Easy opening of a reference from its name or its ID
* Powerful search and system on description, tags, rating, and any bibtex fields
* Memorization of the selection you made (you can assign the result of a filter to sort of variable called register to match vim vocabulary)
* Export to bibtex format of either the entire bibliography either only a selection
* Possibility to edit the metadata from the software
* Easy to extend (create other formatters, exports, filter etc.

Philosophy
==========

This software is meant to respect KISS principles i.e. to be as simple as possible.

To use it, you only need to have a bibliography directory, and put all your pdf in it. The name of the pdf will be the bibtex identifier for using with the ``\cite`` command. Then, just touch a file with the same name but the ``.torefl`` extension.

so you should have a file tree like this ::

    biblio
    |--topology
    |  |--MorseTheory.pdf
    |  |--MorseTheory.torefl
    |  |--ReebGraph.pdf
    |  |--ReebGraph.torefl
    |--Other
    |  |--Matrices.pdf
    |  |--Matrices.torefl
    |--SuperArticle.pdf
    |--SuperArticle.torefl

.torefl format
==============

This file can be either empty, either contain only the reference in bibtex format, either contain some meta-data (format described below) and the bibtex both separated by a line starting with 16 stars : ``****************``

Example::

    #NotRead #Topology @10 
    
    Presentation of the #Morse Morse Theory
    
    @-55.0
    
    ****************
    
    @book{9781400881802,
      Author = {John Milnor},
      Title = {Morse Theory. (AM-51) (Annals of Mathematics Studies)},
      Publisher = {Princeton University Press},
      Year = {1963},
      ISBN = {9781400881802},
    }

**Note :** the identifier given in the bibtex will be discarded at export, and replaced by the name of the file without the extension

Metadata format
---------------

The metadata are basically a comment for yourself of the referenced article, a sum up, a description or whatever you like. You can also specify tags you will be able to search on, and also a rating that has the meaning you want, you will also be able to search on, with comparators like lesser than greater than etc.

Tags
~~~~

A tag is surrounded by two spaces, and begins with a ``#``. It will be converted to CamelCase starting with an uppercase letter. ``#TAG`` will become ``#Tag``, ``#test_tag`` will be converted to ``#TestTag``.

Rating
~~~~~~

The rating is surrounded by two spaces it begins by ``@`` followed by a positive or negative, int or float number. If there are several ratings in the metadata, only the last one will be used, the others will be discarded.

Comment
~~~~~~~

The parser removes all the tags and the ratings, and strip all spaces before and after the remaining. The remaining is what is called the "comment", or "description". It's user-defined, and you will also be able to search for string appearing in the comments.

From the previous example
~~~~~~~~~~~~~~~~~~~~~~~~~

In the previous example, the tags are ``#NotRead``, ``#Topology`` and ``#Morse``, the rating is ``-55.0`` (the ``@10`` being discarded), and the comment is "Presentation of the Morse Theory".

Using Torefl
============

To use Torefl, just go to your bibliography root, and type::

    $> torefl

(the ``$>`` means you are a standard user in your operating system)

Then, a command line appears. Here is a list of the commands :

Command List
============

Each command has a short and a long alias. Different aliases are separated by a coma below.

l, list
-------

::

    torefl>l [ [ [-leg] /path/*/patern/* ] [ #tags ]... [ @[ < | > | <= | >= | = ] ]... [ -bib [ [field] [content] ]... ] [-com [commentSearch] ]...

Lists the entries using or not a filter. There are 3 filters currently, legacy ( ``-leg``) (default filter at the begin), bibtex (``-bib``) and comment (``-com``). You can switch between them using the ``-xxx`` corresponding.

Without arguments, it just lists all the entries in the bibliography

You can combine them at your will, it will do an AND between the results. For a or, just do the filter twice, and use the selections (explained below)

legacy filter
~~~~~~~~~~~~~

Legacy because it is the first filter I did, and I added the other ones after.

The first parameter is a path to look into, using unix glob pattern. Then, you can add tags and priority filters. Tags will filter all articles with the given tags appearing in the ``.torefl``.
Rating start with ``@``, then a comparator (left member is the rating of the article, right member is the number to compare) followed by the number to compare to. ``@<30`` will give all entries with priority lesser than 30.

bibtex filter
~~~~~~~~~~~~~

Bibtex filter is a list of pairs ``field content``, and will keep only entries with a bibtex containing ``content`` in the field ``field``. You can put several field/content pairs and it will combine them with an AND between the results

comment filter
~~~~~~~~~~~~~~

The comment filter just filters the entries containing all the arguments given to the filter

o, open
-------

::

    torefl>o <ID|Name>

Opens ID (The blue number when listed using the default formatter) or the name (same identifier than used with \cite, i.e. the file name without extension) with the command given in the configuration key ``open_cmd``.

ed, edit
--------

::

   torefl>ed  <ID|Name>

Opens the ``.torefl`` file corresponding to ID (The blue number when listed using the default formatter) or Name (same identifier than used with \cite, i.e. the file name without extension) with the command given in the configuration key ``edit_cmd``, and refresh the database.

s, sel, selection
-----------------

This command permits to work with selections. Its syntax is just a mind f***. Any suggestion to improve it is definitively welcome !!!

::

    torefl>s <register> <operator> [register]

``register`` can be any register name. ``operator`` is an operator amoung ``|=`` (union), ``&=`` (intersection), ``^=`` (symetric difference), ``-=`` (difference) and ``=`` (copy).
The left member is assigned the result of the operation. The right member can be either empty (it will use the result of the previous list call) either ``0`` (the empty set), either another register name.

To do a 'OR' filter, one can do ::

    torefl>l [filter]
    torefl>s a =
    torefl>l [filter2]
    torefl>s a |=
    torefl>ls a

ls
---

List Selection ::

    torefl>ls <register>

List the content of ``register``

e, export
---------

::

    torefl>e -bib <filename> [register]

Exports in bibtex format the selection in register if given, else the selection of the previous call to ``list``. You have to type the ``-bib`` because other exporters could be supported in the future (like an html exporter or other reference list formats)


