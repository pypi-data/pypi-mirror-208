import git
import ast
import astunparse
import importlib

from pathlib import Path
from fire import Fire

from collections import OrderedDict


def read_text_from_file(fn):
    with open(fn, 'r') as file:
        return file.read()


def write_text_to_file(fn, text):
    with open(fn, "w") as f:
        f.write(text)


def get_imported_module_names(code, cwd):
    tree = ast.parse(code["text"])

    imported_module_names = []

    code["imports_to_remove"] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):

            for name in node.names:
                if "name" in code:
                    module_name = importlib.util.resolve_name(name.name, code["name"])
                else:
                    module_name = name.name
                imported_module_names.append((module_name, astunparse.unparse(node)))
                code["imports_to_remove"].append(astunparse.unparse(node))

        elif isinstance(node, ast.ImportFrom):

            if node.level == 1 and "name" in code:
                module_name = importlib.util.resolve_name("." + node.module, code["name"])
            else:
                module_name = node.module
            imported_module_names.append((module_name, astunparse.unparse(node)))
            code["imports_to_remove"].append(astunparse.unparse(node))

        # TODO detect __name__ == "__main__"
        # elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
        #     if hasattr(node.test.comparators[0], "s") \
        #     and node.test.comparators[0].s == "__main__" \
        #     and hasattr(node.test.left, "id") \
        #     and node.test.left.id == "__name__":
        #         print(ast.unparse(node))
        #         # print(node.enlineno)
        #     # if isinstance(node.test.comparators[0], ast.Str):
        #     #     print(node.test.comparators[0])

    imports = []
    for name, import_code in imported_module_names:
        # print(name)
        module_specs = importlib.util.find_spec(name)
        # print(type(module_specs.loader))
        # print(module_specs)

        if module_specs.origin is not None:
            module_fn = Path(module_specs.origin)
            module_is_local = cwd in module_fn.parents
        else:
            module_fn = None
            module_is_local = False

        info = {
            "name": name,
            "imported_code": import_code,
            "is_local": module_is_local,
            "fn": module_fn,
        }
        if module_is_local:
            info = {
                **info,
                "text": read_text_from_file(module_fn),
            }
            info = get_imported_module_names(info, cwd)

        imports.append(info)
    code["imports"] = imports
    return code


def del_text(code):
    if "text" in code:
        del code["text"]
    if "imports" in code:
        for sub_code in code["imports"]:
            del_text(sub_code)


def path_to_str(code):
    if "fn" in code:
        code["fn"] = str(code["fn"])
    if "imports" in code:
        for sub_code in code["imports"]:
            path_to_str(sub_code)


def update_load_order(code, load_order=[]):
    if code["is_local"]:
        load_order.append(code)
        if "imports" in code:
            for sub_code in reversed(code["imports"]):
                load_order = update_load_order(sub_code, load_order)
    return load_order


def get_load_order(code):
    load_order = update_load_order(code)
    load_order = list(reversed(load_order))
    load_order_fn = [n["fn"] for n in load_order]
    unique_fn = list(OrderedDict.fromkeys(load_order_fn))
    idx_of_unqiue = [load_order_fn.index(fn) for fn in unique_fn]
    load_order = [load_order[idx] for idx in idx_of_unqiue]
    return load_order

def remove_imports(text):
    tree = ast.parse(text)
    tree.body = [node for node in tree.body if not isinstance(node, ast.Import) \
                                            and not isinstance(node, ast.ImportFrom)]
    modified_text = astunparse.unparse(tree)
    return modified_text


def remove_nodes(text, nodes):
    tree = ast.parse(text)
    tree.body = [node for node in tree.body if node in nodes]
    modified_text = astunparse.unparse(tree)
    return modified_text

def get_modified_files(repo):
    diff = repo.index.diff(None)

    modified_files = []
    for file_diff in diff:
        modified_files.append(file_diff.a_path)

    return modified_files


def get_git_info():
    repo = git.Repo(search_parent_directories=True)

    modified = get_modified_files(repo)
    if modified:
        print("There are modified files in repo:")
        for fn in modified:
            print(f"{fn} - modified")

    commit_hash = repo.head.object.hexsha
    branch = repo.active_branch
    url = list(repo.remote().urls)[0]
    return url, branch, commit_hash


def get_nodes(entering_filename, cwd):
    code = {}
    code["text"] = read_text_from_file(str(entering_filename))
    code["fn"] = entering_filename
    code["is_local"] = True
    code = get_imported_module_names(code, cwd)
    return code


def flatten(code, init_message, cwd, ):
    load_order = get_load_order(code)

    full_text = ""
    imports_to_add = []

    for code in load_order:
        print(f"Flatten: {code['fn'].relative_to(cwd)}")
        text = remove_imports(code["text"])
        imports_to_add += [subcode["imported_code"] for subcode in code["imports"] \
                           if not subcode["is_local"]]
        full_text += f"\n# Code from {code['fn'].relative_to(cwd)} \n " + text
    imports_to_add = [i.replace("\n", "") + "\n" for i in imports_to_add]
    imports_to_add = list(sorted(set(imports_to_add)))
    modified_text = init_message + "".join(imports_to_add) + full_text
    return modified_text


def save_code_dependencies_to_json(code):
    import json

    del_text(code)
    path_to_str(code)

    with open("code.json", "w") as f:
        json.dump(code, f, indent=4)


def main(
    entering_filename,
    output_filename,
):
    import sys, os
    sys.path.append(os.getcwd())

    cwd = Path.cwd()
    entering_filename = Path(entering_filename).resolve()
    output_filename = Path(output_filename)

    git_url, git_branch, git_commit_hash = get_git_info()

    code = get_nodes(entering_filename, cwd)


    init_message = f"# Auto-generated code\n" \
                   f"# Entering point:  {entering_filename.relative_to(cwd)}\n" \
                   f"# Git repo link: {git_url}\n" \
                   f"# Git branch: {git_branch}, git commit hash: {git_commit_hash}\n\n"

    modified_text = flatten(code, init_message, cwd)
    write_text_to_file(output_filename, modified_text)

cli = lambda: Fire(main)
