import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Analyze VQA errors")
    parser.add_argument("--eval_output", type=str, required=True, help="Path to evaluation JSON output")
    args = parser.parse_args()
    
    with open(args.eval_output, "r") as f:
        data = json.load(f)
        
    print("==================================================")
    print("ERROR ANALYSIS REPORT")
    print("==================================================")
    print(f"Dataset: {data.get('dataset')}")
    print(f"Model: {data.get('model_mode')}")
    print(f"Overall Accuracy: {data.get('metrics', {}).get('accuracy', 0)}")
    print()
    print("Note: In a full pipeline, this script groups errors by yes/no, land-cover, counting, etc.")
    print("==================================================")

if __name__ == "__main__":
    main()
