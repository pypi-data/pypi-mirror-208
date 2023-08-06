import os
import re

RE_REFERENCE = r'(\[@(.+?)\])'


def contains_letter(line):
    for c in line:
        if c.isalpha():
            return True
    return False


def find_token_end(lines, start):
    end = 0

    for i, line in enumerate(lines[start:]):
        if i == len(lines) - 1 - start:
            break

        if len(line) == 0 or line[0] == '\n' or (len(line) == 1 and line[0] == '\n') or line == '':
            continue

        if line[0] == ' ' and contains_letter(line):
            end = i

        if i != 0 and line[0].isalpha():
            break

    return start + end + 1


def find_token_body(lines, token):
    re_class = re.compile(r"class\s+" + re.escape(token) + r"\b(\((?:[\w\s,]+)?\))?.*?(?=class|\Z)", re.DOTALL)
    re_func = re.compile(f'.+def\s+({token})')
    re_var = re.compile(f'^%s[,\s]*=.+({token})')

    for i, line in enumerate(lines):
        if not (re_class.match(line) or re_func.match(line) or re_var.match(line)):
            continue

        end = find_token_end(lines, i)
        body = ''.join(lines[i:end]).strip()
        return body, i, end
    return '', -1, -1


def find_docstring_in_body(body):
    re_docstring = re.compile(r'("""(.+?)""")|(\'\'\'(.+?)\'\'\')', re.DOTALL)
    match_obj = re_docstring.search(body)
    if match_obj:
        docstring = match_obj.group(2) or match_obj.group(4)
        return docstring.strip()
    return ''


def remove_whitespaces(docstring):
    return '\n'.join([line.strip() for line in docstring.split('\n')])


def get_docstring(filepath, name):
    with open(filepath) as f:
        lines = f.readlines()

    tokens = name.split('.')

    while tokens:
        token = tokens.pop(0)
        body, start, end = find_token_body(lines, token)
        lines = body.split('\n')

    docstring = find_docstring_in_body(body)
    references = re.findall(RE_REFERENCE, docstring)
    if not references:
        return docstring

    for ref in references:
        if '#' in ref[1]:
            mod, name = ref[1].split('#')
            docstring = docstring.replace(ref[0], get_docstring(mod, name))
        else:
            if ref[1].startswith('.'):
                name = token + ref[1]
            else:
                name = ref[1]
            docstring = docstring.replace(ref[0], get_docstring(filepath, name))
    return docstring


class DocGenerator:
    def __init__(self, docs_folder, compiled_docs_folder):
        self.docs_folder = docs_folder
        self.compiled_docs_folder = compiled_docs_folder

    def parse_file(self, filepath):
        compiled_markdown = ''
        cwd = os.getcwd()
        print('cwd')
        base = filepath.replace(self.docs_folder, '')

        with open(filepath) as f:
            markdown = f.readlines()

        for line in markdown:
            matches = re.findall(RE_REFERENCE, line)
            if not matches:
                compiled_markdown += line
                continue

            for match in matches:
                mod, name = match[1].split('#')
                docstring = get_docstring(mod, name)
                docstring = remove_whitespaces(docstring)
                line = line.replace(match[0], docstring)
            compiled_markdown += line

        with open(f'{cwd}/{self.compiled_docs_folder}{base}', 'w') as f:
            f.write(compiled_markdown)

    def create_folder_structure(self):
        cwd = os.getcwd()
        os.makedirs(f'{cwd}/{self.compiled_docs_folder}', exist_ok=True)

        for root, dirs, files in os.walk(self.docs_folder):
            for dir in dirs:
                path = f'{cwd}/{self.compiled_docs_folder}/{root.replace(self.docs_folder, "")}/{dir}'
                os.makedirs(path, exist_ok=True)

    def generate(self):
        self.create_folder_structure()

        for root, dirs, files in os.walk(self.docs_folder):
            for file in files:
                if file.endswith('.md'):
                    self.parse_file(os.path.join(root, file))
                else:
                    os.system(f'cp {os.path.join(root, file)} {self.compiled_docs_folder}/{root.replace(self.docs_folder, "")}')


if __name__ == '__main__':
    with open('docs/index.md') as f:
        markdown = f.readlines()

    # markdown = [
    #     '[@code/places/models.py#Place.get_coordinates]'
    # ]

    compiled_markdown = ''

    for line in markdown:
        matches = re.findall(RE_REFERENCE, line)
        if not matches:
            compiled_markdown += line
            continue

        for match in matches:
            mod, name = match[1].split('#')
            docstring = get_docstring(mod, name)
            docstring = remove_whitespaces(docstring)
            line = line.replace(match[0], docstring)
        compiled_markdown += line

    with open('docs_compiled/index.md', 'w') as f:
        f.write(compiled_markdown)
