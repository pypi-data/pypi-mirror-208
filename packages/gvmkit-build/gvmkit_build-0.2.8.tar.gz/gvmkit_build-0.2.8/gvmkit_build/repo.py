import hashlib
import io

import requests
from alive_progress import alive_bar
from termcolor import cprint
from typing.io import BinaryIO
import srvlookup


def resolve_repo(domain="dev.golem.network") -> str:
    for record in srvlookup.lookup("girepo", domain=domain):
        try:
            base_url = f"http://{record.host}:{record.port}"
            resp = requests.get(f"{base_url}/status", timeout=1.0)
            if resp.status_code == 200:
                return base_url
        except requests.RequestException:
            pass

    raise RuntimeError("unable to resolve default repo")


def upload_image(file_obj: BinaryIO, file_name: str):

    file_size = file_obj.seek(0, io.SEEK_END)
    hasher = hashlib.sha3_224()
    assert file_obj.seek(0, io.SEEK_SET) == 0

    def chunks(bar, chunk_size=1024 * 1024):
        chunk = file_obj.read(chunk_size)
        while chunk:
            hasher.update(chunk)
            yield chunk
            bar(incr=len(chunk))
            chunk = file_obj.read(chunk_size)

    repo_url = resolve_repo()
    with alive_bar(file_size, title="upload image") as bar:
        resp = requests.put(f"{repo_url}/upload/{file_name}", data=chunks(bar))
        if resp.status_code == 409:
            cprint("image already uploaded", "yellow")
            return
        resp.raise_for_status()

        image_url = f"{repo_url}/{file_name}"
        hash_hex = hasher.hexdigest()
        requests.put(
            f"{repo_url}/upload/image.{hash_hex}.link",
            data=image_url.encode("utf-8"),
        )

        print(f"success. hash link {hash_hex}")
