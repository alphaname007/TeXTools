import re
import streamlit as st


def parse_toc(content: str) -> str:
    """
    Parse LaTeX .toc content and return a plain-text representation.
    Supports nested braces and extracts numbering from \numberline commands.
    """
    indent_map = {'section': 0, 'subsection': 1, 'subsubsection': 2}

    def extract_group(s: str, start: int):
        # Extract text inside matching braces starting at s[start] == '{'
        if s[start] != '{':
            raise ValueError("Expected '{' at position {}".format(start))
        depth = 0
        for i in range(start, len(s)):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    return s[start+1:i], i + 1
        raise ValueError("No matching '}' found")

    lines_out = []
    for line in content.splitlines():
        l = line.strip()
        if not l.startswith(r'\\contentsline'):
            continue
        try:
            # Parse the four brace groups: type, raw_title, page, label
            pos = l.find('{')
            entry_type, pos = extract_group(l, pos)
            # Skip to next group
            while pos < len(l) and l[pos].isspace():
                pos += 1
            raw_title, pos = extract_group(l, pos)
            while pos < len(l) and l[pos].isspace():
                pos += 1
            page, pos = extract_group(l, pos)
        except Exception:
            continue

        # Handle \numberline if present
        num_match = re.match(r'\\numberline\s*{(?P<num>[^}]+)}\s*(?P<title>.*)', raw_title)
        if num_match:
            title_text = num_match.group('title').strip()
            title = f"{num_match.group('num')} {title_text}"
        else:
            title = raw_title.strip()

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
