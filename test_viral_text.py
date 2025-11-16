#!/usr/bin/env python3
"""
Test del generador de texto viral
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from facebook_api import FacebookAPI

def test_viral_text_generation():
    """Prueba el generador de texto viral"""
    
    print("🚀 Ejemplos de texto viral generado automáticamente 🚀\n")
    
    api = FacebookAPI()
    
    # Generar varios ejemplos
    prompts = [
        "Tutorial de cocina para hacer pizza casera",
        "Rutina de ejercicios para principiantes",
        "Tips de fotografía para redes sociales",
        "Reseña de producto tecnológico innovador",
        "Viaje por destinos exóticos de Europa"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"--- Ejemplo {i}: {prompt} ---")
        viral_text = api._generate_viral_copyright_text(prompt)
        print(viral_text)
        print("-" * 60)
        print()

if __name__ == "__main__":
    test_viral_text_generation()