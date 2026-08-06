"""
Outil de validation de gamme d'etalonnage
==========================================

Automatise la validation d'une methode analytique lineaire
(spectrophotometrie, chromatographie...) a partir d'une gamme
d'etalonnage : regression lineaire, R2, LOD, LOQ, et verdict de
conformite -- avec un rapport et un graphique.

NOUVEAU : peut lire une gamme directement depuis un fichier CSV.

Concu par un technicien en chimie analytique pour supprimer le
traitement manuel sous tableur (des heures -> quelques secondes,
sans erreur de recopie, resultat reproductible).

Utilisation :
    python validation_gamme.py                  # demo sur donnees synthetiques
    python validation_gamme.py gamme.csv        # sur ton propre fichier CSV
    (le CSV doit avoir 2 colonnes : concentration, absorbance)

Auteur : Martial
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def valider_gamme(concentrations, absorbances, seuil_r2=0.995):
    """Valide une gamme d'etalonnage lineaire.

    Parametres
    ----------
    concentrations : liste ou tableau des concentrations (ex. mg/L)
    absorbances    : liste ou tableau des reponses mesurees (ex. absorbance)
    seuil_r2       : critere de linearite (defaut 0.995)

    Retour
    ------
    dict : pente, ordonnee, R2, LOD, LOQ, sigma, verdict
    """
    x = np.asarray(concentrations, dtype=float)
    y = np.asarray(absorbances, dtype=float)

    # Regression lineaire y = pente * x + ordonnee
    pente, ordonnee = np.polyfit(x, y, 1)
    y_predit = pente * x + ordonnee

    # Coefficient de determination R2
    r_carre = np.corrcoef(x, y)[0, 1] ** 2

    # Dispersion residuelle (ecart des points a la droite)
    sigma = np.std(y - y_predit)

    # Limites de detection / quantification (approche ICH)
    lod = 3.3 * sigma / pente
    loq = 10.0 * sigma / pente

    verdict = "CONFORME" if r_carre >= seuil_r2 else "NON CONFORME"

    return {
        "pente": pente,
        "ordonnee": ordonnee,
        "R2": r_carre,
        "sigma": sigma,
        "LOD": lod,
        "LOQ": loq,
        "verdict": verdict,
    }


def charger_gamme_csv(chemin, col_conc="concentration", col_abs="absorbance"):
    """Charge une gamme depuis un fichier CSV.

    Le CSV doit contenir deux colonnes nommees (par defaut
    'concentration' et 'absorbance'). Renvoie deux tableaux NumPy.
    """
    df = pd.read_csv(chemin)
    concentrations = df[col_conc].to_numpy()
    absorbances = df[col_abs].to_numpy()
    return concentrations, absorbances


def afficher_rapport(nom, rapport):
    """Affiche un rapport de validation lisible dans la console."""
    print(f"\n----- RAPPORT DE VALIDATION : {nom} -----")
    print(f"  Droite     : A = {rapport['pente']:.4f} * C + {rapport['ordonnee']:.4f}")
    print(f"  R2         : {rapport['R2']:.5f}")
    print(f"  LOD        : {rapport['LOD']:.3f}")
    print(f"  LOQ        : {rapport['LOQ']:.3f}")
    print(f"  VERDICT    : {rapport['verdict']}")


def tracer_gamme(concentrations, absorbances, rapport, fichier="exemple_rapport.png"):
    """Trace la gamme + la droite ajustee et enregistre l'image."""
    x = np.asarray(concentrations, dtype=float)
    y = np.asarray(absorbances, dtype=float)
    y_droite = rapport["pente"] * x + rapport["ordonnee"]

    plt.figure(figsize=(8, 5))
    plt.scatter(x, y, color="crimson", label="Points mesures")
    plt.plot(x, y_droite, color="navy",
             label=f"A = {rapport['pente']:.4f}*C + {rapport['ordonnee']:.4f}")
    plt.title(f"Droite d'etalonnage (R2 = {rapport['R2']:.5f}) - {rapport['verdict']}")
    plt.xlabel("Concentration")
    plt.ylabel("Absorbance")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(fichier, dpi=150, bbox_inches="tight")
    print(f"\nGraphique enregistre : {fichier}")


def generer_gamme_demo(seed=42):
    """Genere une gamme d'etalonnage SYNTHETIQUE realiste (donnees inventees)."""
    rng = np.random.default_rng(seed)
    concentrations = np.arange(0, 11, 2)            # 0..10
    absorbances = 0.12 * concentrations + rng.normal(0, 0.02, size=len(concentrations))
    return concentrations, absorbances


if __name__ == "__main__":
    # Si un fichier CSV est passe en argument, on l'utilise ;
    # sinon on retombe sur la demonstration synthetique.
    if len(sys.argv) > 1:
        chemin = sys.argv[1]
        concentrations, absorbances = charger_gamme_csv(chemin)
        nom = f"Fichier : {chemin}"
    else:
        concentrations, absorbances = generer_gamme_demo()
        nom = "Gamme de demonstration (synthetique)"

    rapport = valider_gamme(concentrations, absorbances)
    afficher_rapport(nom, rapport)
    tracer_gamme(concentrations, absorbances, rapport)
