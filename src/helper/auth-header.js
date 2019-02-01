export function authHeader() {
    // return authorization header with jwt token
    let auth = JSON.parse(localStorage.getItem('auth'));
    if (auth && auth.key) {
        return { 'Authorization': 'Token ' + auth.key };
    } else {
        return {};
    }
}