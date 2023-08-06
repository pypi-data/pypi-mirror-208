import os
import site

site_package_url = site.getsitepackages()[0]
main_script = "cookiestream/src/stream.py"


def main():
    try:
        os.system('streamlit run cookiestream/src/stream.py')
    except:
        os.system('streamlit run {}/{}'.format(site_package_url, main_script))


if __name__ == '__main__':
    main()
