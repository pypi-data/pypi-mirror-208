#!/usr/bin/env python
# Description: Check for outdated packages in your Pipfile
import json
import subprocess
from multiprocessing.pool import ThreadPool
from urllib.request import urlopen
import ssl
import os


def color_print(message, text_type, bold=False):
    if bold:
        print(text_type + "\033[1m" + message + "\033[0m")  # noqa T201
    else:
        print(text_type + message + "\033[0m")  # noqa T201


class BColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    # - ENDC = "\033[0m"


def main():
    ssl._create_default_https_context = ssl._create_unverified_context

    color_print(
        'Checking for outdated packages in your "Pipfile"...', BColors.OKBLUE, True
    )

    pipfile = os.path.join(os.getcwd(), "Pipfile")
    pipfile_packages = []

    if os.path.exists(pipfile):
        with open(pipfile, "r+") as pipfile:
            pipfile_lines = pipfile.read().splitlines()
            for i in range(len(pipfile_lines)):
                if pipfile_lines[i] == "[packages]":
                    for j in range(i + 1, len(pipfile_lines)):
                        if pipfile_lines[j] == "" or pipfile_lines[j][0] == "[":
                            break
                        elif not pipfile_lines[j].startswith("#"):
                            pipfile_packages.append(pipfile_lines[j].split("=")[0])

    pipfile_packages = [x.strip(' ') for x in pipfile_packages]
    # get package names max len
    package_name_len = (
            max([len(package) for package in pipfile_packages]) + 1
    )

    # get the list of installed packages
    try:
        installed_packages = json.loads(subprocess.check_output(["pip", "list", "--format=json"]).decode('utf-8').lower())
    except Exception as e:
        print("Error occurred while fetching installed packages:", e)
        exit(1)
    # pip list --format=json command sometimes gives different naming formats of the libraries.
    installed_packages = [{"name": i["name"].replace("_", "-"), "version": i["version"]} for i in installed_packages]


    # installed_packages_in_pipfile with current version
    installed_packages_in_pipfile = {
        package["name"]: {"current": package["version"]}
        for package in installed_packages
        if package["name"] in pipfile_packages
    }

    # uninstalled packages
    for package in pipfile_packages:
        if package not in installed_packages_in_pipfile:
            installed_packages_in_pipfile[package] = {"current": "not installed"}

    version_len = (
            max(
                [
                    len(package["current"])
                    for package in installed_packages_in_pipfile.values()
                ]
            )
            + 1
    )

    def get_latest_version(package_name):
        data = urlopen(f"https://pypi.org/pypi/{package_name}/json").read()
        r = json.loads(data.decode("utf-8"))
        version = r["info"]["version"]
        return version

    pool = ThreadPool()
    latest_versions = pool.map(get_latest_version, installed_packages_in_pipfile)
    pool.close()
    pool.join()

    for package_name, latest_version in zip(installed_packages_in_pipfile.keys(), latest_versions):
        installed_packages_in_pipfile[package_name]["latest"] = latest_version

    # group packages by major, minor and bug fix update
    packages_by_update = {
        "not installed": [],
        "major": [],
        "minor": [],
        "bugfix": [],
        "up to date": [],
    }

    for package_name, versions in installed_packages_in_pipfile.items():
        current_version = versions["current"]
        latest_version = versions["latest"]
        if current_version == "not installed":
            packages_by_update["not installed"].append(package_name)
        elif current_version != latest_version:
            current_version = current_version.split(".")
            latest_version = latest_version.split(".")
            if current_version[0] != latest_version[0]:
                packages_by_update["major"].append(package_name)
            elif current_version[1] != latest_version[1]:
                packages_by_update["minor"].append(package_name)
            elif current_version[2] != latest_version[2]:
                packages_by_update["bugfix"].append(package_name)
        else:
            packages_by_update["up to date"].append(package_name)

    for update_type, packages in packages_by_update.items():
        if packages:
            color_print(
                "{title:<{len}} {cur:<{len_ver}} {latest:<{len_ver}} {url}".format(
                    title=update_type.title(),
                    len=package_name_len,
                    cur="Current",
                    len_ver=version_len,
                    latest="Latest",
                    url="Url",
                ),
                BColors.OKGREEN if update_type == "up to date" else BColors.FAIL,
                False if update_type == "up to date" else True,
            )
            for package_name in packages:
                print(
                    "{title:<{len}} {cur:<{len_ver}} {latest:<{len_ver}} {url}".format(
                        title=package_name,
                        len=package_name_len,
                        cur=installed_packages_in_pipfile[package_name]["current"],
                        len_ver=version_len,
                        latest=installed_packages_in_pipfile[package_name]["latest"]
                        if update_type != "up to date"
                        else installed_packages_in_pipfile[package_name]["current"],
                        url=f"https://pypi.org/project/{package_name}",
                    )
                )
            if update_type != "up to date":
                print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass