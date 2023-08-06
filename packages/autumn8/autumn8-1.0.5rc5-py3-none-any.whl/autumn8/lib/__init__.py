import io
import json
import os
import sys
import zipfile

from autumn8.common._version import __version__
from autumn8.lib.package_resolver import lazy_import_pytorch, package

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))


def export_tensorflow_model_repr(
    model,
    dummy_input,
    interns=[],
    externs=[],
    max_search_depth=5,
    preprocess=None,
    postprocess=None,
):
    return export_model_repr(
        model,
        dummy_input,
        "TENSORFLOW",
        interns,
        externs,
        max_search_depth,
        preprocess,
        postprocess,
    )


def export_pytorch_model_repr(
    model,
    dummy_input,
    interns=[],
    externs=[],
    max_search_depth=5,
    preprocess=None,
    postprocess=None,
):
    return export_model_repr(
        model,
        dummy_input,
        "PYTORCH",
        interns,
        externs,
        max_search_depth,
        preprocess,
        postprocess,
    )


def export_model_repr(
    model,
    dummy_input,
    framework,
    interns=[],
    externs=[],
    max_search_depth=5,
    preprocess=None,
    postprocess=None,
):
    bytes = io.BytesIO()

    if framework == "PYTORCH":
        externs.append("torch")
        externs.append("torchvision")

    if framework == "TENSORFLOW":
        externs.append("tensorflow")

    file, requirements, package_name = package(
        model, interns, externs, max_search_depth
    )

    (
        file_preprocess,
        requirements_preprocess,
        package_name_preprocess,
        file_postprocess,
        requirements_postprocess,
        package_name_postprocess,
    ) = [None for i in range(6)]

    if preprocess is not None:
        (
            file_preprocess,
            requirements_preprocess,
            package_name_preprocess,
        ) = package(preprocess, interns, externs, max_search_depth)
        requirements.update(requirements_preprocess)

    if postprocess is not None:
        (
            file_postprocess,
            requirements_postprocess,
            package_name_postprocess,
        ) = package(postprocess, interns, externs, max_search_depth)
        requirements.update(requirements_postprocess)

    (
        file_input,
        requirements_input,
        package_name_input,
    ) = package(dummy_input, interns, externs, max_search_depth)
    requirements.update(requirements_input)

    with zipfile.ZipFile(bytes, "w") as zip:
        zip.writestr(
            "MANIFEST",
            json.dumps(
                {
                    "version": __version__,
                    "package_name": package_name,
                    "package_name_preprocess": package_name_preprocess,
                    "package_name_postprocess": package_name_postprocess,
                    "package_name_input": package_name_input,
                }
            ),
        )
        zip.write(file.name, arcname="model.package")
        zip.write(file_input.name, arcname="input.package")
        if file_preprocess is not None:
            zip.write(file_preprocess.name, arcname="preprocess.package")
        if file_postprocess is not None:
            zip.write(file_postprocess.name, arcname="postprocess.package")
        requirement_list = []
        for package_name, package_version in requirements.items():
            requirement_list.append(f"{package_name}=={package_version}")

        zip.writestr("requirements.txt", "\n".join(requirement_list))

    bytes.seek(0)
    return bytes


def load_model(filename):
    extract_path = "/tmp/" + os.path.basename(filename)
    with zipfile.ZipFile(filename) as z:
        z.extractall(extract_path)

    with open(os.path.join(extract_path, "MANIFEST"), "r") as manifest:
        manifest_content = json.loads(manifest.read())
        package_name = manifest_content["package_name"]
        package_name_preprocess = (
            manifest_content["package_name_preprocess"]
            if "package_name_preprocess" in manifest_content
            else None
        )
        package_name_postprocess = (
            manifest_content["package_name_postprocess"]
            if "package_name_postprocess" in manifest_content
            else None
        )
        package_name_input = (
            manifest_content["package_name_input"]
            if "package_name_input" in manifest_content
            else None
        )
    torch = lazy_import_pytorch()
    model_file = open(os.path.join(extract_path, "model.package"), "rb")
    resource_name = "model.pkl"
    imp = torch.package.PackageImporter(model_file)
    loaded_model = imp.load_pickle(package_name, resource_name)

    loaded_input = None
    if package_name_input is not None:
        input_file = open(os.path.join(extract_path, "input.package"), "rb")
        resource_name = "model.pkl"
        imp = torch.package.PackageImporter(input_file)
        loaded_input = imp.load_pickle(package_name_input, resource_name)

    loaded_preprocess = None
    if package_name_preprocess is not None:
        model_file = open(
            os.path.join(extract_path, "preprocess.package"), "rb"
        )
        resource_name = "model.pkl"
        imp = torch.package.PackageImporter(model_file)
        loaded_preprocess = imp.load_pickle(
            package_name_preprocess, resource_name
        )

    loaded_postprocess = None
    if package_name_postprocess is not None:
        model_file = open(
            os.path.join(extract_path, "postprocess.package"), "rb"
        )
        resource_name = "model.pkl"
        imp = torch.package.PackageImporter(model_file)
        loaded_postprocess = imp.load_pickle(
            package_name_postprocess, resource_name
        )

    return loaded_model, loaded_preprocess, loaded_postprocess, loaded_input


attached_models = []


# TODO: create 'annotate' module?
def attach_model(
    model,
    example_input,
    interns=None,
    externs=None,
    max_search_depth=5,
    preprocess=None,
    postprocess=None,
):
    if interns is None:
        interns = []
    if externs is None:
        externs = []
    attached_models.append(
        (
            model,
            example_input,
            interns,
            externs,
            max_search_depth,
            preprocess,
            postprocess,
        )
    )
