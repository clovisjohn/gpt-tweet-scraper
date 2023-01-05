import argparse
import datetime
import json
import openai
import time
import snscrape.modules.twitter as sntwitter
import pandas as pd

OAI_API_KEY = ""
GPT_QUERY = "is the following text related to cryptocurrencies or blockchain, reply with yes or no?. "

MAX_TOKEN_PER_TWEET = 280//4

TOKEN_LIMIT_PER_MINUTE = 120000

RATE_LIMIT_PER_MINUTE = 20
DELAY = 60.0 / RATE_LIMIT_PER_MINUTE

MAX_PROMPTS_PER_REQUEST = 20

openai.api_key = OAI_API_KEY

def gpt3_batch_size(texts, gpt3_query_size):
    """
    Calculate the maximum number of texts that can be included in a single request to the GPT-3 API.

    Args:
        texts (List[str]): The texts to be included in the request.
        gpt3_query_size (int): The size of the GPT-3 query.

    Returns:
        int: The maximum number of texts that can be included in a single request.
    """
    available_tokens = TOKEN_LIMIT_PER_MINUTE
    total_tokens = sum( (len(text) // 4)+gpt3_query_size for text in texts)
    return len(texts) if total_tokens <= available_tokens else max(1, available_tokens // (MAX_TOKEN_PER_TWEET + gpt3_query_size))


def gptCheck(texts):
    """
    Check whether the given texts meet some criteria for further processing.

    Args:
        texts (List[str]): The texts to check.

    Returns:
        List[bool]: A list of booleans indicating whether each text should be processed further.
    """
    gpt3_query_size = len(GPT_QUERY)// 4
    results = []
    i = 0
    while i < len(texts):
        step = gpt3_batch_size(texts[i:], gpt3_query_size)
        if step > MAX_PROMPTS_PER_REQUEST:
            step = MAX_PROMPTS_PER_REQUEST
        prompts = [GPT_QUERY + " \"{textQ}\"".format(textQ=text) for text in texts[i:i+step]]

        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=prompts,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # match completions to prompts by index
        temp = [""] * len(prompts)
        for choice in response.choices:
            #print(choice.text.lower())
            temp[choice.index] = choice.text.lower()

        #print(temp)
        results.extend([
            "yes" in r for r in temp
        ])
        i += step

        time.sleep(DELAY)

    return results



def convert_to_csv(input_list, output_file):
    """
    Convert the given input file (in JSONL format) to CSV format.

    Args:
        input_file (str): The path to the input file.
        output_file (str): The path to the output file.
    """
    df = pd.DataFrame(input_list)
    df.to_csv(output_file, index=False, header=True)


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
        tweets = []
        print(f"Analyzing tweets from query {query}")
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i>max_results:
                break

            temp = vars(tweet)
            temp.update({"user_name": tweet.user.username,"query" : query })

            tweets.append(temp)

        try:
            keep_list = gptCheck([tweet["content"] for tweet in tweets])
        except openai.error.RateLimitError :
            print("Rate limit hit, will retry in 1 min")
            time.sleep(61)
            tokens_used=0
            keep_list = gptCheck([tweet["content"] for tweet in tweets])

        for tweet, keep in zip(tweets, keep_list):
            if keep:
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

    valid_tweets = []

    row_count=0
    for tweet in search_tweets(queries, args.start_time, args.end_time, args.max_results):
         valid_tweets.append(tweet)
         if(row_count%50==0):
            convert_to_csv(valid_tweets, args.output_file.name)

    convert_to_csv(valid_tweets, args.output_file.name)
    

if __name__ == "__main__":
    main()