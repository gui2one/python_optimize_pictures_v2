from pathlib import Path
import sys


def read_version_truth():
    version_str = ""
    with open("app_version.txt", "r") as f:
        version_str = f.read().strip()

    return [int(x) for x in version_str.split(".")]


def bump_version_truth():
    version_ints = read_version_truth()
    with open("app_version.txt", "w") as f:
        f.write(f"{version_ints[0]}.{version_ints[1]}.{version_ints[2] + 1}")


def get_version_variable_name_in_ISS_file(setup_file: Path):
    # find AppVersion= line
    lines = []
    with open(setup_file, "r") as f:
        lines = f.readlines()

    var_name = None
    for line in lines:
        if line.startswith("AppVersion="):
            #  extracting "MyAppVersion" from pattern -> AppVersion={#MyAppVersion}
            var_part = line.split("=")[1].split("{#")[1].replace("}", "")
            if len(var_part) > 0:
                var_name = var_part
                break

    if var_name is None:
        raise Exception(f"Could not find AppVersion line in {setup_file}")

    return var_name


def write_version_in_ISS_file(setup_file: Path):
    var_name = get_version_variable_name_in_ISS_file(setup_file)
    version_line_pattern = f"#define {var_name}".strip()
    version_ints = read_version_truth()

    with open(setup_file, "r") as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith(version_line_pattern):
            strings = line.split('"')[1].split(".")
            strings[2] = str(version_ints[2])
            modified_lines.append(
                f'{version_line_pattern} "{version_ints[0]}.{version_ints[1]}.{version_ints[2]}"\n'
            )
        else:
            modified_lines.append(line)

    with open(setup_file, "w") as f:
        f.writelines(modified_lines)

    return version_ints


if __name__ == "__main__":

    root = Path(__file__).parent
    setup_file = root / "inno_setup" / "setup.iss"

    bump_version_truth()
    ints = write_version_in_ISS_file(setup_file)
    print(f"new Version : {ints[0]}.{ints[1]}.{ints[2]}")
