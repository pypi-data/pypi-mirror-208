# prendre les meta champs du user par streamlit OK
# clone template  OK
# make_rename  OK
# prendre les champs du yaml par streamlit  OK
# modify yaml content script  OK
# à faire ne V2
# facultatif: prendre les params du Makefile (à voir dans la v2)
# message de confirmation à l'utilisateur (suite aux tests unitaires facultatifs, peut etre en v2)

import sys

sys.path.insert(0, "./")

# cookiestream.src.
from cookiestream.src.modify_yaml_content import generate_yaml_template
from cookiestream.src.clone_template import make_clone
from cookiestream.src.make_rename import rename_all

import streamlit as st

st.set_page_config(
    page_title="Create CI Template",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.empty()

with col2:
    st.header("# Cookiestream Template Generator")

    st.subheader("Meta information")
    asset_name = st.text_input("Asset name", "asset_name")
    asset_type = st.selectbox("Asset type", ("Python-based template", "Docker-based template"))
    project_empl = st.text_input("Project emplacement", "/home/zied/PycharmProjects")

    st.subheader("Project information")
    asset_version = st.text_input("Asset Version", "0.0.1")
    author = st.text_input("Author", "author")
    author_email = st.text_input("Author_email", "author@email.com")
    description = st.text_input("Short description", "for some work")
    url = st.text_input("Project url", "https://github.com/pypa/sampleproject")
    keywords = st.text_input("Keywords", "key_word1,key_word2,key_word3",
                             placeholder="separate keywords by gomma and without any space")
    project_urls = st.text_input("Project associated urls", "https://github.com/pypa/sampleproject/issues",
                                 placeholder="separate values by gomma and without any space")
    python_required = st.text_input("Python_required", ">=3.7")
    copyright_ = st.text_input("Copyright", "2023, Cookiestream")
    license_ = st.text_input("License", "BSD")
    classifiers_default_values = \
        "Programming Language :: Python :: 3," \
        "License :: OSI Approved :: MIT License," \
        "Operating System :: OS Independent," \
        "Topic :: Software Development :: Build Tools," \
        "Development Status :: 3 - Alpha,Intended Audience :: Developers," \
        "Programming Language :: Python :: 3.7"
    classifiers = st.text_area("Classifiers", classifiers_default_values)
    long_description_content_type = st.text_input("Long description content type", "text/markdown")
    long_description = st.text_area("Long description", "Your readMe.md content goes here")

    yaml_data = {
        "asset_version": asset_version,
        "asset_name": asset_name,
        "author": author,
        "author_email": author_email,
        "description": description,
        "url": url,
        "keywords": keywords,
        "project_urls": project_urls,
        "python_required": python_required,
        "copyright": copyright_,
        "license": license_,
        "classifiers": classifiers_default_values,
        "long_description_content_type": long_description_content_type,
        "long_description": long_description,
    }
    if st.button("Generate Template"):
        # make clone
        make_clone(project_empl, asset_name)
        # rename all names
        main_dir = project_empl + "/" + asset_name
        rename_all(main_dir, asset_name)
        yaml_file = project_empl + "/{}/configs/{}_config.yaml".format(asset_name, asset_name)
        # Genrate yaml configuration file
        generate_yaml_template(yaml_file, yaml_data)
        # Display sucess
        st.success('Done ..', icon="✅")
    with col3:
        st.empty()
