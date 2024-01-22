import os
import subprocess
import sys

repo_name = "dummy"
description = "dummy grep"
version = "1.0.3"
deps = []
debug = False

if not repo_name:
    repo_name = input("Repo name: ")

if not version:
    version = input("Release version: ")

if not description:
    description = input("Description: ")

def exec_command(args, debug=debug):
    if debug:
        return subprocess.run(args)
    else:
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Clone the repository
print("\n-------------------CLONING REPO-------------------\n")
if os.path.exists(repo_name):
    os.chdir(repo_name)
    exec_command(["git", "stash", "--all"])
    exec_command(["gh", "repo", "sync", "--force"])
else:
    exec_command(["gh", "repo", "clone", repo_name])
    os.chdir(repo_name)

print("------------------BUILDING CRATE------------------\n")
# Build the crate
exec_command(["cargo", "build", "--release"])

# Change directory to target/release
os.chdir("target/release")

print("-------------CREATING TARBALL AND HASH------------\n")
# Create a tarball
tar_name = f"{repo_name}-mac.tar.gz"
tar_command = ["tar", "-czf", tar_name, repo_name]
exec_command(tar_command)

# Compute SHA-256 hashsum
hash_command = ["shasum", "-a", "256", tar_name]
hash = subprocess.check_output(hash_command).decode().split()[0]

print("----------------CREATING BREW REPO----------------\n")
# Create a new public repo if it doesn't exist
brew_repo_name = "homebrew-" + repo_name
exec_command(["gh", "repo", "create", brew_repo_name, "--public"])

output = subprocess.check_output(['gh', 'auth', 'status'], text=True)
lines = output.split('\n')
username = next((line.split()[-2] for line in lines if "Logged in to github.com account" in line), None)

print("---------------CREATING NEW RELEASE---------------\n")
# Create a new release with GitHub CLI
title = f"v{version}"
result = exec_command(["gh", "release", "--repo", f"{username}/{repo_name}", "create", "--generate-notes", version, tar_name])
if result.returncode != 0:
    print("Error in creating release, you likely need to bump your version")
    sys.exit(1)

binary_link = f"https://github.com/{username}/{repo_name}/releases/download/{version}/{tar_name}"

def generate_config(repo_name, description, binary_link, hash, version, deps):
    deps_lines = "\n".join([f'depends_on "{dep}"' for dep in deps])
    config = f'''class {repo_name.capitalize()} < Formula
  desc "{description}"
  homepage "https://github.com/{username}/{repo_name}"
  url "{binary_link}"
  sha256 "{hash}"
  version "{version}"

  {deps_lines}

  def install
    bin.install "{repo_name}"
  end
end
'''
    return config

print("--------------UPDATING BREW FORMULA---------------\n")
# Get brew repo and update it
os.chdir("../../../")
if os.path.exists(brew_repo_name):
    os.chdir(brew_repo_name)
else:
    exec_command(["gh", "repo", "clone", brew_repo_name])
    os.chdir(brew_repo_name)

with open("README.md", "w") as f:
    f.write(f"# {repo_name}")

if not os.path.exists("Formula"):
    os.makedirs("Formula")

with open(f"Formula/{repo_name}.rb", "w") as f:
    f.write(generate_config(repo_name, description, binary_link, hash, version, deps))

exec_command(["git", "add", "."])
exec_command(["git", "commit", "-m", "bump version"])
exec_command(["git", "push"])

print("---------------COMPLETED EXECUTION----------------")
