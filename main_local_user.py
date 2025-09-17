import paramiko
import sys
import datetime
from scp import SCPClient
import km_lin

linKey = r'/home/sigma.sbrf.ru@22682851/.ssh/id_rsa_prometheus'
file_path = r'/home/work/22682851@sigma.sbrf.ru/Replication_of_exporters/exporters/'
from_file = 'host_user.txt'
flag_exporter = True

phost = []
puser = []
pdb = []
pexporter = ['node_exporter', 'postgres_exporter', 'sql_exporter', 'check_exporter']

exporter_files = {
    'node_exporter': ['node_exporter', 'LICENSE', 'NOTICE'],
    'postgres_exporter': ['postgres_exporter', 'LICENSE', 'NOTICE', 'env'],
    'sql_exporter': ['sql_exporter', 'LICENSE', 'sql_exporter.yml', 'pg_gotham.collector.yml'],
    'check_exporter': ['check_exporter']
}
overwr_files = {
    'check_exporter': ['etalon_check_exporter'],
    'postgres_exporter': ['etalon_env'],
    'sql_exporter': ['etalon_sql_exporter.yml', 'etalon_env_s']
}
test_command = {
    'node_exporter': 'ps -C "node_exporter" > /dev/null 2>&1 && echo 1 || echo 0',
    'postgres_exporter': 'ps -C "postgres_exporter" > /dev/null 2>&1 && echo 1 || echo 0',
    'sql_exporter': 'ps -C "sql_exporter" > /dev/null 2>&1 && echo 1 || echo 0',
    'check_exporter': 'crontab -l | grep -q check_exporter && echo 1 || echo 0'
}

# функция формирования из эталонных файлов - файлы для соответвующего хоста
def overwriting(input_file, host, db, output_file):
    with open(input_file, 'r', encoding="utf-8") as f:
        content = f.read()
    new_content = content.replace('{host}', host)
    new_content = new_content.replace('{db}', db)
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(new_content)

# функция проверки наличия и запущенности экспортеров
def available_exporter(host, user, exporter):
    pp_res, s = km_lin.linCommand(f'test -d /home/{user}/dir_{exporter}/ && echo 1 || echo 0', host, user, linKey)
    if s.strip()=='1':
        flag_exporter = True
        pp_res, s = km_lin.linCommand(test_command[exporter], host, user, linKey)
        if s.strip()=='1':
            print('\t\t' + exporter + ' - запущен.')
            return flag_exporter
        else:
            pp_res, s = km_lin.linCommand(start_command[exporter], host, user, linKey)
            pp_res, s = km_lin.linCommand(test_command[exporter], host, user, linKey)
            if s.strip()=='1':
                print('\t\t' + exporter + ' - запущен.')
                return flag_exporter
            else:
                print('\t\t' + exporter + ' - ВНИМАНИЕ! НЕ ЗАПУСКАЕТСЯ!')
                return flag_exporter
    else:
        print('\t' + exporter + ' - НЕ найден.')
        flag_exporter = False
        return flag_exporter

# функция копирования экспортеров
def replication_exporter(host, user, db, exporter):
    for file in exporter_files[exporter]:
        try:
            for overwr_file in overwr_files[exporter]:
                overwriting(overwr_file, host, db, file_path + f'{exporter}/' + overwr_file.replace('etalon_', ''))
        except KeyError: pass
        pp_res, s = km_lin.linCommand(f'mkdir /home/{user}/dir_{exporter}', host, user, linKey)
        path_out = file_path + f'{exporter}/' + file
        path_in = f'/home/{user}/'
        pp_res_transfer = km_lin.linPutFile(host, user, linKey, path_in, path_out)
        pp_res, s = km_lin.linCommand(f'mv /home/{user}/{file} /home/{user}/dir_{exporter}/', host, user, linKey)
        pp_res, s = km_lin.linCommand(f'/usr/bin/chmod -R 755 /home/{user}/dir_{exporter}', host, user, linKey)
    print('\t\t' + exporter + ' - создан, попытка запуска:')
    available_exporter(host, user, exporter)

# функция принудительного перезапуска экспортеров
def restarted_exporter(host, user, exporter):
    pp_res, s = km_lin.linCommand(f'pgrep -f {exporter}', host, user, linKey)
    for pid in s.split():
        pp_res, s = km_lin.linCommand(f'kill -9 {pid}', host, user, linKey)
    pp_res, s = km_lin.linCommand(start_command[exporter], host, user, linKey)
    pp_res, s = km_lin.linCommand(test_command[exporter], host, user, linKey)
    if s.strip()=='1':
        print('\t\t' + exporter + ' - перезапущен.')
        return flag_exporter
    else:
        print('\t\t' + exporter + ' - ВНИМАНИЕ! НЕ ПЕРЕЗАПУСКАЕТСЯ!')
        return flag_exporter

# ----------------------------------------------------------------------------------------------------------------------
with open(from_file) as file:
    array_from=[row.strip() for row in file]

for f in array_from:    # цикл по строкам файла
    if f=='': continue # пропускаем пустые строки
    if f.startswith('#'): continue # пропускаем закомментированные строки
    phost.append(f.split()[0])
    puser.append(f.split()[1])
    pdb.append(f.split()[2])

for host, user, db in zip(phost, puser, pdb): # цикл по связкам хост-уз-бд
    print(host)
    for exporter in pexporter: # цикл по экспортерам
        start_command = {
            'node_exporter': f'nohup bash -c /home/{user}/dir_node_exporter/node_exporter >/dev/null 2>&1 &',
            'postgres_exporter': f'/home/{user}/dir_postgres_exporter/env',
            'sql_exporter': f'/home/{user}/dir_sql_exporter/env_s',
            'check_exporter': f'echo "* * * * * /home/{user}/dir_check_exporter/check_exporter" > mycron && crontab mycron && rm mycron'
        }

        flag_exporter = available_exporter(host, user, exporter)
        # restarted_exporter(host, user, exporter)
        # flag_exporter = True
        if flag_exporter: continue
        else:
            replication_exporter(host, user, db, exporter)
            restarted_exporter(host, user, exporter)






