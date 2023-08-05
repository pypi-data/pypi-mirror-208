from __future__ import annotations

import logging
import pathlib
from typing import TYPE_CHECKING

from great_expectations.core.batch import BatchDefinition
from great_expectations.core.id_dict import IDDict
from great_expectations.datasource.fluent.constants import (
    _DATA_CONNECTOR_NAME,
)
from great_expectations.datasource.fluent.file_path_data_asset import _FilePathDataAsset

if TYPE_CHECKING:
    from great_expectations.datasource.fluent.batch_request import (
        BatchRequest,
    )

logger = logging.getLogger(__name__)


class _DirectoryDataAsset(_FilePathDataAsset):
    """Used for accessing all the files in a directory as a single batch."""

    data_directory: pathlib.Path

    def _get_batch_definition_list(
        self, batch_request: BatchRequest
    ) -> list[BatchDefinition]:
        """Generate a batch definition list from a given batch request, handling a splitter config if present.

        Args:
            batch_request: Batch request used to generate batch definitions.

        Returns:
            List of batch definitions, in the case of a _DirectoryDataAsset the list contains a single item.
        """
        if self.splitter:
            # Currently non-sql asset splitters do not introspect the datasource for available
            # batches and only return a single batch based on specified batch_identifiers.
            batch_identifiers = batch_request.options
            if not batch_identifiers.get("path"):
                batch_identifiers["path"] = self.data_directory

            batch_definition = BatchDefinition(
                datasource_name=self._data_connector.datasource_name,
                data_connector_name=_DATA_CONNECTOR_NAME,
                data_asset_name=self._data_connector.data_asset_name,
                batch_identifiers=IDDict(batch_identifiers),
            )
            batch_definition_list = [batch_definition]
        else:
            batch_definition_list = self._data_connector.get_batch_definition_list(
                batch_request=batch_request
            )
        return batch_definition_list

    def _get_reader_method(self) -> str:
        raise NotImplementedError(
            """One needs to explicitly provide "reader_method" for File-Path style DataAsset extensions as temporary \
work-around, until "type" naming convention and method for obtaining 'reader_method' from it are established."""
        )

    def _get_reader_options_include(self) -> set[str]:
        raise NotImplementedError(
            """One needs to explicitly provide set(str)-valued reader options for "pydantic.BaseModel.dict()" method \
to use as its "include" directive for File-Path style DataAsset processing."""
        )
