#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
import urllib.request

# Конфігурація
GITLEAKS_VERSION = "8.18.2"
CONFIG_KEY = "hooks.gitleaks.enabled"

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def is_enabled():
    rc, out, _ = run_command(f"git config --get {CONFIG_KEY}")
    return out.lower() == "true"

def install_gitleaks():
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"🔍 Gitleaks не знайдено. Встановлення версії {GITLEAKS_VERSION} для {system}...")
    
    # Визначення назви файлу залежно від ОС
    ext = "zip" if system == "windows" else "tar.gz"
    suffix = "windows_x64.zip" if system == "windows" else \
             "darwin_x64.tar.gz" if system == "darwin" else "linux_x64.tar.gz"
    
    if "arm" in arch or "aarch64" in arch:
        suffix = suffix.replace("x64", "arm64")

    url = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}/gitleaks_{GITLEAKS_VERSION}_{suffix}"
    
    # Шлях для встановлення (локально в .git/hooks для ізоляції)
    bin_path = os.path.abspath(".git/hooks/gitleaks-bin")
    if not os.path.exists(bin_path):
        os.makedirs(bin_path)

    try:
        archive_path = os.path.join(bin_path, f"gitleaks.{ext}")
        urllib.request.urlretrieve(url, archive_path)
        
        # Розпакування (спрощено через shutil або tar)
        if system == "windows":
            shutil.unpack_archive(archive_path, bin_path)
        else:
            run_command(f"tar -xzf {archive_path} -C {bin_path}")
        
        executable = os.path.join(bin_path, "gitleaks.exe" if system == "windows" else "gitleaks")
        os.chmod(executable, 0o755)
        return executable
    except Exception as e:
        print(f"❌ Помилка при встановленні gitleaks: {e}")
        sys.exit(1)

def main():
    if not is_enabled():
        # Скрипт вимикається, якщо git config hooks.gitleaks.enabled не true
        return

    # Перевірка наявності gitleaks в PATH або локально
    gitleaks_path = shutil.which("gitleaks")
    if not gitleaks_path:
        local_bin = os.path.abspath(".git/hooks/gitleaks-bin/gitleaks")
        if os.path.exists(local_bin):
            gitleaks_path = local_bin
        else:
            gitleaks_path = install_gitleaks()

    print("🛡️  Запуск Gitleaks для перевірки секретів...")
    
    # Запуск перевірки лише застейджених файлів (--staged)
    rc, out, err = run_command(f"{gitleaks_path} protect --staged --verbose --redact")

    if rc != 0:
        print("\n" + "!"*50)
        print("❌ ПОМИЛКА: Gitleaks виявив потенційні секрети у вашому коміті!")
        print(out)
        print("!"*50)
        print("\nПорада: Видаліть секрети або використовуйте 'gitleaks.toml' для ігнорування.")
        sys.exit(1)
    
    print("✅ Секретів не виявлено. Коміт дозволено.")

if __name__ == "__main__":
    main()