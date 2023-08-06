import logging

from dql.nodes_thread_pool import NodesThreadPool

logger = logging.getLogger("dql")


class NodesFetcher(NodesThreadPool):
    def __init__(self, client, data_storage, file_path, max_threads, cache):
        super().__init__(max_threads)
        self.client = client
        self.data_storage = data_storage
        self.file_path = file_path
        self.cache = cache

    def done_task(self, done):
        updated_nodes = []
        for d in done:
            lst = d.result()
            for node, md5 in lst:
                self.data_storage.update_checksum(node, md5)
                updated_nodes.append(node._replace(checksum=md5))
        return updated_nodes

    def do_task(self, chunk):
        res = []
        for node in chunk:
            if self.cache.exists(node.checksum):
                self.increase_counter(node.size)
                continue

            pair = self.fetch(self.client.name, node.path_str, node)
            res.append(pair)
        return res

    def fetch(self, bucket, path, node):
        from dvc_data.hashfile.build import _upload_file
        from dvc_objects.fs.callbacks import Callback

        class _CB(Callback):
            def relative_update(  # pylint: disable=no-self-argument
                _, inc: int = 1  # noqa: disable=no-self-argument
            ):
                self.increase_counter(inc)

        _, obj = _upload_file(
            f"{bucket}/{path}",
            self.client.fs,
            self.cache,
            self.cache,
            callback=_CB(),
        )

        return node, obj.hash_info.value
