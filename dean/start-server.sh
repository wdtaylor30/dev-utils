# on HPC, need to load ollama module
module load ollama
ollama serve &

# start uv venv
source .venv/bin/activate

# start dean server
uv run src/server.py