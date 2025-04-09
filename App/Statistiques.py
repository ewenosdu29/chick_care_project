def save_statistiques(poussins_count, date_today):
    """
    Enregistre le nombre de poussins et la date fournie dans un fichier texte.
    """
    # Créer une chaîne de caractères avec les données à enregistrer
    data = f"{date_today}, {poussins_count}\n"

    # Enregistrer dans un fichier texte (par exemple, "statistiques.txt")
    with open("statistiques.txt", "a") as file:
        file.write(data)

    # Optionnel : afficher un message de confirmation
    print(f"Statistique enregistrée : {data}")
