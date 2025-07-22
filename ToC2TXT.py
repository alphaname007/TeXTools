import re
import streamlit as st

# --- Constants ---
# Regular expressions are compiled here once for efficiency.
LINE_REGEX = re.compile(r'\\contentsline \{(.*?)\}\{(.*?)\}\{(.*?)\}')
NUMBERLINE_REGEX = re.compile(r'\\numberline \{(.*?)\}(.*)')

# A dictionary to map LaTeX levels to indentation depths.
INDENT_LEVELS = {
    "section": 0,
    "subsection": 1,
    "subsubsection": 2,
}


def parse_toc(toc_content: str, make_numbering: bool, indent_size: int, make_page: bool) -> str:
    """
    Parses the content of a LaTeX .toc file and returns a clean text representation.

    Args:
        toc_content (str): The string content of the .toc file.
        make_numbering (bool): If True, section numbering will be preserved.
        indent_size (int): The number of spaces per indentation level.
        make_page (bool): If True, the page number is appended to the end of each line.

    Returns:
        str: A formatted string representing the table of contents.
    """
    output_lines = []

    for line in toc_content.strip().split('\n'):
        # Search for the main structure of a \contentsline entry.
        match = LINE_REGEX.match(line)
        if not match:
            continue

        level, title_raw, page_num = match.groups()

        # Determine the indentation based on the section level.
        indent_depth = INDENT_LEVELS.get(level, 0)
        indent = ' ' * (indent_depth * indent_size)

        # Append the page number if requested.
        page = f" {page_num}" if make_page else ""

        # Process numbered and unnumbered entries.
        number_match = NUMBERLINE_REGEX.match(title_raw)
        if number_match:
            num, txt = number_match.groups()
            text = txt.strip()
            number = f"{num} " if make_numbering else ""
        else:
            text = title_raw.strip()
            number = ""

        # Assemble the final line and add it to the list.
        output_lines.append(f"{indent}{number}{text}{page}")

    return "\n".join(output_lines)


def main():
    """
    Initializes and runs the Streamlit web application.
    """
    st.set_page_config(page_title="LaTeX TOC to Text", page_icon="📄")
    st.title("LaTeX TOC to Plain Text Converter")
    st.write("Upload a LaTeX `.toc` file to extract its table of contents as plain text.")

    # --- Sidebar for Settings ---
    with st.sidebar:
        st.subheader("Settings ⚙️")
        make_numbering = st.checkbox("Add numbering", value=True)
        make_page = st.checkbox("Add page numbers", value=True)

        # The indentation settings are conditional.
        add_indentation = st.checkbox("Add indentation", value=True)
        indent_size = 0
        if add_indentation:
            indent_size = st.number_input(
                "Indent size (spaces)",
                min_value=1,
                max_value=10,
                value=4,
                step=1
            )

    # --- File Upload and Processing ---
    uploaded_file = st.file_uploader("Choose a .toc file", type=["toc", "txt"])

    if uploaded_file:
        try:
            toc_content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            st.error("Error: Failed to decode the file. Please ensure it's UTF-8 encoded.")
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.stop()

        # Parse the content with the selected settings.
        result = parse_toc(toc_content, make_numbering, indent_size, make_page)

        # --- Display Results ---
        if result:
            st.subheader("Formatted Table of Contents")
            st.text_area("Preview", result, height=400)
            st.download_button(
                label="Download as .txt",
                data=result,
                file_name="table_of_contents.txt",
                mime="text/plain"
            )
        else:
            st.warning("No entries could be parsed from the file.")


if __name__ == "__main__":
    main()
