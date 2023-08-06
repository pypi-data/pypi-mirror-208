import openai
import re
import subprocess

def extract_code_block(text: str) -> str:
    code_pattern = re.compile("```(.*?)```", re.DOTALL)
    match = code_pattern.search(text)
    if match:
        return match.group(1)
    else:
        return "No code block found."
    
def run_terraform_init():
    try:
        subprocess.run(['terraform', 'init'])
    except FileNotFoundError:
        print("Terraform command not found. Make sure it's installed and in your system's PATH.")

def run_terraform_validate():
    try:
        subprocess.run(['terraform', 'validate'])
    except FileNotFoundError:
        print("Terraform command not found. Make sure it's installed and in your system's PATH.")

def run_terraform_plan():
    try:
        subprocess.run(['terraform', 'plan'])
    except FileNotFoundError:
        print("Terraform command not found. Make sure it's installed and in your system's PATH.")

def run_terraform_apply():
    try:
        subprocess.run(['terraform', 'apply', '-auto-approve'])
    except FileNotFoundError:
        print("Terraform command not found. Make sure it's installed and in your system's PATH.")

def kubernetes_architecture_to_be_evaluated(main_prompt, text_prompt="write me a sqs and sns solution", cloud_watch_logs="", restart_gpt=False, vector_db=False, iteration=1):

    meta_prompt = '''You are an autonomous agent called "assistant for Kubernetes
    solution architecture" which acts as an terraform code generator.
    Don't include any explanations in your responses.
    This code should encapsulate all of the infrastructure needed to
    deploy to a Kubernetes cluster.

    To accomplish the goal, you must follow following rules:

    Rules:
    1. As "assistant", you MUST response only in python code. No other text besides terraform code.
    2. You should take into account previous responses and the error messages you get in the process.
    3. The responses from "user" are the error messages of the action you performed. Use them to correct the solution.
    4. Try not to over-engineer the solution.
    5. The solution should be as short as possible.
    6. Encapsulate the terraform code inside a SINGLE Terraform object.
    7. execute the script with terraform init, validate and plan.
    8. Execute the proposed solution with main.
    
    '''

    mainFile = open("main.tf", "w")

    messages = []

    if iteration == 1:
        messages.append({"role": "system", "content": meta_prompt})
        messages.append({"role": "user", "content": str(text_prompt)})
    else:
        messages.append({"role": "user", "content": "Here is the error message: " + str(text_prompt) + "This is the initially posed task to accomplish: " +
                        main_prompt + 'Additionally use the following cloud watch log messages to correct your response' + cloud_watch_logs})

    # CALL GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    

    if restart_gpt:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            user="New session"
        )

    # parse response, remove everything before the first ```python
    code_response_body = extract_code_block(response["choices"][0]["message"]["content"]).strip()

    search_string = "provider \"kubernetes\" {"
    index = code_response_body.find(search_string)
    if index == -1:
        # add the provider to the main.tf file
        # provider "kubernetes" {
        #   config_path = "~/.kube/config"
        # }
        mainFile.write("provider \"kubernetes\" {\n")
        mainFile.write("  config_path = \"~/.kube/config\"\n")
        mainFile.write("}\n")
    

    # write to main.tf
    mainFile.write(code_response_body)
    mainFile.close()

    run_terraform_init()
    run_terraform_validate()
    run_terraform_plan()
    run_terraform_apply()

    return code_response_body
