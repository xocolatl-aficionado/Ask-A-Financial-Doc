from script import load, run_query
import os
import pickle
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
import matplotlib.pyplot as plt
import json
import re
import hashlib
import time as time

def save_to_json_file(data, metric_name, folder_path="./data"):
    """
    Saves the parsed data into a JSON file with a metric name prefix and versioning.
    :param data: List of dictionaries to save.
    :param metric_name: Name of the metric to include in the file name.
    :param folder_path: Path to the folder where JSON files will be stored.
    :return: None
    """
    try:
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Get existing files with the same metric name in the folder
        existing_files = [f for f in os.listdir(folder_path) if f.startswith(metric_name) and f.endswith(".json")]

        # Extract version numbers from existing files
        version_numbers = []
        for file in existing_files:
            match = re.search(rf"{metric_name}_v(\d+).json", file)
            if match:
                version_numbers.append(int(match.group(1)))

        # Determine the next version number
        next_version = max(version_numbers, default=0) + 1

        # Construct the file name with versioning
        file_name = f"{metric_name}_v{next_version}.json"

        # Full file path
        file_path = os.path.join(folder_path, file_name)

        # Write the data to the JSON file
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Data successfully saved to {file_path}")

    except Exception as e:
        raise Exception(f"Error saving data to JSON file: {e}")
    
def plot_test_results(parsed_results):
    """
    Plot test case results as a bar chart.
    :param parsed_results: List of dictionaries containing test case names and metrics.
    """
    # Extract data for plotting
    test_names = [result["test_name"] for result in parsed_results]
    scores = [result["metrics"][0]["score"] if result["metrics"] else 0 for result in parsed_results]
    success_flags = [result["success"] for result in parsed_results]

    # Color bars based on success or failure
    bar_colors = ["green" if success else "red" for success in success_flags]

    # Create the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(test_names, scores, color=bar_colors, alpha=0.8)

    # Add labels to bars
    for bar, score in zip(bars, scores):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{score:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="black"
        )

    # Add chart details
    plt.title("Test Case Scores", fontsize=16)
    plt.xlabel("Test Cases", fontsize=12)
    plt.ylabel("Score", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 1.1)  # Assuming scores are normalized between 0 and 1
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()

def parse_test_results(evaluation_result):
    """
    Parse EvaluationResult to extract details from test_results.
    :param evaluation_result: An instance of EvaluationResult containing test_results.
    :return: A list of parsed results in dictionary format.
    """
    parsed_results = []

    for test in evaluation_result.test_results:
        test_data = {
            "test_name": test.name,
            "success": test.success,
            "input_query": test.input,
            "actual_output": test.actual_output,
            "expected_output": test.expected_output,
            "metrics": []
        }

        # Extract metrics data
        if test.metrics_data:
            for metric in test.metrics_data:
                metric_data = {
                    "metric_name": metric.name,
                    "threshold": metric.threshold,
                    "success": metric.success,
                    "score": metric.score,
                    "reason": metric.reason,
                    "evaluation_model": metric.evaluation_model,
                    "evaluation_cost": metric.evaluation_cost,
                    "verbose_logs": metric.verbose_logs
                }
                test_data["metrics"].append(metric_data)

        parsed_results.append(test_data)

    return parsed_results

def generate_query_id(query, document_choice):
    """
    Generate a unique query ID based on the query and document name.
    :param query: The query string.
    :param document_choice: The document name used for query.
    :return: A unique query ID string.
    """
    unique_str = f"{document_choice}:{query}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def append_to_json_file(new_data, file_path):
    """
    Appends new data to an existing JSON file or creates the file if it doesn't exist.
    :param new_data: List of new data dictionaries to append.
    :param file_path: Path to the JSON file.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Load existing data
        with open(file_path, "r") as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = []  # If the file is empty or corrupted, start fresh
    else:
        existing_data = []

    # Append the new data
    existing_data.append(new_data)

    # Write back to the JSON file
    with open(file_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)

    print(f"Data appended to {file_path}")
    
tests = {}
def runEvaluation(metric_name: str):
    results = []
    
    """
    Run evaluation with the specified metric.
    :param metric_name: Name of the metric to use (e.g., 'AnswerRelevancyMetric' or 'FaithfulnessMetric').
    """
    # Map metric names to classes
    metric_mapping = {
        "AnswerRelevancyMetric": lambda: AnswerRelevancyMetric(model="gpt-4o-mini", include_reason=True),
        "FaithfulnessMetric": lambda: FaithfulnessMetric(model="gpt-4o-mini", include_reason=True)
    }

    # Check if the metric name is valid
    if metric_name not in metric_mapping:
        raise ValueError(f"Invalid metric name '{metric_name}'. Choose from: {list(metric_mapping.keys())}")

    # Initialize the metric
    metric = metric_mapping[metric_name]()
    document_choice = "./PANW-10Q-Oct2024.pdf"
    pkl_file = "./test_data_PANW.pkl"
    test_cases = [] 

    save_to_cache = False
    # Define test cases
    with open(pkl_file, "rb") as f:
        loaded_data = pickle.load(f)
    print(len(loaded_data), '<<<<<<<<<LOADED DATA')

    # Load existing cache
    cache_file = f"cache_answers_{os.path.splitext(os.path.basename(document_choice))[0]}_gpt-4o-mini_text-embedding-ada-002.pkl"
    results_file = "results_gpt-4o-mini_text-embedding-ada-002_relevancy.json"
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            print(f"Using cache file {cache_file}")
            cache_data = pickle.load(f)
    else:
        cache_data = {}
        save_to_cache = True

    existing_results = {}
    
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            existing_results = {entry["Query ID"]: entry for entry in json.load(f)}

    retrieval_depth = 5
    query_engine = load(document_choice, retrieval_depth, False)
    document_name = os.path.splitext(os.path.basename(document_choice))[0]
    #tests = {}
    #counter = 1
    for query_id, content in loaded_data.items():
        # if counter>3:
        #     break
        # counter = counter +1 
        # Check if result is cached
        if query_id in cache_data:
            answer, context = cache_data[query_id]
            
            #print(f"QUERY: {content['query']} is:\nANSWER: {answer}")
        else:
            # Run query if not cached
            answer, context = run_query(query=content['query'], query_engine=query_engine, document_name=document_name, retrieval_depth=retrieval_depth, verbose=False)
            cache_data[query_id] = (answer, context)  # Cache the result
            print(f"Generated result for query id: {query_id}")
        
        #Create the test case
        
        test_case = LLMTestCase(input=content['query'], actual_output=answer, retrieval_context=context)
        q_id = generate_query_id(content['query'], document_choice)
        tests[q_id] = test_case  
        
    if save_to_cache:
        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)
            print(f"Cache of answers saved to {cache_file}")

    #counter = 1
    for q_id, t in tests.items():
        # if counter>3:
        #     break
        # counter = counter +1 
        if q_id in existing_results:
            print(f"Skipping query id: {q_id} (already in {cache_file})")
            continue
            
        time.sleep(1)
        answer, context = cache_data[q_id]
        
        metric.measure(t)
        print(f"Query : {loaded_data[q_id]['query']} \nAnswer: {answer} \nExpected Answer: {loaded_data[q_id]['expected_answer']} \nScore: {metric.score}")
        
        append_to_json_file({
        "Query ID": q_id,
        "Query": loaded_data[q_id]['query'],
        "Answer": answer,
        "Expected Answer": loaded_data[q_id]['expected_answer'],
        "Score": metric.score
        }, results_file)


if __name__ == "__main__":
    start = time.time()
    runEvaluation("AnswerRelevancyMetric")
    print(f"Takes {time.time() - start} secs")
