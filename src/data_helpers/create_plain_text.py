from src.paths import ekavica_path, ijekavica_path, DATA_DIR


def write_files(input_file, output_folder):
    output_folder.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as in_file:
        file = in_file.read()

    for text in file.split('newdoc')[1:]:
        doc_id = text.split('=')[1].split('\n')[0].strip()
        title = text.split('# title =')[1].split('\n')[0].strip()
        source = text.split('# source =')[1].split('\n')[0].strip()

        txt = f"# title = {title}\n# source = {source}\n"

        for sentence in text.split('# text =')[1:]:
            txt += sentence.split('\n')[0].strip() + '\n'

        with open(output_folder / f"{doc_id}.txt", 'w', encoding='utf-8', newline='\n') as out_file:
            out_file.write(txt)

if __name__ == "__main__":
    write_files(ekavica_path, DATA_DIR/"ekavica_txt")
    write_files(ijekavica_path, DATA_DIR/"ijekavica_txt")