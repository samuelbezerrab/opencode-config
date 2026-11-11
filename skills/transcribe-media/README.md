# Manutenção — macOS Apple Silicon

Esta cópia usa `mlx-whisper`, Python em `.venv` e `ffmpeg`/`ffprobe` no PATH. O primeiro uso baixa `mlx-community/whisper-large-v3-turbo` para o cache do Hugging Face; os arquivos de mídia são processados localmente. Mantenha a venv e o cache fora de pacotes compartilhados.

Para reinstalar neste Mac, crie uma venv nesta pasta e execute `.venv/bin/python -m pip install -r requirements.lock`. Execute os testes com `.venv/bin/python -m unittest discover -s tests -v`. Testes de transcrição reais exigem mídia local e o modelo baixado.
