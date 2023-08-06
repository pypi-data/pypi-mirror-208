#!/usr/bin/env python3

import os
import argparse
import pyperclip

INFRA_PATH = "~/Documents/Clients/citadel/infra/.clients"

def select_customer():
    customers = [folder for folder in os.listdir(os.path.expanduser(INFRA_PATH)) if os.path.isdir(os.path.join(os.path.expanduser(INFRA_PATH), folder)) and not folder.startswith(".")]
    print("Available customers:")
    for i, customer in enumerate(customers):
        print(f"{i+1}. {customer}")

    customer_index = int(input("Select a customer (enter the corresponding number): ")) - 1
    selected_customer = customers[customer_index]
    return selected_customer

def select_stack(customer):
    stack_path = os.path.expanduser(os.path.join(INFRA_PATH, customer))
    stack_files = [folder for folder in os.listdir(stack_path) if os.path.isdir(os.path.join(stack_path, folder)) and not folder.startswith(".")]
    print("Available stacks:")
    for i, stack in enumerate(stack_files):
        print(f"{i+1}. {stack}")

    stack_index = int(input("Select a stack (enter the corresponding number): ")) - 1
    selected_stack = stack_files[stack_index]
    return os.path.join(stack_path, selected_stack)

def select_workspace(stack_path):
    workspace_files = [file for file in os.listdir(stack_path) if file.endswith(".yaml")]
    print("Available workspaces:")
    for i, file in enumerate(workspace_files):
        print(f"{i+1}. {os.path.splitext(file)[0]}")

    workspace_index = int(input("Select a workspace (enter the corresponding number): ")) - 1
    selected_workspace = os.path.splitext(workspace_files[workspace_index])[0]
    return selected_workspace

def export_workspace_variable(workspace_name):
    workspace = f"export WORKSPACE={workspace_name}"
    return workspace

def main():
    parser = argparse.ArgumentParser(description="Select customer and stack for setting the workspace.")
    parser.add_argument("--customer", help="Name of the customer.")
    parser.add_argument("--stack", help="Name of the stack.")
    parser.add_argument("--no-copy", action="store_true", help="Disable copying the output to the clipboard.")
    args = parser.parse_args()

    if args.customer:
        customer = f"client-{args.customer}"
    else:
        customer = select_customer()

    if args.stack:
        stack_folder = os.path.join(os.path.expanduser(INFRA_PATH), customer, args.stack)
    else:
        stack_folder = select_stack(customer)

    workspace_name = select_workspace(stack_folder)
    output = export_workspace_variable(workspace_name)

    if not args.no_copy:
        pyperclip.copy(output)
        print("Output copied to clipboard.")
