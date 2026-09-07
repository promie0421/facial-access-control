from modules.database import (
    init_database,
    contar_embeddings_do_usuario,
    buscar_usuario_por_public_id,
)

from modules.registration import cadastrar_pessoa


init_database()

nome = input("Digite o nome da pessoa a cadastrar: ").strip()

if not nome:
    print("Nome inválido.")
else:
    sucesso, mensagem, public_id = cadastrar_pessoa(nome)

    print(mensagem)

    if sucesso:
        usuario = buscar_usuario_por_public_id(public_id)

        if usuario:
            total_embeddings = contar_embeddings_do_usuario(
                usuario["id"]
            )

            print(
                f"Usuario '{usuario['name']}' "
                f"(ID {public_id}) tem "
                f"{total_embeddings} embeddings salvos no banco."
            )
        else:
            print(
                "ERRO: usuário foi cadastrado, "
                "mas não foi encontrado na consulta."
            )