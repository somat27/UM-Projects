#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h> // Fornece definições de tipos de dados usados por chamadas de sistema. Por exemplo, pid_t (para IDs de processo) é definido aqui.
#include <sys/wait.h> // Contém declarações relacionadas ao controle de processos, incluindo a função wait.
#include <unistd.h> // Contém definições para chamadas de sistema e constantes, como fork, exec, pipe e close.
#include <dirent.h> // Para manipulação de diretórios e a estrutura DIR.
#include <fcntl.h> // Para as constantes usadas na chamada open.
#include <time.h>
#include <signal.h>

#define INTERVALO 10

typedef struct {
    int found;
    const char *operator;
    int argc_cmd1;
    char **argv_cmd1;
    int argc_cmd2;
    char **argv_cmd2;
} comands;

typedef struct {
    int pid;
    char Estado;
    char Username[256];
    char Linha_Comando[256];
} Info_Processo;

comands parse(char *argv[], int argc);
void executarComandos(comands Resultado_Parse);
void executarComandoTop();
char *Obter_Nome_Estado_Processo(char estado);

void alarmHandler(int signum) {
    /*Criamos um novo alarme para voltar a ativar o sinal passado 10 segundos
    formando assim um loop infinito*/
    executarComandoTop();
    alarm(INTERVALO); // Configura o próximo alarme
}

int main(int argc, char *argv[]) {
    struct timeval timeout;
    char input;
    if (argc < 2) {
        printf("Uso: %s <argumento>\n", argv[0]);
        return EXIT_FAILURE;
    }

    comands Resultado_Parse = parse(argv+1, argc-1);

    if (strcmp(Resultado_Parse.argv_cmd1[0], "top") == 0) {
        /*Criamos um sinal que executa a função 'alarmHandler' sempre que o alarme
        ativar, e em baixo estamos a criar um alarme com 10 segundos de espera.
        Apesar de criarmos um sinal o codigo que se segue esta em funcionamento, 
        neste caso é um loop infino a espera de um input 'q'*/
        executarComandoTop();
        signal(SIGALRM, alarmHandler);
        alarm(INTERVALO); // Configura o primeiro alarme

        while (1) {
            char input;
            scanf(" %c", &input);

            if (input == 'q') {
                break;
            }
        }
    }else{
        executarComandos(Resultado_Parse);
    }

    // libertar memoria
    for (int i = 0; i < Resultado_Parse.argc_cmd1; i++) {
        free(Resultado_Parse.argv_cmd1[i]);
    }
    free(Resultado_Parse.argv_cmd1);
    
    if(Resultado_Parse.found) {
        for (int i = 0; i < Resultado_Parse.argc_cmd2; i++) {
            free(Resultado_Parse.argv_cmd2[i]);
        }
        free(Resultado_Parse.argv_cmd2);
    }

    return EXIT_SUCCESS;
}

comands parse(char *argv[], int argc) {
    comands result;

    result.found = 0;
    result.operator = NULL;
    result.argc_cmd1 = 0;
    result.argc_cmd2 = 0;
    result.argv_cmd1 = NULL;
    result.argv_cmd2 = NULL;

    int found = 0;
    for (int i = 0; i < argc; i++) {
    
        if (strcmp(argv[i], ">") == 0 || strcmp(argv[i], "<") == 0 || strcmp(argv[i], "|") == 0) {
            found++;
            if (found > 1) {
                printf("Só pode inserir um operador!\n");
                exit(0);
            }
            result.found = 1;
            result.operator = argv[i];
            continue;
        }

        if (!found) {
            // Adiciona argumentos no contexto do cmd1
            result.argv_cmd1 = realloc(result.argv_cmd1, (result.argc_cmd1 + 1) * sizeof(char *));
            result.argv_cmd1[result.argc_cmd1] = strdup(argv[i]);
            result.argc_cmd1++;
        } else {
            // Adiciona argumentos no contexto do cmd2
            result.argv_cmd2 = realloc(result.argv_cmd2, (result.argc_cmd2 + 1) * sizeof(char *));
            result.argv_cmd2[result.argc_cmd2] = strdup(argv[i]);
            result.argc_cmd2++;
        }
    }
    
    result.argv_cmd1 = realloc(result.argv_cmd1, (result.argc_cmd1 + 1) * sizeof(char *));
    result.argv_cmd1[result.argc_cmd1] = NULL;
    if (found) {
        result.argv_cmd2 = realloc(result.argv_cmd2, (result.argc_cmd2 + 1) * sizeof(char *));
        result.argv_cmd2[result.argc_cmd2] = NULL;
    }

    return result;
}

void executarComandos(comands Resultado_Parse) {
    if (Resultado_Parse.found && strcmp(Resultado_Parse.operator, "|") == 0) {
        int pipefd[2];
        if (pipe(pipefd) == -1) {
            perror("Erro ao criar o pipe");
            exit(EXIT_FAILURE);
        }
        pid_t Fork = fork();
        if (Fork == -1) {
            perror("Erro no fork");
            exit(EXIT_FAILURE);
        } else if (Fork == 0) {  
            // Processo filho
            close(pipefd[0]);
            dup2(pipefd[1], 1); 
            close(pipefd[1]);

            execlp(Resultado_Parse.argv_cmd1[0], Resultado_Parse.argv_cmd1[0], Resultado_Parse.argv_cmd1[1], NULL);
            
            perror("Erro ao executar o comando");
            exit(EXIT_FAILURE);
        } else {  
            // Processo pai
            close(pipefd[1]);
            dup2(pipefd[0], 0);
            close(pipefd[0]);

            execlp(Resultado_Parse.argv_cmd2[0], Resultado_Parse.argv_cmd2[0], Resultado_Parse.argv_cmd2[1], NULL);
            
            perror("Erro ao executar o comando");
            exit(EXIT_FAILURE);
        }
    } else {
        pid_t Fork = fork();
        if (Fork == -1) {
            perror("Erro ao criar processo filho");
            exit(EXIT_FAILURE);
        }
        if (Fork == 0) {
            // Processo filho
            if (Resultado_Parse.found && strcmp(Resultado_Parse.operator, ">") == 0) {
            int file_desc = open(Resultado_Parse.argv_cmd2[0], O_WRONLY | O_CREAT | O_TRUNC, 0644);

                if(file_desc == -1) {
                    perror("Erro ao abrir o arquivo");
                    exit(EXIT_FAILURE);

                }
                dup2(file_desc, 1);
            }else if (Resultado_Parse.found && strcmp(Resultado_Parse.operator, "<") == 0) {
                int file_desc = open(Resultado_Parse.argv_cmd2[0], O_RDONLY);
                if(file_desc == -1) {
                    perror("Erro ao abrir o arquivo");
                    exit(EXIT_FAILURE);

                }
                dup2(file_desc, 0);
            }
            execlp(Resultado_Parse.argv_cmd1[0], Resultado_Parse.argv_cmd1[0], Resultado_Parse.argv_cmd1[1], NULL);
            
            perror("Erro ao executar comando");
            exit(EXIT_FAILURE);
        } else if (Fork > 0) {
            // Processo pai
            int Status_Fork;
            if (waitpid(Fork, &Status_Fork, 0) == -1) {
                perror("Erro ao esperar pelo processo filho");
                exit(EXIT_FAILURE);
            }
        } 
    }
}

void executarComandoTop() {
    system("clear");
    /*
        Carga Media do CPU (1, 5 e 15 minutos)
        Numero total de processos e número total de processos no estado running
    */
    char Infos_loadavg[256];
    int FILE_loadavg = open("/proc/loadavg", O_RDONLY);

    ssize_t Ler_Ficheiro_cmdline = read(FILE_loadavg, Infos_loadavg, sizeof(Infos_loadavg));

    float CPU_Media_1, CPU_Media_5, CPU_Media_15;
    int N_Processos_Running, N_Processos_Total;
    
    sscanf(Infos_loadavg, "%f %f %f %d/%d", &CPU_Media_1, &CPU_Media_5, &CPU_Media_15, &N_Processos_Running, &N_Processos_Total);

    printf("|-------------------------------------------------------------------------|\n");
    printf("| Carga Media CPU (1min, 5min, 15min): %.2f, %.2f, %.2f %-17s |\n", CPU_Media_1, CPU_Media_5, CPU_Media_15, "");
    printf("| Processos Totais: %d | Processos Running: %d %-26s |\n", N_Processos_Total, N_Processos_Running, "");
    
    close(FILE_loadavg);
    /*
        Apresenta ainda a
        informação sobre os processos correntemente ativos no
        sistema, nomeadamente o pid, o estado, a linha de
        comando e o username
    */
    printf("|-------------------------------------------------------------------------|\n");
    printf("| %-7s | %-10s | %-15s | %-30s |\n", "PID", "Estado", "Username", "Linha de Comando");
    printf("|-------------------------------------------------------------------------|\n");

    DIR *Diretorias;
    struct dirent *Ficheiros;
    /*
        Criar um estrutura para guardar as infos dos processos
        para mais a frente poder contabilizar quantos running existem 
        e ai exibit por ordem
    */
    Info_Processo Processos_Running[20];
    Info_Processo Processos_Restantes[20];
    int Total_Processos_Running = 0;
    int Total_Processos_Restantes = 0;

    Diretorias = opendir("/proc/");
    while ((Ficheiros = readdir(Diretorias)) != NULL && (Total_Processos_Running < 20 || Total_Processos_Restantes < 20)) {
        int pid = atoi(Ficheiros->d_name);
        if(pid > 0) { // o atoi faz com que os nomes dos ficheiros que nao tenham numeros viram 0 e da erro mais a frente
            // FILE: cmdline (Linha de Comando)
            char PATH_cmdline[256];
            sprintf(PATH_cmdline, "/proc/%d/cmdline", pid);
            int FILE_cmdline = open(PATH_cmdline, O_RDONLY);

            // Verificar se da para abrir os arquivos
            if (FILE_cmdline == -1) {
                perror("Erro ao abrir o arquivo");
                exit(EXIT_FAILURE);
            }

            // Ler as infos do arquivo cmdline
            char Infos_cmdline[256];
            ssize_t Ler_Ficheiro_cmdline = read(FILE_cmdline, Infos_cmdline, sizeof(Infos_cmdline));
            if (Ler_Ficheiro_cmdline == -1) {
                perror("Error reading file");
                close(FILE_cmdline);
                exit(EXIT_FAILURE);
            }

            // FILE: status (Pid, Estado, Username)
            char PATH_status[256];
            sprintf(PATH_status, "/proc/%d/status", pid);
            int FILE_status = open(PATH_status, O_RDONLY);

            // Verificar se da para abrir os arquivos
            if (FILE_status == -1) {
                perror("Erro ao abrir o arquivo");
                exit(EXIT_FAILURE);
            }

            // Ler as infos do arquivo status
            char Infos_status[256];
            ssize_t Ler_Ficheiro_status = read(FILE_status, Infos_status, sizeof(Infos_status));
            if (Ler_Ficheiro_status == -1) {
                perror("Error reading file");
                close(FILE_status);
                exit(EXIT_FAILURE);
            }
            
            char Estado_Processo; // É apenas uma Letra
            char Username[256];
            char *Posicao_State = strstr(Infos_status, "State:"); // Vai procurar por um State no Infos e vai guardar tudo o que estiver a seguir
            if (Posicao_State != NULL) {
                sscanf(Posicao_State, "State: %c", &Estado_Processo); // Vai a posição e copia o valor que esta a seguir a State
            } else {
                Estado_Processo = '?';
            }

            char *Posicao_UID = strstr(Infos_status, "Uid:");
            if (Posicao_UID != NULL) {
                uid_t UID;
                sscanf(Posicao_UID, "Uid: %d", &UID);

                // Descobrir nome pelo /etc/passwd/
                FILE *FILE_passwd = fopen("/etc/passwd", "r");
                if (FILE_passwd == NULL) {
                    perror("Erro ao abrir o arquivo /etc/passwd");
                    exit(EXIT_FAILURE);
                }

                int UID_passwd;
                char Linha[256];
                while (fgets(Linha, sizeof(Linha), FILE_passwd) != NULL) { // Guarda a info de cada linha do Ficheiro
                    char nomeUsuario[256];
                    //%[^:] copia tudo ate encontrar :
                    sscanf(Linha, "%[^:]:x:%d:", nomeUsuario, &UID_passwd); // Procura aquele formato "username:x:UID" e copia para as variaveis
                    if (UID_passwd == UID) {
                        strncpy(Username, nomeUsuario, sizeof(Username));
                        break;
                    }
                }

                fclose(FILE_passwd);
            } else {
                strncpy(Username, "Desconhecido", sizeof(Username));
            }


            if (Estado_Processo == 'R' && Total_Processos_Running < 20) {
                Processos_Running[Total_Processos_Running].pid = pid;
                Processos_Running[Total_Processos_Running].Estado = Estado_Processo;
                strcpy(Processos_Running[Total_Processos_Running].Username, Username);
                strcpy(Processos_Running[Total_Processos_Running].Linha_Comando, Infos_cmdline);
                Total_Processos_Running++;
            } else if (Total_Processos_Restantes < 20) {
                Processos_Restantes[Total_Processos_Restantes].pid = pid;
                Processos_Restantes[Total_Processos_Restantes].Estado = Estado_Processo;
                strcpy(Processos_Restantes[Total_Processos_Restantes].Username, Username);
                strcpy(Processos_Restantes[Total_Processos_Restantes].Linha_Comando, Infos_cmdline);
                Total_Processos_Restantes++;
            }

            // Fechar ficheiros
            close(FILE_status);
            close(FILE_cmdline);
        }
    }

    // Imprimir as informaçãoes todas
    for(int i = 0; i < Total_Processos_Running; i++){
        printf("| %-7d | %-10s | %-15s | %-30s |\n", 
            Processos_Running[i].pid, 
            Obter_Nome_Estado_Processo(Processos_Running[i].Estado), 
            Processos_Running[i].Username, 
            Processos_Running[i].Linha_Comando
        );
    }
    for(int i = 0; i < Total_Processos_Restantes-Total_Processos_Running; i++){
        printf("| %-7d | %-10s | %-15s | %-30s |\n", 
            Processos_Restantes[i].pid, 
            Obter_Nome_Estado_Processo(Processos_Restantes[i].Estado), 
            Processos_Restantes[i].Username, 
            Processos_Restantes[i].Linha_Comando
        );
    }
    printf("|-------------------------------------------------------------------------|\n");
    printf("Esta informacao sera atualizada a cada %d segundos, pressione 'q' para sair!\n", INTERVALO);
}

char *Obter_Nome_Estado_Processo(char estado) {
    switch (estado) {
        case 'R': return "Running";
        case 'S': return "Sleeping";
        case 'I': return "Idle";
        default: return "Desconhecido";
    }
}