import re
import streamlit as st

def parse_toc(content: str) -> str:
    """
    Parse LaTeX .toc content and return a plain-text representation.
    This handles nested braces by matching braces manually for each argument.
    """
    output_lines = []

    line_regex = re.compile(r'\\contentsline \{(.*?)\}\{(.*?)\}\{(.*?)\}')
    
    numberline_regex = re.compile(r'\\numberline \{(.*?)\}(.*)')

    for line in toc_content.strip().split('\n'):
        if not line.startswith('\\contentsline'):
            continue

        match = line_regex.match(line)
        if match:
            level, title_raw, page = match.groups()

            indent = ""
            if level == 'subsection':
                indent = "  "
            elif level == 'subsubsection':
                indent = "    "

            number_match = numberline_regex.match(title_raw)
            if number_match:
                number, text = number_match.groups()
                full_title = f"{number} {text.strip()}"
            else:
                full_title = title_raw.strip()
            
            output_lines.append(f"{indent}{full_title}\t{page}")

    return "\n".join(output_lines)


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
