import asyncio


def insert_entries(data_storage, entries):
    """
    Takes a list of entries and inserts them synchronously.

    This assumes that, for every entry in entries, all of its parent
    directories also have an entry.
    """
    entries_by_path = [(tuple(e["path"].split("/")), e) for e in entries]
    entries_by_path.sort(key=lambda e: (len(e[0]), not e[1]["is_dir"]))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        dir_ids = {(): asyncio.run(data_storage.insert_root())}
        for path_parts, entry in entries_by_path:
            entry = {
                **entry,
                "parent_id": dir_ids[path_parts[:-1]],
                "partial_id": 0,
            }
            node_id = loop.run_until_complete(data_storage.insert_entry(entry))
            if entry["is_dir"]:
                dir_ids[path_parts] = node_id
    finally:
        asyncio.set_event_loop(None)
        loop.close()


DEFAULT_TREE = {
    "description": "Cats and Dogs",
    "cats": {
        "cat1": "meow",
        "cat2": "mrow",
    },
    "dogs": {
        "dog1": "woof",
        "dog2": "arf",
        "dog3": "bark",
        "others": {"dog4": "ruff"},
    },
}


def instantiate_tree(path, tree):
    for key, value in tree.items():
        if isinstance(value, str):
            (path / key).write_text(value)
        elif isinstance(value, dict):
            (path / key).mkdir()
            instantiate_tree(path / key, value)
        else:
            raise TypeError(f"{value=}")


def tree_from_path(path):
    tree = {}
    for child in path.iterdir():
        if child.is_dir():
            tree[child.name] = tree_from_path(child)
        else:
            tree[child.name] = child.read_text()
    return tree


def uppercase_scheme(uri: str) -> str:
    """
    Makes scheme (or protocol) of an url uppercased
    e.g s3://bucket_name -> S3://bucket_name
    """
    return f'{uri.split(":")[0].upper()}:{":".join(uri.split(":")[1:])}'
