from typing import Optional, Dict
from datetime import datetime

from .space_task import SpaceTask
from ...codable import KeyDescriptor
from ...networking import NetworkObject


class BaseObject(NetworkObject):

    """
        Represents the base class for Space/Project objects from Coretex.ai

        Properties
        ----------
        name : str
            name of object
        description : Optional[str]
            description of object
        createdOn : datetime
            date of creation of object
        createdById : str
            id of user that created object
        spaceTask : SpaceTask
            space task of created object
    """

    name: str
    description: Optional[str]
    createdOn: datetime
    createdById: str
    spaceTask: SpaceTask

    @classmethod
    def _endpoint(cls) -> str:
        return "project"

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()
        descriptors["spaceTask"] = KeyDescriptor("project_task", SpaceTask)

        return descriptors

    def rename(self, name: str) -> bool:
        """
            Renames the Space/Project

            Parameters
            ----------
            name : str
                new name

            Returns
            -------
            bool -> True if Space/Project was renamed, False if Space/Project was not renamed
        """

        if self.name == name:
            return False

        success = self.update(
            parameters = {
                "name": name
            }
        )

        if success:
            self.name = name

        return success

    def updateDescription(self, description: str) -> bool:
        """
            Updates the Space/Project's description

            Parameters
            ----------
            description : str
                new description

            Returns
                bool -> True if Space/Project's description was updated,
                False if Space/Project's description was not updated
        """

        if self.description == description:
            return False

        success = self.update(
            parameters = {
                "description": description
            }
        )

        if success:
            self.description = description

        return success
