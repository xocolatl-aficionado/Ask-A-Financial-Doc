

from script import load, run_query
import os
def evaluate():

    document_choice = "./TSLA-10Q-Sep2024.pdf"
    # Define test cases
    ##TODO: CHANGE BELOW AS PER README
    test_cases = [
        {
            "query": "What is the net income for this quarter of 2024?",
            "expected_answer": "Net income for this quarter of 2024 is $2,183 million.",
        },
        {
            "query": "What is the value of total assets owned in the year 2024?",
            "expected_answer": "Total assets in 2024 were worth $119,852 million.",
        },
    ]
    retrieval_depth = 5
    query_engine = load(document_choice, retrieval_depth, False)
    document_name = os.path.splitext(os.path.basename(document_choice))[0]
    
    
    for test in test_cases:
        

        answer, context = run_query(
         query=test['query'], query_engine=query_engine, document_name=document_name, retrieval_depth=retrieval_depth, verbose=False
        )
        
        print(f"Query: {test['query']}")
        print(f"Answer: {answer}")
        print(f"Expected: {test['expected_answer']}")
        #print(f"Context: {context}")
        print("------")

if __name__ == "__main__":
    evaluate()
