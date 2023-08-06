import os
import sys
import subprocess

def check_r_installation():
    try:
        subprocess.run(["R", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print("R is not installed on this system. Skipping R library installation.")
        return False

def install_r_library():
    print("Installing R library 'WGCNA'...")
    if check_r_installation():
        try:
            subprocess.run(["R", "-e", "install.packages('BiocManager'); BiocManager::install('WGCNA')"], check=True)
            print("R library 'WGCNA' has been installed successfully.")
        except subprocess.CalledProcessError:
            print("An error occurred while installing the R library 'WGCNA'.")
            sys.exit(1)

if __name__ == "__main__":
    install_r_library()
