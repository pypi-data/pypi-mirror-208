# Install torch

This script can be used to automatically install torch and CUDA. 

## How it works?

1. The user is prompted to select whether they want to install the CPU or GPU version of torch.
2. If the GPU version is selected, the user is prompted to enter the version of CUDA they want to install.
3. The script checks if CUDA is already installed and if it is not, it downloads and installs the version specified by the user.
4. The script then downloads and installs the appropriate version of torch based on the user's initial selection.

## Requirements

This script requires the following Python packages:

- rich
- beautifulsoup4
- wget
- requests
- requests-html
- tqdm

You can install these packages by running `pip install -r requirements.txt`.

## Usage

To use this script install it using pip:

```bash
pip install install_torch
install-torch
```

Alternatively, you can download the script and run it directly using Python:

```bash
git clone https://github.com/hawier-dev/install_torch.git
python install_torch.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.