import subprocess

def install_jupyter():
    try:
        subprocess.check_call(['pip', 'install', 'jupyter'])
        print("Jupyter installed successfully!")
    except subprocess.CalledProcessError:
        print("Error occurred while installing Jupyter.")

if __name__ == "__main__":
    install_jupyter()
