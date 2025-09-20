<template>

    <AppHeader titulo="Detalhe" />

    <button class="flex-linha transparente margem" @click="goToPaginaIncial">
        <h2><i class="bi bi-arrow-left"></i> Voltar para menu</h2>
    </button>

    <div class="flex-coluna margem painel" v-if="auditoria.tipo">

        <div class="flex-linha centro item-ponta">
            <h1>{{ nomeOcorrencia(auditoria.tipo) }}</h1>
            <h2 :class="corEstado(auditoria.status)" id="estado">{{ auditoria.status }}</h2>
        </div>

        <h3 class="margem-cima"><i class="bi bi-geo-alt"></i> {{ auditoria.endereco }}</h3>
        <h3><i class="bi bi-clock"></i> {{ auditoria.dataInicio.toDate().toLocaleDateString() }}</h3>

        <div class="painel fundo-cinza margem-cima">
            <h2>Descricao</h2>
            <h3>{{ auditoria.descricao || "Verificação de rotina dos sistemas conforme procedimento padrão." }}</h3>
        </div>


        <button class="flex-linha transparente margem-cima" @click="guardarProfissionais">
            <h2><i class='bi bi-people'></i> Profissionais</h2>
            <PopUpPresente v-if="popUpProfissionais && auditoria.profissionais.length > 0"
                :dados="this.auditoria.profissionais" :texto="`<i class='bi bi-people'></i> Profissionais`" />
        </button>


        <button class="flex-linha transparente" @click="guardarMateriais">
            <h2><i class='bi bi-file-earmark-text'></i> Materiais</h2>
            <PopUpPresente v-if="popUpMateriais && auditoria.materiais.length > 0" :dados="this.auditoria.materiais"
                :texto="`<i class='bi bi-file-earmark-text'></i> Materiais`" />
        </button>

        <div v-if="mostrarAcaoCorretiva" class="flex-coluna">
            <h2 class="margem-cima">Recomendação de ações corretivas</h2>
            <textarea type="text" v-model="auditoria.acaoCorretiva"
                placeholder="Adicione ações corretivas para evitar que ocorra novamente o problema"
                @change="guardarAcaoCorretiva" class="painel fundo-cinza" id="caixa-texto"
                :disabled="auditoria.status === 'Concluido'"></textarea>
        </div>

        <div v-if="mostrarImpacto" class="flex-coluna">
            <h2 class="margem-cima">Impacto esperado das recomendações</h2>
            <textarea type="text" v-model="auditoria.impacto" placeholder="Adicione o impacto que das ações corretivas"
                @change="guardarImpacto" class="painel fundo-cinza" id="caixa-texto"
                :disabled="auditoria.status === 'Concluido'"></textarea>
        </div>



        <div v-if="this.auditoria.status !== 'Concluido'" class="flex-linha margem-cima" style="gap: 5vw;">
            <button class="flex-linha transparente centro fundo-azul botao-acao flex" @click="goToPaginaRegisto">
                <h2><i class="bi bi-play-circle"></i> Alterar Auditoria</h2>
            </button>

            <button class="flex-linha transparente centro fundo-verde botao-acao flex" @click="concluir"
                v-if="this.auditoria.materiais.every(elemento => elemento.presente === true) && this.auditoria.profissionais.every(elemento => elemento.presente === true)">
                <h2><i class="bi bi-check-lg"></i> Completar Auditoria</h2>
            </button>
        </div>


    </div>
</template>


<script>
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { db } from '@/firebase/firebase.js';
import PopUpPresente from './PopUp/PopUpPresente.vue';
import AppHeader from '../AppHeader.vue';
export default {
    name: "InfoAuditoria",
    components: {
        AppHeader,
        PopUpPresente,
    },
    data() {
        return {
            auditoria: {},
            popUpProfissionais: false,
            popUpMateriais: false,
        }
    },
    async mounted() {
        const id = this.$route.params.id;
        const docSnap = await getDoc(doc(db, "auditorias", id));
        if (docSnap.exists()) {
            const dados = docSnap.data();
            this.auditoria = { id: docSnap.id, ...dados };
        } else {
            this.auditoria = {};
        }
    },
    computed: {
        mostrarAcaoCorretiva() {
            const status = (this.auditoria.status || "").toLowerCase();
            const acao = (this.auditoria.acaoCorretiva || "").trim();

            return (
                status === "incompleto" ||
                status === "pendente" ||
                (status === "concluido" && acao !== "")
            );
        },
        mostrarImpacto() {
            const status = (this.auditoria.status || "").toLowerCase();
            const acao = (this.auditoria.acaoCorretiva || "").trim();
            const impacto = (this.auditoria.impacto || "").trim();

            return (
                (status === "incompleto" || status === "pendente") && acao !== "" ||
                (status === "concluido" && acao !== "" && impacto !== "")
            );
        }
    },
    methods: {
        goToPaginaIncial() {
            this.$router.push("/ListaAuditorias");
        },
        goToPaginaRegisto() {
            this.$router.push({
                name: "RegistoAuditoria",
                params: { id: this.auditoria.id },
            });
        },
        corEstado(valor) {
            switch (valor) {
                case "Concluido":
                    return "fundo-verde";
                case "Pendente":
                    return "fundo-amarelo";
                case "Incompleto":
                    return "fundo-vermelho";
                default:
                    return "";
            }
        },
        async concluir() {
            await updateDoc(doc(db, "ocorrencias", this.auditoria.id), {
                status: "Resolvido"
            });
            await updateDoc(doc(db, "auditorias", this.auditoria.id), {
                dataFim: new Date(),
                status: "Concluido"
            });

            for (const profissional of this.auditoria.profissionais) {
                const profissionalRef = doc(db, "profissionais", profissional.id);
                const profissionalSnap = await getDoc(profissionalRef);

                if (profissionalSnap.exists()) {
                    const dadosAtuais = profissionalSnap.data();
                    const quantidadeAtual = dadosAtuais.quantidade || 0;

                    await updateDoc(profissionalRef, {
                        quantidade: quantidadeAtual + profissional.quantidade
                    });
                }
            }

            this.goToPaginaIncial();
        },
        async guardarProfissionais() {
            this.popUpProfissionais = !this.popUpProfissionais;
            if (!this.popUpProfissionais) {
                await updateDoc(doc(db, "auditorias", this.auditoria.id), {
                    profissionais: this.auditoria.profissionais
                });
            }
        },
        async guardarMateriais() {
            this.popUpMateriais = !this.popUpMateriais;
            if (!this.popUpMateriais) {
                await updateDoc(doc(db, "auditorias", this.auditoria.id), {
                    materiais: this.auditoria.materiais
                });
            }
        },
        async guardarAcaoCorretiva() {
            await updateDoc(doc(db, "auditorias", this.auditoria.id), {
                acaoCorretiva: this.auditoria.acaoCorretiva
            });
        },
        async guardarImpacto() {
            await updateDoc(doc(db, "auditorias", this.auditoria.id), {
                impacto: this.auditoria.impacto
            });
        },
        nomeOcorrencia(valor) {
            switch (valor) {
                case "lights": return "Iluminação Pública"
                case "sinals": return "Sinalização em Falta"
                case "roads": return "Vias e Passeios"
            }
        },
    }
}
</script>


<style>
.botao-acao {
    padding: 1.5vh 1.5vh;

    color: #F8FAFC;

    border: 1px solid #e6eaf0;
    border-radius: 15px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
</style>