#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <dirent.h>
#include <fcntl.h>
#include <time.h>
#include <signal.h>

#define INTERVAL_SECONDS 10

typedef struct {
    int found;
    const char *operator;
    int argc_cmd1;
    char **argv_cmd1;
    int argc_cmd2;
    char **argv_cmd2;
} Commands;

typedef struct {
    int pid;
    char state;
    char username[256];
    char command_line[256];
} ProcessInfo;

Commands parse(char *argv[], int argc);
void executeCommands(Commands parsed);
void runTop();
char *getProcessStateName(char state);

void alarmHandler(int signum) {
    runTop();
    alarm(INTERVAL_SECONDS);
}

int main(int argc, char *argv[]) {
    char input;
    if (argc < 2) {
        printf("Usage: %s <argument>\n", argv[0]);
        return EXIT_FAILURE;
    }

    Commands parsed = parse(argv+1, argc-1);

    if (strcmp(parsed.argv_cmd1[0], "top") == 0) {
        runTop();
        signal(SIGALRM, alarmHandler);
        alarm(INTERVAL_SECONDS);

        while (1) {
            char input;
            scanf(" %c", &input);

            if (input == 'q') {
                break;
            }
        }
    } else {
        executeCommands(parsed);
    }

    for (int i = 0; i < parsed.argc_cmd1; i++) {
        free(parsed.argv_cmd1[i]);
    }
    free(parsed.argv_cmd1);
    
    if(parsed.found) {
        for (int i = 0; i < parsed.argc_cmd2; i++) {
            free(parsed.argv_cmd2[i]);
        }
        free(parsed.argv_cmd2);
    }

    return EXIT_SUCCESS;
}

Commands parse(char *argv[], int argc) {
    Commands result;

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
                printf("Only one operator is allowed!\n");
                exit(0);
            }
            result.found = 1;
            result.operator = argv[i];
            continue;
        }

        if (!found) {
            result.argv_cmd1 = realloc(result.argv_cmd1, (result.argc_cmd1 + 1) * sizeof(char *));
            result.argv_cmd1[result.argc_cmd1] = strdup(argv[i]);
            result.argc_cmd1++;
        } else {
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

void executeCommands(Commands parsed) {
    if (parsed.found && strcmp(parsed.operator, "|") == 0) {
        int pipefd[2];
        if (pipe(pipefd) == -1) {
            perror("Error creating pipe");
            exit(EXIT_FAILURE);
        }
        pid_t Fork = fork();
        if (Fork == -1) {
            perror("Error on fork");
            exit(EXIT_FAILURE);
        } else if (Fork == 0) {
            close(pipefd[0]);
            dup2(pipefd[1], 1);
            close(pipefd[1]);

            execlp(parsed.argv_cmd1[0], parsed.argv_cmd1[0], parsed.argv_cmd1[1], NULL);
            
            perror("Error executing command");
            exit(EXIT_FAILURE);
        } else {
            close(pipefd[1]);
            dup2(pipefd[0], 0);
            close(pipefd[0]);

            execlp(parsed.argv_cmd2[0], parsed.argv_cmd2[0], parsed.argv_cmd2[1], NULL);
            
            perror("Error executing command");
            exit(EXIT_FAILURE);
        }
    } else {
        pid_t Fork = fork();
        if (Fork == -1) {
            perror("Error creating child process");
            exit(EXIT_FAILURE);
        }
        if (Fork == 0) {
            if (parsed.found && strcmp(parsed.operator, ">") == 0) {
                int file_desc = open(parsed.argv_cmd2[0], O_WRONLY | O_CREAT | O_TRUNC, 0644);
                if(file_desc == -1) {
                    perror("Error opening file");
                    exit(EXIT_FAILURE);
                }
                dup2(file_desc, 1);
            } else if (parsed.found && strcmp(parsed.operator, "<") == 0) {
                int file_desc = open(parsed.argv_cmd2[0], O_RDONLY);
                if(file_desc == -1) {
                    perror("Error opening file");
                    exit(EXIT_FAILURE);
                }
                dup2(file_desc, 0);
            }
            execlp(parsed.argv_cmd1[0], parsed.argv_cmd1[0], parsed.argv_cmd1[1], NULL);
            
            perror("Error executing command");
            exit(EXIT_FAILURE);
        } else if (Fork > 0) {
            int status;
            if (waitpid(Fork, &status, 0) == -1) {
                perror("Error waiting for child process");
                exit(EXIT_FAILURE);
            }
        } 
    }
}

void runTop() {
    system("clear");
    char loadavg_buf[256];
    int fd_loadavg = open("/proc/loadavg", O_RDONLY);

    ssize_t r_cmdline = read(fd_loadavg, loadavg_buf, sizeof(loadavg_buf));
    (void)r_cmdline;

    float cpu_avg_1, cpu_avg_5, cpu_avg_15;
    int procs_running, procs_total;
    
    sscanf(loadavg_buf, "%f %f %f %d/%d", &cpu_avg_1, &cpu_avg_5, &cpu_avg_15, &procs_running, &procs_total);

    printf("|-------------------------------------------------------------------------|\n");
    printf("| CPU Load Avg (1m, 5m, 15m): %.2f, %.2f, %.2f %-17s |\n", cpu_avg_1, cpu_avg_5, cpu_avg_15, "");
    printf("| Total Processes: %d | Running: %d %-26s |\n", procs_total, procs_running, "");
    
    close(fd_loadavg);
    printf("|-------------------------------------------------------------------------|\n");
    printf("| %-7s | %-10s | %-15s | %-30s |\n", "PID", "State", "Username", "Command Line");
    printf("|-------------------------------------------------------------------------|\n");

    DIR *dirs;
    struct dirent *direntp;
    ProcessInfo running[20];
    ProcessInfo others[20];
    int total_running = 0;
    int total_others = 0;

    dirs = opendir("/proc/");
    while ((direntp = readdir(dirs)) != NULL && (total_running < 20 || total_others < 20)) {
        int pid = atoi(direntp->d_name);
        if(pid > 0) {
            char path_cmdline[256];
            sprintf(path_cmdline, "/proc/%d/cmdline", pid);
            int fd_cmdline = open(path_cmdline, O_RDONLY);

            if (fd_cmdline == -1) {
                perror("Error opening file");
                exit(EXIT_FAILURE);
            }

            char info_cmdline[256];
            ssize_t n_cmdline = read(fd_cmdline, info_cmdline, sizeof(info_cmdline));
            if (n_cmdline == -1) {
                perror("Error reading file");
                close(fd_cmdline);
                exit(EXIT_FAILURE);
            }

            char path_status[256];
            sprintf(path_status, "/proc/%d/status", pid);
            int fd_status = open(path_status, O_RDONLY);

            if (fd_status == -1) {
                perror("Error opening file");
                exit(EXIT_FAILURE);
            }

            char info_status[256];
            ssize_t n_status = read(fd_status, info_status, sizeof(info_status));
            if (n_status == -1) {
                perror("Error reading file");
                close(fd_status);
                exit(EXIT_FAILURE);
            }
            
            char proc_state;
            char username[256];
            char *pos_state = strstr(info_status, "State:");
            if (pos_state != NULL) {
                sscanf(pos_state, "State: %c", &proc_state);
            } else {
                proc_state = '?';
            }

            char *pos_uid = strstr(info_status, "Uid:");
            if (pos_uid != NULL) {
                uid_t uid;
                sscanf(pos_uid, "Uid: %d", &uid);

                FILE *f_passwd = fopen("/etc/passwd", "r");
                if (f_passwd == NULL) {
                    perror("Error opening /etc/passwd");
                    exit(EXIT_FAILURE);
                }

                int passwd_uid;
                char line[256];
                while (fgets(line, sizeof(line), f_passwd) != NULL) {
                    char user_name[256];
                    sscanf(line, "%[^:]:x:%d:", user_name, &passwd_uid);
                    if (passwd_uid == uid) {
                        strncpy(username, user_name, sizeof(username));
                        break;
                    }
                }

                fclose(f_passwd);
            } else {
                strncpy(username, "Unknown", sizeof(username));
            }

            if (proc_state == 'R' && total_running < 20) {
                running[total_running].pid = pid;
                running[total_running].state = proc_state;
                strcpy(running[total_running].username, username);
                strcpy(running[total_running].command_line, info_cmdline);
                total_running++;
            } else if (total_others < 20) {
                others[total_others].pid = pid;
                others[total_others].state = proc_state;
                strcpy(others[total_others].username, username);
                strcpy(others[total_others].command_line, info_cmdline);
                total_others++;
            }

            close(fd_status);
            close(fd_cmdline);
        }
    }

    for(int i = 0; i < total_running; i++){
        printf("| %-7d | %-10s | %-15s | %-30s |\n", 
            running[i].pid, 
            getProcessStateName(running[i].state), 
            running[i].username, 
            running[i].command_line
        );
    }
    for(int i = 0; i < total_others-total_running; i++){
        printf("| %-7d | %-10s | %-15s | %-30s |\n", 
            others[i].pid, 
            getProcessStateName(others[i].state), 
            others[i].username, 
            others[i].command_line
        );
    }
    printf("|-------------------------------------------------------------------------|\n");
    printf("This information updates every %d seconds, press 'q' to quit!\n", INTERVAL_SECONDS);
}

char *getProcessStateName(char state) {
    switch (state) {
        case 'R': return (char*)"Running";
        case 'S': return (char*)"Sleeping";
        case 'I': return (char*)"Idle";
        default: return (char*)"Unknown";
    }
}
