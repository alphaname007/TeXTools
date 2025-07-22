import re
import streamlit as st


def parse_toc(content: str) -> str:
    """
    Parse LaTeX .toc content and return a plain-text representation.
    This handles nested braces by matching braces manually for each argument.
    """
    lines_out = []
    indent_map = {'chapter': 0, 'section': 0, 'subsection': 1, 'subsubsection': 2}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line.startswith(r'\\contentsline'):
            continue
        # Extract the first three brace-delimited arguments robustly
        args = []
        idx = line.find('{', line.find('\\contentsline') + len('\\contentsline'))
        while len(args) < 3 and idx != -1:
            brace_level = 0
            start = None
            for j in range(idx, len(line)):
                if line[j] == '{':
                    if brace_level == 0:
                        start = j + 1
                    brace_level += 1
                elif line[j] == '}':
                    brace_level -= 1
                    if brace_level == 0 and start is not None:
                        end = j
                        break
            else:
                break  # unmatched braces
            args.append(line[start:end])
            idx = line.find('{', end + 1)
        if len(args) < 3:
            continue
        entry_type, raw_title, page = args
        # Clean up title, handle \numberline
        num_match = re.search(r'\\numberline\s*{([^}]*)}', raw_title)
        title_text = re.sub(r'\\numberline\s*{[^}]*}', '', raw_title).strip()
        if num_match:
            title = f"{num_match.group(1)} {title_text}"
        else:
            title = title_text
        # Indentation based on type
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
