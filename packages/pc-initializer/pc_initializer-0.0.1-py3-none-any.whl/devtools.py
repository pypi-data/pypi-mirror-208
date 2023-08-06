import os
import requests, zipfile, tarfile, io
import logging

from util.util import Util
from util.config_reader import ConfigReader
from util.github_repo import GithubRepo

class Devtools:
    @staticmethod
    def download_devtools(args):
        config = ConfigReader.get(args)

        output_dir = config['output-dir']
        if config['subdir']:
            output_dir = os.path.join(output_dir, 'devtools')

        dry_run = config['dry-run']
        
        gr = GithubRepo(args)
        data = gr.get_json(config['config-file'])

        content = []

        for name in data:
            devtool = data[name]

            main_version = devtool["main_version"]
            versions = []
            if "additional_versions" in devtool:
                versions.extend(devtool["additional_versions"])

            versions.append(main_version)

            for version in versions:
                url = devtool["url"].replace("$version", version)

                if "subdir" in devtool:
                    dev_dir = devtool["subdir"].replace("$version", version)
                else:
                    dev_dir = url.rsplit('/', 1)[-1].replace('.tar.gz', '').replace('.zip', '')

                extract_dir = os.path.join(output_dir, name)
                source_dir = os.path.join(extract_dir, dev_dir)
                dest_dir = os.path.join(extract_dir, version)

                if 'no_subfolder' in devtool and devtool['no_subfolder']:
                    extract_dir = os.path.join(extract_dir, dev_dir)
                    source_dir = extract_dir

                if dry_run:
                    logging.info(f"Dry run active. Would download the tool to {dest_dir}")
                else:
                    if not os.path.isdir(dest_dir):
                        logging.info(f"Download: {name} {version} to {dest_dir}")

                        r = requests.get(url, stream=True)

                        if devtool["type"] == "zip":
                            z = zipfile.ZipFile(io.BytesIO(r.content))
                            z.extractall(extract_dir)
                        elif devtool["type"] == "tar":
                            file = tarfile.open(fileobj=r.raw, mode="r|gz")
                            file.extractall(path=extract_dir)

                        os.rename(source_dir, dest_dir)

                        logging.info(f"Downloaded: {name} {version} to {dest_dir}")
                    else:
                        logging.info(f"{name} {version} already exists in {dest_dir}")

                
            name_version = f"{name.upper()}_VERSION"
            f"${name_version}"
            devtool_dir = extract_dir.replace(main_version, f"${name_version}")
            executable_path = f"{devtool_dir}/bin"
            content.append(f"export {name_version}={main_version}")
            content.append(f"export PATH={executable_path}:$PATH")
            content.append("")
                
        content = '\n'.join(content)

        env_output_dir = os.environ['ENV_FOLDER'] if 'ENV_FOLDER' in os.environ else output_dir
        env_file = os.path.join(env_output_dir, "env_devtools.sh")
        if dry_run:
            logging.info(f'Dry run active. Would create env file at {env_file}')
            print(content)
        else:
            logging.info(f'Create env file at {env_file}')
            Util.create_dir(env_output_dir)
            with open(env_file, "w+") as file:
                file.write(content)
