import uvicorn

import config

if __name__ == '__main__':
    uvicorn.run("api.server:app", host='localhost', port=8000, reload=True, reload_includes=config.root_dir)
