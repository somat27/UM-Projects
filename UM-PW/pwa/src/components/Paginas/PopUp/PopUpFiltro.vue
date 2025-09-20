<template>
    <div id="popup">
        <div v-for="status in estado" :key="status">
            <label class="flex-linha" id="texto">
                <input type="radio" :value="status" name="filtro" v-model="selecionado" @click="fechaPopUp(status)" style="accent-color: #204C6D"> 
                <h2>{{ status }}</h2>
            </label>
        </div>
    </div>
</template>


<script>
    export default {
        name: "PopUpFiltro",
        props: {
            filtroValor: {
                type: String,
                required: true
            }
        },
        data() {
            return {
                estado: ["Concluido", "Pendente", "Incompleto"],
                selecionado: this.filtroValor,
            }
        },
        methods: {
            fechaPopUp(escolhido) {
                if (this.selecionado === escolhido) {
                    this.selecionado = "";
                }
                else {
                    this.selecionado = escolhido;
                }
                this.$emit('fechaFiltro', this.selecionado);
            }
        }
    };
</script>


<style scoped>
    #popup {
        position: absolute;
        width: 100%;
        padding: 1vh 1vw;

        background-color: #F1F5F9;

        border: 1px solid #e6eaf0;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);

        z-index: 25;
    }

    #texto {
        align-items: center;
        gap: 1vw;
    }
</style>