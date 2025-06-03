import asyncio
import os
# Adjust the import path based on where this script is located relative to the app module
# If this script is in the root of presell_platform_backend, this should work:
from app.services.image_capture import capture_screenshot_service

async def main():
    print("Iniciando teste de captura de screenshot...")
    # Define a URL de teste e o caminho para salvar
    test_url = "https://www.google.com"
    # Salvar na pasta de screenshots definida nos endpoints de presell para consistência
    save_dir = "/home/ubuntu/presell_platform_backend/generated_assets/screenshots"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "test_capture.png")

    print(f"Capturando screenshot de: {test_url}")
    print(f"Salvando em: {save_path}")

    success = await capture_screenshot_service(test_url, save_path)

    if success and os.path.exists(save_path):
        print(f"Screenshot capturado com sucesso e salvo em: {save_path}")
        # Você pode querer verificar o tamanho do arquivo ou outras propriedades
        file_size = os.path.getsize(save_path)
        print(f"Tamanho do arquivo: {file_size} bytes")
        if file_size == 0:
            print("ALERTA: O arquivo de screenshot foi criado mas está vazio (0 bytes).")
    elif success and not os.path.exists(save_path):
        print("ERRO: Serviço de captura reportou sucesso, mas o arquivo não foi encontrado em {save_path}.")
    else:
        print("Falha ao capturar screenshot.")

if __name__ == "__main__":
    asyncio.run(main())

