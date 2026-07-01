# Ollama on Windows with models on D:\

Ollama’s app itself installs to Windows Program Files, but you can keep **models** on **D:\\** (this is what uses disk).

## Steps

1. Create folder:

```powershell
mkdir D:\ollama-models
```

2. Set **System** environment variable **before installing** Ollama:

- Name: `OLLAMA_MODELS`
- Value: `D:\ollama-models`

3. Install Ollama from `https://ollama.com/download`

4. Start server:

```powershell
ollama serve
```

5. Pull the model:

```powershell
ollama pull llama3.2:1b
```

## Verify

```powershell
ollama list
```

