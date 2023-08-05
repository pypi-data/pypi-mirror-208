Sphinx LV2 Theme
================

This is a minimal pure-CSS theme for [Sphinx][] that uses the documentation
style of the [LV2][] plugin specification and related projects.

This theme is geared toward producing beautiful API documentation for C, C++,
and Python that is documented using the standard Sphinx domains.  The output
does not use Javascript at all, and some common features are not implemented,
so this theme should not be considered a drop-in replacement for typical Sphinx
themes.

The design uses a sidebar on wide screens, but condenses to a linear document
if there is not enough space.  It is readable on very small mobile displays,
and produces reasonably nice output when printed.  The color palette is mostly
[Solarized][], but using neutral base colors and a few additional grays.

Principles
----------

This theme tries to adhere to a simple and accessible philosophy of web design
inspired by typeset documents, and avoids bloat by not inheriting from a
builtin Sphinx theme.

  - No Javascript.
  - No external dependencies.
  - Valid HTML5 and CSS output.
  - Small download size.
  - Uses only standard system fonts.
  - All sizes in text-based units.
  - Elegant sizing and spacing based on the golden ratio.
  - Sensible document hierarchy with minimal abuse of structure for style.
  - Readable on large and small screens, mobile devices, and when printed.

The use of a sidebar is a slight departure from the typeset document ideal, but
is included as an option since it is particularly useful for single-page
reference documentation, and an almost universally expected Sphinx feature.

Installation
------------

This theme can be installed with [pip][]:

    pip install sphinx_lv2_theme

Installation from the source directory is also possible:

    cd path_to_sphinx_lv2_theme_source
    pip install .

Options
-------

`body_max_width`
: CSS size, default `60em`.  The maximum width of the main body text.  This
  plus `sidebar_width` should be less than `page_width`.

`body_min_width`
: CSS size, default `50em`.  The minimum width of the main body text.  If the
  screen is too small to fit this and the sidebar, then the layout switches to
  a linear layout with the table of contents at the top.  If the screen is to
  small to fit just this, the layout is further compressed to suit very small
  displays as on mobile.

`description`
: String, default unset.  The project description displayed below the logo.

`globaltoc_collapse`
: Boolean, default `true`.  If true then all paths in the sidebar index that do
  not lead to the current page are collapsed.

`globaltoc_includehidden`
: Boolean, default `false`.  Include hidden entries in the sidebar index.

`globaltoc_maxdepth`
: Integer, default unset.  Maximum depth of the sidebar index tree.

`display_version`
: Boolean, default `true`.  If true then the version is displayed beside the
  logo name.

`logo`
: Path, default unset.  Logo to display at the top of the sidebar.

`logo_name`
: Boolean, default `true`.  If true then the project name is displayed below
  the logo.

`logo_width`
: CSS size, default `12em`.  The width of the sidebar logo.

`nosidebar`
: Boolean, default `false`.  If true then the sidebar is never displayed even
  on wide screens.

`page_width`
: CSS size, default `80em`.  The width of the content portion of the page,
  including both body and sidebar.

`show_footer_version`
: Boolean, default `true`.  If true then the project name and version is
  included in the footer.

`show_logo_version`
: Boolean, default `false`.  If true then the version is added to the logo
  text.

`show_nav_version`
: Boolean, default `true`.  If true then the version added to the root link on
  the navigation bar.

`sidebar_width`
: CSS size, default `20em`.  The width of the sidebar.  This plus
  `body_max_width` should be less than `page_width`.

Usage
-----

Add something lke the following to your `conf.py`:

```python

html_theme = "sphinx_lv2_theme"

html_theme_options = {
    "body_max_width": "62em",
    "body_min_width": "52em",
    "description": "Probably the greatest project ever.",
    "display_version": True,
    "globaltoc_collapse": False,
    "globaltoc_includehidden": False,
    "globaltoc_maxdepth": 3,
    "logo": "myawesomeproject.svg",
    "logo_name": True,
    "logo_width": "8em",
    "nosidebar": False,
    "page_width": "80em",
    "show_footer_version": True,
    "show_logo_version": False,
    "show_nav_version": True,
    "sidebar_width": "18em",
}
```

 -- David Robillard <d@drobilla.net>

[Sphinx]: https://www.sphinx-doc.org/
[LV2]: https://lv2plug.in/
[Solarized]: https://ethanschoonover.com/solarized/
[pip]: https://pypi.org/project/pip/
