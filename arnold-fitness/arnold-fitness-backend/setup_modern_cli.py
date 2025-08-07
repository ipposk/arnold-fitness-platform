#!/usr/bin/env python3
"""
🚀 Setup per Arnold Modern CLI
Installa le dipendenze necessarie per l'interfaccia CLI moderna
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name, description):
    """Installa un pacchetto Python con feedback"""
    print(f"Installando {description}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"OK {description} installato con successo!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRORE nell'installazione di {description}: {e}")
        return False

def main():
    """Setup principale"""
    print("Arnold Modern CLI Setup")
    print("=" * 50)
    print()
    
    # Lista dei pacchetti necessari
    packages = [
        ("rich", "Rich - Libreria per CLI belle e interattive"),
        ("colorama", "Colorama - Supporto colori cross-platform"),
        ("python-dotenv", "Python-dotenv - Gestione file .env"),
    ]
    
    success_count = 0
    
    for package, description in packages:
        if install_package(package, description):
            success_count += 1
        print()
    
    print("=" * 50)
    
    if success_count == len(packages):
        print("Setup completato con successo!")
        print()
        print("Ora puoi utilizzare Arnold Modern CLI:")
        print("   python arnold_cli_modern.py")
        print()
        print("Oppure usa la versione classica:")
        print("   python arnold_main_local.py")
        print()
        print("Confronta le due interfacce per vedere la differenza!")
        
    else:
        print(f"Setup parzialmente completato: {success_count}/{len(packages)} pacchetti installati")
        print()
        print("Puoi provare a installare manualmente i pacchetti mancanti:")
        for package, description in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()