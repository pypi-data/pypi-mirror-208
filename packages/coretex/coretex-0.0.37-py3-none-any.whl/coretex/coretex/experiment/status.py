from enum import IntEnum


class ExperimentStatus(IntEnum):

    """
        List of possible Experiment statuses during the Experiment lifetime
    """

    queued = 1
    preparingToStart = 2
    inProgress = 3
    completedWithSuccess = 4
    completedWithError = 5
    stopped = 6
    stopping = 7
    startRequested = 8
    stopRequested = 9

    @property
    def defaultMessage(self) -> str:
        """
            List of supported statuses:
            - preparingToStart : Experiment preparing to start
            - completedWithSuccess : Experiment is completed without errors
            - completedWithError : Experiment is completed with error
            - stopped : Experiment is stopped manually
            - stopping : Experiment is stopping

            Returns
            -------
            str -> Appropriate message based on Experiment status

            Raises
            ------
            ValueError -> if unsupported status is provided
        """

        if self == ExperimentStatus.preparingToStart:
            return "Preparing to start the experiment."

        if self == ExperimentStatus.completedWithSuccess:
            return "Experiment completed successfully."

        if self == ExperimentStatus.completedWithError:
            return "Experiment execution was interrupted due to an error. View experiment console for more details."

        if self == ExperimentStatus.stopped:
            return "Experiment execution was stopped by request from the user."

        if self == ExperimentStatus.stopping:
            return "Stopping the experiment."

        raise ValueError(f">> [Coretex] {self.name} has no default message")

    @property
    def isFinal(self) -> bool:
        """
            List of final statuses:
            - ExperimentStatus.completedWithSuccess : Experiment finished without error
            - ExperimentStatus.completedWithError : Experiment finished with an error
            - ExperimentStatus.stopped : Experiment is manually stopped

            Returns
            -------
            bool -> True if a status is a final status for a experiment
        """

        return (
                self == ExperimentStatus.completedWithSuccess or
                self == ExperimentStatus.completedWithError or
                self == ExperimentStatus.stopped
        )
