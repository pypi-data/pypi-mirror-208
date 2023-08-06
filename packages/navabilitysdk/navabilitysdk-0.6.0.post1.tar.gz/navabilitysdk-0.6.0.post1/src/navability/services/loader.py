from __future__ import annotations
import os
import toml
import re
import pathlib

from gql import gql  # used to parse GraphQL queries
from graphql import GraphQLSyntaxError  # used to handle GraphQL errors

# Define a class to represent a GraphQL fragment with a name and data
class Fragment:
    def __init__(self, name: str, data: str):
        self.name = name
        self.data = data

    def generate_dependencies(
        self, all_fragments: dict[str, Fragment]
    ) -> list[Fragment]:
        # Pattern for any fragment starting with an ellipsis
        pattern = r"\.{3}[a-zA-Z_]*[ \n\r]"
        dependent_fragment_names = [
            match[3:-1] for match in re.findall(pattern, self.data)
        ]
        for d in dependent_fragment_names:
            if all_fragments.get(d, None) == None:
                raise Exception(
                    f"Query ${self.name} uses fragment ${d} and this fragment does not exist."
                )
        self.dependent_fragments = [all_fragments[d] for d in dependent_fragment_names]
        return self.dependent_fragments

    # Define a function to extract the name of a fragment from its string representation
    def get_fragment_name(self) -> str:
        pattern = r"fragment\s+(\S+)\s+on"
        match = re.search(pattern, self.data)
        if match:
            return match.group(1)
        else:
            return None

    def __str__(self) -> str:
        return f"{self.name}:\n" + "\n".join([str(d) for d in self.data])


# Define a class to represent a GraphQL operation (query, mutation, or subscription) with a type and data
class Operation:
    def __init__(self, operation_type: str, data: str):
        self.operation_type = operation_type
        self.data = data

    def __str__(self) -> str:
        return f"{self.operation_type}:\n{self.data}"


# Define a function to get all files with a given extension from a given folder path
def get_files(folder_path: str, extension: str) -> list[str]:
    files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isdir(file_path):
            files += get_files(file_path, extension)
        elif file.endswith(extension):
            files.append(file_path)
    return files


# Define a function to read all TOML files in a given folder path and return a dictionary of operation names mapped to their corresponding Operation objects
def get_operations(folder_path: str) -> dict[str, Operation]:
    files = get_files(folder_path, ".toml")

    fragments = {}
    operations = {}

    # Load all fragments
    for file in files:
        with open(file, "r") as f:
            data = toml.load(f)

            # Extract and store all fragments from the TOML file
            for (name, frag_string) in data["fragments"].items():
                fragment = Fragment(name=name, data=frag_string)
                fragments[name] = fragment

    # Flatten all dependencies
    for fragment in fragments.values():
        fragment.generate_dependencies(fragments)

    # [Alucard] Helper to detect cyclic dependencies - @GearsAD - could add in fragment
    def detect_cycle(
        fragment: Fragment, visited: set[Fragment], path: list[Fragment]
    ) -> bool:
        visited.add(fragment)
        path.append(fragment)

        for dep in fragment.dependent_fragments:
            if dep not in visited:
                if detect_cycle(dep, visited, path):
                    return True
            elif dep in path:
                print(
                    f"Warning: Cyclic reference detected in fragments: {', '.join([f.name for f in path])}"
                )
                return True

        path.pop()
        return False

    visited = set()
    for fragment in fragments.values():
        if fragment not in visited:
            detect_cycle(fragment, visited, [])

    # Remove duplicates
    # import pdb; pdb.set_trace()
    for f in fragments.values():
        pass

    # Replace all fragment recursion if any exist (expecting "...")
    while any([len(f.dependent_fragments) > 0 for f in fragments.values()]):
        # Go through the list until done.
        for fragment in fragments.values():
            if len(fragment.dependent_fragments) > 0:  # Else ignore.
                # If all parents have been resolved, resolve it.
                if all(
                    [
                        len(f.dependent_fragments) == 0
                        for f in fragment.dependent_fragments
                    ]
                ):
                    fragment.data = (
                        "\r\n".join([df.data for df in fragment.dependent_fragments])
                        + "\r\n"
                        + fragment.data
                    )
                    # Clear it
                    fragment.dependent_fragments = []

    # Load all operations and include all fragments
    for file in files:
        with open(file, "r") as f:
            data = toml.load(f)
            # Extract and store all operations from the TOML file
            for (name, operation_data) in data["operations"].items():
                operation = Operation(operation_type="", data=operation_data)
                # Include any fragments at the bottom of the query if they are used in the query
                for (fd_name, fragment) in fragments.items():
                    if fd_name in operation_data:
                        operation.data += "\n" + "\n" + fragment.data
                try:
                    # Parse the operation data using the gql function and set the operation type
                    operation.data = gql(operation.data)
                    operation.operation_type = operation.data.definitions[0].operation
                    operations[name] = operation
                except GraphQLSyntaxError as e:
                    # If there is an error parsing the operation data, print an error message
                    print(
                        f"Error: Error parsing operation data: {e} \n {operation.data}"
                    )

    return (fragments, operations)


# Load all GraphQL operations from the "sdkCommonGQL" folder and export them
GQL_FRAGMENTS, GQL_OPERATIONS = get_operations(os.path.join(pathlib.Path(__file__).parent.parent.parent,"sdkCommonGQL"))
#   (os.path.join(".", "sdkCommonGQL"))
