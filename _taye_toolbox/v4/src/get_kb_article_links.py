import re

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def trim_content(content):
    # start_str = '<div class="col col--main has--side qa-div-main">'
    start_str = '<div data-preact="category/CategoryListWithTopics"'
    end_str = '<div data-preact="powered-by-insided/index" class=""'

    start_index = content.find(start_str)
    end_index = content.find(end_str)
    if start_index != -1 and end_index != -1:
        content = content[start_index:end_index + len(end_str)]
    else:
        content = 'The specified strings were not found in the file.'
    return content

def replace_content(content):
    content = content.replace('<a class="topic-curation__item-link link" href="', '\n<LINK>')
    content = content.replace('"></a>', '</LINK>')

    content = content.replace('<h4 class="topic-curation__title thread-list-block__title">', '<TITLE>')
    content = content.replace('</h4>', '</TITLE>')

    content = content.replace('<div class="default-avatar avatar-variant-0">S</div></a>', '')
    content = content.replace('</TITLE>\n\n\n</LINK>\n\n\n<LINK>', '</TITLE>\n\n<LINK>')
    return content

def trim_pattern(content, _pattern):
    pattern = _pattern
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content

def save_content(content, filepath):
    new_file_path = filepath
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(content)

def make_csv(content):
    """Get the data from the content and make a csv file."""
    content = content.replace("<LINK>", "")
    content = content.replace("</LINK>", "")
    content = content.replace("<TITLE>", ";") # delimited with semi-colon due to commas in the titles
    content = content.replace("</TITLE>", "")
    content = content.replace('"<div class="default-avatar avatar-variant-9">G</div></a>"', "")
    content = content.replace('<div class="default-avatar avatar-variant-9">G</div></a>', "")
    return content

def save_csv(content, filepath):
    with open(filepath, 'w+', encoding='utf-8') as file: # "a+ MEANS append, w+ MEANS create/overwrite"
        file.write(content)

def main():
    input_path = '__raw_for_parse.txt'
    output_path = '__output.txt'
    _csv = '_links.csv'

    content = read_file(input_path)

    t_content = trim_content(content)
    r_content = replace_content(t_content)
    save_content(r_content, output_path)

    trim_content_1 = trim_pattern(r_content, _pattern=r'<div class="topic-curation__item-icon">.*?<div class="topic-curation__item-body">')
    save_content(trim_content_1, output_path)

    trim_content_2 = trim_pattern(trim_content_1, _pattern=r'</div></div><a class="topic-curation__item-type-link".*?</li><li class="topic-curation__item">')
    save_content(trim_content_2, output_path)

    trim_content_3 = trim_pattern(trim_content_2, _pattern=r'<div class="topic-curation__item-type">.*?el="noreferrer">')
    save_content(trim_content_3, output_path)

    trim_content_4 = trim_pattern(trim_content_3, _pattern=r'<img class="".*?.png')
    save_content(trim_content_4, output_path)

    _csv_content = make_csv(trim_content_4)
    save_csv(_csv_content, _csv)

    # r_content = replace_content(t_content)
    # save_csv(r_content, output_path)

    print("DONE!")

if __name__ == '__main__':
    main()

