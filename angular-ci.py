import subprocess
import sys
import argparse
import os

# Fonction pour exécuter une commande et vérifier les erreurs
def run_command(command):
    try:
        # Exécute la commande et capture la sortie
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e.stderr}")
        sys.exit(1)

# Fonction pour installer les dépendances avec npm
def install_dependencies():
    print("Installation des dépendances...")
    run_command(["npm", "ci", "--cache", ".npm", "--prefer-offline"])

# Fonction pour lancer le build de l'application
def build():
    print("Lancement de la construction de l'application...")
    install_dependencies()  # Installer les dépendances avant le build
    run_command(["npm", "run", "build"])

# Fonction pour lancer les tests de l'application
def test():
    print("Lancement des tests de l'application...")
    run_command(["npm", "test"])

# Fonction pour empaqueter l'application
def pack():
    print("Lancement du packaging de l'application...")
    run_command(["npm", "pack"])

    # Générez un fichier .tar contenant le dossier dist
    dist_folder = "dist"
    tar_file = "angular-app.tar"
    run_command(["tar", "-cvf", tar_file, dist_folder])

# Fonction pour publier l'application sur GitLab
def publish_to_gitlab(token, project_id, scope):
    print(f"Publication du paquet dans GitLab avec le project_id {project_id}...")

    # Si aucun scope n'est fourni, on l'ignore dans la configuration du .npmrc
    npmrc_content = f"registry=https://gitlab.com/api/v4/projects/{project_id}/packages/npm/\n"
    if scope:
        npmrc_content += f"@{scope}:registry=https://gitlab.com/api/v4/projects/{project_id}/packages/npm/\n"
    npmrc_content += f"//gitlab.com/api/v4/projects/{project_id}/packages/npm/:_authToken={token}\n"
    
    # Sauvegarder le contenu dans un fichier .npmrc
    with open(".npmrc", "w") as f:
        f.write(npmrc_content)
    
    # Exécuter la commande npm publish pour publier le paquet
    try:
        subprocess.check_call(["npm", "publish"])
        print("Publication réussie dans GitLab Package Registry.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la publication : {e}")
        sys.exit(1)

# Fonction principale pour gérer les arguments de la ligne de commande
def main():
    parser = argparse.ArgumentParser(description="Script d'intégration continue pour Angular")
    subparsers = parser.add_subparsers(dest="command")

    # Sous-commande build
    subparsers.add_parser("build", help="Construire l'application")

    # Sous-commande test
    subparsers.add_parser("test", help="Lancer les tests de l'application")

    # Sous-commande pack
    subparsers.add_parser("pack", help="Emballer l'application")

    # Sous-commande publish
    publish_parser = subparsers.add_parser("publish", help="Publier l'application sur GitLab")
    publish_parser.add_argument("--token", required=True, help="Token de déploiement GitLab")
    publish_parser.add_argument("--project-id", required=True, help="ID du projet GitLab")
    publish_parser.add_argument("--scope", help="Scope npm pour l'application", default="")

    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "test":
        test()
    elif args.command == "pack":
        pack()
    elif args.command == "publish":
        publish_to_gitlab(args.token, args.project_id, args.scope)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
