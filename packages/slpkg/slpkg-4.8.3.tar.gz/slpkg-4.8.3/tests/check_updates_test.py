import os
from pathlib import Path
from urllib3 import PoolManager

from slpkg.repositories import Repositories


class Check:

    def __init__(self):
        self.repos = Repositories()
        self.repositories = Repositories().repositories

    def test(self):
        local_size: int = 0
        for name, data in self.repositories.items():

            local_chg_txt: Path = Path(data['path'], 'ChangeLog.txt')
            repo_chg_txt: str = f"{data['mirror'][0]}ChangeLog.txt"

            http = PoolManager()
            repo = http.request('GET', repo_chg_txt)
            repo_size: int = int(repo.headers['Content-Length'])

            if local_chg_txt.is_file():
                local_size: int = int(os.stat(local_chg_txt).st_size)

            print(f'{name=} = {local_size=}, {repo_size=}, {local_size != repo_size}')


if __name__ == "__main__":
    check = Check()
    check.test()
