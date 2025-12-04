from pathlib import Path


def read_version_truth():
    version_str = ""
    with open("app_version.txt", "r") as f:
        version_str = f.read().strip()

    return [int(x) for x in version_str.split(".")]


def bump_version_truth():
    version_ints = read_version_truth()
    with open("app_version.txt", "w") as f:
        f.write(f"{version_ints[0]}.{version_ints[1]}.{version_ints[2] + 1}")


def read_version_in_ISS_file(setup_file: Path, version_line_pattern: str) -> list[int]:
    lines = []
    with open(setup_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith(version_line_pattern):
            strings = line.split('"')[1].split(".")
            ints = [int(strings[0]), int(strings[1]), int(strings[2])]
            return ints

    raise Exception(f"Could not find version line in {setup_file}")


def write_version_in_ISS_file(setup_file: Path, version_line_pattern: str):
    # version_ints = read_version_in_ISS_file(setup_file, version_line_pattern)
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

    version_line_pattern = "#define MyAppVersion"

    bump_version_truth()
    ints = write_version_in_ISS_file(setup_file, version_line_pattern)

    print(f"new Version : {ints[0]}.{ints[1]}.{ints[2]}")
