import os
import dotenv
import argparse
import time
import openai
import snscrape.modules.twitter as sntwitter
import pandas as pd


# Load environment variables from a .env file
dotenv.load_dotenv()

# Get the OpenAI API key from the environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Get the GPT-3 query from the environment variables
GPT_QUERY =  os.environ.get("GPT_QUERY")

# Set the maximum number of prompts per request
MAX_PROMPTS_PER_REQUEST = 20

# Calculate the maximum number of tokens per tweet
MAX_TOKEN_PER_TWEET = 280 // 4

# Set the token limit per minute
TOKEN_LIMIT_PER_MINUTE = 120000

# Set the rate limit per minute
RATE_LIMIT_PER_MINUTE = 20

# Calculate the delay between requests
DELAY = 60.0 / RATE_LIMIT_PER_MINUTE

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

FULL_PROMPT = """Using the following text, answer the following question with Yes or No and provide an explanation

Text:
\"""
{tweet}
\"""

Question: {gpt_Query}

Answer: """

FULL_PROMPT = FULL_PROMPT.format(tweet="{tweet}", gpt_Query=GPT_QUERY)

# Calculate the size of the FULL_PROMPT
FULL_PROMPT_SIZE = len(FULL_PROMPT) // 4



def gpt3_batch_size(texts):
    """
    Calculate the maximum number of texts that can be included in a single request to the GPT-3 API.

    Args:
        texts (List[str]): The texts to be included in the request.

    Returns:
        int: The maximum number of texts that can be included in a single request.
    """
    available_tokens = TOKEN_LIMIT_PER_MINUTE
    total_tokens = sum((len(text) // 4) for text in texts)
    return len(texts) if total_tokens <= available_tokens else max(1, available_tokens // (MAX_TOKEN_PER_TWEET + FULL_PROMPT_SIZE))


def gpt_check(texts):
    """
    Check whether the given texts meet some criteria for further processing.

    Args:
        texts (List[str]): The texts to check.

    Returns:
        List[bool,string]: A list of [booleans,string] indicating whether each text should be processed further and the response from gpt3.
    """

    # Initialize an empty list to store the results
    results = []
    
    # Format the prompts with the GPT_QUERY and the current texts
    prompts = [FULL_PROMPT.format(tweet=text) for text in texts]
    
    #print(prompts)
    #return False;
    # Initialize a counter variable to keep track of the current index
    i = 0

    # Calculate the maximum number of texts that can be included in a single request
    step = gpt3_batch_size(prompts)
    
    # Limit the number of texts to the maximum number of prompts per request
    step = min(step, MAX_PROMPTS_PER_REQUEST)

    # Loop through the texts
    while i < len(prompts):
        
        # Get a batch of prompts to send to the GPT-3 API
        batch = prompts[i:i + step]

        # Send the prompts to the GPT-3 API and get the response
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=batch,
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
        except openai.error.RateLimitError:
            print("Rate limit hit, will retry in 1 min")
            time.sleep(61)
            continue

        # Initialize a list to store the lowercase completions
        temp = [""] * len(prompts)
        
        # Iterate through the choices in the response
        for choice in response.choices:
            # Store the lowercase completion in the temp list
            temp[choice.index] = choice.text.lower()

        # Append a boolean indicating whether "yes" is in the completion to the results list
        results.extend([
            ["yes" in r,r] for r in temp
        ])
        
        # Increment the counter variable by the step size
        i += step

        # Delay the next iteration to avoid exceeding the rate limit
        time.sleep(DELAY)

    # Return the results
    return results



def convert_to_csv(input_list, output_file):
    """
    Convert the given input file (in JSONL format) to CSV format.

    Args:
        input_list (str): The list of dict to write as csv.
        output_file (str): The path to the output file.
    """
    df = pd.DataFrame(input_list)
    df.to_csv(output_file, index=False, header=True)


def search_tweets(queries, max_results):
    """
    Search for tweets matching the given queries and yield the tweets that meet certain criteria.

    Args:
        queries (List[str]): The list of queries to search for.
        max_results (int): The maximum number of results to return for each query.

    Yields:
        dict: A tweet object.
    """
    
    # Loop through the queries
    for query in queries:
        # Initialize a list to store the tweets
        tweets = []
        
        # Print a message indicating the current query
        print(f"Analyzing tweets from query {query}")
        
        # Loop through the tweets from the query
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            # Break the loop if the maximum number of results has been reached
            if i > max_results:
                break
            
            # Convert the tweet object to a dictionary and add the user name and query to the dictionary
            temp = vars(tweet)
            temp.update({"user_name": tweet.user.username, "twitter_search_query": query})
            
            # Add the dictionary to the tweets list
            tweets.append(temp)
        
        # Check the tweets with the GPT-3 API
        keep_list = gpt_check([tweet["rawContent"] for tweet in tweets])
            
        # Loop through the tweets and the keep list
        for tweet, keep in zip(tweets, keep_list):
            # If the tweet should be kept, yield it
            if keep[0]:
                tweet["gpt_answer"] = keep[1].strip()
                yield tweet

def main():
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-results", type=int, default=10, help="maximum number of results to return")
    parser.add_argument("--query-file", type=argparse.FileType("r"), required=True, help="file containing the queries")
    parser.add_argument("--output-file", type=argparse.FileType("w"), required=True, help="output file for the tweets")
    args = parser.parse_args()

    # Read the queries from the query file
    queries = args.query_file.readlines()

    
    # Search for tweets and write the results to the output file

    valid_tweets = []

    row_count = 0
    for tweet in search_tweets(queries, args.max_results):
         valid_tweets.append(tweet)
         if row_count % 50 == 0:
            convert_to_csv(valid_tweets, args.output_file.name)

    convert_to_csv(valid_tweets, args.output_file.name)
    

if __name__ == "__main__":
    main()


    