

from script import load, run_query
import os
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
import matplotlib.pyplot as plt
import json
import re

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

def runEvaluation(metric_name: str):
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
    test_cases = [] 
    # Define test cases
    test_questions = [
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the reporting period for the Palo Alto Networks quarterly report?",
    "expected_answer": "The quarterly report covers the period ending October 31, 2024."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the total revenue for the quarter?",
    "expected_answer": " Total revenue for the quarter was $2,138.8 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How did the revenue for the current quarter compare to the same quarter last year?",
    "expected_answer": "Revenue increased from $1,878.1 million in the same quarter last year to $2,138.8 million, showing a year-over-year growth"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the sources of revenue for Palo Alto Networks in this quarter?",
    "expected_answer": "Revenue sources included: Product revenue: $353.8 million ,Subscription and support revenue: $1,785.0 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the net income for the quarter?",
    "expected_answer": "Net income for the quarter was $350.7 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How does the net income this quarter compare to the previous year's same quarter?",
    "expected_answer": "Net income increased from $194.2 million in the same quarter last year to $350.7 million, indicating improved profitability."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the earnings per share (EPS) for the quarter?",
    "expected_answer": "The EPS for the quarter was: Basic: $1.07 and Diluted: $0.99"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the total operating expenses for the quarter?",
    "expected_answer": "Total operating expenses were $1,298.2 million, broken down as follows: Research and Development: $480.4 million Sales and Marketing: $720.1 million General and Administrative: $97.7 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What is the company's cash and cash equivalents balance as of October 31, 2024?",
    "expected_answer": "The cash and cash equivalents balance was $2,282.8 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What is Palo Alto Networks primary market focus?",
    "expected_answer": "Palo Alto Networks focuses on providing cybersecurity solutions for enterprises, organizations, service providers, and government entities, emphasizing AI-driven automation and comprehensive security."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the total gross profit for the quarter?",
    "expected_answer": "The total gross profit was $1,584.7 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What percentage of total revenue was derived from subscription and support services?",
    "expected_answer": "Approximately 83.5% of total revenue came from subscription and support services."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much did Palo Alto Networks spend on Research and Development this quarter?",
    "expected_answer": "The Company spent $480.4 million on Research and Development."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much was allocated to Sales and Marketing?",
    "expected_answer": "$720.1 million was allocated to Sales and Marketing."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the year-over-year growth in subscription revenue?",
    "expected_answer": "Subscription revenue grew from $988.3 million in the prior year to $1,191.8 million, a growth of approximately 20.6%"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the company’s deferred revenue balance as of October 31, 2024?",
    "expected_answer": "Deferred revenue was $5,507.7 million for the current portion and $5,585.9 million for the long-term portion."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How did accounts receivable change from July 31, 2024, to October 31, 2024?",
    "expected_answer": "Accounts receivable decreased from $2,618.6 million to $1,132.9 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What were the company’s total liabilities as of October 31, 2024?",
    "expected_answer": "Total liabilities amounted to $14,462.8 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the goodwill balance as of October 31, 2024?",
    "expected_answer": "Goodwill stood at $4,050.8 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much was spent on business acquisitions during the quarter?",
    "expected_answer": "$500.0 million was spent on business acquisitions."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the fair value of the company’s long-term investments as of October 31, 2024?",
    "expected_answer": "The fair value of long-term investments was $4,119.7 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What were the company’s total assets as of October 31, 2024?",
    "expected_answer": "Total assets were $20,374.6 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How did the company’s stockholders’ equity change during the quarter?",
    "expected_answer": "Stockholders’ equity increased from $5,169.7 million to $5,911.8 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the total revenue from the Americas region?",
    "expected_answer": "Revenue from the Americas was $1,442.1 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much revenue was generated in the EMEA region?",
    "expected_answer": "The EMEA region generated $441.4 million in revenue."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much revenue came from the APAC region?",
    "expected_answer": "The APAC region contributed $255.3 million in revenue."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What is the total value of the remaining performance obligations?",
    "expected_answer": "Remaining performance obligations totaled $12.6 billion as of 31st October, 2024. "
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What portion of the remaining performance obligations is expected to be recognized within the next 12 months?",
    "expected_answer": "Approximately $5.9 billion is expected to be recognized within the next 12 months."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much was spent on share-based compensation during the quarter?",
    "expected_answer": "$294.3 million was spent on share-based compensation"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the effective tax rate for the quarter?",
    "expected_answer": "The effective tax rate was 4.9%"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the increase in net carrying amount of goodwill due to acquisitions?",
    "expected_answer": "The net carrying amount of goodwill increased by $700.7 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much was recognized as amortization expense for purchased intangible assets?",
    "expected_answer": "$41.3 million was recognized as amortization expense."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What is the estimated future amortization expense for intangible assets for the fiscal year ending July 31, 2025?",
    "expected_answer": "The estimated future amortization expense is $124.5 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much did the company recognize in interest income?",
    "expected_answer": "The company recognized $85.7 million in interest income"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the net cash provided by operating activities during the quarter?",
    "expected_answer": "Net cash provided by operating activities was $1,509.6 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much cash was used in investing activities?",
    "expected_answer": "$543.8 million was used in investing activities."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much cash was used in financing activities?",
    "expected_answer": "$219.7 million was used in financing activities."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the Closing balance of cash and cash equivalents?",
    "expected_answer": "The ending balance was $2,282.8 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How many RSUs were granted during the quarter?",
    "expected_answer": "0.4 million RSUs were granted"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the weighted-average grant date fair value per share for the RSUs?",
    "expected_answer": "The weighted-average grant date fair value per share was $351.52."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How did Palo Alto Networks address foreign currency risks?",
    "expected_answer": "The company used foreign currency forward contracts as cash flow hedges."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much was the total notional amount of foreign currency forward contracts designated as cash flow hedges?",
    "expected_answer": "The total notional amount was $656.6 million as of October 31, 2024."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the unrealized loss on cash flow hedges recognized in Accumulated Other Comprehensive Income (AOCI)?",
    "expected_answer": "A net loss of $7.5 million was recognized in AOCI."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much was the contingent consideration liability related to business acquisitions?",
    "expected_answer": "The contingent consideration liability was $655.2 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What acquisition did Palo Alto Networks complete during the quarter?",
    "expected_answer": "The company completed the acquisition of certain IBM QRadar assets on August 31, 2024."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the total purchase consideration for the IBM QRadar acquisition?",
    "expected_answer": "The total purchase consideration was $1.1 billion."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much goodwill was generated from the IBM QRadar acquisition?",
    "expected_answer": "$700.7 million in goodwill was generated."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What was the fair value of intangible assets acquired in the IBM QRadar acquisition?",
    "expected_answer": "The fair value was $476.0 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much of the acquired intangible assets was allocated to customer relationships?",
    "expected_answer": "$464.0 million was allocated to customer relationships."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " How much of the acquired intangible assets was allocated to developed technology?",
    "expected_answer": "$12.0 million was allocated to developed technology."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the estimated useful life of customer relationships acquired in the IBM QRadar acquisition?",
    "expected_answer": "The estimated useful life is 12 years. "
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What were the company’s total purchase commitments as of October 31, 2024?",
    "expected_answer": "Total purchase commitments were $4,450.4 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much of the purchase commitments was allocated to cloud services?",
    "expected_answer": "$4,088.9 million was allocated to cloud services."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the company’s legal contingencies during the quarter?",
    "expected_answer": "Significant legal contingencies included lawsuits filed by Centripetal Networks, Inc., and Finjan, Inc."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much was accrued for the Centripetal Networks lawsuit?",
    "expected_answer": "$141.4 million was accrued for the Centripetal Networks lawsuit"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the resolution of the Centripetal Networks lawsuit?",
    "expected_answer": "A judgment was issued affirming infringement on three patents and reducing damages to $113.6 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much was recognized as general and administrative expense due to the lawsuit?",
    "expected_answer": "$43.0 million was released as a reduction to general and administrative expense."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How many PSUs were granted during the quarter?",
    "expected_answer": "1.6 million PSUs were granted."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What performance conditions are tied to the granted PSUs?",
    "expected_answer": "The PSUs are tied to next-generation security annualized recurring revenue and non-GAAP net income per diluted share"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company spend on taxes related to share settlement of equity awards?",
    "expected_answer": "The company spent $21.4 million on taxes related to share settlement."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the expected remaining amortization period for purchased intangible assets?",
    "expected_answer": "The remaining amortization period spans from fiscal year 2025 to 2030 and thereafter. "
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much revenue was recognized from amounts deferred as of July 31, 2024?",
    "expected_answer": "Approximately $1.6 billion in revenue was recognized."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the effective interest rate for the 2025 Convertible Senior Notes?",
    "expected_answer": "The effective interest rate is 0.6%."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the total interest expense on the 2025 Notes during the quarter?",
    "expected_answer": "Total interest expense was $1.2 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How many shares of common stock were issued to holders of the 2025 Notes?",
    "expected_answer": "2.3 million shares were issued to holders during the quarter."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the strike price for the 2025 Note Hedges?",
    "expected_answer": "The strike price is $99.20 per share."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company spend on the 2025 Note Hedges?",
    "expected_answer": "$370.8 million was spent on the 2025 Note Hedges."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much remains authorized for share repurchases?",
    "expected_answer": "$1.0 billion remains authorized for share repurchases."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How many shares were repurchased during the quarter?",
    "expected_answer": "No shares were repurchased during the quarter."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What are the financial instruments classified as Level 1 in fair value measurements?",
    "expected_answer": "Money market funds are classified as Level 1."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the estimated fair value of the 2025 Notes as of October 31, 2024?",
    "expected_answer": "The estimated fair value is $2.3 billion."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How many outstanding PSOs were fully vested as of October 31, 2024?",
    "expected_answer": "All 4.2 million PSOs were fully vested."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much was allocated for cloud service purchase commitments through September 2027?",
    "expected_answer": "$137.2 million was allocated."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the company's long-term operating lease liabilities as of October 31, 2024?",
    "expected_answer": "Long Term Operating lease liabilities totaled $379.6 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the estimated volatility used for PSUs with market conditions?",
    "expected_answer": "Volatility estimates ranged from 44.1% to 47.6%."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the total value of unrealized losses on available-for-sale securities?",
    "expected_answer": "Total unrealized losses were $8.6 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the net change in accounts payable during the quarter?",
    "expected_answer": "Accounts payable increased by $96.8 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company invest in property, equipment and other assets during the quarter?",
    "expected_answer": "The company invested $44.1 million in property, equipment and other assets."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the value of the company's deferred tax assets as of October 31, 2024?",
    "expected_answer": "Deferred tax assets were valued at $2,397.5 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the main sources of other income, net, during the quarter?",
    "expected_answer": "Other income, net, included: Interest income: $85.7 million Foreign currency exchange losses: $(7.5) million and Other income: $5.1 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company amortize for deferred contract costs?",
    "expected_answer": "Amortization of deferred contract costs was $110.4 million"
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the maturity date for the 2025 Convertible Senior Notes?",
    "expected_answer": "The maturity date is June 1, 2025."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the maximum contractual term for Performance Stock Options (PSOs)?",
    "expected_answer": "The maximum contractual term is 7.5 years."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much revenue was deferred during the quarter?",
    "expected_answer": "Approximately $416.6 million in revenue was deferred."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much cash did the company generate from financing receivables during the quarter?",
    "expected_answer": "Net cash generated from financing receivables was $10.7 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much is the estimated amortization expense for fiscal year 2026?",
    "expected_answer": "The estimated amortization expense for fiscal year 2026 is $140.6 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How does the company plan to utilize its $400 million revolving credit facility?",
    "expected_answer": "The credit facility is available for general corporate purposes, with no amounts drawn as of October 31, 2024."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much contingent consideration is expected to be paid for the IBM QRadar acquisition?",
    "expected_answer": "The estimated range of undiscounted contingent consideration is between $0.5 billion and $0.9 billion."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the weighted-average remaining period for unvested share-based compensation?",
    "expected_answer": "The weighted-average remaining period is approximately 2.5 years."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What percentage of total assets does goodwill represent as of October 31, 2024?",
    "expected_answer": "Goodwill represents approximately 19.9% of total assets, calculated as $4,050.8 million of goodwill out of $20,374.6 million in total assets."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What is the estimated useful life for developed technology acquired in the IBM QRadar deal?",
    "expected_answer": "The estimated useful life is 2 years."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the total gross unrealized losses on available-for-sale debt securities for less than 12 months as of October 31, 2024?",
    "expected_answer": "The total gross unrealized losses were $7.3 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What was the total cash inflow from proceeds related to employee equity incentive plans during the quarter?",
    "expected_answer": "The total cash inflow was $120.7 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company recognize in foreign currency exchange losses during the quarter?",
    "expected_answer": "The company recognized $7.5 million in foreign currency exchange losses."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company report as accumulated other comprehensive loss as of October 31, 2024?",
    "expected_answer": "Accumulated other comprehensive loss was $4.0 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "What were the company’s operating lease right-of-use assets as of October 31, 2024?",
    "expected_answer": "Operating lease right-of-use assets were valued at $389.0 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did Palo Alto Networks pay for taxes related to share settlements during the quarter?",
    "expected_answer": "The company paid $21.4 million in taxes related to share settlements."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much revenue was recognized from product sales during the quarter?",
    "expected_answer": "Revenue from product sales was $353.8 million."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": "How much did the company spend on purchases of investments during the quarter?",
    "expected_answer": "The company spent $660.0 million on purchases of investments."
  },
  {
    "document_choice": "./PANW-10Q-Oct2024.pdf",
    "query": " What is the value of the interest expense for the quarter ending October 31, 2024?",
    "expected_answer": "The value of total interest expense is $1.2 Million. "
  }
]
    
    retrieval_depth = 5
    query_engine = load(document_choice, retrieval_depth, False)
    document_name = os.path.splitext(os.path.basename(document_choice))[0]
    ##TODO: CHANGE BELOW AS PER README

    for test in test_questions:
        answer, context = run_query(query = test['query'], query_engine=query_engine, document_name=document_name, retrieval_depth=retrieval_depth, verbose=False)
        test_case = LLMTestCase(input=test["query"], actual_output=answer, retrieval_context=context)
        test_cases.append(test_case)  # Add the test case to the list
        print(f"Query: {test['query']}")
        print(f"Answer: {answer}")
        print(f"Expected: {test['expected_answer']}")
        print("------")
    results = evaluate(test_cases, [metric], use_cache=True)  # Evaluate using the specified metric(s)
    parsed_results = parse_test_results(results)
    save_to_json_file(parse_test_results, metric_name)
    plot_test_results(parsed_results)
        
if __name__ == "__main__":
    runEvaluation("FaithfulnessMetric")
