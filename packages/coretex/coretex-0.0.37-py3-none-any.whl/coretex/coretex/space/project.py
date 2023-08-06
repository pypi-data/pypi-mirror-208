from typing import Optional, Dict
from typing_extensions import Self

from .base import BaseObject
from ...codable import KeyDescriptor


class Project(BaseObject):

    """
        Represents the project entity from Coretex.ai\n
        Contains properties that describe the project
    """

    isDefault: bool
    projectId: int

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()
        descriptors["projectId"] = KeyDescriptor("parentId")

        return descriptors

    @classmethod
    def createProject(cls, name: str, spaceId: int, description: Optional[str]=None) -> Optional[Self]:
        """
            Creates a new project with the provided name and description
            Project is added to the space with provided space id

            Parameters
            ----------
            name : str
                project name
            spaceId : int
                space id the project belongs to
            description : Optional[str]
                project description

            Returns
            -------
            Optional[Self] -> The created project object

            Example
            -------
            >>> from coretex import Project
            \b
            >>> dummyProject = Project.createProject(
                    name = "dummyProject",
                    spaceId = 23,
                    description = "This is dummy project"
                )
            >>> if dummyProject is None:
                    print("Failed to create project")
        """

        return cls.create(parameters={
            "name": name,
            "parent_id": spaceId,
            "description": description
        })
