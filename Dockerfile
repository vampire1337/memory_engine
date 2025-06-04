FROM python:3.12-slim

ARG PORT=8050

WORKDIR /app

# Install uv
RUN pip install uv

# Copy the MCP server files
COPY . .

# Install packages
RUN python -m venv .venv
RUN uv pip install -e .

# Set default environment variables
ENV TRANSPORT=sse
ENV HOST=0.0.0.0
ENV PORT=${PORT}

# Set OpenAI API key
ENV OPENAI_API_KEY=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

# Set LLM configuration
ENV LLM_PROVIDER=openai
ENV LLM_API_KEY=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
ENV LLM_CHOICE=gpt-4o-mini
ENV EMBEDDING_MODEL_CHOICE=text-embedding-3-small

EXPOSE ${PORT}

# Command to run the MCP server
CMD ["uv", "run", "src/main.py"]