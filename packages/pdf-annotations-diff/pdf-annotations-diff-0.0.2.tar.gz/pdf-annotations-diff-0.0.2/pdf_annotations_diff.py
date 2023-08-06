#!/usr/bin/env python3

import sys
import fitz  # PyMuPDF
import ast


def get_annotations(pdf_file):
    try:
        doc = fitz.open(pdf_file)
        annotations = []
        for i in range(len(doc)):
            for annot in doc[i].annots():
                page = doc[i]
                words = page.get_text("words")  # list of words on page
                words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x coordinate
                annot_rect = annot.rect  # rectangle of this annotation
                text_range = [
                    w for w in words if fitz.Rect(w[:4]).intersects(annot_rect)
                ]
                text_range_content = " ".join(w[4] for w in text_range)
                annotations.append(
                    (
                        i,
                        str(annot.info),
                        annot.info.get("content", ""),
                        text_range_content,
                        annot.type[1],
                    )
                )
        return annotations
    except Exception as e:
        print(f"Error reading annotations in file {pdf_file}: {str(e)}")
        sys.exit(1)


def format_annotation(annotation):
    page_num, annot_info_str, annot_content, text_range_content, annot_type = annotation
    annot_info = ast.literal_eval(annot_info_str)

    formatted_annot = f"{annot_type} at page {page_num+1}\n"  # Pages are 0-indexed, so add 1 for display
    if text_range_content:  # Only add "Text" field if it has content
        formatted_annot += f"Text: {text_range_content}\n"
    if annot_content:  # Only add "Content" field if it has content
        formatted_annot += f"Content: {annot_content}\n"
    formatted_annot += f"Info:\n"
    for key, value in annot_info.items():
        if value:  # Only show the fields that have a value
            formatted_annot += f"  {key}: {value}\n"

    return formatted_annot


def compare_files(file1, file2):
    annotations1 = get_annotations(file1)
    annotations2 = get_annotations(file2)

    unique_annotations1 = set(annotations1) - set(annotations2)
    unique_annotations2 = set(annotations2) - set(annotations1)

    if unique_annotations1:
        print(f"Unique Annotations in {file1}:\n")
        for annotation in unique_annotations1:
            print(format_annotation(annotation))
    if unique_annotations1 and unique_annotations2:
        # Insert a horizontal rule between the two files
        print("-" * 80 + "\n")
    if unique_annotations2:
        print(f"Unique Annotations in {file2}:\n")
        for annotation in unique_annotations2:
            print(format_annotation(annotation))


def main():
    # Check that two arguments are provided
    if len(sys.argv) != 3:
        print("Usage: pdf-annotations-diff file1.pdf file2.pdf")
        sys.exit(1)

    compare_files(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
