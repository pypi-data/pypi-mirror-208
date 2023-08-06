import re
import sys


def convert_latex(content):
    try:
        pattern1 = r"\$\$\n*([\s\S]*?)\n*\$\$"
        new_pattern1 = r'\n<img src="https://www.zhihu.com/equation?tex=\1" alt="\1" class="ee_img tr_noresize" eeimg="1">\n'
        pattern2 = r"\$\n*(.*?)\n*\$"
        new_pattern2 = r'\n<img src="https://www.zhihu.com/equation?tex=\1" alt="\1" class="ee_img tr_noresize" eeimg="1">\n'
        new_lines1 = re.sub(pattern1, new_pattern1, content)
        new_content = re.sub(pattern2, new_pattern2, new_lines1)
        return new_content
    except Exception as e:
        print(e)

def main():
    if len(sys.argv) < 2:
        print("need file name")
        sys.exit(1)
    file_name = sys.argv[1]
    # file_name = "极大似然小结.md".decode('utf-8')
    file_name_pre = file_name.split(".")[0]
    output_file_name = file_name_pre + "_zhihu.md"
    with open(file_name, "r", encoding="utf-8") as f, open(
        output_file_name, "w", encoding="utf-8"
    ) as f_output:
        all_lines = f.read()
        new_content = convert_latex(all_lines)
        f_output.write(new_content)

if __name__ == "__main__":
    main()
