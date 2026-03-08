import argparse
from hunter import analyze_path, to_report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    args = ap.parse_args()
    print(to_report(analyze_path(args.target)))

if __name__ == "__main__":
    main()
