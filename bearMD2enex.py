import os
import datetime
from xml.sax.saxutils import escape

# 文件目录
source_dir = 'source'
output_file = 'output.enex'


# 获取当前时间的字符串格式
def get_current_time_str():
    return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


# 获取文件的创建时间和更新时间
def get_file_times(file_path):
    try:
        # 获取文件的创建时间和最后修改时间
        created_timestamp = os.path.getctime(file_path)
        modified_timestamp = os.path.getmtime(file_path)

        # 将时间戳转换为 UTC 时间格式
        created_time = datetime.datetime.utcfromtimestamp(created_timestamp).strftime('%Y%m%dT%H%M%SZ')
        modified_time = datetime.datetime.utcfromtimestamp(modified_timestamp).strftime('%Y%m%dT%H%M%SZ')

        return created_time, modified_time
    except Exception as e:
        print(f"Error retrieving file times for {file_path}: {e}")
        return get_current_time_str(), get_current_time_str()


# 将Markdown内容转换为ENML内容，每行用 <div> 标签包裹
def markdown_to_enml(content):
    lines = content.splitlines()
    # 将每一行包裹在 <div> 标签中
    return ''.join(f'<div>{escape(line)}</div>' for line in lines)


# 读取文件内容和提取信息
def extract_note_info(md_file_path):
    try:
        with open(md_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            # 文件为空
            return "Untitled", get_current_time_str(), get_current_time_str(), ""

        # 提取标题
        title_line = lines[0].strip()
        title = title_line[2:].strip() if title_line.startswith('# ') else title_line  # 去掉标题前的 '# '

        # 从文件属性获取创建时间和更新时间
        created_time, updated_time = get_file_times(md_file_path)

        # 将更新时间设定为创建时间
        created_time = updated_time

        # 将 Markdown 内容转换为 ENML
        content = markdown_to_enml(''.join(lines[1:]).strip() if len(lines) > 1 else "")

        return title, created_time, updated_time, content

    except Exception as e:
        # 只在遇到错误时打印文件名和错误信息
        print(f"Error processing file {md_file_path}: {e}")
        return None, None, None, None


# 生成enex文件内容
def generate_enex_file(md_files, output_path):
    export_date = get_current_time_str()
    notes = []

    for md_file in md_files:
        title, created, updated, content = extract_note_info(md_file)

        if title is None:  # 如果提取信息失败，则跳过该文件
            continue

        note = f'''
  <note>
    <title>{escape(title)}</title>
    <created>{created}</created>
    <updated>{updated}</updated>
    <note-attributes>
      <author>Automatically Generated</author>
    </note-attributes>
    <content>
      <![CDATA[<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
  {content}
</en-note>
      ]]>
    </content>
  </note>
'''
        notes.append(note)

    enex_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export4.dtd">
<en-export export-date="{export_date}" application="Evernote" version="10.101.4">
{''.join(notes)}
</en-export>'''

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(enex_content)


# 获取所有.md文件
md_files = [os.path.join(source_dir, f) for f in os.listdir(source_dir) if f.endswith('.md')]

# 生成enex文件
generate_enex_file(md_files, output_file)
print(f'ENEX file has been generated: {output_file}')