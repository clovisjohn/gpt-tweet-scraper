import argparse
import datetime
import json
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened
from twarc_csv import CSVConverter

BEARER_TOKEN = ""
GPT_QUERY = ""

client = Twarc2(bearer_token=BEARER_TOKEN)

def chatGPT(text):
    """
    Check whether the given text meets some criteria for further processing.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if the text should be processed further, False otherwise.
    """
    #return True


def convert_to_csv(input_file, output_file):
    """
    Convert the given input file (in JSONL format) to CSV format.

    Args:
        input_file (str): The path to the input file.
        output_file (str): The path to the output file.
    """
    print("Converting to CSV...")
    with open(input_file, "r") as infile:
        with open(output_file, "w", encoding="utf-8") as outfile:
            converter = CSVConverter(infile, outfile)
            converter.process()
    print("Finished.")


def search_tweets(queries, start_time, end_time, max_results):
    """
    Search for tweets matching the given queries.

    Args:
        queries (List[str]): The list of queries to search for.
        start_time (datetime.datetime): The start time for the tweet search.
        end_time (datetime.datetime): The end time for the tweet search.
        max_results (int): The maximum number of results to return.

    Yields:
        dict: A tweet object.
    """

    for query in queries:
        print(f"Analyzing tweets from query {query}")
        search_results = client.search_recent(
            query=query, start_time=start_time, end_time=end_time, max_results=max_results
        )
        for page in search_results:
            for tweet in ensure_flattened(page):
                if chatGPT(tweet["text"]):
                    yield tweet

def main():
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start-time",
        type=lambda s: datetime.datetime.fromisoformat(s),
        default=None,
        help="start time for the tweet search (in ISO format)",
    )
    parser.add_argument(
        "--end-time",
        type=lambda s: datetime.datetime.fromisoformat(s),
        default=None,
        help="end time for the tweet search (in ISO format)",
    )
    parser.add_argument(
        "--max-results", type=int, default=10, help="maximum number of results to return"
    )
    parser.add_argument(
        "--query-file", type=argparse.FileType("r"), required=True, help="file containing the queries"
    )
    parser.add_argument(
        "--output-file", type=argparse.FileType("w"), required=True, help="output file for the tweets"
    )
    args = parser.parse_args()

    # Read the queries from the query file
    queries = args.query_file.readlines()

    
    # Search for tweets and write the results to the output file
    jsonl_file =  args.output_file.name.replace("csv", "jsonl")

    with open(jsonl_file, "w", encoding="utf-8") as f:
        for tweet in search_tweets(queries, args.start_time, args.end_time, args.max_results):
            json.dump(tweet, f)
            f.write("\n")

    convert_to_csv(jsonl_file, args.output_file.name)

if __name__ == "__main__":
    main()
