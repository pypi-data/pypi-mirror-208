
# compact
file_type_to_endings = {
    'image': ['png', 'jpeg', 'jpg', 'gif', 'svg'],
    'video': ['mkv', 'mp4', 'mpeg'],
    'audio': ['mp3', 'aac', 'flac', 'm3u', 'm4b', 'wav'],
    'usenet': ['nzb'],
    'text': ['txt'],
    'scene': ['nfo'],
    'archive': ['rar', 'zip', '7z', 'tar'],
    'documents': ['pdf', 'docs'],
    'code': ['py', 'js', 'html', 'css'],
    'ebook': ['epub', 'mobi'],
    'meta': ['json', 'yaml', 'yml', 'xml']
}

# flat
ending_to_file_type = {}
for type, file_type_list in file_type_to_endings.items():
    for file_type in file_type_list:
        ending_to_file_type[file_type] = type
