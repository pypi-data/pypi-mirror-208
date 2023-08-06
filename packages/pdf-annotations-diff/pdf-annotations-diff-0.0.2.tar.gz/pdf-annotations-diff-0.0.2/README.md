# pdf-annotations-diff

I frequently need to compare my annotations on multiple versions of a PDF file. If you are amongst the three other people who need to do the same, this Python script would be useful to you.

This script compares annotations across two PDF files (which are assumed to be two versions of the same base PDF file). It outputs annotations that are unique to each of the two files.

## Installation

```bash
pip install pdf-annotations-diff
```

## Usage

To compare annotations in two PDF files, you can use the following command:

```bash
pdf-annotations-diff file1.pdf file2.pdf
```

## Dependencies

This script depends on the [PyMuPDF](https://pypi.org/project/PyMuPDF/) library.

## License

Licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Example

This is an example of how to use pdf-annotations-diff to compare two PDF files:

```bash
pdf-annotations-diff Men\ Without\ Women\ -\ Haruki\ Murakami.pdf Men\ Without\ Women\ -\ Haruki\ Murakami.sync-conflict.pdf
```

And the resulting output would look something like this:

```
Unique Annotations in Men Without Women - Haruki Murakami.pdf:

Underline at page 207
Text: paperback. Whenever he got tired of reading (at least, Kino guessed that he was tired), he looked up from the page and studied the bottles of liquor lined up on the shelves in front of him, as if examining a series of unusual taxidermied animals from faraway lands.
Info:
  title: NovaPro

Underline at page 248
Text: Teddy Wilson, Vic Dickenson, Buck Clayton— sometimes he longed desperately to listen to their old-time jazz, with its steady, dependable technique and its straightforward chords. He wanted to feel the pure joy they had in performing, their wonderful optimism. That was the kind of music Kino sought,
Info:
  title: NovaPro

Underline at page 180
Text: stapler, his calendar—the most mundane objects became somehow radiant by being his.
Info:
  title: NovaPro

--------------------------------------------------------------------------------

Unique Annotations in Men Without Women - Haruki Murakami.sync-conflict.pdf:

Highlight at page 207
Text: paperback. Whenever he got tired of reading (at least, Kino guessed that he was tired), he looked up from the page and studied the bottles of liquor lined up on the shelves in front of him, as if examining a series of unusual taxidermied animals from faraway lands.
Info:
  title: Sameer A5
  creationDate: D:20230423214101Z00'00
  modDate: D:20230423214101Z00'00
```
