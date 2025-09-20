<template>
    <header class="flex-linha item-ponta" id="cabecalho">
        <h1>{{ titulo }}</h1>

        <div class="pop-up">
            <button class="transparente icon" id="icon-perfil" @click="perfil = !perfil">
                <i class="bi bi-person"></i>
            </button>

            <PopUpPerfil v-if="perfil" />
        </div>
            
    </header>
</template>


<script>
    import PopUpPerfil from './Paginas/PopUp/PopUpPerfil.vue';
    export default {
        name: "AppHeader",
        components: {
            PopUpPerfil
        },
        props: {
            titulo: {
                type: String,
                default: 'EyesEverywhere'
            }
        },
        data() {
            return {
                perfil: false,
            }
        },
    }
</script>


<style>
    #cabecalho {
        position: sticky;
        top: 0;

        padding: 2vh 2vh;

        background-color: #fff;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);

        z-index: 100;
    }

    #icon-perfil {
        font-size: 20px;

        border-radius: 50%;

        background-color: #F1F5F9;
    }
</style>