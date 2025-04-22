# Video Intelligent Annotation Lab (VIAL)

## Table of Contents

- [Features](#features)
- [Installation and Running](#installation-and-running)
  - [System Requirements](#system-requirements)
  - [Running the Program](#running-the-program)
- [Packaging into an Executable File](#packaging-into-an-executable-file)
  - [Install Nuitka](#install-nuitka)
  - [Dependencies](#dependencies)
  - [Executing the Packaging](#executing-the-packaging)
  - [Packaging Options Explanation](#packaging-options-explanation)
  - [Customizing Packaging Options](#customizing-packaging-options)
- [Project Structure](#project-structure)
- [Use Case Example: Eye Disease Video Annotation](#use-case-example-eye-disease-video-annotation)
- [Detailed Usage Instructions](#detailed-usage-instructions)
  - [Basic Workflow](#basic-workflow)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
  - [Advanced Feature Settings](#advanced-feature-settings)
- [Input Folder Format Requirements](#input-folder-format-requirements)
  - [Format Description](#format-description)
- [Annotation Data Format](#annotation-data-format)
- [API Support](#api-support)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
- [Notes](#notes)
- [More Information](#more-information)

This is a video dataset annotation program based on PyQt5, specifically designed for annotating videos, and generating AI inference data using large models. The system is named "Video Intelligent Annotation Lab (VIAL)".

## Features

- **Data Management**: Import multi-level folders; the program loads videos and images from each subfolder sequentially.
- **Video Playback**: Supports play/pause, variable speed playback (0.1x-2.0x), progress control, zoom, and reset functions.
- **Video Annotation**: Add labels and descriptions to any segment of the video (e.g., "00:30-00:32: Left eye looks up").
- **Image Viewing**: Supports viewing document images, with zoom in/out, rotation, and page turning.
- **Label Management**: Customize diagnostic label categories, allowing multiple selections or adding custom labels.
- **AI Analysis Integration**: Calls large model APIs to generate analysis results based on annotation descriptions and diagnostic results.
- **Data Formatting**: Saves annotation data and AI analysis results in standard JSONL format.
- **History Tracking**: Supports viewing and modifying previously annotated historical data.
- **Rich Shortcuts**: Provides various keyboard shortcuts to improve annotation efficiency.

## Installation and Running

### System Requirements

- Windows 10 or later operating system (requires internet connection)
- Python 3.8 or higher
- Install required dependencies

```bash
pip install -r requirements.txt
```

### Running the Program

```bash
cd Video_Intelligent_Annotation_Lab
python main.py
```

## Packaging into an Executable File

This project supports packaging Python code into a standalone Windows executable file (EXE) using Nuitka, allowing users to run it without installing a Python environment.

### Install Nuitka

```bash
pip install nuitka
```

### Dependencies

- Install Visual C++ Build Tools (downloadable from the official Microsoft website)
- Ensure all project dependencies are installed: `pip install -r requirements.txt`

### Executing the Packaging

1. In the project directory (**Note: The project directory path must be entirely in English, without any Chinese characters, otherwise packaging will fail**), use the provided `build.bat` script:

```bash
cd Video_Intelligent_Annotation_Lab
build.bat
```

2. The packaging process may take a few minutes. Upon completion, the `main.exe` executable file will be generated in the `dist` directory.
3. The generated EXE file includes all dependencies and can be directly distributed to end-users.

### Packaging Options Explanation

The current `build.bat` script configuration is as follows:

- `--onefile`: Generate a single standalone executable file.
- `--enable-plugin=pyqt5`: Enable PyQt5 plugin support.
- `--windows-icon-from-ico=logo.ico`: Set the application icon.
- `--include-data-dir=config=config`: Include the configuration file directory.
- `--output-dir=dist`: Set the output directory to `dist`.

### Customizing Packaging Options

You can modify the `build.bat` script to adjust parameters as needed:

- Add `--windows-console-mode=disable` to hide the console window.
- Use `--include-package` to include specific Python packages.
- Use `--include-data-files` to include additional data files.

For more Nuitka packaging options, please refer to the [Nuitka Official Documentation](https://nuitka.net/doc/user-manual.html).

## Project Structure

```
Video_Intelligent_Annotation_Labn/
├── main.py                 # Program entry point
├── modules/
│   ├── main_window.py      # Main window implementation
│   ├── video_player.py     # Video player component
│   ├── image_viewer.py     # Image viewer component
│   ├── annotation_manager.py # Annotation manager
│   ├── api_handler.py      # API call handler
│   ├── file_handler.py     # File handling utility
│   └── help_dialog.py      # Help dialog
├── config/
│   ├── default_api_config.json  # Default API configuration
│   ├── user_api_config.json     # User API configuration
│   ├── diagnosis_labels_config.json # Diagnosis labels configuration
│   └── output_folder_config.json    # Output folder configuration
├── logo.ico              # Application icon
├── logo.png               # Original application icon image
├── convert_to_ico.py  # Icon conversion script
├── build.bat              # Software packaging script
├── requirements.txt        # Dependency list
└── README-en.md               # Project description (English)
└── README-zh.md            # Project description (Chinese)

```

## Detailed Usage Instructions

### Basic Workflow

1. **Import Data Folder**: Click the "Import Data Folder" button on the toolbar and select the directory containing subfolders.
2. **Set Output Folder**: Configure the save location for annotation data using the "Output Folder Settings" button on the toolbar (defaults to the "视频标注结果" folder on the Desktop).
3. **Video Annotation**:
   - Use the player controls to play and pause the video (Spacebar).
   - Use the scissor button (✂) or Ctrl+D twice to mark a segment (start and end times).
   - Add a label description in the pop-up dialog.
   - Alternatively, click the "Add" button to manually add segment annotations.
4. **Image Viewing**: Switch to the "Image" tab to view image documents in the current folder.
5. **Add Overall Video Description**: Enter a description for the entire video in the right-hand text box (must be at least 10 characters).
6. **Select Diagnosis Results**: Check one or more diagnostic labels in the "Diagnosis Results" area that match the video's presentation.
7. **Generate AI Analysis**: Click the "Generate Annotation Data" button; the program will call the large model API to generate analysis results.
8. **View/Edit AI Results**: View and edit the AI-generated content in the "Chain of Thought" and "Large Model Response" text boxes.
9. **Save Data**: Click the "Confirm Save" button; the program will save all annotation information to a JSONL file.
10. **Process Next**: After saving, the program automatically loads the content of the next unprocessed subfolder.

### Keyboard Shortcuts

- **Video Player**

  - Spacebar: Play/Pause video
  - Left/Right Arrow: Rewind/Forward video
  - Ctrl+D: Mark video segment start/end time
  - Ctrl+Mouse Wheel: Zoom video
  - Ctrl+0: Reset video zoom

- **Image Viewer**
  - Ctrl+Mouse Wheel: Zoom image
  - Ctrl+R: Rotate image
  - Left/Right Arrow: View previous/next image

### Advanced Feature Settings

- **Model Parameter Settings**: Supports configuring API connection, model name, API key, system prompt, user prompt template (for AI analysis), and human question template (for JSONL output).
- **Diagnosis Label Management**: Customize the list of diagnosis result labels, supporting add, edit, and delete operations.
- **History Browsing**: View and edit previously saved annotation data.

## Input Folder Format Requirements

The specific structure required for the input folder that the program can process is as follows:

```
Root Folder/
├── Sample 1/
│   ├── video.mp4          # Video file (only one video processed)
│   ├── pic1.jpg # Image file (multiple supported)
│   ├── pic2.png       # Image file
│   └── ...                # Other image files
├── Sample 2/
│   ├── test.mp4           # Video file
│   ├── pic1.jpg           # Image file
│   └── pic2.png           # Image file
└── ...                    # More sample folders
```

### Format Description

1. **Root Folder**: The folder selected via the "Import Data Folder" button.
2. **Sample Folder**: Each subfolder under the root folder is treated as an independent sample (e.g., data for one patient).
3. **File Requirements**:
   - Each sample folder must contain **one video file** (if multiple exist, only the first one found will be processed).
   - Can contain **zero or more image files** (for reference viewing).
   - Supported video formats: mp4, avi, mov, wmv, mkv.
   - Supported image formats: jpg, jpeg, png, bmp, gif.

## Annotation Data Format

The generated JSONL file format is as follows:

```json
{
  "video": "videos/video_filename.mp4",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\n Human question content"
    },
    {
      "from": "gpt",
      "value": "<think>Chain of thought analysis content</think>\n\n<answer>Model response content</answer>"
    }
  ],
  "duration": 23.77147,
  "raw_description": "Overall video description:\n xxx...\n\nAnnotated segments:\n00:10-00:15: xxx\n00:30-00:35: xxx\n\nFinal diagnosis results: xxx",
  "id": "1"
}
```

## API Support

The software supports multiple API service providers:

- Recommended: DeepSeek API (https://api.deepseek.com)
- Supported: WiseDiag API (https://api.wisediag.com/v1)
- Compatible with other service providers using the standard OpenAI API format.

## Frequently Asked Questions (FAQ)

### Q: What should I do if the API call fails when clicking "Generate Annotation Data"?

A: Please check the following:

- Is your computer connected to the internet?
- Has the API Key been correctly added in Toolbar -> Model Parameter Settings?
- Are the API Base URL and Model Name appropriate for the key you added?
- Is your API account valid or does it have sufficient balance?
- Try "Restore Default Settings" in the settings, then re-add your key.
- If using a local model or proxy, ensure the service is running and the address is correct.

### Q: Video cannot play or shows a black screen?

A: Please try:

- Confirm the video file itself is not corrupted; try opening it with another player.
- Confirm the video format is common (e.g., .mp4, .avi, .mov, .mkv).
- It might be missing video codecs. For Windows systems, installing a codec pack like K-Lite Codec Pack might help.

### Q: How to improve annotation efficiency?

A:

- Master the shortcuts for playback control and segment marking (Space, Left/Right Arrows, Ctrl+D).
- Use the variable speed playback feature to quickly browse the video.
- For common segment descriptions, write them elsewhere first and then copy-paste them into the label description box.
- Configure frequently used diagnostic labels in the settings beforehand.

### Q: Where is the generated annotation data saved?

A:

- Data is saved in the "Output Folder" you set via the toolbar.
- The program creates a subdirectory within the output folder with the same name as the root folder you imported.
- This subdirectory contains a `videos` folder (holding copied video files) and a `.jsonl` file named after the subdirectory (containing all annotation information).

### Q: How to modify already saved annotation data?

A:

- **Recommended Method**: Use the program's history tracking feature. Click "View Previous Saved Data" to find the record you want to modify, make changes, and click "Confirm Save" to overwrite and update.
- **Manual Method**: Directly open the corresponding `.jsonl` file with a text editor for modification. Note the JSONL format requirement: each line is a complete JSON object. The program will read the modified content the next time it loads.

### Q: How to customize diagnostic labels?

A:

- Click "Diagnosis Result Label Settings" (wrench icon) on the toolbar.
- In the pop-up dialog, you can "Add New", "Edit", or "Delete" labels.
- You can also "Restore Default Settings".
- The modified label list will take effect the next time the program starts or reloads data.
- The "Other" option always exists for entering diagnoses not in the list.

### Q: Why does clicking the scissor button (✂) or pressing Ctrl+D sometimes have no effect?

A:

- Marking a segment requires two clicks: the first marks the start, the second marks the end. Ensure you have clicked twice.
- After the first click, the scissor button changes color (to orange), indicating you need to click again to mark the end.
- If another operation is in progress (like an API call), the button might be temporarily disabled.

## Notes

- Ensure all necessary dependency packages are installed.
- A valid API key must be configured in the Model Parameter Settings before use.
- Supported video formats: mp4, avi, mov, wmv, mkv.
- Supported image formats: jpg, jpeg, png, bmp, gif.
- The overall video description must be at least 10 characters long, and at least one diagnosis result must be selected.
- The save operation automatically copies the video to the output directory and creates the JSONL file.

## More Information

Please use the "Help" button within the software to view detailed usage instructions.
