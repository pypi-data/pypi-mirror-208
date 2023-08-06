from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, validator
from .base import Endpoint
from .utils import convert_image_to_data_uri


class ConnectButton(BaseModel):
    """Style for the connect button."""
    inner_text: str = "Connect"
    button_color: str = "gray"
    button_text_color: str = "white"


class UserColorInfo(BaseModel):
    button_color: str = "red"
    button_text_color: str = "white"


class User(BaseModel):
    user_title: str = "red"
    is_integrate: bool = False
    redirection_url: str = ""

    # Can vary a lot
    input_fields: List[dict] = [
        {
            "input_placeholder": "Phone number",
            "input_id": "phone",
            "input_name": "phone",
            "display_name": "phone_number",
        }
    ]


class Payload(BaseModel):
    """Configuration data related to fields and style of portal.

    Attributes:
        logo: use Base64 encoded data URI scheme.
            https://en.wikipedia.org/wiki/Data_URI_scheme#Syntax
    """
    logo: str = ""  # Pass string filepath
    font_color: str = "black"
    background_color: str = "white"
    pageTitle: str = "Public Wifi"
    terms_title: str = "EULA"
    terms_content: str = ""
    connect_button: ConnectButton = ConnectButton()
    user_color_info: UserColorInfo = UserColorInfo()
    user: List[User] = [User]

    @validator('logo')
    def logo_as_data_uri(cls, v: str) -> str:
        """Convert logo filepath to data URI.

        Validate if Path exists, then convert to.

        Args:
            v: filepath.
        Returns:
            Data URI.
        """
        if v == '':
            return v
        if not Path(v).resolve().exists():
            raise ValueError(
                f'File Does Not Exist: {v}. Provide valid filepath.'
            )
        return convert_image_to_data_uri(v)


class CaptivePortalModel(BaseModel):
    """Model for create or update captive portal."""
    portal_name: str = "Portal"
    redirect_url: str = ""
    validity_time: str = "1440"
    blocked_url: List[str] = None
    payload: Payload = Payload()


class CaptivePortal(Endpoint):
    """Operations related to captive portal endpoint.

    This is considered a sub-endpoint from API point of view.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.url = self.base_url_v2 + '/wifi/api/captive-portal'

    def _parse_pydantic_to_dict(self, _data: Union[BaseModel, dict]) -> dict:
        """Parse pydantic data to dict.

        Args:
            data: data to parse.
        """
        if isinstance(_data, CaptivePortalModel):
            return _data.dict()
        return _data

    def list(self) -> dict:
        """get list of captive portal.

        Returns:
            A list of captive portal.
        """
        d = self.session.req('get', self.url)
        return d

    def get_by_id(self, id: int) -> dict:
        """Obtain a captive portal by id.

        Args:
            id: item id. 1, 2, ... n

        Returns:
            Captive portal data.

        Raises:
            HTTPError:
        """
        url = self.url + f'/{id}'
        d = self.session.req('get', url)
        return d

    def create(self, data: Union[CaptivePortalModel, dict]) -> dict:
        """Create a new portal, requires a complete data structure.

        Args:
            data: data to create.
                Allowed file types jpg, png, svg ,jpeg, refer to official docs.

        Returns:
            A list of captive portal.

        Raises:
            HTTPError:
        """
        data = self._parse_pydantic_to_dict(data)
        d = self.session.req('post', self.url, json=data)
        return d

    def update(self, id: int,
               data: Union[CaptivePortalModel, dict]) -> dict:
        """Update a captive portal by id.

        Args:
            id: item id. 1, 2, ... n
            data: data to update.
                Allowed file types jpg, png, svg ,jpeg, refer to official docs.

        Returns:
            Captive portal data.

        Raises:
            HTTPError:
        """
        url = self.url + f'/{id}'
        data = self._parse_pydantic_to_dict(data)
        d = self.session.req('put', url, json=data)
        return d

    def delete_captive_portal(self, id: int) -> dict:
        """Delete a captive portal by id.

        Args:
            id: item id. 1, 2, ... n

        Returns:
            HTTP 200 with data.

        Raises:
            HTTPError:
        """
        url = self.url + f'/{id}'
        d = self.session.req('delete', url)
        return d


if __name__ == "__main__":
    from pprint import pprint

    # Data example for create or update Captive Portal obtained from API.
    captive = CaptivePortalModel(
        portal_name="API Test 1",
        redirect_url="https://goole.com",
        blocked_url=['https://example.com'],
        validity_time="1440",
        payload=Payload(
            logo="",
            font_color="black",
            background_color="white",
            pageTitle="Public Wifi",
            terms_title="EULA",
            terms_content="lorem ipsum ....",
            connect_button=ConnectButton(
                inner_text="Connect",
                button_color="gray",
                button_text_color="white",
            ),
            user_color_info=UserColorInfo(
                button_color="red",
                button_text_color="white",
            ),
            user=[User()],
        )
    )
    pprint(captive.dict())
