# from .token import Token
# from .transcription import Transcription
# from .utils import getTxtFilePath
# from ..coretex import CustomSample


# def loadTxtSample(sample: CustomSample) -> Transcription:
#     """
#         Tokenizes text sample

#         Parameters
#         ----------
#         sample : CustomSample
#         sample to be tokenized

#         Returns
#         -------
#         Transcription -> text and a list of tokens contained in the text

#         Raises
#         ------
#         ValueError -> if provided sample is not a valid text sample
#     """

#     path = getTxtFilePath(sample)
#     if path is None:
#         raise ValueError(f">> [Coretex] {sample.name} does not contain a valid txt file")

#     with path.open("r") as txtFile:
#         text = "\n".join(txtFile.readlines()).strip()

#     return Transcription.create(text, Token.fromText(text))
