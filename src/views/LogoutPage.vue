<template>
    
</template>

<script>
import { mapState, mapActions } from 'vuex'
    export default {
        name: "logout-page",
    computed: {
        ...mapState('account', ['status'])
    },
    created () {
        // reset login status
        this.logout();
    },
    methods: {
        ...mapActions('account', ['logout'])
    }
    }
</script>

<style scoped>

</style>