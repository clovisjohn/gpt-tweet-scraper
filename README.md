# gpt-tweet-scraper
This script searches for tweets matching a list of queries, filter them according to a yes or no gpt query and converts the results to CSV format.

## Requirements

- `twarc`: A command line utility and Python library for accessing the Twitter API.
- `twarc_csv`: A library for converting JSONL data to CSV format.

## Configuration

- Set the `BEARER_TOKEN` variable to your Twitter API bearer token.
- Set the `GPT_QUERY` variable to your desired GPT query.

## Usage

To run the script, use the following command:

```bash
python script.py --query-file [query_file] --output-file [output_file]
```

## Options

    --start-time: The start time for the tweet search, in ISO format. If not provided, the search will start from the earliest possible time.
    --end-time: The end time for the tweet search, in ISO format. If not provided, the search will end at the current time.
    --max-results: The maximum number of results to return. Default is 10.
    --query-file: A file containing the queries to search for, one per line.
    --output-file: The file to write the results to. The file will be in CSV format.
    
  ## Example
  ```bash
  python script.py --query-file queries.txt --output-file tweets.csv --start-time "2022-12-13"--end-time "2022-12-18" --max-results 100
  ```
This will search for tweets matching the queries in queries.txt, starting from the earliest possible time and ending at the current time, and return a maximum of 100 results. The results will be written to tweets.csv in CSV format.


## Functions
Here is a more detailed description of each of the functions in the code:

### `chatGPT(text)`

This function checks whether the given text meets some criteria for further processing.

#### Parameters

- `text` (_str_): The text to check.

#### Returns

- (_bool_): True if the text should be processed further, False otherwise.

### `convert_to_csv(input_file, output_file)`

This function converts the given input file (in JSONL format) to CSV format.

#### Parameters

- `input_file` (_str_): The path to the input file.
- `output_file` (_str_): The path to the output file.

### `search_tweets(queries, start_time, end_time, max_results)`

This function searches for tweets matching the given queries.

#### Parameters

- `queries` (_List[str]_): The list of queries to search for.
- `start_time` (_datetime.datetime_): The start time for the tweet search.
- `end_time` (_datetime.datetime_): The end time for the tweet search.
- `max_results` (_int_): The maximum number of results to return.

#### Yields

- (_dict_): A tweet object.

### `main()`

This function is the entry point for the script. It parses the command-line arguments, searches for tweets matching the given queries, and writes the results to the output file.


## Note

The chatGPT function is currently commented out
