from requests import get
from bs4 import BeautifulSoup


def count_lines(items, bl_files):
    lines = 0
    file_types = [".py", ".c", ".cgi", ".class", ".cpp", ".cs", ".h", ".hpp", ".java", ".php", ".sh", ".swift", ".vb",
                  ".js", ".css", ".cc", ".o", ".sass", ".asm", ".s", ".swift", ".bat", ".go", ".rb", ".ps1", ".cxx",
                  ".hxx", ".hh"]

    for item in items:
        file_name = item['href'].split("/")[-1]

        if "." not in file_name:
            continue

        if item['title'] in bl_files or file_name[file_name.index("."):] not in file_types:
            continue

        try:
            req = get("https://github.com" + item["href"]).content.decode()
            start = req.index("lines") - 5
            lines += int(req[start:start + 5])

        except Exception as e:
            print(e)
            pass

    return lines


def get_items(repo, bl_folders):
    print("Started counting...")

    def find(typ, soup):
        all_folders = soup.find_all('a', href=True, class_="js-navigation-open link-gray-dark")
        all_items = soup.find_all('a', href=True, class_="js-navigation-open link-gray-dark")

        if typ == "folder":
            return [x for x in all_folders if "tree" in x['href'].lower()]
        elif typ == "item":
            return [x for x in all_items if "blob" in x['href'].lower()]

    repo_soup = BeautifulSoup(get(repo).content, 'html.parser')

    folders = find("folder", repo_soup)
    items_to_get = find("item", repo_soup)

    while len(folders):
        for folder in folders:
            if folder["title"] in bl_folders:
                folders.remove(folder)
                continue

            folder_soup = BeautifulSoup(get("https://github.com/" + folder['href']).content, 'html.parser')
            folders_in_folder = find("folder", folder_soup)
            items_in_folder = find("item", folder_soup)

            for ff in folders_in_folder:
                if ff not in folders:
                    folders.append(ff)

            for it in items_in_folder:
                if it not in items_to_get:
                    items_to_get.append(it)

            folders.remove(folder)
    return items_to_get


url = input("Please enter URL of the repository:\n")
blacklist_folders = input("Please enter folders you want to exclude (Separated by spaces):\n").split()
blacklist_files = input("Please enter files you want to exclude (Separated by spaces):\n").split()
print(f'{url.split("/")[-1]} consists of', count_lines(get_items(url, blacklist_folders), blacklist_files),
      "Lines of Code.")
