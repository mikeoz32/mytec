from venv import EnvBuilder

def create_virtual_env(env_dir: str):
    builder = EnvBuilder(system_site_packages=True,symlinks=True, with_pip=True)
    builder.create(env_dir)
