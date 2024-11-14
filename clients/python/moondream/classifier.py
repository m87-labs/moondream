from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from PIL import Image
from io import BytesIO
from moondream.utils import BASE_URL, validate_image, API_VERSION
import httpx
import uuid


class Classifier:
    """A client for making image classification requests to the Moondream API.
    Support for local inference is not yet supported, but is coming soon.

    Args:
        api_key (Optional[str]): The API key for authentication. Defaults to None.
        model_endpoint (Optional[str]): Custom model endpoint path. Defaults to None.
        model_path (Optional[str]): Local model path (not supported). Defaults to None.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_endpoint: Optional[str] = None,
        model_path: Optional[str] = None,
    ):
        if model_path:
            raise ValueError(
                "model_path is not yet supported for the classifier models"
            )

        self.api_key = api_key
        self.model_endpoint = model_endpoint
        self.httpx_client = httpx.Client(timeout=20.0)

    def _make_classification_request(
        self, image_buffer: BytesIO
    ) -> List[Dict[str, Any]]:
        """Makes an HTTP request to the classification endpoint.

        Args:
            image_buffer (BytesIO): The image data to be classified.

        Returns:
            List[Dict[str, Any]]: The raw response from the server.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        request_id = str(uuid.uuid4())
        request_files = {"content": (f"{request_id}.jpg", image_buffer, "image/jpeg")}

        request_headers = {
            "X-MD-Auth": self.api_key,
        }

        request_url = f"{BASE_URL}/{API_VERSION}/{self.model_endpoint}"

        response = self.httpx_client.post(
            request_url,
            files=request_files,
            headers=request_headers,
        )
        response.raise_for_status()

        return dict(response.json())

    def classify(
        self,
        image: Union[Image.Image, Path, str],
    ) -> Union[str, List[Dict[str, Any]]]:
        """Classifies the given image using the Moondream API.

        Args:
            image (Union[Image.Image, Path, str]): The image to classify. Can be a PIL Image,
                a path to an image file, or a base64 encoded image string.

        Returns:
            Union[str, List[Dict[str, Any]]]:
            If you are using an expert model, the result will be a string of the predicted class.
            If you are using a distilled model, the result will be a list of dictionaries in the format...
                {"answer": [{"label": str, "confidence": float}]}. In descending order of confidence.
        """
        if not self.model_endpoint:
            raise ValueError(
                "model_endpoint must be provided to use the classify method."
            )

        validated_image = validate_image(image)

        server_response = self._make_classification_request(validated_image)
        return {"answer": server_response["result"]}
