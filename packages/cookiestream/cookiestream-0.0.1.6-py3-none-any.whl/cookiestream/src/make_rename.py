from utils.util import get_log
import os


@get_log
def find_and_replace_new_project_name(file, project_name):
    # Read in the file
    with open(file, 'r') as file1:
        filedata = file1.read()

    # Replace the target string
    filedata = filedata.replace('template_vierge', project_name)

    # Write the file out again
    with open(file, 'w') as f:
        f.write(filedata)
    return True


@get_log
def rename_all(main_dir, project_name):
    # files
    base_config_file = "{}/configs/base_config.py".format(main_dir)
    yaml_config_file = "{}/configs/template_vierge_config.yaml".format(main_dir)
    exemple_job_file = "{}/template_vierge/src/job_example.py".format(main_dir)
    init_file_for_build = "{}/template_vierge/__init__.py".format(main_dir)
    test_job_default_file = "{}/tests/template_vierge/test_job_example.py".format(main_dir)
    main_file = "{}/main.py".format(main_dir)

    # folders
    default_folder_name = "{}/template_vierge".format(main_dir)
    default_test_folder = "{}/tests/template_vierge".format(main_dir)

    # rename into files
    find_and_replace_new_project_name(base_config_file, project_name)
    find_and_replace_new_project_name(yaml_config_file, project_name)
    find_and_replace_new_project_name(exemple_job_file, project_name)
    find_and_replace_new_project_name(init_file_for_build, project_name)
    find_and_replace_new_project_name(test_job_default_file, project_name)
    find_and_replace_new_project_name(main_file, project_name)

    # rename files
    os.rename(yaml_config_file, '{}/configs/{}_config.yaml'.format(main_dir, project_name))

    # rename folders
    os.rename(default_test_folder, '{}/tests/{}'.format(main_dir, project_name))
    os.rename(default_folder_name, '{}/{}'.format(main_dir, project_name))
    return True


if __name__ == "__main__":
    project_name = "data_loader"
    main_dir = "/home/zied/PycharmProjects" + "/" + project_name

    rename_all(main_dir, project_name)
