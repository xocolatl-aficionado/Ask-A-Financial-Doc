

from script import main

def evaluate():
    # Define test cases
    test_cases = [
        {
            "document_choice": "./TSLA-10Q-Sep2024.pdf",
            "query": "What is the net income for this quarter of 2024?",
            "expected_answer": "Net income for this quarter of 2024 is $2,183 million.",
        },
        {
            "document_choice": "./TSLA-10Q-Sep2024.pdf",
            "query": "What is the value of total assets owned in the year 2024?",
            "expected_answer": "Total assets in 2024 were worth $119,852 million.",
        },
    ]
    
    ##TODO: CHANGE BELOW AS PER README

    for test in test_cases:
        answer, context = main(
            document_choice=test["document_choice"],
            query=test["query"],
            retreival_depth=5,
            verbose=True,
        )
        
        print(f"Query: {test['query']}")
        print(f"Answer: {answer}")
        print(f"Expected: {test['expected_answer']}")
        print(f"Context: {context}")
        print("------")

if __name__ == "__main__":
    evaluate()
