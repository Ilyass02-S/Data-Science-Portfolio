import os
import json

from pandas import DataFrame
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def rows_to_json(df: DataFrame, path ="persistent/chatbot/data", file_prefix: str = "movies")-> None:
    """
    Converts the rows of a DataFrame into a single JSON file containing a list of JSON objects.

    This function iterates over every row in the provided DataFrame, converts each row
    to a dictionary, and writes all the dictionaries to a single JSON file as a list.
    The output file is named using the provided file prefix (e.g., "movie.json") and saved
    in the specified directory.

    Args:
        df (DataFrame): The pandas DataFrame containing the data to be exported.
        path (str, optional): The directory where the JSON file will be saved.
            Defaults to "data/json".
        file_prefix (str, optional): The prefix to use for naming the JSON file.
            Defaults to "movie".

    Returns:
        None

    Raises:
        IOError: If an error occurs while writing the JSON file.
    """
    os.makedirs(path, exist_ok=True)

    # Convert all rows to a list of dictionaries.
    rows = [row.to_dict() for _, row in df.iterrows()]
    filename = f"{path}/{file_prefix}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=4)


def metadata_func(record: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a JSON record, excluding the 'overview' key.

    Args:
        record (Dict[str, Any]): A single JSON object representing movie details.
        metadata (Dict[str, Any]): Default metadata.

    Returns:
        Dict[str, Any]: A dictionary containing all keys and values from the input
                        record except the 'overview' key.
    """
    return {key: value for key, value in record.items() if key != 'overview'}


def create_prompt_template() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    """You are a helpful AI assistant. You help the user to find suitable movies to watch. \
                    Give the suggestions based on the given context. \
                    If the context doesn't have a suitable movie apologize and say that you could not find a suitable \
                    movie. 
                    """
                )
            ),
            MessagesPlaceholder(variable_name="context"),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="input")
        ]
    )
