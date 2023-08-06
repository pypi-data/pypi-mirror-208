import ruamel.yaml


def generate_yaml_template(yaml_file, yaml_data):
    list_with_dics = lambda ll: [{"url" + str(i): val} for i, val in enumerate(ll)]

    yaml = ruamel.yaml.YAML()
    with open(yaml_file) as fp:
        data = yaml.load(fp)

    data[0]["asset_meta_information"]["asset_version"] = yaml_data["asset_version"] if yaml_data[
        "asset_version"] else "0.01"
    data[0]["asset_meta_information"]["asset_name"] = yaml_data["asset_name"] if yaml_data[
        "asset_name"] else "asset_name"
    data[0]["asset_meta_information"]["author"] = yaml_data["author"] if yaml_data[
        "author"] else "author"
    data[0]["asset_meta_information"]["author_email"] = yaml_data["author_email"] if yaml_data[
        "author_email"] else "author@email.com"
    data[0]["asset_meta_information"]["description"] = yaml_data["description"] if yaml_data[
        "description"] else "for some work"
    data[0]["asset_meta_information"]["url"] = yaml_data["url"] if yaml_data[
        "url"] else "https://github.com/pypa/sampleproject"
    data[0]["asset_meta_information"]["keywords"] = yaml_data["keywords"].split(",") if yaml_data[
        "keywords"] else ["key_word1", "key_word2", "key_word3"]
    data[0]["asset_meta_information"]["project_urls"][0] = list_with_dics(yaml_data["project_urls"].split(",")) if \
        yaml_data[
            "project_urls"] else {"url1": "https://github.com/pypa/sampleproject/issues"}
    data[0]["asset_meta_information"]["python_required"] = yaml_data["python_required"] if yaml_data[
        "python_required"] else ">=3.7"
    data[0]["asset_meta_information"]["copyright"] = yaml_data["copyright"] if yaml_data[
        "copyright"] else "2023, Cookiestream"
    data[0]["asset_meta_information"]["license"] = yaml_data["license"] if yaml_data[
        "license"] else "BSD"
    data[0]["asset_meta_information"]["classifiers"] = yaml_data["classifiers"].split(",") if yaml_data[
        "classifiers"] else [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7"]
    data[0]["asset_meta_information"]["long_description_content_type"] = yaml_data["long_description_content_type"] if \
        yaml_data[
            "long_description_content_type"] else "text/markdown"
    data[0]["asset_meta_information"]["long_description"] = yaml_data["long_description"] if \
        yaml_data["long_description"] else "long_description"

    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)

    return True


if __name__ == "__main__":
    yaml_file = "/home/zied/PycharmProjects/data_loader/configs/data_loader_config.yaml"

    generate_yaml_template(yaml_file)
