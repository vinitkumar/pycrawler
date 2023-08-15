def generate_page_tree(input_urls):
    page_tree = {}

    for url in input_urls:
        parts = url.strip().split("/")[3:]  # Ignore the protocol and domain

        current_level = page_tree
        for part in parts:
            if part.endswith(".html"):
                part = part[:-5]  # Remove the ".html" extension

            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    def convert_to_nested_list(tree):
        nested_list = []
        for key, value in tree.items():
            nested_list.append([key, convert_to_nested_list(value)])
        return nested_list

    return convert_to_nested_list(page_tree)


# Example usage
input_urls = [
    "https://wicherzitsema.nl/index.html",
    "https://wicherzitsema.nl/aanmelden/index.html",
    "https://wicherzitsema.nl/contact/index.html",
    "https://04HO00.mijnschool.nl/mijnschool/index.html",
    "https://www.wicherzitsema.nl/nieuwsbericht/149189154-gratis-naar-het-theater.html",
    "https://www.wicherzitsema.nl/nieuwsbericht/148961925-piep-de-brandweer-rukt-uit-naar-bibliotheek-middelstum.html",
    "https://www.wicherzitsema.nl/nieuwsbericht/148452275-school-kerk-gezinsdienst.html",
    "https://www.wicherzitsema.nl/nieuws/overzicht.html",
    "https://www.wicherzitsema.nl/verlofaanvragen/index.html",
    "https://www.wicherzitsema.nl/vakantiesenvrijedagen2022-2023/index.html",
    "https://www.wicherzitsema.nl/schooltijden/schooltijden.html",
    "https://www.wicherzitsema.nl/mrenor/index.html",
    "https://www.wicherzitsema.nl/hierstaanwijvoor/index.html",
    "https://www.wicherzitsema.nl/onsteam/index.html",
    "https://www.wicherzitsema.nl/onsonderwijs/index.html",
    "https://www.wicherzitsema.nl/aanmelden/aanmelden.html",
    "https://www.wicherzitsema.nl/documenten/documenten1.html",
    "https://www.wicherzitsema.nl/agenda/overzicht.html",
    "https://wicherzitsema.nl/privacy.html",
    "https://wicherzitsema.nl/cookies.html"
]

page_tree = generate_page_tree(input_urls)
print(page_tree)
