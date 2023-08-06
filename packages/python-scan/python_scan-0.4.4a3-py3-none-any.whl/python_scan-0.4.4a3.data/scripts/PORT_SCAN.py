try:
    print("\n[♦] Identificando requisitos para la ejecución del programa...\n")
    from host_discover import discove
    import subprocess
    import concurrent.futures
    import time
    import ctypes
    import string
    from datetime import datetime
    import re
    import nvdlib
    import socket
    import pyfiglet
    import sys
    import io
    import os
    import nmap
    from pathlib import Path
    from pyExploitDb import PyExploitDb
    import colorama
    from colorama import Fore
    colorama.init()

    print(Fore.BLUE + "\n[♦]" +
          Fore.YELLOW + " Modulos importados correctamente, procediendo con la ejecución del programa")
    time.sleep(1)
    modules = True

except Exception as e:
    # If there are any errors encountered during the importing of the modules,
    # then we display the error message on the console screen
    print('Existen modulos necesarios que no tiene instalado... \n\n', e)
    exit()

# añadir más opciones, como escaneo de webs (http-enum) / sqlinjection / brute force / etc...
# Añadir Logs en el arhchivo (ip/puertos/vulns/etc...)

if modules:
    nm = nmap.PortScanner()
    open_ports = []


def verifi_tools():

    print(Fore.BLUE + "\n[♦]" +
          Fore.YELLOW + " Verificando herramientas necesarias...")
    time.sleep(1)

    if os.name == "posix":
        if os.system('command -v nmap > /dev/null') != 0:
            print(Fore.RED + "\n[♦] No tienes NMAP instalado...")
            exit()

        if os.system('command -v msfconsole > /dev/null') != 0:
            print(Fore.RED + "\n[♦] No tienes METASPLOIT instalado...")

    else:
        if os.system("where nmap") != 0:
            print(Fore.RED + "\n[♦] No tienes NMAP instalado...")
            exit()

        if os.system("where nmap") != 0:
            print(Fore.RED + "\n[♦] No tienes METASPLOIT instalado...")



def clean():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")


def is_admin():
    if os.name == "posix":
        if os.geteuid() != 0:
            print('ESTA HERRAMIENTA NECESITA PERMISOS DE ADMINISTRADOR / ROOT')
            exit()
        
    else:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            print(Fore.RED + "ESTA HERRAMIENTA NECESITA PERMISOS DE ADMINISTRADOR / ROOT.")
            exit()


def print_help():
    print(Fore.YELLOW + """
        ╔════════════════════════════════════════════════╗
        ║                                                ║
        ║   --  Usabilidad 'PORT SCANNER' v0.4.4.a2 --   ║        
        ║                                                ║
        ╚════════════════════════════════════════════════╝""" +

          Fore.GREEN + "\n\nArgumentos de la herramienta:\n\n" +
          Fore.BLUE + "[♦]" + Fore.YELLOW + " Enter IP --> IP OBETIVO\n" +
    Fore.CYAN + """
            ║       
            ╚═► EJEMPLO --> [♦] ENTER IP -> 127.0.0.1\n""" +

Fore.BLUE + "\n[♦]" + Fore.YELLOW + ' Introduce la cantidad de puertos a escanear - (EJ: 500 - Primeros 500)\n' +

          Fore.CYAN + """ 
            ║       
            ╚═► EJEMPLO --> Introduce cant ports --> 65535 (nº MAX ports)\n""" +


         Fore.YELLOW + "\n\n              -- PROCEDIMIENTO UTILIZADO POR LA HERRAMIENTA --\n\n" +
Fore.CYAN + """1. Se ejecuta un escaneo de puertos para localizar los abiertos

2. Ejecutamos un analisis de servicios de dichos puertos abiertos, identificamos información sobre 
   los servicios encontrados 

3. Iniciamos una busqueda de vulnerabilidades públicas en dichos servicios...

4. Tenemos la opcion de buscar en la base de datos de ExploitDb algún exploit público.

5. Podemos abrir metasploit para utilziar la informacion recopilada
   anteriomente para lo que tengamos que hacer""" +

Fore.GREEN + """\n\nREQUISITOS:\n
            - NMAP
            - Metasploit (opcional)""")


def num_ports():
    global ports
    while True:
        print(Fore.BLUE + "\n[♦]" +
              Fore.YELLOW + ' Introduce la cantidad de puertos a escanear - (EJ: 500 - Primeros 500)')
        ports = input("""
    ╚═► """)
        if 'help' in str(ports):
            clean()
            port_scan_banner()
            print_help()
        else:
            try:
                ports = int(ports)
                if ports > 65535:
                    input('Has superado el número máximo de puertos.\n'
                          'Se reducirá a "65535" (numero máx. de puertos) -- [ENTER]')
                    ports = 65535
                    write_file(f'[!] PORTS TO SCAN ---> 1-{str(ports)}\n')
                else:
                    write_file(f'[!] PORTS TO SCAN ---> 1-{str(ports)}\n')
                break
            except ValueError:
                print(Fore.RED + "Arguemnto inválido.\nPara obtener ayuda escriba --> '--help'")



def port_scan_banner():
    print(Fore.GREEN + """\n
    
                                                                                © 
 ██▓███   ▒█████   ██▀███  ▄▄▄█████▓     ██████  ▄████▄   ▄▄▄       ███▄    █ 
▓██░  ██▒▒██▒  ██▒▓██ ▒ ██▒▓  ██▒ ▓▒   ▒██    ▒ ▒██▀ ▀█  ▒████▄     ██ ▀█   █ 
▓██░ ██▓▒▒██░  ██▒▓██ ░▄█ ▒▒ ▓██░ ▒░   ░ ▓██▄   ▒▓█    ▄ ▒██  ▀█▄  ▓██  ▀█ ██▒
▒██▄█▓▒ ▒▒██   ██░▒██▀▀█▄  ░ ▓██▓ ░      ▒   ██▒▒▓▓▄ ▄██▒░██▄▄▄▄██ ▓██▒  ▐▌██▒
▒██▒ ░  ░░ ████▓▒░░██▓ ▒██▒  ▒██▒ ░    ▒██████▒▒▒ ▓███▀ ░ ▓█   ▓██▒▒██░   ▓██░
▒▓▒░ ░  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░  ▒ ░░      ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ 
░▒ ░       ░ ▒ ▒░   ░▒ ░ ▒░    ░       ░ ░▒  ░ ░  ░  ▒     ▒   ▒▒ ░░ ░░   ░ ▒░
░░       ░ ░ ░ ▒    ░░   ░   ░         ░  ░  ░  ░          ░   ▒      ░   ░ ░ 
             ░ ░     ░                       ░  ░ ░            ░  ░         ░ 
                                                ░                                                                                                 
                                                
       [INFO] Herramienta para analizar puertos de una dirección IP 
             ║                                                 ║                                                                                             
             ║                    v0.4.4.a3                    ║
             ╚══════► Escriba --help para obtener ayuda ◄══════╝
                    \n\n""")


def host_disc_bann():
    print(Fore.RED + '''\n
                               .    .        s              ....             .       .                                 _                                 
  .uef^"                  z`    ^%      :8          .xH888888Hx.        @88>          ^%                          u                                  
:d88E              u.        .   <k    .88        .H8888888888888:      %8P        .   <k                  u.    88Nu.   u.                .u    .   
`888E        ...ue888b     .@8Ned8"   :888ooo     888*"""?""*88888X      .       .@8Ned8"       .    ...ue888b  '88888.o888c      .u     .d88B :@8c  
 888E .z8k   888R Y888r  .@^%8888"  -*8888888    'f     d8x.   ^%88k   .@88u   .@^%8888"   .udR88N   888R Y888r  ^8888  8888   ud8888.  ="8888f8888r 
 888E~?888L  888R I888> x88:  `)8b.   8888       '>    <88888X   '?8  ''888E` x88:  `)8b. <888'888k  888R I888>   8888  8888 :888'8888.   4888>'88"  
 888E  888E  888R I888> 8888N=*8888   8888        `:..:`888888>    8>   888E  8888N=*8888 9888 'Y"   888R I888>   8888  8888 d888 '88%"   4888> '    
 888E  888E  888R I888>  %8"    R88   8888               `"*88     X    888E   %8"    R88 9888       888R I888>   8888  8888 8888.+"      4888>      
 888E  888E u8888cJ888    @8Wou 9%   .8888Lu=       .xHHhx.."      !    888E    @8Wou 9%  9888      u8888cJ888   .8888b.888P 8888L       .d888L .+   
 888E  888E  "*888*P"   .888888P`    ^%888*        X88888888hx. ..!     888&  .888888P`   ?8888u../  "*888*P"     ^Y8888*""  '8888c. .+  ^"8888*"    
m888N= 888>    'Y"      `   ^"F        'Y"        !   "*888888888"      R888" `   ^"F      "8888P'     'Y"          `Y"       "88888%       "Y"      
 `Y"   888                                               ^"***"`         ""                  "P'                                "YP'                 
      J88"                                                                                                                                           
      @%                                                                                                                                             
    :" 
                                [INFO] Herramienta para analizar puertos de una dirección IP                                                                                             
                                     ║                    v0.4.4.a3                    ║
                                     ╚══════► Escriba --help para obtener ayuda ◄══════╝
    
    \n''')


def service_scan_bann():
    print(Fore.GREEN + """\n

.▄▄ · ▄▄▄ .▄▄▄   ▌ ▐·▪   ▄▄· ▄▄▄ .    .▄▄ ·  ▄▄·  ▄▄▄·  ▐ ▄ 
▐█ ▀. ▀▄.▀·▀▄ █·▪█·█▌██ ▐█ ▌▪▀▄.▀·    ▐█ ▀. ▐█ ▌▪▐█ ▀█ •█▌▐█
▄▀▀▀█▄▐▀▀▪▄▐▀▀▄ ▐█▐█•▐█·██ ▄▄▐▀▀▪▄    ▄▀▀▀█▄██ ▄▄▄█▀▀█ ▐█▐▐▌
▐█▄▪▐█▐█▄▄▌▐█•█▌ ███ ▐█▌▐███▌▐█▄▄▌    ▐█▄▪▐█▐███▌▐█ ▪▐▌██▐█▌
 ▀▀▀▀  ▀▀▀ .▀  ▀. ▀  ▀▀▀·▀▀▀  ▀▀▀      ▀▀▀▀ ·▀▀▀  ▀  ▀ ▀▀ █▪                                                                                            
\n""")


def help_discover():
    print(Fore.YELLOW + """
            ╔════════════════════════════════════════════════╗
            ║   --  Usabilidad 'HOST DISCOVER' v0.4.4.a3 --  ║        
            ╚════════════════════════════════════════════════╝\n\n""" +

          Fore.BLUE + "[♦]" + Fore.YELLOW + " Enter IP --> IP OBETIVO\n" +
          Fore.CYAN + """
                ║       
                ╚════ EJEMPLO --> [♦] ENTER IP -> 192.168.1.0/24\n""" +

          Fore.CYAN + """ 
                ║       
                ╚═► """ + Fore.BLUE + "[♦] " + Fore.YELLOW + "REQUERIMIENTO --> " + Fore.YELLOW + 'Mascara en formato CIDR\n\n')


def graph_host():
    print(Fore.BLUE + "\t\t[!] " + Fore.GREEN + '↓ EJEMPLOS ↓ \n')
    print(Fore.LIGHTRED_EX + "\t\t \t║")
    print("\t\t\t║══════► 192.168.1.0/24")
    print("\t\t\t║")
    print("\t\t\t╚══════► --help")
    print(Fore.BLUE + '\n\n\t\t[♦] ' + Fore.YELLOW + 'Enter IP Range')


def init_host():
    now = datetime.now()
    print(Fore.RED + "[!] " + Fore.YELLOW + "Escaneo de subred iniciado...\n")
    print(Fore.RED + "[T] " + Fore.YELLOW + "", now, "\n")


def host_discover():
    clean()
    host_disc_bann()
    target = None
    err = False
    while not target:
        clean()
        host_disc_bann()

        if err:
            graph_host()
            print(Fore.RED + "[!] Has introducido una máscara inválida...")

            print("\t\t\t║")
            target = input("\t\t\t╚═► " + Fore.RESET)

        else:
            # Printear ayuda la 1ª vez que se ejecute
            graph_host()
            print("\t\t\t║")
            target = input("\t\t\t╚═► " + Fore.RESET)

        # Printear ayuda
        if 'help' in target:
            clean()
            host_disc_bann()
            help_discover()
            graph_host()

            print("\t\t\t║")
            target = input("\t\t\t╚═► " + Fore.RESET)

        # Comprobar si está bien escrita la IP
        else:
            mask = re.findall("/([0-9]+)$", target)
            mask = "".join(mask)

            try:
                mask = int(mask)

                # Verificar que la mascara dentro de la lista no supere los 32 y sea int
                if mask > 32:
                    err = True
                    target = None

            # Verificar que sea un número
            except ValueError:
                err = True
                target = None


    clean()
    host_disc_bann()
    init_host()
    discove(target)


def init(now, target):
    # Inicio del analisis, tiempo y objetivo
    print(Fore.YELLOW + "-" * 55)
    print(Fore.GREEN + "[♦] " + Fore.YELLOW + "Objetivo -->" + Fore.RED + f" {target}" +
          Fore.YELLOW + " <--> Nº ports" + Fore.RED + " {}".format(ports))
    print(Fore.GREEN + "[♦] " + Fore.YELLOW + "Analisis iniciado --> {}".format(now))
    print("-" * 55)



def graph(target):
    # Escaneo de puertos gráfico
    clean()
    port_scan_banner()
    num_ports()
    clean()
    port_scan_banner()
    # Banner
    scan(target)


def funcions():
    clean()
    port_scan_banner()
    # Añadir funciones preguntando antes de los puertos.
    print(Fore.BLUE + "[♦]" + Fore.YELLOW + " Que herramienta quieres utilizar?")
    print(Fore.YELLOW + "-" * 50)
    print(Fore.BLUE + 'A:' + Fore.YELLOW + ' --> Port and vuln scan' + '\n \n'
          + Fore.BLUE + 'B:' + Fore.YELLOW + ' --> Metasploit.\n\n'
          + Fore.BLUE + 'C: ' + Fore.YELLOW + '--> Host Discovery\n')
    fun = None
    while not fun:
        fun = input(Fore.YELLOW + "         ╚═► ")
        if 'help' in fun:
            clean()
            port_scan_banner()
            print_help()

            print(Fore.YELLOW + "\nQue herramienta quieres utilizar?")
            print("-" * 50)
            print(Fore.BLUE + 'A:' + Fore.YELLOW + ' --> Port and vuln scan' + '\n \n'
                  + Fore.BLUE + 'B:' + Fore.YELLOW + ' --> Metasploit.\n')
            fun = None

        # Entramos en Port scan
        elif fun.lower() in ['a']:
            enter_arguments()
            funcions()

        # Entramos en metasploit
        elif fun.lower() in ['b']:
            input(Fore.YELLOW + "[!] Esta funcion requiere que tengas instalado Metasploit [-ENTER-].")
            try:
                os.system('msfconsole')
                break
            except Exception as error:
                print(Fore.RED + "[!] ERROR: {}\nPrueba a reinstalar o instalar metasploit.".format(error))

        # Entramos en host discover
        elif fun.lower() in ['c']:
            host_discover()
            funcions()

        else:
            print(Fore.RED + "Introduce una opción válida, has escogido '{}',"
                             " que no está entre las opciones disponibles".format(fun))
            fun = None


def ping(ip_address):
    global alive
    while True:
        clean()
        port_scan_banner()
        # Confirmación con PING?

        p = input(Fore.YELLOW + '[!] ¿Quieres hacer una confirmación con PING?\n\n' + Fore.GREEN
                                + '\t[I] El host puede tener un FireWall bien configurado que bloquee este tipo de paquetes.\n'
            '\t   Si sabes que esta activo no ejecutes la confirmación.' + Fore.LIGHTRED_EX + '\n\n\t[S/n] --> ')

        # En línea o no
        if p in ['S', 's']:

            """
            Pings the given IP address to check if it's active or not.
            """
            response = os.system("ping -n 1 " + ip_address)
            if response == 0:
                alive = True
            else:
                alive = False
            return alive

        elif p in ['n', 'N']:
            alive = None
            break
        else:
            print(Fore.RED + "Indicación inválida... [S/n]")

    return alive


def init_scan(target, now):

    def scaning(port):

        print("\r" + 'Analizando Puerto : %s/%s [%s%s] %.2f%%' % (port, ports, "▓" * int(port * 25 / ports),
                                                    "▒" * (25 - int(port * 25 / ports)),
                                float(port / ports * 100)), end="")

        # Creamos el Socket para la conexión
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Definimos tiempo máximo de espera a la conexion
        socket.setdefaulttimeout(0.15)
        # creamos la conexion
        result = s.connect_ex((target, port))
        # Si resulta victorioisa la conexion informamos de puerto abierto
        if result == 0:
            open_ports.append(port)
            clean()
            port_scan_banner()
            init(now, target)
            for open_port in open_ports:
                print(Fore.BLUE + "[♦]" + Fore.YELLOW + f" - El puerto {open_port} esta abierto.", end="")
                print("\n" + "-" * 55 + "\n", end="")
        s.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = []
        for port in range(1, ports + 1):
            try:
                time.sleep(0.08)
                futures.append(executor.submit(scaning, port))
            # Excepciones del código
            except KeyboardInterrupt:
                end = datetime.now()
                elapsed = end - now
                print(Fore.YELLOW + '\n\nAnálisis interrumpido en el puerto {}.'.format(port))
                write_file(f"\n[!] Port Scan interrupt in port {port} {elapsed}")
                break
            except Exception as err:
                print("Error inesperado : {}".format(err))


def scan(target):
    try:
        # Confirmacion con ping y resultado
        ping(target)
        if alive is None:
            pass

        elif not alive:
            a = None
            while not a:
                a = input(Fore.YELLOW + "¿El host no está en línea, quieres salir del programa...? [S/n]\n")
                if a.lower() == "s":
                    exit()
                elif a.lower() == "n":
                    break
                else:
                    print("Introduccion inválida...")

        # Inicio del analisis.
        clean()
        port_scan_banner()

        if alive:
            print(Fore.YELLOW + 'El HOST está en línea.')
        elif alive is None:
            print(Fore.YELLOW + 'No se ha realizado la confirmación con PING')

    except socket.gaierror:
        print(Fore.RED + "\nNo se ha encontrado el HOST")

    now = datetime.now()
    init(now, target)

    init_scan(target, now)

    # Final del analisis sin puertos
    end = datetime.now()
    if not open_ports:
        elapsed = end - now
        print(Fore.YELLOW + "\nTiempo transcurrido --> {}".format(elapsed))
        print(Fore.YELLOW + "\nNo se han detectado puertos abiertos. :_(")
        write_file("[!] No open Ports exiting the program :'(")
        exit()

    # Final del analisis con puertos encontrados
    print(Fore.YELLOW + "\nTiempo transcurrido --> {}".format((end - now)))
    write_file("[*] END SCAN\n")
    write_file(f"[*] ELAPSED --> {end - now}")
    ports_used(open_ports, target)


def ports_used(open_ports, target):
    # Creamos lista ordenada de puertos para el scaner
    p_str = [str(a) for a in open_ports]
    p_str = (",".join(p_str))
    print(Fore.GREEN + "\n\nLos puertos abiertos son: {}".format(open_ports))

    text = "[!] OPEN PORTS: {}\n".format(p_str)
    write_file(text)

    # Iniciamos check services
    check_serv(target, p_str, open_ports)


def serv_search():
    while True:
        serv = input(Fore.BLUE + "\n[♦]" + Fore.YELLOW +
                     r" ¿Quieres ejecutar un analisis completo a los puertos abiertos? [S/n] --> ")
        if serv in ["S", 's']:
            break
        elif serv in ['n', 'N']:
            print(Fore.YELLOW + 'Has escojido NO hacer el análisis.' + Fore.RED + '\n¿Estas seguro?')
            s = input(Fore.RED + '[S]' + Fore.GREEN + 'alir / ' +
                      Fore.RED + '[E]' + Fore.GREEN + 'scanear' + Fore.YELLOW + '-->')
            if s in ["S", 's']:
                exit()
            else:
                break


def graph_serv(init_scan_service):
    service_scan_bann()
    print(Fore.GREEN + "\n\n" + 54 * "═" + "►")

    print(Fore.YELLOW + """Escaneando versiones de servicio... 
        ╚══════► Esto puede tardar un poco, vale la pena.\n""")
    print("\nAnálisis iniciado --> {}".format(init_scan_service))
    print("-" * 50 + "\n")


def graph_know_nmap(default_args):
    print(Fore.BLUE + "\n[!] " + Fore.YELLOW + "Si eres usuario avanzado con NMAP selecciona la 'A', si no la 'B'\n")
    print(Fore.WHITE + "\n\t[♦] " + Fore.GREEN + "<<< Default Command Line >>> \n")
    print("\t\t║\n")
    print("\t\t╚════► {}\n".format(default_args))
    print(Fore.RED + "\n\t\t\t[A] " + Fore.YELLOW + "NMAP COMMAND LINE")
    print(Fore.BLUE + "\n\t\t\t[B] " + Fore.YELLOW + "Automatic Command Line\n")


def know_nmap():
    clean()
    service_scan_bann()
    default_args = "<ip> -p <prts> --script vuln  -sS --min-rate 5000 -sC -sV -Pn --version-intensity 3 -n -A -O"
    know = None
    first = True

    while not know:
        clean()
        if not first:
            service_scan_bann()
            graph_know_nmap(default_args)
            print(Fore.RED + "No has introducido un caracter válido (e.g -> A | b)")

            know = input("\t\t\t     ╚════► ")
        else:
            service_scan_bann()
            graph_know_nmap(default_args)

            know = input("\t\t\t     ╚════► ")

        if know in ["A", "a"]:
            clean()
            service_scan_bann()
            return process_args()

        elif know in ['B', 'b']:
            return False
        else:
            first = None
            know = None


def graph_args():
    print(Fore.BLUE + "\n   [♦] " + Fore.YELLOW + "Introduce los argumentos de nmap que desees")
    print(Fore.BLUE + "\n   [I] " + Fore.YELLOW + "No introduzcas la IP ni los puertos")


def process_args():
    # Printear grafico
    graph_args()

    args = None
    # Bucle para introducir argumentos válidos
    while not args:
        args = input(Fore.GREEN + "\nArguments >>> ")
        try:
            # Mostramos Ayuda .... JAJAJA
            if args in ["help", "--help"]:
                print(Fore.RED + "\t[!] Introduce 'default' para introducir los argumentos predeterminaods")
                print(Fore.WHITE + "\t[-] ¿?Usuario Avanzado¿?")
                args = None
            # Probamos argumentos
            else:
                return args
        except KeyboardInterrupt:
            return False
        except Exception:
            print(Fore.RED + "[!] Ha ocurrido un error, arguentos de nmap predeterminados")
            return False


def check_args(args, default_args, target, p_str):
    clean()
    service_scan_bann()

    if not args:
        return default_args
    arguments = ["nmap", target, '-p' + p_str, args]

    try:
        print(Fore.YELLOW + "\n\t [!] Comprobando Argumentos...")
        subprocess.check_output(arguments, timeout=5)
        print(Fore.BLUE + "\n\t [+] Argumentos comprobados correctamente...")
        return args

    except subprocess.TimeoutExpired:
        print(Fore.RED + "[!] Error... argumentos inválidos")
        time.sleep(2)
        return default_args
    except subprocess.CalledProcessError:
        print(Fore.RED + "[!] Error... definiendo argumentos predeterminados")
        time.sleep(2)
        return default_args
    except Exception as err:
        print(err)
        time.sleep(2)
        return default_args


def write_info_in_file():
    pass


def check_serv(target, p_str, open_ports):
    # Preguntamos si quiere analisis de versiones de servicio
    serv_search()

    write_file('[!] Service Scan initiate\n')

    # Hora del inicio
    init_scan_service = datetime.now()

    # Argumentos de NMAP default
    default_args = "-p {} --script vuln -sS --min-rate 5000 -sC -sV -Pn --version-intensity 3 -n -A -O".format(p_str)

    args = know_nmap()

    # Comprobar los buenos comandos
    args = check_args(args, default_args, target, p_str)
    write_file(f'[*] Nmap comman line {args}\n')

    # Inicio de análisis de nmap
    clean()

    # Inicio del escaneo
    graph_serv(init_scan_service)
    print(Fore.BLUE + "   [I] " + Fore.YELLOW + "Argumentos utilizados \n\t[{}]".format(args))
    print(Fore.GREEN + "\n" + 54 * "═" + "►")

    nm.scan(target, arguments=args)
    end_service_scan = datetime.now()
    dict_serv = {}

    for p in open_ports:
        p = int(p)

        print(Fore.YELLOW + "Analisis puerto nº{} \n".format(p))
        # Recolectamos información del escaneo de servicion anterior y procesamos los datos .
        # Introducer N/D a los que no se encuentren.
        try:
            state = nm[target]['tcp'][int(p)]['state']
        except Exception:
            state = "N/D"
        try:
            name = nm[target]['tcp'][int(p)]['name']
        except Exception:
            name = "N/D"
        try:
            product = nm[target]['tcp'][int(p)]['product']
        except Exception:
            product = "N/D"
        try:
            version = nm[target]['tcp'][int(p)]['version']
        except Exception:
            version = "N/D"
        try:
            extrainfo = nm[target]['tcp'][int(p)]['extrainfo']
        except Exception:
            extrainfo = "N/D"
        try:
            cpe = nm[target]['tcp'][int(p)]['cpe']
        except Exception:
            cpe = "N/D"
        try:
            all_host = nm[target]['hostscript']
        except KeyError:
            all_host = None
        # Añadimos al diccionario para la búsqueda de vulners
        if product == "":
            dict_serv[p] = {
                'name': name,
                'version': version,
            }
        else:
            dict_serv[p] = {
                'name': product,
                'version': version
            }
        # Printeamos los datos

        try:
            script = [nm[target]['tcp'][int(p)]['script'][ind] for ind in nm[target]['tcp'][int(p)]['script']]
            if len(script) <= 1:
                print(
                    Fore.CYAN + "Puerto: " + Fore.GREEN + f"{p}/{state} \n" + Fore.YELLOW +
                    "<--> Especificaciones del servicio <--> \n" + Fore.BLUE +
                    "[♦]" + Fore.YELLOW + " Nombre:" + Fore.GREEN + f"  {name}  |" +
                    Fore.YELLOW + "  Producto:" + Fore.GREEN + f" {product}   |" +
                    Fore.YELLOW + "  Versión:" + Fore.GREEN + f" {version}  |  {extrainfo}  |  " +
                    Fore.YELLOW + "CPE:" + Fore.GREEN + f" {cpe}  \n\nInfo: \n{script[0]}  \n")

                print(Fore.GREEN + "\n" + "-" * 50, "\n")

                text = f"""Puerto: {p}/{state} \n<--> Especificaciones del servicio <--> \n
    [♦] Nombre: {name}    
    Producto: {product}   
    Versión: {version}  
    Extra Info: {extrainfo}    
    CPE: {cpe}  \n\n
    Info: \n{script[0]}  \n""" + "\n" + "-" * 50 + "\n"

                write_file(f"[!] FOUND INFORMATION ABOUT SERVICE!!\n")
                write_file(text)

            else:
                print(Fore.CYAN +
                      "Puerto: " + Fore.GREEN + f" {p}/{state} \n" + Fore.YELLOW +
                     "<--> Información del servicio <--> \n" + Fore.BLUE + "[♦]" + Fore.YELLOW +
                    " Nombre: " + Fore.GREEN + f"{name}  |   " + Fore.YELLOW + "Producto: " + Fore.GREEN + f"{product}"
                   + Fore.YELLOW + "  |  Versión: " + Fore.GREEN + f"{version}" + Fore.YELLOW + "|  Extra info: " +
                   Fore.GREEN + f"{extrainfo}" + Fore.YELLOW + "|  CPE:" + Fore.GREEN +
                  f"{cpe}  \n\nInfo: \n{script[0]}\n{script[1]}  \n")
                print(Fore.GREEN + "\n"+"-" * 50, "\n")

                text = f"""Puerto:  {p}/{state} \n<--> Información del servicio <--> \n
    [♦] Nombre: {name}
    Producto: {product}  
    Versión: {version}   
    Extra info: {extrainfo}    
    CPE: {cpe}  \n\n
    Info: \n{script[0]}\n{script[1]}  \n""" + "\n"+"-" * 50 + "\n"

                write_file(f"[!] FOUND INFORMATION ABOUT SERVICE!!\n")
                write_file(text)

        except KeyError:
            print(
                Fore.CYAN + "Puerto: " + Fore.GREEN + f"{p}/{state} \n" + Fore.YELLOW +
                "<--> Especificaciones del servicio <--> \n" + Fore.BLUE +
                "[♦]" + Fore.YELLOW + " Nombre:" + Fore.GREEN + f"  {name}"
                                                                "  |  " + Fore.YELLOW + "Producto:" + Fore.GREEN +
                f" {product}    |  " + Fore.YELLOW + "Versión:" + Fore.GREEN + f" {version}  |  {extrainfo}  |  " +
                Fore.YELLOW + "CPE:" + Fore.GREEN + f" {cpe} \n")
            print(Fore.GREEN + "\n" + "-" * 50)

            text = f"""Puerto: {p}/{state} \n<--> Especificaciones del servicio <--> \n
    [♦] Nombre: {name}    
    Producto: {product}    
    Versión: {version}  
    Extra Info: {extrainfo}    
    CPE: {cpe} \n""" + "\n" + "-" * 50 + "\n"

            write_file(f"[!] FOUND INFORMATION ABOUT SERVICE!!\n")
            write_file(text)

    if all_host is not None:
        if len(all_host) > 1:
            print(Fore.YELLOW + "OUTPUTS")
            for information in range(len(all_host)):
                ids = all_host[information]['id']
                if ids == "clock-skew":
                    continue
                else:
                    output = all_host[information]['output']
                    print(Fore.GREEN + f"\n {ids} : {output}")
                    print(Fore.GREEN + "\n" + "═" * 30 + "►", "\n")

    print_information(target, end_service_scan, init_scan_service, dict_serv)


def print_information(target, end_service_scan, init_scan_service, dict_serv):
    # Tipo de sistema encontrado
    try:
        ip = nm[target]['addresses']['ipv4']
    except Exception:
        ip = "N/D"
    try:
        ip_vendor = nm[target]['vendor']
    except Exception:
        ip_vendor = "N/D"
    try:
        name_os = nm[target]['osmatch'][0]['name']
    except Exception:
        name_os = "N/D"
    try:
        accuracy = nm[target]['osmatch'][0]['accuracy']
    except Exception:
        accuracy = "N/D"
    try:
        vendor = nm[target]['osmatch'][0]['osclass'][0]['vendor']
    except Exception:
        vendor = "N/D"
    try:
        sys_cpe = nm[target]['osmatch'][0]['osclass'][0]['cpe'][0]
    except Exception:
        sys_cpe = "N/D"

    def how_print():
        if ip_vendor == "N/D":
            return ip_vendor
        else:
            return [data for data in ip_vendor]

    # Imprimimos la informacion del sistema
    print(Fore.YELLOW + "\nINFORMACIÓN DEL SISTEMA OBJETIVO")
    print(Fore.GREEN + "═" * 50 + "►", "\n")
    print(Fore.BLUE + "SISTEMA " + Fore.YELLOW + "-->" + Fore.GREEN + f" {name_os}\n")
    print(Fore.GREEN + "═" * 50 + "►", "\n")
    print(Fore.BLUE + "Precisión " + Fore.YELLOW + "--> " + Fore.GREEN + f"{accuracy}\n")
    print(Fore.GREEN + "═" * 50 + "►", "\n")
    print(Fore.BLUE + "Vendedor " + Fore.YELLOW + "--> " + Fore.GREEN + f"{vendor}\n")
    print(Fore.GREEN + "═" * 50 + "►", "\n")
    print(Fore.BLUE + "CPE " + Fore.YELLOW + "--> " + Fore.GREEN + f"{sys_cpe}\n")
    print(Fore.GREEN + "═" * 50 + "►", "\n")
    print(Fore.BLUE + "IP " + Fore.YELLOW + "--> " + Fore.GREEN + f"{ip}\n")
    print(Fore.GREEN + "═" * 50 + "►", "\n")
    print(Fore.BLUE + "MAC & Vendor " + Fore.YELLOW + "--> " + Fore.GREEN + f"{how_print()}")

    elapsed = (end_service_scan - init_scan_service)
    print(Fore.GREEN + "\n" + "-" * 50)
    print(Fore.GREEN + "Tiempo transcurrido duante el analisis -> {}".format(elapsed))

    write_file("\nINFORMACIÓN DEL SISTEMA OBJETIVO" + "═" * 50 + "►" + "\n" + "SISTEMA -->" + f" {name_os}\n"
               + "═" * 50 + "►" + "\n" + "Precisión --> " + f"{accuracy}\n" + "═" * 50 + "►" + "\n" + "Vendedor --> " +
                            f"{vendor}\n" + "═" * 50 + "►" + "\n" + "CPE --> " + f"{sys_cpe}\n" + "═" * 50 + "►" + "\n" +
               "IP --> " + f"{ip}\n" + "═" * 50 + "►" + "\n" + "MAC & Vendor --> " + f"{how_print()}")

    vlnsrch(dict_serv)


def vlnsrch(dict_serv):
    # Analisis de vulners?
    while True:
        vuln = input(
            Fore.YELLOW + "\n[♦] ¿Quieres ejecutar un analisis de vulnerabilidades "
                          "a los servicios analizados? [S/n] --> ")
        if vuln in ['S', 's']:
            scan_vuln_services(dict_serv)
            break
        elif vuln in ['N', 'n']:
            exit()
        else:
            print(Fore.RED + 'Introduzca una opción válida... [S/n]')


def graph_vuln():
    ascii_part_2 = pyfiglet.figlet_format("Vulner SCAN")
    print(Fore.YELLOW + ascii_part_2)
    print('Contactando con la base de datos, espere porfavor')


def scan_vuln_services(dict_serv):
    # Banner vulerns
    graph_vuln()

    count = 0
    vulner = {}

    # Busqueda de vulers
    for prt in dict_serv:
        name = dict_serv[prt]['name']
        version = dict_serv[prt]['version']
        service = "{} {}".format(name, version)

        if version == "":
            print(Fore.RED + f'\n[-] No se ha detectado una versión en el serivcio {name}'
                             f', falta de información para continuar la busqueda.')
            continue

        try:
            # Escogemos la mejor opcion o la mas exacta.
            results = nvdlib.searchCVE(keywordSearch=service)[0]
            if name and version not in results:
                results = nvdlib.searchCVE(keywordSearch=service)[1]

            # Procesamos los datos
            cve = results.id
            cpe = results.cpe[0].criteria
            date = results.lastModified
            desc = results.descriptions[0].value
            dificulty = results.metrics.cvssMetricV2[0].cvssData.accessComplexity
            exploit_score = results.v2exploitability
            severity = results.v2severity
            access = results.metrics.cvssMetricV2[0].cvssData.accessVector
            url = results.references[0].url

            print(Fore.GREEN + "\n[+] " + Fore.RED + "VULNERABILIDAD -> P: " + Fore.GREEN + f"{prt}" +
                  Fore.RED + " | SERVICE: " + Fore.GREEN + f"{service}")
            print(Fore.GREEN + "\n═══════════════════════════════════════════════════►")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "CVE: " + Fore.GREEN + f"{cve}")
            print(Fore.GREEN + "\n-------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "CPE: " + Fore.GREEN + f"{cpe}")
            print(Fore.GREEN + "\n-------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "Date: " + Fore.GREEN + f"{date}")
            print(Fore.GREEN + "\n-------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "Dificulty: " + Fore.GREEN + f"{dificulty}")
            print(Fore.GREEN + "\n------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "Severity: " + Fore.GREEN + f"{severity}")
            print(Fore.GREEN + "\n------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "Risk Score: " + Fore.GREEN + f"{exploit_score}")
            print(Fore.GREEN + "\n-------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "How to acces: " + Fore.GREEN + f"{access}")
            print(Fore.GREEN + "\n-------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "Desciption: " + Fore.GREEN + f"{desc}")
            print(Fore.GREEN + "\n-------------------------------------------------")
            print(Fore.BLUE + "\n[♦] " + Fore.RED + "URL: " + Fore.GREEN + f"{url}")
            print(Fore.GREEN + "\n═══════════════════════════════════════════════════►\n\n")

            vulner[cve] = {"name": name,
                           "service": service}
            count += 1

        # Excepciones para no vulenr
        except IndexError:
            print(Fore.RED + "\n[-] No vulnerabildades detectadas en el servicio {}".format(service))
        except TimeoutError:
            print(Fore.RED + "\n[-] La base de datos no ha respondido a la solicitud...")
            pass

    if count == 0:
        print(Fore.RED + "\n[-] No se han detectado vulnerabilidades públicas en los sevicios...")
        exit()
    else:
        expsrch(vulner)


def expsrch(vulner):
    while True:
        # Buscamos exploits públicos?
        search_exp = input(Fore.YELLOW + '\n¿Deseas buscar exploits en la base de datos de EXPLOITdB? [S/n]')
        if search_exp in ['s', 'S']:
            search_exploit(vulner)
            break
        elif search_exp in ['n', 'N']:
            print("Has escogido NO buscar el exploit.\n")
            if input('¿Seguro?  [C]errar/[B]uscar ->') in ['c', 'C']:
                print("Cerrando programa")
                exit()
            else:
                search_exploit(vulner)
        else:
            print(Fore.RED + "Opción inválida...")


def no_print(pedb):
    # Creamos un objeto StringIO vacío que descarta los datos
    fake_stdout = io.StringIO()
    # Redirigimos la salida estándar a nuestro objeto StringIO falso
    sys.stdout = fake_stdout
    # Abrimos y actualizamos base de datos
    pedb.openFile()
    # Restauramos la salida estándar original
    sys.stdout = sys.__stdout__


def search_exploit(vulner):
    # Preparamos la busqueda de exploits
    pedb = PyExploitDb()
    pedb.debug = False
    input(Fore.YELLOW + "Esto puede tardar un poco y algunos antivirus lo detectan como virus."
                        " Tendremos a nuestra disposición todos los exploits públicos de ExploitdB."
                        " \n[ENTER] -- [CTRL + C]/Salir \n")

    # Actualizamos abse de datos sin printear en consola
    no_print(pedb)

    count = 0
    # Buscamos los exploits
    for vlr in vulner:
        results = pedb.searchCve(vlr)
        try:
            if not results:
                print(Fore.RED + "[-] No se han encontrado exploits públicos para el CVE: {}".format(vlr))
                print("\n", "-" * 50)

            # Procesamos los datos
            else:

                count += 1
                location = results['file']
                date = results['date']
                sistem = results['type']
                afect = results['platform']
                desc = results['description']
                url = results['app_url']

                # Printeamos los datos
                print(Fore.YELLOW + '[✚] EXPLOIT ENCONTRADO -> {} '.format(vlr))
                print(Fore.GREEN + """
═══════════════════════════════════════════════════►
[♦] Location: {} 
-------------------------------------------------
[♦] Date: {}              
-------------------------------------------------
[♦] Type: {} 
-------------------------------------------------
[♦] Afected Plataform: {}
-------------------------------------------------
[♦] Desciption: {}                        
-------------------------------------------------                                   
[♦] Exploit URL: {}                              
═══════════════════════════════════════════════════►\n""".format(location, date, sistem, afect, desc, url))
                print("-" * 50, "\n")

        # No exploit encontrado
        except TypeError:
            print(Fore.RED + '[-] No EXPLOIT encontrado en la base de datos.')
            print("-" * 50, "\n")
    if count == 0:
        print(Fore.RED + '[-] No se han ecnontrado exploits :·( ')


def enter_arguments():
    ip = None
    while not ip:
        try:
            clean()
            port_scan_banner()
            ip = input(Fore.BLUE + "[♦]" + Fore.YELLOW + " Enter IP --> ")
            # change hostname to IPv4
            if "help" in ip:
                clean()
                port_scan_banner()
                print_help()
                ip = input(Fore.BLUE + "\n[♦]" + Fore.YELLOW + " Enter IP --> ")
            elif re.findall("[.]", ip) == [".", ".", "."]:
                veryfy = ip.split(".")
                for num in veryfy:
                    if int(num) < 255:
                        continue
                    else:
                        print("\nDirección IPv4 inválida.")
                        time.sleep(2)
                        ip = None
                if ip is not None:
                    try:
                        write_file('[*] ¡¡Port Scan iniciado!!\n')
                        write_file("[!] TARGET ---> " + ip)
                        target = socket.gethostbyname(ip)
                        clean()
                        graph(target)

                    except socket.gaierror:
                        print('Direccion IPv4 inválida')
                        time.sleep(2)
                        ip = None

            else:
                print(Fore.RED + "Dirección IPv4 inválida")
                time.sleep(2)
                ip = None

        except ValueError:
            print('Debes introducir NUMEROS...')
            print(Fore.RED + """
                ║
                ╠══════► Obligatorio --> Direccion IP / Puertos a analizar.  
                ║
                ╠══════► Tipología   --> <name_script>   
                ║  
                ╚══════► EJEMPLO 	 --> port_scaner """)
            time.sleep(2.5)


def get_user_path():
    return "{}/".format(Path.home())


def write_file(text):
    userpath = get_user_path()
    location = userpath + "/Desktop/"
    filename = "scan.log"

    with open(location + filename, "a", encoding="utf-8") as log:
        now = str(time.ctime())
        log.write("\n<<< " + now + " >>> " + text)


def main():
    try:
        # Añadirmos el texto inicial en el archivo
        text = "PREPARING SCAN PORTS\n" + "═" * 60 + "\n"

        # Creamos archivo y añadimos el inicio
        write_file(text)

        # Empezamos código limpiando pantalla
        clean()

        # Miramos si eres admin / root
        is_admin()

        # Verificamos NMAP
        verifi_tools()

        # Iniciamos la herramienta
        funcions()

    # Salida con CTRL + C
    except KeyboardInterrupt:
        print("\n\nSaliendo del programa...")

        # Añadimos salida en el texto de salida
        text = "EXITING PROGRAM...\n" + "═" * 60 + "\n"
        write_file(text)

        # Salimos del programa
        exit()


if __name__ == "__main__":
    # Ejecutamos la función principal
    main()
