<template>
    <header class="navbar navbar-static-top navbar-inverse">
        <div class="container">
            <div class="row" style="width:100%;">
                <b-navbar toggleable="md" type="dark">

                    <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

                    <b-navbar-brand :to="{name: 'home'}"><img
                            src="../assets/full_logo.png" style="float:left; height:50px;">
                    </b-navbar-brand>

                    <b-collapse is-nav id="nav_collapse">

                            <b-nav-item-dropdown text="Annotator" right>
                                <b-dropdown-item :to="{name: 'event-list'}">Event listing</b-dropdown-item>
                                <b-dropdown-item :to="{name: 'round-status'}">Round listing</b-dropdown-item>
                                <b-dropdown-item :to="{name: 'vod-status'}">Training vod listing</b-dropdown-item>
                            </b-nav-item-dropdown>

                            <b-nav-item-dropdown text="Reporter" right>
                                <b-dropdown-item :to="{name: 'team-list'}">Team listing</b-dropdown-item>
                            </b-nav-item-dropdown>
                        <!-- Right aligned nav items -->
                        <b-navbar-nav class="ml-auto">

                            <b-nav-form v-if="false">
                                <b-form-input size="sm" class="mr-sm-2" type="text" placeholder="Search"/>
                                <b-button size="sm" class="my-2 my-sm-0" type="submit">Search</b-button>
                            </b-nav-form>

                            <b-nav-item-dropdown text="Lang" right v-if="false">
                                <b-dropdown-item href="#">EN</b-dropdown-item>
                                <b-dropdown-item href="#">ES</b-dropdown-item>
                                <b-dropdown-item href="#">RU</b-dropdown-item>
                                <b-dropdown-item href="#">FA</b-dropdown-item>
                            </b-nav-item-dropdown>

                            <b-nav-item-dropdown right v-if="account.status.loggedIn">
                                <!-- Using button-content slot -->
                                <template slot="button-content">
                                    <em>{{account.user.username}}</em>
                                </template>
                                <b-dropdown-item href="">Profile</b-dropdown-item>
                                <b-dropdown-item :to="{name: 'logout'}">Logout</b-dropdown-item>
                            </b-nav-item-dropdown>
                            <b-nav-item v-if="!account.status.loggedIn" href="/login">
                                Login
                            </b-nav-item>
                        </b-navbar-nav>

                    </b-collapse>
                </b-navbar>
            </div>
        </div>

    </header>
</template>

<script>
    import {mapState} from 'vuex'

    export default {
        name: 'Navigation',

        computed: {
            ...mapState({
                account: state => state.account
            })
        }
    }
</script>
<style>
    .spacing {
        margin-right: 10px;
    }
</style>