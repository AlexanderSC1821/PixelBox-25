def create_header(fileName: str, projectName: str, author: str, date: str, lastUpdate: str, version: str, summary: str) -> str:

    header = f"""\
# =====================================================================
#                   {projectName} - {fileName}
#   {fileName}
#   {projectName}
#   Author: {author}
#   Date: {date}
#   Last Update: {lastUpdate}
#   Version: {version}
#   Summary: {summary}
# =====================================================================
"""

    return header 


header = create_header(
    fileName="grid_draw_pixelbox.py",
    projectName="Pixelbox",
    author="Alex Closson",
    date="09/08/2025",
    lastUpdate="09/08/2025",
    version="1.0.0",
    summary="File to use GUI to draw on LED matrix with touchscreen."
)

def modify_file_with_header(file_path: str, header: str):
    with open(file_path, 'r') as file:
        original_content = file.read()

    with open(file_path, 'w') as file:
        file.write(header + '\n\n' + original_content)

modify_file_with_header('GUI_LED/grid_draw_pixelbox.py', header)