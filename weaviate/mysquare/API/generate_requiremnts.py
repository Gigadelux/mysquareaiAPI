import subprocess

def generate_requirements_file():
    with open('requirements.txt', 'w') as f:
        subprocess.run(['pip', 'freeze'], stdout=f)

if __name__ == "__main__":
    generate_requirements_file()
