# Latin Website
Name sucks I know, I have nothing better.

## Development Setup

### Backend
You need Python installed.
1. Install the Python dependencies.
    - Open the project root directory in the terminal and run `pip install -r backend/requirements.txt`.
2. Install [PyWORDS](https://github.com/sjgallagher2/PyWORDS)
    1. `git clone https://github.com/sjgallagher2/PyWORDS`
    2. `cd PyWORDS`
    3. `pip install .`
3. Create `backend/.env` file:

    ```
    SECRET_KEY="some random secret key"
    ```
4. Run `backend/main.py`.
