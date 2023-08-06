import argparse
import os
import re

from .upload_images import upload_images

OBSIDIAN_IMAGE_LINK_RE = re.compile(r"!\[\[([^\]]*)\]\]")


def append_newline_to_list_items(markdown_string):
    # Regular expression pattern to match unordered and ordered list items
    pattern = r"(^[-*+]\s|\d+\.\s)"

    # Split the markdown string into lines
    lines = markdown_string.split("\n")

    # Iterate over each line and check for list items
    for i in range(len(lines)):
        # Check if the line starts with a list item
        if re.match(pattern, lines[i]):
            # Append a newline character before the list item
            lines[i] = "\n" + lines[i]

    # Join the modified lines back into a single string
    modified_string = "\n".join(lines)
    return modified_string


def ensure_image_link_newline(markdown_string):
    # Find all image links in the markdown string
    image_links = re.findall(OBSIDIAN_IMAGE_LINK_RE, markdown_string)

    # Iterate over each image link and ensure it appears at the beginning of a newline
    for image_link in image_links:
        # Replace the image link with a newline + image link
        markdown_string = markdown_string.replace(
            f"![[{image_link}]]", "\n" + f"![[{image_link}]]"
        )

    return markdown_string


def process_image_link(container, conn_str, image_folder, re_match, is_mdnice):
    image_link = re_match.group(1)
    if not image_link.startswith("http://") and not image_link.startswith("https://"):
        uploaded_urls = upload_images(
            container,
            conn_str,
            image_folder,
            [image_link],
            overwrite=True,
        )
        image_link = uploaded_urls[0]
    if is_mdnice:
        return f"![]({image_link})"
    else:
        return f'<img src="{image_link}" class="origin_image zh-lightbox-thumb lazy">\n'


def main():
    parser = argparse.ArgumentParser(
        description="""
    Convert standard Markdown file to mdnice Format
    1. Upload all the images

    Assume all the local image links in markdown file is relative paths based on `image_folder`
    """
    )

    parser.add_argument(
        "--container",
        help="The Container which the file will be uploaded to.",
        default="imagehost",
    )
    parser.add_argument(
        "--mdnice",
        action="store_true",
        help="Convert to mdnice format, default is zhihu format",
    )
    parser.add_argument("image_link_root", help="The root folder of image links.")
    parser.add_argument("output_folder", help="The folder to store converted md files")
    parser.add_argument(
        "files", nargs="+", help="The file to be uploaded. Must Include at least one."
    )

    args = parser.parse_args()
    container = args.container
    image_link_root = args.image_link_root
    output_folder = args.output_folder
    files = args.files
    conn_str = os.environ["IMAGEHOST_CONN_STR"]

    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        output_file_path = os.path.join(output_folder, os.path.split(file_path)[1])
        with open(file_path, encoding="utf-8") as in_f, open(
            output_file_path, "w", encoding="utf-8"
        ) as out_f:
            content = in_f.read()
            new_content = ensure_image_link_newline(content)
            new_content = OBSIDIAN_IMAGE_LINK_RE.sub(
                lambda m: process_image_link(
                    container, conn_str, image_link_root, m, args.mdnice
                ),
                new_content,
            )
            if not args.mdnice:
                # if append newline before list items for mdnice,
                # there will be extra newline between items after rendering
                new_content = append_newline_to_list_items(new_content)
            out_f.write(new_content)


if __name__ == "__main__":
    main()
