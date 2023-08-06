import base64


def convert_file_to_base64(filename: str) -> str:
    """Convert file to base64 string.

    Args:
        filename: path of file to convert.

    Returns:
        base64 string

    Raises:
    """
    with open(filename, 'rb') as f:
        file_data = f.read()
    _base64_string = base64.b64encode(file_data).decode('utf-8')
    return _base64_string


def image_to_base64(image_file: str, image_type: str) -> str:
    """Convert image to base64 as Data URI.

    Does not verify if file type or extension.

    Args:
        image_file: image file.
        image_type: supported API types as png, svg, jpeg. Refer to api docs.

    Returns:
        Data URI string

    Raises:
    """
    _schema_uri = f'data:image/{image_type};base64,'
    _base64 = convert_file_to_base64(image_file)
    return f'{_schema_uri}{_base64}'


def extract_extension_from_name(filename: str) -> str:
    """Extract extension from filename.

    Args:
        filename: filename.

    Returns:
        Extension string.

    Raises:
    """
    if '.' not in filename:
        raise ValueError('Filename must have extension.')
    return filename.split('.')[-1]


def convert_image_to_data_uri(image_file: str) -> str:
    """Detect image type and convert to base64 as Data URI.

    Args:
        image_file: image file. Must provide accepted extension image type.

    Returns:
        Data URI string "data:image/<IMAGE_TYPE>;base64,iVBORw0KGgoAAAAN...
    """
    _extension = extract_extension_from_name(image_file)
    return image_to_base64(image_file, _extension)
