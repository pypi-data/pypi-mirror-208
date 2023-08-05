#!/usr/bin/env python
# similarity_ranker.py
import argparse
import glob
import json
import os

import torch
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer


def find_files(folder, extension):
    return glob.glob(f"{folder}/**/*{extension}", recursive=True)


def query_embeddings(query, embeddings_folder):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    query_embedding = model.encode(query)

    embeddings_files = find_files(embeddings_folder, '.pt')

    similarities = []
    for embed_file in embeddings_files:
        embedding = torch.load(embed_file)
        similarity = 1 - cosine(query_embedding, embedding)
        similarities.append((embed_file, similarity))

    return sorted(similarities, key=lambda x: x[1], reverse=True)


def save_ranking_to_json(prompt, ranking, txt_folder, output_file):
    txt_files = find_files(txt_folder, '.txt')

    top_ranking = ranking[:10]
    result = {
        'prompt': prompt,
        'ranking': []
    }

    for idx, (embed_file, similarity) in enumerate(top_ranking):
        txt_file = os.path.splitext(embed_file)[0] + '.txt'
        txt_file_path = [f for f in txt_files if os.path.basename(f) == os.path.basename(txt_file)][0]
        with open(txt_file_path, 'r') as f:
            content = f.read()

        result['ranking'].append({
            'rank': idx + 1,
            'similarity': f'{similarity * 100:.2f}%',
            'file': txt_file_path,
            'content': content
        })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    with open(output_file, 'r') as f:
        print(f.read())


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Find the most similar embeddings for a given query sentence using Hugging Face Transformers.')
    parser.add_argument('--prompt', type=str, required=True, help='Prompt sentence for finding similar embeddings.')
    parser.add_argument('--txt-folder', type=str, required=True, help='Folder containing the txt files.')
    parser.add_argument('--embeddings-folder', type=str, required=True, help='Folder containing the embeddings files.')
    parser.add_argument('--output-json', type=str, default='data/top_similarity.json',
                        help='Output JSON file containing the top 10 similar txt files (default: data/top_similarity.json)')
    return parser.parse_args()


def main():
    args = parse_arguments()
    ranking = query_embeddings(args.prompt, args.embeddings_folder)
    save_ranking_to_json(args.prompt, ranking, args.txt_folder, args.output_json)
    print(f'Top 10 similar txt files saved to {args.output_json}')


if __name__ == '__main__':
    main()
