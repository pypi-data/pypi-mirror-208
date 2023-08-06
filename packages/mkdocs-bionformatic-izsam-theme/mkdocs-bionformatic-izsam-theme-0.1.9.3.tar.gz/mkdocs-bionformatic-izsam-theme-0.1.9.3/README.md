# mkdocs-bioinformatic-izsam-theme

This is an MkDocs theme designed to layout the documentation provided by Bioinformatic Unit of the Istituto Zooprofilattico Sperimentale dell'Abruzzo e del Molise "G. Caporale".

#### Important!

The theme is intended to work with the plugin **mkdocs-izsam-search** [https://pypi.org/project/mkdocs-izsam-search/](https://pypi.org/project/mkdocs-izsam-search/)

```bash
pip install mkdocs-izsam-search
```

## Theme customization

The theme allows you to customize Title and top right label using your mdkdocs configuration file `mkdocs.yml`.

```yaml
extra:
  platform_title: Piattaforma GenPat
  header_tool_label: Wiki
  header_tool_label_mobile: Wiki
```

## Theme localization

The theme supports a lightweight localization system written in javascript. At the moment it supports Italian and English but you are free to add every language by duplicate the existing `js/theme-langauges/theme-loc-en.js` file and renaming it with your language a for example `js/theme-langauges/theme-loc-it.js`. Edit/override `js/theme-localization.js` to add more fields and translations.

> Please refer to MkDocs documentation on how to customize a theme [https://www.mkdocs.org/user-guide/customizing-your-theme/#customizing-your-theme](https://www.mkdocs.org/user-guide/customizing-your-theme/#customizing-your-theme).

To activate the localization, add a value to `locale` in `config.theme`:

```yml
theme:
  name: bioinformatic-izsam-theme
  locale: it
```

Here the code used in the theme (`base.html`) to hold the localization:

```html
{% if config.theme.locale %}
  {% set js_path = 'js/theme-languages/theme-loc-' ~ config.theme.locale ~ '.js' %}
  <script src="{{ js_path|url }}"></script>
  <script src="{{ 'js/theme-localization.js'|url }}"></script>
{% endif %}
```

#### Important!

The `locale` variable is used also to set search functionalities, there are some limitations on the values it can assume. Allowed languages are: `ar`, `da`, `de`, `du`, `es`, `fi`, `fr`, `hi`, `hu`, `it`, `ja`, `jp`, `nl`, `no`, `pt`, `ro`, `ru`, `sv`, `ta`, `th`, `tr`, `vi`, `zh`. If you want to use a different language, you should not to use **mkdocs-izsam-search** plugin and customize the `base.html` file removing all the code related to it.

## Theme features

#### Use image caption

If you need to use a caption for images, you can use the markdown image title sintax.

`![](image.png "image title")`

> A function in `theme.js` loops all images and if a title exists will append a `figcaption` tag after the image.

#### Use icons inline

To use icons inline inside the contents, please add the alt attribute `inline-icon`:

```
![inline-icon](icona.png)
```

> Images will have inherent size and displayed inline.

#### Use diagram as images (no plantuml)

To use diagram inside the contents as images, please add the alt attribute `diagram` to avoid box shadow.

```
![diagram](file.png)
```

#### Expand image

`zoom-img.js` allows images to be expanded on click.