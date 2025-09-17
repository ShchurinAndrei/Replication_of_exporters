from dbm import error

import paramiko

# Процедура выполнение передаваемой команды на хосте
def linCommand(command, host, user, key):
  SSHClient = paramiko.SSHClient()
  SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  outtext='Not Connected'
  s_conn='Connection - OK'
  str_res=''
  #print(key)
  try:
    SSHClient.connect(hostname=host, username=user, key_filename=key)
  except paramiko.AuthenticationException as sshException:
    s_conn=('SSH AUTHENTICATION ERROR -----> ' + host)
  except paramiko.ssh_exception.SSHException:
    s_conn=('Not a valid OPENSSH private key file! '+ host)
  except:
    s_conn=('Unknown SSH connection error '+ host)
  p_res='failed';
  good_pos=0;
  #print(s_conn)
  if s_conn == 'Connection - OK':
    #print('Выполняем команду: ' + command)
    #log.write('Выполняем команду: ' + command)
    stdIn, stdOut, stdErr = SSHClient.exec_command(command)
    outtext = stdOut.read().decode('utf-8')
    #print('Результат: ' + outtext)
    p_res='success';
    str_res=outtext
  else:
    p_res='failed';
    str_res='Not Connected!'
  SSHClient.close()
  
  return p_res, str_res;

  
def linCommandMute(command, host, user, key):
  SSHClient = paramiko.SSHClient()
  SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  outtext='Not Connected'
  s_conn='Connection - OK'
  str_res=''
  try:
    SSHClient.connect(hostname=host, username=user, key_filename=key)
  except paramiko.AuthenticationException as sshException:
    s_conn=('SSH AUTHENTICATION ERROR -----> ' + host)
  except paramiko.ssh_exception.SSHException:
    s_conn=('Not a valid OPENSSH private key file! '+ host)
  except:
    s_conn=('Unknown SSH connection error '+ host)
  p_res='failed';
  good_pos=0;
  #print(s_conn)
  if s_conn == 'Connection - OK':
    #print('Выполняем команду: ' + command)
    stdIn, stdOut, stdErr = SSHClient.exec_command(command)
    outtext = stdOut.read().decode('utf-8')
    #print('Результат: ' + outtext)	
    p_res='success';
    str_res=outtext
  else:
    p_res='failed';
    str_res='Not Connected!'
  SSHClient.close()
  
  return p_res, str_res;  

# Процедура получения заданного файла с хоста  
def linGetFile(sHost, sUser, sKey, sLinFile, sDirFile):
  from scp import SCPClient
  p_res='success';
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  sPort=22
  try:
    ssh.connect(hostname=sHost, port=sPort, username=sUser, key_filename=sKey)
  # Обрабатываем ошибки
  except paramiko.ssh_exception.AuthenticationException:
    #print ("ScriptRes:Bad:"+ "Authentification failed")
    ssh.close()
    p_res='failed';
  except paramiko.ssh_exception.SSHException:
    if badCount>1:
      #print ("ScriptRes:Bad:"+ "SSH error:" + str(badCount) + ' attempt(s)')
      ssh.close()
      p_res='failed';
  except:
    #print ("ScriptRes:Bad:"+ "Incorrect host ")
    ssh.close()
    p_res='failed';
  
  # Забираем файл
  scp_from=sLinFile
  scp_to=sDirFile
  sftp=SCPClient(ssh.get_transport())
  sftp.get(scp_from, scp_to) 
  return (p_res)
  
# Процедура получения заданного файла с хоста  
def linPutFile(sHost, sUser, sKey, sLinFile, sDirFile):
  from scp import SCPClient
  p_res='success';
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  sPort=22
  try:
    ssh.connect(hostname=sHost, port=sPort, username=sUser, key_filename=sKey)
  # Обрабатываем ошибки
  except paramiko.ssh_exception.AuthenticationException:
    #print ("ScriptRes:Bad:"+ "Authentification failed")
    ssh.close()
    p_res='failed';
  except paramiko.ssh_exception.SSHException:
    if badCount>1:
      print ("ScriptRes:Bad:"+ "SSH error:" + str(badCount) + ' attempt(s)')
      ssh.close()
      p_res='failed';
  except Exception as e:
    print ("ScriptRes:Bad:"+ "Incorrect host ")
    print(str(e))
    ssh.close()
    p_res='failed';
  
  # Заливаем файл
  scp_to=sLinFile
  scp_from=sDirFile
  sftp=SCPClient(ssh.get_transport())
  sftp.put(scp_from,scp_to)

  
