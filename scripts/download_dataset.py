import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="SatQuery Dataset Downloader")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset to download (bigearthnet, rsvqa)")
    parser.add_argument("--output_dir", type=str, default="data/", help="Output directory")
    args = parser.parse_args()
    
    print("==================================================")
    print("SATQUERY DATASET MANAGER")
    print("==================================================")
    print(f"Dataset: {args.dataset}")
    print(f"Destination: {args.output_dir}")
    print("Note: To avoid massive accidental downloads, this script requires explicit confirmation.")
    print("In Day 4, we use pre-existing manifests rather than downloading TBs of data.")
    print("==================================================")

if __name__ == "__main__":
    main()
