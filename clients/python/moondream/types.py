import numpy as np
from abc import ABC, abstractmethod
from PIL import Image
from dataclasses import dataclass
from typing import Generator, List, TypedDict, Union, Optional, Literal


@dataclass
class EncodedImage(ABC):
    @abstractmethod
    def get_format(self) -> str:
        """Returns the format of the encoded image."""
        pass


@dataclass
class OnnxEncodedImage(EncodedImage):
    pos: int
    kv_cache: np.ndarray

    def get_format(self) -> str:
        return "onnx"


@dataclass
class Base64EncodedImage(EncodedImage):
    image_url: str

    def get_format(self) -> str:
        return "base64"


SamplingSettings = TypedDict(
    "SamplingSettings",
    {"max_tokens": int},
    total=False,
)

CaptionOutput = TypedDict(
    "CaptionOutput", {"caption": Union[str, Generator[str, None, None]]}
)

QueryOutput = TypedDict(
    "QueryOutput", {"answer": Union[str, Generator[str, None, None]]}
)

Region = TypedDict(
    "Region", {"x_min": float, "y_min": float, "x_max": int, "y_max": float}
)
DetectOutput = TypedDict("DetectOutput", {"objects": List[Region]})

Point = TypedDict("Point", {"x": float, "y": float})
PointOutput = TypedDict("PointOutput", {"points": List[Point]})


class VLM(ABC):
    @abstractmethod
    def encode_image(self, image: Union[Image.Image, EncodedImage]) -> EncodedImage:
        """
        Preprocess the image by running it through the model. Only supported for local
        inference.

        This method is useful if the user wants to make multiple queries with the same image.
        The output is not guaranteed to be backward-compatible across version updates,
        and should not be persisted out of band.

        Args:
            image (Image.Image): The input image to be encoded.

        Returns:
            The encoded representation of the image.
        """
        pass

    @abstractmethod
    def caption(
        self,
        image: Union[Image.Image, EncodedImage],
        length: Literal["normal", "short"] = "normal",
        stream: bool = False,
        settings: Optional[SamplingSettings] = None,
    ) -> CaptionOutput:
        """
        Generate a caption for the input image.

        Args:
            image (Union[Image.Image, EncodedImage]): The input image to be captioned.
            length (str): Length of caption to generate. Can be "normal" or "short".
                Defaults to "normal".
            stream (bool): If True, returns a generator that streams the output tokens.
                Defaults to False.
            settings (Optional[SamplingSettings]): Optional settings for the caption
                generation. If not provided, default settings will be used.

        Returns:
            CaptionOutput: A dictionary containing the 'caption' field with either a string
                or generator that yields strings for the caption.
        """
        pass

    @abstractmethod
    def query(
        self,
        image: Union[Image.Image, EncodedImage],
        question: str,
        stream: bool = False,
        settings: Optional[SamplingSettings] = None,
    ) -> QueryOutput:
        """
        Generate an answer to the input question about the input image.

        Args:
            image (Union[Image.Image, EncodedImage]): The input image to be queried.
            question (str): The question to be answered.
            stream (bool): If True, returns a generator that streams the output tokens.
                (default: False)
            settings (Optional[SamplingSettings]): Optional settings for the query
                generation.

        Returns:
            QueryOutput: A dictionary containing the 'answer' field with either a string
                or generator that yields strings for the response.
        """
        pass

    @abstractmethod
    def detect(
        self,
        image: Union[Image.Image, EncodedImage],
        object: str,
    ) -> DetectOutput:
        """
        Detect and localize the specified object in the input image.

        Args:
            image (Union[Image.Image, EncodedImage]): The input image to be analyzed.
            object (str): The object to be detected in the image.

        Returns:
            DetectOutput: A dictionary containing:
                'objects' (List[Region]): List of detected object regions, where each
                    Region has:
                    - x_min (float): Left boundary of detection box
                    - y_min (float): Top boundary of detection box
                    - x_max (float): Right boundary of detection box
                    - y_max (float): Bottom boundary of detection box
        """
        pass
