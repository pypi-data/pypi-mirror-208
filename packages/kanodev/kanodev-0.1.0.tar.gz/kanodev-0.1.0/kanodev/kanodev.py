import argparse
import os
import argparse
import openai
from .src.utils.chat_utils import kubernetes_architecture_to_be_evaluated
from .src.utils.general_utils import collect_cloudwatch_logs

def check_env_vars():
    if 'OPENAI_API_KEY' not in os.environ:
        raise EnvironmentError('The OPENAI_API_KEY environment variable is not set.')
    else:
        openai.api_key = os.environ['OPENAI_API_KEY']
    if 'AWS_ACCESS_KEY_ID' not in os.environ:
        raise EnvironmentError('The AWS_ACCESS_KEY_ID environment variable is not set.')
    if 'AWS_SECRET_ACCESS_KEY' not in os.environ:
        raise EnvironmentError('The AWS_SECRET_ACCESS_KEY environment variable is not set.')
    if 'AWS_DEFAULT_REGION' not in os.environ:
        raise EnvironmentError('The AWS_DEFAULT_REGION environment variable is not set.')
    

def generate_infrastructure(text: str):
    check_env_vars()
    print("Generating infrastructure...")
    main_prompt=text.description
    local_text=text.description
    first_iteration=0
    second_iteration=0

    while first_iteration<11:
        try:
            first_iteration+=1
            cloud_watch_logs = collect_cloudwatch_logs()
            code_response_body = kubernetes_architecture_to_be_evaluated(main_prompt=main_prompt, text_prompt=local_text, cloud_watch_logs=cloud_watch_logs, iteration=first_iteration)
            print("Operation completed without errors.")
            break # If no exception is caught, exit the loop

        except Exception as error:
            print("Caught an error:", error)
            local_text=error

    while first_iteration>11 and second_iteration<11:
        try:
            second_iteration+=1
            cloud_watch_logs = collect_cloudwatch_logs()
            code_response_body = kubernetes_architecture_to_be_evaluated(main_prompt=main_prompt, text_prompt=local_text, cloud_watch_logs=cloud_watch_logs, restart_gpt=True, iteration=first_iteration)
            print("Operation completed without errors.")
            break # If no exception is caught, exit the loop

        except Exception as error:
            print("Caught an error:", error)
            local_text=error

    print(f"Final code: {code_response_body}")

def main():
    parser = argparse.ArgumentParser(description='KanoDev: Use natural language to create a fully functional, tested and deployed cloud infrastructure with a single command!')
    subparsers = parser.add_subparsers()

    generate_parser = subparsers.add_parser('generate')
    generate_parser.add_argument('--description', type=str, required=True, help='Description of the problem')
    generate_parser.set_defaults(func=generate_infrastructure)

    destroy_parser = subparsers.add_parser('destroy')
    destroy_parser.add_argument('--description', type=str, required=True, help='Description of the problem')

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()