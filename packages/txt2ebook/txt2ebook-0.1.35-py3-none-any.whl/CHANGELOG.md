# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## [Unreleased]

## v0.1.35 - 2023-05-14

### Added

- Add and get default font name and file from language settings
- Add table of content to PDF file
- Log when generating volume or chapter in PDF output

### Changed

- Refactor all writer class to use common generated filename
- Use translated table of content text in PDF output

## v0.1.34 - 2023-05-07

### Added

- Add initial support for exporting to PDF format through `-f pdf` for
  `--language zh-cn`

### Changed

- Group deps accordingly
- Ensure pre-commit works with Python 3.11

### Fixed

- Update missing translations

## v0.1.33 - 2023-04-30

### Added

- Add tests for `format` flag

### Changed

- Bump Python's deps
- Regroup Python deps under same group in project config
- Refactor common functions for format writer as abstract class

### Fixed

- Fix missing dep error in environments for Tox

## v0.1.32 - 2023-04-23

### Added

- Add initial support for exporting to Markdown (`md`) format

### Changed

- Bump Python's deps
- Update PyPi's classifiers

## v0.1.31 - 2023-04-16

### Added

- Add new filename format of `authors_title.ebook_extension`
- Add initial pypandoc dep for future support for pandoc

### Fixed

- Fix incorrect example in help message

## v0.1.30 - 2023-04-09

### Added

- Add `-of` or `--filename-format` to save filename in different naming
  convention

### Changed

- Rename all test files with names from `options` to `flags`
- Add missing typing for Book model

## v0.1.29 - 2023-04-02

### Fixed

- Fix missing replacing space with underscore when exporting multiple text file

### Changed

- Ensure all split and overwritten text filenames are in lower case and
  underscore

## v0.1.28 - 2023-03-26

### Added

- `zh_words_to_numbers(words, match_all=True)` will convert all found word, by
  default it convert the first found word only

### Changed

- Convert `zh_words_to_numbers` to support keyword arguments,
  `zh_words_to_numbers(words, length)` to `zh_words_to_numbers(words, length=5)`

## v0.1.27 - 2023-03-19

### Added

- Add `-toc` or `--table-of-content` option which add a toc to the text file

### Changed

- Change filename format when generating multiple txt through `-sp` option
- Remove `-ob` or `--overwrite-backup` option
- New `txt` file will be created when `-f txt` option is set
- Group options in help message

### Fixed

- Fix cannot set export format to `txt`

## v0.1.26 - 2023-03-12

### Changed

- Rename epub template names, `clean_no_indent` to `noindent`, and
  `clean_no_paragraph_space` to `condense`
- Raise warnings for invalid prepend length for `zh_words_to_numbers` function

### Fixed

- Fix missing translations
- Fix missing EPUB template names not showing in help message

## v0.1.25 - 2023-03-05

### Added

- Add new EPUB templates, `clean_no_indent` and `clean_no_paragraph_space`

### Fixed

- Add missing `zh-*` character for `zh_numeric`
- Remove unused import
- Fix incorrect dep added to wrong environment

### Changed

- Refactor ebook extensions variable into package

## v0.1.24 - 2023-02-26

### Changed

- Remove escaped paragraph separator argument during argument parsing
- Extract and add `zh_utils.zh_words_to_numbers` function
- Bump Python's version for `pyenv`

## v0.1.23 - 2023-02-19

### Changed

- Refactor conversion of halfwidth to fullwidth into
  `zh_utils.zh_halfwidth_to_fullwidth` function
- Support default value for `zh_utils.zh_numeric` function
- Add more chapter regex for `zh-*` language
- Revise default environments for tox to run
- Group options by ebook format in help message

## v0.1.22 - 2023-02-12

### Added

- Add missing chapter number for `zh-*`
- Support more conversion of chapter words to numbers for `zh-*` language
- Add `zh_utils` module for handling all `zh-*` language text

## v0.1.21 - 2023-02-05

### Added

- Add `-sp` or `--split-volume-and-chapter` to export a `txt` file into
  multiple text files by header

### Fixed

- Exclude gettext related files from pre-commit

## v0.1.20 - 2023-01-29

### Fixed

- Fix UUID not added to the EPUB e-book

### Changed

- Add more test cases to improve test coverage
- Format help message indentation to improve readability
- Put coverage report config into `.coveragerc`
- Speed up tests through parallel testing using `pytest-xdist`

## v0.1.19 - 2023-01-22

### Added

- Support Python 3.11 environment for Tox in testing

### Fixed

- Fix cannot build doc in Tox
- Fix missing msgfmt step for updating mo translation files
- Remove unused `cchardet` dep which break Python 3.11

### Changed

- Set base python in Tox env to Python 3.11
- Use correct way to get module attribute
- Use gettext for structure names for book model

## v0.1.18 - 2023-01-15

### Changed

- Use Gettext for localization of book metadata by language
- Remove chapter regex rule that affect header with punctuation
- Support long options for all command option flags
- Warn on mismatch between configured and detected language

### Fixed

- Fix missing default tags regex for `en` language
- Fix words to numbers conversion `-hn` only applies to `zh-cn` or `zh-tw`
  language
- Fix halfwidth to fullwidth conversion `-fw` only applies to `zh-cn` or `zh-tw`
  language
- Fix incorrect text file generated due to undecode paragraph separator

## v0.1.17 - 2023-01-08

### Added

- Add `-v`, `-vv`, or `-vvv` to set verbosity level for debugging log
- Add test cases for `-hn` or `--header-number` option
- Add test cases for `-rw` or `--raise-warns` option
- Show line number in source file for token in debug log
- Support repr for Tokenizer class

### Changed

- Add padding between volume in table of content in default EPUB CSS style
- Generated output ebook filename should follow the source input filename by
  default instead of title of the ebook
- Replace categories with tags of a book metadata
- Show debug log for tokenized chapter at `-vv` and paragraph at `-vvv`
- Show selected text when converting words to numbers in debug log
- Show token sequence number in padded zeroes in debug log
- Rename `raise-warns` option to `raise-on-warning`
- Use `-V` flag instead of `-v` for show program version
- Use the sample paragraph separator `-ps` when exporting to text format

## v0.1.16 - 2022-12-30

### Added

- Add `-hn` or `--header-number` to convert section sequence from words to
  numbers, only for `zh-cn` language, and left padding added when section
  sequence is integer
- Add `-fw` or `--fullwidth` to convert ASCII characters from halfwidth to
  fullwidth numbers, only for `zh-cn` language
- Add `-rw` or `--raise-warns` to raise exception when there are warnings on
  parsing
- Add `-ob` or `--overwrite-backup` to overwrite massaged content and backup
  the original source content
- Add category field to metadata of the book
- Add `repr` for Volume model
- Show warning on extra newline before section header
- Get statistic data on Book model

### Changed

- Output text file from parsed Book structure data instead of massaged text
- Rename `-nb` / `--no-backup` option as `-ow` / `--overwrite`
- Retain the original source content file by default unless explicitly set
  using `-ow`
- Do not backup source content file by default unless explicitly set using
  `-ob`
- Support setting multiple ebook formats at once using `-f` option
- Remove unused `raw_content` field for Volume and Chapter model
- Add custom `repr` for Volume and Chapter model
- Deprecate `DEFAULT_RE_VOLUME_CHAPTER` regex for each language
- Update and revise regex for different section header for `zh-cn` and `en`
  language
- Use `logger.warning` instead of deprecated `logger_warn`
- Refactor debugging and logging of Book model
- Raise warning when cannot split paragraphs by paragraph separator
- Raise warning when no table of content found when generating ebook
- Deprecate unused `raw_content` field in Volume and Chapter model

### Fixed

- Fix and update regex patterns for `zh-cn` language
- Fix escaped paragraph separator not unescaped when set from command line

## v0.1.15 - 2022-11-10

### Fixed

- Fix missing volume pattern when parsing header with both volume and chapter
- Fix help menu which affected the sphinx doc generation

### Changed

- Shorten the option description in the help menu
- Refactor parsing by tokenizing instead
- Support and test against Python 3.11

## v0.1.14 - 2022-10-14

### Added

- Able to run program as `python -m txt2ebook` or `python -m src.txt2ebook`
- Add `--rvc` option to parse header with volume and chapter title
- Add `--ps` option to parse text file by paragraph separator
- Show repo details in help message

### Changed

- Replace DotMap with argparse.Namespace as config container
- Handle argument parsing using argparse standard library instead of Click
- Logging using standard library instead of loguru
- Show stacktrace in debug mode or `-d` option enabled
- Use `importlib.resources` to load CSS template
- Refactor language config into separate own module
- Refactor to use single Parser module to handle all supported languages
- Switch linting to pre-commit instead of tox environment
- Use better approach to handle exception message
- Test console script directly using pytest-console-scripts

## v0.1.13 - 2022-05-02

### Added

- Generate documentation through Sphinx
- Add contribution guideline on how to contribute to this project
- Add `-vp/--volume-page` option to create separate page for volume title
- Add `-rv/--re-volume` option to parse multiple volume header by regex
- Add `-rc/--re-chapter` option to parse multiple volume header by regex
- Add `-ra/--re-author` option to parse and extract author by regex
- Add `-rt/--re-title` option to parse and extract title by regex

### Changed

- Rename and standardize on regex option
- Rename `-dr/--delete-regex` to `-rd/re-delete`
- Rename `-rr/--replace-regex` to `-rr/re-replace`
- Rename `-dlr/--delete-line-regex` to `-rl/re-delete-line`
- Refactor detecting book title to base parsing class

### Fixed

- Show longer and exact raw string when repr(Chapter)

## v0.1.12 - 2022-01-18

### Added

- Add `tte` as the alternative shorter command name to `txt2ebook`
- Separate page for volume title in epub format
- Use Tox for automation and testing

### Changed

- Refactor EPUB template loading
- Refactor base parser module to use dataclass
- Stricter rules on Chinese header parsing
- Support Python 3.7 onwards
- Use DotMap to manage config
- Add more fields to repr for Chapter model

### Fixed

- Fix removing line by regex not working
- Fix section header not showing in toc in Foliate
- Fix cannot parse content with no empty line as paragraph separator
- Fix cannot generate ebook for English text file

## v0.1.11 - 2021-12-19

### Added

- Add `--epub-template/-et` option to set CSS style for EPUB file
- Add `--test-parsing/-tp` option to show only parsed headers without
  generating ebook
- Build cover page when cover image `--cover` was set
- Add typing to the project
- Update more project classifiers

### Changed

- Update default table of content style sheet
- Switch logging to loguru library and rephrase logging messages
- Wrap program's config with configuror library

### Fixed

- Do not capture newline when parsing book title and author name
- Add missing language when generating HTML for each chapter
- Remove whitespace in chapter title in HTML
- Generate EPUB file in tmp dir when running test case

## v0.1.10 - 2021-11-22

### Fixed

- Do not generate txt file twice when txt format was set
- Fix cannot parse txt file other than Unix line end
- Fix test default to unknown parser

### Changed

- Refactor parser and writer factory into subpackage
- Support setting multiple authors
- Move common functions to helper subpackage
- Set unique identified for epub based on book's title

## v0.1.9 - 2021-10-26

### Added

- Add `--format` option to specify output format

### Fixed

- Fix missing deps in requirements.txt
- Fix issues raised by PyLint

### Changed

- Refactor txt and epub file generation in separate module
- Refactor txt formatting and parsing in separate module
- Switch chapter header regex to constant

## v0.1.8 - 2021-10-04

### Added

- Allow setting of optional argument for output path and file name
- Add `--width` option to set line width for paragraph wrapping

### Changed

- Rename `--remove-wrapping` option to `-no-wrapping` to follow the convention
- Refactor and move string helper functions
- Refactor extracting title and author from txt file
- Replace magic number with constant
- Remove using Click's context object

### Fixed

- Disable backup txt fixtures during test
- Fix warnings raised by Pylint

## v0.1.7 - 2021-09-19

### Added

- Detect the original encoding of txt file, convert, and save to utf-8
- Add `--cover` option to add cover image to ebook

### Changed

- Revise logging message format
- Do not raise exception when no chapter header found
- Show indentation for chapter title in debugging message
- Match different chapter headers and line separator
- Replace full-width space with half-width space in chapter headers
- Generate HTML manually instead through Markdown
- Keep original txt file formatting except chapter header
- Refactor and use more ways to extract book title from txt file
- Relax chapter header regex rules

### Fixed

- Fix paragraph wrapping of imbalance opening and closing quote
- Fix group match not working with replacing regex

## v0.1.6 - 2021-09-11

### Changed

- Backup original txt file and overwrite with parsed content
- Include and refactor more chapter header regex

### Added

- Add `--no-backup` option to skip backup the original txt file

## v0.1.5 - 2021-09-02

### Added

- Add `--delete-regex` option to remove selected words or phrases from the file
  content
- Add `--replace-regex` option to replace selected words or phrases from the
  file content
- Add `--delete-line-regex` option to remove whole line from the file content
- Detect author name from file content
- Parse volumes and chapters correctly and generate nested toc

### Fixed

- Fix incorrect chapter filename
- Fix missing title in Epub file
- Fix issues raised by Flake8 and PyLint
- Replace missing space between chapter header and chapter title

### Changed

- Parse more different chapter headers
- Save HTML filename in Epub as chapter header and title
- Dump parsed txt file during debug mode
- Use only single quotation punctuation

## v0.1.4 - 2021-08-04

### Added

- Add `--remove_wrapping` option to remove text wrapping in the body content of
  a chapter
- Capture the book title from the file if found and not explicitly set through
  `--title` option

#### Fixed

- Fix no paragraph separation for txt file without single-line spacing for
  markdown
- Fix issues raised by PyLint

### Changed

- Parse more different chapter headers
- Refactor argument parsing

## v0.1.3 - 2021-07-24

### Fixed

- Fix no parsing and split by introduction chapter
- Fix issues raised by PyLint

### Changed

- Switch license to AGPL-3

## v0.1.2 - 2021-07-20

### Added

- Add option to set metadata for ebook
- Add missing requirements.txt
- Show full help message when missing required argument

### Changed

- Use better way to check for input file
- Print message using click.ecto
- Code formatting

## v0.1.1 - 2021-07-13

### Added

- Enable logging for debugging and showing status
- Set log level through `LOG` environment variable

### Fixed

- Check for missing filename, empty file content, and missing chapters

## v0.1.0 - 2021-07-08

### Added

- Initial public release
- Support converting txt file in Chinese language into epub format
