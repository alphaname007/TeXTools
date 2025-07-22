import re
import streamlit as st


def parse_toc(content: str) -> str:
    """
    Parse LaTeX .toc content and return a plain-text representation.
    """
    pattern = re.compile(r'\\contentsline\s*{(?P<type>[^}]+)}\s*{(?P<raw_title>[^}]*)}\s*{(?P<page>[^}]*)}')
    indent_map = {'section': 0, 'subsection': 1, 'subsubsection': 2}
    lines_out = []
    for line in content.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        entry_type = match.group('type')
        raw_title = match.group('raw_title')
        page = match.group('page')
        # Extract numbering if present
        num_match = re.search(r'\\numberline\s*{(?P<num>[^}]*)}', raw_title)
        # Remove \numberline command to get clean title
        title_text = re.sub(r'\\numberline\s*{[^}]*}', '', raw_title).strip()
        if num_match:
            title = f"{num_match.group('num')} {title_text}"
        else:
            title = title_text
        # Indent based on section level
        indent = '    ' * indent_map.get(entry_type, 0)
        lines_out.append(f"{indent}{title} ..... {page}")
    return "\n".join(lines_out)


def main():
    st.set_page_config(page_title="LaTeX TOC to Text Converter", page_icon="📄")
    st.title("LaTeX TOC to Plain Text Converter")
    st.write("Upload a LaTeX `.toc` file to extract its table of contents as plain text.")

    uploaded_file = st.file_uploader("Choose a .toc file", type=["toc", "txt"])
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            st.error("Failed to decode file. Please ensure it's UTF-8 encoded.")
            return

        result = parse_toc(content)
        if result:
            st.subheader("Plain Text Output")
            st.text_area("Table of Contents", result, height=400)
            st.download_button("Download as .txt", data=result, file_name="toc.txt", mime="text/plain")
        else:
            st.warning("No contents found in the file.")


if __name__ == "__main__":
    main()
