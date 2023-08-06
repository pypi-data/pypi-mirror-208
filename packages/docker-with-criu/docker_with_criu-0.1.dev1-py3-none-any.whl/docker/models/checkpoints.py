from ..errors import CheckpointNotFound
from .resource import Collection
from .resource import Model


class Checkpoint(Model):
    id_attribute = 'Name'

    @property
    def short_id(self):
        return self.id

    def remove(self):
        return self.client.api.container_remove_checkpoint(
            self.collection.container_id,
            checkpoint=self.id,
            checkpoint_dir=self.collection.checkpoint_dir,
        )

    def __eq__(self, other):
        if isinstance(other, Checkpoint):
            return self.id == other.id
        return self.id == other


class CheckpointCollection(Collection):
    """(Experimental)."""
    model = Checkpoint

    def __init__(self, container_id, checkpoint_dir=None, **kwargs):
        #: The client pointing at the server that this collection of objects
        #: is on.
        super().__init__(**kwargs)
        self.container_id = container_id
        self.checkpoint_dir = checkpoint_dir

    def create(self, checkpoint_id, **kwargs):
        self.client.api.container_create_checkpoint(
            self.container_id,
            checkpoint=checkpoint_id,
            checkpoint_dir=self.checkpoint_dir,
            **kwargs,
        )
        return Checkpoint(
            attrs={"Name": checkpoint_id},
            client=self.client,
            collection=self
        )

    def get(self, checkpoint_id):
        checkpoints = self.list()

        for checkpoint in checkpoints:
            if checkpoint == checkpoint_id:
                return checkpoint

        raise CheckpointNotFound(
            f"Checkpoint with id={checkpoint_id} does not exist"
            f" in checkpoint_dir={self.checkpoint_dir}"
        )

    def list(self):
        resp = self.client.api.container_checkpoints(
            self.container_id, checkpoint_dir=self.checkpoint_dir
        )
        return [self.prepare_model(checkpoint) for checkpoint in resp or []]

    def prune(self):
        for checkpoint in self.list():
            checkpoint.remove()
