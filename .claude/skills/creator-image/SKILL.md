---
name: creator-image
description: Workflow to generate E-commerce product images batch by batch using Coze API.
---

The user will provide a path to a folder containing product images. The folder name is the prompt for the image generation unless user required.

Follow these steps to generate images for each product folder. 

1. **Analyze Directories**: Identify product folders. Each folder is a separate task.
2. **Execute Workflow**: For each folder, run the automation script. Use the folder name as the `prompt` unless user required.

### Execute Workflow
Run the automated workflow which handles uploading, generating, and downloading images for the specified folder.
```bash
python3 .agent/skills/creator-image/resource/run_script.py "/path/to/folder" "Optional Custom Prompt"
```
