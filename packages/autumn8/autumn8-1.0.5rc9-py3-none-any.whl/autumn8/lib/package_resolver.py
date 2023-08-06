import pkgutil
import random
import string
import sys
import tempfile
import traceback

import pkg_resources

# TODO that package resolver needs some work
env = dict(tuple(str(ws).split()) for ws in pkg_resources.working_set)

packages = []
for ws in pkgutil.iter_modules():
    if ws.ispkg:
        packages.append(ws.name)

system_packages = list(sys.builtin_module_names)
system_packages.append("os")
system_packages.append("pkg_resources")
for p in system_packages:
    env[p] = "0"
    packages.append(p)


def guess_if_package_is_external(name, interns, externs):
    split_name = name.split(".")
    for extern in externs:
        split_extern = extern.split(".")
        if split_extern[0] == split_name[0]:
            return True

    for intern in interns:
        split_intern = intern.split(".")
        if split_intern[0] == split_name[0]:
            return False

    return split_name[0] in env


# Max search depth is just some constant to ensure it will end.
# And if it is resolving that long, that can mean 2 thing:
# model has a lot of submodules importing submodules etc or
# we added some system module by accident and we are trying now recursively add some subsystems.
def package(model, interns=[], externs=[], max_search_depth=5):
    file = tempfile.NamedTemporaryFile()
    # NOTE: if any intern name will be equal to package_name, then packaged model will not be possible to import
    package_name_length = 10
    package_name = "".join(
        random.choices(string.ascii_lowercase, k=package_name_length)
    )
    resource_name = "model.pkl"

    success = False
    torch = lazy_import_pytorch()
    for i in range(0, max_search_depth):
        try:
            with torch.package.PackageExporter(file.name) as exp:
                for intern in interns:
                    exp.intern(intern)

                for extern in externs:
                    exp.extern(extern)
                exp.save_pickle(package_name, resource_name, model)

            success = True
            break
        except torch.package.package_exporter.PackagingError as err:
            for node in err.dependency_graph.nodes:
                if "error" in err.dependency_graph.nodes[node]:
                    if guess_if_package_is_external(node, interns, externs):
                        externs.append(node)
                    else:
                        interns.append(node)
        except:
            traceback.print_exc()
            break

    if not success:
        raise Exception(
            """Failed to resolve dependencies. Modules marked as intern:
{}

Modules marked as extern:
{}

If module was incorrectly labeled please pass it in autumn8.attach_model. Example:
autumn8.attach_model(model, input, interns = ["mymodule"], externs=["yaml"])
Specifing root of modules as extern should be enough
If all modules seems to be correctly marked as intern/extern please try bumping search depth. Example:
autumn8.attach_model(model, input, max_search_depth = 10)""".format(
                interns, externs
            )
        )
    requirements = {}

    for extern in externs:
        if extern in env and extern not in system_packages:
            requirements[extern] = env[extern]

    return file, requirements, package_name


def lazy_import_pytorch():
    try:
        import torch

        return torch
    except ModuleNotFoundError as err:
        raise RuntimeError(
            "This operation requires Pytorch to be installed, please install it by running `pip3 install pytorch`"
        ) from err
