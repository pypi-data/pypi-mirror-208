import os
from git import Repo


def make_clone(main_dir, project_name):
    new_project_empl = main_dir + "/" + project_name
    os.mkdir(new_project_empl)

    git_url = "https://github.com/Proxia-ai/template_vierge.git"

    Repo.clone_from(git_url, new_project_empl)
    return True


if __name__ == "__main__":
    main_dir = "/home/zied/PycharmProjects"
    project_name = "data_loader"
    make_clone(main_dir, project_name)
