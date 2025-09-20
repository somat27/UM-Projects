#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <locale.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include <conio.h>
#define STR_SIZE 50
#define MAXFRIENDS 50

struct User {
	int accountId,day,month,year,phoneNumber,friendsCount,accountType;
	char firstName[50];
	char lastName[50];
	char email[50];
	char username[50];
	char password[50];
	char description[50];
};

struct Post {
	int visibility,accountId,postId;
	char text[150];
	char dateStr[20];
	char firstName[50];
	char lastName[50];
};

struct Friendship {
	int accountId,friendId;
	char firstName[50];
	char lastName[50];
	char sourceFirstName[50];
	char sourceLastName[50];
};

void showInterface();
int mainMenu();
void loginAccount();
void friendsterMenu();
void deleteAccount();
void postsPage();
void deletePost();
void profilePage();
int isFriend();
int countFriends();
void addFriend();
void postMenu();
void friendsList();
void removeFriend();
void editPost();
int countPosts();
void searchAccount();
void showPosts();
void getAccountType();
void createPost();
void editAccount();
void registerAccount();
void inputFirstName();
void inputLastName();
void inputEmail();
void inputBirthDate();
void inputPhone();
void inputUsername();
void inputPassword();
int nextAccountId();
void showStatistics();
int exitProgram();

int main(){
	setlocale(LC_ALL, "C");
	system("CLS");
	showInterface();
	int option = mainMenu();
	if(option){
		if(option==1)
			loginAccount();
		else if(option==2)
			registerAccount();
		else if(option==3)
			postsPage(0,0);
		else if(option==4)
			showStatistics();
		else if(option==5)
			exitProgram();
	}else{
		return 0;
	}

	return 0;
}

void showInterface(){
	printf("\n");
	printf("\n ������� ������  �� ������� ���    �� ������  ������� �������� ������� ������ ");
	printf("\n ��      ��   �� �� ��      ����   �� ��   �� ��         ��    ��      ��   ��");
	printf("\n �����   ������  �� �����   �� ��  �� ��   �� �������    ��    �����   ������ ");
	printf("\n ��      ��   �� �� ��      ��  �� �� ��   ��      ��    ��    ��      ��   ��");
	printf("\n ��      ���  �� �� ������� ��   ���� ������  �������    ��    ������� ��   ��");
	printf("\n");
}

int mainMenu(){
	int option;
	printf("\n Welcome to Friendster, a console social network written in C. \n");
	printf("\n 1) log in  2) Create Account  3) Anonymous Mode*  4) Statistics  5) Exit");
	printf("\n *You can only view content marked as public.");
	printf("\n Option: ");
	scanf("%d",&option);
	switch(option){
		case 1:
		case 2:
		case 3:
		case 4:
		case 5:
			return option;
			break;
		default:
			printf("\n Invalid option");
			printf("\n Press any key to continue......");
			getch();
			system("CLS");
			main();
			break;
	}
}

void loginAccount(){
	system("CLS");
	FILE *usersFileR;
	usersFileR = fopen("users","rb");
	if (usersFileR == NULL){
		printf("1 ERROR: File not open");
		fclose(usersFileR);
		usersFileR = fopen("users","ab");
		fclose(usersFileR);
		printf("\nTry Again ....");
		getch();
		loginAccount();
	}
	FILE *lastlog;
	lastlog = fopen("lastlog","wb");
	struct User user;
	char username[200] = {};
	int i=0,accountIdVar;
	showInterface();
	printf("\n LOGIN System\n");
	printf(" Username: ");scanf("%s",username);
	printf(" Password: ");
	char ch,password[200] = {};
	int cPos = 0;
	while(1){
		ch = getch();
		if(ch==13){
			break;
		}else if(ch==8){
			if(cPos>0){
				cPos--;
				password[cPos] = '\0';
				printf("\b \b");
			}
		}else if(ch==32||ch==9){
			continue;
		}else{
			password[cPos] = ch;
			cPos++;
			printf("*");
		}
	}
	int fuser=0,fpass=0;
	while(fread(&user,sizeof(user),1,usersFileR)){
		if(strcmp(username,user.username) == 0){
			fuser = 1;
			if(strcmp(password, user.password) == 0){
				fpass = 1;
				accountIdVar = user.accountId;
				fwrite(&user,sizeof(user),1,lastlog);
				break;
			}
		}
	}
	fclose(usersFileR);
	fclose(lastlog);
	if(fuser == 0){
		printf("\n");
		printf("\n Invalid username!");
		printf("\n Try again...");
		getch();
		loginAccount();
	}else if(fpass == 0){
		printf("\n");
		printf("\n Password for username %s is invalid!",username);
		printf("\n Try again...");
		getch();
		loginAccount();
	}else{
		friendsterMenu(accountIdVar);
	}
}

void friendsterMenu(int authorId){
	int option;
	system("CLS");
	showInterface();
	printf("\n 1) Home 2) Profile 3) Delete Account 4) usersFileR Out 5) Exit");
	printf("\n Option: ");
	scanf("%d",&option);
	switch(option){
		case 1:
			postsPage(1,authorId);
			break;
		case 2:
			profilePage(authorId,0,0);
			break;
		case 3:
			deleteAccount(authorId);
			break;
		case 4:
			main();
			break;
		case 5:
			exitProgram();
			break;
		default:
			printf("\n Invalid option");
			printf("\n Press any key to continue......");
			getch();
			system("CLS");
			friendsterMenu(authorId);
			break;
	}
}

void deleteAccount(int authorId){
	char option[25];
	system("CLS");
	printf("\n =======WARNING=======");
    printf("\n This action is irreversible.\n\n");
	printf("\n Do you want to continue? (yes or no)\n ");
	scanf("%s",option);
	if(!strcmp(option,"nao")||!strcmp(option,"Nao")||!strcmp(option,"no")||!strcmp(option,"No")){
		friendsterMenu(authorId);
	}

    FILE *usersFileR;
    usersFileR = fopen("users","rb");
    if(usersFileR == NULL){
    	printf("1 ERROR: File not open");
    	fclose(usersFileR);
    	usersFileR = fopen("users","ab");
    	fclose(usersFileR);
		getch();
		deleteAccount(authorId);
	}
	FILE *tmpFile;
	tmpFile = fopen("tmpFile","wb");

	struct User user;
	int tmp, i=0, apagar = 0;
	char ch,password[200] = {};
	int cPos = 0;
	while(fread(&user,sizeof(user),1,usersFileR)){
		if(user.accountId==authorId){
			printf("\n To verify account ownership, please enter your password! \n Pass: ");
			while(1){
				ch = getch();
				if(ch==13){
					break;
				}else if(ch==8){
					if(cPos>0){
						cPos--;
						password[cPos] = '\0';
						printf("\b \b");
					}
				}else if(ch==32||ch==9){
					continue;
				}else{
					password[cPos] = ch;
					cPos++;
					printf("*");
				}
			}
			if(strcmp(user.password,password)==0){
				apagar = 1;
			}else{
				system("CLS");
				printf("\n Incorrect password, please try again later!");
				printf("\n Press any key to continue......");
				getch();
				remove("tmpFile");
				friendsterMenu(authorId);
			}
		}else{
			fwrite(&user,sizeof(user),1, tmpFile);
		}
	}
	fclose(usersFileR);
	fclose(tmpFile);
	printf("\n\n Account deleted successfully.\n");
	printf("\n Press any key to continue......");
	getch();
	if(apagar == 1){
		remove("users");
		rename("tmpFile","users");
	}
	main();
}

void postsPage(int userType, int authorId){
	int option;
	system("CLS");
	showInterface();
	printf("\n Posts Feed: \n");
	if(userType == 0){
		showPosts(1,0,0,0);
		printf("\n 1) Search Account 2) Back");
		printf("\n Option: ");
		scanf("%d", &option);
		switch(option){
			case 1:
				searchAccount(authorId,userType);
				break;
			case 2:
				main();
				break;
			default:
				printf("\n Invalid option");
				printf("\n Press any key to continue......");
				getch();
				system("CLS");
				postsPage(userType, authorId);
				break;
		}
	}if(userType == 1){
		FILE *usersFileR;
		usersFileR = fopen("users","rb");
		printf("%s",usersFileR);
		if (usersFileR == NULL){
			printf("3 ERROR: File not open");
			fclose(usersFileR);
			usersFileR = fopen("users","ab");
			fclose(usersFileR);
			printf("\nTry Again ....");
			getch();
			postsPage(userType, authorId);
		}
		struct User user;
		while(fread(&user,sizeof(user),1,usersFileR)){
			if(user.accountId == authorId){
				showPosts(1,1,0,0);
				printf("\n 1) Search Account 2) Create Post 3) Back");
				printf("\n Option: ");
				scanf("%d", &option);
				fclose(usersFileR);
				switch(option){
					case 1:
						searchAccount(authorId,userType);
						break;
					case 2:
						createPost(user.firstName, user.lastName, authorId);
						break;
					case 3:
						friendsterMenu(authorId);
						break;
					default:
						printf("\n Invalid option");
						printf("\n Press any key to continue......");
						getch();
						system("CLS");
						postsPage(userType, authorId);
						break;
				}
				break;
			}
		}

	}
}

void searchAccount(int authorId, int backType){
	system("CLS");
	showInterface();
	char name[50];
	printf("\n Account first name to search: ");
	scanf("%s",name);

	FILE *usersFileR;
	usersFileR = fopen("users","rb");
	printf("%s",usersFileR);
	if (usersFileR == NULL){
		printf("3 ERROR: File not open");
		fclose(usersFileR);
		usersFileR = fopen("users","ab");
		fclose(usersFileR);
		printf("\nTry Again ....");
		getch();
		searchAccount(authorId,backType);
	}

	struct User user;
	int i=1,option,proceed=0;
	char option2[5];
	while(fread(&user,sizeof(user),1,usersFileR)){
		if(strcmp(name,user.firstName)==0){
			printf("\n %s %s [@%s] — is this the account you are looking for? (yes or no)",user.firstName,user.lastName,user.username);
			printf("\n Option: ");
			scanf("%s",option2);
			if(!strcmp(option2,"sim")||!strcmp(option2,"Sim")||!strcmp(option2,"yes")||!strcmp(option2,"Yes")){
				proceed = 1;
				fclose(usersFileR);
				profilePage(authorId, 1, user.accountId);
				break;
			}
		}
	}
	if(proceed == 0){
		printf("\n 1) Search Again 2) Back");
		printf("\n Option: ");
		scanf("%d",&option);
		switch(option){
			case 1:
				searchAccount(authorId,backType);
				break;
			case 2:
				postsPage(backType, authorId);
				break;
			default:
				printf("\n Invalid option");
				printf("\n Press any key to continue......");
				getch();
				searchAccount(authorId,backType);
				break;
		}
	}
}

void showPosts(int op1,int option2,int op3,int authorId){
	FILE *postsFile;
	postsFile = fopen("posts","rb");
	if (postsFile == NULL){
		printf("2 ERROR: File not open");
		fclose(postsFile);
		postsFile = fopen("posts","ab");
		fclose(postsFile);
		printf("\nTry Again ....");
		getch();
		showPosts(op1,option2,op3,authorId);
	}

	struct Post post;
	while(fread(&post,sizeof(post),1,postsFile)){
		if(authorId != 0){
			if(post.accountId == authorId){
				if(post.visibility == 1 && op1){
					printf("\n %s %s -- %s [Public]\n ID %d -> %s\n",post.firstName,post.lastName,post.dateStr,post.postId,post.text);
				}
				if(post.visibility == 2 && option2){
					printf("\n %s %s -- %s [Restricted]\n ID %d -> %s\n",post.firstName,post.lastName,post.dateStr,post.postId,post.text);
				}
				if(post.visibility == 3 && op3){
					printf("\n %s %s -- %s [Private]\n ID %d -> %s\n",post.firstName,post.lastName,post.dateStr,post.postId,post.text);
				}
			}
		}else{
			if(post.visibility == 1 && op1){
				printf("\n %s %s -- %s [Public]\n ID %d -> %s\n",post.firstName,post.lastName,post.dateStr,post.postId,post.text);
			}
			if(post.visibility == 2 && option2){
				printf("\n %s %s -- %s [Restricted]\n ID %d -> %s\n",post.firstName,post.lastName,post.dateStr,post.postId,post.text);
			}
			if(post.visibility == 3 && op3){
				printf("\n %s %s -- %s [Private]\n ID %d -> %s\n",post.firstName,post.lastName,post.dateStr,post.postId,post.text);
			}
		}
	}
	fclose(postsFile);
}

void profilePage(int authorId, int viewOwner, int targetAccountId){
	system("CLS");
	if(viewOwner == 0){
		FILE *usersFileR;
		usersFileR = fopen("users","rb");
		printf("%s",usersFileR);
		if (usersFileR == NULL){
			printf("3 ERROR: File not open");
			fclose(usersFileR);
			usersFileR = fopen("users","ab");
			fclose(usersFileR);
			printf("\nTry Again ....");
			getch();
			profilePage(authorId,viewOwner, 0);
		}
		int option;
		struct User user;
		while(fread(&user,sizeof(user),1,usersFileR)){
			if(authorId == user.accountId){
				int postsFile = countPosts(user.accountId,0);
				int friendsCount = countFriends(user.accountId);
				char accountType[50];
				getAccountType(user.accountId, accountType);
				printf("\n %s %s [@%s]\\t Account %d: %s\n",user.firstName, user.lastName,user.username,user.accountId,accountType);
				printf("\n Posts: %d \t Friends: %d\n",postsFile,friendsCount);
				printf("\n Description: %s", user.description);
				printf("\n\n\n Posts: \n");
				showPosts(1,1,1,authorId);
				printf("\n 1) Post Menu 2) Edit Account 3) Friends List 4) Back");
				printf("\n Option: ");
				scanf("%d", &option);
				fclose(usersFileR);
				switch(option){
					case 1:
						postMenu(user.firstName, user.lastName, authorId);
						break;
					case 2:
						editAccount(authorId);
						break;
					case 3:
						friendsList(authorId);
						break;
					case 4:
						friendsterMenu(authorId);
						break;
					default:
						printf("\n Invalid option");
						printf("\n Press any key to continue......");
						getch();
						system("CLS");
						profilePage(authorId,viewOwner,0);
						break;
				}
			}
		}
	}else if(viewOwner == 1){
		FILE *usersFileR;
		usersFileR = fopen("users","rb");
		printf("%s",usersFileR);
		if (usersFileR == NULL){
			printf("3 ERROR: File not open");
			fclose(usersFileR);
			usersFileR = fopen("users","ab");
			fclose(usersFileR);
			printf("\nTry Again ....");
			getch();
			profilePage(authorId,viewOwner,0);
		}
		int option;
		struct User user;
		while(fread(&user,sizeof(user),1,usersFileR)){
			if(targetAccountId == user.accountId){
				int postsFile = countPosts(user.accountId,0);
				int friendsCount = countFriends(user.accountId);
				int areFriends = isFriend(authorId,user.accountId);
				char accountType[50];
				getAccountType(user.accountId, accountType);
				if(areFriends == 1){
					printf("\n %s %s [@%s]\\t Account %d: %s\n",user.firstName, user.lastName,user.username,user.accountId,accountType);
					printf("\n Posts: %d \t Friends: %d\n",postsFile,friendsCount);
					printf("\n Description: %s", user.description);
					printf("\n\n YOU ARE FRIENDS!\n\n Posts: \n");
				}else{
					printf("\n %s %s [@%s]\\t Account %d: %s\n",user.firstName, user.lastName,user.username,user.accountId,accountType);
					printf("\n Posts: %d \t Friends: %d\n",postsFile,friendsCount);
					printf("\n Description: %s", user.description);
					printf("\n\n\n Posts: \n");
				}
				if(authorId == 0){
					showPosts(1,0,0,user.accountId);
					printf("\n 1) Back");
					printf("\n Option: ");
					scanf("%d", &option);
					fclose(usersFileR);
					switch(option){
						case 1:
							postsPage(0,0);
							break;
						default:
							printf("\n Invalid option");
							printf("\n Press any key to continue......");
							getch();
							system("CLS");
							profilePage(authorId,viewOwner,targetAccountId);
							break;
					}
				}else{
					if(areFriends == 1){
						showPosts(1,1,1,user.accountId);
					}else{
						showPosts(1,1,0,user.accountId);
					}
					if(strcmp(accountType,"Private")==0||areFriends==1||authorId==user.accountId){
						printf("\n 1) Back");
						printf("\n Option: ");
						scanf("%d", &option);
						fclose(usersFileR);
						switch(option){
							case 1:
								friendsterMenu(authorId);
								break;
							default:
								printf("\n Invalid option");
								printf("\n Press any key to continue......");
								getch();
								system("CLS");
								profilePage(authorId,viewOwner,targetAccountId);
								break;
						}
					}else{
						printf("\n 1) Add Friend 2) Back");
						printf("\n Option: ");
						scanf("%d", &option);
						fclose(usersFileR);
						switch(option){
							case 1:
								addFriend(authorId,targetAccountId);
								break;
							case 2:
								friendsterMenu(authorId);
								break;
							default:
								printf("\n Invalid option");
								printf("\n Press any key to continue......");
								getch();
								system("CLS");
								profilePage(authorId,viewOwner,targetAccountId);
								break;
						}
					}
				}
			}
		}
	}
}

int isFriend(int authorId, int accountId){
	FILE *friendsFile;
	friendsFile = fopen("friendships","rb");
	if(friendsFile == NULL){
		fclose(friendsFile);
		friendsFile = fopen("friendships","ab");
		fclose(friendsFile);
		friendsList(authorId);
	}
	struct Friendship friendship;
	while(fread(&friendsCount,sizeof(friendship),1,friendsFile)){
		if(friendsCount.accountId==authorId && friendsCount.friendId==accountId||friendsCount.accountId==accountId && friendsCount.friendId==authorId){
			return 1;
		}
	}
	fclose(friendsFile);
	return 0;
}

int countFriends(int authorId){
	int totalFriends=0;
	FILE *friendsFile;
	friendsFile = fopen("friendships","rb");
	if(friendsFile == NULL){
		fclose(friendsFile);
		friendsFile = fopen("friendships","ab");
		fclose(friendsFile);
		friendsList(authorId);
	}
	struct Friendship friendship;
	while(fread(&friendsCount,sizeof(friendship),1,friendsFile)){
		if(friendsCount.accountId==authorId||friendsCount.friendId==authorId){
			totalFriends++;
		}
	}
	fclose(friendsFile);
	return totalFriends;
}

void addFriend(int authorId, int targetAccountId){
	system("CLS");
	showInterface();
	int totalFriends = countFriends(authorId);
	if(totalFriends<=50){
		struct Friendship friendship;
		FILE *friendsFile;
		friendsFile = fopen("friendships","ab");
		FILE *usersFileR;
		usersFileR = fopen("users","rb");
		struct User user;
		while(fread(&user,sizeof(user),1,usersFileR)){
			if(user.accountId == targetAccountId){
				strcpy(friendsCount.firstName,user.firstName);
				strcpy(friendsCount.lastName,user.lastName);
			}
			if(user.accountId == authorId){
				strcpy(friendsCount.sourceFirstName,user.firstName);
				strcpy(friendsCount.sourceLastName,user.lastName);
			}
		}
		friendsCount.accountId = authorId;
		friendsCount.friendId = targetAccountId;
		fwrite(&friendsCount,sizeof(friendship),1,friendsFile);
		fclose(friendsFile);
		fclose(usersFileR);
		printf("\n %s %s, you are now friends with %s %s!",friendsCount.sourceFirstName,friendsCount.sourceLastName,friendsCount.firstName,friendsCount.lastName);
		getch();
		profilePage(authorId,1,targetAccountId);
	}else{
		printf("\n You cannot add more friends!");
		printf("\n Press any key to go back .....");
		getch();
		profilePage(authorId,1,targetAccountId);
	}
}

void postMenu(char* firstName, char* lastName, int authorId){
	int option;
	system("CLS");
	showPosts(1,1,1,authorId);
	printf("\n 1) Create Post 2) Edit Post 3) Delete Post");
	printf("\n Option: ");
	scanf("%d",&option);
	switch(option){
		case 1:
			createPost(firstName, lastName, authorId);
			break;
		case 2:
			editPost(authorId);
			break;
		case 3:
			deletePost(authorId);
			break;
		default:
			printf("\n Invalid option");
			printf("\n Press any key to continue......");
			getch();
			system("CLS");
			postMenu(firstName,lastName,authorId);
			break;
	}
}

void friendsList(int authorId){
	system("CLS");
	showInterface();
	int totalFriends = countFriends(authorId);
	if(totalFriends>0){
		printf("\n Friends List: \n");
		FILE *friendsFile;
		friendsFile = fopen("friendships","rb");
		if(friendsFile == NULL){
			fclose(friendsFile);
			friendsFile = fopen("friendships","ab");
			fclose(friendsFile);
			friendsList(authorId);
		}
		struct Friendship friendship;
		while(fread(&friendsCount,sizeof(friendship),1,friendsFile)){
			if(friendsCount.accountId == authorId){
				printf("\n 1: %d -> %s %s",friendsCount.friendId,friendsCount.firstName,friendsCount.lastName);
			}else if(friendsCount.friendId == authorId){
				printf("\n 2: %d -> %s %s",friendsCount.accountId,friendsCount.sourceFirstName,friendsCount.sourceLastName);
			}
		}
		int option;
		printf("\n\n 1) Remove Friendship 2) Back");
		printf("\n Option: ");
		scanf("%d",&option);
		switch(option){
			case 1:
				fclose(friendsFile);
				removeFriend(authorId);
				break;
			case 2:
				fclose(friendsFile);
				friendsterMenu(authorId);
				break;
			default:
				fclose(friendsFile);
				printf("\n Invalid option, tente novamente mais tarde!");
				printf("\n Press any key to continue......");
				getch();
				friendsList(authorId);
				break;
		}
	}else{
		printf("\n You don't have any friends yet! \n");
		int option;
		printf("\n\n 1) Back");
		printf("\n Option: ");
		scanf("%d",&option);
		switch(option){
			case 1:
				friendsterMenu(authorId);
				break;
			default:
				printf("\n Invalid option, tente novamente mais tarde!");
				printf("\n Press any key to continue......");
				getch();
				friendsList(authorId);
				break;
		}
	}
}

void removeFriend(int authorId){
	system("CLS");
	showInterface();
	FILE *friendsFile;
	friendsFile = fopen("friendships","rb");
	FILE *tmp;
	tmp = fopen("tmp","wb");
	struct Friendship friendship;
	printf("\n Which ID do you want to remove as a friend? ");
	printf("\n ID: ");
	int id,removido=0;
	scanf("%d",&id);

	while(fread(&friendsCount,sizeof(friendship),1,friendsFile)){
		if(friendsCount.friendId == id && friendsCount.accountId == authorId){
			removido = 1;
		}else{
			fwrite(&friendsCount,sizeof(friendship),1,tmp);
		}
	}

	fclose(tmp);
	fclose(friendsFile);
	printf("\n\n Friend removed successfully.\n");
	printf("\n Press any key to continue......");
	getch();
	if(removido == 1){
		remove("friendships");
		rename("tmp","friendships");
	}
	friendsList(authorId);
}

void editPost(int authorId){
	system("CLS");
	FILE *postsFile;
    postsFile = fopen("posts","rb");
    if(postsFile == NULL){
    	printf("1 ERROR: File not open");
    	fclose(postsFile);
    	postsFile = fopen("posts","ab");
    	fclose(postsFile);
		getch();
		deletePost(authorId);
	}
	FILE *tmpFile;
	tmpFile = fopen("tmpFile","wb");

	struct Post post;
	int tmp, i=0, editar = 0,postId,option;
	char password[50]={},textInput[150];

	printf("\n Which post ID do you want to edit? \n ID: ");
	scanf("%d",&postId);
	while(fread(&post,sizeof(post),1,postsFile)){
		if((post.accountId==authorId)&&(post.postId==postId)){
			printf("\n textInput: ");
			fflush(stdin);
			gets(textInput);
			if(strlen(textInput)>sizeof(textInput)){
				printf("\n A post can have up to 150 characters, please try again\n");
				printf("\n Press any key to continue......");
				getch();
				editPost(authorId);
			}
			strcpy(post.text, textInput);
			printf("\n Post visibility? (1-Public, 2-Restricted, 3-Private)");
			printf("\n Option: ");
			scanf("%d",&option);
			switch(option){
				case 1:
					post.visibility = 1;
					break;
				case 2:
					post.visibility = 2;
					break;
				case 3:
					post.visibility = 3;
					break;
				default:
					printf("\n Invalid type, please try again later!");
					printf("\n Press any key to continue......");
					getch();
					editPost(authorId);
					break;
			}
			fwrite(&post,sizeof(post),1, tmpFile);
			editar = 1;
		}else{
			fwrite(&post,sizeof(post),1, tmpFile);
		}
	}
	if(editar == 0){
		system("CLS");
		printf("\n Post ID not found, please try again later!");
		printf("\n Press any key to continue......");
		getch();
		remove("tmpFile");
		profilePage(authorId,0,0);
	}
	fclose(postsFile);
	fclose(tmpFile);
	printf("\n\n Post edited successfully.\n");
	printf("\n Press any key to continue......");
	getch();
	if(editar == 1){
		remove("posts");
		rename("tmpFile","posts");
	}
	profilePage(authorId,0,0);
}

void deletePost(int authorId){
	char option[25];
	system("CLS");
	printf("\n =======WARNING=======");
    printf("\n This action is irreversible.\n\n");
	printf("\n Do you want to continue? (yes or no)\n ");
	scanf("%s",option);
	if(!strcmp(option,"nao")||!strcmp(option,"Nao")||!strcmp(option,"no")||!strcmp(option,"No")){
		profilePage(authorId,0,0);
	}

    FILE *postsFile;
    postsFile = fopen("posts","rb");
    if(postsFile == NULL){
    	printf("1 ERROR: File not open");
    	fclose(postsFile);
    	postsFile = fopen("posts","ab");
    	fclose(postsFile);
		getch();
		deletePost(authorId);
	}
	FILE *tmpFile;
	tmpFile = fopen("tmpFile","wb");

	struct Post post;
	int tmp, i=0, apagar = 0,postId;
	char password[50]={};
	printf("\n Which post ID do you want to delete? \n ID: ");
	scanf("%d",&postId);
	while(fread(&post,sizeof(post),1,postsFile)){
		if((post.accountId==authorId)&&(post.postId==postId)){
			apagar = 1;
		}else{
			fwrite(&post,sizeof(post),1, tmpFile);
		}
	}
	if(apagar == 0){
		system("CLS");
		printf("\n Post ID not found, please try again later!");
		printf("\n Press any key to continue......");
		getch();
		remove("tmpFile");
		profilePage(authorId,0,0);
	}
	fclose(postsFile);
	fclose(tmpFile);
	printf("\n\n Post deleted successfully.\n");
	printf("\n Press any key to continue......");
	getch();
	if(apagar == 1){
		remove("posts");
		rename("tmpFile","posts");
	}
	profilePage(authorId,0,0);
}

int countPosts(int authorId, int counterType){
	if (counterType == 0){

		int postCount = 0;
		FILE *postFile;
		postFile = fopen("posts","rb");
		struct Post post;
		if (postFile == NULL){
			printf("4 ERROR: File not open");
			fclose(postFile);
			postFile = fopen("posts","ab");
			fclose(postFile);
			printf("\nTry Again ....");
			getch();
			countPosts(authorId,counterType);
		}
		while(fread(&post,sizeof(post),1,postFile)){
			if(post.accountId == authorId){
				postCount = postCount + 1;
			}
		}
		fclose(postFile);
		return postCount;
	}else if(counterType == 1){

		int postCount = 0;
		FILE *postFile;
		postFile = fopen("posts","rb");
		struct Post post;
		if (postFile == NULL){
			printf("4 ERROR: File not open");
			fclose(postFile);
			postFile = fopen("posts","ab");
			fclose(postFile);
			printf("\nTry Again ....");
			getch();
			countPosts(authorId, counterType);
		}
		while(fread(&post,sizeof(post),1,postFile)){
			postCount = postCount + 1;
		}
		fclose(postFile);
		return postCount;
	}
}

void getAccountType(int authorId, char* accountType){
	char accountTypeStr[STR_SIZE];
	FILE *usersFileR;
	usersFileR = fopen("users","rb");
	struct User user;
	if (usersFileR == NULL){
		printf("5 ERROR: File not open");
		fclose(usersFileR);
		usersFileR = fopen("users","ab");
		fclose(usersFileR);
		printf("\nTry Again ....");
		getch();
		getAccountType(authorId, accountType);
	}
	while(fread(&user,sizeof(user),1,usersFileR)){
		if(user.accountId == authorId){
			if(user.accountType == 1){
				strcpy(accountTypeStr, "Private");
			}else if(user.accountType == 0){
				strcpy(accountTypeStr, "Public");
			}
		}
	}
	fclose(usersFileR);
	strcpy(accountType, accountTypeStr);
}

void createPost(char* firstName,char* lastName, int authorId){
	system("CLS");
	FILE *postsFile;
	postsFile = fopen("posts","ab");
	struct Post post;
	time_t rawtime;
	struct tm * timeinfo;
	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	char rawDate[50];
	strcpy(rawDate,asctime(timeinfo));
	char text[150];
	printf("\n Create Post");
	printf("\n What would you like to write? ");
	fflush(stdin);
	gets(text);
	if(strlen(text)>sizeof(text)){
		printf("A post can have up to 150 characters, please try again\n");
		printf("\nPress any key to continue......");
		getch();
		createPost(firstName,lastName,authorId);
	}

	int numPosts = countPosts(authorId,1);

	printf("\n Which type of post do you want?\n 1) Public 2) Restricted 3) Private");
	printf("\n Option: ");
	int option;
	fflush(stdin);scanf("%d",&option);
	switch(option){
		case 1:
			post.visibility = 1;
			break;
		case 2:
			post.visibility = 2;
			break;
		case 3:
			post.visibility = 3;
			break;
		default:
			printf("\n Invalid type, please try again later!");
			printf("\n Press any key to continue......");
			getch();
			createPost(firstName,lastName,authorId);
			break;
	}

	strcpy(post.text, text);
	strcpy(post.dateStr, rawDate);
	post.accountId = authorId;
	strcpy(post.firstName, firstName);
	strcpy(post.lastName, lastName);
	post.postId = numPosts;
	fwrite(&post,sizeof(post),1,postsFile);
	fclose(postsFile);
	profilePage(authorId, 0,0);

}

void editAccount(int authorId){
	system("CLS");
	showInterface();

	FILE *usersFile;
	usersFile = fopen("users","rb");

	FILE *tmpFile;
	tmpFile = fopen("tmpFile","wb");

	struct User user;
	char resposta[50];
	int editar = 0;
	int i=1;
	while(fread(&user,sizeof(user),1,usersFile)){
		if(authorId == user.accountId){
			printf("\n Do you want to edit the name [ %s %s ]? (yes or no)",user.firstName,user.lastName);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				printf("\n First Name: ");
				scanf("%s",user.firstName);
				printf(" Last Name: ");
				scanf("%s",user.lastName);
				if(strlen(user.firstName)>sizeof(user.firstName)||strlen(user.lastName)>sizeof(user.lastName)){
					printf("Name too long, please try again later!");
					printf("\nPress any key to continue......");
					getch();
					profilePage(authorId,0,0);
				}
			}
			system("CLS");
			showInterface();
			printf("\n Do you want to edit the email [ %s ]? (yes or no)",user.email);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				printf("\n Email: ");
				scanf("%s",user.email);
				if(strlen(user.email)>sizeof(user.email)){
					printf("Email too long, please try again later!");
					printf("\nPress any key to continue......");
					getch();
					profilePage(authorId,0,0);
				}
			}
			system("CLS");
			showInterface();
			printf("\n Do you want to edit the birth date [ %d/%d/%d ]? (yes or no)",user.day,user.month,user.year);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				int rday,rmonth,ryear,errorFlag=0;
				printf("\n Birth date (DD/MM/YYYY): ");
				scanf("%d/%d/%d",&rday,&rmonth,&ryear);
				if(rday>=1&&rday<=31){
					if(rmonth>=1&&rmonth<=12){
						if(ryear>=1900&&ryear<=2022){
							switch(rmonth){
								case 1:
								case 3:
								case 5:
								case 7:
								case 8:
								case 10:
								case 12:
									user.day = rday;
									user.month = rmonth;
									user.year = ryear;
									break;
								case 2:
									if(ryear%4==0){
										if(rday<30){
											user.day = rday;
											user.month = rmonth;
											user.year = ryear;
										}else{
											errorFlag = 1;
										}
									}else{
										if(rday<29){
											user.day = rday;
											user.month = rmonth;
											user.year = ryear;
										}else{
											errorFlag = 1;
										}
									}
									break;
								case 4:
								case 6:
								case 9:
								case 11:
									if(rday<31){
										user.day = rday;
										user.month = rmonth;
										user.year = ryear;
									}else{
										errorFlag = 1;
									}
									break;
								default:
									errorFlag = 1;
									break;
							}

						}else{

							errorFlag = 1;
						}
					}else{

						errorFlag = 1;
					}
				}else{

					errorFlag = 1;
				}
				if(errorFlag == 1){
					printf("Invalid birth date, please try again later!");
					printf("\nPress any key to continue......");
					getch();
					profilePage(authorId,0,0);
				}

			}
			system("CLS");
			showInterface();
			printf("\n Do you want to edit the phone number [ %d ]? (yes or no)",user.phoneNumber);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				printf("\n Phone Number: ");
				scanf("%s",user.phoneNumber);
				if(user.phoneNumber>999999999||user.phoneNumber<900000000){
					printf("Invalid phone number, please try again later!");
					printf("\nPress any key to continue......");
					getch();
					profilePage(authorId,0,0);
				}
			}
			system("CLS");
			showInterface();
			printf("\n Do you want to edit the password? (yes or no)",user.password);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				int i = 0;
				char password[50],ch;
				int cPos=0;

				printf(" Password (Minimum 6 characters):");
				while(1){
					ch = getch();
					if(ch==13){
						break;
					}else if(ch==8){
						if(cPos>0){
							cPos--;
							password[cPos] = '\0';
							printf("\b \b");
						}
					}else if(ch==32||ch==9){
						continue;
					}else{
						password[cPos] = ch;
						cPos++;
						printf("*");
					}
				}
				if(strlen(password)>sizeof(password)){
					printf("\n Password too long, please try again later!");
					printf("\n Press any key to continue......");
					getch();
					profilePage(authorId,0,0);
				}
				strcpy(user.password, password);
			}
			system("CLS");
			showInterface();
			printf("\n Do you want to edit your account description? (yes or no)",user.description);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				char description[50];
				printf("\n Description: ");
				fflush(stdin);
				gets(description);
				if(strlen(description)>sizeof(description)){
					printf("A description can have up to 50 characters, please try again later!");
					printf("\nPress any key to continue......");
					getch();
					profilePage(authorId,0,0);
				}
				strcpy(user.description,description);
			}
			system("CLS");
			showInterface();
			printf("\n Do you want to change your account visibility? (yes or no)",user.description);
			printf("\n Option: ");
			scanf("%s",resposta);
			if(!strcmp(resposta,"sim")||!strcmp(resposta,"Sim")||!strcmp(resposta,"yes")||!strcmp(resposta,"Yes")){
				int option;
				printf("\n Account Visibility [1) Public 2) Private]: ");
				scanf("%d",&option);
				switch(option){
					case 1:
						user.accountType = 0;
						break;
					case 2:
						user.accountType = 1;
						break;
					default:
						printf("Invalid account type, please try again later!");
						printf("\nPress any key to continue......");
						getch();
						profilePage(authorId,0,0);
						break;
				}
			}
			editar = 1;
			fwrite(&user,sizeof(user),1,tmpFile);
		}else{
			fwrite(&user,sizeof(user),1,tmpFile);
		}
	}
	fclose(usersFile);
	fclose(tmpFile);
	printf("\n\n Account updated successfully.\n");
	printf("\n Press any key to continue......");
	if(editar == 1){
		remove("users");
		getch();
		rename("tmpFile","users");
	}
	profilePage(authorId,0,0);
}

void registerAccount(){
	system("CLS");

	int targetAccountId = nextAccountId();

	FILE *usersFileW;
	usersFileW = fopen("users","ab");

	struct User user;

	char firstname[50],lastname[50],email[50],username[50],password[50];
	int day,month,year;
	int phone;

	if(targetAccountId<=200){

		inputFirstName(firstname);
		strcpy(user.firstName, firstname);

		inputLastName(lastname);
		strcpy(user.lastName, lastname);

		inputEmail(email);
		strcpy(user.email, email);

		inputPhone(&phone);
		user.phoneNumber = phone;

		inputBirthDate(&day,&month,&year);
		user.day = day;
		user.month = month;
		user.year = year;

		inputUsername(username);
		strcpy(user.username, username);

		inputPassword(password);
		strcpy(user.password, password);

		user.accountId = targetAccountId;
		user.friendsCount = 0;
		user.accountType = 0;
		strcpy(user.description, "Ainda sem Descri��o!");
		/* DEBUG:
		printf("\n Account Number: %d", user.accountId);
	    printf("\n name: %s %s", user.firstName, user.lastName);
	    printf("\n Email: %s", user.email);
	    printf("\n phone: %ld", user.phoneNumber);
	    printf("\n Username: %s", user.username);
	    printf("\n Password: %s", user.password);
	    printf("\n Description: %s", user.description);
	    printf("\n Friends: %d", user.friendsCount);
	    printf("\n Account Type: %d", user.accountType);
	    printf("\n Birth Date: %d/%d/%d", user.day,user.month,user.year);
		*/

		fwrite(&user,sizeof(user),1,usersFileW);
		fclose(usersFileW);

		printf("\n Registered successfully!\nNow please log in with your new account.");
		printf("\n Press any key to continue......");
		getch();
		system("CLS");
		loginAccount();
	}else{
		printf("\n Unfortunately there are already 200 accounts registered in the application.\n It is not possible to create more accounts.");
		printf("\n Press any key to continue......");
		getch();
		main();
	}
}

int nextAccountId(){
	FILE *usersFileW;
	usersFileW = fopen("users","rb");
	if (usersFileW == NULL){
		printf("7 ERROR: File not open");
		fclose(usersFileW);
		usersFileW = fopen("users","ab");
		fclose(usersFileW);
		getch();
		registerAccount();
	}
	struct User user;
	int lastId;
	while(fread(&user,sizeof(user),1,usersFileW)){
		lastId = user.accountId;
	}
	if (lastId>200||lastId<0)
		lastId = 0;
	fclose(usersFileW);
	return lastId+1;
}

void inputFirstName(char* firstname){
	char firstTmp[STR_SIZE];
	system("CLS");
	showInterface();
	printf("\n First Name: ");
	scanf("%s",firstTmp);
	if(strlen(firstTmp)>sizeof(firstTmp)){
		printf("Name too long, please try again\n");
		printf("\nPress any key to continue......");
		getch();
		inputFirstName(firstname);
	}else
		strcpy(firstname, firstTmp);
}

void inputLastName(char* lastname){
	char lastTmp[STR_SIZE];
	system("CLS");
	showInterface();
	printf("\n Last Name: ");
	scanf("%s",lastTmp);
	if(strlen(lastTmp)>sizeof(lastTmp)){
		printf("Name too long, please try again\n");
		printf("\nPress any key to continue......");
		getch();
		inputLastName(lastname);
	}else
		strcpy(lastname, lastTmp);
}

void inputEmail(char* email){
	char mail[STR_SIZE];
	int i, j=0;
	system("CLS");
	showInterface();
	printf("\n Email: ");
	scanf("%s",mail);

	for(i=0;i<=strlen(mail);i++){
		if(mail[i]=='@')
			j = 1;
	}
	if(strlen(mail)>sizeof(mail)){
		printf("Email too long, please try again\n");
		printf("\nPress any key to continue......");
		getch();
		inputEmail(email);
	}else if(strlen(mail)<10){
		printf("Email too short, please try again\n");
		printf("\nPress any key to continue......");
		getch();
		inputEmail(email);
	}else if(j==0){
		printf("Invalid email\n");
		printf("\nPress any key to continue......");
		getch();
		inputEmail(email);
	}else
		strcpy(email, mail);
}

void inputBirthDate(int* day, int* month,int* year){
	system("CLS");
	showInterface();
	int rday,rmonth,ryear,errorFlag=0;
	printf("\n Birth date (DD/MM/YYYY): ");
	scanf("%d/%d/%d",&rday,&rmonth,&ryear);
	if(rday>=1&&rday<=31){
		if(rmonth>=1&&rmonth<=12){
			if(ryear>=1900&&ryear<=2022){
				switch(rmonth){
					case 1:
					case 3:
					case 5:
					case 7:
					case 8:
					case 10:
					case 12:
						*day = rday;
						*month = rmonth;
						*year = ryear;
						break;
					case 2:
						if(ryear%4==0){
							if(rday<30){
								*day = rday;
								*month = rmonth;
								*year = ryear;
							}else{
								errorFlag = 1;
							}
						}else{
							if(rday<29){
								*day = rday;
								*month = rmonth;
								*year = ryear;
							}else{
								errorFlag = 1;
							}
						}
						break;
					case 4:
					case 6:
					case 9:
					case 11:
						if(rday<31){
							*day = rday;
							*month = rmonth;
							*year = ryear;
						}else{
							errorFlag = 1;
						}
						break;
					default:
						errorFlag = 1;
						break;
				}

			}else{

				errorFlag = 1;
			}
		}else{

			errorFlag = 1;
		}
	}else{

		errorFlag = 1;
	}
	if(errorFlag == 1){
		printf("Invalid birth date!");
		printf("\nPress any key to continue......");
		getch();
		inputBirthDate(day,month,year);
	}
}

void inputPhone(int* phone){
	int phoneVal;
	system("CLS");
	showInterface();
	printf("\n Phone Number: ");
	scanf("%ld",&phoneVal);
	if(phoneVal<900000000||phoneVal>999999999){
		printf("Invalid phone number!");
		printf("\nPress any key to continue......");
		getch();
		inputPhone(phone);
	}else
		*phone = phoneVal;
}

void inputUsername(char* username){
	char name[50];
	system("CLS");
	showInterface();
	printf("\n Username: ");
	scanf("%s",name);
	if(strlen(name)>sizeof(name)){
		printf("Username too long, please try again\n");
		printf("\nPress any key to continue......");
		getch();
		inputUsername(username);
	}else
		strcpy(username, name);
}

void inputPassword(char* password){
	char pass[50] = {},pass2[50] = {},ch;
	int cPos=0;
	system("CLS");
	showInterface();
	printf("\n Password (Minimum 6 characters):");
	while(1){
		ch = getch();
		if(ch==13){
			break;
		}else if(ch==8){
			if(cPos>0){
				cPos--;
				pass[cPos] = '\0';
				printf("\b \b");
			}
		}else if(ch==32||ch==9){
			continue;
		}else{
			pass[cPos] = ch;
			cPos++;
			printf("*");
		}
	}
	cPos = 0;
	printf("\n Confirm Password:");
	while(1){
		ch = getch();
		if(ch==13){
			break;
		}else if(ch==8){
			if(cPos>0){
				cPos--;
				pass2[cPos] = '\0';
				printf("\b \b");
			}
		}else if(ch==32||ch==9){
			continue;
		}else{
			pass2[cPos] = ch;
			cPos++;
			printf("*");
		}
	}
	int cmpResult = strcmp(pass,pass2);
	if(strlen(pass)>sizeof(pass)){
		printf("\n Password too long, please try again\n");
		printf("\n Press any key to continue......");
		getch();
		inputPassword(password);
	}else if(strlen(pass)<6){
		printf("\n Password too short, please try again\n");
		printf("\n Press any key to continue......");
		getch();
		inputPassword(password);
	}else if(cmpResult!=0){
		printf("\n Passwords do not match!\n");
		printf("\n Press any key to continue......");
		getch();
		inputPassword(password);
	}else
		strcpy(password, pass);
}

void showStatistics(){
	system("CLS");
	showInterface();

	FILE *lastlog;
	lastlog = fopen("lastlog","rb");
	if (lastlog == NULL){
		printf("1 ERROR: File not open");
		fclose(lastlog);
		lastlog = fopen("lastlog","ab");
		fclose(lastlog);
		printf("\nTry Again ....");
		getch();
		showStatistics();
	}
	struct User user;
	while(fread(&user,sizeof(user),1,lastlog)){
		printf("\n Last logged-in account: %s %s - ID: %d",user.firstName,user.lastName,user.accountId);
	}
	fclose(lastlog);
	FILE *postsFile;
	postsFile = fopen("posts","rb");
	if (postsFile == NULL){
		printf("1 ERROR: File not open");
		fclose(postsFile);
		postsFile = fopen("posts","ab");
		fclose(postsFile);
		printf("\nTry Again ....");
		getch();
		showStatistics();
	}
	struct Post post;
	int totalUsers = nextAccountId();
	int i,totalPostsCount=0,maxPostsByUser=0;
	char lastN[50],firstN[50],maxFirst[50],maxLast[50];
	while(fread(&post,sizeof(post),1,postsFile)){
		for(i=1;i<totalUsers;i++){
			if(i==post.accountId){
				totalPostsCount ++;
				strcpy(firstN,post.firstName);
				strcpy(lastN,post.lastName);
			}
		}
		if(totalPostsCount>maxPostsByUser){
			maxPostsByUser = totalPostsCount;
			strcpy(maxFirst,firstN);
			strcpy(maxLast,lastN);
		}
	}
	fclose(postsFile);
	FILE *usersFileR;
	usersFileR = fopen("users","rb");
	if (postsFile == NULL){
		printf("1 ERROR: File not open");
		fclose(usersFileR);
		usersFileR = fopen("users","ab");
		fclose(usersFileR);
		printf("\nTry Again ....");
		getch();
		showStatistics();
	}
	int maxFriendsCount=0,totalUsersCount=0;
	while(fread(&user,sizeof(user),1,usersFileR)){
		totalUsersCount++;
		if(user.friendsCount>maxFriendsCount){
			maxFriendsCount = user.friendsCount;
			strcpy(firstN,user.firstName);
			strcpy(lastN,user.lastName);
		}
	}
	fclose(usersFileR);
	postsFile = fopen("posts","rb");
	int totalPosts=0;
	while(fread(&post,sizeof(post),1,postsFile)){
		totalPosts++;
	}
	fclose(postsFile);

	printf("\n %s %s has %d posts!",maxFirst,maxLast,maxPostsByUser);

	printf("\n %s %s has %d friends!",firstN,lastN,maxFriendsCount);

	printf("\n There are %d registered users!",totalUsersCount);

	printf("\n There are %d posts created!",totalPosts);
	int option;
	printf("\n\n 1) Back");
	printf("\n Option: ");
	scanf("%d",&option);
	switch(option){
		case 1:
			main();
			break;
		default:
			printf("\n Invalid option, tente novamente!");
			printf("\n Press any key to continue......");
			getch();
			showStatistics();
			break;
	}
}

int exitProgram(){
	exit(0);
}