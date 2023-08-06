from typing import Optional, Any, List, Dict
from typing_extensions import Self

from .base import BaseObject
from .project import Project
from .space_task import SpaceTask


class Space(BaseObject):

    """
        Represents the space entity from Coretex.ai\n
        Contains properties that describe the space
    """

    projects: List[Project]

    @classmethod
    def createSpace(cls, name: str, spaceTask: SpaceTask, description: Optional[str] = None) -> Optional[Self]:
        """
            Creates a new space with the provided name and description

            Parameters
            ----------
            name : str
                space name
            description : Optional[str]
                space description

            Returns
            -------
            Optional[Self] -> The created space object

            Example
            -------
            >>> from coretex import Space, SpaceTask
            \b
            >>> dummySpace = Space.createSpace(
                    name = "dummySpace",
                    spaceTask = SpaceTask.other,
                    description = "This is dummy Coretex Space"
                )
            >>> if dummySpace is None:
                    print("Failed to create space")
        """

        return cls.create(parameters={
            "name": name,
            "project_task": spaceTask.value,
            "description": description
        })

    @classmethod
    def decode(cls, encodedObject: Dict[str, Any]) -> Self:
        obj = super().decode(encodedObject)
        obj.projects = Project.fetchAll(queryParameters=[
            f"parentId={obj.id}"
        ])

        return obj

    def addProject(self, name: str, description: Optional[str]) -> bool:
        """
            Adds new project to the space

            Parameters
            ----------
            name : str
                project name
            description : Optional[str]
                project description

            Returns
            -------
            bool -> True if the project was added. False if the project was not added
        """

        project = Project.createProject(name, self.id, description)
        if project is None:
            return False

        self.projects.append(project)
        return True
