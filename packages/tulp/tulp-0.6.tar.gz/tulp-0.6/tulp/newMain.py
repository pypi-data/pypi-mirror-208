import argparse

def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-e', action='store_true', help='Description for option e')
    parser.add_argument('--model', type=str, choices=['gpt-3.5-turbo', 'gpt-4'], help='Description for option model')
    parser.add_argument('--max-chars', type=int, help='Description for option max-chars')
    parser.add_argument('-v', action='store_true', help='Description for option v')
    parser.add_argument('-q', action='store_true', help='Description for option q')
    parser.add_argument('prompt', nargs=argparse.REMAINDER, help='Instructions prompt')
    args = parser.parse_args()
    print(args)


    if 'help' in args:
        parser.print_help()
        return

    print( args.model or "fede" )
    if 'prompt' in args:
        print(args.prompt)


    # Your code here

if __name__ == '__main__':
    main()
