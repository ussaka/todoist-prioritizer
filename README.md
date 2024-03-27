<div class="readme-header" align="center">
  <img src="https://github.com/ussaka/todoist-prioritizer/blob/main/docs/priority.svg" alt="Description of the image" width="150" height="150">
  <h1>todoist-prioritizer</h1>  

  [![Release](https://img.shields.io/badge/Release-1.0.0-blue?style=flat)](https://github.com/ussaka/todoist-prioritizer/releases/latest)
  [![wakatime](https://wakatime.com/badge/user/41c5948e-4207-46a3-bcb4-2f355d15e4ac/project/018e4894-c1f1-49df-b86c-1d01599a769f.svg)](https://wakatime.com/badge/user/41c5948e-4207-46a3-bcb4-2f355d15e4ac/project/018e4894-c1f1-49df-b86c-1d01599a769f)
  [![CodeQL](https://github.com/ussaka/todoist-prioritizer/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/ussaka/todoist-prioritizer/actions/workflows/github-code-scanning/codeql)
  <p>
      <b>
          📑 <a href="https://ussaka.github.io/todoist-prioritizer/">Documentation</a>
      </b>
  </p>  
  <h3>Automatic <a href="https://todoist.com">Todoist</a> tasks prioritizer</h3>
</div>

# Usage
Available commands
```bash
python todoist-prioritizer.py -h
```

Example usage
```bash
python todoist-prioritizer.py -a 3x4mpl34p1k3y -h 00 -m 00 -d
```

Reset to default settings
```bash
python todoist-prioritizer.py -r
```
# Installation
Pre-compiled .exe binaries are available in the [releases] for Windows users.

## PyInstaller
Users can compile the script to an executable using PyInstaller
### Windows
```bash
pyinstaller src/todoist-prioritizer.py --icon=docs/priority.ico -c --onefile --add-data src/config.ini:.
```