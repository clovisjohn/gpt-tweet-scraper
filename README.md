# gpt-tweet-scraper
This script searches for tweets matching a list of queries, filter them according to a yes or no gpt query and converts the results to CSV format.
The model used is text-davinci-003

## Update 06/18/2023
You can now use the new [chat completion api](https://platform.openai.com/docs/guides/gpt/chat-completions-api). It unlocks recent models like gpt4

To use it, add the option --v2Model followed by the model you want to use.

Example
  ```bash
 python script.py --query-file queries.txt --output-file tweets.csv --max-results 10 --v2Model gpt-3.5-turbo   
  ```


## Requirements
- Python 3.6 or higher

- [dotenv](https://pypi.org/project/python-dotenv/)
- [openai](https://pypi.org/project/openai/)
- [snscrape](https://pypi.org/project/snscrape/)
- [pandas](https://pypi.org/project/pandas/)

## Configuration
In the env file,

- Set the `OPENAI_API_KEY` variable to your OpenAi API key.
- Set the `GPT_QUERY` variable to your desired GPT query.

## GPT-3 Query

The `GPT_QUERY` should be a valid GPT-3 query in the [Prompt Format](https://beta.openai.com/docs/api-reference/completions/create#prompt-format) specified in the OpenAI API documentation. It should be a question that can be answered with Yes or No.

Here are a few examples of prompts that you might use with this module:

- `"Is this tweet relevant to my interests?"`: This prompt could be used to filter tweets based on relevance to a certain topic or theme.
- `"Is this tweet appropriate for all audiences?"`: This prompt could be used to filter out tweets that might be inappropriate or offensive.
- `"Does this tweet contain useful information?"`: This prompt could be used to filter out tweets that might be spam or low-quality content.

Considering the second example the full prompt that will be submitted to gpt3 is :

```
Using the following text, answer the following question with Yes or No and provide an explanation

Text:
"""
tweet example
"""

Question: Is this tweet appropriate for all audiences?

Answer:
```

## Usage

To run the script, use the following command:

```bash
python script.py --query-file [query_file] --output-file [output_file]
```

## Options

    --max-results: The maximum number of results to return. Default is 10.
    --query-file: A file containing the queries to search for, one per line.
    --output-file: The file to write the results to. The file will be in CSV format.
 

## Example

  ```bash
  python script.py --query-file queries.txt --output-file tweets.csv --max-results 100
  ```
This will search for tweets matching the queries in queries.txt, starting from the most recent ones. The results will be written to tweets.csv in CSV format.


## Potential Enhancements
- Add the ability to specify the GPT-3 model.
- Add the ability to specify a gpt query for each tweet search query.
