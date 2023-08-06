# Hack Mentor

## Description

Welcome to Hack Mentor, an AI companion for your coding journey. This project leverages the power of GPT-4 to actively watch you code in your terminal, providing real-time feedback and suggestions.

There are two key modes in Hack Mentor:

- **Mentor Mode**: Here, Hack Mentor will focus on the quality of your code, making sure it follows best practices, and suggesting improvements.

- **Architect Mode**: In this mode, Hack Mentor takes a more holistic view, helping you design your code structure and suggesting architectural changes.

## Installation

Before starting, ensure you have Python 3.6 or above installed on your system.

To get Hack Mentor running, follow the steps below:

1. Set up a virtual environment. This helps to avoid any conflicts with other installed Python packages.

   ```bash
   python3 -m venv hack_mentor_env
   ```

2. Activate the virtual environment.

   On Linux or MacOS:

   ```bash
   source hack_mentor_env/bin/activate
   ```

   On Windows:

   ```bash
   .\hack_mentor_env\Scripts\activate
   ```

3. Install Hack Mentor via pip.

   ```bash
   pip install hack_mentor
   ```

4. Set up your OpenAI API key

- change the name of `.env.example` to `.env`
- go to https://platform.openai.com to get that

## Usage

Once you have Hack Mentor installed, you can use it in the following ways:

- To use Mentor mode with a single file, use:

  ```bash
  hack_mentor mentor App.js ~/george/my_cool_app/index.js
  ```

- To use Architect mode with multiple files, use:

  ```bash
  hack_mentor architect App.js component.js reducer.js ~/george/my_cool_app/index.js
  ```

In both cases, replace `App.js`, `component.js` and `reducer.js` with the actual paths to your JavaScript files.

Hack Mentor is currently optimized for JavaScript, but we're actively working on supporting more languages. Stay tuned!

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
