"""Main entry point for robot vision application."""

import numpy as np
import os
from src.image_processing import apply_threshold, detect_edges
from src.vision_algorithms import ObjectDetector, PathPlanner, calculate_centroid
from src.robot_interface import RobotVisionController
from src.core import BitmapProcessor
from src.storage import RuntimeStorage


def main():
    """Main function to demonstrate robot vision capabilities."""
    robot_id = "robot_fr_001"
    print("Vision Robotique avec Traitement Bitmap")
    print("=" * 50)
    
    # Initialize components
    storage = RuntimeStorage(robot_id=robot_id)
    detector = ObjectDetector(min_area=100)
    planner = PathPlanner(grid_size=(640, 480))
    controller = RobotVisionController(safety_distance=0.5, storage=storage, robot_id=robot_id)
    
    print("\nComposants initialises :")
    print(f"- Detecteur d'objets (surface minimale : {detector.min_area})")
    print(f"- Planificateur de trajectoire (grille : {planner.grid_size})")
    print(f"- Controleur de vision (distance de securite : {controller.safety_distance} m)")
    print("- BitmapProcessor (prise en charge des fichiers photo bruts)")
    print(f"- Voix du robot : {controller.speak('startup')}")
    print(f"- {controller.storage_summary()}")
    
    # Example: Process a sample image
    print("\nExemple : traitement d'une image d'essai...")
    sample_image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    
    # Apply threshold
    binary_image = apply_threshold(sample_image, threshold=128)
    print(f"Seuil applique pour creer une image binaire : {binary_image.shape}")
    
    # Calculate centroid
    centroid = calculate_centroid(binary_image)
    print(f"Centroide calcule : ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
    # Generate robot command
    command = controller.process_frame(sample_image)
    print(f"\nCommande generee : {command.direction} a la vitesse {command.speed}")
    print(f"Le robot dit : {controller.speak('processing')}")
    print(f"Donnees d'execution enregistrees dans : {storage.robot_path()}/")
    
    # Check for raw camera files
    print("\nTraitement des fichiers photo bruts :")
    raw_extensions = ['.nef', '.cr2', '.arw', '.dng', '.raf']
    raw_files = [f for f in os.listdir('.') if any(f.lower().endswith(ext) for ext in raw_extensions)]
    
    if raw_files:
        print(f"{len(raw_files)} fichier(s) brut(s) trouve(s)")
        print(f"Example: BitmapProcessor('{raw_files[0]}').process_to_1bit('output.bmp')")
    else:
        print("Aucun fichier photo brut trouve dans le dossier courant")
        print("Formats pris en charge : NEF, CR2, ARW, DNG, RAF")
    
    print("\n✓ Systeme de vision robotique pret !")
    print("\nProchaines etapes :")
    print("1. Ajouter des fichiers photo bruts (NEF, CR2, ARW) pour le traitement")
    print("2. Integrer l'interface camera a votre robot")
    print("3. Adapter les algorithmes de vision a votre usage")
    print("4. Tester avec le materiel robotique reel")


if __name__ == "__main__":
    main()
