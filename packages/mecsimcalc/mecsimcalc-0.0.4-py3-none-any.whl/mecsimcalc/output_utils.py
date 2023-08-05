import matplotlib.pyplot as plt
import matplotlib.figure as figure
from PIL import Image
import base64
import io
import pandas as pd
from typing import Tuple, Union, List


def print_dataframe(
    df: pd.DataFrame,
    download: bool = False,
    DownloadText: str = "Download Table",
    DownloadFileName: str = "myfile",
    FileType: str = "csv",
) -> Union(str, Tuple[str, str]):
    """
    Creates an HTML table and a download link for a given DataFrame

    Args:
        df (pandas.DataFrame): DataFrame to be converted
        download (bool, optional): If True, function returns a download link (Defaults to False)
        DownloadText (str, optional): Text to be displayed as the download link (Defaults to "Download File")
        DownloadFileName (str, optional): Name of file when downloaded (Defaults to "myfile")
        FileType (str, optional): File type of download (Defaults to "csv")

    Returns:
        str: HTML table (if download is False)
        Tuple[str, str]: HTML table, and download link (if download is True)
    """

    if not download:
        return df.to_html()

    FileType = FileType.lower()

    # check if file type is an alias of excel
    if FileType in {
        "excel",
        "xlsx",
        "xls",
        "xlsm",
        "xlsb",
        "odf",
        "ods",
        "odt",
    }:
        # create excel file and download link
        df.to_excel(f"{DownloadFileName}.xlsx", index=False)
        excel_file = df.to_excel(index=False)
        encoded_data = (
            "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
            + base64.b64encode(excel_file.encode()).decode()
        )
        download_link = f"<a href='{encoded_data}' download='{DownloadFileName}.xlsx'>{DownloadText}</a>"

    # defaults to csv if file type is not excel
    else:
        # create csv file and download link
        df.to_csv(f"{DownloadFileName}.csv", index=False)
        csv_file = df.to_csv(index=False)
        encoded_data = (
            "data:text/csv;base64," + base64.b64encode(csv_file.encode()).decode()
        )
        download_link = f"<a href='{encoded_data}' download='{DownloadFileName}.csv'>{DownloadText}</a>"

    return df.to_html(), download_link


def print_img(
    img: Image.Image,
    metadata: str,
    WIDTH: int = 200,
    HEIGHT: int = 200,
    OriginalSize: bool = False,
    download: bool = False,
    DownloadText: str = "Download Image",
    ImageName: str = "myimg",
) -> Tuple[str, str]:
    """
    Converts a pillow image into an HTML image and a download link

    Args:
        img (PIL.Image.Image): Pillow image
        metadata (str): Image metadata
        WIDTH (int, optional): Output width of the image in pixels (Defaults to 200)
        HEIGHT (int, optional): Output height of the image in pixels (Defaults to 200)
        OriginalSize (bool, optional): If True, the HTML image will be displayed in its original size (Defaults to False)
        download (bool, optional): If True, the download link will be displayed (Defaults to False)
        DownloadText (str, optional): The text to be displayed on the download link (Defaults to "Download Image")
        ImageName (str, optional): download file name (Defaults to 'myimg')

    Returns:
        str: HTML image (if download is False)
        Tuple[str, str]: HTML image, download link (if download is True)
    """

    displayImg = img.copy()

    if not OriginalSize:
        displayImg.thumbnail((WIDTH, HEIGHT))

    # Get downloadable data (Full Resolution)
    buffer = io.BytesIO()
    img.save(buffer, format=img.format)
    encoded_data = metadata + base64.b64encode(buffer.getvalue()).decode()

    # Get displayable data (Custom Resolution)
    displayBuffer = io.BytesIO()

    # It seems tempting to use displayImg.format here, but it doesn't work for some reason
    displayImg.save(displayBuffer, format=img.format)

    # Get the encoded data
    encoded_display_data = (
        metadata + base64.b64encode(displayBuffer.getvalue()).decode()
    )

    # Convert Display image to HTML
    image = f"<img src='{encoded_display_data}'>"

    if not download:
        return image

    # Convert full resolution image to an HTML download link
    downloadLink = f"<a href='{encoded_data}' download='{ImageName}.{img.format}'>{DownloadText}</a>"

    return image, downloadLink


def print_plt(
    plt: plt or figure,
    width: int = 500,
    dpi: int = 100,
    download: bool = False,
    DownloadText: str = "Download Plot",
    DownloadFileName: str = "myplot",
) -> Union[str, Tuple[str, str]]:
    """
    Converts a matplotlib.pyplot or matplotlib.figure into an HTML image tag and
    optionally provides a download link for the image

    Args:
        plt (matplotlib.pyplot or matplotlib.figure): matplotlib plot
        width (int, optional): Width of the image in pixels. Defaults to 500.
        dpi (int, optional): dpi of the image. Defaults to 100.
        download (bool, optional): If True, a download link will be provided. Defaults to False.
        DownloadText (str, optional): The text to be displayed on the download link. Defaults to "Download Plot".
        DownloadFileName (str, optional): The name of the downloaded file. Defaults to 'myplot'.

    Returns:
        str: HTML image (if download is False)
        Tuple[str, str]: HTML image, download link (if download is True)
    """

    # Save plot to a buffer in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=dpi)

    # Close the plot
    if hasattr(plt, "close"):
        plt.close()

    # Convert the buffer to a base64 string
    buffer.seek(0)
    base64_string = "data:image/png;base64," + base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    # Create the html image tag
    html_image = f"<img src='{base64_string}' width='{width}'>"

    if not download:
        return html_image

    # Create the download link
    download_link = f"<a href='{base64_string}' download='{DownloadFileName}.png'>{DownloadText}</a>"

    return html_image, download_link


def download_text(
    text: str,
    filename: str = "myfile",
    extension: str = ".txt",
    download_text: str = "Download File",
) -> str:
    """
    Generates a downloadable text file containing the given text

    Args:
        text (str): Text to be downloaded
        filename (str, optional): Name of the download file. (Defaults to "myfile")
        extension (str, optional): Extension of the download file. (Defaults to ".txt")
        download_text (str, optional): Text to be displayed as the download link (Defaults to "Download File")

    Returns:
        str: HTML text download link
    """

    # Add a dot to the extension if it doesn't have one
    if extension[0] != "." and extension != "":
        extension = f".{extension}"

    # Encode the text
    newdata = base64.b64encode(text.encode()).decode()
    meta = "data:text/plain;base64,"
    encoded_data = meta + newdata

    # Return the download link
    return (
        f"<a href='{encoded_data}' download='{filename}{extension}'>{download_text}</a>"
    )


def print_table(columns: List[List[str]], column_headers: List[str]) -> str:
    """
    Creates an HTML table from given columns and column headers.

    Args:
        columns (List[List[str]]): A list of columns (each column is a list of strings) (columns are the vertical data)
        column_headers (List[str]): The header for each column
    Returns:
        str: HTML table
    """

    # Create the header row
    header_row = (
        "<tr>" + "".join(f"<th>{header}</th>" for header in column_headers) + "</tr>"
    )

    # Create the data rows
    rows = len(columns[0])
    data_rows = "".join(
        "<tr>" + "".join(f"<td>{str(column[i])}</td>" for column in columns) + "</tr>"
        for i in range(rows)
    )

    # Return the table
    return f"<table border='3' cellpadding='5' style='border-collapse:collapse;'>{header_row}{data_rows}</table>"
