import argparse
import yaml


def analyze_yaml(filename):
    with open(filename, 'r') as f:
        contents = yaml.load(f, Loader=yaml.FullLoader)
        print(contents)
        print(contents[0]['date'] > contents[1]['date'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_file", nargs=1, help='yaml file name')
    args = parser.parse_args()
    analyze_yaml(args.yaml_file[0])
