import sys
import shutil
import os

def deploy(destination):
    folders = [
        'ArtN7',
        'catalog',
    ]
    files = [
        'manage.py',
        'requirements.txt',
        'README.txt',
        'startArtN7.sh'
    ]
    static_folder = 'staticfiles'

    # deletion of old folders and files
    print("\nRemoving old implementation...")
    for folder in folders:
        if os.path.exists(os.path.join(destination, folder)):
            shutil.rmtree(os.path.join(destination, folder))
    for file in files:
        if os.path.exists(os.path.join(destination, file)):
            os.remove(os.path.join(destination, file))
    if os.path.exists(os.path.join(destination, static_folder)):
        shutil.rmtree(os.path.join(destination, static_folder))
    print("Old implementation removed successfully.")

    # coping of new folders and files
    print("\nCopying new implementation...")
    for folder in folders:
        shutil.copytree(f"./{folder}", f"{destination}/{folder}")
    for file in files:
        shutil.copyfile(f"./{file}", f"{destination}/{file}")
    print("New implementation copied successfully.")

    print()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print("Starting deployment...")
        try:
            deploy(sys.argv[1])
            print("Deployment completed!")
        except Exception as e:
            print(f"Failed to deploy: {e}")
    else:
        print("The number of arguments passed to the deployment is incorrect.")