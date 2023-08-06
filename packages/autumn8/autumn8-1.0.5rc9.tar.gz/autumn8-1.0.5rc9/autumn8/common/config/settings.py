import enum


class CloudServiceProvider(str, enum.Enum):
    AMAZON = "Amazon"
    GOOGLE = "Google Cloud Platform"
    ORACLE = "Oracle"
    AZURE = "Azure"
    AUTUMN8 = "Autumn8"


supported_hardwares = [
    {
        "name": "Ampere Altra",
        "vendor": "Ampere",
        "arch": "armv8.2+",
    },
    {
        "name": "Intel Xeon",
        "vendor": "Intel",
        "arch": "x86",
    },
    {
        "name": "Intel Xeon Platinum",
        "vendor": "Intel",
        "arch": "x86",
    },
    {
        "name": "Intel Xeon Platinum Ice Lake",
        "vendor": "Intel",
        "arch": "x86",
    },
    {
        "name": "Intel Cascade Lake CPU",
        "vendor": "Intel",
        "arch": "x86",
    },
    {
        "name": "Intel Skylake CPU",
        "vendor": "Intel",
        "arch": "x86",
    },
    {
        "name": "AMD EPYC",
        "vendor": "AMD",
        "arch": "amd64",
    },
    {
        "name": "Amazon Graviton2",
        "vendor": "Amazon",
        "arch": "Arm64 Neoverse",
    },
    {
        "name": "NVIDIA K80 GPUs",
        "vendor": "NVIDIA",
        "arch": "NVIDIA K80 GPUs",
    },
    {
        "name": "NVIDIA T4 GPUs",
        "vendor": "NVIDIA",
        "arch": "NVIDIA T4 GPUs",
    },
    {
        "name": "NVIDIA V100 GPUs",
        "vendor": "NVIDIA",
        "arch": "NVIDIA V100 GPUs",
    },
    {
        "name": "NVIDIA A10G",
        "vendor": "NVIDIA",
        "arch": "NVIDIA A10G",
    },
    {
        "name": "NVIDIA Tesla M60 GPU",
        "vendor": "NVIDIA",
        "arch": "NVIDIA Tesla M60 GPU",
    },
]


class Quantization(str, enum.Enum):
    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"


supported_quants = [q.value for q in Quantization]


class Framework(str, enum.Enum):
    TENSORFLOW = "TENSORFLOW"
    PYTORCH = "PYTORCH"
    TFLITE = "TFLITE"
    ONNX = "ONNX"


supported_frameworks = [f.value for f in Framework]

supported_domains = [
    {
        "domain": "Computer Vision",
        "tasks": [
            "Classification",
            "Object Detection",
            "Image Segmentation",
            "Depth Estimation",
            "Pose Estimation",
        ],
    },
    {"domain": "NLP", "tasks": ["Translation", "Text Classification", "BERT"]},
    {"domain": "Other", "tasks": ["Other"]},
]

# TODO make an enum out of this after I'm merged with Rafal's MLFlow PRs
def get_supported_providers():
    return [provider.value for provider in CloudServiceProvider]


supported_batch_sizes = [1, 8, 16, 32, 64]


class ModelFileType(str, enum.Enum):
    H5 = "h5"
    PB = "pb"
    FOLDER = "folder"
    MLFLOW = "mlflow"
    MAR = "mar"
    GPTJ = "gptj"


def is_domain_task_supported(domain, task):
    for supported_domain in supported_domains:
        if supported_domain["domain"] == domain:
            for supported_task in supported_domain["tasks"]:
                if supported_task == task:
                    return True
    return False
