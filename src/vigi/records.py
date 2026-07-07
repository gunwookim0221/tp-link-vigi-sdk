"""Recording service placeholders."""

from vigi.models import RecordFile, RecordSearchQuery


class RecordService:
    """Placeholder for documented recording search APIs."""

    def search(self, query: RecordSearchQuery) -> list[RecordFile]:
        """Search recordings through a future documented OpenAPI flow."""

        raise NotImplementedError("Recording search is planned for Phase 4.")
