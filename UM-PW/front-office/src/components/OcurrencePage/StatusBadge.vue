<template>
  <span :class="badgeClass">{{ statusText }}</span>
</template>

<script>
export default {
  name: "StatusBadge",
  props: {
    status: {
      type: String,
      required: true,
      validator: (value) =>
        ["pending", "analyzing", "resolved", "rejected"].includes(value),
    },
  },
  computed: {
    badgeClass() {
      return {
        "status-badge": true,
        "status-pending": this.status === "pending",
        "status-analyzing": this.status === "analyzing",
        "status-resolved": this.status === "resolved",
        "status-rejected": this.status === "rejected",
      };
    },
    statusText() {
      const statusMap = {
        pending: "Pendente",
        analyzing: "Em Análise",
        resolved: "Resolvido",
        rejected: "Rejeitado",
      };
      return statusMap[this.status];
    },
  },
};
</script>

<style scoped>
.status-badge {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  color: #fff;
}

.status-pending {
  background-color: #ffa500;
}

.status-analyzing {
  background-color: #00bfff;
}

.status-resolved {
  background-color: #008000;
}

.status-rejected {
  background-color: #ff0000;
}
</style>
