#!/usr/bin/env python
# csv_embeddings_creator.py
import argparse
import csv
import glob
import os

import torch
from sentence_transformers import SentenceTransformer


def create_embeddings(input_folder, output_txt_folder, output_embeddings_folder, force=False):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    os.makedirs(output_txt_folder, exist_ok=True)
    os.makedirs(output_embeddings_folder, exist_ok=True)

    csv_files = glob.glob(os.path.join(input_folder, '**/*.csv'), recursive=True)

    for csv_file in csv_files:
        file_base_name = os.path.splitext(os.path.basename(csv_file))[0]
        existing_txt_files = glob.glob(os.path.join(output_txt_folder, f"{file_base_name}_*.txt"))

        if not force and existing_txt_files:
            continue

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header

            for idx, row in enumerate(reader):
                folder_txt = os.path.join(output_txt_folder, f"{file_base_name}")
                os.makedirs(folder_txt, exist_ok=True)
                txt_file = os.path.join(folder_txt, f"{file_base_name}_{idx + 1}.txt")
                with open(txt_file, 'w', encoding='utf-8') as txt_f:
                    txt_f.write('"' + '","'.join(row) + '"')

                embeddings = model.encode('"' + '","'.join(row) + '"')
                folder_embeddings = os.path.join(output_embeddings_folder, f"{file_base_name}")
                os.makedirs(folder_embeddings, exist_ok=True)
                embeddings_file = os.path.join(folder_embeddings, f"{file_base_name}_{idx + 1}.pt")
                torch.save(embeddings, embeddings_file)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create embeddings for text files using Hugging Face Transformers.')
    parser.add_argument('--input-folder', type=str, required=True,
                        help='Input folder containing CSV files')
    parser.add_argument('--output-txt-folder', type=str, required=True,
                        help='Output folder for the txt files')
    parser.add_argument('--embeddings-folder', type=str, required=True,
                        help='Output folder for the embeddings')
    parser.add_argument('--force', action='store_true',
                        help='Force to recreate embeddings even if they already exist')
    return parser.parse_args()


def main():
    args = parse_arguments()
    create_embeddings(args.input_folder, args.output_txt_folder, args.embeddings_folder, args.force)


if __name__ == '__main__':
    main()
