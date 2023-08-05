#!/usr/bin/env python3
import argparse

# Introduction comment
# This program parses command line arguments according to the specified rules.

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="A program that parses arguments according to specific rules.")

    # Add the valid options
    parser.add_argument("-e", action="store_true", help="Enable the -e option")
    parser.add_argument("--model", choices=["gpt-3.5-turbo", "gpt-4"], help="Select the model to use")
    parser.add_argument("--max-chars", type=int, help="Set the maximum number of characters for message chunks")
    parser.add_argument("-v", action="store_true", help="Enable verbose mode")
    parser.add_argument("-q", action="store_true", help="Enable quiet mode")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    # Parse the arguments
    args, unknown_args = parser.parse_known_args()

    # Join the unknown arguments as a single string
    string_argument = " ".join(unknown_args)

    # Print the parsed arguments
    print("Parsed arguments:")
    print(args)
    print("String argument:")
    print(string_argument)

if __name__ == "__main__":
    main()
