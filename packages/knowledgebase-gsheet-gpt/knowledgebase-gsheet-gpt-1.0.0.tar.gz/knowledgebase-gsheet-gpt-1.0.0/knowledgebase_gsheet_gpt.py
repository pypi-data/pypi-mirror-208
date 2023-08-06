#!/usr/bin/env python
# knowledgebase_gsheet_gpt.py
import argparse
import os

import csv_embeddings_creator
import google_sheet_downloader
import openai_chat_thread
import similarity_ranker

DEFAULT_BEFORE_KNOWLEDGE_PROMPT = '\n-- reference following knowledge base content to answer the user question (answer as long as possible)\n'


def parse_arguments():
    parser = argparse.ArgumentParser(description='Knowledgebase GSheet GPT')
    parser.add_argument('--user', type=str, required=True, help='User email')
    parser.add_argument('--key-file', type=str, required=True, help='Google service account key JSON file path')
    parser.add_argument('--sheet-ids', type=str, required=True, help='Comma separated Google sheet IDs to download')
    parser.add_argument('--prompt', type=str, required=True, help='Prompt sentence for finding similar embeddings.')
    parser.add_argument('--before-question-prompt', type=str, default='\n-- the user question\n',
                        help='Text before the user question in the final prompt')
    parser.add_argument('--before-knowledge-prompt', type=str,
                        default=DEFAULT_BEFORE_KNOWLEDGE_PROMPT,
                        help='Text before the knowledge base content in the final prompt')
    parser.add_argument('--top-n', type=int, default=3,
                        help='Number of top similar knowledge base texts to include in the final prompt')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo',
                        help='gpt-3.5-turbo or gpt-4')
    return parser.parse_args()


def knowledgebase_gsheet_gpt(user, key_file, sheet_ids, prompt, before_question_prompt='\n-- the user question\n',
                             before_knowledge_prompt=DEFAULT_BEFORE_KNOWLEDGE_PROMPT,
                             top_n=3, model='gpt-3.5-turbo'):
    os.environ["TOKENIZERS_PARALLELISM"] = "true"

    user = user.lower().replace('@', '_').replace('.', '_')
    data_folder = f'./data/users/{user}'

    # Google Sheet Downloader
    google_sheet_downloader.download_google_sheets(
        key_file,
        sheet_ids,
        os.path.join(data_folder, 'google_sheet_downloader'),
        False
    )

    # CSV Embeddings Creator
    csv_embeddings_creator.create_embeddings(
        os.path.join(data_folder, 'google_sheet_downloader'),
        os.path.join(data_folder, 'csv_embeddings_creator', 'txt'),
        os.path.join(data_folder, 'csv_embeddings_creator', 'embeddings'),
        False
    )

    # Similarity Ranker
    ranking_result = similarity_ranker.query_embeddings(
        prompt,
        os.path.join(data_folder, 'csv_embeddings_creator', 'embeddings'),
        top_n
    )
    ranked_result = similarity_ranker.save_ranking_to_json(
        prompt,
        ranking_result,
        os.path.join(data_folder, 'csv_embeddings_creator', 'txt'),
        os.path.join(data_folder, 'similarity_ranker', 'similarity_ranker.json')
    )

    # Combine prompt with most similar sheet content
    knowledge_prompt = before_knowledge_prompt
    num_ranked_results = len(ranked_result['ranking'])
    top_n = min(top_n, num_ranked_results)

    for i in range(top_n):
        knowledge_prompt += f"{ranked_result['ranking'][i]['content']}"
        knowledge_prompt += '\n\n'

    knowledge_prompt += before_question_prompt
    knowledge_prompt += f"{prompt}\n"

    # print('knowledgebase_gsheet_gpt.py, knowledge_prompt:\n', knowledge_prompt)
    response_queue = openai_chat_thread.openai_chat_thread_taiwan(prompt=knowledge_prompt, model=model)
    return response_queue


def main():
    arg = parse_arguments()
    response_stream = knowledgebase_gsheet_gpt(arg.user,
                                               arg.key_file,
                                               arg.sheet_ids,
                                               arg.prompt,
                                               arg.before_question_prompt,
                                               arg.before_knowledge_prompt,
                                               arg.top_n,
                                               arg.model
                                               )
    while True:
        response = response_stream.get()
        if response is None:
            break
        print(response, end="", flush=True)


if __name__ == '__main__':
    main()
