<template>
    <div v-if="dados" class="fundo centro">
        <div class="fundo-cinza painel flex-coluna popup" @click.stop>

            <h1 v-html="texto"/>

            <div v-for="(elemento, index) in dados" :key="index" class="flex-linha item-ponta centro">
                <h2>{{ elemento.nome }}</h2>

                <button class="transparente" :class="elemento.presente ? 'fundo-verde' : 'fundo-vermelho'" id="botao-verificar" @click="elemento.presente = !elemento.presente" :disabled="listaCopia[index].presente">
                    <i v-if="elemento.presente" class='bi bi-check' style="color: #fff;"></i>
                    <i v-else class='bi bi-x' style="color: #fff;"></i>
                </button>

            </div>
        </div>
    </div>
</template>


<script>
    export default {
        name: "PopUpPresente",
        data() {
            return {
                listaCopia: JSON.parse(JSON.stringify(this.dados))
            }
        },
        props: {
            dados: {
                type: Array,
                required: true
            },
            texto: {
                type: String,
                required: true
            }
        },
    }
</script>


<style scoped>
    .popup {
        width: 90vw;
    }

    #botao-verificar {
        border: 1px solid #e6eaf0;
        border-radius: 5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
</style>