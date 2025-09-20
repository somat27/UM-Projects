<template>
    <div class="flex-coluna painel" id="popupPerfil">
        <button class="transparente" @click="goToVerPerfil"><h3>Ver Perfil</h3></button>
        <button class="transparente" @click="logout"><h3>Log Out</h3></button>
    </div>
</template>


<script>
    import { signOut } from "firebase/auth";
    import { auth } from "@/firebase/firebase.js";
    export default {
        name: "PopUpPerfil",
        methods: {
            goToVerPerfil() {
                this.$router.push("/Perfil");
            },
            logout() {
                signOut(auth);
                this.$router.push("/");
            },
        }
    }
</script>


<style>
    #popupPerfil {
        position: absolute;

        justify-content: space-around;

        width: 350%;
        height: 200%;
        right: 0;
        padding: 1vh 1vh;
        gap: 0;

        z-index: 100;
    }
</style>