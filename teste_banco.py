from modules.database import (
    init_database,
    get_connection,
    listar_tabelas,
    criar_usuario,
    buscar_usuario_por_public_id,
    remover_usuario,
)

print("Inicializando banco...")
init_database()

print("Rodando a inicialização de novo, para garantir que nada quebra...")
init_database()

conexao = get_connection()
cursor = conexao.cursor()

cursor.execute("PRAGMA foreign_keys")
foreign_keys_ativas = cursor.fetchone()[0]

conexao.close()

print("Foreign keys ativas:", bool(foreign_keys_ativas))

tabelas = listar_tabelas()

print("Tabelas encontradas:", tabelas)

esperadas = {
    "users",
    "face_embeddings",
    "access_logs"
}

if esperadas.issubset(set(tabelas)):
    print("Todas as tabelas esperadas existem.")
else:
    print(
        "ATENÇÃO: faltam tabelas ->",
        esperadas - set(tabelas)
    )

print("Testando inserção de usuário fictício...")

novo_id, novo_public_id = criar_usuario(
    "Usuario Teste",
    "hash-fake-de-teste"
)

print(
    "Usuário criado. id interno:",
    novo_id,
    "| public_id:",
    novo_public_id
)

usuario = buscar_usuario_por_public_id(novo_public_id)

print(
    "Usuário encontrado na busca:",
    dict(usuario) if usuario else None
)

print("Removendo usuário de teste...")

remover_usuario(novo_id)

usuario_apos_remocao = buscar_usuario_por_public_id(
    novo_public_id
)

print(
    "Usuário após remoção (deve ser None):",
    usuario_apos_remocao
)

print("Teste concluído.")