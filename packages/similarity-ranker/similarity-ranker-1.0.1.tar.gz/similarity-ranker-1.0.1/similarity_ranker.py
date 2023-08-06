#!/usr/bin/env python
import argparse
import glob
import heapq
import json
import os

import torch
from scipy.spatial.distance import cosine
# 1.2s 慢速瓶頸
from sentence_transformers import SentenceTransformer


def find_files(folder, extension):
    return glob.glob(f"{folder}/**/*{extension}", recursive=True)


def query_embeddings(query, embeddings_folder, top_n):
    # 1.5s 慢速瓶頸
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    query_embedding = model.encode(query)
    embeddings_files = find_files(embeddings_folder, '.pt')
    max_heap = []
    for embed_file in embeddings_files:
        embedding = torch.load(embed_file)
        similarity = 1 - cosine(query_embedding, embedding)
        if len(max_heap) < top_n:
            heapq.heappush(max_heap, (similarity, embed_file))
        elif max_heap[0][0] < similarity:
            heapq.heappop(max_heap)
            heapq.heappush(max_heap, (similarity, embed_file))
    ranking = [(embed_file, similarity) for similarity, embed_file in sorted(max_heap, reverse=True)]
    return ranking


def save_ranking_to_json(prompt, ranking, txt_folder, output_file):
    txt_files = find_files(txt_folder, '.txt')

    result = {
        'prompt': prompt,
        'ranking': []
    }

    for idx, (embed_file, similarity) in enumerate(ranking):
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
    print(result)
    return result


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Find the most similar embeddings for a given query sentence using Hugging Face Transformers.')
    parser.add_argument('--prompt', type=str, required=True, help='Prompt sentence for finding similar embeddings.')
    parser.add_argument('--txt-folder', type=str, required=True, help='Folder containing the txt files.')
    parser.add_argument('--embeddings-folder', type=str, required=True, help='Folder containing the embeddings files.')
    parser.add_argument('--output-json', type=str, default='data/top_similarity.json',
                        help='Output JSON file containing the top 10 similar txt files (default: data/top_similarity.json)')
    parser.add_argument('--top-n', type=int, default=3,
                        help='Top N results to maintain in the priority queue (default: 10)')
    return parser.parse_args()


def main():
    args = parse_arguments()
    ranking = query_embeddings(args.prompt, args.embeddings_folder, args.top_n)
    save_ranking_to_json(args.prompt, ranking, args.txt_folder, args.output_json)
    print(f'Top similar txt files saved to {args.output_json}')


if __name__ == '__main__':
    main()
