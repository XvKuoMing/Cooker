import subprocess

# запускаем команду sql
def make_dump(user="root",
              password="101",
              database="cookbook",
              backup_file="backup.sql"):

    command = f"docker exec recipes_db mysqldump -u {user} --password={password} {database} > {backup_file}"
    process = subprocess.run(command, shell=True)

    # логи
    if process.returncode == 0:
        print("таблица успешно сохранена")
    else:
        print(f"Ошибка сохранения. Код: {process.returncode}.")