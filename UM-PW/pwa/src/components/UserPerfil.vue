<template>
    
    <AppHeader titulo="Perfil"/>

    <button class="flex-linha transparente margem" @click="goToPaginaIncial">
        <h2><i class="bi bi-arrow-left"></i>   Voltar para menu</h2>
    </button>

    <div class="flex-coluna margem painel" v-if="user">
        <img :src="userEmail.photoURL" alt="Foto de perfil" id="imagem"/>

        <div class="flex-linha item-ponta centro listaInforcacao">
            <h1>Email</h1>
            <h2>{{ user.email }}</h2>
        </div>

        <div class="flex-linha item-ponta centro listaInforcacao">
            <h1>Nome</h1>
            <h2>{{ user.displayName }}</h2>
        </div>

        <div class="flex-linha item-ponta centro listaInforcacao">
            <h1>Morada</h1>
            <h2>{{ user.address }}</h2>
        </div>

        <div class="flex-linha item-ponta centro listaInforcacao">
            <h1>Data de Nascimento</h1>
            <h2>{{ user.birthDate }}</h2>
        </div>

        <div class="flex-linha item-ponta centro listaInforcacao">
            <h1>Numero Telemovel</h1>
            <h2>{{ user.phone }}</h2>
        </div>

        <div class="flex-linha item-ponta centro listaInforcacao">
            <h1>Especialidade</h1>
            <h2>{{ user.specialty }}</h2>
        </div>

        <div class="flex-linha item-ponta centro">
            <h1>Estado</h1>
            <h2 :class="corEstado(user.status)" id="estado">{{ user.status }}</h2>
        </div>

        <h1>Local de atividade</h1>
        <div class="flex-linha painel" v-for="(local, index) in user.localidades" :key="index">
            <h2>Local {{ index+1 }}: </h2>
            <h2> {{ local }}</h2>
        </div>
    </div>
</template>


<script>
    import { collection, query, where, getDocs } from "firebase/firestore";
    import { db } from '@/firebase/firebase.js';
    import { getAuth } from "firebase/auth";
    import AppHeader from './AppHeader.vue';
    export default {
        name: "UserPerfil",
        components: {
            AppHeader,
        },
        data() {
            return {
                user: null,
            };
        },
        methods: {
            goToPaginaIncial() {
                this.$router.push("/ListaAuditorias");
            },
            corEstado(valor) {
                switch(valor) {
                    case "Ativo":
                        return "fundo-verde";
                    case "Inativo":
                        return "fundo-vermelho";
                    default:
                        return "";
                }
            },
        },
        async mounted() {
            const auth = getAuth();
            this.userEmail = auth.currentUser;
            if (auth.currentUser) {
                const docSnap = query(collection(db, "peritos"), where("email", "==", auth.currentUser.email));
                const querySnapshot = await getDocs(docSnap);
                if (!querySnapshot.empty) {
                    this.user = querySnapshot.docs[0].data();
                }
            }
        }
    }
</script>


<style>
    #imagem {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
        height: 15vh;
        width: 15vh;
        border-radius: 50%;
        margin: 2vh;

        align-self: center;
    }

    .listaInforcacao {
        padding: 1vh 0.5vh;
        gap: 2.5vw;

        background-color: #fff;

        box-shadow: 0 2px 0 rgba(0, 0, 0, 0.1);
    }
</style>